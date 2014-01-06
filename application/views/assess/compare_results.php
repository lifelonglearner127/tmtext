<link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/smoothness/jquery-ui-1.8.2.custom.css" />
<link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/styles.css" />
          
<!--    <ul class="nav nav-tabs jq-measure-tabs">
        <li class="active"><a data-toggle="tab" href="<?php echo site_url('assess/products');?>">Products</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_departments');?>">Categories</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('assess');?>">Home Pages</a></li>
        <li class='pull_right_navlink'><a href="javascript:void(0);" onclick="viewCustomBatches()">Custom Batch</a></li>
    </ul>-->
<div class="title_result" style="padding-bottom: 10px;">
    
</div>
  
<ul class="research_table_filter">
    <li class="boxes hideBox">
        <h3>
            <span class=''>
                Batch:
                <select name="research_assess_customers" class="mt_10">
                    <?php foreach($customer_list as $customer):?>
                        <option value="<?php echo strtolower($customer); ?>"><?php echo $customer; ?></option>
                    <?php endforeach;?>
                </select>
                <select name="research_assess_batches" class="research_assess_batches_select mt_10 mr_10 ml_20" style="width: 175px;">
                    <?php foreach($batches_list as $ks => $vs):?>
                        <option value="<?php echo $ks; ?>"><?php echo $vs; ?></option>
                    <?php endforeach;?>
                </select>
            </span>
            <!--<label class="research_assess_flagged"><input type="checkbox" id="research_assess_flagged" > Only show flagged items</label>-->
            <div class="clear"></div>
            <a href="#" onclick="return false;" class="hideShow float_r">
                <img src="<?php echo base_url();?>img/arrow.png" />
            </a>
        </h3>
        <div class="boxes_content">
            <div class="row-fluid">
                <div class="span4">
                    Text:
                    <input id="assess_filter_text" type="text" id="assess_filter_text" class="mt_10 w_100"/>
                </div>
                <div class="span5">
                    Date Range:
                    <input id="assess_filter_datefrom" type="text" class="mt_10" value="" style="width: 85px;"/>
                    &nbsp-&nbsp
                    <input id="assess_filter_dateto" type="text" class="mt_10" value="" style="width: 85px;"/>
                    <button id="assess_filter_clear_dates" class="btn">Clear</button>
                </div>
                <div class="assess_filter_options">
                    <label class="checkbox">
                        <input id="research_assess_select_all" type="checkbox">
                        Select All
                    </label>
                    <label class="checkbox">
                        <input id="research_assess_price_diff" type="checkbox" unchecked>
                        Priced Higher
                    </label>
                </div>
            </div>
            <div class="row-fluid assess_filter_options">
                <div id="research_assess_filter_short_descriptions_panel" class="span12">
                    <div class="span3" style="height: 50px;">
                        <label class="checkbox">
                            <input id="research_assess_short_check" type="checkbox" checked>
                            <span id="research_assess_filter_short_descriptions_label">Short Descriptions:</span>
                        </label>
                    </div>
                    <div id="research_assess_short_params">
                        <div class="span4">
                            <input id="research_assess_short_less_check" type="checkbox">
                            &#60;
                            <input id="research_assess_short_less" type="text" value="20"/>
                            words
                            &nbsp &nbsp &nbsp
                            <input id="research_assess_short_more_check" type="checkbox">
                            &#62;
                            <input id="research_assess_short_more" type="text" value="50"/>
                            words
                        </div>
                        <div class="span5" style="height: 50px;">
                            <label class="checkbox">
                                <input id="research_assess_short_seo_phrases" type="checkbox" checked>
                                SEO Phrases
                            </label>
                            <label class="checkbox">
                                <input id="research_assess_short_duplicate_content" type="checkbox" checked>
                                Duplicate content
                            </label>
                        </div>
                    </div>
                </div>
            </div>
            <div class="row-fluid assess_filter_options">
                <div id="research_assess_filter_long_descriptions_panel" class="span12">
                    <div class="span3" style="height: 50px;">
                        <label class="checkbox">
                            <input type="checkbox" id="research_assess_long_check" checked>
                            <span id="research_assess_filter_long_descriptions_label">Long Descriptions:</span>
                        </label>
                    </div>
                    <div id="research_assess_long_params">
                        <div class="span4">
                            <input id="research_assess_long_less_check" type="checkbox">
                            &#60;
                            <input id="research_assess_long_less" type="text" value="100"/>
                            words
                            &nbsp &nbsp &nbsp
                            <input id="research_assess_long_more_check" type="checkbox">
                            &#62;
                            <input id="research_assess_long_more" type="text" value="200"/>
                            words
                        </div>
                        <div class="span5">
                            <label class="checkbox">
                                <input id="research_assess_long_seo_phrases" type="checkbox" checked>
                                SEO Phrases
                            </label>
                            <label class="checkbox">
                                <input id="research_assess_long_duplicate_content" type="checkbox" checked>
                                Duplicate content
                            </label>
                        </div>
                    </div>
                </div>
            </div>
           
                <div style="float: left;">
                    Compare with:
                    <select id="research_assess_compare_batches_customer"></select>
                    <select id="research_assess_compare_batches_batch"></select>
                </div>
                <div style="float: left;" class="ml_5">
                    <button id="research_assess_compare_batches_reset" class="btn">Reset</button>
                </div>
                <div style="float: right;">
                    <button id="research_assess_update" class="btn btn-success">Update</button>
                    <a href="<?php echo base_url();?>index.php/assess/export_assess" class="fileDownloadPromise btn" id="research_assess_export" >Export...</a>
                </div>
            <div style="clear:both;"></div>
            <div style="float: left;margin-top: 10px;" class="generate_url">
                <button id="generate_url">Generate URL</button>
                <input id="generate_url_link" style="margin-bottom:0;" type="text" >
                 <input type="checkbox" id="generate_url_check">
            </div>
        </div>
    </li>
