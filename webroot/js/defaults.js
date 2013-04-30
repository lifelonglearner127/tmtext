var current_product = 0;
var products = '';

function saveCurrentProduct(text) {
	products.each(function(index, e) {
		if (index+1 === current_product) {
			 $(e).html(text);
			 return;
		}
	});
}

function getPager() {
	var pager = '';
    if (products.length >1) {
    	products.each(function(index){
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

		    url = $('#attributesForm').attr( 'action' );

		    var attributes = $.post( url, { s: term } );

		    attributes.done(function( data ) {
			    $( "#attributes" ).html( $(data).find('#content') );

			    var title = $( ".auto_title #title" );
			    title.val( $(data).find('#product_title').html() ).removeAttr('disabled').trigger('change');

			    products = $(data).find('#product_descriptions').find('li');

			    var description = $('.new_product').find('textarea[name="description"]');
			    description.removeAttr('disabled');
			    description.val(products.first().html());
			    description.trigger('change');
			    current_product = 1;

			    $('#pagination').html(getPager());
		    });
		});
	});

	$(document).on("click", "#pagination a", function(){
		event.preventDefault();
		current_product = $(this).data('page');

		var description = $('.new_product').find('textarea[name="description"]');

		products.each(function(index, e){
			if (index+1 === current_product) {
				 description.val($(e).html());
				 description.trigger('change');
				 $('#pagination').html(getPager());
				 return;
			}
		});

	});

	$(document).ajaxStart(function(){
		$('html').addClass('busy');
	}).ajaxStop(function(){
	    $('html').removeClass('busy');
	});
});
//var start = new Date().getMilliseconds();
//console.log("Executed in " + (new Date().getMilliseconds() - start) + " milliseconds");
