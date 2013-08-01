var readAssessUrl = base_url + 'index.php/research/get_assess_info';
var pageRDInitialized = false;
$(function () {
    if(pageRDInitialized)
        return;
    pageRDInitialized = true;

    var textToCopy;

    var tblAssess = $('#tblAssess').dataTable({
        "bJQueryUI": true,
        "bDestroy": true,
        "sPaginationType": "full_numbers",
        "bProcessing": true,
        "bServerSide": true,
        "sAjaxSource": readAssessUrl,
        "fnServerData": function (sSource, aoData, fnCallback) {
            aoData = buildTableParams(aoData);
            $.getJSON( sSource, aoData, function (json) {
                fnCallback(json)
            });
        },
        "fnRowCallback": function(nRow, aData, iDisplayIndex) {
            $(nRow).attr("add_data", aData[9]);
            return nRow;
        },
        "fnDrawCallback": function(oSettings) {
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
            {"sTitle" : "SEO Phrases (S)", "sName":"seo_s", "sWidth": "10%"},
            {"sTitle" : "Word Count (L)", "sName":"long_description_wc", "sWidth": "5%"},
            {"sTitle" : "SEO Phrases (L)", "sName":"seo_l", "sWidth": "10%"},
            {"sTitle" : "Duplicate Content", "sName":"duplicate_context", "sWidth": "5%"},
            {"sTitle" : "Price diff", "sName":"price_diff", "sWidth": "10%"},
            {"bVisible": false}
        ]
    });

    $('<button id="research_batches_columns" class="btn btn-success ml_5 float_r">Columns...</button>').appendTo('div.dataTables_filter');

    $('#tblAssess tbody').click(function(event) {
        $('#ajaxLoadAni').fadeIn('slow');
        var add_data = JSON.parse($(event.target.parentNode).attr('add_data'));
        $('#assessDetails_ProductName').val(add_data.product_name);
        $('#assessDetails_url').val(add_data.url);
        $('#assess_open_url_btn').attr('href', add_data.url);
        $('#assessDetails_Price').val(add_data.own_price);
        $('#assessDetails_ShortDescription').val(add_data.short_description);
        $('#assessDetails_ShortDescriptionWC').html(add_data.short_description_wc);
        $('#assessDetails_ShortSEO').val(add_data.seo_s);
        $('#assessDetails_LongDescription').val(add_data.long_description);
        $('#assessDetails_LongDescriptionWC').html(add_data.long_description_wc);
        $('#assessDetails_LongSEO').val(add_data.seo_l);

        $('#assessDetailsDialog').dialog('open');

        $('#ajaxLoadAni').fadeOut('slow');
    });

    $('#assessDetailsDialog').dialog({
        autoOpen: false,
        modal: true,
        buttons: {
            'Cancel': function() {
                $(this).dialog('close');
            },
            'Copy': function() {
                copyToClipboard(textToCopy);
            }
        },
        width: '850px'
    });

    $('#assessDetailsDialog input[type="text"], textarea').bind({
        focus : function() {
            this.select();
            textToCopy = this.value;
        },
        mouseup : function() {
            textToCopy = this.value;
            return false;
        }
    });

    function copyToClipboard(text) {
        window.prompt ("Copy to clipboard: Ctrl+C, Enter", text);
    }

    function getAssessCustomerDropdown(){
        var customers_list_ci = $.post(base_url + 'index.php/measure/getcustomerslist_new', { }, function(c_data) {
            var jsn = $('#research_assess_customers').msDropDown({byJson:{data:c_data, name:'customers_list'}}).data("dd");
            if(jsn != undefined){
                jsn.on("change", function(res) {
                    $.post(base_url + 'index.php/research/filterBatchByCustomer', { 'customer_name': res.target.value}, function(data){
                        var research_assess_batches = $("select[name='research_assess_batches']");
                        if(data.length>0){
                            research_assess_batches.empty();
                            for(var i=0; i<data.length; i++){
                                research_assess_batches.append('<option>'+data[i]+'</option>');
                            }
                        } else if(data.length==0 && res.target.value !="All customers"){
                            research_assess_batches.empty();
                        }
                        $('#research_assess_update').click();
                    });
               });
            }
        }, 'json');
    }

    $('select[name="research_assess_batches"]').on("change", function() {
        var selectedBatch = $(this).find("option:selected").text();
        $.post(base_url + 'index.php/research/filterCustomerByBatch', {
                'batch': selectedBatch
        }, function(data){
            var oDropdown = $("#research_assess_customers").msDropdown().data("dd");
            if(data != ''){
                oDropdown.setIndexByValue(data);
            } else {
                oDropdown.setIndexByValue('All customers');
            }
            if (selectedBatch.length == 0)
                oDropdown.setIndexByValue('All Customers');
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

    $('#research_assess_choiceColumnDialog').dialog({
        autoOpen: false,
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

    $('#research_batches_columns').on('click', function() {
        $('#research_assess_choiceColumnDialog').dialog('open');
        $('#research_assess_choiceColumnDialog').parent().find('button:first').addClass("popupGreen");
    });

    function hideColumns() {
        var columns_checkboxes = $('#research_assess_choiceColumnDialog').find('input[type=checkbox]');
        $(columns_checkboxes).each(function(i) {
            if($(this).attr('checked') == 'checked') {
                tblAssess.fnSetColumnVis(i, true, false);
            } else {
                tblAssess.fnSetColumnVis(i, false, false);
            }
        });
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
        tblAssess.fnDraw();
        hideColumns();
    }



    getAssessCustomerDropdown();
});