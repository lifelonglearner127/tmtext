var readUrl = base_url + 'index.php/research/search_results_bathes';
var pageInitialized = false;
$(function() {
    if(pageInitialized) return;
        pageInitialized = true;

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
        //"bServerSide": true,
        //"sAjaxSource": readUrl,
        "fnRowCallback": function( nRow, aData, iDisplayIndex ) {
            $(nRow).attr("batch_id", aData[3]);
            $(nRow).attr("url", aData[2]);
            return nRow;
        },
        "oLanguage": {
            "sInfo": "Showing _START_ to _END_ of _TOTAL_ records",
            "sInfoEmpty": "Showing 0 to 0 of 0 records",
            "sInfoFiltered": ""
        },
        "aoColumns": [
            {"sTitle" : "#", "sWidth": "5%", "bSortable": false},
            {"sTitle" : "Product Name"},
            {"sTitle" : "URL"},
            {"bVisible": false}
        ]
    });
    dataTable.fnSort([[1, 'asc']]);

    $('#records tbody').click(function(event) {
        $(dataTable.fnSettings().aoData).each(function (){
            $(this.nTr).removeClass('row_selected');
        });
        var row = $(event.target.parentNode);
        row.addClass('row_selected');
        var request = {
            batch_id: row.attr('batch_id'),
            url: row.attr('url')
        };
        $.get(base_url + 'index.php/research/getResearchDataByURLandBatchId', request, function(response) {
            $('ul#product_descriptions').empty();
            $('ul#research_products').empty();
            $('ul#rel_keywords').empty();
            $('ul[data-st-id="short_desc_seo"]').empty();
            $('ul[data-st-id="long_desc_seo"]').empty();


            $('input[name="product_name"]').val(response.product_name);
            $('input[name="url"]').val(row.attr('url'));
            $('input[name="meta_title"]').val(response.meta_name);
            $('textarea[name="meta_description"]').val(response.meta_description);
            $('input[name="meta_keywords"]').val(response.meta_keywords);
            $('textarea[name="short_description"]').val(response.short_description);
            $('div#long_description').text(response.long_description);
            $('textarea[name="short_description"]').trigger('change');
            $('div#long_description').trigger('change');
        });
    });

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
    if (obj) {
        $(obj).parent().find('a').removeClass('active_link');
        $(obj).addClass('active_link');
    }
    var link_id = $('div.research_edit_filter_links a[class=active_link]').attr('id');

    var selected_batch =  $('select[name="research_batches"]').find('option:selected').text();

    var urlWithParams = readUrl + '?status=' + link_id + '&batch=' + selected_batch;
    dataTable.fnReloadAjax(urlWithParams, null, null);
}
