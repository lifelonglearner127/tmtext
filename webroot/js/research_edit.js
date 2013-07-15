//var readUrl = base_url + 'index.php/research/getREProducts';
var readUrl = base_url + 'index.php/research/search_results_bathes';

$( function() {
    /* Research & edit / Edit */
    drawREProductsTable(); // Research & edit / Edit

    $("div.research_edit_filter_links a").live("click", function(event) {
//        console.log('aaa');
        event.preventDefault();
        drawREProductsTable(this);
    });
});

// Research & edit / Edit
function drawREProductsTable(obj) {
    //event.preventDefault();
    $(obj).parent().find('a').removeClass('active_link');
    $(obj).addClass('active_link');
    var link_id = $(obj).attr('id');
    $.ajax({
        url: readUrl,
        type: 'POST',
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
                    { "bSortable": false },
                    {"sName" : "product_name"},
                    {"sName" : "url"}
                ]
            });
            dataTable.fnSort([[1, 'asc']]);

            //hide ajax loader animation here...
            $( '#ajaxLoadAni' ).fadeOut( 'slow' );
        } //end success
    });
}
