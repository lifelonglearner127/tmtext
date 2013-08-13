var readAssessUrl = base_url + 'index.php/research/get_assess_info';

$(function () {
    $.fn.serializeObject = function()
    {
        var o = {};
        var a = this.serializeArray();
        $.each(a, function() {
            if (o[this.name]) {
                if (!o[this.name].push) {
                    o[this.name] = [o[this.name]];
                }
                o[this.name].push(this.value || '');
            } else {
                o[this.name] = this.value || '';
            }
        });
        return o;
    };

    var textToCopy;
    var zeroTableDraw = true;

    var tableCase = {
        details: [
            "created",
            "product_name",
            "url",
            "short_description_wc",
            "short_seo_phrases",
            "long_description_wc",
            "long_seo_phrases",
            "duplicate_content",
            "price_diff"
        ],
        recommendations: [
            "product_name",
            "url",
            "recommendations"
        ]
    }

    $.fn.dataTableExt.oApi.fnGetAllSColumnNames = function (oSettings) {
        allColumns = [];
        for( var i = 0; i < oSettings.aoColumns.length; i++) {
            allColumns.push($.trim(oSettings.aoColumns[i].sName));
        }
        return allColumns;
    }

    $.fn.dataTableExt.oApi.fnGetSColumnIndexByName = function (oSettings, colname) {
        for( var i = 0; i < oSettings.aoColumns.length; i++) {
            if(oSettings.aoColumns[i].sName == $.trim(colname)) {
                return i;
            }
        }
        return -1;
    }

    $.fn.dataTableExt.oApi.fnProcessingIndicator = function ( oSettings, onoff ) {
        if ( typeof( onoff ) == 'undefined' ) {
            onoff = true;
        }
        this.oApi._fnProcessingDisplay( oSettings, onoff );
    };

        var tblAssess = $('#tblAssess').dataTable({
            "bJQueryUI": true,
            "bDestroy": true,
            "sPaginationType": "full_numbers",
            "bProcessing": true,
            "bServerSide": true,
            "sAjaxSource": readAssessUrl,
            "fnServerData": function (sSource, aoData, fnCallback) {
                    aoData = buildTableParams(aoData);
                    $.getJSON(sSource, aoData, function (json) {
                        if (json.ExtraData != undefined) {
                            buildReport(json);
                        }
                        fnCallback(json);
                        setTimeout(function(){
                            tblAssess.fnProcessingIndicator( false );
                        }, 100);
                    });
            },
            "fnRowCallback": function(nRow, aData, iDisplayIndex) {
                $(nRow).attr("add_data", aData[10]);
                return nRow;
            },
            "fnDrawCallback": function(oSettings) {
                highlightPrices();
                if (zeroTableDraw) {
                    zeroTableDraw = false;
                    return;
                }
                hideColumns();
            },
            "oLanguage": {
                "sInfo": "Showing _START_ to _END_ of _TOTAL_ records",
                "sInfoEmpty": "Showing 0 to 0 of 0 records",
                "sInfoFiltered": ""
            },
            "aoColumns": [
                {"sTitle" : "Date", "sName":"created", "sWidth": "5%"},
                {"sTitle" : "Product Name", "sName":"product_name", "sWidth": "25%"},
                {"sTitle" : "URL", "sName":"url", "sWidth": "30%"},
                {"sTitle" : "Word Count (S)", "sName":"short_description_wc", "sWidth": "5%"},
                {"sTitle" : "SEO Phrases (S)", "sName":"short_seo_phrases", "sWidth": "10%"},
                {"sTitle" : "Word Count (L)", "sName":"long_description_wc", "sWidth": "5%"},
                {"sTitle" : "SEO Phrases (L)", "sName":"long_seo_phrases", "sWidth": "10%"},
                {"sTitle" : "Duplicate Content", "sName":"duplicate_content", "sWidth": "5%"},
                {"sTitle" : "Price", "sName":"price_diff", "sWidth": "10%"},
                {"sTitle" : "Recommendations", "sName":"recommendations", "sWidth": "45%", "bVisible": false, "bSortable": false},
                {"sName":"add_data", "bVisible": false}
            ]
        });

    $('#research_batches_columns').appendTo('div.dataTables_filter');
    $('#tblAssess_length').after($('#assess_tbl_show_case'));
    $('#assess_tbl_show_case a').on('click', function(event) {
        event.preventDefault();
        assess_tbl_show_case(this);
    });

    function assess_tbl_show_case(obj) {
        if (obj) {
            $(obj).parent().find('a').removeClass('active_link');
            $(obj).addClass('active_link');
            hideColumns();
        }
    }

    function highlightPrices() {
        $('#tblAssess td input:hidden').each(function() {
            $(this).parent().addClass('highlightPrices');
        });
    }

    function buildReport(data) {
        if (data.ExtraData == undefined) {
            reportPanel(false);
            return;
        }

        var report = data.ExtraData.report;
        $('#assess_report_total_items').html(report.summary.total_items);
        $('#assess_report_items_priced_higher_than_competitors').html(report.summary.items_priced_higher_than_competitors);
        $('#assess_report_items_have_more_than_20_percent_duplicate_content').html(report.summary.items_have_more_than_20_percent_duplicate_content);
        $('#assess_report_items_unoptimized_product_content').html(report.summary.items_unoptimized_product_content);
        $('#assess_report_items_have_product_context_that_is_too_short').html(report.summary.items_short_products_content);
    }

    $(document).on('change', '#assessDetailsDialog_chkIncludeInReport', function(){
        var isChecked = $(this).is(':checked');
        var data = {

        };
        $.post(
            base_url + 'index.php/research/filterBatchByCustomer',
            data,
            function(data){

            }
        );
    });

    $('#tblAssess tbody').click(function(event) {
        $('#ajaxLoadAni').fadeIn('slow');
        var add_data = JSON.parse($(event.target).parents('tr').attr('add_data'));
        $('#assessDetails_ProductName').val(add_data.product_name);
        $('#assessDetails_url').val(add_data.url);
        $('#assess_open_url_btn').attr('href', add_data.url);
        $('#assessDetails_Price').val(add_data.own_price);
        $('#assessDetails_ShortDescription').val(add_data.short_description);
        $('#assessDetails_ShortDescriptionWC').html(add_data.short_description_wc);
        $('#assessDetails_ShortSEO').val(add_data.short_seo_phrases);
        $('#assessDetails_LongDescription').val(add_data.long_description);
        $('#assessDetails_LongDescriptionWC').html(add_data.long_description_wc);
        $('#assessDetails_LongSEO').val(add_data.long_seo_phrases);

        $('#assessDetailsDialog').parent().find('.ui-dialog-buttonpane button[id="assessDetailsDialog_btnIncludeInReport"]').replaceWith('<div id="assess_details_dialog_opstions"><label><input id="assessDetailsDialog_chkIncludeInReport" type="checkbox">Include in report</label></div></div>');
        $('#assessDetailsDialog').dialog('open');

        $('#ajaxLoadAni').fadeOut('slow');
    });

    $('#assessDetailsDialog').dialog({
        autoOpen: false,
        modal: true,
        resizable: false,
        buttons: {
            'Close': {
                text: 'Close',
                click: function() {
                    $(this).dialog('close');
                }
            },
            'Copy': {
                text: 'Copy',
                id: 'assessDetailsDialog_btnCopy',
                click: function() {
                    copyToClipboard(textToCopy);
                }
            },
            '': {
                id: 'assessDetailsDialog_btnIncludeInReport'
            }
        },
        width: '850px'
    });

    $('#assessDetailsDialog input[type="text"], textarea').bind({
        focus: function() {
            this.select();
            textToCopy = this.value;
        },
        mouseup: function() {
            textToCopy = this.value;
            return false;
        }
    });

    function copyToClipboard(text) {
        window.prompt ("Copy to clipboard: Ctrl+C, Enter (or Esc)", text);
    }

    $('select[name="research_assess_customers"]').on("change", function(res) {
        $.post(base_url + 'index.php/research/filterBatchByCustomer', { 'customer_name': res.target.value}, function(data){
            var research_assess_batches = $("select[name='research_assess_batches']");
            if(data.length>0){
                research_assess_batches.empty();
                for(var i=0; i<data.length; i++){
                    research_assess_batches.append('<option>'+data[i]+'</option>');
                }
            } else if(data.length==0 && res.target.value !="select customer"){
                research_assess_batches.empty();
            }
            $('#research_assess_update').click();
        });
    });

    $('select[name="research_assess_batches"]').on("change", function() {
        var selectedBatch = $(this).find("option:selected").text();
        if (selectedBatch == 'Select batch') {
            $('#assess_report_download_panel').hide();
        } else {
            $('#assess_report_download_panel').show();
        }
        $.post(base_url + 'index.php/research/filterCustomerByBatch', {
                'batch': selectedBatch
        }, function(data){
            var research_assess_customers = $('select[name="research_assess_customers"]');
            if(data != ''){
                research_assess_customers.val(data.toLowerCase()).prop('selected', true);
            } else {
                research_assess_customers.val('select customer').prop('selected', true);
            }
            if (selectedBatch.length == 0)
                research_assess_customers.val('select customer').prop('selected', true);
            $('#research_assess_update').click();
        });
    });

    $('#research_assess_select_all').on('click', function() {
        var isChecked = $(this).is(':checked');
        $('div.boxes_content input[type="checkbox"]').each(function() {
            $(this).attr('checked', isChecked);
        });
    });

    $('#assess_filter_datefrom').datepicker({
        format: 'mm-dd-yyyy'
    });

    $('#assess_filter_dateto').datepicker({
        format: 'mm-dd-yyyy'
    });

    $('#research_assess_short_check').on('change', function() {
        var enabled = $(this).is(':checked');
        if (enabled) {
            $('#research_assess_short_params').find('checkbox').removeAttr('disabled');
            $('#research_assess_short_params').find('input').removeAttr('disabled');
        }
        else {
            $('#research_assess_short_params').find('checkbox').attr('disabled', 'disabled');
            $('#research_assess_short_params').find('input').attr('disabled', 'disabled');
        }
    });

    $('#research_assess_long_check').on('change', function() {
        var enabled = $(this).is(':checked');
        if (enabled) {
            $('#research_assess_long_params').find('checkbox').removeAttr('disabled');
            $('#research_assess_long_params').find('input').removeAttr('disabled');
        }
        else {
            $('#research_assess_long_params').find('checkbox').attr('disabled', 'disabled');
            $('#research_assess_long_params').find('input').attr('disabled', 'disabled');
        }
    });

    $('#assess_filter_clear_dates').on('click', function() {
        $('#assess_filter_datefrom').val('');
        $('#assess_filter_dateto').val('');
    });

    $('#research_assess_update').on('click', function() {
        readAssessData();
    });

    $('#assess_report_download_panel > a').click(function(){
        var type_doc = $(this).data('type');
        assess_report_download(type_doc);
    });

    function assess_report_download(type_doc) {
        var batch_name = $("select[name='research_assess_batches']").find("option:selected").text();
        var batch_id = $("select[name='research_assess_batches']").find("option:selected").val();
        var url = base_url
            + 'index.php/research/assess_report_download?batch_name=' + batch_name
            + '&type_doc=' + type_doc
            + '&batch_id=' + batch_id
        window.open(url);
    }

    $('#research_assess_choiceColumnDialog').dialog({
        autoOpen: false,
        resizable: false,
        modal: true,
        buttons: {
            'Save': function() {
                // get columns params
                var columns = {
                    created : $("#column_created").attr('checked') == 'checked',
                    product_name : $("#column_product_name").attr('checked') == 'checked',
                    url : $("#column_url").attr('checked') == 'checked',
                    short_description_wc : $("#column_short_description_wc").attr('checked') == 'checked',
                    short_seo_phrases : $("#column_short_seo_phrases").attr('checked') == 'checked',
                    long_description_wc : $("#column_long_description_wc").attr('checked') == 'checked',
                    long_seo_phrases : $("#column_long_seo_phrases").attr('checked') == 'checked',
                    duplicate_content : $("#column_duplicate_content").attr('checked') == 'checked',
                    price_diff : $("#column_price_diff").attr('checked') == 'checked'
                };

                // save params to DB
                $.ajax({
                    url: base_url + 'index.php/research/assess_save_columns_state',
                    dataType : 'json',
                    type : 'post',
                    data : {
                        value : columns
                    },
                    success : function( data ) {
                        if(data == true) {
                            hideColumns();
                        }
                    }
                });

                $(this).dialog('close');
            },
            'Cancel': function() {
                $(this).dialog('close');
            }
        },
        width: '250px'
    });

    $('#assess_report_options_dialog_button').on('click', function() {
        var selected_batch_id = $('select[name="research_assess_batches"] option:selected').val();
        var data = {
            'batch_id' : selected_batch_id
        };
        $.get(
            base_url + 'index.php/assess/research_assess_report_options_get',
            data,
            function(data) {
                var report_options = $.parseJSON(data);
                console.log(report_options);
                if (report_options != undefined) {
                    $('#assess_report_page_layout').val(report_options.assess_report_page_layout);
                } else {
                    $('#assess_report_page_layout').val(1);
                }

            }
        );
        $('#assess_report_options_dialog').parent().find('.ui-dialog-buttonpane button[id="assess_report_options_dialog_save"]').addClass("btn btn-success");
        $('#assess_report_options_dialog').parent().find('.ui-dialog-buttonpane button[id="assess_report_options_dialog_cancel"]').addClass("btn");
        $('#assess_report_options_dialog').dialog('open');
    });

    $('#assess_report_options_dialog').dialog({
        autoOpen: false,
        resizable: false,
        modal: true,
        buttons: {
            'Cancel': {
                id: 'assess_report_options_dialog_cancel',
                text: 'Cancel',
                click: function() {
                    $(this).dialog('close');
                }
            },
            'Save': {
                id: 'assess_report_options_dialog_save',
                text: 'Save',
                click: function() {
//                    var competitors = $('#assess_report_competitors :selected');
//                    competitors.each(function(index) {
//                        console.log(this.value);
//                    });
                    var batch_id = $('select[name="research_assess_batches"] option:selected').val();
                    var assess_report_options_form = $('#assess_report_options_form').serializeObject();
                    assess_report_options_form.batch_id = batch_id;
                    var data = {
                        'data' : JSON.stringify(assess_report_options_form)
                    };
                    $.post(
                        base_url + 'index.php/assess/research_assess_report_options_set',
                        data
                    );

                    $(this).dialog('close');
                }
            }
        },
        width: '350px'
    });

    $('#research_batches_columns').on('click', function() {
        $('#research_assess_choiceColumnDialog').dialog('open');
        $('#research_assess_choiceColumnDialog').parent().find('button:first').addClass("popupGreen");
    });

    var tblAllColumns = tblAssess.fnGetAllSColumnNames();
    function hideColumns() {
        var table_case = $('#assess_tbl_show_case a[class=active_link]').data('case');
        var columns_checkboxes = $('#research_assess_choiceColumnDialog').find('input[type=checkbox]:checked');
        var columns_checkboxes_checked = [];
        $.each(columns_checkboxes, function(index, value) {
            columns_checkboxes_checked.push($(value).data('col_name'));
        });
        if (table_case == 'recommendations') {
            reportPanel(false);
            $.each(tblAllColumns, function(index, value) {
                if ($.inArray(value, tableCase.recommendations) > -1) {
                    tblAssess.fnSetColumnVis(index, true, false);
                }
                else {
                    tblAssess.fnSetColumnVis(index, false, false);
                }
            });
        } else if (table_case == 'details') {
            reportPanel(false);
            $.each(tblAllColumns, function(index, value) {
                if ($.inArray(value, columns_checkboxes_checked) > -1) {
                    tblAssess.fnSetColumnVis(index, true, false);
                } else {
                    tblAssess.fnSetColumnVis(index, false, false);
                }
            });
        } else if (table_case == 'report') {
            reportPanel(true);
            var batch_name = $('select[name="research_assess_batches"]').find('option:selected').text();
            //$('#assess_report_download_pdf').attr('href', base_url + 'index.php/research/assess_download_pdf?batch_name=' + batch_name);
        }
    }

    function reportPanel(visible) {
        console.log(visible);
        if (visible) {
            $('#tblAssess').hide();
            $('#tblAssess').parent().find('div.ui-corner-bl').hide();
            $('#assess_report').show();
        } else {
            $('#tblAssess').show();
            $('#tblAssess').parent().find('div.ui-corner-bl').show();
            $('#assess_report').hide();
        }
    }

    function buildTableParams(existingParams) {
        var assessRequestParams = {};

        assessRequestParams.search_text =  $('#assess_filter_text').val();
        assessRequestParams.batch_name = $('select[name="research_assess_batches"]').find('option:selected').text();

        var assess_filter_datefrom = $('#assess_filter_datefrom').val();
        var assess_filter_dateto = $('#assess_filter_dateto').val();
        if (assess_filter_datefrom && assess_filter_dateto) {
            assessRequestParams.date_from = assess_filter_datefrom,
                assessRequestParams.date_to = assess_filter_dateto
        }

        if ($('#research_assess_price_diff').is(':checked')) {
            assessRequestParams.price_diff = true;
        }

        if ($('#research_assess_short_check').is(':checked')) {
            if ($('#research_assess_short_less_check').is(':checked')) {
                assessRequestParams.short_less = $('#research_assess_short_less').val();
            }
            if ($('#research_assess_short_more_check').is(':checked')) {
                assessRequestParams.short_more = $('#research_assess_short_more').val();
            }

            if ($('#research_assess_short_seo_phrases').is(':checked')) {
                assessRequestParams.short_seo_phrases = true;
            }
            if ($('#research_assess_short_duplicate_content').is(':checked')) {
                assessRequestParams.short_duplicate_content = true;
            }
        }

        if ($('#research_assess_long_check').is(':checked')) {
            if ($('#research_assess_long_less_check').is(':checked')) {
                assessRequestParams.long_less = $('#research_assess_long_less').val();
            }
            if ($('#research_assess_long_more_check').is(':checked')) {
                assessRequestParams.long_more = $('#research_assess_long_more').val();
            }

            if ($('#research_assess_long_seo_phrases').is(':checked')) {
                assessRequestParams.long_seo_phrases = true;
            }
            if ($('#research_assess_long_duplicate_content').is(':checked')) {
                assessRequestParams.long_duplicate_content = true;
            }
        }

        for (var p in assessRequestParams) {
            existingParams.push({"name": p, "value": assessRequestParams[p]});
        }

        return existingParams;
    }

    function readAssessData() {
        $("#tblAssess tbody tr").remove();
        tblAssess.fnDraw();
    }

    hideColumns();
    $('#assess_report_download_panel').hide();
});