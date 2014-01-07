/*
 * All GLOBAL variables are placed in initdata.js
 */

function close_popover(elem)
{
	var element = $(elem);
		
	element.closest('.popover').prev().popover('hide');
	
	return false;
}
function topScroll(){
	$( "#tableScrollWrapper.red" ).remove();
	$( "#tableScrollWrapper" ).clone().insertBefore( "#tableScrollWrapper" ).addClass("red");
	$( "#tableScrollWrapper:not(.red)" ).addClass("xw");
	//$( "#tableScrollWrapper.red td" ).css("display", "none");
	$( "div#tableScrollWrapper.red" ).css("height", "16px").css("width", "101.6%");
	$(function(){
    $(".red").scroll(function(){
        $(".xw:not(.red)").scrollLeft($(".red").scrollLeft());
		});
	$(".xw:not(.red)").scroll(function(){
        $(".red").scrollLeft($(".xw:not(.red)").scrollLeft());
		});
		//console.log("topScroll");
		
	});
	$("#tblAssess").floatThead('reflow');
}
function resizeImpDown(status){
	
	var status = status || true	
	  , onResize = function(event) {			
		tblAssessTable.floatThead({
			scrollContainer: function($table){
				return $table.closest('.wrapper');
			}
		});
		topScroll();				
	};
	
	var tblAssessTable = $("#tblAssess");
	tblAssessTable.colResizable({ disable : true });	
	status && tblAssessTable.colResizable({
		liveDrag:true, 
		gripInnerHtml:"<div class='grip'></div>", 
		draggingClass:"dragging",
		onResize : onResize
	});	
	
	onResize(null);
}

