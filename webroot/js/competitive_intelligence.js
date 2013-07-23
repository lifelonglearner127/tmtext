    var readUrl = base_url + 'index.php/measure/get_product_price';

$( function() {
    /* Pricing */
    readGridData(); // for pricing
});

// for pricing
function readGridData() {
    //display ajax loader animation
    $( '#ajaxLoadAni' ).fadeIn( 'slow' );

    $.ajax({
        url: readUrl,
        dataType: 'json',
        data:{
            'search_text': $('input[name="research_batches_text"]').val()
        },
        success: function( response ) {
            //clear old rows
            $( '#records > tbody' ).html( '' );

            //append new rows
            $( '#readTemplate' ).render( response ).appendTo( "#records > tbody" );

            //apply dataTable to #records table and save its object in dataTable variable
            dataTable = $( '#records' ).dataTable({
                "bJQueryUI": true,
                "bDestroy": true,
                "sPaginationType": "full_numbers",
                "bProcessing": true,
                "bServerSide": true,
                "sAjaxSource": readUrl,
                "oLanguage": {
                    "sInfo": "Showing _START_ to _END_ of _TOTAL_ records",
                    "sInfoEmpty": "Showing 0 to 0 of 0 records",
                    "sInfoFiltered": ""
                },
                "aoColumns": [
                    {"sName" : "created"},
                    {"sName" : "url"},
                    {"sName" : "model"},
                    {"sName" : "product_name"},
                    {"sName" : "price"}
                ]

            });
            dataTable.fnSort([[0, 'desc']]);

            //hide ajax loader animation here...
            $( '#ajaxLoadAni' ).fadeOut( 'slow' );
        }
    });
}