</ul>

        <div class="modal hide fade ci_hp_modals crawl_launch_panel" id='recipients_control_panel_modal'></div>
        <div class="modal hide fade ci_hp_modals" style='top: 20%' id='dep_rep_preview_list_modal'></div>

<!-- choise column dialog box -->
<div id="research_assess_choiceColumnDialog" title="Select Table Columns" style="height: 172px !important; width: 320px !important;">
    <div>
        <form action="" method="post">

            <div id="columns_checking">
            <ul>
                <?php foreach(AssessHelper::getSelectableColumns(AssessHelper::columns()) as $column): ?>
						<li>
							<p>
								<!-- $columns must be rewrited!!! -->
								<input type="checkbox" class="research_assess_choiceColumnDialog_checkbox" id="column_<?php echo $column['sName']?>" data-col_name="<?php echo $column['sName']?>" name="column_<?php echo $column['sName']?>_name" <?php echo(isset($columns[$column['sName']]) && $columns[$column['sName']] == 'true' ? 'checked="checked"' : '') ?> />
								<label for="column_<?php echo $column['sName']?>"><?php echo $column['sTitle']?></label>
								
								<?php if (isset($column['moreHtml'])): ?>
									<?php echo $column['moreHtml'] ?>
								<?php endif ?>								
							</p>
						</li>
					<?php endforeach ?>
                
            </ul>
            </div>
            
            
        </form>
    </div>
</div>

