jQuery(document).ready(function($) {

	$("#searchForm").submit(function(event) {
		event.preventDefault();
		var $form = $( this ),
			term = $form.find( 'input[name="s"]' ).val(),
		    url = $form.attr( 'action' );

		var posting = $.post( url, { s: term } );

		posting.done(function( data ) {
		    $( "#items" ).html( data );
		    url = $('#attributesForm').attr( 'action' );

		    var attributes = $.post( url, { s: term } );

		    attributes.done(function( data ) {
			    $( "#attributes" ).html( data );
		    });

		});
	});

});