var readUrl = base_url + 'index.php/research/search_results_bathes';

$(function() {
    $.fn.dataTableExt.oApi.fnReloadAjax = function ( oSettings, sNewSource, fnCallback, bStandingRedraw )
    {
        if ( typeof sNewSource != 'undefined' && sNewSource != null )
        {
            oSettings.sAjaxSource = sNewSource;
        }
        this.oApi._fnProcessingDisplay( oSettings, true );
        var that = this;
        var iStart = oSettings._iDisplayStart;

        oSettings.fnServerData( oSettings.sAjaxSource, [], function(json) {
            /* Clear the old information from the table */
            that.oApi._fnClearTable( oSettings );

            /* Got the data - add it to the table */
            for ( var i=0 ; i<json.aaData.length ; i++ )
            {
                that.oApi._fnAddData( oSettings, json.aaData[i] );
            }

            oSettings.aiDisplay = oSettings.aiDisplayMaster.slice();
            that.fnDraw();

            if ( typeof bStandingRedraw != 'undefined' && bStandingRedraw === true )
            {
                oSettings._iDisplayStart = iStart;
                that.fnDraw( false );
            }

            that.oApi._fnProcessingDisplay( oSettings, false );

            /* Callback user function - for event handlers etc */
            if ( typeof fnCallback == 'function' && fnCallback != null )
            {
                fnCallback( oSettings );
            }
        }, oSettings );
    }

    dataTable = $('#records').dataTable({
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

    drawREProductsTable();

    $("div.research_edit_filter_links a").live("click", function(event) {
        event.preventDefault();
        drawREProductsTable(this);
    });

    $(document).on("change", 'select[name="research_batches"]', function() {
        drawREProductsTable();
    });
});

function drawREProductsTable(obj) {
    $(obj).parent().find('a').removeClass('active_link');
    $(obj).addClass('active_link');
    var link_id = $('div.research_edit_filter_links a[class=active_link]').attr('id');

    var selected_batch =  $('select[name="research_batches"]').find('option:selected').text();

    var urlWithParams = readUrl + '?status=' + link_id + '&batch=' + selected_batch;
    dataTable.fnReloadAjax(urlWithParams, null, null);
}