<div id="assessDetailsDialog" title="Details">
    <form name="access_details">
    <div style="float:left;"  class="details_left">
    <p>
        <label for="assessDetails_ProductName">Product Name:</label>
        <input type="text" id="assessDetails_ProductName" />
    </p>
    <p>
        <label for="assessDetails_Model">Model:</label>
        <input type="text" id="assessDetails_Model" />
    </p>
    <p>
        <label for="assessDetails_url">URL:</label>
        <input type="text" id="assessDetails_url" />
        <a id="assess_open_url_btn" class="icon-hand-right" target="_blank"></a>
    </p>

    <p>
        <label for="assessDetails_Price">Price:</label>
        <input type="text" id="assessDetails_Price" />
    </p>

    <div id="assessDetails_short_and_long_description_panel">
        <div class="parag">
            <span class="labeler">
                <label for="assessDetails_ShortDescription">Short Description:</label>
            </span>
            <textarea id="assessDetails_ShortDescription" ></textarea>
            <div class="bottom-labeler">
                <label><span id="assessDetails_ShortDescriptionWC">0</span> words</label>
            </div>
        </div>

        <p>
            <label for="assessDetails_ShortSEO">Short SEO:</label>
            <input type="text" id="assessDetails_ShortSEO"/>
        </p>

        <div class="parag">
            <span class="labeler">
                <label for="assessDetails_LongDescription">Long Description:</label>
            </span>
            <textarea id="assessDetails_LongDescription"></textarea>
            <div class="bottom-labeler">
                <label><span id="assessDetails_LongDescriptionWC">0</span> words</label>
            </div>
        </div>

        <p>
            <label for="assessDetails_LongSEO">Long SEO:</label>
            <input type="text" id="assessDetails_LongSEO"/>
        </p>
    </div>
    <div id="assessDetails_description_panel">
        <div class="parag">
            <span class="labeler">
                <label for="assessDetails_Description">Description:</label>
            </span>
            <textarea id="assessDetails_Description"></textarea>
            <div class="bottom-labeler">
                <label><span id="assessDetails_DescriptionWC">0</span> words</label>
            </div>
        </div>

        <p>
            <label for="assessDetails_SEO">SEO:</label>
            <input type="text" id="assessDetails_SEO" />
        </p>
    </div>
    
    </div>  
    <div style="float:right;" class="details_right">
    
    <p>
        <label for="assessDetails_ProductName1">Product Name:</label>
        <input type="text" id="assessDetails_ProductName1" />
    </p>
    <p>
        <label for="assessDetails_Model1">Model:</label>
        <input type="text" id="assessDetails_Model1" />
    </p>
    <p>
        <label for="assessDetails_url1">URL:</label>
        <input type="text" id="assessDetails_url1" />
        <a id="assess_open_url_btn1" class="icon-hand-right" target="_blank"></a>
    </p>

    <p>
        <label for="assessDetails_Price1">Price:</label>
        <input type="text" id="assessDetails_Price1" />
    </p>

    <div id="assessDetails_short_and_long_description_panel1">
        <div class="parag">
            <span class="labeler">
                <label for="assessDetails_ShortDescription1">Short Description:</label>
            </span>
            <textarea id="assessDetails_ShortDescription1" ></textarea>
            <div class="bottom-labeler">
                <label><span id="assessDetails_ShortDescriptionWC1">0</span> words</label>
            </div>
        </div>

        <p>
            <label for="assessDetails_ShortSEO1">Short SEO:</label>
            <input type="text" id="assessDetails_ShortSEO1"/>
        </p>

        <div class="parag">
            <span class="labeler">
                <label for="assessDetails_LongDescription1">Long Description:</label>
            </span>
            <textarea id="assessDetails_LongDescription1"></textarea>
            <div class="bottom-labeler">
                <label><span id="assessDetails_LongDescriptionWC1">0</span> words</label>
            </div>
        </div>

        <p>
            <label for="assessDetails_LongSEO1">Long SEO:</label>
            <input type="text" id="assessDetails_LongSEO1"/>
        </p>
    </div>
    <div id="assessDetails_description_panel1">
        <div class="parag">
            <span class="labeler">
                <label for="assessDetails_Description1">Description:</label>
            </span>
            <textarea id="assessDetails_Description1"></textarea>
            <div class="bottom-labeler">
                <label><span id="assessDetails_DescriptionWC1">0</span> words</label>
            </div>
        </div>

        <p>
            <label for="assessDetails_SEO1">SEO:</label>
            <input type="text" id="assessDetails_SEO1" />
        </p>
    </div>
    <?php if ($this->ion_auth->is_admin($this->ion_auth->get_user_id())) { ?>
        <style type="text/css">
            #assessDetailsDialog_btnReCrawl{
                display: block!important;
            }
        </style>
    <?php } ?>