$(function() {
	
	$.expr[':'].contains = function(a, i, m) {
	  return $(a).text().toUpperCase()
		  .indexOf(m[3].toUpperCase()) >= 0;
	};
	
	$( '#research_assess_update' ).ajaxStart(function() {
		$( this ).text( "Updating..." ).attr('disabled', 'disabled');
	});
	
	$( '#research_assess_update' ).ajaxStop(function() {
		$( this ).text( "Update" ).removeAttr('disabled');
	});
	
    $.ajax({
            url: getbatchesvalue,
            dataType: 'json',
            type: 'POST'
        }).done(function(data){
           last_batch_id  = data.batch_id;
           last_compare_batch_id = data.compare_batch_id;
                     
			$('select[name="research_assess_batches"]').val(last_batch_id).change();				
			$('select[id="research_assess_compare_batches_batch"]').val(last_compare_batch_id).change();
			 			                              
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

//    var textToCopy;

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
	
	// show or hide graphs blocks
	function toggleGraphBlocks(isDisplayed)
	{
		if (isDisplayed)
		{
			$("#assess_graph_dropdown").show();
			$("#assess_graph").show();
		} else {
			$("#assess_graph_dropdown").hide();
			$("#assess_graph").hide();
		}
	}
	
	// show or hide results blocks
	function toggleResultsBlocks(isDisplayed)
	{
		if (isDisplayed)
		{
			$('#tblAssess_info').show();
			$('#tblAssess_paginate').show();
			$(".tblDataTable").show();
			$("#tblAssess_wrapper .CRC").show();
			$("#tblAssess_info").parent().show();
		} else {
			$('#tblAssess_info').hide();
			$('#tblAssess_paginate').hide();
			$(".tblDataTable").hide();
			$("#tblAssess_wrapper .CRC").hide();
			$("#tblAssess_info").parent().hide();
		}
	}
	
	function setBorderSeparator()
	{
		$("#tblAssess th[class*=1]:not(th[class*=_1]):first").css('border-left', '2px solid #ccc');					
		$("#tblAssess tr").each(function() {
			var elem = $(this);						
			elem.find("td[class*=1]:not(td[class*=_1]):first").css('border-left', '2px solid #ccc');								
		});	
	}
	
	// Use this variable to define "togglers" for each tab
	var tabsRelatedBlocks = {
		details_compare : function(isDisplayed) {			
			//code here...
			toggleDetailsCompareBlocks(isDisplayed);
			toggleResultsBlocks(isDisplayed);
			toggleGraphBlocks( ! isDisplayed);
		},
		view : function(isDisplayed) {			
			//code here...
			toggleDetailsCompareBlocks(isDisplayed);
			toggleResultsBlocks( ! isDisplayed);
			toggleGraphBlocks( ! isDisplayed);
		},
		details_compare_result : function(isDisplayed) {			
			//code here...
			toggleDetailsCompareBlocks(isDisplayed);
			toggleResultsBlocks( ! isDisplayed);
			toggleGraphBlocks( ! isDisplayed);
		},
		graph : function(isDisplayed) {			
			//code here...
			toggleDetailsCompareBlocks(isDisplayed);
			toggleResultsBlocks( ! isDisplayed);
			toggleGraphBlocks(isDisplayed);
		},
	};
	
	$('.summary_edit_btn').on('click', function() {
		var elem = $(this);
		if (!elem.hasClass('active'))
		{
			$(elem).text('Done');
			$(elem).blur();
			$('.icon_question_wrapper').css('vertical-align', 'bottom');
			$('.selectable_summary_handle, .selectable_summary_handle_with_competitor').css({'visibility' : 'visible'});
		}
		else 
		{
			$(elem).text('Edit');
			$(elem).blur();
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
	}).find( ".item_line:not(.batch1_filter_item):not(.batch2_filter_item)" )   
		.addClass( "ui-corner-all" )
        .prepend( "<div class='selectable_summary_handle'><i class='icon-move'></i></div>" );			
	
	$(document).on('click', '.research_arrow_assess_tbl_res', function(e) {
		if($("#tblAssess").is(":visible")) {
			$(".table_scroll_wrapper").hide();
		} else {
			$(".table_scroll_wrapper").show();
		}
	});
		
	function readAssessData() {
		var research_batch = $('.research_assess_batches_select')
		  , research_batch_competitor = $('#research_assess_compare_batches_batch')
          , storage_key = research_batch.val() + '_' + (parseInt(research_batch_competitor.val() ? research_batch_competitor.val() : 0) + 0)				  
		  , json_data = customLocalStorage[storage_key] ? JSON.parse(customLocalStorage[storage_key]) : null;	
		  
		$('.assess_report_download_panel').hide();
        $("#tblAssess tbody tr").remove();
		
		if (!json_data)
		{																
			var aoData = buildTableParams([]);	
				
			$.getJSON(readAssessUrl, aoData, function(json) {
				if(!json)
					return;	
																			
				customLocalStorage[storage_key] = JSON.stringify(json);		
									
				tblAssess = reInitializeTblAssess(json);				
			});       							
		}
		else									
			tblAssess = reInitializeTblAssess(json_data); 					
    }	
	
	function reInitializeTblAssess(json_data) {
		
		return $('#tblAssess').dataTable(_.extend({
			bDestroy : true,
			bJQeuryUI : true,				
			bJUI : true,				
			sPaginationType : 'full_numbers',
			aaSorting : [[5, "desc"]],
			bAutoWidth : false,
			bProcessing : true,
			bDeferRender : true,								
			aLengthMenu : [ 5, 10, 25, 50, 100 ],								
			fnInitComplete : function(oSettings, json) {
				console.log('local init complete');	
				hideColumns(); 									
				setBorderSeparator();					
				loadSetTK();
																			 
				resizeImpDown();										
			},
			fnRowCallback : function(nRow, aData, iDisplayIndex) {					
				$(nRow).attr("add_data", tblAssess.fnSettings().json_encoded_data[iDisplayIndex]); 	
				tblAssess_postRenderProcessing(nRow);					
			},
			fnDrawCallback : function(oSettings) {
				console.log('local draw callback');					
				tblAssess.fnAdjustColumnSizing(false);				
			},
			fnPreDrawCallback : function( oSettings ) {										
				buildReport(json_data);
				
				//setting main tblAssess instance
				tblAssess = oSettings.oInstance;
				tblAllColumns = tblAssess.fnGetAllSColumnNames();
				
				if (json_data.ExtraData)
				{
					oSettings.json_encoded_data = json_data.ExtraData.json_encoded_data ? json_data.ExtraData.json_encoded_data : '';					
					oSettings.display_competitor_columns = json_data.ExtraData.display_competitor_columns;					
					oSettings.getSelectableColumns = json_data.ExtraData.getSelectableColumns;					
				}
			},
			oLanguage : {
				sInfo : "Showing _START_ to _END_ of _TOTAL_ records",
				sInfoEmpty : "Showing 0 to 0 of 0 records",
				sInfoFiltered : "",
				sSearch : "Filter:",
				sLengthMenu : "_MENU_ rows"
			},
			aoColumns : json_data.aoColumns
		}, json_data));	
	}	

	// setting global static variables	
	$.fn.dataTable.defaults.bJQueryUI = true;	
	
    
    // tblAssess = $('#tblAssess').dataTable({
		// aoColumns : columns,
		// bDestroy : true,
		// bAutoWidth : false,
		// fnInitComplete : function( oSettings,json ) {										
			
			// displayInitColumns(oSettings);					
		// },
	// });

	
	// tblAllColumns = tblAssess.fnGetAllSColumnNames();
	
	// function displayInitColumns(oSettings)
	// {		
		
		// var columns_checkboxes = $('#research_assess_choiceColumnDialog').find('input[type=checkbox]:checked');
		// var columns_checkboxes_checked = []
		  // , localTblAssess = oSettings.oInstance;
		  
        // $.each(columns_checkboxes, function(index, value) {
            // columns_checkboxes_checked.push($(value).data('col_name'));
        // });		
		// $.each(oSettings.oInstance.fnGetAllSColumnNames(), function(index, value) {
				
			// value = value.replace(/[0-9]$/, '');				
			// if (oSettings.aoColumns[index])
			// {										
				// if ($.inArray(value, tableCase.details_compare) > -1 && $.inArray(value, columns_checkboxes_checked) > -1) {						
					// localTblAssess.fnSetColumnVis(index, true, false);
				// } else {
					// localTblAssess.fnSetColumnVis(index, false, false);						
				// }
			// }
		// }); 
	// }
	
	$('.get_board_view_snap').on('click', function() {
		var batch_set = $('.result_batch_items:checked').val() || 'me';		
		var compare_batch_id = $(batch_sets[batch_set]['batch_compare']).find('option:selected').val() ;
		$.ajax({
			type: "POST",
			url: readBoardSnapUrl,
			data: {
					batch_id: $('select[name="' + batch_sets[batch_set]['batch_batch'] + '"]').find('option:selected').val(),
					compare_batch_id: $(batch_sets[batch_set]['batch_compare']).find('option:selected').val()
			},
			success : function(data){
				if(!data.length) return false;
				
				console.log('1');
									  
				var str = '';
				var showcount = 12;
				if(compare_batch_id != '0' && compare_batch_id !='all'){
					showcount = 6 ;
				}
				for(var i=0; i<data.length; i++)
				{
//                            
					if(i < showcount)
					{

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
					else {
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
				$('#assess_view .assess_view_content').html(str);
				$('#assess_view .board_item img').on('click', function(){
					var info = $(this).parent().find('div.prod_description').html();
					showSnap('<img src="'+$(this).attr('src')+'" style="float:left; max-width: 495px; margin-right: 10px"><div style="float:right; width:315px">'+info+'</div>');
				});
				
			}
		});
	});

function highChart(graphBuild) {
	
	// Castro #1119: disable charts dropdown and show over time checkbox and empty chart container
	$('#graphDropDown').attr("disabled", true);
	$('#show_over_time').attr("disabled", true);
	$('#highChartContainer').empty().addClass("loading");
	
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
            batch_compare_id: batch2Value,
            graphBuild: graphBuild
        }
    }).done(function(data){					
        var value1 = [];
        var value2 = [];
        var valueName = [];
        valueName[0] = [];
        valueName[1] = [];
        var valueDate = [];
        valueDate[0] = [];
        valueDate[1] = [];
        var valueUrl = [];
        valueUrl[0] = [];
        valueUrl[1] = [];
        var graphName1 = '';
        var graphName2 = '';
        var cloneToolTip = null;
        var cloneToolTip2 = null;
        var updated_Features = [];
        updated_Features[0] = [];
        updated_Features[1] = [];
        var updated_long_description_wc = [];
        updated_long_description_wc[0] = [];
        updated_long_description_wc[1] = [];
        var updated_revision = [];
        updated_revision[0] = [];
        updated_revision[1] = [];
        var updated_short_description_wc = [];
        updated_short_description_wc[0] = [];
        updated_short_description_wc[1] = [];
        var updated_total_description_wc = [];
        updated_total_description_wc[0] = [];
        updated_total_description_wc[1] = [];
        var updated_h1_word_counts = [];
        updated_h1_word_counts[0] = [];
        updated_h1_word_counts[1] = [];
        var updated_h2_word_counts = [];
        updated_h2_word_counts[0] = [];
        updated_h2_word_counts[1] = [];
        var oldest_values =[];
        oldest_values[0] =[];
        oldest_values[1] =[];
        if(data.length) {
    
            /***First Batch - Begin***/
            if(data[0] && data[0].product_name.length > 0){
                valueName[0] = data[0].product_name;
            }
            if(data[0] && data[0].Date.length > 0){
                valueDate[0] = data[0].Date;
            }
            if(data[0] && data[0].updated_Features.length > 0){
                updated_Features[0] = data[0].updated_Features;
            }
            if(data[0] && data[0].updated_long_description_wc.length > 0){
                updated_long_description_wc[0] = data[0].updated_long_description_wc;
            }
            if(data[0] && data[0].updated_revision.length > 0){
                updated_revision[0] = data[0].updated_revision;
            }
            if(data[0] && data[0].updated_short_description_wc.length > 0){
                updated_short_description_wc[0] = data[0].updated_short_description_wc;
            }
            if(data[0] && data[0].updated_total_description_wc.length > 0){
                updated_total_description_wc[0] = data[0].updated_total_description_wc;
            }
            if(data[0] && data[0].updated_h1_word_counts.length > 0){
                updated_h1_word_counts[0] = data[0].updated_h1_word_counts;
            }
            if(data[0] && data[0].updated_h2_word_counts.length > 0){
                updated_h2_word_counts[0] = data[0].updated_h2_word_counts;
            }
            if(data[0] && data[0].url.length > 0){
                valueUrl[0] = data[0].url;
            }
            /***First Batch - End***/
            /***Second Batch - Begin***/
            if(data[1] && data[1].product_name.length > 0){
                valueName[1] = data[1].product_name;
            }
             if(data[1] && data[1].Date.length > 0){
                valueDate[1] = data[1].Date;
            }
             if(data[1] && data[1].updated_Features.length > 0){
                updated_Features[1] = data[1].updated_Features;
            }
             if(data[1] && data[1].updated_long_description_wc.length > 0){
                updated_long_description_wc[1] = data[1].updated_long_description_wc;
            }
             if(data[1] && data[1].updated_revision.length > 0){
                updated_revision[1] = data[1].updated_revision;
            }
             if(data[1] && data[1].updated_short_description_wc.length > 0){
                updated_short_description_wc[1] = data[1].updated_short_description_wc;
            }
             if(data[1] && data[1].updated_total_description_wc.length > 0){
                updated_total_description_wc[1] = data[1].updated_total_description_wc;
            }
            if(data[1] && data[1].updated_h1_word_counts.length > 0){
                updated_h1_word_counts[1] = data[1].updated_h1_word_counts;
            }
            if(data[1] && data[1].updated_h2_word_counts.length > 0){
                updated_h2_word_counts[1] = data[1].updated_h2_word_counts;
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
                    oldest_values[0] = updated_short_description_wc[0];
                    oldest_values[1] = updated_short_description_wc[1];
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
                    oldest_values[0] = updated_long_description_wc[0];
                    oldest_values[1] = updated_long_description_wc[1];
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
                    oldest_values[0] = updated_total_description_wc[0];
                    oldest_values[1] = updated_total_description_wc[1];
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
                    oldest_values[0] = updated_revision[0];
                    oldest_values[1] = updated_revision[1];
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
                    oldest_values[0] = updated_Features[0];
                    oldest_values[1] = updated_Features[1];
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
                    graphName2 = 'characters';
                    oldest_values[0] = updated_h1_word_counts[0];
                    oldest_values[1] = updated_h1_word_counts[1];
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
                    graphName2 = 'charactes';
                    oldest_values[0] = updated_h2_word_counts[0];
                    oldest_values[1] = updated_h2_word_counts[1];
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
        
        // Castro #1119: if checkbox is checked add lines of trendlines
        if($("#show_over_time").is(":checked"))
		{
			var series_index = seriesObj.length;

			var trendlines_data = data[0].updated_trendlines_data;
			var trendline_series = new Array([], [], [], [], [], []);
			var total_trendlines = 6;
			var trendline_colors = ['#555555', '#666666', '#777777', '#888888', '#999999', '#AAAAAA'];

			for(i = 0; i < trendlines_data.length; i++)
			{
				for(j = 0; j < total_trendlines; j++)
				{
					trendline_series[j][i] = trendlines_data[i][j];
				}
			}

			for(j = 0; j < total_trendlines; j++)
			{
				seriesObj[series_index + j] = {
					name: batch1Name,
					data: trendline_series[j],
					color: trendline_colors[j]
				}
			}
		}

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
                    $.each(this.points, function(i, datum) 
					{
						// Castro #1119: add line to tooltip only when show overtime is not checked
                        if(i > 0  && ! $("#show_over_time").is(":checked"))
						{
							result += '<hr style="border-top: 1px solid #2f7ed8;margin:0;" />';
						}
						
                        if(datum.series.color == '#2f7ed8')
						{
                            j = 0;
						}
                        else
						{
                            j = 1;
						}
						
						// Castro #1119: add data to tooltip only when show overtime is not checked or is the first point
						if((i > 0 && ! $("#show_over_time").is(":checked")) || i == 0)
						{
							result += '<b style="color: '+datum.series.color+';" >' + datum.series.name + '</b>';
							result += '<br /><span>' + valueName[j][datum.x] + '</span>';
							result += '<br /><a href="'+valueUrl[j][datum.x]+'" target="_blank" style="color: blue;" >' + valueUrl[j][datum.x] + '</a>';
							result += '<br /><span ">'+graphName1+' ' + valueDate[j][datum.x] + ' - ' + datum.y + ' '+graphName2+'</span>';
							result += '<span style="color: grey;display:'+display_property+';" class="update_class">'+oldest_values[j][datum.x]+'</span>';
						}
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
		
		// Castro #1119: enable drodown and checkbox again remove loading image
		$('#graphDropDown').removeAttr("disabled");
		$('#show_over_time').removeAttr("disabled");
		$("#highChartContainer").removeClass("loading");
		
        $('.highcharts-button').each(function(i){
            if(i > 0)
                $(this).remove();
        });
    });
    
}
	$('#graphDropDown').live('change',function(){
		showHighChart();
	});
	
	$('#show_over_time').live('click',function(){
		showHighChart();
	});

	// Castro #1119: function called by two events, show_over_time click and graphDropDown change
	function showHighChart()
	{
		var graphDropDownValue = $('#graphDropDown').children('option:selected').val();
		if(graphDropDownValue != "") // Castro #1119: create chart when a valid option is selected
		{
			highChart(graphDropDownValue);
		}
	}
	
    $(document).scroll(function() {
		var batch_set = $('.result_batch_items:checked').val() || 'me';		
		if($('#assess_view .assess_view_content').children('div')) {
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
							// o_O !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! WTF?!
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
    
    $('#assess_tbl_show_case a').on('click', function(event) {
        // if ($(this).text() == 'Results' || $(this).text() == 'Compare') {
            // $('#research_batches_columns').show();
        // } else {
            // $('#research_batches_columns').hide();
        // }
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
      
            hideColumns();                   
        }
    }

    function tblAssess_postRenderProcessing(tr) {
       		
		var jTr = $(tr)
		  , row_height = jTr.height();
		
		if (row_height > 5) {
			jTr.find('table.url_table').height('auto');
		}       
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
		
		fillReportSummary(report.summary, batch_sets[batch_set]['batch_items_prefix']);				                                     
    }   	   	
		
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
		}
	}
	
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
     // === disable / change some buttons (start) (I.L.)
     $("#assessDetailsDialog_btnSave").css('visibility', 'hidden');
     // === disable / change some buttons (end) (I.L.)
     var table_case = $('#assess_tbl_show_case a[class=active_link]').data('case');
      var checked_columns_results = GetURLParameter('checked_columns_results');
    
     // ==== figure out position of clicked 'tr'(start)
     var click_object = $(event.target).parent();
     if(click_object[0].localName == 'tr') { // <tr>
        var click_object = $(event.target).parent();
        var click_object_index = click_object[0]._DT_RowIndex;
     } else { // <td>
        var click_object = $(event.target).parent().parent();
        var click_object_index = click_object[0]._DT_RowIndex;
     }
     console.log("CLICKED TR INDEX: ", click_object_index);
     var click_object_real_index = 0;
     if(click_object_index == 0) {
        click_object_real_index = 1;
     } else {
        click_object_real_index = click_object_index + 1;
     }
     console.log("REAL CLICKED TR INDEX: ", click_object_real_index);
     if(click_object_real_index == 1) {
        $("#assessDetailsDialog_btnPrev").attr('disabled', true);
     } else if(click_object_real_index == 9) {
        $("#assessDetailsDialog_btnNext").attr('disabled', true);
     }
     // ==== figure out position of clicked 'tr'(end)

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
        $('#impdataid').attr('val',add_data.imported_data_id);
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
        $('#impdataid').attr('val',add_data.imported_data_id);
        $('#assessDetails_ProductName').val(add_data.product_name);
        $('#assessDetails_Model').val(add_data.model);
        $('#assessDetails_url').val(add_data.url);
        $('#assess_open_url_btn').attr('href', add_data.url);
        // $('#assessDetails_Price').val(add_data.own_price);
        $('#assessDetails_Price').val( Number(add_data.own_price).toFixed(2) );

        $('#assessDetails_ProductName1').val(add_data.product_name1);
        $('#assessDetails_Model1').val(add_data.model1);
        $('#assessDetails_url1').val(url_compare);
        $('#assess_open_url_btn1').attr('href', url_compare);
        // $('#assessDetails_Price1').val(add_data.competitors_prices[0]); // old stuff
        // ==== new stuff (I.L) (start)
        if(typeof(url_compare) !== 'undefined' && $.trim(url_compare) !== "") {
            console.log('start altering right side price field : OLD (DEFAULT) PRICE : ', Number(add_data.competitors_prices[0]).toFixed(2));
            var send_data = {
                url: url_compare
            };
            $.post(base_url + 'index.php/assess/get_crawler_price_by_url', send_data, function(d) {
                console.log(d.data);
                if(typeof(d.data) !== 'undefined' && d.data !== null) {
                    $('#assessDetails_Price1').val( Number(d.data.price).toFixed(2) );
                } else {
                    $('#assessDetails_Price1').val( Number(add_data.competitors_prices[0]).toFixed(2) );
                }
            });
        } else {
            console.log('RIGHT SIDE URL NOT SPECIFIED');
            $('#assessDetails_Price1').val( Number(add_data.competitors_prices[0]).toFixed(2) );
        }
        // ==== new stuff (I.L) (end)
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
        if(typeof(add_data.title_seo_phrases1) !== 'undefined' && add_data.title_seo_phrases1 !== null && add_data.title_seo_phrases1 !== "None") $("#assessDetails_SEO1_div").html(add_data.title_seo_phrases1);
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
        if(typeof(add_data.title_seo_phrases) !== 'undefined' && add_data.title_seo_phrases !== null && add_data.title_seo_phrases !== "None") $("#assessDetails_SEO_div").html(add_data.title_seo_phrases);
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
                   // ==== restore prev / next buttons to init state (start)
                   $("#assessDetailsDialog_btnPrev, #assessDetailsDialog_btnNext").removeAttr('disabled');
                   // ==== restore prev / next buttons to init state (end)
                   // ==== figure prev / next buttons availability states (start)
                   if(click_object_real_index == 1) {
                       $("#assessDetailsDialog_btnPrev").attr('disabled', true);
                   } else if(click_object_real_index == 9) {
                       $("#assessDetailsDialog_btnNext").attr('disabled', true);
                   }
                   // ==== figure prev / next buttons availability states (end)
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
            // 'Close': {
            //     text: 'Cancel',
            //     click: function() {
            //         $(this).dialog('close');
            //     }
            // },
            'Close': {
                text: 'Close',
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
            'Not a match': {
                text: 'Not a match',
                id: 'assessDetailsDialog_btnNotAMatch',
                style: 'margin-right:125px',
                click: function() {
                    var impdata_id = $('#impdataid').attr('val');
                    $.ajax({
                        url: base_url + 'index.php/assess/deleteSecondaryMatch',
                        dataType: 'json',
                        type: 'post',
                        data: {
                            impdataid: impdata_id
                }
                    }).done(function(){
                        $('#assessDetailsDialog').dialog('close');                        
                        
                    });
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
                         url: $('input#assessDetails_url').val(),
                         url_right: $('input#assessDetails_url1').val()
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
//    $('#assessDetailsDialog input[type="text"], textarea').bind({
//        focus: function() {
//            this.select();
//            textToCopy = this.value;
//        },
//        mouseup: function() {
//            textToCopy = this.value;
//            return false;
//        }
//    });

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

//    function copyToClipboard(text) {
//        window.prompt("Copy to clipboard: Ctrl+C, Enter (or Esc)", text);
//    }

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
        });
        var own_customer = $(this).val();
        fill_lists_batches_compare(own_customer, 0);        
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
        });
        var own_customer = $(this).val();
        fill_lists_batches_compare(own_customer, 1);        
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
			
		}
	});

    $('#research_assess_compare_batches_reset').click(function() {
		$('#research_assess_compare_batches_customer').val('select customer').prop('selected', true);
        $('#research_assess_compare_batches_batch').val('select batch').prop('selected', true);

		$('#research_assess_compare_batches_customer_competitor').val('select customer').prop('selected', true);
        $('#research_assess_compare_batches_batch_competitor').val('select batch').prop('selected', true);
        
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
                $('#assess_view .assess_view_content').html(str);
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
                $('#assess_view .assess_view_content').html(str);
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
       						
		readAssessData();							
        
    });

  
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

    $(".research_assess_choiceColumnDialog_checkbox").change(function(){
        		
		var columns_checkboxes = {};
		var settings = tblAssess.fnSettings();
		for (var it in settings.getSelectableColumns)
			columns_checkboxes[settings.getSelectableColumns[it]['sName']] = $('#column_' + settings.getSelectableColumns[it]['sName']).is(':checked');
		
		$.ajax({
			url: base_url + 'index.php/assess/assess_save_columns_state',
			dataType: 'json',
			type: 'post',
			data: {
				value: columns_checkboxes
			},
			success: function(data) {
				if (data == true) {
					hideColumns();										
					resizeImpDown();
					
					// bad hack, need to be rewrited, Nikita, please check
					$('#tblAssess thead th').css('width', '100%');
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

	$('#summary_filters_configuration_wrapper, #custom_batch_create_modal').dialog({
		autoOpen : false,
		resizable: false,
		modal : true,
		width : 'auto'
	});

	$('.show_filters_configuration_popup').on('click', function() {
		$('#summary_filters_configuration_wrapper').dialog('open');
	});

    $(".custom-batch-trigger").on("click", function(e) {
        e.preventDefault();
        getCustomerDropdown();
        $.post(base_url + 'index.php/batches/index', {}, function(data) {
            $("#custom_batch_create_modal").html(data).dialog("open");
        });
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
        width: 'auto'
    });
   $('#research_assess_choiceColumnDialog_export').dialog({
        autoOpen: false,
        resizable: false,
        modal: true,      
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

    function hideColumns() {
		var tableSettings = tblAssess.fnSettings();	
		console.log(tableSettings);
		var batch_set = $('.result_batch_items:checked').val() || 'me';                
		var table_case = $('#assess_tbl_show_case a[class=active_link]').data('case') || 'details_compare';				       
		
		//turn off related blocks here
		toggleRelatedBlocks('details_compare', false);
		
        if (table_case == 'recommendations') {
			
			/**
			 * using one place to turn on/off different blocks
			 */
			toggleRelatedBlocks('recommendations', true);
			
            reportPanel(false);
            $.each(tblAllColumns, function(index, value) {
                if ($.inArray(value, tableCase.recommendations) > -1) {
                    tblAssess.fnSetColumnVis(index, true, false);
                }
                else {
                    tblAssess.fnSetColumnVis(index, false, false);
                }
            });                       
		} 
        else if (table_case == 'details_compare') {							
			/**
			 * using one place to turn on/off different blocks
			 */
			toggleRelatedBlocks('details_compare', true);
            
			reportPanel(false);
			
			var columns_checkboxes = $('#research_assess_choiceColumnDialog').find('input[type=checkbox]:checked');
			var columns_checkboxes_checked = [];
			$.each(columns_checkboxes, function(index, value) {
				columns_checkboxes_checked.push($(value).data('col_name'));
			});
			
            $.each(tblAllColumns, function(index, value) {
				
                value = value.replace(/[0-9]$/, '');	
				
				if (tableSettings.aoColumns[index])
				{							
					if ($.inArray(value, columns_checkboxes_checked) > -1) {
							
						if (tableSettings.display_competitor_columns)
							tblAssess.fnSetColumnVis(index, true);
						else if (!tableSettings.display_competitor_columns && !tableSettings.aoColumns[index]['batch_number'])
							tblAssess.fnSetColumnVis(index, true);
						else
							tblAssess.fnSetColumnVis(index, false);		
							
					} else {											
						tblAssess.fnSetColumnVis(index, false);						
					}
				}
            }); 
			
        } else if (table_case == 'view') {
		
            toggleRelatedBlocks('view', true);
			
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
			
            $('.board_view').hide();
            $('.tblDataTable').hide(); // Castro #1119: change #tblAssess selector with .tblDataTable to avoid that table assess bar appears over graph dropdown
            //$('#tblAssess').parent().find('div.ui-corner-bl').hide();
            $('.assess_report').hide();
            $('#assess_view').hide();
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
		console.log(visible);
		var tblAssess = $('#tblAssess');
        if (visible) {
            tblAssess.hide();
			$('.tblDataTable').hide(); // Castro #1119: table assess header fix
            tblAssess.parent().find('div.ui-corner-bl').hide();
            $('.assess_report').show();
        } else {
            tblAssess.show();
			$('.tblDataTable').show(); // Castro #1119: table assess header fix
			tblAssess.parent().find('div.ui-corner-bl').show();
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
    function collectionParams() {
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
            assessRequestParams.short_less_check = $('#research_assess_short_less_check').is(':checked') + 0;
            assessRequestParams.short_less = $('#research_assess_short_less').val();
            assessRequestParams.short_more_check = $('#research_assess_short_more_check').is(':checked') + 0;
            assessRequestParams.short_more = $('#research_assess_short_more').val();

            if ($('#research_assess_short_seo_phrases').is(':checked')) {
                assessRequestParams.short_seo_phrases = 1;
            }
            if ($('#research_assess_short_duplicate_content').is(':checked')) {
                assessRequestParams.short_duplicate_content = 1;
            }
        }

        if ($('#research_assess_long_check').is(':checked')) {
            assessRequestParams.long_less_check = $('#research_assess_long_less_check').is(':checked') + 0;
            assessRequestParams.long_less = $('#research_assess_long_less').val();
            assessRequestParams.long_more_check = $('#research_assess_long_more_check').is(':checked') + 0;
            assessRequestParams.long_more = $('#research_assess_long_more').val();

            if ($('#research_assess_long_seo_phrases').is(':checked')) {
                assessRequestParams.long_seo_phrases = 1;
            }
            if ($('#research_assess_long_duplicate_content').is(':checked')) {
                assessRequestParams.long_duplicate_content = 1;
            }
        }

        var research_assess_compare_batches_batch = $(batch_sets[batch_set]['batch_compare']).val();
        if (research_assess_compare_batches_batch > 0) {
            assessRequestParams.compare_batch_id = research_assess_compare_batches_batch;
        }
		
		assessRequestParams.summaryFilterData = summaryInfoSelectedElements.join(',');
		assessRequestParams.sort_columns = 5;
		assessRequestParams.sort_dir = 'desc';
		assessRequestParams.sSearch = '';
		assessRequestParams.bRegex = false;
		assessRequestParams.iDisplayLength = 10;
		assessRequestParams.iDisplayStart = 0;
				
        return assessRequestParams;
    }


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
        var columns_check = $('#research_assess_choiceColumnDialog_export').find('input[type=checkbox]:checked');
            var columns_checked = [];
            $.each(columns_check, function(index, value) {
				if($(value).attr('id') == "column_title_seo_phrases_f" && $("#tk-frequency").is(':checked') ){
					columns_checked.push("title_seo_phrases_f");
				}
				else{
				columns_checked.push($(value).data('col_name'));
				}
                
            });
            console.log(columns_checked);
            
           var summaryFilterData = summaryInfoSelectedElements.join(',')
          
            
        $(this).text('Exporting...');
        var main_path=  $(this).prop('href');
        $(this).attr('href', $(this).prop('href')+'?batch_id='+batch_id+'&cmp_selected='+cmp_selected+'&checked_columns='+columns_checked+'&batch_name='+batch_name+'&summaryFilterData='+summaryFilterData);
	
        $.fileDownload($(this).prop('href'))
                .done(function() {
            $('#research_assess_export').removeAttr('disabled');
            $('#research_assess_export').attr('href', main_path);
            $('#research_assess_export').text('Export');
        })
                .fail(function() {
        });
        
    });

	function wrapResultsTable() {
		$( "div[id^=tblAssess_length], div[id^=assess_tbl_show_case], div[class^=dataTables_filter], div[id^=tblAssess_processing]" ).wrapAll( "<div class='fg-toolbar ui-toolbar ui-widget-header ui-corner-tl ui-corner-tr ui-helper-clearfix'></div>" );
		$( "#tblAssess_info, #tblAssess_paginate" ).wrapAll( "<div class='fg-toolbar ui-toolbar ui-widget-header ui-corner-bl ui-corner-br ui-helper-clearfix'></div>" );
	}	

  
	  $('#tk-frequency').click(function() {
	    var $target = $('input#column_title_seo_phrases');
		newData = "column_title_seo_phrases_f";
		
		$target.removeAttr('id').attr({ 'id': newData });
		$target.removeAttr('name').attr({ 'name': newData });
		$target.removeAttr('data-col_name').attr({ 'data-col_name': 'title_seo_phrases_f' });
		$target.click();
		$target.click();
		});
		$('#tk-denisty').click(function() {
		var $target = $('input#column_title_seo_phrases_f');
		newData = "column_title_seo_phrases";
		$target.removeAttr('id').attr({ 'id': newData });
		$target.removeAttr('name').attr({ 'name': newData });
		$target.removeAttr('data-col_name').attr({ 'data-col_name': 'title_seo_phrases' });
		$target.click();
		$target.click();
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
		
	$('.assess_report_download_panel').hide();
});