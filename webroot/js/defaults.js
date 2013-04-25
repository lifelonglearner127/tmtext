var current_product = 0;
var products = '';

function getPager(){
	var pager = '';
    if (products.length >1) {
    	products.each(function(index){
    		var i = index+1;
    		if (i == current_product) {
    			pager += '<li>'+i+'</li>';
    		} else if ((i < current_product && i>current_product-3) || (i > current_product && i<current_product+3)) {
    			pager += '<li><a href="#" data-page="'+i+'">'+i+'</a></li>';
    		}
    	});

    	if (current_product-3 > 0) {
    		pager = '<li><a href="#" data-page="'+(current_product-1)+'">&lt;</a></li>'+pager;
    	}
    	if (current_product+3 < products.length) {
    		pager += '<li><a href="#" data-page="'+(current_product+1)+'">&gt;</a></li>';
    	}
    }
    return pager;
}

jQuery(document).ready(function($) {

	$('textarea[name="description"]').change(function() {
	 	var number = 0;
	    var matches = $(this).val().match(/\b/g);
	    if(matches) {
	        number = matches.length/2;
	    }
	    $('#wc').html(number);

	});

	$( ".auto_title #title" ).change(function() {
		$('#tc').html($(this).val().length);
	});

	$("#searchForm").submit(function(event) {
		event.preventDefault();
		var $form = $( this ),
			term = $form.find( 'input[name="s"]' ).val(),
		    url = $form.attr( 'action' );

		var posting = $.post( url, { s: term } );

		posting.done(function( data ) {
		    $( "#items" ).html( $(data).find('#content') );
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