</div>
    </form>
</div>

<div id="assess_report_options_dialog" title="Report Options" >
    <form id="assess_report_options_form">
        <table style="width:100%;">
            <tr>
                <td>Layout:</td>
                <td>
                    <select id="assess_report_page_layout" name="assess_report_page_layout" style="width: 100%;" class="mt_5">
                        <option value="L">Landscape</option>
                        <option value="P">Portrait</option>
                    </select>
                </td>
            </tr>
            <tr>
                <td style="vertical-align: top;">Competitors:<span style="color: red;"><sup>*</sup></span></td>
                <td>
                    <select id="assess_report_competitors" name="assess_report_competitors" style="width: 100%;height: 250px;" multiple="">
                    </select>
                </td>
            </tr>
            <tr>
                <td></td>
                <td>
                    <span style="color: red;"><sup>*</sup></span><span style="font-size: 9px;">To select more than one item, press and hold down the Ctrl or Shift keys, and then click each item that you want to select.<span>
                </td>
            </tr>
        </table>
    </form>
</div>

<div class="modal hide fade ci_hp_modals" id='assess_preview_crawl_snap_modal'>
    <div class="modal-body" style='overflow: hidden'>
        <div class='snap_holder'>&nbsp;</div>
    </div>
    <div class="modal-footer">
        <a href="javascript:void(0)" class="btn" data-dismiss="modal">Close</a>
    </div>
</div>
<?php 
	$this->load->view('assess/_summary', array(
		'display' => 'none',
		'wrapper_class' => 'assess_report_compare',
		'user_filters' => $user_filters,
		'user_filters_order' => $user_filters_order,
		'direct_access' => true
	)) 
?>

<div class="row-fluid">	
    <div id="read" class="ui-tabs-panel ui-widget-content ui-corner-bottom">		
        <div id="records_wrapper" class="dataTables_wrapper block_data_table">			
            <div class="span12" id="dt_tbl">	
					<div id="assess_tbl_show_case" class="assess_tbl_show_case">                    
						<a id="assess_tbl_show_case_details_compare" data-case="details_compare" title="Details_compare" class="active_link" href="#compare">Results</a> |
						<a id="assess_tbl_show_case_graph" data-case="graph" title="Graph" href="#graph">Charts</a> |
						<a id="assess_tbl_show_case_view" data-case="view" title="Board View" href="#board_view">Board View</a> |
						<a id="assess_tbl_show_case_recommendations" data-case="recommendations" title="Recommendations" href="#recommendations">Recommendations</a>
					</div>
					<a class='research_arrow research_arrow_assess_tbl_res' onclick='return false;'><img src='<?php echo base_url() ?>img/arrow.png'></a>
                    <table id="tblAssess" class="tblDataTable" >
                        <thead>
                        </thead>
                        <tbody></tbody>
                    </table>
                <div id="comare_table"></div>
                <div id="assess_tbl_show_case" class="assess_tbl_show_case">
