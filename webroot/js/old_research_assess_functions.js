 function createTableByServerSide() {
		var batch_set = $('.result_batch_items:checked').val() || 'me';		
        $('#tblAssess_wrapper').remove();
        var th = '';
        for(var i =0;i<Object.keys(columns);i++){
            th += '<th with = "100px"></th>';
        }
        var newTable = '<table id="tblAssess" class="tblDataTable"><thead>'+th+'</thead><tbody></tbody></table>';
        
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
                   
                    tblAssess.fnProcessingIndicator(false);
                                    
                    if (json.iTotalRecords == 0) {
                        $('.assess_report_compare_panel').hide();
                        $('.assess_report_numeric_difference').hide();
                        if ($('select[name="' + batch_sets[batch_set]['batch_batch'] + '"]').find('option:selected').val() != "") {
                            $('#summary_message').html(" - Processing data. Check back soon.");                         
                            $('.assess_report_items_1_descriptions_pnl').hide();
                            $('.assess_report_items_2_descriptions_pnl').hide();                           
                        }                                                                     
                    }                   
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
            },
            "fnDrawCallback": function(oSettings) {
				console.log(487);
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
    }
	
	    function createTable() {
        var oSettings = $("#tblAssess").dataTable().fnSettings();
        var aoDataa = buildTableParams(oSettings.aoData);
        var newObject = jQuery.extend(true, {}, aoDataa);
        var batch_set = $('.result_batch_items:checked').val() || 'me';				
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
                    },
                    "fnDrawCallback": function(oSettings) {
						console.log(608);
                        tblAssess_postRenderProcessing();
                        if (zeroTableDraw) {
                            zeroTableDraw = false;
                            return;
                        }         				
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
               
				tblAssess.fnProcessingIndicator(false);
                              
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
                // $('.dataTables_filter').append('<a id="research_batches_columns" class="ml_5 float_r" title="Customize..." style="display: none;"><img style="width:32px; heihgt: 32px;" src="http://tmeditor.dev//img/settings@2x.png"></a>');
                // $('#research_batches_columns').on('click', function() {
                    // $('#research_assess_choiceColumnDialog').dialog('open');
                    // $('#research_assess_choiceColumnDialog').parent().find('button:first-child').addClass("popupGreen");
                // });
                // $('#assess_tbl_show_case a').on('click', function(event) {
                    // event.preventDefault();
                    // if ($(this).text() == 'Details' || $(this).text() == 'Compare') {
                        // $('#research_batches_columns').show();
                    // } else {
                        // $('#research_batches_columns').hide();
                    // }
                    // assess_tbl_show_case(this);
                // });
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
             }
        });       
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
	
	//don't need createTable and createTableByServerSide
	$('#research_assess_update').on('click', function() {
        if(first_click)
		{			
			if ($("#research_assess_compare_batches_batch").val() == 'all') {
				console.log(1);
				createTable();
				serevr_side = false;
				return;
			} else {
				if (!serevr_side) {
					console.log(21);				
					createTableByServerSide();
					tblAllColumns = tblAssess.fnGetAllSColumnNames();
					serevr_side = true;
				} else {
					console.log(22);
					serevr_side = true;
					readAssessData();
				}
			}
			
			check_word_columns();
        }
    });
	
	
	// need to be rewrited on the backend
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
		console.log(tblAllColumns);
        $.each(tblAllColumns, function(index, value) {
			
			console.log('Begin...');
			console.log(index);
			console.log(value);
			console.log('End');
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
		
		var subtitle_vars = [
			{
				'Long_Description' : Long_Description,
				'Short_Description' : Short_Description,
			},
			{
				'Long_Description' : Long_Description1,
				'Short_Description' : Short_Description1,
			},
			{
				'Long_Description' : Long_Description2,
				'Short_Description' : Short_Description2,
			},
			{
				'Long_Description' : Long_Description3,
				'Short_Description' : Short_Description3,
			},
			{
				'Long_Description' : Long_Description4,
				'Short_Description' : Short_Description4,
			},
		];
		for (var it = 0; it < 4; it++)
		{
			var number = it || '';
								
			if(!subtitle_vars[it]['Long_Description'] && subtitle_vars[it]['Short_Description']){
				$('.subtitle_desc_short' + number).text('Product ')
			}else if(!subtitle_vars[it]['Short_Description'] && subtitle_vars[it]['Long_Description']){
				$('.subtitle_desc_long' + number).text('Product ')
			}else{
				$('.subtitle_desc_long' + number).text('Long ')
				$('.subtitle_desc_short' + number).text('Short ')
			}
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