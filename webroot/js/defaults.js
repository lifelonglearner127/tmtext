var current_product = 0;
var products = '';
var attribs = '';

function replaceAt(search, replace, subject, n) {
    return subject.substring(0, n) +subject.substring(n).replace(search, replace);
}

function saveCurrentProduct(text) {
	products[current_product-1] = text;
}

function getPager() {
	var pager = '';
    if (products.length >1) {
    	$.each(products, function(index, node) {
    		var i = index+1;
    		if (i == current_product) {
    			pager += '<li><a href="#">'+i+'</a></li>';
    		} else if ((i < current_product && i>current_product-3) || (i > current_product && i<current_product+3)) {
    			pager += '<li><a href="#" data-page="'+i+'">'+i+'</a></li>';
    		}
    	});


    	if (current_product-3 > 0) {
    		pager  = '<li><a href="#" data-page="1">&lt;&lt;</a></li>'
    				+'<li><a href="#" data-page="'+(current_product-1)+'">&lt;</a></li>'+pager;
    	}
    	if (current_product+3 <= products.length) {
    		pager += '<li><a href="#" data-page="'+(current_product+1)+'">&gt;</a></li>'
    				+'<li><a href="#" data-page="'+(products.length)+'">&gt;&gt;</a></li>';
    	}
    }
    return pager;
}

function clearEditorForm() {
	$('.new_product').find('textarea[name="description"]').val('');
	$( ".auto_title #title" ).val('');
	$('#pagination').html('');
	$( "#items" ).html('Original product descriptions');
	$( "#attributes" ).html('Product attributes');
	$('#wc').html('0');
	$('#tc').html('0');
}

jQuery(document).ready(function($) {

	$('.new_product #textarea').on('keyup change',function() {
		$('textarea[name="description"]').val($(this).text()).trigger('change');
	});

	$('textarea[name="description"]').on('keydown change',function() {
	 	var number = 0;
	    var matches = $(this).val().match(/\b/g);
	    if(matches) {
	        number = matches.length/2;
	    }

	    var _limit = $('input[name="description_length"]').val();

	    if (number>_limit) {
	    	var limited = $.trim($(this).val()).split(" ", _limit);
			limited = limited.join(" ");
			$(this).val(limited);
	    }

	    $('#wc').html(number);
	    saveCurrentProduct($(this).val());
	});

	$( ".auto_title #title" ).on('keydown change',function() {
		var _limit = $('input[name="title_length"]').val();
		if($(this).val().length > _limit) {
			var string = $(this).val();
			$(this).val(string.substring(0, _limit));
		}
		$('#tc').html($(this).val().length);
	});

	$("#searchForm").submit(function(event) {
		event.preventDefault();

		clearEditorForm();

		var $form = $( this ),
			term = $form.find( 'input[name="s"]' ).val(),
		    url = $form.attr( 'action' );

		var posting = $.post( url, { s: term } );

		posting.done(function( data ) {
		    $( "#items" ).html( $(data).find('#content') );
		    $( "#items #items_list li" ).expander({
		    	slicePoint: 150,
		    	expandText: '[&hellip;]',
		    	expandPrefix: ' ',
		    	userCollapseText: '[^]',
		    	expandEffect : 'show',
		    	collapseEffect : 'hide',
		    	expandSpeed: 0,
		    	collapseSpeed: 0,
		    	afterExpand: function() {
		    		$(this).find('.details').css('display', 'inline');
		    	}
		    });

		    $("#content #items_list li:first").css({'background':'#CAEAFF'});

		    url = $('#attributesForm').attr( 'action' );

		    var attributes = $.post( url, { s: term }, 'json' );

		    attributes.done(function( data ) {
		    	var a = "<ul>";
		    	$.each(data.attributes, function(i,e){
		    		a += "<li>"+i+" "+e+"</li>";
		    	});
		    	a += "</ul>";
		    	$( "#attributes" ).html( a );
 			    attribs = data['attributes'];

			    var title = $( ".auto_title #title" );
			    title.val( data['product_title'] ).trigger('change');

			    products = data['product_descriptions'];

			    var description = $('.new_product').find('textarea[name="description"]');
			    description.removeAttr('disabled');
			    description.val(products[0]);
			    description.trigger('change');

			    var descriptionDiv = $('.new_product #textarea');
			    descriptionDiv.text(products[0]);
			    descriptionDiv.trigger('change');

			    current_product = 1;

			    $('#pagination').html(getPager());
		    });
		});
	});

	$(document).on("click", "#pagination a", function(){
		event.preventDefault();
		current_product = $(this).data('page');
		if ($(this).data('page')!==undefined) {
			var description = $('.new_product').find('textarea[name="description"]');
			var descriptionDiv = $('.new_product #textarea');

			description.val(products[current_product-1]);
			descriptionDiv.html(products[current_product-1]).trigger('change');

			 $('#pagination').html(getPager());

		}
	});

	$(document).ajaxStart(function(){
		$('html').addClass('busy');
	}).ajaxStop(function(){
	    $('html').removeClass('busy');
	});

	$(document).on("click", "#validate", function(){
		var description = $('.new_product').find('textarea[name="description"]').val();

		var url =  $('#attributesForm').attr( 'action' ).replace('attributes', 'validate');

		$.post(url, { description: description }, 'json')
		.done(function(data) {
			var d = [];
			$.each(data['spellcheck'], function(i, node) {
				description = replaceAt(i, '<b>'+i+'</b>', description, parseInt(node.offset));
			});

			var textAttribs = data['attributes']['description']['attributes']['attribute'];
			$.each(textAttribs, function(i,e){
				if (attribs[e['@attributes']['tagName']] !== undefined) {
					if (attribs[e['@attributes']['tagName']] !== e['@attributes']['value']) {
						description = replaceAt(e['@attributes']['value'], '<i>'+e['@attributes']['value']+'</i>', description, e['@attributes']['startCharOrig']);
					}
				};
			});

			$('.new_product #textarea').html(description).trigger('change');
		});

	});

	$(document).on("click", "#content #items_list li", function(){
	    $("#content #items_list li").each(function(){
	    	$(this).css({'background':'none'})
	    });
	    $(this).css({'background':'#CAEAFF'});
	});

	$(document).on("click", "#attributes ul li", function(){
	    $("#attributes ul li").each(function(){
	    	$(this).css({'background':'none'})
	    });
	    $(this).css({'background':'#CAEAFF'});
	});


});
//var start = new Date().getMilliseconds();
//console.log("Executed in " + (new Date().getMilliseconds() - start) + " milliseconds");