<!--                    <a id="assess_tbl_show_case_recommendations" data-case="recommendations" title="Recommendations" href="#recommendations"  class="active_link">Recommendations</a> |
                    <a id="assess_tbl_show_case_report" data-case="report" title="Report" href="#summary">Summary</a> |
                    <a id="assess_tbl_show_case_details" data-case="details" title="Details" href="#details">Details</a> |-->
                    <a id="assess_tbl_show_case_details_compare" data-case="details_compare_result" title="Details_compare" class="active_link">Content Analytics Report</a> |
                    <a id="assess_tbl_show_case_graph" data-case="graph" title="Graph">Graph</a> 
                    <!--<a id="assess_tbl_show_case_view" data-case="view" title="Board View" href="#board_view">Board View</a>-->
                </div>
                <!-- <a id="research_batches_columns" class="ml_5 float_r" title="Customize..."><img  style="width:32px; heihgt: 32px;"src ="<?php echo base_url() ?>/img/settings@2x.png"></a>  -->
                <a id="research_batches_columns" class="ml_5 float_r" title="Customize..."><img  style="width:32px; heihgt: 32px;"src ="<?php echo base_url() ?>/img/gear_32_32.png"></a>           
                <div id="assess_view">
					<button class="btn btn-success get_board_view_snap">Get board view snap</button>
					<div class="assess_view_content"></div>
                    <p>No images available for this batch</p>
                </div>
                <img id="imgLoader" style="display: none;margin-top: -16px;margin-left: 81px;" src="<?php echo base_url();?>img/img-loader.gif" />
                <div id="assess_graph">
                    <div id="highChartContainer" style="min-width: 878px; height: 300px; margin: 0 auto"></div>
                </div>
                             
                <script type="text/javascript" src="<?php echo base_url();?>js/jquery.json-2.4.min.js"></script>
                <script type="text/javascript" src="<?php echo base_url();?>js/jquery.fileDownload.js"></script>               
               
                <script type="text/javascript" src="<?php echo base_url(); ?>js/measure_department.js"></script>
                <script type='text/javascript' src="<?php echo base_url();?>js/ci_home_pages.js"></script>
            </div>
        </div>
    </div>
</div>

<div class="modal hide fade ci_hp_modals" id='preview_crawl_snap_modal'>
    <div class="modal-body" style='overflow: hidden'>
        <div class='snap_holder'>&nbsp;</div>
    </div>
    <div class="modal-footer">
        <a href="" class="left_snap"> < </a>
        <a href="" class="right_snap"> > </a>
        <a href="javascript:void(0)" class="btn" data-dismiss="modal">Close</a>
    </div>
</div>
  
<style>
    .span_img{
        overflow:hidden;
        display:block;
        height:60px;
    }
    .span_img:hover{
        height:auto;
    }
    .span_img:before {
        content: "...";
        float: right;
        position: relative;
        top: 42px;
    }
.span_img:hover.span_img:before{
        content: " ";
}
#tblAssess tr th{
    font-weight: bold;
    font-size: 13px;
}
#tblAssess tr td:first-child {
    text-align: center;
}.keyword_short,.Custom_Keywords_Description_Class{
    padding: 0 !important;
}
.table_keywords_short td,.table_keywords_long td{

 border: 0px solid #fff !important;
}
.comp_res{
    visibility: hidden;
}
.comp_res_none{
    display: none;
}
.solution-logo-page{
    margin-left: 0 !important;
}
.h3_title{
    float: left;
    margin-left: 70px;
    margin-top: 0;
}
.research_batches_columns_res{
    display: block !important;
}

