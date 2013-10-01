var readAssessUrl = base_url + 'index.php/research/get_assess_info';

$(function () {
    $.fn.serializeObject = function(){
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

    var short_wc_total_not_0 = 0;
    var long_wc_total_not_0 = 0;
    var items_short_products_content_short = 0;
    var items_long_products_content_short = 0;

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
        "price_diff",
        "product_selection"
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
                if($('select[name="research_assess_batches"]').find('option:selected').val() == "0"){
                    $('#assess_report_total_items').html("");
                    $('#assess_report_items_priced_higher_than_competitors').html("");
                    $('#assess_report_items_have_more_than_20_percent_duplicate_content').html("");
                    $('#assess_report_items_unoptimized_product_content').html("");
                    $('#assess_report_items_have_product_short_descriptions_that_are_too_short').html("");
                    $('#assess_report_items_have_product_long_descriptions_that_are_too_short').html("");
                }
                if(json.iTotalRecords == 0){
                    $('#assess_report_compare_panel').hide();
                    $('#assess_report_numeric_difference').hide();
                    if($('select[name="research_assess_batches"]').find('option:selected').val() != ""){
                        $('#summary_message').html(" - Processing data. Check back soon.");
                        //                                $('#research_assess_filter_short_descriptions_panel').show();
                        //                                $('#research_assess_filter_long_descriptions_panel').show();
                        $('#assess_report_items_1_descriptions_pnl').hide();
                        $('#assess_report_items_2_descriptions_pnl').hide();
                    }
                }
            });
        },
        "fnRowCallback": function(nRow, aData, iDisplayIndex) {
            $(nRow).attr("add_data", aData[10]);
            return nRow;
        },
        "fnDrawCallback": function(oSettings) {
            tblAssess_postRenderProcessing();
            if (zeroTableDraw) {
                zeroTableDraw = false;
                return;
            }
            hideColumns();
        },
        "oLanguage": {
            "sInfo": "Showing _START_ to _END_ of _TOTAL_ records",
            "sInfoEmpty": "Showing 0 to 0 of 0 records",
            "sInfoFiltered": "",
            "sSearch":"Filter:",
            "sLengthMenu": "_MENU_ rows"
        },
        "aoColumns": [
        {
            "sTitle" : "Date",
            "sName":"created", 
            "sWidth": "5%"
        },

        {
            "sTitle" : "Product Name", 
            "sName":"product_name", 
            "sWidth": "25%"
        },

        {
            "sTitle" : "URL", 
            "sName":"url", 
            "sWidth": "7%"
        },

        {
            "sTitle" : "Words (S)",
            "sName":"short_description_wc", 
            "sWidth": "4%"
        },

        {
            "sTitle" : "Keywords (S)",
            "sName":"short_seo_phrases", 
            "sWidth": "10%"
        },

        {
            "sTitle" : "Words (L)",
            "sName":"long_description_wc", 
            "sWidth": "4%"
        },

        {
            "sTitle" : "Keywords (L)",
            "sName":"long_seo_phrases", 
            "sWidth": "10%"
        },

        {
            "sTitle" : "Duplicate Content", 
            "sName":"duplicate_content", 
            "sWidth": "5%"
        },

        {
            "sTitle" : "Price", 
            "sName":"price_diff", 
            "sWidth": "10%"
        },

        {
            "sTitle" : "Recommendations", 
            "sName":"recommendations", 
            "sWidth": "30%",
            "bVisible": false, 
            "bSortable": false
        },

        {
            "sName":"add_data", 
            "bVisible": false
        }
        ]
    });

    $('#research_batches_columns').appendTo('div.dataTables_filter');
    $('#tblAssess_length').after($('#assess_tbl_show_case'));
    $('#assess_tbl_show_case a').on('click', function(event) {
        event.preventDefault();
        if($(this).text()=='Details'){
            $('#research_batches_columns').show();
        } else {
            $('#research_batches_columns').hide();
        }
        assess_tbl_show_case(this);
    });

    function assess_tbl_show_case(obj) {
        if (obj) {
            $(obj).parent().find('a').removeClass('active_link');
            $(obj).addClass('active_link');
            if($(obj).text()=='Report'){
                $(".research_assess_flagged").css('display','none');
            }else{
                $(".research_assess_flagged").css('display','inline');
            }
            hideColumns();
            tblAssess_postRenderProcessing();
        }
    }

    function tblAssess_postRenderProcessing() {
        $('#tblAssess td input:hidden').each(function() {
            $(this).parent().addClass('highlightPrices');
        });
        $('#tblAssess tbody tr').each(function() {
            var row_height = $(this).height();
            if (row_height > 5){
                $(this).find('table.url_table').height(row_height - 11);
            }
        });
    }

    function buildReport(data) {
        if (data.ExtraData == undefined) {
            reportPanel(false);
            return;
        }

        var report = data.ExtraData.report;
        $('#summary_message').html("");
        $('#assess_report_total_items').html(report.summary.total_items);
        $('#assess_report_items_priced_higher_than_competitors').html(report.summary.items_priced_higher_than_competitors);
        $('#assess_report_items_have_more_than_20_percent_duplicate_content').html(report.summary.items_have_more_than_20_percent_duplicate_content);
        $('#assess_report_items_unoptimized_product_content').html(report.summary.items_unoptimized_product_content);
        $('#research_assess_filter_short_descriptions_panel').show();
        $('#research_assess_filter_long_descriptions_panel').show();
        short_wc_total_not_0 = report.summary.short_wc_total_not_0;
        long_wc_total_not_0 = report.summary.long_wc_total_not_0;
        items_short_products_content_short = report.summary.items_short_products_content_short;
        items_long_products_content_short = report.summary.items_long_products_content_short;
        if (report.summary.short_wc_total_not_0 > 0 && report.summary.long_wc_total_not_0 > 0) {
            $('#assess_report_items_have_product_short_descriptions_that_are_too_short').html(report.summary.items_short_products_content_short);
            $('#assess_report_items_have_product_long_descriptions_that_are_too_short').html(report.summary.items_long_products_content_short);

            $('#assess_report_items_have_product_short_descriptions_that_are_less_than_value').html(report.summary.short_description_wc_lower_range);
            $('#assess_report_items_have_product_long_descriptions_that_are_less_than_value').html(report.summary.long_description_wc_lower_range);

            $('#assess_report_items_1_descriptions_pnl').hide();
            $('#assess_report_items_2_descriptions_pnl').show();

            $('#research_assess_filter_short_descriptions_label').html("Short Descriptions:");
            $('#research_assess_filter_long_descriptions_label').html("Long Descriptions:");
            $('#research_assess_filter_short_descriptions_panel').show();
            $('#research_assess_filter_long_descriptions_panel').show();
        } else {
            $('#assess_report_items_1_descriptions_pnl').show();
            $('#assess_report_items_2_descriptions_pnl').hide();

            if (report.summary.short_wc_total_not_0 == 0) {
                $('#research_assess_filter_long_descriptions_label').html("Descriptions:");
                $('#research_assess_short_less_check').removeAttr('checked');
                $('#research_assess_short_more_check').removeAttr('checked');
                $('#research_assess_filter_short_descriptions_panel').hide();
            }
            if (report.summary.long_wc_total_not_0 == 0) {
                $('#research_assess_filter_short_descriptions_label').html("Descriptions:");
                $('#research_assess_long_less_check').removeAttr('checked');
                $('#research_assess_long_more_check').removeAttr('checked');
                $('#research_assess_filter_long_descriptions_panel').hide();
            }
            if(report.summary.short_wc_total_not_0 == 0 && report.summary.long_wc_total_not_0 != 0){
                $('#assess_report_items_have_product_descriptions_that_are_too_short').html(report.summary.items_long_products_content_short);
                $('#assess_report_items_have_product_descriptions_that_are_less_than_value').html(report.summary.long_description_wc_lower_range);
            }else if(report.summary.short_wc_total_not_0 != 0 && report.summary.long_wc_total_not_0 == 0){
                $('#assess_report_items_have_product_descriptions_that_are_too_short').html(report.summary.items_short_products_content_short);
                $('#assess_report_items_have_product_descriptions_that_are_less_than_value').html(report.summary.short_description_wc_lower_range);
            }else if(report.summary.short_wc_total_not_0 == 0 && report.summary.long_wc_total_not_0 == 0){
                $('#assess_report_items_1_descriptions_pnl').hide();
            }
        }

        if (report.summary.items_long_products_content_short == 0 && report.summary.items_short_products_content_short == 0) {
            $('#assess_report_items_1_descriptions_pnl').hide();
            $('#assess_report_items_2_descriptions_pnl').hide();
        }

        if (report.summary.absent_items_count == undefined || report.summary.absent_items_count == 0) {
            $('#assess_report_compare_panel').hide();
        } else {
            $('#assess_report_absent_items_count').html(report.summary.absent_items_count);
            $('#assess_report_compare_customer_name').html(report.summary.compare_customer_name);
            $('#assess_report_compare_batch_name').html(report.summary.compare_batch_name);
            $('#assess_report_own_batch_name').html(report.summary.own_batch_name);
            $('#assess_report_compare_panel').show();
        }
        var research_assess_compare_batches_batch = $('#research_assess_compare_batches_batch').val()
        if (research_assess_compare_batches_batch != null && research_assess_compare_batches_batch != 0 && report.summary.compare_batch_total_items != undefined) {
            var secondary_company_name = $('#research_assess_compare_batches_customer option:selected').text();
            var num_diff = report.summary.compare_batch_total_items - report.summary.own_batch_total_items;
            var numeric_difference_caption = '';
            if (num_diff < 0) {
                numeric_difference_caption = Math.abs(num_diff) + ' more products in your selection than in the ' + secondary_company_name + ' selection';
            } else {
                if (num_diff > 0) {
                    numeric_difference_caption = num_diff + ' fewer products in your selection than in the ' + secondary_company_name + ' selection';
                } else {
                    numeric_difference_caption = num_diff + ' items in your selection and in the ' + secondary_company_name + ' selection';
                }
            }
            $('#assess_report_numeric_difference_caption').html(numeric_difference_caption);
            $('#assess_report_numeric_difference').show();
        } else {
            $('#assess_report_numeric_difference').hide();
        }

        if (report.detail_comparisons_total > 0) {
            comparison_details_load();
            var comparison_pagination = report.comparison_pagination;
            $('#comparison_pagination').html(comparison_pagination);
        } else {
            $('#comparison_detail').html('');
            $('#comparison_pagination').html('');
        }

        $('#assess_report_download_panel').show();
    }

    function comparison_details_load(url){
        var batch_id = $("select[name='research_assess_batches']").find("option:selected").val();
        var data = {
            batch_id:batch_id
        };
        if (url == undefined) {
            url = base_url + 'index.php/research/comparison_detail';
        }
        $.post(
            url,
            data,
            function(data) {
                $('#comparison_detail').html(data.comparison_detail);
                $('#comparison_pagination').html(data.comparison_pagination);
            }
            );
    }

    $(document).on('click', '#comparison_pagination a', function(event){
        event.preventDefault();
        comparison_details_load($(this).attr('href'));
    });

    $(document).on('change', '#assessDetailsDialog_chkIncludeInReport', function(){
        var research_data_id = $('#assessDetailsDialog_chkIncludeInReport').attr('research_data_id');
        var include_in_report = $(this).is(':checked');
        var data = {
            research_data_id:research_data_id,
            include_in_report:include_in_report
        };
        $.post(
            base_url + 'index.php/assess/include_in_report',
            data,
            function(data){
            }
            );
    });

    $('#tblAssess tbody').click(function(event) {
        if ($(event.target).is('a')) {
            return;
        }
        var target = $(event.target);
        if (target.parents('table').attr('class') == 'url_table')
            target = target.parents('table');
        var add_data = JSON.parse(target.parents('tr').attr('add_data'));
        // if this product is absent product from second batch
        if (add_data.id == undefined) {
            return;
        }
        $('#ajaxLoadAni').fadeIn('slow');
        $('#assessDetails_ProductName').val(add_data.product_name);
        $('#assessDetails_url').val(add_data.url);
        $('#assess_open_url_btn').attr('href', add_data.url);
        $('#assessDetails_Price').val(add_data.own_price);
        if (short_wc_total_not_0 == 0 || long_wc_total_not_0 == 0) {
            $('#assessDetails_short_and_long_description_panel').hide();
            $('#assessDetails_description_panel').show();

            if (short_wc_total_not_0 == 0) {
                var description = add_data.long_description;
                var description_wc = add_data.long_description_wc;
                var seo_phrases = add_data.long_seo_phrases;
            } else {
                var description = add_data.short_description;
                var description_wc = add_data.short_description_wc;
                var seo_phrases = add_data.short_seo_phrases;
            }
            $('#assessDetails_Description').val(description);
            $('#assessDetails_DescriptionWC').html(description_wc);
            $('#assessDetails_SEO').val(seo_phrases);
        } else {
            $('#assessDetails_short_and_long_description_panel').show();
            $('#assessDetails_description_panel').hide();

            $('#assessDetails_ShortDescription').val(add_data.short_description);
            $('#assessDetails_ShortDescriptionWC').html(add_data.short_description_wc);
            $('#assessDetails_ShortSEO').val(add_data.short_seo_phrases);
            $('#assessDetails_LongDescription').val(add_data.long_description);
            $('#assessDetails_LongDescriptionWC').html(add_data.long_description_wc);
            $('#assessDetails_LongSEO').val(add_data.long_seo_phrases);
        }

        var chk_include_in_report = '<div id="assess_details_dialog_options" style="float: right;"><label><input id="assessDetailsDialog_chkIncludeInReport" type="checkbox">&nbspInclude in report</label></div>';
        var btn_delete_from_batch = '<button id="assess_details_delete_from_batch" class="btn btn-danger" style="float:left;">Delete</button>';
        var assessDetailsDialog_replace_element = $('#assessDetailsDialog').parent().find('.ui-dialog-buttonpane button[id="assessDetailsDialog_btnIncludeInReport"]');
        if (assessDetailsDialog_replace_element.length > 0) {
            assessDetailsDialog_replace_element.replaceWith(btn_delete_from_batch + chk_include_in_report);
        }

        var data = {
            research_data_id: add_data.research_data_id
        };
        var checked = false;
        $.get(
            base_url + 'index.php/assess/include_in_assess_report_check',
            data,
            function(data) {
                checked = data.checked;
                var assessDetailsDialog_chkIncludeInReport = $('#assessDetailsDialog_chkIncludeInReport');
                assessDetailsDialog_chkIncludeInReport.removeAttr('checked');
                if (checked == true) {
                    assessDetailsDialog_chkIncludeInReport.attr('checked', 'checked');
                }
                assessDetailsDialog_chkIncludeInReport.attr('research_data_id', add_data.research_data_id);
                $('#assessDetailsDialog').dialog('open');
            }
            );

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
        width: 850
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
        window.prompt("Copy to clipboard: Ctrl+C, Enter (or Esc)", text);
    }

    $(document).on('click', '#assess_details_delete_from_batch', function(){
        if(confirm('Are you sure you want to delete this item?')){
            var batch_id = $("select[name='research_assess_batches']").find("option:selected").val();
            var research_data_id = $('#assessDetailsDialog_chkIncludeInReport').attr('research_data_id');
            var data = {
                batch_id:batch_id,
                research_data_id:research_data_id
            };
            $.post(
                base_url + 'index.php/assess/delete_from_batch',
                data,
                function(){
                    $('#assessDetailsDialog').dialog('close');
                    readAssessData();
                }
                );
        }
    });

    $('select[name="research_assess_customers"]').on("change", function(res) {
        var research_assess_batches = $("select[name='research_assess_batches']");
        $.post(base_url + 'index.php/research/filterBatchByCustomerName', {
            'customer_name': res.target.value
            }, function(data){
            if(data.length>0){
                research_assess_batches.empty();
                for(var i=0; i<data.length; i++){
                    research_assess_batches.append('<option value="'+data[i]['id']+'">'+data[i]['title']+'</option>');
                }
            } else if(data.length==0 && res.target.value !="select customer"){
                research_assess_batches.empty();
            }
            $('#research_assess_update').click();
        });
        var own_customer = $(this).val();
        fill_lists_batches_compare(own_customer);
    });
    
    $('#research_assess_flagged').live('click', function(){
        $('#research_assess_update').click();
    });

    function fill_lists_batches_compare(own_customer) {
        var research_assess_compare_batches_customer = $('#research_assess_compare_batches_customer');
        var research_assess_compare_batches_batch = $('#research_assess_compare_batches_batch');
        research_assess_compare_batches_customer.empty();
        research_assess_compare_batches_batch.empty();
        if (own_customer == 'Select customer') {
            return;
        }

        if (own_customer == 'select customer') {
            research_assess_compare_batches_customer.empty();
            research_assess_compare_batches_batch.empty();
            return;
        }

        $.get(
            base_url + 'index.php/assess/customers_get_all',
            {},
            function(data){
                research_assess_compare_batches_customer.empty();
                if (data) {
                    $.each(data, function(i, v){
                        research_assess_compare_batches_customer.append('<option value="'+v.toLowerCase()+'">'+v+'</option>');
                    });
                    research_assess_compare_batches_customer.find('option[value="'+own_customer+'"]').remove();
                }
            }
            );

        $.get(
            base_url + 'index.php/assess/batches_get_all',
            {},
            function(data){
                research_assess_compare_batches_batch.empty();
                if (data) {
                    $.each(data, function(i, v){
                        research_assess_compare_batches_batch.append('<option value="'+i+'">'+v+'</option>');
                    });
                    var own_batch_id = $("select[name='research_assess_batches']").find("option:selected").val();
                    research_assess_compare_batches_batch.find('option[value="'+own_batch_id+'"]').remove();
                }
            }
            );
    }

    $('#research_assess_compare_batches_customer').change(function(res){
        var research_assess_compare_batches_batch = $("#research_assess_compare_batches_batch");
        $.post(base_url + 'index.php/research/filterBatchByCustomerName', {
            'customer_name': res.target.value
            }, function(data){
            if(data.length>0){
                research_assess_compare_batches_batch.empty();
                for(var i=0; i<data.length; i++){
                    research_assess_compare_batches_batch.append('<option value="'+data[i]['id']+'">'+data[i]['title']+'</option>');
                }
            } else if(data.length==0 && res.target.value !="select customer"){
                research_assess_compare_batches_batch.empty();
            }
        });
    });

    $('#research_assess_compare_batches_batch').change(function(){
        var selectedBatch = $(this).find("option:selected").text();
        $.post(base_url + 'index.php/research/filterCustomerByBatch', {
            'batch': selectedBatch
        }, function(data){
            var research_assess_compare_batches_customer = $('#research_assess_compare_batches_customer');
            if(data != ''){
                research_assess_compare_batches_customer.val(data.toLowerCase()).prop('selected', true);
            } else {
                research_assess_compare_batches_customer.val('select customer').prop('selected', true);
            }
            if (selectedBatch.length == 0)
                research_assess_compare_batches_customer.val('select customer').prop('selected', true);
        });
    });

    $('#research_assess_compare_batches_reset').click(function(){
        var research_assess_compare_batches_customer = $('#research_assess_compare_batches_customer');
        var research_assess_compare_batches_batch = $('#research_assess_compare_batches_batch');
        research_assess_compare_batches_customer.val('select customer').prop('selected', true);
        research_assess_compare_batches_batch.val('select batch').prop('selected', true);
        $('#research_assess_update').click();
    });

    $('select[name="research_assess_batches"]').on("change", function() {
        var selectedBatch = $(this).find("option:selected").text();
        var selectedBatchId = $(this).find("option:selected").val();
        $('#assess_report_download_panel').hide();
        if (selectedBatchId == '') {
            var data = {
                ExtraData:{
                    report:{
                        summary:{
                            total_items:'',
                            items_priced_higher_than_competitors:'',
                            items_have_more_than_20_percent_duplicate_content:'',
                            items_unoptimized_product_content:'',
                            items_short_products_content:''
                        }
                    }
                }
            }
            buildReport(data);
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
            var own_customer = research_assess_customers.val();
            fill_lists_batches_compare(own_customer);
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
        addColumn_url_class();
    });
    
    function addColumn_url_class(){
        //Denis add class to URL column
        if(  $("#column_url").attr('checked') == 'checked' ){
			
            table = $('#assess_tbl_show_case').find('.active_link').data('case')
            column = '';
            if( table == 'recommendations' ){
                column = 'td:eq(1)';
            }else if( table == 'details' ){
                column = 'td:eq(2)';
            }
			
            //			setTimeout(function(){
            //				//console.log( $("#tblAssess").html() );
            //				$("#tblAssess").find('tr').each(function(){
            //					//$(this).find('td:eq(2)').addClass('column_url');
            //					$(this).find(column).addClass('column_url');
            //				});
            //			}, 2000);
            $("#tblAssess").find('tr').each(function(){
                $(this).find(column).addClass('column_url');
            });
        }
    //----------------------
    }

    $('#assess_report_download_panel > a').click(function(){
        var type_doc = $(this).data('type');
        assess_report_download(type_doc);
    });

    function assess_report_download(type_doc) {
        var batch_name = $("select[name='research_assess_batches']").find("option:selected").text();
        //var batch_id = $("select[name='research_assess_batches']").find("option:selected").val();
        var compare_batch_id = $("#research_assess_compare_batches_batch").val();
        var price_diff = false;
        if ($('#research_assess_price_diff').is(':checked')) {
            price_diff = true;
        }
        var url = base_url
        + 'index.php/research/assess_report_download?batch_name=' + batch_name
        + '&type_doc=' + type_doc
        //+ '&batch_id=' + batch_id
        + '&compare_batch_id=' + compare_batch_id
        + '&price_diff=' + price_diff
        var assessRequestParams = collectionParams();
        for (var p in assessRequestParams) {
            url = url + '&'+p+'='+assessRequestParams[p];
        }
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
                            addColumn_url_class();
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
                if (report_options != undefined) {
                    $('#assess_report_page_layout').val(report_options.assess_report_page_layout);
                } else {
                    $('#assess_report_page_layout').val(1);
                }
                var assess_report_competitors = $('#assess_report_competitors');
                assess_report_competitors.empty();
                $.each(report_options.assess_report_competitors, function(index, value) {
                    var selected = '';
                    if (value.selected) {
                        selected = 'selected="selected"';
                    }
                    assess_report_competitors.append('<option value="'+value.id+'" '+selected+'>'+value.name+'</option>');
                });
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
                    assess_report_options_dialog_close();
                }
            },
            'Save': {
                id: 'assess_report_options_dialog_save',
                text: 'Save',
                click: function() {
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
                    assess_report_options_dialog_close();
                }
            }
        },
        width: '450px'
    });

    function assess_report_options_dialog_close(){
        $('#assess_report_competitors').empty();
        $('#assess_report_options_dialog').dialog('close');
    }

    $('#research_batches_columns').on('click', function() {
        $('#research_assess_choiceColumnDialog').dialog('open');
        $('#research_assess_choiceColumnDialog').parent().find('button:first-child').addClass("popupGreen");
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
            addColumn_url_class();
        } else if (table_case == 'details') {
            reportPanel(false);
            $.each(tblAllColumns, function(index, value) {
                if ($.inArray(value, columns_checkboxes_checked) > -1) {
                    tblAssess.fnSetColumnVis(index, true, false);
                } else {
                    tblAssess.fnSetColumnVis(index, false, false);
                }
            });
            addColumn_url_class();
        } else if (table_case == 'report') {
            reportPanel(true);
            var batch_id = $('select[name="research_assess_batches"]').find('option:selected').val();
        //$('#assess_report_download_pdf').attr('href', base_url + 'index.php/research/assess_download_pdf?batch_name=' + batch_name);
        }
    }

    function reportPanel(visible) {
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
        var assessRequestParams = collectionParams();

        for (var p in assessRequestParams) {
            existingParams.push({
                "name": p, 
                "value": assessRequestParams[p]
                });
        }

        return existingParams;
    }

    function collectionParams(){
        var assessRequestParams = {};

        assessRequestParams.search_text =  $('#assess_filter_text').val();
        assessRequestParams.batch_id = $('select[name="research_assess_batches"]').find('option:selected').val();

        var assess_filter_datefrom = $('#assess_filter_datefrom').val();
        var assess_filter_dateto = $('#assess_filter_dateto').val();
        if (assess_filter_datefrom && assess_filter_dateto) {
            assessRequestParams.date_from = assess_filter_datefrom,
            assessRequestParams.date_to = assess_filter_dateto
        }

        if ($('#research_assess_flagged').is(':checked')) {
            assessRequestParams.flagged = true;
        }

        if ($('#research_assess_price_diff').is(':checked')) {
            assessRequestParams.price_diff = true;
        }

        if ($('#research_assess_short_check').is(':checked')) {
            assessRequestParams.short_less_check = $('#research_assess_short_less_check').is(':checked');
            assessRequestParams.short_less = $('#research_assess_short_less').val();
            assessRequestParams.short_more_check = $('#research_assess_short_more_check').is(':checked')
            assessRequestParams.short_more = $('#research_assess_short_more').val();

            if ($('#research_assess_short_seo_phrases').is(':checked')) {
                assessRequestParams.short_seo_phrases = true;
            }
            if ($('#research_assess_short_duplicate_content').is(':checked')) {
                assessRequestParams.short_duplicate_content = true;
            }
        }

        if ($('#research_assess_long_check').is(':checked')) {
            assessRequestParams.long_less_check = $('#research_assess_long_less_check').is(':checked');
            assessRequestParams.long_less = $('#research_assess_long_less').val();
            assessRequestParams.long_more_check = ($('#research_assess_long_more_check').is(':checked'));
            assessRequestParams.long_more = $('#research_assess_long_more').val();

            if ($('#research_assess_long_seo_phrases').is(':checked')) {
                assessRequestParams.long_seo_phrases = true;
            }
            if ($('#research_assess_long_duplicate_content').is(':checked')) {
                assessRequestParams.long_duplicate_content = true;
            }
        }

        var research_assess_compare_batches_batch = $('#research_assess_compare_batches_batch').val();
        if (research_assess_compare_batches_batch > 0) {
            assessRequestParams.compare_batch_id = research_assess_compare_batches_batch;
        }

        return assessRequestParams;
    }

    function readAssessData() {
        $('#assess_report_download_panel').hide();
        $("#tblAssess tbody tr").remove();
        tblAssess.fnDraw();
    }

    hideColumns();
    $('#assess_report_download_panel').hide();

    $(document).on('mouseenter', 'i.snap_ico', function () {
        var snap = "webshoots/" + $(this).attr('snap');
        $("#assess_preview_crawl_snap_modal .snap_holder").html("<img src='" + base_url +  snap + "'>");
        $("#assess_preview_crawl_snap_modal").modal('show');
    });
    $(document).on('mouseleave', '#assess_preview_crawl_snap_modal', function () {
        $(this).modal('hide');
    });
    $('#research_assess_export').click(function () {
        $(this).attr('disabled', true);
        $(this).text('Exporting...');
        $.fileDownload($(this).prop('href'))
        .done(function () { 
            $('#research_assess_export').removeAttr('disabled');
            $('#research_assess_export').text('Export');
            })
        .fail(function () {
        });
    });
});
