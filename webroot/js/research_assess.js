var readAssessUrl = base_url + 'index.php/assess/get_assess_info';
var readBoardSnapUrl = base_url + 'index.php/assess/get_board_view_snap';
var readGraphDataUrl = base_url + 'index.php/assess/get_graph_batch_data';
var readAssessUrlCompare = base_url + 'index.php/assess/compare';
var rememberBatchValue = base_url + 'index.php/assess/remember_batches';
var getbatchesvalue = base_url + 'index.php/assess/getbatchvalues';
var get_summary_filters = base_url + 'index.php/assess/get_summary_filters';
var save_summary_filters = base_url + 'index.php/assess/save_summary_filters';
var save_summary_filters_order = base_url + 'index.php/assess/save_summary_filters_order';
var serevr_side = true;
var serverside_table;
var tblAllColumns = [];
var summaryInfoSelectedElements = [];
var tblAssess;
var last_batch_id;
var last_compare_batch_id;
var first_click = true ;
var summary_active_items = [];
var arrow_css_top;
var summary_filters_order;

function close_popover(elem)
{
	var element = $(elem);
		
	element.closest('.popover').prev().popover('hide');
	
	return false;
}


function resizeImp(){
			var status = "no ok";
			var statusinterval = setInterval( function(){
			if($("#tblAssess td").length > 1){
				status = "ok";
			}
			if(status == "ok"){
			clearInterval(statusinterval); 
			$("#tblAssess").colResizable({
			disable:true
			});
			$("#tblAssess").colResizable({
				liveDrag:true, 
				gripInnerHtml:"<div class='grip'></div>", 
				draggingClass:"dragging"});
			}
			},500);
			//console.log("resizeImp");
}
$(function() {
	
	$.expr[':'].contains = function(a, i, m) {
	  return $(a).text().toUpperCase()
		  .indexOf(m[3].toUpperCase()) >= 0;
	};

    $.ajax({
            url: getbatchesvalue,
            dataType: 'json',
            type: 'POST'
        }).done(function(data){
           last_batch_id  = data.batch_id;
           last_compare_batch_id = data.compare_batch_id;
           
                first_click = false;
          $('select[name="research_assess_batches"]').val(last_batch_id).change()
                setTimeout(function(){
                first_click = true;

                $('select[id="research_assess_compare_batches_batch"]').val(last_compare_batch_id).change()
                 $('#research_assess_update').click();
                },1500);
                
               
        });
        
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
	
	function toggleDetailsCompareBlocks(isDisplayed)
	{
		var assess_report_compare = $('.assess_report_compare');
		if (isDisplayed)
		{
			assess_report_compare.show();
		} else {
			assess_report_compare.hide();
		}
	}
	
	// Use this variable to define "togglers" for each tab
	var tabsRelatedBlocks = {
		details_compare : toggleDetailsCompareBlocks,
		view : toggleDetailsCompareBlocks,
		details_compare_result : toggleDetailsCompareBlocks,
		graph : toggleDetailsCompareBlocks
	};
	
	var summaryFieldNames = [
		'assess_report_competitor_matches_number',
		'skus_shorter_than_competitor_product_content',
		'skus_longer_than_competitor_product_content',
		'skus_same_competitor_product_content',
		'skus_fewer_features_than_competitor',
		'skus_fewer_reviews_than_competitor',
		'skus_fewer_competitor_optimized_keywords',
		
		'skus_zero_optimized_keywords',
		'skus_one_optimized_keywords',
		'skus_two_optimized_keywords',
		'skus_three_optimized_keywords',
		
		'skus_zero_optimized_keywords_competitor',
		'skus_one_optimized_keywords_competitor',
		'skus_two_optimized_keywords_competitor',
		'skus_three_optimized_keywords_competitor',
		
		'skus_title_less_than_70_chars',
		'skus_title_more_than_70_chars',
		'skus_title_less_than_70_chars_competitor',
		'skus_title_more_than_70_chars_competitor',		
		'skus_75_duplicate_content',
		'skus_25_duplicate_content',
		'skus_50_duplicate_content',
		'total_items_selected_by_filter',
		'skus_third_party_content',
		'skus_third_party_content_competitor',
		'skus_fewer_50_product_content',
		'skus_fewer_100_product_content',
		'skus_fewer_150_product_content',
		'skus_fewer_50_product_content_competitor',
		'skus_fewer_100_product_content_competitor',
		'skus_fewer_150_product_content_competitor',
		'skus_features',
		'skus_features_competitor',
		
		'skus_zero_reviews',
		'skus_one_four_reviews',
		'skus_more_than_five_reviews',
		'skus_more_than_hundred_reviews',
		
		'skus_zero_reviews_competitor',
        'skus_one_four_reviews_competitor',
        'skus_more_than_five_reviews_competitor',
        'skus_more_than_hundred_reviews_competitor',
		
		'skus_pdfs',
		'skus_videos',
		'skus_videos_competitor',
		'skus_pdfs_competitor',
		
		'skus_with_no_product_images',
		'skus_with_one_product_image',
		'skus_with_more_than_one_product_image',
		'skus_with_no_product_images_competitor',
		'skus_with_one_product_image_competitor',

		'skus_with_more_than_one_product_image_competitor',
		'assess_report_items_priced_higher_than_competitors'
	];
	
	var batch_sets = {
		me : {
			batch_batch : 'research_assess_batches',
			batch_compare : '#research_assess_compare_batches_batch',
			batch_items_prefix : 'batch_me_',
		},
		competitor : {
			batch_batch : 'research_assess_batches_competitor',
			batch_compare : '#research_assess_compare_batches_batch_competitor',
			batch_items_prefix : 'batch_competitor_'
		}
	};
	
    var tableCase = {
        details: [
            "snap",
            "created",
            "imp_data_id",
            "product_name",
            "item_id",
            "model",
            "url",
            "Page_Load_Time",
            "Short_Description",
            "short_description_wc",
            "Meta_Keywords",
            "short_seo_phrases",
            "title_seo_phrases",
            "images_cmp",
            "video_count",
            "title_pa",
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
            "imp_data_id",
            "product_name",
            "item_id",
            "model",
            "url",
            "Page_Load_Time",
            "Short_Description",
            "short_description_wc",
            "Meta_Keywords",
            "title_seo_phrases",
            "images_cmp",
            "video_count",
            "title_pa",
            "Long_Description",
            "long_description_wc",
            "Meta_Description",
            "Meta_Description_Count",
            "column_external_content",
            "H1_Tags",
            "H1_Tags_Count",
            "H2_Tags",
            "H2_Tags_Count",
            "column_reviews",
            "average_review",
            "column_features",
            "snap1",
            "imp_data_id1",
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
            "column_external_content1",
            "H1_Tags1",
            "H1_Tags_Count1",
            "H2_Tags1",
            "H2_Tags_Count1",
            "column_reviews1",
            "average_review1",
            "column_features1",
            "title_seo_phrases1",
            "images_cmp1",
            "video_count1",
            "title_pa1",
            "gap",
            "Duplicate_Content"
            
        ],
        recommendations: [
            "product_name",
            "url",
            "recommendations"
        ]
    }

    function createTableByServerSide() {
		var batch_set = $('.result_batch_items:checked').val() || 'me';		
        $('#tblAssess_wrapper').remove();
        var th = '';
        for(var i =0;i<Object.keys(columns);i++){
            th += '<th with = "100px"></th>';
        }
        var newTable = '<table id="tblAssess" class="tblDataTable"><thead>'+th+'</thead><tbody></tbody></table>';
        // $('table#tblAssess').floatThead('reflow');
        $('#dt_tbl').prepend(newTable); 
              
        			
        tblAssess = $('#tblAssess').dataTable({
        	"sDom": 'Rlfrtip',
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
						console.log('createTableByServerSide function, dataTable object, fnServerData callback');
                        buildReport(json);
                    }

                    fnCallback(json);
                    setTimeout(function() {
                        tblAssess.fnProcessingIndicator(false);
                    }, 100);
                    if ($('select[name="' + batch_sets[batch_set]['batch_batch'] + '"]').find('option:selected').val() == "0") {
                        $('.' + batch_sets[batch_set]['batch_items_prefix'] + 'assess_report_total_items').html("");
                        $('.' + batch_sets[batch_set]['batch_items_prefix'] + 'assess_report_items_priced_higher_than_competitors').html("");
                        $('.assess_report_items_have_more_than_20_percent_duplicate_content').html("");
                        $('.assess_report_items_unoptimized_product_content').html("");
                        $('.assess_report_items_have_product_short_descriptions_that_are_too_short').html("");
                        $('.assess_report_items_have_product_long_descriptions_that_are_too_short').html("");
                    }
                    if (json.iTotalRecords == 0) {
                        $('.assess_report_compare_panel').hide();
                        $('.assess_report_numeric_difference').hide();
                        if ($('select[name="' + batch_sets[batch_set]['batch_batch'] + '"]').find('option:selected').val() != "") {
                            $('#summary_message').html(" - Processing data. Check back soon.");
                            //                                $('#research_assess_filter_short_descriptions_panel').show();
                            //                                $('#research_assess_filter_long_descriptions_panel').show();
                            $('.assess_report_items_1_descriptions_pnl').hide();
                            $('.assess_report_items_2_descriptions_pnl').hide();
                            // $('table#tblAssess').floatThead('reflow');
                        }
                        
                        
                        // $('table#tblAssess').floatThead('reflow');
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
                highChart('total_description_wc');
                var compare_batch_id = $(batch_sets[batch_set]['batch_compare']).find('option:selected').val();
                $.ajax({
                    type: "POST",
                    url: readBoardSnapUrl,
                    data: {
                        batch_id: $('select[name="' + batch_sets[batch_set]['batch_batch'] + '"]').find('option:selected').val(),
                        compare_batch_id: $(batch_sets[batch_set]['batch_compare']).find('option:selected').val()
                    }
                }).done(function(data){
                    if(data.length > 0){
                        var str = '';
                        var showcount = 12;
                        if(compare_batch_id != '0' && compare_batch_id !='all'){
                            showcount = 6 ;
                        }
                        for(var i=0; i<data.length; i++){
//                            var obj = jQuery.parseJSON(data[i][2]);
                            if(i < showcount){

                                if(data[i]['product_name'] != null && data[i]['product_name'] != '' && data[i]['snap']!=''){
                                    if(data[i]['product_name'].length > 93)
                                      str += '<div id="snap'+i+'" class="board_item"><span class="span_img">'+data[i]['product_name']+'</span><br />'+data[i]['snap']+
                                          '<div class="prod_description"><b>URL:</b><br/>'+data[i]['url']+'<br /><br /><b>Product name:</b><br/>'+data[i]['product_name']+'</div></div>';
                                else
                                      str += '<div id="snap'+i+'" class="board_item"><span>'+data[i]['product_name']+'</span><br />'+data[i]['snap']+
                                          '<div class="prod_description"><b>URL:</b><br/>'+data[i]['url']+'<br /><br /><b>Product name:</b><br/>'+data[i]['product_name']+'</div></div>';
                            }
                                else{
                                    str += '<div id="snap'+i+'" class="board_item"></div>'
                        }                   
                                if(compare_batch_id != '0' && compare_batch_id !='all'){
                                    if(data[i]['product_name1'] != null && data[i]['product_name1'] != '' && data[i]['snap1']!=''){

            //                            console.log(data.length);
                                        if(data[i]['product_name1'].length > 93)
                                          str += '<div id="compare_snap'+i+'" class="board_item"><span class="span_img">'+data[i]['product_name1']+'</span><br />'+data[i]['snap1']+
                                              '<div class="prod_description"><b>URL:</b><br/>'+data[i]['url1']+'<br /><br /><b>Product name:</b><br/>'+data[i]['product_name1']+'</div></div>';
                                        else
                                          str += '<div id="compare_snap'+i+'" class="board_item"><span>'+data[i]['product_name1']+'</span><br />'+data[i]['snap1']+
                                              '<div class="prod_description"><b>URL:</b><br/>'+data[i]['url1']+'<br /><br /><b>Product name:</b><br/>'+data[i]['product_name1']+'</div></div>';
                                    }
                                    else{
                                        str += '<div id="compare_snap'+i+'" class="board_item"></div>'
                                    }
                                }
                            }
                            else{
                                if(data[i]['product_name'] != null && data[i]['product_name'] != '' && data[i]['snap']!=''){
                                    if(data[i]['product_name'].length > 93)
                                      str += '<div id="snap'+i+'" class="board_item" style="display: none;"><span class="span_img">'+data[i]['product_name']+'</span><br />'+data[i]['snap']+
                                          '<div class="prod_description"><b>URL:</b><br/>'+data[i]['url']+'<br /><br /><b>Product name:</b><br/>'+data[i]['product_name']+'</div></div>';
                                    else
                                      str += '<div id="snap'+i+'" class="board_item" style="display: none;"><span>'+data[i]['product_name']+'</span><br />'+data[i]['snap']+
                                          '<div class="prod_description"><b>URL:</b><br/>'+data[i]['url']+'<br /><br /><b>Product name:</b><br/>'+data[i]['product_name']+'</div></div>';
                                }
                                else{
                                    str += '<div id="snap'+i+'" class="board_item" style="display: none;"></div>'
                                }
                                if(compare_batch_id != '0' && compare_batch_id !='all'){
                                    if(data[i]['product_name1'] != null && data[i]['product_name1'] != '' && data[i]['snap1']!=''){

            //                            console.log(data.length);
                                        if(data[i]['product_name1'].length > 93)
                                          str += '<div id="compare_snap'+i+'" class="board_item" style="display: none;"><span class="span_img">'+data[i]['product_name1']+'</span><br />'+data[i]['snap1']+
                                              '<div class="prod_description"><b>URL:</b><br/>'+data[i]['url1']+'<br /><br /><b>Product name:</b><br/>'+data[i]['product_name1']+'</div></div>';
                                        else
                                          str += '<div id="compare_snap'+i+'" class="board_item style="display: none;""><span>'+data[i]['product_name1']+'</span><br />'+data[i]['snap1']+
                                              '<div class="prod_description"><b>URL:</b><br/>'+data[i]['url1']+'<br /><br /><b>Product name:</b><br/>'+data[i]['product_name1']+'</div></div>';
                                    }
                                    else{
                                        str += '<div id="compare_snap'+i+'" class="board_item" style="display: none;"></div>'
                                    }
                                }
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
                $(nRow).attr("add_data", aData[34]);
                return nRow;
                $('table#tblAssess').floatThead('reflow');
            },
            "fnDrawCallback": function(oSettings) {
                tblAssess_postRenderProcessing();
                if (zeroTableDraw) {
                    zeroTableDraw = false;
                    return;
                }
                hideColumns();
                check_word_columns();
                $('table#tblAssess').floatThead('reflow');
				console.log("reflow 2");
				var status = "no ok";
				var statusinterval = setInterval( function(){
				if($("#tblAssess td").length > 1){
					status = "ok";
				}
				if(status == "ok"){clearInterval(statusinterval); 
				$("#tblAssess").colResizable({
				disable:true
				});
				$("#tblAssess").colResizable({
					liveDrag:true, 
					gripInnerHtml:"<div class='grip'></div>", 
					draggingClass:"dragging"});
				}
				},500);
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
		 //new FixedHeader( tblAssess, { "bottom": true } );
		
			
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
        // $('table#tblAssess').floatThead('reflow');
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
        var batch_set = $('.result_batch_items:checked').val() || 'me';		
		// $('table#tblAssess').floatThead('reflow');
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
		  console.log(json.columns);
            for(var i =0;i<Object.keys(json.columns).length;i++){
                th += '<th with = "100px"></th>';
            }
            var newTable = '<table id="tblAssess" class="tblDataTable"><thead>'+th+'</thead><tbody></tbody></table>';
            $('#dt_tbl').prepend(newTable);

            setTimeout(function() {
                tblAssess = $('#tblAssess').dataTable({
                	"sDom": 'Rlfrtip',
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
                        $(nRow).attr("add_data", aData[34]);
                        return nRow;
                        $('table#tblAssess').floatThead('reflow');
                    },
                    "fnDrawCallback": function(oSettings) {
                        tblAssess_postRenderProcessing();
                        if (zeroTableDraw) {
                            zeroTableDraw = false;
                            return;
                        }
         				$('table#tblAssess').floatThead('reflow');
						var status = "no ok";
						var statusinterval = setInterval( function(){
						if($("#tblAssess td").length > 1){
							status = "ok";
						}
						if(status == "ok"){clearInterval(statusinterval); 
						$("#tblAssess").colResizable({
						disable:true
						});
						$("#tblAssess").colResizable({
							liveDrag:true, 
							gripInnerHtml:"<div class='grip'></div>", 
							draggingClass:"dragging"});
						}
						},500);

                    }
                });

                $('#tblAssess').after('<div id="tableScrollWrapper" style="overflow-x:scroll"></div>');
                $('#tblAssess').appendTo('#tableScrollWrapper');
				
                if (json.ExtraData != undefined) {
					console.log('create table function');
                    buildReport(json);
                }
                tblAssess.fnDraw();
                serevr_side = false;
                setTimeout(function() {
                    tblAssess.fnProcessingIndicator(false);
                }, 2000);
                if ($('select[name="' + batch_sets[batch_set]['batch_batch'] + '"]').find('option:selected').val() == "0") {
                    $('.' + batch_sets[batch_set]['batch_items_prefix'] + 'assess_report_total_items').html("");
                    $('.' + batch_sets[batch_set]['batch_items_prefix'] + 'assess_report_items_priced_higher_than_competitors').html("");
                    $('.assess_report_items_have_more_than_20_percent_duplicate_content').html("");
                    $('.assess_report_items_unoptimized_product_content').html("");
                    $('.assess_report_items_have_product_short_descriptions_that_are_too_short').html("");
                    $('.assess_report_items_have_product_long_descriptions_that_are_too_short').html("");
                }
                if (json.iTotalRecords == 0) {
                    $('.assess_report_compare_panel').hide();
                    $('.assess_report_numeric_difference').hide();
                    if ($('select[name="' + batch_sets[batch_set]['batch_batch'] + '"]').find('option:selected').val() != "") {
                        $('#summary_message').html(" - Processing data. Check back soon.");
                        //                                $('#research_assess_filter_short_descriptions_panel').show();
                        //                                $('#research_assess_filter_long_descriptions_panel').show();
                        $('.assess_report_items_1_descriptions_pnl').hide();
                        $('.assess_report_items_2_descriptions_pnl').hide();
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
        highChart('total_description_wc');
        var compare_batch_id = $(batch_sets[batch_set]['batch_compare']).find('option:selected').val();
        $.ajax({
            type: "POST",
            url: readBoardSnapUrl,
            data: {
                        batch_id: $('select[name="' + batch_sets[batch_set]['batch_batch'] + '"]').find('option:selected').val(),
                        compare_batch_id: $(batch_sets[batch_set]['batch_compare']).find('option:selected').val()
                    }
        }).done(function(data){
            if(data.length > 0){
                var str = '';
                var showcount = 12;
                if(compare_batch_id != '0' && compare_batch_id !='all'){
                    showcount = 6 ;
                }
                for(var i=0; i<data.length; i++){
//                            var obj = jQuery.parseJSON(data[i][2]);
                    if(i < showcount){

                        if(data[i]['product_name'] != null && data[i]['product_name'] != '' && data[i]['snap']!=''){
                            if(data[i]['product_name'].length > 93)
                              str += '<div id="snap'+i+'" class="board_item"><span class="span_img">'+data[i]['product_name']+'</span><br />'+data[i]['snap']+
                                  '<div class="prod_description"><b>URL:</b><br/>'+data[i]['url']+'<br /><br /><b>Product name:</b><br/>'+data[i]['product_name']+'</div></div>';
                        else
                              str += '<div id="snap'+i+'" class="board_item"><span>'+data[i]['product_name']+'</span><br />'+data[i]['snap']+
                                  '<div class="prod_description"><b>URL:</b><br/>'+data[i]['url']+'<br /><br /><b>Product name:</b><br/>'+data[i]['product_name']+'</div></div>';
                    }
                        else{
                            str += '<div id="snap'+i+'" class="board_item"></div>'
                }                   
                        if(compare_batch_id != '0' && compare_batch_id !='all'){
                            if(data[i]['product_name1'] != null && data[i]['product_name1'] != '' && data[i]['snap1']!=''){

    //                            console.log(data.length);
                                if(data[i]['product_name1'].length > 93)
                                  str += '<div id="compare_snap'+i+'" class="board_item"><span class="span_img">'+data[i]['product_name1']+'</span><br />'+data[i]['snap1']+
                                      '<div class="prod_description"><b>URL:</b><br/>'+data[i]['url1']+'<br /><br /><b>Product name:</b><br/>'+data[i]['product_name1']+'</div></div>';
                                else
                                  str += '<div id="compare_snap'+i+'" class="board_item"><span>'+data[i]['product_name1']+'</span><br />'+data[i]['snap1']+
                                      '<div class="prod_description"><b>URL:</b><br/>'+data[i]['url1']+'<br /><br /><b>Product name:</b><br/>'+data[i]['product_name1']+'</div></div>';
                            }
                            else{
                                str += '<div id="compare_snap'+i+'" class="board_item"></div>'
                            }
                        }
                    }
                    else{
                        if(data[i]['product_name'] != null && data[i]['product_name'] != '' && data[i]['snap']!=''){
                            if(data[i]['product_name'].length > 93)
                              str += '<div id="snap'+i+'" class="board_item" style="display: none;"><span class="span_img">'+data[i]['product_name']+'</span><br />'+data[i]['snap']+
                                  '<div class="prod_description"><b>URL:</b><br/>'+data[i]['url']+'<br /><br /><b>Product name:</b><br/>'+data[i]['product_name']+'</div></div>';
                            else
                              str += '<div id="snap'+i+'" class="board_item" style="display: none;"><span>'+data[i]['product_name']+'</span><br />'+data[i]['snap']+
                                  '<div class="prod_description"><b>URL:</b><br/>'+data[i]['url']+'<br /><br /><b>Product name:</b><br/>'+data[i]['product_name']+'</div></div>';
                        }
                        else{
                            str += '<div id="snap'+i+'" class="board_item" style="display: none;"></div>'
                        }
                        if(compare_batch_id != '0' && compare_batch_id !='all'){
                            if(data[i]['product_name1'] != null && data[i]['product_name1'] != '' && data[i]['snap1']!=''){

    //                            console.log(data.length);
                                if(data[i]['product_name1'].length > 93)
                                  str += '<div id="compare_snap'+i+'" class="board_item" style="display: none;"><span class="span_img">'+data[i]['product_name1']+'</span><br />'+data[i]['snap1']+
                                      '<div class="prod_description"><b>URL:</b><br/>'+data[i]['url1']+'<br /><br /><b>Product name:</b><br/>'+data[i]['product_name1']+'</div></div>';
                                else
                                  str += '<div id="compare_snap'+i+'" class="board_item" style="display: none;"><span>'+data[i]['product_name1']+'</span><br />'+data[i]['snap1']+
                                      '<div class="prod_description"><b>URL:</b><br/>'+data[i]['url1']+'<br /><br /><b>Product name:</b><br/>'+data[i]['product_name1']+'</div></div>';
                            }
                            else{
                                str += '<div id="compare_snap'+i+'" class="board_item" style="display: none;"></div>'
                            }
                        }
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
                $('table#tblAssess').floatThead('reflow');
             }
        });
       // $('table#tblAssess').floatThead('reflow');
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
            "sWidth": "10%",
            "sClass": "Snapshot"
        },
        {
            "sTitle": "Date",
            "sName": "created",
            "sWidth": "3%"
        },
        {
            "sTitle": "ID",
            "sName": "imp_data_id",
            "sWidth": "15%",
            "sClass": "imp_data_id"
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
            "sTitle": "Title Keywords",
            "sName": "title_seo_phrases",
            "sWidth": "2%",
            "sClass": "title_seo_phrases"
        },
        {
            "sTitle": "Images",
            "sName": "images_cmp",
            "sWidth": "2%",
            "sClass": "images_cmp"
        },
        {
            "sTitle": "Videos",
            "sName": "video_count",
            "sWidth": "2%",
            "sClass": "video_count"
        },/*max*/
        {
            "sTitle": "Title",
            "sName": "title_pa",
            "sWidth": "2%",
            "sClass": "title_pa"
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
            "sTitle": "Third Party Content",
            "sName": "column_external_content",
            "sWidth": "2%",
            "sClass" :  "column_external_content"
        },
        {
            "sTitle": "Reviews",
            "sName": "column_reviews",
            "sWidth": "3%",
            "sClass" :  "column_reviews"
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
            "sWidth": "10%",
            "sClass": "Snapshot1"
        },
        {
            "sTitle": "ID",
            "sName": "imp_data_id1",
            "sWidth": "10%",
            "sClass": "imp_data_id1"
        },
        {
            "sTitle": "Product Name",
            "sName": "product_name1",
            "sWidth": "15%",
			"sClass": "product_name1"
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
            "sWidth": "15%",
            "sClass": "url1"
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
            "sTitle": "Third Party Content",
            "sName": "column_external_content1",
            "sWidth": "2%",
            "sClass" :  "column_external_content1"
        },
        {
            "sTitle" : "H1 Tags", 
            "sName":"H1_Tags1", 
            "sWidth": "1%",
            "sClass" :  "HTags_11"
        },
        {
            "sTitle" : "Chars", 
            "sName":"H1_Tags_Count1", 
            "sWidth": "1%",
            "sClass" :  "HTags1"
        },
        {
            "sTitle" : "H2 Tags", 
            "sName":"H2_Tags1", 
            "sWidth": "1%",
            "sClass" :  "HTags_21"
        },
        {
            "sTitle" : "Chars", 
            "sName":"H2_Tags_Count1", 
            "sWidth": "1%",
            "sClass" :  "HTags1 CharsHTags1"
        },
        {
            "sTitle": "Reviews",
            "sName": "column_reviews1",
            "sWidth": "3%",
            "sClass": "column_reviews1"
        },
        {
            "sTitle": "Avg Review",
            "sName": "average_review1",
            "sWidth": "3%",
            "sClass" :  "average_review1"
        },
        {
            "sTitle": "Features",
            "sName": "column_features1",
            "sWidth": "4%",
            "sClass" :  "column_features1"
        },
        {
            "sTitle": "Title Keywords",
            "sName": "title_seo_phrases1",
            "sWidth": "1%",
            "sClass": "title_seo_phrases1"
        },
        {
            "sTitle": "Images",
            "sName": "images_cmp1",
            "sWidth": "1%",
            "sClass": "images_cmp1"
        },
        {
            "sTitle": "Videos",
            "sName": "video_count1",
            "sWidth": "1%",
            "sClass": "video_count1"
        },
        {
            "sTitle": "Title",
            "sName": "title_pa1",
            "sWidth": "1%",
            "sClass": "title_pa1"
        },
        {
            "sTitle": "Gap Analysis",
            "sName": "gap",
            "sWidth": "3%",
            "sClass" :  ""
        },
        {
            "sTitle": "Duplicate Content",
            "sName": "Duplicate_Content",
            "sWidth": "3%",
            "sClass" :  ""
        },

    ];
	
	var filter_expand_btn_imgs = [
		'filter_expand_btn.jpg',
		'filter_unexpand_btn.jpg',
	];
	var filter_toggler_flag = 0
		, current_filter_list_wrapper_height = 200;
	
	$('.summary_edit_btn').on('click', function() {
		var elem = $(this);
		if (!elem.hasClass('active'))
		{
			$('.icon_question_wrapper').css('vertical-align', 'bottom');
			$('.selectable_summary_handle, .selectable_summary_handle_with_competitor').css({'visibility' : 'visible'});
		}
		else 
		{
			$('.icon_question_wrapper').css('vertical-align', 'middle');
			$('.selectable_summary_handle, .selectable_summary_handle_with_competitor').css({'visibility' : 'hidden'});
		}
	});
	
	$('.clean_summary_search_field').on('click', function(e) {
		e.preventDefault();
		var search_field = $('.summary_search_field');
		
		search_field.val('');
		search_field.trigger('keyup');
		
		return false;
	});
	
	$('.summary_search_field').on('keyup', function() {
		var elem = $(this)
		  , elem_value = elem.val()
		  , filters = $('.item_line.selected_by_config');
		  
		if (elem_value)
		{
			filters.hide();			
			$('.item_line.selected_by_config:contains("' + elem_value + '")').show();
		} else {
			filters.show();
		}
	});
	/*
	 * Summary filter section expanding
	 */
	$('.filter_expand_btn').on('click', function(e) {
		e.preventDefault();
					
		var elem = $(this)
			, img = elem.find('img')
			, img_src = img.attr('src')			
			, lines = $('.item_line:visible')
			, lines_length = lines.length				
			, height = 0			
			, filter_list_wrapper = $('.boxes_content.resizable').parent();			
				 
		filter_toggler_flag = !filter_toggler_flag + 0;
					
		(function get_heights(lines) {
			lines.each(function(index, element) {
			
				var elem = $(element)
				  , local_height = $(element).height();
				
				height += local_height;		
							
				if (!local_height)
					get_heights(elem.children('div'));
			});
		})(lines);		
		
		
		if (filter_toggler_flag)			
			filter_list_wrapper.height($('#batch_set_toggle').is(':checked') ? height / 2 : height); //expand list
		else								
			filter_list_wrapper.height(current_filter_list_wrapper_height); //unexpand list		
				
		img.attr('src', img_src.substring(0, img_src.lastIndexOf('/') + 1) + filter_expand_btn_imgs[filter_toggler_flag]);
		
		return false;
	});
	
	$('table#tblAssess').floatThead('reflow');
	$('.resizable').wrap('<div/>')
        .css({'overflow':'hidden'})
          .parent()
            .css({'overflow':'visible',
                  'height':function(){return $('.resizable',this).height();},                                                                
                }).resizable({
					maxWidth : 1021,
					minWidth : 1021,
					minHeight: 200,
					resize : function( event, ui ) {						
						current_filter_list_wrapper_height = ui.size.height;
					},
					start : function( event, ui ) {
						$(window).unbind('resize');
					}					
				}).find('.resizable')
					.css({overflow:'auto',
						width:'100%',
                        height:'100%'});
	
	$('.question_mark').popover({
		html : true
	});	
	
	$('.question_mark').on('show.bs.popover', function() {
		
		var elem = $(this)
		  , uniqueid = elem.data('popover-uniqueid');
			
		$('.question_mark:not(.question_mark[data-popover-uniqueid="' + uniqueid + '"])').popover('hide');
	});
		
	$( ".summary_sortable_wrapper" ).sortable({
      placeholder: "ui-state-highlight",
	  handle: ".selectable_summary_handle, .selectable_summary_handle_with_competitor",
	  cancel : '.summary_filter_batch_name',	 
	  start : function( event, ui ) {
		
		// fixing style bugs
		var icon_wrapper = $(event.srcElement).parent();
		arrow_css_top = icon_wrapper.css('top');
		icon_wrapper.css('top', '0px');
		
		summary_filters_order = [];
	  },
	  stop : function( event, ui ) {
		// fixing style bugs
		var icon_wrapper = $(event.srcElement).parent();		
		icon_wrapper.css('top', arrow_css_top);
				
		//filling summary_filters_order variable
		$('.item_line').each(function(index, element) {
			var elem = $(element);
			summary_filters_order.push(elem.data('filterkey'));
		});
		
		
		//saving replacement
		$.ajax({
			type : 'POST',
			url : save_summary_filters_order,
			data : {
				summary_items_order : summary_filters_order
			},
			success : function(data) {
				console.log(data);
			}
		});
	  }
    });
		
	$( ".selectable_summary_info" ).disableSelection();
	
	$('.selectable_summary_info').on('mousedown', function(e) {
		e.metaKey = true;
	}).selectable({
		cancel : '.non-selectable, .question_mark, .popover_close_btn, .selectable_summary_handle, .selectable_summary_handle_with_competitor',
		tolerance : 'touch',
		filter : '.item_line',
		selected : function(event, ui) {
			// console.log('Selected...');
			summaryInfoSelectedElements = [];
			$('.selectable_summary_info .ui-selected').each(function(index, element) {
				var filterid = $(element).data('filterid');
				if (filterid)
					summaryInfoSelectedElements.push(filterid);
			});			
		},
		unselected : function(event,ui) {
			// console.log('Unselected...');
			summaryInfoSelectedElements = [];
			$('.selectable_summary_info .ui-selected').each(function(index, element) {		
				var filterid = $(element).data('filterid');
				if (filterid)
					summaryInfoSelectedElements.push(filterid);
			});			
		},
		selecting : function( event, ui ) {
			// console.log('Selecting...');
			// console.log(event);
			// console.log(ui);
		},
		unselecting : function( event, ui ) {
			// console.log('UNSelecting...');
			// console.log(event);
			// console.log(ui);
		},
		start : function( event, ui ) {
			// console.log('Starting...');
			// console.log(event);
			// console.log(ui);
		},
		stop : function( event, ui ) {
			// console.log('Stopping...');
			// console.log(event);
			// console.log(ui);
		}
	}).find( ".item_line:not(.batch1_filter_item):not(.batch2_filter_item)" )   
		.addClass( "ui-corner-all" )
        .prepend( "<div class='selectable_summary_handle'><i class='icon-move'></i></div>" );
	
	
	
	// $('table#tblAssess').floatThead('reflow');
    tblAssess = $('#tblAssess').dataTable({
    	"sDom": 'Rlfrtip',
        "bJQueryUI": true,
        "bDestroy": true,
        "sPaginationType": "full_numbers",
        "bProcessing": true,
        "aaSorting": [[5, "desc"]],
        "bAutoWidth": false,
        "bServerSide": true,
        "sAjaxSource": readAssessUrl,
        "fnServerData": function(sSource, aoData, fnCallback) {
			
			//Toggling total items selected count by filter
			var total_items_selected_by_filter_wrapper = $('.total_items_selected_by_filter_wrapper');
			var batch_set = $('.result_batch_items:checked').val() || 'me';			
			total_items_selected_by_filter_wrapper.hide();
			
			aoData.push({
                'name': 'summaryFilterData',
                'value': summaryInfoSelectedElements.join(',')
            });
										
            aoData = buildTableParams1(aoData);						
			
            first_aaData = aoData;
			console.log(sSource);
            $.getJSON(sSource, aoData, function(json) {
                if(json) {
                
                if (json.ExtraData != undefined) {
					console.log('dataTable callback: fnServerData');
                    buildReport(json);
                    if($("table[id^=tblAssess]")){
						if($("a#assess_tbl_show_case_details_compare[class^=active_link]")){
							if($("#tblAssess th[class*=1][style*='border-left-width: 2px']:not([class*=_1])")){$("#tblAssess th[class*=1][style*='border-left-width: 2px']:not([class*=_1])").css("border-left", "1px solid #ccc");}
							$("#tblAssess th[class*=1]:not([class*=_1]):first").css("border-left", "2px solid #ccc");
							$("#tblAssess tr").each(function(){
								if($(this).find("td[class*=1][style*='border-left-width: 2px']:not([class*=_1])"))
								{$(this).find("td[class*=1]:not([class*=_1])").css("border-left", "1px solid #ccc");}
								$(this).find("td[class*=1]:not([class*=_1]):first").css("border-left", "2px solid #ccc");
								
							});
						}
						
					}
                }
				
				
				if (summaryInfoSelectedElements.length)
					total_items_selected_by_filter_wrapper.show();
				
                fnCallback(json);
                setTimeout(function() {
                    tblAssess.fnProcessingIndicator(false);
                }, 100);
					
				
                if ($('select[name="' + batch_sets[batch_set]['batch_batch'] + '"]').find('option:selected').val() == "0") {
                    $('.' + batch_sets[batch_set]['batch_items_prefix'] + 'assess_report_total_items').html("");
                    $('.' + batch_sets[batch_set]['batch_items_prefix'] + 'assess_report_items_priced_higher_than_competitors').html("");
                    $('.assess_report_items_have_more_than_20_percent_duplicate_content').html("");
                    $('.assess_report_items_unoptimized_product_content').html("");
                    $('.assess_report_items_have_product_short_descriptions_that_are_too_short').html("");
                    $('.assess_report_items_have_product_long_descriptions_that_are_too_short').html("");
                }
                if (json.iTotalRecords == 0) {
                    $('.assess_report_compare_panel').hide();
                    $('.assess_report_numeric_difference').hide();
                    if ($('select[name="' + batch_sets[batch_set]['batch_batch']  + '"]').find('option:selected').val() != "") {
                        $('#summary_message').html(" - Processing data. Check back soon.");
                        //                                $('#research_assess_filter_short_descriptions_panel').show();
                        //                                $('#research_assess_filter_long_descriptions_panel').show();
                        $('.assess_report_items_1_descriptions_pnl').hide();
                        $('.assess_report_items_2_descriptions_pnl').hide();
                    }
                }
                }
            });
             if($("#tableScrollWrapper").length === 0){  
                $('#tblAssess').after('<div id="tableScrollWrapper" style="overflow-x:scroll"></div>');
                $('#tblAssess').appendTo('#tableScrollWrapper');
             }
            highChart('total_description_wc');
            var compare_batch_id = $(batch_sets[batch_set]['batch_compare']).find('option:selected').val() ;
            $.ajax({
                type: "POST",
                url: readBoardSnapUrl,
                data: {
                        batch_id: $('select[name="' + batch_sets[batch_set]['batch_batch'] + '"]').find('option:selected').val(),
                        compare_batch_id: $(batch_sets[batch_set]['batch_compare']).find('option:selected').val()
                    }
            }).done(function(data){
                if(data.length > 0){
                    console.log('1');
			resizeImp();
            if($("table[id^=tblAssess]")){
				if($("a#assess_tbl_show_case_details_compare[class^=active_link]")){
					if($("#tblAssess th[class*=1][style*='border-left-width: 2px']:not([class*=_1])")){$("#tblAssess th[class*=1][style*='border-left-width: 2px']:not([class*=_1])").css("border-left", "1px solid #ccc");}
					$("#tblAssess th[class*=1]:not([class*=_1]):first").css("border-left", "2px solid #ccc");
					$("#tblAssess tr").each(function(){
						if($(this).find("td[class*=1][style*='border-left-width: 2px']:not([class*=_1])"))
						{$(this).find("td[class*=1]:not([class*=_1])").css("border-left", "1px solid #ccc");}
						$(this).find("td[class*=1]:not([class*=_1]):first").css("border-left", "2px solid #ccc");
						
					});
				}
				console.log("borders on");
			}
                    var str = '';
                    var showcount = 12;
                    if(compare_batch_id != '0' && compare_batch_id !='all'){
                        showcount = 6 ;
                    }
                    for(var i=0; i<data.length; i++){
//                            var obj = jQuery.parseJSON(data[i][2]);
                        if(i < showcount){

                            if(data[i]['product_name'] != null && data[i]['product_name'] != '' && data[i]['snap']!=''){
                                if(data[i]['product_name'].length > 93)
                                  str += '<div id="snap'+i+'" class="board_item"><span class="span_img">'+data[i]['product_name']+'</span><br />'+data[i]['snap']+
                                      '<div class="prod_description"><b>URL:</b><br/>'+data[i]['url']+'<br /><br /><b>Product name:</b><br/>'+data[i]['product_name']+'</div></div>';
                            else
                                  str += '<div id="snap'+i+'" class="board_item"><span>'+data[i]['product_name']+'</span><br />'+data[i]['snap']+
                                      '<div class="prod_description"><b>URL:</b><br/>'+data[i]['url']+'<br /><br /><b>Product name:</b><br/>'+data[i]['product_name']+'</div></div>';
                        }
                            else{
                                str += '<div id="snap'+i+'" class="board_item"></div>'
                    }                   
                            if(compare_batch_id != '0' && compare_batch_id !='all'){
                                if(data[i]['product_name1'] != null && data[i]['product_name1'] != '' && data[i]['snap1']!=''){

        //                            console.log(data.length);
                                    if(data[i]['product_name1'].length > 93)
                                      str += '<div id="compare_snap'+i+'" class="board_item"><span class="span_img">'+data[i]['product_name1']+'</span><br />'+data[i]['snap1']+
                                          '<div class="prod_description"><b>URL:</b><br/>'+data[i]['url1']+'<br /><br /><b>Product name:</b><br/>'+data[i]['product_name1']+'</div></div>';
                                    else
                                      str += '<div id="compare_snap'+i+'" class="board_item"><span>'+data[i]['product_name1']+'</span><br />'+data[i]['snap1']+
                                          '<div class="prod_description"><b>URL:</b><br/>'+data[i]['url1']+'<br /><br /><b>Product name:</b><br/>'+data[i]['product_name1']+'</div></div>';
                                }
                                else{
                                    str += '<div id="compare_snap'+i+'" class="board_item"></div>'
                                }
                            }
                        }
                        else{
                            if(data[i]['product_name'] != null && data[i]['product_name'] != '' && data[i]['snap']!=''){
                                if(data[i]['product_name'].length > 93)
                                  str += '<div id="snap'+i+'" class="board_item" style="display: none;"><span class="span_img">'+data[i]['product_name']+'</span><br />'+data[i]['snap']+
                                      '<div class="prod_description"><b>URL:</b><br/>'+data[i]['url']+'<br /><br /><b>Product name:</b><br/>'+data[i]['product_name']+'</div></div>';
                                else
                                  str += '<div id="snap'+i+'" class="board_item" style="display: none;"><span>'+data[i]['product_name']+'</span><br />'+data[i]['snap']+
                                      '<div class="prod_description"><b>URL:</b><br/>'+data[i]['url']+'<br /><br /><b>Product name:</b><br/>'+data[i]['product_name']+'</div></div>';
                            }
                            else{
                                str += '<div id="snap'+i+'" class="board_item" style="display: none;"></div>'
                            }
                            if(compare_batch_id != '0' && compare_batch_id !='all'){
                                if(data[i]['product_name1'] != null && data[i]['product_name1'] != '' && data[i]['snap1']!=''){

        //                            console.log(data.length);
                                    if(data[i]['product_name1'].length > 93)
                                      str += '<div id="compare_snap'+i+'" class="board_item" style="display: none;"><span class="span_img">'+data[i]['product_name1']+'</span><br />'+data[i]['snap1']+
                                          '<div class="prod_description"><b>URL:</b><br/>'+data[i]['url1']+'<br /><br /><b>Product name:</b><br/>'+data[i]['product_name1']+'</div></div>';
                                    else
                                      str += '<div id="compare_snap'+i+'" class="board_item" style="display: none;"><span>'+data[i]['product_name1']+'</span><br />'+data[i]['snap1']+
                                          '<div class="prod_description"><b>URL:</b><br/>'+data[i]['url1']+'<br /><br /><b>Product name:</b><br/>'+data[i]['product_name1']+'</div></div>';
                                }
                                else{
                                    str += '<div id="compare_snap'+i+'" class="board_item" style="display: none;"></div>'
                                }
                            }
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
            $(nRow).attr("add_data", aData[34]);
            return nRow;
            $('table#tblAssess').floatThead('reflow');
        },
        "fnDrawCallback": function(oSettings) {
            tblAssess_postRenderProcessing();
            if (zeroTableDraw) {
                zeroTableDraw = false;
                return;
            }
            hideColumns();
            check_word_columns();
            $('table#tblAssess').floatThead('reflow');
			
			console.log("reflow 3");
			var status = "no ok";
				var statusinterval = setInterval( function(){
				if($("#tblAssess td").length > 1){
					status = "ok";
				}
				if(status == "ok"){clearInterval(statusinterval); 
				$("#tblAssess").colResizable({
				disable:true
				});
				$("#tblAssess").colResizable({
					liveDrag:true, 
					gripInnerHtml:"<div class='grip'></div>", 
					draggingClass:"dragging"});
				}
				},500);
			
			
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
	var batch_set = $('.result_batch_items:checked').val() || 'me';	
    var batch1Value = $('select[name="' + batch_sets[batch_set]['batch_batch'] + '"]').find('option:selected').val();
    var batch2Value = $(batch_sets[batch_set]['batch_compare']).find('option:selected').val();
    var batch1Name = $('select[name="' + batch_sets[batch_set]['batch_batch'] + '"]').find('option:selected').text();
    var batch2Name = $(batch_sets[batch_set]['batch_compare']).find('option:selected').text();
    
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
        var value1 = [];
        var value2 = [];
        var valueName = [];
        valueName[0] = [];
        valueName[1] = [];
        var valueUrl = [];
        valueUrl[0] = [];
        valueUrl[1] = [];
        var graphName1 = '';
        var graphName2 = '';
        var cloneToolTip = null;
        var cloneToolTip2 = null;
        var valueupdated = [];
        valueupdated[0] = [];
        valueupdated[1] = [];
        if(data.length) {
    
            /***First Batch - Begin***/
            if(data[0] && data[0].product_name.length > 0){
                valueName[0] = data[0].product_name;
            }
            if(data[0] && data[0].updated.length > 0){
                valueupdated[0] = data[0].updated;
            }
            if(data[0] && data[0].url.length > 0){
                valueUrl[0] = data[0].url;
            }
            /***First Batch - End***/
            /***Second Batch - Begin***/
            if(data[1] && data[1].product_name.length > 0){
                valueName[1] = data[1].product_name;
            }
             if(data[1] && data[1].updated.length > 0){
                valueupdated[1] = data[1].updated;
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
                case 'total_description_wc':{
                    if(data[0] && data[0].total_description_wc.length > 0){
                        value1 = data[0].total_description_wc;
                    }
                    
                    if(data[1] && data[1].total_description_wc.length > 0){
                        value2 = data[1].total_description_wc;
                    }
                    graphName1 = 'Total Description Word Count:';
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
//                case 'own_price':{
//                    if(data[0] && data[0].own_price.length > 0){
//                        value1 = data[0].own_price;
//                    }
//                    if(data[1] && data[1].own_price.length > 0){
//                        value2 = data[1].own_price;
//                    }
//                    graphName1 = 'Price:';
//                    graphName2 = '';
//                } break;
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
                    graphName1 = 'H1 Characters:';
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
                    graphName1 = 'H2 Characters:';
                    graphName2 = 'words';
                }
                  break;
                default:{
            
                }
            }
            /***Switch - End***/
        }
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
                spacingRight: 20,
            },
            xAxis: {
                min: 0,
                max: 300,
                categories: [],
                labels: {
                  enabled: false
                }
            },
            yAxis: {
                minPadding: 0.1,
                maxPadding: 2,
                min:0
            },
            tooltip: {
                shared: true,
                useHTML: true,
//                positioner: function (boxWidth, boxHeight, point) {
//                    if(point.plotX < bigdatalength*2.3)
//                        return { x: point.plotX +100, y: 0 };
//                    else
//                        return { x: point.plotX -300, y: 0 };
//                },
                positioner: function () {
                        return { x: 85, y: 0 };
                },
                formatter: function() {
                    var result = '<small>'+this.x+'</small> <div class="highcharts-tooltip-close" onclick=\'$(".highcharts-tooltip").css("visibility","hidden"); $("div .highcharts-tooltip span").css("visibility","hidden");\' style="float:right;">X</div><br />';
                    var j;
                     if($('#show_over_time').prop('checked')){
                            var display_property = "block";
                        }else{      
                            var display_property = "none";

                        }
                    $.each(this.points, function(i, datum) {
                        if(i > 0)
                            result += '<hr style="border-top: 1px solid #2f7ed8;margin:0;" />';
                        if(datum.series.color == '#2f7ed8')
                            j = 0;
                        else
                            j = 1;
                        result += '<b style="color: '+datum.series.color+';" >' + datum.series.name + '</b>';
                        result += '<br /><span>' + valueName[j][datum.x] + '</span>';
                        result += '<br /><a href="'+valueUrl[j][datum.x]+'" target="_blank" style="color: blue;" >' + valueUrl[j][datum.x] + '</a>';
                        result += '<br /><span>'+graphName1+' ' + datum.y + ' '+graphName2+'</span>';
                        result += '<span style="display:'+display_property+';" class="update_class">'+valueupdated[j][datum.x]+'</span>';                       
                    });
                    return result;
                }
            },

            
        plotOptions: {
            series: {
                cursor: 'pointer',
                point: {
                    events: {
                        click: function() { 
                            $('.highcharts-tooltip').first().css('visibility','visible');
                            $('div .highcharts-tooltip span').first().css('visibility','visible');
                            if (cloneToolTip)
                            {
                                chart1.container.firstChild.removeChild(cloneToolTip);
                            }
                            if (cloneToolTip2)
                            {
                                cloneToolTip2.remove();
                            }
                            cloneToolTip = this.series.chart.tooltip.label.element.cloneNode(true);
                            chart1.container.firstChild.appendChild(cloneToolTip);
                            
                            cloneToolTip2 = $('.highcharts-tooltip').clone(); 
                            $(chart1.container).append(cloneToolTip2);
                            $('.highcharts-tooltip').first().css('visibility','hidden');
                            $('div .highcharts-tooltip span').first().css('visibility','hidden');
                        }
                    }
                }
            }
        },

        scrollbar: {
            enabled:true,
			barBackgroundColor: 'gray',
			barBorderRadius: 7,
			barBorderWidth: 0,
			buttonBackgroundColor: 'gray',
			buttonBorderWidth: 0,
			buttonArrowColor: 'yellow',
			buttonBorderRadius: 7,
			rifleColor: 'yellow',
			trackBackgroundColor: 'white',
			trackBorderWidth: 1,
			trackBorderColor: 'silver',
			trackBorderRadius: 7
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
		var batch_set = $('.result_batch_items:checked').val() || 'me';		
    if($('#assess_view').children('div')) {
        var docHeight = parseInt($(document).height());
        var windHeight = parseInt($(window).height());
        var scrollTop = parseInt($(document).scrollTop());
        if(window.location.hash == '#board_view' && scrollYesOrNot && (docHeight - windHeight - scrollTop) < 100){
            scrollYesOrNot = false;
            if($('.board_item').length >= 12)
                $('#imgLoader').show();
            setTimeout(function(){
                $('#assess_view .board_item').each(function(){
                    if($(this).css('display') == 'none'){
                        $(this).css('display', 'block');
                        $(this).next().css('display', 'block');
                        $(this).next().next().css('display', 'block');
                        $(this).next().next().next().css('display', 'block');
                        $(this).next().next().next().next().css('display', 'block');
                        $(this).next().next().next().next().next().css('display', 'block');
                        $(this).next().next().next().next().next().next().css('display', 'block');
                        $(this).next().next().next().next().next().next().next().css('display', 'block');
                        return false;
                    }
                });
                    $('#imgLoader').hide();
                        $('#assess_view .board_item img').on('click', function(){
                            var info = $(this).parent().find('div.prod_description').html();
                            showSnap('<img src="'+$(this).attr('src')+'" style="float:left; max-width: 600px; margin-right: 10px">'+info);
                        });
                        $('.fadeout').each(function(){
                            $(this).fadeIn('slow');
                            $(this).removeClass('fadeout');
                        })
                        scrollYesOrNot = true;
            },1000);      
                     }
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

 function GetURLParameter(sParam) {
        var sPageURL = window.location.search.substring(1);
        var sURLVariables = sPageURL.split('&');
        for (var i = 0; i < sURLVariables.length; i++) 
        {
            var sParameterName = sURLVariables[i].split('=');
            if (sParameterName[0] == sParam) 
            {
                return sParameterName[1];
            }
        }
    }

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
	

	function numberWithCommas(x) {			
		if (x == 0 || (x + '').length <= 3)
			return x;
		
		var r = x.toString(),
			general_parts = r.match(/([0-9.]+)/g);								
		
		for (var it = 0; it < general_parts.length; it++)
		{
			var parts = general_parts[it].split('.');
			parts[0] = parts[0].replace(/(?=(\B\d{3})+(?!\d))/g, ',');
			r = r.replace(general_parts[it], parts.join("."));			
		}
		
		return r;
	}

	function transformSummarySection()
	{
		var batch_set_toggle = $('#batch_set_toggle');
		var common_batch1_filter_items = $('.common_batch1_filter_items');
		var hidden_batch2_filter_items = $('.hidden_batch2_filter_items');
		if (batch_set_toggle.is(':checked'))
		{
			$('.selectable_summary_handle_with_competitor').addClass('dual_mode');
			$('.ui-selectee, .non-selectable').css({'font-size' : 'small'});
			
			//display percentages
			$('.filter_item_percentage').show();
			
			if (!common_batch1_filter_items.hasClass('batch1_filter_items'))
				common_batch1_filter_items.addClass('batch1_filter_items');
				
			hidden_batch2_filter_items.show();
			if (!hidden_batch2_filter_items.hasClass('batch2_filter_items'))
				hidden_batch2_filter_items.addClass('batch2_filter_items');
				
			$('.batch1_filter_item, .batch2_filter_item').each(function(index, element) {
				var current_element = $(element);
				if (current_element.hasClass('batch1_filter_item')) {
					current_element.addClass('dual_batch1_filter_item');					
					current_element.removeClass('batch1_filter_item');					
				} else {
					current_element.addClass('dual_batch2_filter_item');					
					current_element.removeClass('batch2_filter_item');					
				}
			});
		} else {
			$('.selectable_summary_handle_with_competitor').removeClass('dual_mode');
			$('.ui-selectee, .non-selectable').css({'font-size' : '1em'});
			
			//hide percentages
			$('.filter_item_percentage').hide();
			
			if (common_batch1_filter_items.hasClass('batch1_filter_items'))
				common_batch1_filter_items.removeClass('batch1_filter_items');
			
			if (hidden_batch2_filter_items.hasClass('batch2_filter_items'))
				hidden_batch2_filter_items.removeClass('batch2_filter_items');
				
			hidden_batch2_filter_items.hide();
			
			$('.dual_batch1_filter_item, .dual_batch2_filter_item').each(function(index, element) {
				var current_element = $(element);
				if (current_element.hasClass('dual_batch1_filter_item')) {
					current_element.addClass('batch1_filter_item');					
					current_element.removeClass('dual_batch1_filter_item');					
				} else {
					current_element.addClass('batch2_filter_item');					
					current_element.removeClass('dual_batch2_filter_item');					
				}
			});
		}
	}
	
	/*
	** Fill all values in summary section		
	** summary - summary data
	** batch_set - batch prefix	
	** @author Oleg Meleshko <qu1ze34@gmail.com>
	*/
	function fillReportSummary(summary, batch_prefix)
	{			
		var batch_prefix = batch_prefix || 'batch_me_';
		var select_boxes = {
			'batch_me_' : {
				'batch1' : 'research_assess_batches',
				'batch2' : 'research_assess_compare_batches_batch'
			},
			'batch_competitor_' : {
				'batch1' : 'research_assess_batches_competitor',
				'batch2' : 'research_assess_compare_batches_batch_competitor'
			}
		};
		$('.' + batch_prefix + 'batch1_name').html($('select[name="' + select_boxes[batch_prefix]['batch1'] + '"]>option:selected').text());
		$('.' + batch_prefix + 'batch2_name').html($('#' + select_boxes[batch_prefix]['batch2'] + '>option:selected').text());
		
		for (var it = 0; it < summaryFieldNames.length; it++)
			if (summary[summaryFieldNames[it]] !== undefined)
			{			
				var filter_item_data_wrapper = $('.' + batch_prefix + summaryFieldNames[it]);				
				if (summary[summaryFieldNames[it] + '_icon'])
				{					
					var current_icon = $('.' + batch_prefix + summaryFieldNames[it] + '_icon')		
						, icon_src = current_icon.attr('src');
					
					current_icon.attr('src', icon_src.substring(0, icon_src.lastIndexOf('/') + 1) + summary[summaryFieldNames[it] + '_icon']);				
				}
					
				filter_item_data_wrapper.html(numberWithCommas(summary[summaryFieldNames[it]]));
			}
		
		transformSummarySection();
	}
	
    function buildReport(data) {
        if (data.ExtraData == undefined) {
            reportPanel(false);
            return;
        }
		
        var report = data.ExtraData.report;
		var batch_set = $('.result_batch_items:checked').val() || 'me';					
		
        $('.' + batch_sets[batch_set]['batch_items_prefix'] + 'assess_report_total_items').html(numberWithCommas(report.summary.total_items));
        $('.' + batch_sets[batch_set]['batch_items_prefix'] + 'assess_report_items_priced_higher_than_competitors').html(report.summary.items_priced_higher_than_competitors);
		
		fillReportSummary(report.summary, batch_sets[batch_set]['batch_items_prefix']);
				
        $('#summary_message').html("");
        if (report.summary.items_have_more_than_20_percent_duplicate_content == 0) {
            $(".items_have_more_than_20_percent_duplicate_content").hide();
        } else {
            $('.assess_report_items_have_more_than_20_percent_duplicate_content').html(report.summary.items_have_more_than_20_percent_duplicate_content);
            $(".items_have_more_than_20_percent_duplicate_content").show();
        }
        $('.assess_report_items_unoptimized_product_content').html(report.summary.items_unoptimized_product_content);
        $('#research_assess_filter_short_descriptions_panel').show();
        $('#research_assess_filter_long_descriptions_panel').show();
        short_wc_total_not_0 = report.summary.short_wc_total_not_0;
        long_wc_total_not_0 = report.summary.long_wc_total_not_0;
        items_short_products_content_short = report.summary.items_short_products_content_short;
        items_long_products_content_short = report.summary.items_long_products_content_short;
        if (report.summary.short_wc_total_not_0 > 0 && report.summary.long_wc_total_not_0 > 0) {
            $('.assess_report_items_have_product_short_descriptions_that_are_too_short').html(report.summary.items_short_products_content_short);
            $('.assess_report_items_have_product_long_descriptions_that_are_too_short').html(report.summary.items_long_products_content_short);

            $('.assess_report_items_have_product_short_descriptions_that_are_less_than_value').html(report.summary.short_description_wc_lower_range);
            $('.assess_report_items_have_product_long_descriptions_that_are_less_than_value').html(report.summary.long_description_wc_lower_range);

            $('.assess_report_items_1_descriptions_pnl').hide();
            $('.assess_report_items_2_descriptions_pnl').show();

            $('#research_assess_filter_short_descriptions_label').html("Short Descriptions:");
            $('#research_assess_filter_long_descriptions_label').html("Long Descriptions:");
            $('#research_assess_filter_short_descriptions_panel').show();
            $('#research_assess_filter_long_descriptions_panel').show();
        } else {
            $('.assess_report_items_1_descriptions_pnl').show();
            $('.assess_report_items_2_descriptions_pnl').hide();

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
                $('.assess_report_items_have_product_descriptions_that_are_too_short').html(report.summary.items_long_products_content_short);
                $('.assess_report_items_have_product_descriptions_that_are_less_than_value').html(report.summary.long_description_wc_lower_range);
            } else if (report.summary.short_wc_total_not_0 != 0 && report.summary.long_wc_total_not_0 == 0) {
                $('.assess_report_items_have_product_descriptions_that_are_too_short').html(report.summary.items_short_products_content_short);
                $('.assess_report_items_have_product_descriptions_that_are_less_than_value').html(report.summary.short_description_wc_lower_range);
            } else if (report.summary.short_wc_total_not_0 == 0 && report.summary.long_wc_total_not_0 == 0) {
                $('.assess_report_items_1_descriptions_pnl').hide();
            }
        }

        if (report.summary.items_long_products_content_short == 0 && report.summary.items_short_products_content_short == 0) {
            $('.assess_report_items_1_descriptions_pnl').hide();
            $('.assess_report_items_2_descriptions_pnl').hide();
        }

        if (report.summary.absent_items_count == undefined || report.summary.absent_items_count == 0) {
            $('.assess_report_compare_panel').hide();
        } else {
            $('.assess_report_absent_items_count').html(report.summary.absent_items_count);
            $('.assess_report_compare_customer_name').html(report.summary.compare_customer_name);
            $('.assess_report_compare_batch_name').html(report.summary.compare_batch_name);
            $('.assess_report_own_batch_name').html(report.summary.own_batch_name);
            $('.assess_report_compare_panel').show();
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
            $('.assess_report_numeric_difference_caption').html(numeric_difference_caption);
            $('.assess_report_numeric_difference').show();
        } else {
            $('.assess_report_numeric_difference').hide();
        }

        if (report.detail_comparisons_total > 0) {
            comparison_details_load();
            var comparison_pagination = report.comparison_pagination;
            $('#comparison_pagination').html(comparison_pagination);
        } else {
            $('#comparison_detail').html('');
            $('#comparison_pagination').html('');
        }
var generate_url_check = GetURLParameter('generate_url_check');
        if(!generate_url_check){
            $('.assess_report_download_panel').show();
        }else{
            $('.assess_report_download_panel').show();
            $('.assess_report_download_panel>a').hide();
            $('.assess_report_download_panel>span').hide();
            if(generate_url_check == "0")
               $('.assess_report_download_panel>button').hide();
           else
               $('.assess_report_download_panel>button').show();
               
            
        }
    }

    function comparison_details_load(url) {
		var batch_set = $('.result_batch_items:checked').val() || 'me';		
        var batch_id = $("select[name='" + batch_sets[batch_set]['batch_batch'] + "']").find("option:selected").val();
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
	
	$(document).on('click', '.update_filter_btn', function(e) {
		$('#research_assess_update').click();
	});
        var options = { path: '/', expires: 30 };
        function onDenisty(){
            var tkstatus = $.cookie('tkstatus');
            if(typeof(tkstatus)!=='undefined'){
                $.removeCookie('tkstatus');
            }
            $.cookie('tkstatus','denisty',options);
            if($('#tk-denisty').prop('checked')!==true){
                $('#tk-frequency').prop('checked',false);
                $('#tk-denisty').prop('checked',true);
            }
             $('.phr-frequency').hide();
             $('.phr-density').show();
        }
        $(document).on('click','#tk-denisty',function(){
            onDenisty();
         });
        function onFrequency(){
            var tkstatus = $.cookie('tkstatus');
            if(typeof(tkstatus)!=='undefined'){
                $.removeCookie('tkstatus');
            }
            $.cookie('tkstatus','frequency',options);
            if($('#tk-frequency').prop('checked')!==true){
                $('#tk-denisty').prop('checked',false);
                $('#tk-frequency').prop('checked',true);
            }
            $('.phr-density').hide();
            $('.phr-frequency').show();
        }
        $(document).on('click','#tk-frequency',function(){
            onFrequency();
        });
        function setStatusFromCookie(){
            var tkstatus = $.cookie('tkstatus');
            if(typeof(tkstatus)!=='undefined'){
                if(tkstatus==='denisty'){
                    onDenisty();
                }
                else{
                    onFrequency();
                }
            }
            else{
                $.cookie('tkstatus','denisty',options);
            }
        }
        function loadSetTK(){
            if($('.phr-frequency').html()!==null){
                setStatusFromCookie();
                //clearInterval(table_loaded);
            }
        }
        var table_loaded=false;
        $(document).ready(function(){
            table_loaded = setInterval(loadSetTK,10);
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
    
    var curentSibil = 0
    

    $('#tblAssess tbody').live('click',function(event) {
     var table_case = $('#assess_tbl_show_case a[class=active_link]').data('case');
      var checked_columns_results = GetURLParameter('checked_columns_results');
    
     if((table_case != "details_compare") && (checked_columns_results == undefined)){

        $('.details_left').addClass('details_width');  
        $('.details_right').hide();  
         
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
        curentSibil=target.parents('tr');
        
        console.log("ADD DATA 1 : ", add_data);
       
        $('#ajaxLoadAni').fadeIn('slow');
        $('#assessDetails_ProductName').val(add_data.product_name);
        $('#assessDetails_Model').val(add_data.model);
        $('#assessDetails_url').val(add_data.url);
        $('#assess_open_url_btn').attr('href', add_data.url);
        $('#assessDetails_Price').val(add_data.own_price);
        var short_total_not_0 = '';
        var long_total_not_0 = '';
        var long_wc_total_not_0 = 0;
        var short_wc_total_not_0 = 0;
         short_total_not_0 = add_data.short_description;
         long_total_not_0 = add_data.long_description;
         long_wc_total_not_0 = parseInt(add_data.long_description_wc);
         short_wc_total_not_0 = parseInt(add_data.short_description_wc);
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
    }else{
        $('.details_left').removeClass('details_width');  
        $('.details_right').show();
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
            if($(event.target).parents('td').hasClass('Snapshot')){
                var txt = '<div class="info_area" style="max-width: 240px;"><div id="bi_info_bar" style="float: left; width: 200px; padding-top: 20px; display: block;">' +
                        '<p style="font-size: 16px;margin-bottom: 20px;">'+ob.product_name+'</p><p><b>URL:</b><br/><span class="url">' + ob.url + '</span></p>' +
                        '<p><b>Product name:</b><br/><span class="product_name">' + ob.product_name + '</span></p>' +
                        '<p><b>Price:</b><br/><span class="price">' + ob.price_diff + '</span></p></div><div style="float: right; width: 40px;">' +
                        '<button id="bi_expand_bar_cnt" type="button" class="btn btn-success"><i class="icon-white icon-arrow-left"></i></button></div></div>';
                showSnap('<div class="snap_area"><a target="_blank" href=""><img src="' + str + '"></a></div>' + txt);
            }else{
                var txt = '<div class="info_area" style="max-width: 240px;"><div id="bi_info_bar" style="float: left; width: 200px; padding-top: 20px; display: block;">' +
                        '<p style="font-size: 16px;margin-bottom: 20px;">'+ob.product_name1+'</p><p><b>URL:</b><br/><span class="url">' + $(ob.url1).find('a').attr('href') + '</span></p>' +
                        '<p><b>Product name:</b><br/><span class="product_name">' + ob.product_name1 + '</span></p>' +
                        '<p><b>Price:</b><br/><span class="price">' + ob.price_diff + '</span></p></div><div style="float: right; width: 40px;">' +
                        '<button id="bi_expand_bar_cnt" type="button" class="btn btn-success"><i class="icon-white icon-arrow-left"></i></button></div></div>';
                showSnap('<div class="snap_area"><a target="_blank" href=""><img src="' + str + '"></a></div>' + txt);

            }
            return;
        }

        var target = $(event.target);
        if (target.parents('table').attr('class') == 'url_table')
            target = target.parents('table');
       
        var add_data = JSON.parse(target.parents('tr').attr('add_data'));
         curentSibil=target.parents('tr');
        
       // === insert title seo data (start)
       console.log("ADD DATA 2 : ", add_data);
       console.log("ADD DATA 2 (KEYWORDS): ", add_data.title_seo_phrases);
       // === insert title seo data (end)
         
        // if this product is absent product from second batch
        if (add_data.id == undefined) {
            return;
        }
        var url_compare =$(add_data.url1).find('a').attr('href');
       
        $('#ajaxLoadAni').fadeIn('slow');
        $('#assessDetails_ProductName').val(add_data.product_name);
        $('#assessDetails_Model').val(add_data.model);
        $('#assessDetails_url').val(add_data.url);
        $('#assess_open_url_btn').attr('href', add_data.url);
        $('#assessDetails_Price').val(add_data.own_price);
       
        $('#assessDetails_ProductName1').val(add_data.product_name1);
        $('#assessDetails_Model1').val(add_data.model1);
        $('#assessDetails_url1').val(url_compare);
        $('#assess_open_url_btn1').attr('href', url_compare);
        $('#assessDetails_Price1').val(add_data.competitors_prices[0]);
        var short_total_not_01 = '';
        var long_total_not_01 = '';
        var long_wc_total_not_01 = 0;
        var short_wc_total_not_01 = 0;
        var short_total_not_0 = '';
        var long_total_not_0 = '';
        var long_wc_total_not_0 = 0;
        var short_wc_total_not_0 = 0;
        
         short_total_not_01 = add_data.Short_Description1;
         long_total_not_01 = add_data.Long_Description1;
         long_wc_total_not_01 = parseInt(add_data.long_description_wc1);
         short_wc_total_not_01 = parseInt(add_data.short_description_wc1);
         
         short_total_not_0 = add_data.short_description;
         long_total_not_0 = add_data.long_description;
         long_wc_total_not_0 = add_data.long_description_wc;
         short_wc_total_not_0 = add_data.short_description_wc;
         
         short_wc_total_not_01 = short_wc_total_not_01 ? short_wc_total_not_01 : 0;
         long_wc_total_not_01 = long_wc_total_not_01 ? long_wc_total_not_01 : 0;

        if (short_wc_total_not_01 == 0 || long_wc_total_not_01 == 0) {
            $('#assessDetails_short_and_long_description_panel1').hide();
            $('#assessDetails_description_panel1').show();

            if (short_wc_total_not_01 == 0) {
                var description1 = long_total_not_01;
                var description_wc1 = long_wc_total_not_01;
                var seo_phrases1 = add_data.long_seo_phrases1;
            } else {
                var description1 = short_total_not_01;
                var description_wc1 = short_wc_total_not_01;
                var seo_phrases1= add_data.short_seo_phrases1;
            }
            $('#assessDetails_Description1').val(description1);
            $('#assessDetails_DescriptionWC1').html(description_wc1);
            $('#assessDetails_SEO1').val(seo_phrases1);
            if(typeof(add_data.title_seo_phrases1) !== 'undefined' && add_data.title_seo_phrases1 !== null && add_data.title_seo_phrases1 !== "None")$("#assessDetails_SEO1_div").html(add_data.title_seo_phrases1);
        } else {
            $('#assessDetails_short_and_long_description_panel1').show();
            $('#assessDetails_description_panel1').hide();

            $('#assessDetails_ShortDescription1').val(short_total_not_01);
            $('#assessDetails_ShortDescriptionWC1').html(short_wc_total_not_01);
            $('#assessDetails_ShortSEO1').val(add_data.short_seo_phrases1);
            $('#assessDetails_LongDescription1').val(long_total_not_01);
            $('#assessDetails_LongDescriptionWC1').html(long_wc_total_not_01);
            $('#assessDetails_LongSEO1').val(add_data.long_seo_phrases1);
        }
        if (short_wc_total_not_0 == 0 || long_wc_total_not_0 == 0) {
            $('#assessDetails_short_and_long_description_panel').hide();
            $('#assessDetails_description_panel').show();

            if (short_wc_total_not_0 == 0) {
                var description0 = long_total_not_0;
                var description_wc0 = long_wc_total_not_0;
                var seo_phrases0 = add_data.long_seo_phrases;
            } else {
                var description0 = short_total_not_0;
                var description_wc0 = short_wc_total_not_0;
                var seo_phrases0= add_data.short_seo_phrases;
            }
            $('#assessDetails_Description').val(description0);
            $('#assessDetails_DescriptionWC').html(description_wc0);
            $('#assessDetails_SEO').val(seo_phrases0);
            if(typeof(add_data.title_seo_phrases) !== 'undefined' && add_data.title_seo_phrases !== null && add_data.title_seo_phrases !== "None") $("#assessDetails_SEO_div").html(add_data.title_seo_phrases);
        } else {
            $('#assessDetails_short_and_long_description_panel').show();
            $('#assessDetails_description_panel').hide();

            $('#assessDetails_ShortDescription').val(short_total_not_0);
            $('#assessDetails_ShortDescriptionWC').html(short_wc_total_not_0);
            $('#assessDetails_ShortSEO').val(add_data.short_seo_phrases);
            $('#assessDetails_LongDescription').val(long_total_not_0);
            $('#assessDetails_LongDescriptionWC').html(long_wc_total_not_0);
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
        
        
        
    }
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
            'next': {
                text: 'Next >',
                id: 'assessDetailsDialog_btnNext',
                style: 'margin-right:35px',
                class: 'btn_next_dialog',
                click: function() {
                  nextSibilfunc(curentSibil);
                }
            },
            'prev': {
                text: '< Prev',
                id: 'assessDetailsDialog_btnPrev',
                style: 'margin-right:10px',
                class: 'btn_prev_dialog',
                click: function() {
                    prevSibilfunc(curentSibil)
                }
            },
            'Copy': {
                text: 'Copy',
                id: 'assessDetailsDialog_btnCopy',
                style: 'margin-right:125px',
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
function nextSibilfunc(curentSibil){ 
    $('.btn_prev_dialog').removeAttr('disabled');
            if(curentSibil.next().length == 0){
                if($('#tblAssess_next').hasClass('ui-state-disabled')){
                $('.btn_next_dialog').attr('disabled','disabled');
                }else{
                $('.btn_next_dialog').removeAttr('disabled');
                $('.btn_next_dialog').addClass('next_page');
                }
            }
    curentSibil.next().children().first().trigger('click')
           if($('#assessDetailsDialog_btnNext').hasClass('next_page')){
               $('#tblAssess_next').click();
               $('#assessDetailsDialog_btnNext').text('processing...')
               setTimeout(function(){
                   $('.ui-widget-overlay').css({"display":"none"})
                   $('#tblAssess tbody tr:first td:first').click();
                   $('#assessDetailsDialog_btnNext').text('Next >')
                   $('#assessDetailsDialog_btnNext').removeClass('next_page')
               },15000);
           }
}
function prevSibilfunc(curentSibil){ 
    $('.btn_next_dialog').removeAttr('disabled');
        if(curentSibil.prev().length == 0){
               if($('#tblAssess_previous').hasClass('ui-state-disabled')){
               $('.btn_prev_dialog').attr('disabled','disabled');
               }else{
               $('.btn_prev_dialog').removeAttr('disabled');
               $('.btn_prev_dialog').addClass('prev_page');
               }
           }
    curentSibil.prev().children().first().trigger('click')

       if($('#assessDetailsDialog_btnPrev').hasClass('prev_page')){
           $('#tblAssess_previous').click();
           $('#assessDetailsDialog_btnPrev').text('processing...')
          setTimeout(function(){
                   $('.ui-widget-overlay').css({"display":"none"});
                   if($('select[name="tblAssess_length"]').find('option:selected').val() == 25){
                       $('#tblAssess tbody tr.odd:last td:first').trigger('click');
                   }else{
                       $('#tblAssess tbody tr.even:last td:first').trigger('click');                     
                   }
                   $('#assessDetailsDialog_btnPrev').text('< Prev');
                   $('#assessDetailsDialog_btnPrev').removeClass('prev_page');
               },15000);
       }  
}
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
        fill_lists_batches_compare(own_customer, 0);
        check_word_columns();
    });
	
	$('select[name="research_assess_customers_competitor"]').on("change", function(res) {
        var research_assess_batches_competitor = $("select[name='research_assess_batches_competitor']");
        $.post(base_url + 'index.php/assess/filterBatchByCustomerName', {
            'customer_name': res.target.value
        }, function(data) {
            if (data.length > 0) {
                research_assess_batches_competitor.empty();
                for (var i = 0; i < data.length; i++) {
                    research_assess_batches_competitor.append('<option value="' + data[i]['id'] + '">' + data[i]['title'] + '</option>');
                }
            } else if (data.length == 0 && res.target.value != "select customer") {
                research_assess_batches_competitor.empty();
            }
            $('#research_assess_update').click();
        });
        var own_customer = $(this).val();
        fill_lists_batches_compare(own_customer, 1);
        check_word_columns();
    });

    $('#research_assess_flagged').live('click', function() {
        $('#research_assess_update').click();
    });

    function fill_lists_batches_compare(own_customer, set_number) {
		var set_number = set_number || 0;
		var sets = [{
			batch_customer : '#research_assess_compare_batches_customer',
			batch_batch : '#research_assess_compare_batches_batch',
			batch_assess_batch : 'research_assess_batches'
		}, {
			batch_customer : '#research_assess_compare_batches_customer_competitor',
			batch_batch : '#research_assess_compare_batches_batch_competitor',
			batch_assess_batch : 'research_assess_batches_competitor'
		}];
		
        var research_assess_compare_batches_customer = $(sets[set_number]['batch_customer']);
        var research_assess_compare_batches_batch = $(sets[set_number]['batch_batch']);
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
                        var own_batch_id = $("select[name='" + sets[set_number]['batch_assess_batch'] + "']").find("option:selected").val();
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
        
        $.ajax({
            type: "POST",
            url: rememberBatchValue,
            data: {compare_batch_id: $('select[id="research_assess_compare_batches_batch"]').find('option:selected').val()}
           
        });
        
        
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
	
	$('#batch_set_toggle').on('change', function() {	
		var second_batch_set = $('.research_table_filter_competitor');
		var batch_set_depend_options = $('.batch_set_depend_options');
		if ($(this).is(':checked'))
		{
			$('.result_batch_items')[1].click(); //activating second batch set
			second_batch_set.slideDown();
			batch_set_depend_options.show();
		}
		else
		{
			$('.result_batch_items')[0].click(); //activating first batch set by default
			second_batch_set.slideUp();
			batch_set_depend_options.hide();
			
			$('#research_assess_update').click(); // clicking on Update btn
		}
	});
	
    $('#research_assess_compare_batches_reset').click(function() {       
		$('#research_assess_compare_batches_customer').val('select customer').prop('selected', true);
        $('#research_assess_compare_batches_batch').val('select batch').prop('selected', true);
				
		$('#research_assess_compare_batches_customer_competitor').val('select customer').prop('selected', true);
        $('#research_assess_compare_batches_batch_competitor').val('select batch').prop('selected', true);
		
        $('#research_assess_update').click();
    });

    $('select[name="research_assess_batches"]').on("change", function() {
        var selectedBatch = $(this).find("option:selected").text();
        var selectedBatchId = $(this).find("option:selected").val();
        $('.assess_report_download_panel').hide();
//        alert('sdhfbh');
        
        $.ajax({
            type: "POST",
            url: rememberBatchValue,
            data: {batch_id: $('select[name="research_assess_batches"]').find('option:selected').val()},
           
        });
        
        
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
			console.log('research_assess_batches on change event');
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
            fill_lists_batches_compare(own_customer, 0);
            var batch_id_result = GetURLParameter('batch_id_result');
            if(!batch_id_result)
            {              
                $('#research_assess_update').click();         
            }
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
	
	$('select[name="research_assess_batches_competitor"]').on("change", function() {
        var selectedBatch = $(this).find("option:selected").text();
        var selectedBatchId = $(this).find("option:selected").val();
        $('.assess_report_download_panel').hide();
        
        $.ajax({
            type: "POST",
            url: rememberBatchValue,
            data: {batch_id: selectedBatchId},           
        });        
        
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
			console.log('research_assess_batches_competitor on change event');
            buildReport(data);
        }
        $.post(base_url + 'index.php/assess/filterCustomerByBatch', {
            'batch': selectedBatch
        }, function(data) {
            var research_assess_customers_competitor = $('select[name="research_assess_customers_competitor"]');
            if (data != '') {
                research_assess_customers_competitor.val(data.toLowerCase()).prop('selected', true);
            } else {
                research_assess_customers_competitor.val('select customer').prop('selected', true);
            }
            if (selectedBatch.length == 0)
                research_assess_customers_competitor.val('select customer').prop('selected', true);
            var own_customer = research_assess_customers_competitor.val();
            fill_lists_batches_compare(own_customer, 1);
            var batch_id_result = GetURLParameter('batch_id_result');
            if(!batch_id_result)
            {              
                $('#research_assess_update').click();         
            }
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
        if(first_click){
        
        if ($("#research_assess_compare_batches_batch").val() == 'all' || $("#research_assess_compare_batches_batch_competitor").val() == 'all') {
            console.log(1);			
            createTable();
            serevr_side = false;
            return;
        } else {
            if (!serevr_side) {
				console.log(21);
                //$("#tblAssess").dataTable().fnClearTable();
                //$('#tblAssess_wrapper').remove();
                createTableByServerSide();
                tblAllColumns = tblAssess.fnGetAllSColumnNames();
                serevr_side = true;

            } else {
				console.log(22);
                serevr_side = true;
                readAssessData();

            }
        }


        addColumn_url_class();
        check_word_columns();
        }
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
//function columns_name(name,cnt,exception){
//     var num=0;
//     $("td."+name).each(function() {
//        if ($(this).text()!='') {
//            num += 1;
//        }
//     }); 
//     $.each(tblAllColumns, function(index, value) {
////          if(name == exception){
//          if((value === name && num == 0)){
//                tblAssess.fnSetColumnVis(index, false, false);
////                tblAssess.fnSetColumnVis(index+1, false, false);
//            }
////          }
//      })
//      
//     var num1=0;
//     $("td."+name.concat("1")+"").each(function() {
//        if ($(this).text()!='') {
//            num1 += 1;
//        }
//     }); 
//     var name1 = name.concat("1");
//     $.each(tblAllColumns, function(index, value) {
//          if(name1 == exception){
//          if((value == name1 && num1 == 0)){
//                tblAssess.fnSetColumnVis(index, false, false);
//                tblAssess.fnSetColumnVis(index+1, false, false);
//            }
//          }
//      })  
//}
   function check_word_columns() {
//       columns_name('short_description_wc',4)
//       columns_name('long_description_wc',4)
//       columns_name('item_id',4)
//       columns_name('Meta_Keywords',4)
//       columns_name('Page_Load_Time',4)
//       columns_name('Short_Description',4)
//       columns_name('Long_Description',4)
//       columns_name('average_review',4)
//       columns_name('column_reviews',4)
//       columns_name('model',4)
//       columns_name('column_external_content',4)
//       columns_name('Custom_Keywords_Short_Description',4)
//       columns_name('Custom_Keywords_Long_Description',4)
//       columns_name('Meta_Description',4,'Meta_Description')
//       columns_name('HTags_1',4,'HTags_1')
//       columns_name('HTags_2',4,'HTags_2')
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
        var HTags_11 = 0;
        var HTags_2 = 0;
        var HTags_21 = 0;
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
//        var column_reviews = 0;
//        var column_reviews1 = 0;
//        var column_reviews2 = 0;
//        var column_reviews3 = 0;
//        var column_reviews4 = 0;
        var model = 0;
        var model1 = 0;
        var model2 = 0;
        var model3 = 0;
        var model4 = 0;
        var column_external_content = 0;
        var column_external_content1 = 0;
        var column_external_content2 = 0;
        var column_external_content3 = 0;
        var column_external_content4 = 0;
        var Custom_Keywords_Short_Description = 0;
        var Custom_Keywords_Long_Description = 0;
        var title_seo_phrases = 0;
        var title_seo_phrases1 = 0;
        var images_cmp = 0;
        var images_cmp1 = 0;
        var video_count = 0;
        var video_count1 = 0;
        var title_pa = 0;
        var title_pa1 = 0;
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
        $('td.HTags_11').each(function() {
            
            if ($(this).text()!='') {
                HTags_11 += 1;
            }
        });
        $('td.HTags_21').each(function() {
            
            if ($(this).text()!='') {
                HTags_21 += 1;
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
             var txt = parseInt($(this).text());
            if (txt > 0) {
                Page_Load_Time += 1;
            }
        });
        $('td.Page_Load_Time1').each(function() {
            var txt = parseInt($(this).text());
            if (txt > 0) {
                Page_Load_Time1 += 1;
            }
        });
        $('td.Page_Load_Time2').each(function() {
             var txt = parseInt($(this).text());
            if (txt > 0) {
                Page_Load_Time2 += 1;
            }
        });
        $('td.Page_Load_Time3').each(function() {
             var txt = parseInt($(this).text());
            if (txt > 0) {
                Page_Load_Time3 += 1;
            }
        });
        $('td.Page_Load_Time4').each(function() {
            var txt = parseInt($(this).text());
            if (txt > 0) {
                Page_Load_Time4 += 1;
            }
        });
        $('td.average_review').each(function() {
            var txt = parseInt($(this).text());
            if (txt > 0) {
                average_review += 1;
            }
        });
        $('td.average_review1').each(function() {
           var txt = parseInt($(this).text());
            if (txt > 0) {
                average_review1 += 1;
            }
        });
        $('td.average_review2').each(function() {
            var txt = parseInt($(this).text());
            if (txt > 0) {
                average_review3 += 1;
            }
        });
        $('td.average_review3').each(function() {
           var txt = parseInt($(this).text());
            if (txt > 0) {
                average_review3 += 1;
            }
        });
        $('td.average_review4').each(function() {
           var txt = parseInt($(this).text());
            if (txt > 0) {
                average_review4 += 1;
            }
        });
//        $('td.column_reviews').each(function() {             
//            var txt = parseInt($(this).text());
//            if (txt > 0) {
//                column_reviews += 1;
//            }
//        });
//        $('td.column_reviews1').each(function() {
//            var txt = parseInt($(this).text());
//            if (txt > 0) {
//                column_reviews1 += 1;
//            }
//        });
//        $('td.column_reviews2').each(function() {
//            var txt = parseInt($(this).text());
//            if (txt > 0) {
//                column_reviews2 += 1;
//            }
//        });
//        $('td.column_reviews3').each(function() {
//            var txt = parseInt($(this).text());
//            if (txt > 0) {
//                column_reviews3 += 1;
//            }
//        });
//        $('td.column_reviews4').each(function() {
//           var txt = parseInt($(this).text());
//            if (txt > 0) {
//                column_reviews4 += 1;
//            }
//        });
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
        $('td.column_external_content').each(function() {
            if ($(this).text()!='') {
                column_external_content += 1;
            }
        });
        $('td.column_external_content1').each(function() {
            if ($(this).text()!='') {
                column_external_content1 += 1;
            }
        });
        $('td.column_external_content2').each(function() {
            if ($(this).text()!='') {
                column_external_content2 += 1;
            }
        });
        $('td.column_external_content3').each(function() {
            if ($(this).text()!='') {
                column_external_content3 += 1;
            }
        });
        $('td.column_external_content4').each(function() {
            if ($(this).text()!='') {
                column_external_content4 += 1;
            }
        });
        $('td.title_seo_phrases').each(function() {
            if ($(this).text()!='') {
                title_seo_phrases += 1;
            }
        });
        $('td.title_seo_phrases1').each(function() {
            if ($(this).text()!='') {
                title_seo_phrases1 += 1;
            }
        });
        $('td.images_cmp').each(function() {
            if ($(this).text()!='') {
                images_cmp += 1;
            }
        });
        $('td.images_cmp1').each(function() {
            if ($(this).text()!='') {
                images_cmp1 += 1;
            }
        });
        $('td.video_count').each(function() {
            if ($(this).text()!='') {
                video_count += 1;
            }
        });
        $('td.video_count1').each(function() {
            if ($(this).text()!='') {
                video_count1 += 1;
            }
        });
        $('td.title_pa').each(function() {
            if ($(this).text()!='') {
                title_pa += 1;
            }
        });
        $('td.title_pa1').each(function() {
            if ($(this).text()!='') {
                title_pa1 += 1;
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
            if (value == 'title_seo_phrases' && title_seo_phrases == 0) {
                tblAssess.fnSetColumnVis(index, false, false);
            }
            if (value == 'title_seo_phrases1' && title_seo_phrases1 == 0) {
                tblAssess.fnSetColumnVis(index, false, false);
            }
            if (value == 'images_cmp' && images_cmp == 0) {
                tblAssess.fnSetColumnVis(index, false, false);
            }
            if (value == 'images_cmp1' && images_cmp1 == 0) {
                tblAssess.fnSetColumnVis(index, false, false);
            }
            if (value == 'video_count' && video_count == 0) {
                tblAssess.fnSetColumnVis(index, false, false);
            }
            if (value == 'video_count1' && video_count1 == 0) {
                tblAssess.fnSetColumnVis(index, false, false);
            }
            if (value == 'title_pa' && title_pa == 0) {
                tblAssess.fnSetColumnVis(index, false, false);
            }
            if (value == 'title_pa1' && title_pa1 == 0) {
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
             if((value == 'H1_Tags1' && HTags_11 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
                tblAssess.fnSetColumnVis(index+1, false, false);
            }

            if((value == 'H2_Tags1' && HTags_21 == 0)){
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
//            if((value == 'column_reviews' && column_reviews == 0)){
//                tblAssess.fnSetColumnVis(index, false, false);
//               
//            }
//            if((value == 'column_reviews1' && column_reviews1 == 0)){
//                tblAssess.fnSetColumnVis(index, false, false);
//               
//            }
//            if((value == 'column_reviews2' && column_reviews2 == 0)){
//                tblAssess.fnSetColumnVis(index, false, false);
//               
//            }
//            if((value == 'column_reviews3' && column_reviews3 == 0)){
//                tblAssess.fnSetColumnVis(index, false, false);
//               
//            }
//            if((value == 'column_reviews4' && column_reviews4 == 0)){
//                tblAssess.fnSetColumnVis(index, false, false);
//               
//            }
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
            if((value == 'column_external_content' && column_external_content == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
                
            }
            if((value == 'column_external_content1' && column_external_content1 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
                
            }
            if((value == 'column_external_content2' && column_external_content2 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
                
            }
            if((value == 'column_external_content3' && column_external_content3 == 0)){
                tblAssess.fnSetColumnVis(index, false, false);
                
            }
            if((value == 'column_external_content4' && column_external_content4 == 0)){
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

    $('.assess_report_download_panel > a').click(function() {
        var type_doc = $(this).data('type');
        assess_report_download(type_doc);
    });

    function assess_report_download(type_doc) {
		var batch_set = $('.result_batch_items:checked').val() || 'me';	
        var batch_name = $("select[name='" + batch_sets[batch_set]['batch_batch'] + "']").find("option:selected").text();
        //var batch_id = $("select[name='research_assess_batches']").find("option:selected").val();
        var compare_batch_id = $(batch_sets[batch_set]['batch_compare']).val();
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
            $('#research_assess_choiceColumnDialog, #summary_filters_configuration_wrapper').css({
                'width':'1200'                
            });  
            $('#research_assess_choiceColumnDialog, #summary_filters_configuration_wrapper').parent().css({
            'left':'50%',
             'margin-left':'-600px'                
             });  
        }
        else{
            $("#vertical").css('visibility', 'hidden') ;
            $("#horizontal").css('visibility', 'visible') ;
            $("#columns_checking p").css('display','block');
            $("#columns_checking p").css('float','');
            $('#research_assess_choiceColumnDialog, #summary_filters_configuration_wrapper').css('width','250px');
            $('#research_assess_choiceColumnDialog, #summary_filters_configuration_wrapper').parent().css({
             'margin-left':'-137px'                
             }); 
        }
    });
    $(".research_assess_choiceColumnDialog_checkbox").change(function(){
         // get columns params
                var columns = {
                    snap: $("#column_snap").attr('checked') == 'checked',
                    created: $("#column_created").attr('checked') == 'checked',
                    imp_data_id: $("#imp_data_id").attr('checked') == 'checked',
                    product_name: $("#column_product_name").attr('checked') == 'checked',
//                    item_id: $("#item_id").attr('checked') == 'checked',
                    model: $("#model").attr('checked') == 'checked',
                    url: $("#column_url").attr('checked') == 'checked',
                    Page_Load_Time: $("#Page_Load_Time").attr('checked') == 'checked',
                    Short_Description: $("#Short_Description").attr('checked') == 'checked',
                    short_description_wc: $("#column_short_description_wc").attr('checked') == 'checked',
                    Meta_Keywords: $("#Meta_Keywords").attr('checked') == 'checked',
                    short_seo_phrases: $("#column_short_seo_phrases").attr('checked') == 'checked',
                    title_seo_phrases: $("#column_title_seo_phrases").attr('checked') == 'checked',
                    images_cmp: $("#column_images_cmp").attr('checked') == 'checked',
                    video_count: $("#column_video_count").attr('checked') == 'checked',
                    title_pa: $("#column_title_pa").attr('checked') == 'checked',
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
                    average_review: $("#average_review").attr('checked') == 'checked',
                    column_features: $("#column_features").attr('checked') == 'checked',
                    price_diff: $("#column_price_diff").attr('checked') == 'checked',
                    gap: $("#gap").attr('checked') == 'checked',
                    Duplicate_Content: $("#Duplicate_Content").attr('checked') == 'checked',
                    images_cmp: $("#images_cmp").attr('checked') == 'checked',
                    title_pa: $("#title_pa").attr('checked') == 'checked',
                    video_count: $("#video_count").attr('checked') == 'checked'
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
	
	function fill_summary_config_filters(setting_values)
	{
		$('.summary_filter_config_item').each(function(index, element) {
			$(this).removeAttr('checked');
		});
		
		for (var it = 0; it < setting_values.length; it++)
		{
			$('.summary_filter_config_item[data-realfilterid="' + setting_values[it] + '"]').attr('checked', 'checked');
		}
	}
	
	$.ajax({
		url : get_summary_filters,
		type : 'GET',
		dataType : 'json',
		success : function(data) {
			if (data && data.setting_value)
			{
				fill_summary_config_filters(JSON.parse(data.setting_value));				
			}
		}
	});
	
	$('#summary_filters_configuration_wrapper').dialog({
		autoOpen : false,
		resizable: false,
		modal : true,
		width : 'auto'
	});
	
	$('.show_filters_configuration_popup').on('click', function() {
		$('#summary_filters_configuration_wrapper').dialog('open');
	});
	
	$('.summary_filter_config_item').on('click', function() {
	
		var elem = $(this)
		  , filter_elem = $('.item_line[data-filterid*="' + elem.data('realfilterid') + '"], .batch_me_and_competitor[data-filterid*="' + elem.data('realfilterid') + '"]');
		
		summary_active_items = [];
		
		if (elem.is(':checked'))	
		{
			filter_elem.show();
			
			if (!filter_elem.hasClass('selected_by_config'))
				filter_elem.addClass('selected_by_config');
		} else {
			filter_elem.hide();		
			
			if (filter_elem.hasClass('selected_by_config'))
				filter_elem.removeClass('selected_by_config');
		}
		
		$('.summary_filter_config_item').each(function(index, element) {
			var config_item = $(this);
			if (config_item.is(':checked'))
			{
				summary_active_items.push(config_item.data('realfilterid'));
			}
		});
		
		$.ajax({
			url : save_summary_filters,
			data : {
				summary_active_items : summary_active_items
			},
			type : 'POST',
			dataType : 'json',
			success : function(data) {
				console.log(data);
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

    $('.assess_report_options_dialog_button').on('click', function() {
		var batch_set = $('.result_batch_items:checked').val() || 'me';		
        var selected_batch_id = $('select[name="' + batch_sets[batch_set]['batch_batch'] + '"] option:selected').val();
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
		var batch_set = $('.result_batch_items:checked').val() || 'me';	
        var table_case = 'details_compare';
        var checked_columns_results = GetURLParameter('checked_columns_results');
    if(checked_columns_results){
             if($('#assess_tbl_show_case a[class=active_link]').data('case') == 'details_compare_result'){
         table_case = 'details_compare_result';
    }else{
                 table_case = 'graph';
             }
        }else{
        
        table_case = $('#assess_tbl_show_case a[class=active_link]').data('case');
    }
        var columns_checkboxes = $('#research_assess_choiceColumnDialog').find('input[type=checkbox]:checked');
        var columns_checkboxes_checked = [];
        $.each(columns_checkboxes, function(index, value) {
            columns_checkboxes_checked.push($(value).data('col_name'));
        });
		
		//turn off related blocks here
		toggleRelatedBlocks('details_compare', false);

        if (table_case == 'recommendations') {
            $('#graphDropDown').remove();
            $('#show_over_time').remove();
            $('#show_over_time_span').remove();
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
            $('#show_over_time').remove();
            $('#show_over_time_span').remove();
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
			 
			/**
			 * using one place to turn on/off different blocks			 			 	
			 */				 
			toggleRelatedBlocks('details_compare', true);
			
            $('#graphDropDown').remove();
            $('#show_over_time').remove();
            $('#show_over_time_span').remove();
            $('#assess_graph').hide();
            $('#tblAssess_info').show();
            $('#tblAssess_paginate').show();
            reportPanel(false);
            $.each(tblAllColumns, function(index, value) {
                value = value.replace(/[0-9]$/, "");
              
                if ($.inArray(value, tableCase.details_compare) > -1 && $.inArray(value, columns_checkboxes_checked) > -1) {
                    tblAssess.fnSetColumnVis(index, true, false);
              
                
                }
                else if(value==='H1_Tags_Count' || value==='H2_Tags_Count' || value ==='Meta_Description_Count' ){
                    if ($.inArray("Meta_Description", columns_checkboxes_checked) > -1) {
                    tblAssess.fnSetColumnVis(index, true, false);
                    }
                    else if($.inArray("H1_Tags", columns_checkboxes_checked) > -1){
                        tblAssess.fnSetColumnVis(index, true, false);
                    }
                    else if($.inArray("H2_Tags", columns_checkboxes_checked) > -1){
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
        
        }else if (table_case == 'details_compare_result') {
            toggleRelatedBlocks('details_compare_result', true);
            $('#graphDropDown').remove();
            $('#show_over_time').remove();
            $('#show_over_time_span').remove();
            $('#assess_graph').hide();
            $('#tblAssess_info').show();
            $('#tblAssess_paginate').show();
            reportPanel(false);

            $.each(tblAllColumns, function(index, value) {
           
                value = value.replace(/[0-9]$/, "");
                if ($.inArray(value, tableCase.details_compare) > -1 && $.inArray(value, columns_checkboxes_checked) > -1) {
                    tblAssess.fnSetColumnVis(index, true, false);
              
                
                }
                else if(value==='H1_Tags_Count' || value==='H2_Tags_Count' || value ==='Meta_Description_Count' ){
                    if ($.inArray("Meta_Description", columns_checkboxes_checked) > -1) {
                    tblAssess.fnSetColumnVis(index, true, false);
                    }
                    else if($.inArray("H1_Tags", columns_checkboxes_checked) > -1){
                        tblAssess.fnSetColumnVis(index, true, false);
                    }
                    else if($.inArray("H2_Tags", columns_checkboxes_checked) > -1){
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
        } 
        else if (table_case == 'report') {
            $('#graphDropDown').remove();
            $('#show_over_time').remove();
            $('#show_over_time_span').remove();
            $('#tblAssess_info').show();
            $('#tblAssess_paginate').show();
            $('#assess_graph').hide();
            reportPanel(true);
            var batch_id = $('select[name="' + batch_sets[batch_set]['batch_batch'] + '"]').find('option:selected').val();
            //$('.assess_report_download_pdf').attr('href', base_url + 'index.php/research/assess_download_pdf?batch_name=' + batch_name);
        } else if (table_case == 'view') {
            toggleRelatedBlocks('view', true);
            $('#graphDropDown').remove();
            $('#show_over_time').remove();
            $('#show_over_time_span').remove();
            $('#tblAssess_info').hide();
            $('#tblAssess_paginate').hide();
            $('#assess_graph').hide();
            $('#tblAssess').hide();
            $('#tblAssess').parent().find('div.ui-corner-bl').hide();
            $('#assess_view').show();
            $('.assess_report').hide();
            var batch_id = $('select[name="' + batch_sets[batch_set]['batch_batch'] + '"]').find('option:selected').val();
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
			toggleRelatedBlocks('graph', true);
            $('#graphDropDown').remove();
            $('#show_over_time').remove();
            $('#show_over_time_span').remove();
            $('#tblAssess_info').hide();
            var dropDownString;
            dropDownString = '<select id="graphDropDown" style="width: 235px" >';
            dropDownString += '<option value="total_description_wc" >Total Description Word Counts</option>';
                dropDownString += '<option value="short_description_wc" >Short Description Word Counts</option>';
                dropDownString += '<option value="long_description_wc" >Long Description Word Counts</option>';
                dropDownString += '<option value="h1_word_counts" >H1 Character Counts</option>';
                dropDownString += '<option value="h2_word_counts" >H2 Character Counts</option>';
                dropDownString += '<option value="revision" >Reviews</option>';
                dropDownString += '<option value="Features" >Features</option>';
//                dropDownString += '<option value="own_price" >Prices</option>';
            dropDownString += '</select><input id="show_over_time" style="width: 30px;" type="checkbox"><span id="show_over_time_span">Show changes over time</span>';    
            $('#tblAssess_info').after(dropDownString);
            $('#tblAssess_paginate').hide();
            $('.board_view').hide();
            $('#tblAssess').hide();
            $('#tblAssess').parent().find('div.ui-corner-bl').hide();
            $('.assess_report').hide();
            $('#assess_view').hide();
            $('#assess_graph').show();
        }
    }
	
	/*	
	* toggleRelatedBlocks('details_compare', true);
	* @author Oleg Meleshko
	*/	
	function toggleRelatedBlocks(tabName, isDisplayed)
	{	
		if (tabsRelatedBlocks[tabName])
			tabsRelatedBlocks[tabName].call(null, isDisplayed);
	}

    function reportPanel(visible) {
        if (visible) {
            $('#tblAssess').hide();
            $('#tblAssess').parent().find('div.ui-corner-bl').hide();
            $('.assess_report').show();
        } else {
            $('#tblAssess').show();
            $('#tblAssess').parent().find('div.ui-corner-bl').show();
            $('.assess_report').hide();
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
 function buildTableParams1(existingParams) {

        var assessRequestParams = collectionParams1();
        for (var p in assessRequestParams) {
            existingParams.push({
                "name": p,
                "value": assessRequestParams[p]
            });

        }
        return existingParams;
    }
    function collectionParams1() {
		var batch_set = $('.result_batch_items:checked').val() || 'me';	
		
        var assessRequestParams = {};

        assessRequestParams.search_text = $('#assess_filter_text').val();
        assessRequestParams.batch_id = $('select[name="' + batch_sets[batch_set]['batch_batch'] + '"]').find('option:selected').val();

        var assess_filter_datefrom = $('#assess_filter_datefrom').val();
        var assess_filter_dateto = $('#assess_filter_dateto').val();
        if (assess_filter_datefrom && assess_filter_dateto) {
            assessRequestParams.date_from = assess_filter_datefrom,
                    assessRequestParams.date_to = assess_filter_dateto
        }

        if ($("select[name='" + batch_sets[batch_set]['batch_batch'] + "'").val() != 0 && $(batch_sets[batch_set]['batch_compare']).val() != 0 && $(batch_sets[batch_set]['batch_compare']).val() != null) {
            assessRequestParams.batch2 = $(batch_sets[batch_set]['batch_compare']).find('option:selected').val();

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

        var research_assess_compare_batches_batch = $(batch_sets[batch_set]['batch_compare']).val();
        if (research_assess_compare_batches_batch > 0) {
            assessRequestParams.compare_batch_id = research_assess_compare_batches_batch;
        }

        return assessRequestParams;
    }
    
    function collectionParams() {
		var batch_set = $('.result_batch_items:checked').val() || 'me';		
		
        var assessRequestParams = {};
       
var batch_id_result = GetURLParameter('batch_id_result');
var cmp_selected = GetURLParameter('cmp_selected');
var search_text = GetURLParameter('search_text');

        if(search_text){
            assessRequestParams.search_text = search_text;
        }else{
            assessRequestParams.search_text = $('#assess_filter_text').val();
            
        }
        if(batch_id_result){
            assessRequestParams.batch_id = batch_id_result;            
        }else{
            assessRequestParams.batch_id = $('select[name="' + batch_sets[batch_set]['batch_batch'] + '"]').find('option:selected').val();            
        }

        var assess_filter_datefrom = $('#assess_filter_datefrom').val();
        var assess_filter_dateto = $('#assess_filter_dateto').val();
        if (assess_filter_datefrom && assess_filter_dateto) {
            assessRequestParams.date_from = assess_filter_datefrom,
                    assessRequestParams.date_to = assess_filter_dateto
        }

        if(cmp_selected){
                    assessRequestParams.batch2 = cmp_selected;   
        }else if($("select[name='" + batch_sets[batch_set]['batch_batch'] + "'").val() != 0 && $(batch_sets[batch_set]['batch_compare']).val() != 0 && $(batch_sets[batch_set]['batch_compare']).val() != null) {
            assessRequestParams.batch2 = $(batch_sets[batch_set]['batch_compare']).find('option:selected').val();

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
            if ($('#research_assess_title_seo_phrases').is(':checked')) {
                assessRequestParams.title_seo_phrases = true;
            }
            if ($('#research_assess_images_cmp').is(':checked')) {
                assessRequestParams.images_cmp = true;
            }
            if ($('#research_assess_video_count').is(':checked')) {
                assessRequestParams.video_count = true;
            }
            if ($('#research_assess_title_pa').is(':checked')) {
                assessRequestParams.title_pa = true;
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

        var research_assess_compare_batches_batch = $(batch_sets[batch_set]['batch_compare']).val();
       
        if(cmp_selected){
            assessRequestParams.compare_batch_id = cmp_selected;
                       
        }else if (research_assess_compare_batches_batch > 0) {
            assessRequestParams.compare_batch_id = research_assess_compare_batches_batch;
        }
        return assessRequestParams;
    }
    function readAssessData() {
        $('.assess_report_download_panel').hide();
        $("#tblAssess tbody tr").remove();
        tblAssess.fnDraw();
    }

    hideColumns();
    check_word_columns();
    $('.assess_report_download_panel').hide();

//    $(document).on('mouseenter', 'i.snap_ico', function () {
//     var snap = "webshoots/" + $(this).attr('snap');
//     $("#assess_preview_crawl_snap_modal .snap_holder").html("<img src='" + base_url +  snap + "'>");
//     $("#assess_preview_crawl_snap_modal").modal('show');
//     });
    $(document).on('mouseleave', '#assess_preview_crawl_snap_modal', function() {
        $(this).modal('hide');
    });
    $('#export_unmatches').live('click',function() {
        var batch_id= $('select[name="research_assess_batches"]').find('option:selected').val();
        var batch_name= $('select[name="research_assess_batches"]').find('option:selected').text()+' - '+$('#research_assess_compare_batches_batch').find('option:selected').text();
        var cmp_selected = $('#research_assess_compare_batches_batch').find('option:selected').val();	
       $(this).text('Exporting...');
        var main_path=  $(this).prop('href');
        $(this).attr('href', $(this).prop('href')+'?batch_id='+batch_id+'&cmp_selected='+cmp_selected+'&batch_name='+batch_name);
        
        $.fileDownload($(this).prop('href'))
                .done(function() {
            $('#export_unmatches').removeAttr('disabled');
            $('#export_unmatches').attr('href', main_path);
            $('#export_unmatches').text('Unmatched');
        })
                .fail(function() {
        });
   });
    
   $('#research_assess_export').live('click',function() {
		var batch_set = $('.result_batch_items:checked').val() || 'me';
       if(!GetURLParameter('checked_columns_results')){

            $(this).attr('disabled', true);
            var batch_id= $('select[name="' + batch_sets[batch_set]['batch_batch'] + '"]').find('option:selected').val();
            var batch_name= $('select[name="' + batch_sets[batch_set]['batch_batch'] + '"]').find('option:selected').text();
            var cmp_selected = $(batch_sets[batch_set]['batch_compare']).val();
            
       }else{
            
            $(this).attr('disabled', true);
            var batch_id= GetURLParameter('batch_id_result');
            var  batch_name=GetURLParameter('batch_name');
            var cmp_selected = GetURLParameter('cmp_selected');
         
       }  
        var columns_check = $('#research_assess_choiceColumnDialog').find('input[type=checkbox]:checked');
            var columns_checked = [];
            $.each(columns_check, function(index, value) {
                columns_checked.push($(value).data('col_name'));
            });
            
           var summaryFilterData = summaryInfoSelectedElements.join(',')
          
            
        $(this).text('Exporting...');
        var main_path=  $(this).prop('href');
        $(this).attr('href', $(this).prop('href')+'?batch_id='+batch_id+'&cmp_selected='+cmp_selected+'&checked_columns='+columns_checked+'&batch_name='+batch_name+'&summaryFilterData='+summaryFilterData);
		console.log();
        $.fileDownload($(this).prop('href'))
                .done(function() {
            $('#research_assess_export').removeAttr('disabled');
            $('#research_assess_export').attr('href', main_path);
            $('#research_assess_export').text('Export');
        })
                .fail(function() {
        });
        
    });
	
$('table#tblAssess').floatThead({
	scrollContainer: function($table) {
		return $('#tblAssess').closest('.wrapper');
	}
});
function resizeImpDown(){
	$("#tblAssess").colResizable({
			disable:true
			});
	$("#tblAssess").colResizable({
		liveDrag:true, 
		gripInnerHtml:"<div class='grip'></div>", 
		draggingClass:"dragging"
});
}
function darkHeaders(id) {
	if($("table[id^=tblAssess]")){
		if($("a#assess_tbl_show_case_details_compare[class^=active_link]")){
			if($("#tblAssess th[class*=1][style*='border-left-width: 2px']:not([class*=_1])")){$("#tblAssess th[class*=1][style*='border-left-width: 2px']:not([class*=_1])").css("border-left", "1px solid #ccc");}
			$("#tblAssess th[class*=1]:not([class*=_1]):first").css("border-left", "2px solid #ccc");
			$("#tblAssess tr").each(function(){
				if($(this).find("td[class*=1][style*='border-left-width: 2px']:not([class*=_1])"))
				{$(this).find("td[class*=1]:not([class*=_1])").css("border-left", "1px solid #ccc");}
				$(this).find("td[class*=1]:not([class*=_1]):first").css("border-left", "2px solid #ccc");
				
			});
		}
		
	}
	$('table#tblAssess').floatThead('reflow');
}
$('#tableScrollWrapper').css("overflow-y", "hidden");
$( "div[id^=tblAssess_length], div[id^=assess_tbl_show_case], div[class^=dataTables_filter], div[id^=tblAssess_processing]" ).wrapAll( "<div class='fg-toolbar ui-toolbar ui-widget-header ui-corner-tl ui-corner-tr ui-helper-clearfix'></div>" );
$( "#tblAssess_info, #tblAssess_paginate" ).wrapAll( "<div class='fg-toolbar ui-toolbar ui-widget-header ui-corner-bl ui-corner-br ui-helper-clearfix'></div>" );
$('#assess_tbl_show_case_recommendations').click(function() {
    console.log("RECOMENDATIONS");
	
	$('table#tblAssess').floatThead({ 
		scrollContainer: function($table) {
			return $('#tblAssess').closest('.wrapper');
		}
	});
	$('table#tblAssess').floatThead('reflow');
	resizeImp();	
});
$('#assess_tbl_show_case_details_compare').click(function() {
	$('table#tblAssess').floatThead({
		scrollContainer: function($table) {
			return $('#tblAssess').closest('.wrapper');
		}
	});
	$("li[class*=boxes] div[class*=ui-icon-gripsmall-diagonal-se]").css("display", "none");
	$("li[class*=boxes] div[class*=ui-resizable-e]").css("display", "none");
	darkHeaders($(this));
	resizeImp();
});
$('#assess_tbl_show_case_report').click(function() {
	$('table#tblAssess').floatThead({
		scrollContainer: function($table) {
			return $('#tblAssess').closest('.wrapper');
		}
	});
	$('table#tblAssess').floatThead('reflow');
});
$('#assess_tbl_show_case_details').click(function() {
	$('table#tblAssess').floatThead({
		scrollContainer: function($table) {
			return $('#tblAssess').closest('.wrapper');
		}
	});
	
	if($("table[id^=tblAssess] th[style*='border-left-width: 2px;'], td[style*='border-left-width: 2px;']")){
			$("table[id^=tblAssess] th[style*='border-left-width: 2px;'], td[style*='border-left-width: 2px;']").css("border-left-width", "1px");
			
		}
	if($("table[id^=tblAssess] th[style*='repeat']")) {
			$("table[id^=tblAssess] th[style*='repeat']").css({
			"background": "#e6e6e6 url('/producteditor/css/smoothness/images/ui-bg_glass_75_e6e6e6_1x400.png') 50% 50%",
			"background-repeat": "repeat-x"
		});}
		
	$('table#tblAssess').floatThead('reflow');
	resizeImpDown();
});
/*
$("#tblAssess").mouseover(function(){
				var status = "no ok"; 
				var statusinterval = setInterval( function(){
				if($("#tblAssess td").length > 1){
					status = "ok";
				}
				if(status == "ok"){clearInterval(statusinterval); 
					$('table#tblAssess').floatThead('reflow');
					status = "finish"
				}
				},700);
				if(status == "finish"){
					resizeImpDown();
				}
			
	
});
*/
$('#research_assess_update').click(function() {
	darkHeaders($(this));
});
$('.ui-dialog-titlebar-close').click(function() {
	if($("div[id=assess_tbl_show_case] a[class=active_link]")){darkHeaders($(this));}
	$('table#tblAssess').floatThead('reflow');
	resizeImpDown();
});
$( ".CRG" )
  .mouseup(function() {
   console.log("up");
   $('table#tblAssess').floatThead('reflow');
  })
  .mousedown(function() {
    console.log("down");
	$('table#tblAssess').floatThead('reflow');
  });
	
	
	$('*[id*=mytext]:visible').each(function() {
    $(this).doStuff();
	});
  $('#generate_url').toggle(function() {
	   var batch_set = $('.result_batch_items:checked').val() || 'me';
       var first = $("select[name='" + batch_sets[batch_set]['batch_batch'] + "']").find('option:selected').val();
      var second =  $(batch_sets[batch_set]['batch_compare']).val();
       var batch_name= $('select[name="' + batch_sets[batch_set]['batch_batch'] + '"]').find('option:selected').text();
       var generate_url_check= $('#generate_url_check').is(':checked')?1:0;
       var generate_url_Summary= $('#generate_url_Summary').is(':checked')?1:0;
       if(second == undefined){
           second = 0;
       }
      

        var columns_check = $('#research_assess_choiceColumnDialog').find('input[type=checkbox]:checked');
        var columns_checked = [];
        $.each(columns_check, function(index, value) {
            columns_checked.push($(value).data('col_name'));
        });

       var base = base_url+ "index.php/assess/research_url?";
       var url = "batch_id_result="+first +"&cmp_selected="+second+"&checked_columns_results="+columns_checked+"&generate_url_check="+generate_url_check+"&batch_name="+batch_name+"&generate_url_Summary="+generate_url_Summary;

        $.post(base_url + 'index.php/assess/assess_save_urls', {'url': url}, function(data) {
            $('#generate_url_link').val(base+data);
            $('#generate_url').text('Delete Link');

        });

   },(function(){
       $('#generate_url_link').val('');
       $('#generate_url').text('Share Link');
       
   })
    );    
});