</style>
<script>
            $(function() {
                $('#columns_checking ul').sortable();
                $('#assess_tbl_show_case').addClass('comp_res');
                $('.jq-measure-tabs').addClass('comp_res');
                $('.pull-right').addClass('comp_res');
                $('.pull-left').addClass('comp_res');
                $('.research_table_filter, .research_table_filter_competitor').addClass('comp_res');
                $('#assess_report').addClass('comp_res_none');
                $('head').find('title').text('Content Analytics Report');
                function GetURLParameter(sParam) {
                    $('.ui-dialog-titlebar-close').html('<span style="margin-top:-5px;">x</span>');
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
                
                 var batch_id_result = GetURLParameter('batch_id_result');
                 var batch_name = GetURLParameter('batch_name');
                 var generate_url_check = GetURLParameter('generate_url_check');
                 var generate_url_Summary = GetURLParameter('generate_url_Summary');
                  batch_name = batch_name.replace(/%20/g,' ')
                  $('.title_result').html("<div class='logo'><img  style='width:220px; height: 50px;float:left;'src ='<?php echo base_url() ?>/img/content-analytics_page.png'></div><h3 class='h3_title'>"+batch_name+" Batch</h3>");
                
               
                    $('#research_batches_columns').addClass('research_batches_columns_res');
                      
                    var columns_checked_arr = GetURLParameter('checked_columns_results');
                    if(columns_checked_arr){
                         var checked_columns_results_split = columns_checked_arr.split(',')
                    }
                    var columns_checked = checked_columns_results_split;
                     
                    var a = $('#research_assess_choiceColumnDialog').find('input[type=checkbox]');

                       $.each(columns_checked, function(index, value) {
                           
                           var col_name = $(value).selector;
                         
                            $.each(a, function(index, value) {
                            if($(value).data('col_name') == col_name)
                            {

                                $(value).attr("checked","checked")
                            }
                            });
                       });
                    

                    
                var cmp_selected = GetURLParameter('cmp_selected');
                    $('select[name="research_assess_batches"]').val(batch_id_result).change()
                setTimeout(function(){
                    
                $('select[id="research_assess_compare_batches_batch"]').val(cmp_selected).change()
                 $('#research_assess_update').click();
//                 alert($('#edit_summary').text())
                },2000)
		if(generate_url_Summary == "1"){
                    
                 $('#tblAssess_wrapper').addClass('comp_res_none');
                 }else{
                     
                 $('#div_export').html('<a href="<?php echo base_url();?>index.php/assess/export_assess" class="fileDownloadPromise btn" id="research_assess_export" >Export...</a>');
                 }		
				var scrollScore = 0; 
				$(window).scroll(function(){ if(scrollScore < 10 && $( "table[id^=tblAsses] th" ).length > 0){
				scrollScore++;
				if($("table[id^=tblAssess]")){
					if($("table[id^=tblAssess] th[style*='repeat']")) {
						$("table[id^=tblAssess] th[style*='repeat']").css({
						"background": "#e6e6e6 url('/producteditor/css/smoothness/images/ui-bg_glass_75_e6e6e6_1x400.png') 50% 50%",
						"background-repeat": "repeat-x"
					})
					}
					if($("table[id^=tblAssess] th[style*='border-left-width: 2px;'], td[style*='border-left-width: 2px;']")){
						$("table[id^=tblAssess] th[style*='border-left-width: 2px;'], td[style*='border-left-width: 2px;']").css("border-left-width", "1px");
					}
					
					var count = $("table[id^=tblAsses] th:visible").length;
					var headers =  Math.round((count / 2) - 1);
					$("table[id^=tblAsses] th:visible:gt(" + headers + "):not(th[aria-label*='Gap']):not(th[aria-label*='Duplicate'])").css({
						"background": "url('/producteditor/css/smoothness/images/ui-bg_glass_75_dadada_1x400.png') 50% 50%",
						"background-repeat": "repeat-x"
					});
					$("table[id^=tblAsses] th:visible:gt(" + headers + "):first").css("border-left", "2px solid #ccc");
					$("table[id^=tblAsses] tr").each(function()
					{
						$(this).find("td:gt(" + headers + "):first").css("border-left", "2px solid #ccc");
					});
				}
				} if(scrollScore == 9){
				$('table#tblAssess').floatThead('reflow');
				
				}});
				
            /*
			
			var reflow = $(function(){$(window).scroll(function(){
				var aTop = $('#tblAssess_length').height();
				if($(this).scrollTop()>=aTop){
				   $('table#tblAssess').floatThead('reflow');
				}}  );});
			setTimeout(reflow, 5000);*/
            });
 </script>

