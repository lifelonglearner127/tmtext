var readAssessUrl = base_url + 'index.php/assess/get_assess_info';
var readBoardSnapUrl = base_url + 'index.php/assess/get_board_view_snap';
var readGraphDataUrl = base_url + 'index.php/assess/get_graph_batch_data';
var readAssessUrlCompare = base_url + 'index.php/assess/compare';
var serevr_side = true;
var serverside_table;
var tblAllColumns = [];
var tblAssess;
$(function() {
    $.fn.serializeObject = function() {
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
            "snap",
            "created",
            "product_name",
            "item_id",
            "model",
            "url",
            "Page_Load_Time",
            "Short_Description",
            "short_description_wc",
            "Meta_Keywords",
            "short_seo_phrases",
            "Long_Description",
            "long_description_wc",
            "long_seo_phrases",
            "duplicate_content",
            "Custom_Keywords_Short_Description",
            "Custom_Keywords_Long_Description",
            "Meta_Description",
            "Meta_Description_Count",
            "H1_Tags",
            "H1_Tags_Count",
            "H2_Tags",
            "H2_Tags_Count",
            "column_external_content",
            "column_reviews",
            "average_review",
            "column_features",
            "price_diff",
            "product_selection"

        ],
         details_compare: [
            "snap",
            "product_name",
            "item_id",
            "model",
            "url",
            "Page_Load_Time",
            "Short_Description",
            "short_description_wc",
            "Meta_Keywords",
            "Long_Description",
            "long_description_wc",
            "Meta_Description",
            "Meta_Description_Count",
            "average_review",
            "snap1",
            "product_name1",
            "item_id1",
            "model1",
            "url1",
            "Page_Load_Time1",
            "Short_Description1",
            "short_description_wc1",
            "Meta_Keywords1",
            "Long_Description1",
            "long_description_wc1",
            "Meta_Description1",
            "Meta_Description_Count1",
            "average_review1",
            "gap"
            
        ],
        recommendations: [
            "product_name",
            "url",
            "recommendations"
        ]
    }

    function createTableByServerSide() {

        $('#tblAssess_wrapper').remove();
        var th = '';
        for(var i =0;i<Object.keys(columns);i++){
            th += '<th with = "100px"></th>';
        }
        var newTable = '<table id="tblAssess" class="tblDataTable"><thead>'+th+'</thead><tbody></tbody></table>';
        $('#dt_tbl').prepend(newTable);        
        
        tblAssess = $('#tblAssess').dataTable({
            "bJQueryUI": true,
            "bDestroy": true,
//            "sScrollX": "100%",
            "sPaginationType": "full_numbers",
            "bProcessing": true,
            "aaSorting": [[5, "desc"]],
            "bAutoWidth": false,
            "bServerSide": true,
            "sAjaxSource": readAssessUrl,
            "fnServerData": function(sSource, aoData, fnCallback) {
                aoData = buildTableParams(aoData);

                $.getJSON(sSource, aoData, function(json) {

                    if (json.ExtraData != undefined) {
                        buildReport(json);
                    }

                    fnCallback(json);
                    setTimeout(function() {
                        tblAssess.fnProcessingIndicator(false);
                    }, 100);
                    if ($('select[name="research_assess_batches"]').find('option:selected').val() == "0") {
                        $('#assess_report_total_items').html("");
                        $('#assess_report_items_priced_higher_than_competitors').html("");
                        $('#assess_report_items_have_more_than_20_percent_duplicate_content').html("");
                        $('#assess_report_items_unoptimized_product_content').html("");
                        $('#assess_report_items_have_product_short_descriptions_that_are_too_short').html("");
                        $('#assess_report_items_have_product_long_descriptions_that_are_too_short').html("");
                    }
                    if (json.iTotalRecords == 0) {
                        $('#assess_report_compare_panel').hide();
                        $('#assess_report_numeric_difference').hide();
                        if ($('select[name="research_assess_batches"]').find('option:selected').val() != "") {
                            $('#summary_message').html(" - Processing data. Check back soon.");
                            //                                $('#research_assess_filter_short_descriptions_panel').show();
                            //                                $('#research_assess_filter_long_descriptions_panel').show();
                            $('#assess_report_items_1_descriptions_pnl').hide();
                            $('#assess_report_items_2_descriptions_pnl').hide();
                        }
                    }
//                    if (json.aaData.length > 0) {
//                        var str = '';
//                        for (var i = 0; i < json.aaData.length; i++) {
//                            var obj = jQuery.parseJSON(json.aaData[i][14]);
//                            if (json.aaData[i][2] != null && json.aaData[i][2] != '' && json.aaData[i][0] != '') {
//                                if (json.aaData[i][2].length > 93)
//                                    str += '<div class="board_item"><span class="span_img">' + json.aaData[i][2] + '</span><br />' + json.aaData[i][0] +
//                                            '<div class="prod_description"><b>URL:</b><br/>' + obj.url + '<br /><br /><b>Product name:</b><br/>' + obj.product_name +
//                                            '<br /><br/><b>Price:</b><br/>' + obj.own_price + '</div></div>';
//                                else
//                                    str += '<div class="board_item"><span>' + json.aaData[i][2] + '</span><br />' + json.aaData[i][0] +
//                                            '<div class="prod_description"><b>URL:</b><br/>' + obj.url + '<br /><br /><b>Product name:</b><br/>' + obj.product_name
//                                            + '<br /><br/><b>Price:</b><br/>' + obj.own_price + '</div></div>';
//                            }
//                        }
//                        if (str == '') {
//                            str = '<p>No images available for this batch</p>';
//                        }
//                        $('#assess_view').html(str);
//                        $('#assess_view .board_item img').on('click', function() {
//                            var info = $(this).parent().find('div.prod_description').html();
//                            showSnap('<img src="' + $(this).attr('src') + '" style="float:left; max-width: 600px; margin-right: 10px">' + info);
//                        });
//                    }

                });
                highChart('short_description_wc');
                $.ajax({
                    type: "POST",
                    url: readBoardSnapUrl,
                    data: {batch_id: $('select[name="research_assess_batches"]').find('option:selected').val()}
                }).done(function(data){
                    if(data.length > 0){
                        var str = '';
                        for(var i=0; i<data.length; i++){
                            var obj = jQuery.parseJSON(data[i][2]);
                            if(data[i][1] != null && data[i][1] != '' && data[i][0]!=''){
                                if(data[i][1].length > 93)
                                  str += '<div class="board_item"><span class="span_img">'+data[i][1]+'</span><br />'+data[i][0]+
                                      '<div class="prod_description"><b>URL:</b><br/>'+obj.url+'<br /><br /><b>Product name:</b><br/>'+obj.product_name+
                                      '<br /><br/><b>Price:</b><br/>'+obj.own_price+'</div></div>';
                                else
                                  str += '<div class="board_item"><span>'+data[i][1]+'</span><br />'+data[i][0]+
                                      '<div class="prod_description"><b>URL:</b><br/>'+obj.url+'<br /><br /><b>Product name:</b><br/>'+obj.product_name
                                      +'<br /><br/><b>Price:</b><br/>'+obj.own_price+'</div></div>';
                            }
                        }                   
                        if(str == ''){
                            str = '<p>No images available for this batch</p>';
                        }
                        $('#assess_view').html(str);
                        $('#assess_view .board_item img').on('click', function(){
                            var info = $(this).parent().find('div.prod_description').html();
                            showSnap('<img src="'+$(this).attr('src')+'" style="float:left; max-width: 600px; margin-right: 10px">'+info);
                        });
                     }
                });
                
                if($("#tableScrollWrapper").length === 0){  
                $('#tblAssess').after('<div id="tableScrollWrapper" style="overflow-x:scroll"></div>');
                $('#tblAssess').appendTo('#tableScrollWrapper');
             }
            },
            "fnRowCallback": function(nRow, aData, iDisplayIndex) {
                $(nRow).attr("add_data", aData[29]);
                return nRow;
            },
            "fnDrawCallback": function(oSettings) {
                tblAssess_postRenderProcessing();
                if (zeroTableDraw) {
                    zeroTableDraw = false;
                    return;
                }
                hideColumns();
                check_word_columns();
            },
            "oLanguage": {
                "sInfo": "Showing _START_ to _END_ of _TOTAL_ records",
                "sInfoEmpty": "Showing 0 to 0 of 0 records",
                "sInfoFiltered": "",
                "sSearch": "Filter:",
                "sLengthMenu": "_MENU_ rows"
            },
            "aoColumns": columns

        });

        $('#tblAssess_length').after('<div id="assess_tbl_show_case" class="assess_tbl_show_case">' +
                '<a id="assess_tbl_show_case_recommendations" data-case="recommendations" class="active_link" title="Recommendations" href="#" >Recommendations</a> |' +
                '<a id="assess_tbl_show_case_report" data-case="report" title="Report" href="#">Summary</a> |' +
                '<a id="assess_tbl_show_case_details" data-case="details" title="Details" href="#">Details</a> |' +
                '<a id="assess_tbl_show_case_details_compare" data-case="details_compare" title="Details_compare" href="#">Compare</a> |' +
                '<a id="assess_tbl_show_case_view" data-case="view" title="Board View" href="#">Board View</a>' +
                '</div>');
        
        $('.dataTables_filter').append('<a id="research_batches_columns" class="ml_5 float_r" title="Customize..." style="display: none;"><img style="width:32px; heihgt: 32px;" src="http://tmeditor.dev//img/settings@2x.png"></a>');
                $('#research_batches_columns').on('click', function() {
                    $('#research_assess_choiceColumnDialog').dialog('open');
                    $('#research_assess_choiceColumnDialog').parent().find('button:first-child').addClass("popupGreen");
                });
        
        $('#assess_tbl_show_case a').on('click', function(event) {
            event.preventDefault();
            if ($(this).text() == 'Details' || $(this).text() == 'Compare') {
                $('#research_batches_columns').show();
            } else {
                $('#research_batches_columns').hide();
            }
            assess_tbl_show_case(this);
        });

    }

    function createTable() {
        var oSettings = $("#tblAssess").dataTable().fnSettings();
        var aoDataa = buildTableParams(oSettings.aoData);
        var newObject = jQuery.extend(true, {}, aoDataa);
        

        $.getJSON(readAssessUrl, aoDataa, function(json) {
            tblAllColumns = [];
            for(p in json.columns){
                if(json.columns[p].sName != undefined){
                    tblAllColumns.push(json.columns[p].sName);
                }
//                
       }
          $('#tblAssess_wrapper').remove();
          var th = '';
            for(var i =0;i<Object.keys(json.columns).length;i++){
                th += '<th with = "100px"></th>';
            }
            var newTable = '<table id="tblAssess" class="tblDataTable"><thead>'+th+'</thead><tbody></tbody></table>';
            $('#dt_tbl').prepend(newTable);

            setTimeout(function() {
                tblAssess = $('#tblAssess').dataTable({
                    "bJQueryUI": true,
//                    "bDestroy": true,
//                    "sScrollX": "100%",
//                "bAutoWidth": false,
//                    "bScrollCollapse": true,
//                        "bServerSide": true,
                    "sPaginationType": "full_numbers",
                    "bProcessing": true,
                    "aaSorting": [[5, "desc"]],
                    "bAutoWidth": false,
                    "aaData": json.aaData,
                    "aoColumns": json.columns,
                    "oLanguage": {
                        "sInfo": "Showing _START_ to _END_ of _TOTAL_ records",
                        "sInfoEmpty": "Showing 0 to 0 of 0 records",
                        "sInfoFiltered": "",
                        "sSearch": "Filter:",
                        "sLengthMenu": "_MENU_ rows"
                    },
                    "fnRowCallback": function(nRow, aData, iDisplayIndex) {
                        $(nRow).attr("add_data", aData[29]);
                        return nRow;
                    },
                    "fnDrawCallback": function(oSettings) {
                        tblAssess_postRenderProcessing();
                        if (zeroTableDraw) {
                            zeroTableDraw = false;
                            return;
                        }
         
                       // check_word_columns();

                    }
                });

                $('#tblAssess').after('<div id="tableScrollWrapper" style="overflow-x:scroll"></div>');
                $('#tblAssess').appendTo('#tableScrollWrapper');

                if (json.ExtraData != undefined) {
                    buildReport(json);
                }
                tblAssess.fnDraw();
                serevr_side = false;
                setTimeout(function() {
                    tblAssess.fnProcessingIndicator(false);
                }, 2000);
                if ($('select[name="research_assess_batches"]').find('option:selected').val() == "0") {
                    $('#assess_report_total_items').html("");
                    $('#assess_report_items_priced_higher_than_competitors').html("");
                    $('#assess_report_items_have_more_than_20_percent_duplicate_content').html("");
                    $('#assess_report_items_unoptimized_product_content').html("");
                    $('#assess_report_items_have_product_short_descriptions_that_are_too_short').html("");
                    $('#assess_report_items_have_product_long_descriptions_that_are_too_short').html("");
                }
                if (json.iTotalRecords == 0) {
                    $('#assess_report_compare_panel').hide();
                    $('#assess_report_numeric_difference').hide();
                    if ($('select[name="research_assess_batches"]').find('option:selected').val() != "") {
                        $('#summary_message').html(" - Processing data. Check back soon.");
                        //                                $('#research_assess_filter_short_descriptions_panel').show();
                        //                                $('#research_assess_filter_long_descriptions_panel').show();
                        $('#assess_report_items_1_descriptions_pnl').hide();
                        $('#assess_report_items_2_descriptions_pnl').hide();
                    }
                }

                $('#tblAssess_length').after('<div id="assess_tbl_show_case" class="assess_tbl_show_case">' +
                        '<a id="assess_tbl_show_case_recommendations" data-case="recommendations" title="Recommendations" href="#">Recommendations</a> |' +
                        '<a id="assess_tbl_show_case_report" data-case="report" title="Report" href="#">Summary</a> |' +
                        '<a id="assess_tbl_show_case_details" data-case="details" title="Details" href="#">Details</a> |' +
                        '<a id="assess_tbl_show_case_details_compare" data-case="details_compare" title="Details_compare" href="#" class="active_link">Compare</a> |' +
                        '<a id="assess_tbl_show_case_graph" data-case="graph" title="Graph" href="#graph">Graph</a> |'+
                        '<a id="assess_tbl_show_case_view" data-case="view" title="Board View" href="#">Board View</a>' +
                        '</div>');
//        $('#research_batches_columns').appendTo('div.dataTables_filter');
                $('.dataTables_filter').append('<a id="research_batches_columns" class="ml_5 float_r" title="Customize..." style="display: none;"><img style="width:32px; heihgt: 32px;" src="http://tmeditor.dev//img/settings@2x.png"></a>');
                $('#research_batches_columns').on('click', function() {
                    $('#research_assess_choiceColumnDialog').dialog('open');
                    $('#research_assess_choiceColumnDialog').parent().find('button:first-child').addClass("popupGreen");
                });
                $('#assess_tbl_show_case a').on('click', function(event) {
                    event.preventDefault();
                    if ($(this).text() == 'Details' || $(this).text() == 'Compare') {
                        $('#research_batches_columns').show();
                    } else {
                        $('#research_batches_columns').hide();
                    }
                    assess_tbl_show_case(this);
                });
               hideColumns();
            }, 1000);
        });
        highChart('short_description_wc');
        $.ajax({
            type: "POST",
            url: readBoardSnapUrl,
            data: {batch_id: $('select[name="research_assess_batches"]').find('option:selected').val()}
        }).done(function(data){
            if(data.length > 0){
                var str = '';
                for(var i=0; i<data.length; i++){
                    var obj = jQuery.parseJSON(data[i][2]);
                    if(data[i][1] != null && data[i][1] != '' && data[i][0]!=''){
                        if(data[i][1].length > 93)
                          str += '<div class="board_item"><span class="span_img">'+data[i][1]+'</span><br />'+data[i][0]+
                              '<div class="prod_description"><b>URL:</b><br/>'+obj.url+'<br /><br /><b>Product name:</b><br/>'+obj.product_name+
                              '<br /><br/><b>Price:</b><br/>'+obj.own_price+'</div></div>';
                        else
                          str += '<div class="board_item"><span>'+data[i][1]+'</span><br />'+data[i][0]+
                              '<div class="prod_description"><b>URL:</b><br/>'+obj.url+'<br /><br /><b>Product name:</b><br/>'+obj.product_name
                              +'<br /><br/><b>Price:</b><br/>'+obj.own_price+'</div></div>';
                    }
                }                   
                if(str == ''){
                    str = '<p>No images available for this batch</p>';
                }
                $('#assess_view').html(str);
                $('#assess_view .board_item img').on('click', function(){
                    var info = $(this).parent().find('div.prod_description').html();
                    showSnap('<img src="'+$(this).attr('src')+'" style="float:left; max-width: 600px; margin-right: 10px">'+info);
                });
             }
        });
       
    }
    $.fn.dataTableExt.oApi.fnGetAllSColumnNames = function(oSettings) {
        allColumns = [];
        for (var i = 0; i < oSettings.aoColumns.length; i++) {
            allColumns.push($.trim(oSettings.aoColumns[i].sName));
        }
        return allColumns;
    }

    $.fn.dataTableExt.oApi.fnGetSColumnIndexByName = function(oSettings, colname) {
        for (var i = 0; i < oSettings.aoColumns.length; i++) {
            if (oSettings.aoColumns[i].sName == $.trim(colname)) {
                return i;
            }
        }
        return -1;
    }

    $.fn.dataTableExt.oApi.fnProcessingIndicator = function(oSettings, onoff) {
        if (typeof(onoff) == 'undefined') {
            onoff = true;
        }
        this.oApi._fnProcessingDisplay(oSettings, onoff);
    };
    var columns = [
        {
            "sTitle": "Snapshot",
            "sName": "snap",
            "sWidth": "10%"
        },
        {
            "sTitle": "Date",
            "sName": "created",
            "sWidth": "3%"
        },
        {
            "sTitle": "Product Name",
            "sName": "product_name",
            "sWidth": "15%",
            "sClass": "product_name_text"
        },
        {
            "sTitle": "item ID",
            "sName": "item_id",
            "sWidth": "15%",
            "sClass": "item_id"
        },
        {
            "sTitle": "Model",
            "sName": "model",
            "sWidth": "15%",
            "sClass": "model"
        },
        {
            "sTitle": "URL",
            "sName": "url",
            "sWidth": "15%",
            "sClass": "url_text"
        },
        {
            "sTitle": "Page Load Time",
            "sName": "Page_Load_Time",
            "sWidth": "15%",
            "sClass": "Page_Load_Time"
        },
        {
            "sTitle": "<span class='subtitle_desc_short' >Short</span> Description",
            "sName": "Short_Description",
            "sWidth": "25%",
            "sClass": "Short_Description"
        },
        {
            "sTitle": "Short Desc <span class='subtitle_word_short' ># Words</span>",
            "sName": "short_description_wc",
            "sWidth": "1%",
            "sClass": "word_short"
        },
        {
            "sTitle": "Meta Keywords",
            "sName": "Meta_Keywords",
            "sWidth": "1%",
            "sClass": "Meta_Keywords"
        },
        {
            "sTitle": "Keywords <span class='subtitle_keyword_short'>Short</span>",
            "sName": "short_seo_phrases",
            "sWidth": "2%",
            "sClass": "keyword_short"
        },
        {
            "sTitle": "<span class='subtitle_desc_long' >Long </span>Description",
            "sName": "Long_Description",
            "sWidth": "2%",
            "sClass": "Long_Description"
        },
        {
            "sTitle": "Long Desc <span class='subtitle_word_long' ># Words</span>",
            "sName": "long_description_wc",
            "sWidth": "1%",
            "sClass": "word_long"
        },
        {
            "sTitle": "Keywords <span class='subtitle_keyword_long'>Long</span>",
            "sName": "long_seo_phrases",
            "sWidth": "2%",
            "sClass": "keyword_long"
        },
        {
            "sTitle" : "Custom Keywords Short Description",
            "sName" : "Custom_Keywords_Short_Description", 
            "sWidth" :  "4%",
            "sClass" : "Custom_Keywords_Short_Description"
            
        },
        {
            "sTitle" : "Custom Keywords Long Description",
            "sName" : "Custom_Keywords_Long_Description", 
            "sWidth" : "4%",
            "sClass" : "Custom_Keywords_Long_Description"
            
        },
        {
            "sTitle" : "Meta Description",
            "sName" : "Meta_Description", 
            "sWidth" : "4%",
            "sClass" : "Meta_Description"
            
        },
        {
            "sTitle" : "Meta Desc <span class='subtitle_word_long' ># Words</span>",
            "sName" : "Meta_Description_Count", 
            "sWidth" : "4%",
            "sClass" : "Meta_Description_Count"
            
        },
        
         {
            "sTitle" : "H1 Tags", 
            "sName":"H1_Tags", 
            "sWidth": "1%",
            "sClass" :  "HTags_1"
        },
        {
            "sTitle" : "Chars", 
            "sName":"H1_Tags_Count", 
            "sWidth": "1%",
            "sClass" :  "HTags"
        },
        {
            "sTitle" : "H2 Tags", 
            "sName":"H2_Tags", 
            "sWidth": "1%",
            "sClass" :  "HTags_2"
        },
        {
            "sTitle" : "Chars", 
            "sName":"H2_Tags_Count", 
            "sWidth": "1%",
            "sClass" :  "HTags"
        },
        {
            "sTitle": "Duplicate Content",
            "sName": "duplicate_content",
            "sWidth": "1%"
        },
        {
            "sTitle": "Content",
            "sName": "column_external_content",
            "sWidth": "2%"
        },
        {
            "sTitle": "Reviews",
            "sName": "column_reviews",
            "sWidth": "3%"
        },
        {
            "sTitle": "Avg Review",
            "sName": "average_review",
            "sWidth": "3%",
            "sClass" :  "average_review"
        },
        {
            "sTitle": "Features",
            "sName": "column_features",
            "sWidth": "4%"
        },
        {
            "sTitle": "Price",
            "sName": "price_diff",
            "sWidth": "2%",
            "sClass": "price_text"
        },
        {
            "sTitle": "Recommendations",
            "sName": "recommendations",
            "sWidth": "15%",
            "bVisible": false,
            "bSortable": false
        },
        {
            "sName": "add_data",
            "bVisible": false
        },
        {
            "sTitle": "Snapshot",
            "sName": "snap1",
            "sWidth": "10%"
        },
        {
            "sTitle": "Product Name",
            "sName": "product_name1",
            "sWidth": "15%"
        },
        {
            "sTitle": "item ID",
            "sName": "item_id1",
            "sWidth": "15%",
            "sClass": "item_id1"
        },
        {
            "sTitle": "Model",
            "sName": "model1",
            "sWidth": "15%",
            "sClass": "model1"
        },
        {
            "sTitle": "URL",
            "sName": "url1",
            "sWidth": "15%"
        },
        {
            "sTitle": "Page Load Time",
            "sName": "Page_Load_Time1",
            "sWidth": "15%",
            "sClass": "Page_Load_Time1"
        },
        {
            "sTitle": "<span class='subtitle_desc_short1' >Short </span> Description",
            "sName": "Short_Description1",
            "sWidth": "15%",
            "sClass": "Short_Description1"
        },
        {
            "sTitle": "Short Desc <span class='subtitle_word_short' ># Words</span>",
            "sName": "short_description_wc1",
            "sWidth": "1%",
            "sClass": "word_short1"
        },
        {
            "sTitle": "Meta Keywords",
            "sName": "Meta_Keywords1",
            "sWidth": "1%",
            "sClass": "Meta_Keywords1"
        },
        {
            "sTitle": "<span class='subtitle_desc_long1' >Long </span>Description",
            "sName": "Long_Description1",
            "sWidth": "2%",
            "sClass": "Long_Description1"
        },
        {
            "sTitle": "Long Desc <span class='subtitle_word_long' ># Words</span>",
            "sName": "long_description_wc1",
            "sWidth": "1%",
            "sClass": "word_long1"
        },
        {
            "sTitle" : "Meta Description",
            "sName" : "Meta_Description1", 
            "sWidth" : "4%",
            "sClass" : "Meta_Description1"
            
        },
        {
            "sTitle" : "Meta Desc <span class='subtitle_word_long' ># Words</span>",
            "sName" : "Meta_Description_Count1", 
            "sWidth" : "4%",
            "sClass" : "Meta_Description_Count1"
            
        },
        {
            "sTitle": "Avg Review",
            "sName": "average_review1",
            "sWidth": "3%",
            "sClass" :  "average_review1"
        },
        {
            "sTitle": "Gap Analysis",
            "sName": "gap",
            "sWidth": "3%",
            "sClass" :  ""
        },

    ];

    tblAssess = $('#tblAssess').dataTable({
        "bJQueryUI": true,
        "bDestroy": true,
        "sPaginationType": "full_numbers",
        "bProcessing": true,
        "aaSorting": [[5, "desc"]],
        "bAutoWidth": false,
        "bServerSide": true,
        "sAjaxSource": readAssessUrl,
        "fnServerData": function(sSource, aoData, fnCallback) {

            aoData = buildTableParams(aoData);
            first_aaData = aoData;
            $.getJSON(sSource, aoData, function(json) {
                if (json.ExtraData != undefined) {
                    buildReport(json);
                }

                fnCallback(json);
                setTimeout(function() {
                    tblAssess.fnProcessingIndicator(false);
                }, 100);
                if ($('select[name="research_assess_batches"]').find('option:selected').val() == "0") {
                    $('#assess_report_total_items').html("");
                    $('#assess_report_items_priced_higher_than_competitors').html("");
                    $('#assess_report_items_have_more_than_20_percent_duplicate_content').html("");
                    $('#assess_report_items_unoptimized_product_content').html("");
                    $('#assess_report_items_have_product_short_descriptions_that_are_too_short').html("");
                    $('#assess_report_items_have_product_long_descriptions_that_are_too_short').html("");
                }
                if (json.iTotalRecords == 0) {
                    $('#assess_report_compare_panel').hide();
                    $('#assess_report_numeric_difference').hide();
                    if ($('select[name="research_assess_batches"]').find('option:selected').val() != "") {
                        $('#summary_message').html(" - Processing data. Check back soon.");
                        //                                $('#research_assess_filter_short_descriptions_panel').show();
                        //                                $('#research_assess_filter_long_descriptions_panel').show();
                        $('#assess_report_items_1_descriptions_pnl').hide();
                        $('#assess_report_items_2_descriptions_pnl').hide();
                    }
                }

            });
             if($("#tableScrollWrapper").length === 0){  
                $('#tblAssess').after('<div id="tableScrollWrapper" style="overflow-x:scroll"></div>');
                $('#tblAssess').appendTo('#tableScrollWrapper');
             }
            highChart('short_description_wc');
            $.ajax({
                type: "POST",
                url: readBoardSnapUrl,
                data: {batch_id: $('select[name="research_assess_batches"]').find('option:selected').val()}
            }).done(function(data){
                if(data.length > 0){
                    var str = '';
                    for(var i=0; i<data.length; i++){
                        var obj = jQuery.parseJSON(data[i][2]);
                        if(data[i][1] != null && data[i][1] != '' && data[i][0]!=''){
                            if(data[i][1].length > 93)
                              str += '<div class="board_item"><span class="span_img">'+data[i][1]+'</span><br />'+data[i][0]+
                                  '<div class="prod_description"><b>URL:</b><br/>'+obj.url+'<br /><br /><b>Product name:</b><br/>'+obj.product_name+
                                  '<br /><br/><b>Price:</b><br/>'+obj.own_price+'</div></div>';
                            else
                              str += '<div class="board_item"><span>'+data[i][1]+'</span><br />'+data[i][0]+
                                  '<div class="prod_description"><b>URL:</b><br/>'+obj.url+'<br /><br /><b>Product name:</b><br/>'+obj.product_name
                                  +'<br /><br/><b>Price:</b><br/>'+obj.own_price+'</div></div>';
                        }
                    }                   
                    if(str == ''){
                        str = '<p>No images available for this batch</p>';
                    }
                    $('#assess_view').html(str);
                    $('#assess_view .board_item img').on('click', function(){
                        var info = $(this).parent().find('div.prod_description').html();
                        showSnap('<img src="'+$(this).attr('src')+'" style="float:left; max-width: 495px; margin-right: 10px"><div style="float:right; width:315px">'+info+'</div>');
                    });
                 }
            });
        },
        "fnRowCallback": function(nRow, aData, iDisplayIndex) {
            $(nRow).attr("add_data", aData[29]);
            return nRow;
        },
        "fnDrawCallback": function(oSettings) {
            tblAssess_postRenderProcessing();
            if (zeroTableDraw) {
                zeroTableDraw = false;
                return;
            }
            hideColumns();
            check_word_columns();
        },
        "oLanguage": {
            "sInfo": "Showing _START_ to _END_ of _TOTAL_ records",
            "sInfoEmpty": "Showing 0 to 0 of 0 records",
            "sInfoFiltered": "",
            "sSearch": "Filter:",
            "sLengthMenu": "_MENU_ rows"
        },
          "aoColumns":columns
    });
function highChart(graphBuild){
    var batch1Value = $('select[name="research_assess_batches"]').find('option:selected').val();
    var batch2Value = $('#research_assess_compare_batches_batch').find('option:selected').val();
    var batch1Name = $('select[name="research_assess_batches"]').find('option:selected').text();
    var batch2Name = $('#research_assess_compare_batches_batch').find('option:selected').text();
    if(batch1Value == false || batch1Value == 0 || typeof batch1Value == 'undefined'){
        batch1Value = -1;
    }
    if(batch2Value == false || batch2Value == 0 || typeof batch2Value == 'undefined'){
        batch2Value = -1;
    }
    $.ajax({
        type: "POST",
        url: readGraphDataUrl,
        data: {
            batch_id: batch1Value,
            batch_compare_id: batch2Value
        }
    }).done(function(data){
//        console.log(data);
        var value1 = [];
        var value2 = [];
        var valueName = [];
        valueName[0] = [];
        valueName[1] = [];
        var valueUrl = [];
        valueUrl[0] = [];
        valueUrl[1] = [];
            /***First Batch - Begin***/
            if(data[0] && data[0].product_name.length > 0){
                valueName[0] = data[0].product_name;
            }
            if(data[0] && data[0].url.length > 0){
                valueUrl[0] = data[0].url;
            }
            /***First Batch - End***/
            /***Second Batch - Begin***/
            if(data[1] && data[1].product_name.length > 0){
                valueName[1] = data[1].product_name;
            }
            if(data[1] && data[1].url.length > 0){
                valueUrl[1] = data[1].url;
            }
            /***Second Batch - End***/
            /***Switch Begin***/
            var graphName1;
            var graphName2;
            switch(graphBuild){
                case 'short_description_wc':{
                    if(data[0] && data[0].short_description_wc.length > 0){
                        value1 = data[0].short_description_wc;
                    }
                    if(data[1] && data[1].short_description_wc.length > 0){
                        value2 = data[1].short_description_wc;
                    }
                    graphName1 = 'Short Description:';
                    graphName2 = 'words';
                }
                  break;
                case 'long_description_wc':{
                    if(data[0] && data[0].long_description_wc.length > 0){
                        value1 = data[0].long_description_wc;
                    }
                    if(data[1] && data[1].long_description_wc.length > 0){
                        value2 = data[1].long_description_wc;
                    }
                    graphName1 = 'Long Description:';
                    graphName2 = 'words';
                }
                  break;
                case 'revision':{
                    if(data[0] && data[0].revision.length > 0){
                        value1 = data[0].revision;
                    }
                    if(data[1] && data[1].revision.length > 0){
                        value2 = data[1].revision;
                    }
                    graphName1 = 'Reviews:';
                    graphName2 = '';
                }
                  break;
                case 'own_price':{
                    if(data[0] && data[0].own_price.length > 0){
                        value1 = data[0].own_price;
                    }
                    if(data[1] && data[1].own_price.length > 0){
                        value2 = data[1].own_price;
                    }
                    graphName1 = 'Price:';
                    graphName2 = '';
                } break;
                case 'Features':{
                    if(data[0] && data[0].Features.length > 0){
                        value1 = data[0].Features;
                    }
                    if(data[1] && data[1].Features.length > 0){
                        value2 = data[1].Features;
                    }
                    graphName1 = 'Features:';
                    graphName2 = '';
                }
                  break;
                case 'h1_word_counts':{
                    if(data[0] && data[0].h1_word_counts.length > 0){
                        value1 = data[0].h1_word_counts;
                    }
                    if(data[1] && data[1].h1_word_counts.length > 0){
                        value2 = data[1].h1_word_counts;
                    }
                    graphName1 = 'H1 count:';
                    graphName2 = 'words';
                }
                  break;
                case 'h2_word_counts':{
                    if(data[0] && data[0].h2_word_counts.length > 0){
                        value1 = data[0].h2_word_counts;
                    }
                    if(data[1] && data[1].h2_word_counts.length > 0){
                        value2 = data[1].h2_word_counts;
                    }
                    graphName1 = 'H2 count:';
                    graphName2 = 'words';
                }
                  break;
                default:{
            
                }
            }
            /***Switch - End***/
            
        var seriesObj;
        if(batch1Value != -1 && batch2Value != -1){
            seriesObj = [
                            {
                                name: batch1Name,
                                data: value1,
                                color: '#2f7ed8'
                            },
                            {
                                name: batch2Name,
                                data: value2,
                                color: '#71a75b'
                         }
                        ];
        } else if(batch2Value == -1){
            seriesObj = [
                            {
                                name: batch1Name,
                                data: value1,
                                color: '#2f7ed8'
                            }
                        ];
        }
        $('#highChartContainer').empty();
        var chart1 = new Highcharts.Chart({
            title: {
                text: ''
            },
            chart: {
                renderTo: 'highChartContainer',
                zoomType: 'x',
                spacingRight: 20
            },
            xAxis: {
                categories: [],
                labels: {
                  enabled: false
                }
            },
            tooltip: {
                shared: true,
                useHTML: true,
                formatter: function() {
                    var result = '<small>'+this.x+'</small><br />';
                    var j;
                    $.each(this.points, function(i, datum) {
                        if(i > 0)
                            result += '<hr style="border-top: 1px solid #2f7ed8;" />';
                        if(datum.series.color == '#2f7ed8')
                            j = 0;
                        else
                            j = 1;
                        result += '<b style="color: '+datum.series.color+';" >' + datum.series.name + '</b>';
                        result += '<br /><span>' + valueName[j][datum.x] + '</span>';
                        result += '<br /><a href="'+valueUrl[j][datum.x]+'" target="_blank" style="color: blue;" >' + valueUrl[j][datum.x] + '</a>';
                        result += '<br /><span>'+graphName1+' ' + datum.y + ' '+graphName2+'</span>';
                    });
                    return result;
                }
            },

            series: seriesObj
        });
        $('.highcharts-button').each(function(i){
            if(i > 0)
                $(this).remove();
        });
    });
    
}
$('#graphDropDown').live('change',function(){
    var graphDropDownValue = $(this).children('option:selected').val();
    highChart(graphDropDownValue);
});
var scrollYesOrNot = true;
    $(document).scroll(function() {
        var docHeight = parseInt($(document).height());
        var windHeight = parseInt($(window).height());
        var scrollTop = parseInt($(document).scrollTop());
        if(window.location.hash == '#board_view' && scrollYesOrNot && (docHeight - windHeight - scrollTop) < 100){
            scrollYesOrNot = false;
            if($('.board_item').length >= 12)
                $('#imgLoader').show();
            setTimeout(function(){

                $.ajax({
                    type: "POST",
                    url: readBoardSnapUrl,
                    data: {batch_id: $('select[name="research_assess_batches"]').find('option:selected').val(),next_id: $('#assess_view .board_item:last-child').children('img').attr('rel')}
                }).done(function(data){
                    $('#imgLoader').hide();
                    if(data.length > 0){
                        var str = '';
                        for(var i=0; i<data.length; i++){
                            var obj = jQuery.parseJSON(data[i][2]);
                            if(data[i][1] != null && data[i][1] != '' && data[i][0]!=''){
                                if(data[i][1].length > 93)
                                  str += '<div class="board_item fadeout" style="display: none;" ><span class="span_img">'+data[i][1]+'</span><br />'+data[i][0]+
                                      '<div class="prod_description"><b>URL:</b><br/>'+obj.url+'<br /><br /><b>Product name:</b><br/>'+obj.product_name+
                                      '<br /><br/><b>Price:</b><br/>'+obj.own_price+'</div></div>';
                                else
                                  str += '<div class="board_item fadeout" style="display: none;"><span>'+data[i][1]+'</span><br />'+data[i][0]+
                                      '<div class="prod_description"><b>URL:</b><br/>'+obj.url+'<br /><br /><b>Product name:</b><br/>'+obj.product_name
                                      +'<br /><br/><b>Price:</b><br/>'+obj.own_price+'</div></div>';
                            }
                        }                   
                        if(str == ''){
                            str = '<p>No images available for this batch</p>';
                        }
                        $('#assess_view').append(str);
                        $('#assess_view .board_item img').on('click', function(){
                            var info = $(this).parent().find('div.prod_description').html();
                            showSnap('<img src="'+$(this).attr('src')+'" style="float:left; max-width: 600px; margin-right: 10px">'+info);
                        });
                        $('.fadeout').each(function(){
                            $(this).fadeIn('slow');
                            $(this).removeClass('fadeout');
                        })
                        scrollYesOrNot = true;
                     }
                });

            },500);
            
        }
    });

    $('#research_batches_columns').appendTo('div.dataTables_filter');
    $('#tblAssess_length').after($('#assess_tbl_show_case'));
    $('#assess_tbl_show_case a').on('click', function(event) {
//        event.preventDefault();
        if ($(this).text() == 'Details' || $(this).text() == 'Compare') {
            $('#research_batches_columns').show();
        } else {
            $('#research_batches_columns').hide();
        }
        assess_tbl_show_case(this);
    });

    function showSnap(data) {
        $("#preview_crawl_snap_modal").modal('show');
        $("#preview_crawl_snap_modal").css({'left': 'inherit'});
        $("#preview_crawl_snap_modal").css({'margin': '-250px auto'});
        $("#preview_crawl_snap_modal").css({'width': '1000px'});
        $("#preview_crawl_snap_modal .snap_holder").html(data);
        $("#bi_expand_bar_cnt").click(function(e) {
            if ($("#bi_info_bar").is(":visible")) {
                $("#bi_info_bar").fadeOut('fast', function() {
                    $("#bi_expand_bar_cnt > i").removeClass('icon-arrow-left');
                    $("#bi_expand_bar_cnt > i").addClass('icon-arrow-right');
                    $("#preview_crawl_snap_modal").animate({
                        width: '652px'
                    }, 200);
                });
            } else {
                $("#bi_expand_bar_cnt > i").removeClass('icon-arrow-right');
                $("#bi_expand_bar_cnt > i").addClass('icon-arrow-left');
                $("#preview_crawl_snap_modal").animate({
                    width: '850px'
                }, 200, function() {
                    $("#bi_info_bar").fadeIn('fast');
                });
            }
        });

        $(".left_snap").on("click", function() {
            var im = '';
            var cur_img, im_prev, row, row_prev, ob;
            row = $(this).parent().parent();
            cur_img = row.find("div.snap_area").find('img').attr('src');
            $("#tblAssess tbody tr img").each(function() {
                if (cur_img == $(this).attr('src')) {
                    im = $(this);
                    row_prev = $(this).parent().parent().prev();
                    im_prev = row_prev.find('img').attr("src");
                }
            });
            if (im != '') {
                ob = JSON.parse(row_prev.attr('add_data'));
                row.find("div.snap_area").find('img').attr({'src': im_prev});
                row.find("div.info_area").find('span.product_name').html(ob.product_name);
                row.find("div.info_area").find('span.url').html(ob.url);
                row.find("div.info_area").find('span.price').html(ob.price_diff);
            }
            return false;
        });

        $(".right_snap").on("click", function() {
            var im = '';
            var cur_img, im_next, row, row_next, ob;
            row = $(this).parent().parent();
            cur_img = row.find("div.snap_area").find('img').attr('src');
            $("#tblAssess tbody tr img").each(function() {
                if (cur_img == $(this).attr('src')) {
                    im = $(this);
                    row_next = $(this).parent().parent().next();
                    im_next = row_next.find('img').attr("src");
                }
            });
            if (im != '') {
                ob = JSON.parse(row_next.attr('add_data'));
                row.find("div.snap_area").find('img').attr({'src': im_next});
                row.find("div.info_area").find('span.product_name').html(ob.product_name);
                row.find("div.info_area").find('span.url').html(ob.url);
                row.find("div.info_area").find('span.price').html(ob.price_diff);
            }
            return false;
        });


    }

    function assess_tbl_show_case(obj) {
        if (obj) {
            $(obj).parent().find('a').removeClass('active_link');
            $(obj).addClass('active_link');
            if ($(obj).text() == 'Report') {
                $(".research_assess_flagged").css('display', 'none');
            } else {
                $(".research_assess_flagged").css('display', 'inline');
            }
            hideColumns();
            tblAssess_postRenderProcessing();
            check_word_columns();
        }
    }

    function tblAssess_postRenderProcessing() {
        $('#tblAssess td input:hidden').each(function() {
            $(this).parent().addClass('highlightPrices');
        });
        $('#tblAssess tbody tr').each(function() {
            var row_height = $(this).height();
            if (row_height > 5) {
                $(this).find('table.url_table').height('auto');
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
        if (report.summary.items_have_more_than_20_percent_duplicate_content == 0) {
            $(".items_have_more_than_20_percent_duplicate_content").hide();
        } else {
            $('#assess_report_items_have_more_than_20_percent_duplicate_content').html(report.summary.items_have_more_than_20_percent_duplicate_content);
            $(".items_have_more_than_20_percent_duplicate_content").show();
        }
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
            if (report.summary.short_wc_total_not_0 == 0 && report.summary.long_wc_total_not_0 != 0) {
                $('#assess_report_items_have_product_descriptions_that_are_too_short').html(report.summary.items_long_products_content_short);
                $('#assess_report_items_have_product_descriptions_that_are_less_than_value').html(report.summary.long_description_wc_lower_range);
            } else if (report.summary.short_wc_total_not_0 != 0 && report.summary.long_wc_total_not_0 == 0) {
                $('#assess_report_items_have_product_descriptions_that_are_too_short').html(report.summary.items_short_products_content_short);
                $('#assess_report_items_have_product_descriptions_that_are_less_than_value').html(report.summary.short_description_wc_lower_range);
            } else if (report.summary.short_wc_total_not_0 == 0 && report.summary.long_wc_total_not_0 == 0) {
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

    function comparison_details_load(url) {
        var batch_id = $("select[name='research_assess_batches']").find("option:selected").val();
        var data = {
            batch_id: batch_id
        };
        if (url == undefined) {
            url = base_url + 'index.php/assess/comparison_detail';
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



    $(document).on('click', '#comparison_pagination a', function(event) {
        event.preventDefault();
        comparison_details_load($(this).attr('href'));
    });

    $(document).on('change', '#assessDetailsDialog_chkIncludeInReport', function() {
        var research_data_id = $('#assessDetailsDialog_chkIncludeInReport').attr('research_data_id');
        var include_in_report = $(this).is(':checked');
        var data = {
            research_data_id: research_data_id,
            include_in_report: include_in_report
        };
        $.post(
                base_url + 'index.php/assess/include_in_report',
                data,
                function(data) {
                }
        );
    });

    $(document).on('click', 'i.snap_ico', function() {
        var snap = "webshoots/" + $(this).attr('snap');
        var row = $(this).parent().parent().parent().parent().parent().parent();
        var ob = JSON.parse(row.attr('add_data'));
        var txt = '<div class="info_area" style="max-width: 240px;"><div id="bi_info_bar" style="float: left; width: 200px; padding-top: 20px; display: block;">' +
                '<p style="font-size: 16px;margin-bottom: 20px;">'+ob.product_name+'</p><p><b>URL:</b><br/><span class="ur">' +
                ob.url + '</span></p>' +
                '<p><b>Product name:</b><br/><span class="product_name">' + ob.product_name + '</span></p>' +
                '<p><b>Price:</b><br/><span class="price">' + ob.price_diff + '</span></p></div><div style="float: right; width: 40px;">' +
                '<button id="bi_expand_bar_cnt" type="button" class="btn btn-success"><i class="icon-white icon-arrow-left"></i></button></div></div>';
        showSnap('<div class="snap_area"><a target="_blank" href=""><img src="' + base_url + snap + '"></a></div>' + txt);
    });
    
    

    $('#tblAssess tbody').live('click',function(event) {
        if ($(event.target).is('a')) {
            return;
        }
        if ($(event.target).is('i.snap_ico')) {
            return;
        }
        if ($(event.target).is('td.sorting_1') || $(event.target).is('img')) {
            var str = '';
            var row, ob;
            if ($(event.target).attr('src') != undefined) {
                str = $(event.target).attr('src');
                ob = JSON.parse($(event.target).parents('tr').attr('add_data'));
            } else if ($(event.target).children().attr('src') != undefined) {
                str = $(event.target).children().attr('src');
                ob = JSON.parse($(event.target).children().parents('tr').attr('add_data'));
            }

            var txt = '<div class="info_area" style="max-width: 240px;"><div id="bi_info_bar" style="float: left; width: 200px; padding-top: 20px; display: block;">' +
                    '<p style="font-size: 16px;margin-bottom: 20px;">'+ob.product_name+'</p><p><b>URL:</b><br/><span class="url">' + ob.url + '</span></p>' +
                    '<p><b>Product name:</b><br/><span class="product_name">' + ob.product_name + '</span></p>' +
                    '<p><b>Price:</b><br/><span class="price">' + ob.price_diff + '</span></p></div><div style="float: right; width: 40px;">' +
                    '<button id="bi_expand_bar_cnt" type="button" class="btn btn-success"><i class="icon-white icon-arrow-left"></i></button></div></div>';
            showSnap('<div class="snap_area"><a target="_blank" href=""><img src="' + str + '"></a></div>' + txt);
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
        $('#assessDetails_Model').val(add_data.model);
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

        var chk_include_in_report = '<div id="assess_details_dialog_options" style="float: left; margin-left:30px;"><label><input id="assessDetailsDialog_chkIncludeInReport" type="checkbox">&nbspInclude in report</label></div>';
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

////tblAssess tbody  click end


    $('#assessDetailsDialog').dialog({
        autoOpen: false,
        modal: true,
        resizable: false,
        buttons: {
            'Close': {
                text: 'Cancel',
                click: function() {
                    $(this).dialog('close');
                }
            },
            'Save': {
                text: 'Save',
                id: 'assessDetailsDialog_btnSave',
                class: 'btn-success',
                click: function() {
                    //saveData();
                }
            },
            'Copy': {
                text: 'Copy',
                id: 'assessDetailsDialog_btnCopy',
                style: 'margin-right:275px',
                click: function() {
                    copyToClipboard(textToCopy);
                }
            },
            'Re-Crawl"': {
                text: 'Re-Crawl',
                id: 'assessDetailsDialog_btnReCrawl',
                style: 'margin-right:-210px; float:right; display:none',
                click: function() {
                     $.post(base_url+'index.php/site_crawler/crawl_all', {
                         recrawl: 1,
                         batch_id: $('select[name="research_assess_batches"]').find('option:selected').val(),
                         url: $('input#assessDetails_url').val()
                     }, function(data) {
                        alert('Re-crawl proccess was successful');
                     });
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

    function saveData(){
        var data = {
            product_name: $('input#assessDetails_ProductName').val(),
            model: $('input#assessDetails_Model').val(),
            url: $('input#assessDetails_url').val(),
            price: $('input#assessDetails_Price').val(),
            short_description: $('textarea#assessDetails_ShortDescription').val(),
            short_seo: $('input#assessDetails_ShortSEO').val(),
            long_description: $('textarea#assessDetails_LongDescription').val(),
            long_seo: $('input#assessDetails_LongSEO').val(),
            description: $('textarea#assessDetails_Description').val(),
            seo: $('input#assessDetails_SEO').val(),
            batch_id: $("select[name='research_assess_batches']").find("option:selected").val()
        };
        $.post(
            base_url + 'index.php/assess/save_statistic_data',
            data,
            function(data) {
                $('#assessDetailsDialog').dialog('close');
                readAssessData();
            }
        );
    }

    function copyToClipboard(text) {
        window.prompt("Copy to clipboard: Ctrl+C, Enter (or Esc)", text);
    }

    $(document).on('click', '#assess_details_delete_from_batch', function() {
        if (confirm('Are you sure you want to delete this item?')) {
            var batch_id = $("select[name='research_assess_batches']").find("option:selected").val();
            var research_data_id = $('#assessDetailsDialog_chkIncludeInReport').attr('research_data_id');
            var data = {
                batch_id: batch_id,
                research_data_id: research_data_id
            };
            $.post(
                    base_url + 'index.php/assess/delete_from_batch',
                    data,
                    function() {
                        $('#assessDetailsDialog').dialog('close');
                        readAssessData();
                    }
            );
        }
    });

    $('select[name="research_assess_customers"]').on("change", function(res) {
        var research_assess_batches = $("select[name='research_assess_batches']");
        $.post(base_url + 'index.php/assess/filterBatchByCustomerName', {
            'customer_name': res.target.value
        }, function(data) {
            if (data.length > 0) {
                research_assess_batches.empty();
                for (var i = 0; i < data.length; i++) {
                    research_assess_batches.append('<option value="' + data[i]['id'] + '">' + data[i]['title'] + '</option>');
                }
            } else if (data.length == 0 && res.target.value != "select customer") {
                research_assess_batches.empty();
            }
            $('#research_assess_update').click();
        });
        var own_customer = $(this).val();
        fill_lists_batches_compare(own_customer);
        check_word_columns();
    });

    $('#research_assess_flagged').live('click', function() {
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
                function(data) {
                    research_assess_compare_batches_customer.empty();
                    if (data) {
                        $.each(data, function(i, v) {

                            research_assess_compare_batches_customer.append('<option value="' + v.toLowerCase() + '">' + v + '</option>');

                        });
                        research_assess_compare_batches_customer.find('option[value="' + own_customer + '"]').remove();
                    }
                }
        );

        $.get(
                base_url + 'index.php/assess/batches_get_all',
                {},
                function(data) {
                    research_assess_compare_batches_batch.empty();
                    if (data) {

                        $.each(data, function(i, v) {

                            research_assess_compare_batches_batch.append('<option value="' + v.id + '">' + v.value + '</option>');
                            if (i == 0) {

                                research_assess_compare_batches_batch.append('<option value="all">All</option>');

                            }

                        });
                        var own_batch_id = $("select[name='research_assess_batches']").find("option:selected").val();
                        research_assess_compare_batches_batch.find('option[value="' + own_batch_id + '"]').remove();
                    }
                }
        );
    }

    $('#research_assess_compare_batches_customer').change(function(res) {
        var research_assess_compare_batches_batch = $("#research_assess_compare_batches_batch");
        $.post(base_url + 'index.php/assess/filterBatchByCustomerName', {
            'customer_name': res.target.value
        }, function(data) {
            if (data.length > 0) {
                research_assess_compare_batches_batch.empty();
                for (var i = 0; i < data.length; i++) {
                    research_assess_compare_batches_batch.append('<option value="' + data[i]['id'] + '">' + data[i]['title'] + '</option>');
                    if (i == 0 && $.trim($('#research_assess_compare_batches_customer').val()) == "select customer") {

                        research_assess_compare_batches_batch.append('<option value="all">' + "All" + '</option>');
                    }
                }
            } else if (data.length == 0 && res.target.value != "select customer") {
                research_assess_compare_batches_batch.empty();
            }
        });
    });

    $('#research_assess_compare_batches_batch').change(function() {
        var selectedBatch = $(this).find("option:selected").text();
        $.post(base_url + 'index.php/assess/filterCustomerByBatch', {
            'batch': selectedBatch
        }, function(data) {
            var research_assess_compare_batches_customer = $('#research_assess_compare_batches_customer');
            if (data != '') {
                research_assess_compare_batches_customer.val(data.toLowerCase()).prop('selected', true);
            } else {
                research_assess_compare_batches_customer.val('select customer').prop('selected', true);
            }
            if (selectedBatch.length == 0)
                research_assess_compare_batches_customer.val('select customer').prop('selected', true);
        });
    });

    $('#research_assess_compare_batches_reset').click(function() {
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
                ExtraData: {
                    report: {
                        summary: {
                            total_items: '',
                            items_priced_higher_than_competitors: '',
                            items_have_more_than_20_percent_duplicate_content: '',
                            items_unoptimized_product_content: '',
                            items_short_products_content: ''
                        }
                    }
                }
            }
            buildReport(data);
        }
        $.post(base_url + 'index.php/assess/filterCustomerByBatch', {
            'batch': selectedBatch
        }, function(data) {
            var research_assess_customers = $('select[name="research_assess_customers"]');
            if (data != '') {
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
        if (typeof data != 'undefined') {
            if (data.length > 0) {
                var str = '';
                for (var i = 0; i < data.length; i++) {
                    if (data[i][2] != null && data[i][2] != '' && data[i][0] != '') {
                        str += '<div class="board_item"><span>' + data[i][2] + '</span><br />' + data[i][0] + '</div>';
                    }
                }
                if (str == '') {
                    str = '<p>No images available for this batch</p>';
                }
                $('#assess_view').html(str);
                $('#assess_view .board_item img').on('click', function() {
                    showSnap('<img src="' + $(this).attr('src') + '">');
                });
            }
        }
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


        if ($("#research_assess_compare_batches_batch").val() == 'all') {
            
            createTable();
            serevr_side = false;
            return;
        } else {
            if (!serevr_side) {
                
                //$("#tblAssess").dataTable().fnClearTable();
                //$('#tblAssess_wrapper').remove();
                createTableByServerSide();
                tblAllColumns = tblAssess.fnGetAllSColumnNames();
                serevr_side = true;

            } else {
                serevr_side = true;
                readAssessData();

            }
        }


        addColumn_url_class();
        check_word_columns();

    });

    function addColumn_url_class() {
        //Denis add class to URL column
        if ($("#column_url").attr('checked') == 'checked') {

            table = $('#assess_tbl_show_case').find('.active_link').data('case')
            column = '';
            if (table == 'recommendations') {
                column = 'td:eq(1)';
            } else if (table == 'details') {
                column = 'td:eq(2)';
            }

            //			setTimeout(function(){
            //				//console.log( $("#tblAssess").html() );
            //				$("#tblAssess").find('tr').each(function(){
            //					//$(this).find('td:eq(2)').addClass('column_url');
            //					$(this).find(column).addClass('column_url');
            //				});
            //			}, 2000);
            $("#tblAssess").find('tr').each(function() {
                $(this).find(column).addClass('column_url');
            });
        }
        //----------------------
    }

   function check_word_columns() {
        var word_short_num = 0;
        var word_short_num1 = 0;
        var word_short_num2 = 0;
        var word_short_num3 = 0;
        var word_short_num4 = 0;
        var word_long_num = 0;
        var word_long_num1 = 0;
        var word_long_num2 = 0;
        var word_long_num3 = 0;
        var word_long_num4 = 0;
        var Meta_Description =0;
        var Meta_Description1 =0;
        var Meta_Description2 =0;
        var Meta_Description3 =0;
        var Meta_Description4 =0;
        var HTags_1 = 0;
        var HTags_2 = 0;
        var item_id = 0;
        var item_id1 = 0;
        var item_id2 = 0;
        var item_id3 = 0;
        var item_id4 = 0;
        var Meta_Keywords = 0;
        var Meta_Keywords1 = 0;
        var Meta_Keywords2 = 0;
        var Meta_Keywords3 = 0;
        var Meta_Keywords4 = 0;
        var Page_Load_Time = 0;
        var Page_Load_Time1 = 0;
        var Page_Load_Time2 = 0;
        var Page_Load_Time3 = 0;
        var Page_Load_Time4 = 0;
        var Short_Description = 0;
        var Short_Description1 = 0;
        var Short_Description2 = 0;
        var Short_Description3 = 0;
        var Short_Description4 = 0;
        var Long_Description = 0;
        var Long_Description1 = 0;
        var Long_Description2 = 0;
        var Long_Description3 = 0;
        var Long_Description4 = 0;
        var average_review = 0;
        var average_review1 = 0;
        var average_review2 = 0;
        var average_review3 = 0;
        var average_review4 = 0;
        var model = 0;
        var model1 = 0;
        var model2 = 0;
        var model3 = 0;
        var model4 = 0;
        var Custom_Keywords_Short_Description = 0;
        var Custom_Keywords_Long_Description = 0;
        $('td.word_short').each(function() {
            var txt = parseInt($(this).text());
            if (txt > 0) {
                word_short_num += 1;
            }
        });
        $('td.word_short1').each(function() {
            var txt = parseInt($(this).text());
            if (txt > 0) {
                word_short_num1 += 1;
            }
        });
        $('td.word_short2').each(function() {
            var txt = parseInt($(this).text());
            if (txt > 0) {
                word_short_num2 += 1;
            }
        });
        $('td.word_short3').each(function() {
            var txt = parseInt($(this).text());
            if (txt > 0) {
                word_short_num3 += 1;
            }
        });
        $('td.word_short4').each(function() {
            var txt = parseInt($(this).text());
            if (txt > 0) {
                word_short_num4 += 1;
            }
        });
        $('td.word_long').each(function() {
            var txt = parseInt($(this).text());
            if (txt > 0) {
                word_long_num += 1;
            }
        });
        $('td.word_long1').each(function() {
            var txt = parseInt($(this).text());
            if (txt > 0) {
                word_long_num1 += 1;
            }
        });
        $('td.word_long2').each(function() {
            var txt = parseInt($(this).text());
            if (txt > 0) {
                word_long_num2 += 1;
            }
        });
        $('td.word_long3').each(function() {
            var txt = parseInt($(this).text());
            if (txt > 0) {
                word_long_num3 += 1;
            }
        });
        $('td.word_long4').each(function() {
            var txt = parseInt($(this).text());
            if (txt > 0) {
                word_long_num4 += 1;
            }
        });
        $('td.Custom_Keywords_Short_Description').each(function() {
            if ($(this).text() !='') {
                Custom_Keywords_Short_Description += 1;
            }
        });
        $('td.Custom_Keywords_Long_Description').each(function() {
            
            if ($(this).text()!='') {
                Custom_Keywords_Long_Description += 1;
            }
        });
        $('td.HTags_1').each(function() {
            
            if ($(this).text()!='') {
                HTags_1 += 1;
            }
        });
        $('td.HTags_2').each(function() {
            
            if ($(this).text()!='') {
                HTags_2 += 1;
            }
        });
        $('td.Meta_Description').each(function() {
            
            if ($(this).text()!='') {
                Meta_Description += 1;
            }
        });
        $('td.Meta_Description1').each(function() {
            
            if ($(this).text()!='') {
                Meta_Description1 += 1;
            }
        });
        $('td.Meta_Description2').each(function() {
            
            if ($(this).text()!='') {
                Meta_Description2 += 1;
            }
        });
        $('td.Meta_Description3').each(function() {
            
            if ($(this).text()!='') {
                Meta_Description3 += 1;
            }
        });
        $('td.Meta_Description4').each(function() {
            
            if ($(this).text()!='') {
                Meta_Description4 += 1;
            }
        });
        $('td.item_id').each(function() {
            
           var txt = parseInt($(this).text());
            if (txt > 0) {
                item_id += 1;
            }
        });
        $('td.item_id1').each(function() {
            
           var txt = parseInt($(this).text());
            if (txt > 0) {
                item_id1 += 1;
            }
        });
        $('td.item_id2').each(function() {
            
           var txt = parseInt($(this).text());
            if (txt > 0) {
                item_id2 += 1;
            }
        });
        $('td.item_id3').each(function() {
            
           var txt = parseInt($(this).text());
            if (txt > 0) {
                item_id3 += 1;
            }
        });
        $('td.item_id4').each(function() {
            
           var txt = parseInt($(this).text());
            if (txt > 0) {
                item_id4 += 1;
            }
        });
        $('td.model').each(function() {
            if ($(this).text()!='') {
                model += 1;
            }
        });
        $('td.model1').each(function() {
            if ($(this).text()!='') {
                model1 += 1;
            }
        });
        $('td.model2').each(function() {
            if ($(this).text()!='') {
                model2 += 1;
            }
        });
        $('td.model3').each(function() {
            if ($(this).text()!='') {
                model3 += 1;
            }
        });
        $('td.model4').each(function() {
            if ($(this).text()!='') {
                model4 += 1;
            }
        });
        $('td.Meta_Keywords').each(function() {
            if ($(this).text()!='') {
                Meta_Keywords += 1;
            }
        });
        $('td.Meta_Keywords1').each(function() {
            if ($(this).text()!='') {
                Meta_Keywords1 += 1;
            }
        });
        $('td.Meta_Keywords2').each(function() {
            if ($(this).text()!='') {
                Meta_Keywords2 += 1;
            }
        });
        $('td.Meta_Keywords3').each(function() {
            if ($(this).text()!='') {
                Meta_Keywords3 += 1;
            }
        });
        $('td.Meta_Keywords4').each(function() {
            if ($(this).text()!='') {
                Meta_Keywords4 += 1;
            }
        });
        $('td.Page_Load_Time').each(function() {
            if ($(this).text()!='') {
                Page_Load_Time += 1;
            }
        });
        $('td.Page_Load_Time1').each(function() {
            if ($(this).text()!='') {
                Page_Load_Time1 += 1;
            }
        });
        $('td.Page_Load_Time2').each(function() {
            if ($(this).text()!='') {
                Page_Load_Time2 += 1;
            }
        });
        $('td.Page_Load_Time3').each(function() {
            if ($(this).text()!='') {
                Page_Load_Time3 += 1;
            }
        });
        $('td.Page_Load_Time4').each(function() {
            if ($(this).text()!='') {
                Page_Load_Time4 += 1;
            }
        });
        $('td.average_review').each(function() {
            if ($(this).text()!='') {
                average_review += 1;
            }
        });
        $('td.average_review1').each(function() {
            if ($(this).text()!='') {
                average_review1 += 1;
            }
        });
        $('td.average_review2').each(function() {
            if ($(this).text()!='') {
                average_review2 += 1;
            }
        });
        $('td.average_review3').each(function() {
            if ($(this).text()!='') {
                average_review3 += 1;
            }
        });
        $('td.average_review4').each(function() {
            if ($(this).text()!='') {
                average_review4 += 1;
            }
        });
        $('td.Short_Description').each(function() {
            if ($(this).text()!='') {
                Short_Description += 1;
            }
        });
        $('td.Short_Description1').each(function() {
            if ($(this).text()!='') {
                Short_Description1 += 1;
            }
        });
        $('td.Short_Description2').each(function() {
            if ($(this).text()!='') {
                Short_Description2 += 1;
            }
        });
        $('td.Short_Description3').each(function() {
            if ($(this).text()!='') {
                Short_Description3 += 1;
            }
        });
        $('td.Short_Description4').each(function() {
            if ($(this).text()!='') {
                Short_Description4 += 1;
            }
        });
        $('td.Long_Description').each(function() {
            if ($(this).text()!='') {
                Long_Description += 1;
            }
        });
        $('td.Long_Description1').each(function() {
            if ($(this).text()!='') {
                Long_Description1 += 1;
            }
        });
        $('td.Long_Description2').each(function() {
            if ($(this).text()!='') {
                Long_Description2 += 1;
            }
        });
        $('td.Long_Description3').each(function() {
            if ($(this).text()!='') {
                Long_Description3 += 1;
            }
        });
        $('td.Long_Description4').each(function() {
            if ($(this).text()!='') {
                Long_Description4 += 1;
            }
        });
     
        $.each(tblAllColumns, function(index, value) {
            if ((value == 'short_description_wc' && word_short_num == 0) || (value == 'long_description_wc' && word_long_num == 0)) {
                tblAssess.fnSetColumnVis(index, false, false);
            }
            if ((value == 'short_description_wc1' && word_short_num1 == 0) || (value == 'long_description_wc1' && word_long_num1 == 0)) {
                tblAssess.fnSetColumnVis(index, false, false);
            }
            if ((value == 'short_description_wc2' && word_short_num2 == 0) || (value == 'long_description_wc2' && word_long_num2 == 0)) {
                tblAssess.fnSetColumnVis(index, false, false);
            }
            if ((value == 'short_description_wc3' && word_short_num3 == 0) || (value == 'long_description_wc3' && word_long_num3 == 0)) {
                tblAssess.fnSetColumnVis(index, false, false);
            }
            if ((value == 'short_description_wc4' && word_short_num4 == 0) || (value == 'long_description_wc4' && word_long_num4 == 0)) {
                tblAssess.fnSetColumnVis(index, false, false);
            }
            if ((value == 'short_seo_phrases' && word_short_num == 0) || (value == 'long_seo_phrases' && word_long_num == 0)) {
                tblAssess.fnSetColumnVis(index, false, false);
            }
            if((value == 'Custom_Keywords_Short_Description' && Custom_Keywords_Short_Description == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
            }
            if((value == 'Custom_Keywords_Long_Description' && Custom_Keywords_Long_Description == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
            }
            if((value == 'item_id' && item_id == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
            }
            if((value == 'item_id1' && item_id1 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
            }
            if((value == 'item_id2' && item_id2 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
            }
            if((value == 'item_id3' && item_id3 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
            }
            if((value == 'item_id4' && item_id4 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
            }
            if((value == 'Meta_Keywords' && Meta_Keywords == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
            }
            if((value == 'Meta_Keywords1' && Meta_Keywords1 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
            }
            if((value == 'Meta_Keywords2' && Meta_Keywords2 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
            }
            if((value == 'Meta_Keywords3' && Meta_Keywords3 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
            }
            if((value == 'Meta_Keywords4' && Meta_Keywords4 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
            }
            if((value == 'model' && model == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
            }
            if((value == 'model1' && model1 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
            }
            if((value == 'model2' && model2 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
            }
            if((value == 'model3' && model3 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
            }
            if((value == 'model4' && model4 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
            }
            if((value == 'Meta_Description' && Meta_Description == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
                tblAssess.fnSetColumnVis(index+1, false, false);
            }
            if((value == 'Meta_Description1' && Meta_Description1 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
                tblAssess.fnSetColumnVis(index+1, false, false);
            }
            if((value == 'Meta_Description2' && Meta_Description2 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
                tblAssess.fnSetColumnVis(index+1, false, false);
            }
            if((value == 'Meta_Description3' && Meta_Description3 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
                tblAssess.fnSetColumnVis(index+1, false, false);
            }
            if((value == 'Meta_Description4' && Meta_Description4 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
                tblAssess.fnSetColumnVis(index+1, false, false);
            }
             if((value == 'H1_Tags' && HTags_1 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
                tblAssess.fnSetColumnVis(index+1, false, false);
            }

            if((value == 'H2_Tags' && HTags_2 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
                tblAssess.fnSetColumnVis(index+1, false, false);
            }
            if((value == 'Page_Load_Time' && Page_Load_Time == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
               
            }
            if((value == 'Page_Load_Time1' && Page_Load_Time1 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
               
            }
            if((value == 'Page_Load_Time2' && Page_Load_Time2 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
               
            }
            if((value == 'Page_Load_Time3' && Page_Load_Time3 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
               
            }
            if((value == 'Page_Load_Time4' && Page_Load_Time4 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
               
            }
            if((value == 'average_review' && average_review == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
               
            }
            if((value == 'average_review1' && average_review1 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
               
            }
            if((value == 'average_review2' && average_review2 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
               
            }
            if((value == 'average_review3' && average_review3 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
               
            }
            if((value == 'average_review4' && average_review4 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
               
            }
            if((value == 'Short_Description' && Short_Description == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
                
            }
            if((value == 'Short_Description1' && Short_Description1 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
               
            }
            if((value == 'Short_Description2' && Short_Description2 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
                
            }
            if((value == 'Short_Description3' && Short_Description3 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
               
            }
            if((value == 'Short_Description4' && Short_Description4 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
                
            }
            if((value == 'Long_Description' && Long_Description == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
                
            }
            if((value == 'Long_Description1' && Long_Description1 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
                
            }
            if((value == 'Long_Description2' && Long_Description2 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
                
            }
            if((value == 'Long_Description3' && Long_Description3 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
                
            }
            if((value == 'Long_Description4' && Long_Description4 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
                
            }
        });
//        $('.subtitle_word_long').show();
//        $('.subtitle_word_short').show();
//        $('.subtitle_keyword_short').show();
//        $('.subtitle_keyword_long').show();
        
        if(Long_Description == 0 && Short_Description !=0){
            $('.subtitle_desc_short').text('Product ')
        }else if(Short_Description == 0 && Long_Description != 0){
            $('.subtitle_desc_long').text('Product ')
        }else{
            $('.subtitle_desc_long').text('Long ')
            $('.subtitle_desc_short').text('Short ')
        }
        if(Long_Description1 == 0 && Short_Description1 !=0){
            $('.subtitle_desc_short1').text('Product ')
        }else if(Short_Description1 == 0 && Long_Description1 != 0){
            $('.subtitle_desc_long1').text('Product ')
        }else{
            $('.subtitle_desc_long1').text('Long ')
            $('.subtitle_desc_short1').text('Short ')
        }
        if(Long_Description2 == 0 && Short_Description2 !=0){
            $('.subtitle_desc_short2').text('Product ')
        }else if(Short_Description2 == 0 && Long_Description2 != 0){
            $('.subtitle_desc_long2').text('Product ')
        }else{
            $('.subtitle_desc_long2').text('Long ')
            $('.subtitle_desc_short2').text('Short ')
        }
        if(Long_Description3 == 0 && Short_Description3 !=0){
            $('.subtitle_desc_short3').text('Product ')
        }else if(Short_Description3 == 0 && Long_Description3 != 0){
            $('.subtitle_desc_long3').text('Product ')
        }else{
            $('.subtitle_desc_long3').text('Long ')
            $('.subtitle_desc_short3').text('Short ')
        }
        if(Long_Description4 == 0 && Short_Description4 !=0){
            $('.subtitle_desc_short4').text('Product ')
        }else if(Short_Description4 == 0 && Long_Description4 != 0){
            $('.subtitle_desc_long4').text('Product ')
        }else{
            $('.subtitle_desc_long4').text('Long ')
            $('.subtitle_desc_short4').text('Short ')
        }
        
        
//        if (word_short_num == 0 && word_long_num != 0) {
//            $('.subtitle_word_long').hide();
//            $('.subtitle_keyword_long').hide();
//        } else if (word_short_num != 0 && word_long_num == 0) {
//            $('.subtitle_word_short').hide();
//            $('.subtitle_keyword_short').hide();
//        }
        
    }

    $('#assess_report_download_panel > a').click(function() {
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
                + 'index.php/assess/assess_report_download?batch_name=' + batch_name
                + '&type_doc=' + type_doc
                //+ '&batch_id=' + batch_id
                + '&compare_batch_id=' + compare_batch_id
                + '&price_diff=' + price_diff
        var assessRequestParams = collectionParams();
        for (var p in assessRequestParams) {
            url = url + '&' + p + '=' + assessRequestParams[p];
        }
        window.open(url);
    }
    $(".horizontal_vertical_icon").click(function(){
        if($("#horizontal").css('visibility') === 'visible'){
            $("#vertical").css('visibility', 'visible') ;
            $("#horizontal").css('visibility', 'hidden') ;
            $("#columns_checking p").css('display','block');
            $("#columns_checking p").css('float','left');
            $('#research_assess_choiceColumnDialog').css({
                'width':'1200'
                
            });  
            $('#research_assess_choiceColumnDialog').parent().css({
            'left':'50%',
             'margin-left':'-600px'                
             });  
        }
        else{
            $("#vertical").css('visibility', 'hidden') ;
            $("#horizontal").css('visibility', 'visible') ;
            $("#columns_checking p").css('display','block');
            $("#columns_checking p").css('float','');
            $('#research_assess_choiceColumnDialog').css('width','250px');
            $('#research_assess_choiceColumnDialog').parent().css({
             'margin-left':'-137px'                
             }); 
        }
    });
    $(".research_assess_choiceColumnDialog_checkbox").change(function(){
         // get columns params
                var columns = {
                    snap: $("#column_snap").attr('checked') == 'checked',
                    created: $("#column_created").attr('checked') == 'checked',
                    product_name: $("#column_product_name").attr('checked') == 'checked',
                    item_id: $("#item_id").attr('checked') == 'checked',
                    model: $("#model").attr('checked') == 'checked',
                    url: $("#column_url").attr('checked') == 'checked',
                    Page_Load_Time: $("#Page_Load_Time").attr('checked') == 'checked',
                    Short_Description: $("#Short_Description").attr('checked') == 'checked',
                    short_description_wc: $("#column_short_description_wc").attr('checked') == 'checked',
                    Meta_Keywords: $("#Meta_Keywords").attr('checked') == 'checked',
                    short_seo_phrases: $("#column_short_seo_phrases").attr('checked') == 'checked',
                    Long_Description: $("#Long_Description").attr('checked') == 'checked',
                    long_description_wc: $("#column_long_description_wc").attr('checked') == 'checked',
                    long_seo_phrases: $("#column_long_seo_phrases").attr('checked') == 'checked',
                    Custom_Keywords_Short_Description : $("#Custom_Keywords_Short_Description").attr('checked') == 'checked',
                    Custom_Keywords_Long_Description : $("#Custom_Keywords_Long_Description").attr('checked') == 'checked',
                    Meta_Description : $("#Meta_Description").attr('checked') == 'checked',
                    Meta_Description_Count : $("#Meta_Description_Count").attr('checked') == 'checked',
                    H1_Tags : $("#H1_Tags").attr('checked') == 'checked',
                    H1_Tags_Count : $("#H1_Tags_Count").attr('checked') == 'checked',
                    H2_Tags : $("#H2_Tags").attr('checked') == 'checked',
                    H2_Tags_Count : $("#H2_Tags_Count").attr('checked') == 'checked',
                    duplicate_content: $("#column_duplicate_content").attr('checked') == 'checked',
                    column_external_content: $("#column_external_content").attr('checked') == 'checked',
                    column_reviews: $("#column_reviews").attr('checked') == 'checked',
                    column_features: $("#column_features").attr('checked') == 'checked',
                    price_diff: $("#column_price_diff").attr('checked') == 'checked',
                    gap: $("#gap").attr('checked') == 'checked'
                };

                // save params to DB
                $.ajax({
                    url: base_url + 'index.php/assess/assess_save_columns_state',
                    dataType: 'json',
                    type: 'post',
                    data: {
                        value: columns
                    },
                    success: function(data) {
                        if (data == true) {
                            hideColumns();
                            addColumn_url_class();
                            check_word_columns();
                        }
                    }
                });

    });
    $('#research_assess_choiceColumnDialog').dialog({
        autoOpen: false,
        resizable: false,
        modal: true,
//        buttons: {
//            'Save': function() {
//                // get columns params
//                var columns = {
//                    snap: $("#column_snap").attr('checked') == 'checked',
//                    created: $("#column_created").attr('checked') == 'checked',
//                    product_name: $("#column_product_name").attr('checked') == 'checked',
//                    item_id: $("#item_id").attr('checked') == 'checked',
//                    model: $("#model").attr('checked') == 'checked',
//                    url: $("#column_url").attr('checked') == 'checked',
//                    short_description_wc: $("#column_short_description_wc").attr('checked') == 'checked',
//                    Meta_Keywords: $("#Meta_Keywords").attr('checked') == 'checked',
//                    short_seo_phrases: $("#column_short_seo_phrases").attr('checked') == 'checked',
//                    long_description_wc: $("#column_long_description_wc").attr('checked') == 'checked',
//                    long_seo_phrases: $("#column_long_seo_phrases").attr('checked') == 'checked',
//                    Custom_Keywords_Short_Description : $("#Custom_Keywords_Short_Description").attr('checked') == 'checked',
//                    Custom_Keywords_Long_Description : $("#Custom_Keywords_Long_Description").attr('checked') == 'checked',
//                    Meta_Description : $("#Meta_Description").attr('checked') == 'checked',
//                    Meta_Description_Count : $("#Meta_Description_Count").attr('checked') == 'checked',
//                    H1_Tags : $("#H1_Tags").attr('checked') == 'checked',
//                    H1_Tags_Count : $("#H1_Tags_Count").attr('checked') == 'checked',
//                    H2_Tags : $("#H2_Tags").attr('checked') == 'checked',
//                    H2_Tags_Count : $("#H2_Tags_Count").attr('checked') == 'checked',
//                    duplicate_content: $("#column_duplicate_content").attr('checked') == 'checked',
//                    column_external_content: $("#column_external_content").attr('checked') == 'checked',
//                    column_reviews: $("#column_reviews").attr('checked') == 'checked',
//                    column_features: $("#column_features").attr('checked') == 'checked',
//                    price_diff: $("#column_price_diff").attr('checked') == 'checked'
//                };
//
//                // save params to DB
//                $.ajax({
//                    url: base_url + 'index.php/assess/assess_save_columns_state',
//                    dataType: 'json',
//                    type: 'post',
//                    data: {
//                        value: columns
//                    },
//                    success: function(data) {
//                        if (data == true) {
//                            hideColumns();
//                            addColumn_url_class();
//                            check_word_columns();
//                        }
//                    }
//                });
//
//                $(this).dialog('close');
//            },
//            'Cancel': function() {
//                $(this).dialog('close');
//            }
//        },
        width: 'auto'
                });

    $('#assess_report_options_dialog_button').on('click', function() {
        var selected_batch_id = $('select[name="research_assess_batches"] option:selected').val();
        var data = {
            'batch_id': selected_batch_id
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
                        assess_report_competitors.append('<option value="' + value.id + '" ' + selected + '>' + value.name + '</option>');
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
                        'data': JSON.stringify(assess_report_options_form)
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

    function assess_report_options_dialog_close() {
        $('#assess_report_competitors').empty();
        $('#assess_report_options_dialog').dialog('close');
    }

    $('#research_batches_columns').on('click', function() {
        $('#research_assess_choiceColumnDialog').dialog('open');
        $('#research_assess_choiceColumnDialog').parent().find('button:first-child').addClass("popupGreen");
    });

    tblAllColumns = tblAssess.fnGetAllSColumnNames();

    function hideColumns() {
        var table_case = $('#assess_tbl_show_case a[class=active_link]').data('case');
        var columns_checkboxes = $('#research_assess_choiceColumnDialog').find('input[type=checkbox]:checked');
        var columns_checkboxes_checked = [];
        $.each(columns_checkboxes, function(index, value) {
            columns_checkboxes_checked.push($(value).data('col_name'));
        });

        if (table_case == 'recommendations') {
            $('#graphDropDown').remove();
            $('#assess_graph').hide();
            $('#tblAssess_info').show();
            $('#tblAssess_paginate').show();
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
            check_word_columns();
        } else if (table_case == 'details') {
            $('#graphDropDown').remove();
            $('#assess_graph').hide();
            $('#tblAssess_info').show();
            $('#tblAssess_paginate').show();
            reportPanel(false);
            $.each(tblAllColumns, function(index, value) {
                if ($.inArray(value, columns_checkboxes_checked) > -1) {
                    tblAssess.fnSetColumnVis(index, true, false);
                    
                }else if(value==='H1_Tags_Count' || value==='H2_Tags_Count' || value ==='Meta_Description_Count'){
                    if ($.inArray(tblAllColumns[index-1], columns_checkboxes_checked) > -1) {
                    tblAssess.fnSetColumnVis(index, true, false);
                    }
                    else{
                        tblAssess.fnSetColumnVis(index, false, false);
                    }
                }
                else {
                    tblAssess.fnSetColumnVis(index, false, false);
                    
                }
                //tblAssess.fnSetColumnVis(, false, false);
            });
            addColumn_url_class();
            check_word_columns();
        }
        else if (table_case == 'details_compare') {
            $('#graphDropDown').remove();
            $('#assess_graph').hide();
            $('#tblAssess_info').show();
            $('#tblAssess_paginate').show();
            reportPanel(false);
            $.each(tblAllColumns, function(index, value) {
                value = value.replace(/[0-9]$/, "");
              
                if ($.inArray(value, tableCase.details_compare) > -1 && $.inArray(value, columns_checkboxes_checked) > -1) {
                    tblAssess.fnSetColumnVis(index, true, false);
              
                
                }
                else if(value ==='Meta_Description_Count'){
                    if ($.inArray("Meta_Description", columns_checkboxes_checked) > -1) {
                    tblAssess.fnSetColumnVis(index, true, false);
                    }
                    else{
                        tblAssess.fnSetColumnVis(index, false, false);
                    }
                }
                else {
                    tblAssess.fnSetColumnVis(index, false, false);
                }
            });
            addColumn_url_class();
            check_word_columns();
        } else if (table_case == 'report') {
            $('#graphDropDown').remove();
            $('#tblAssess_info').show();
            $('#tblAssess_paginate').show();
            $('#assess_graph').hide();
            reportPanel(true);
            var batch_id = $('select[name="research_assess_batches"]').find('option:selected').val();
            //$('#assess_report_download_pdf').attr('href', base_url + 'index.php/research/assess_download_pdf?batch_name=' + batch_name);
        } else if (table_case == 'view') {
            $('#graphDropDown').remove();
            $('#tblAssess_info').hide();
            $('#tblAssess_paginate').hide();
            $('#assess_graph').hide();
            $('#tblAssess').hide();
            $('#tblAssess').parent().find('div.ui-corner-bl').hide();
            $('#assess_view').show();
            $('#assess_report').hide();
            var batch_id = $('select[name="research_assess_batches"]').find('option:selected').val();
            $("#board_view").click(function(e) {
                e.stopPropagation();
                if ($('.board_view').css('display') == 'none') {
                    $('#tblAssess_info').show();
                    $('#tblAssess_paginate').show();
                    $('.dashboard').hide();
                    $.post(base_url + 'index.php/measure/getBoardView', {'site_name': $("#hp_boot_drop .btn_caret_sign").text()}, function(data) {
                        var str = '';
                        if (data.length > 0) {
                            for (var i = 0; i < data.length; i++) {
                                var json = $.parseJSON(data[i].title_keyword_description_density);
                                str += '<div class="board_item"><span>' + data[i].text + '</span><br /><img src="' +
                                        data[i].snap + '"/><div class="prod_description"><b>Description word count:' +
                                        data[i].description_words + '</b><br /><br /><b>Keywords (frequency, density)</b><br />';

                                $.each(json, function(m, item) {
                                    str += m + ': ' + item + '<br />';
                                });
                                str += '<b>Category Description:</b><br />' + data[i].description_text + '</div></div>';
                            }

                        }
                        $('.board_view').html(str);
                        $('.board_view .board_item img').on('click', function() {
                            var info = $(this).parent().find('div.prod_description').html();
                            showSnap('<img src="' + $(this).attr('src') + '" style="float:left">' + info);
                        });
                    });
                    $('.board_view').show();
                } else {
                    $('#tblAssess_info').hide();
                    $('#tblAssess_paginate').hide();
                    $('.board_view').hide();
                    $('.dashboard').show();
                }
            });
        } else if (table_case == 'graph') {
            $('#graphDropDown').remove();
            $('#tblAssess_info').hide();
            var dropDownString;
            dropDownString = '<select id="graphDropDown" style="width: 235px" >';
                dropDownString += '<option value="short_description_wc" >Short Description Word Counts</option>';
                dropDownString += '<option value="long_description_wc" >Long Description Word Counts</option>';
                dropDownString += '<option value="h1_word_counts" >H1 Word Counts</option>';
                dropDownString += '<option value="h2_word_counts" >H2 Word Counts</option>';
                dropDownString += '<option value="revision" >Reviews</option>';
                dropDownString += '<option value="Features" >Features</option>';
                dropDownString += '<option value="own_price" >Prices</option>';
            dropDownString += '</select>';
            $('#tblAssess_info').after(dropDownString);
            $('#tblAssess_paginate').hide();
            $('.board_view').hide();
            $('#tblAssess').hide();
            $('#tblAssess').parent().find('div.ui-corner-bl').hide();
            $('#assess_report').hide();
            $('#assess_view').hide();
            $('#assess_graph').show();
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
            $('#assess_view').hide();
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

    function collectionParams() {

        var assessRequestParams = {};

        assessRequestParams.search_text = $('#assess_filter_text').val();
        assessRequestParams.batch_id = $('select[name="research_assess_batches"]').find('option:selected').val();

        var assess_filter_datefrom = $('#assess_filter_datefrom').val();
        var assess_filter_dateto = $('#assess_filter_dateto').val();
        if (assess_filter_datefrom && assess_filter_dateto) {
            assessRequestParams.date_from = assess_filter_datefrom,
                    assessRequestParams.date_to = assess_filter_dateto
        }

        if ($("select[name='research_assess_batches'").val() != 0 && $("#research_assess_compare_batches_batch").val() != 0 && $("#research_assess_compare_batches_batch").val() != null) {
            assessRequestParams.batch2 = $('#research_assess_compare_batches_batch').find('option:selected').val();

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
    check_word_columns();
    $('#assess_report_download_panel').hide();

//    $(document).on('mouseenter', 'i.snap_ico', function () {
//     var snap = "webshoots/" + $(this).attr('snap');
//     $("#assess_preview_crawl_snap_modal .snap_holder").html("<img src='" + base_url +  snap + "'>");
//     $("#assess_preview_crawl_snap_modal").modal('show');
//     });
    $(document).on('mouseleave', '#assess_preview_crawl_snap_modal', function() {
        $(this).modal('hide');
    });
   $('#research_assess_export').live('click',function() {
        var columns_check = $('#research_assess_choiceColumnDialog').find('input[type=checkbox]:checked');
        var columns_checked = [];
        $.each(columns_check, function(index, value) {
            columns_checked.push($(value).data('col_name'));
        });
        $(this).attr('disabled', true);
        var batch_id= $('select[name="research_assess_batches"]').find('option:selected').val();
        var batch_name= $('select[name="research_assess_batches"]').find('option:selected').text();
        var cmp_selected = $('#research_assess_compare_batches_batch').val();
        $(this).text('Exporting...');
        var main_path=  $(this).prop('href');
        $(this).attr('href', $(this).prop('href')+'?batch_id='+batch_id+'&cmp_selected='+cmp_selected+'&checked_columns='+columns_checked+'&batch_name='+batch_name);
        $.fileDownload($(this).prop('href'))
                .done(function() {
            $('#research_assess_export').removeAttr('disabled');
            $('#research_assess_export').attr('href', main_path);
            $('#research_assess_export').text('Export');
        })
                .fail(function() {
        });
        
    });

});
