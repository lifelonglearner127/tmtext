<link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/smoothness/jquery-ui-1.8.2.custom.css" />

    <ul id="report_product_menu" class="nav nav-tabs jq-measure-tabs">
        <li id="product_menu_part" class="active"><a data-toggle="tab" href="<?php echo site_url('assess/products');?>">Products</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_departments');?>">Categories</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('assess');?>">Home Pages</a></li>
        <li class='pull_right_navlink'><a href="#" class="custom-batch-trigger">Custom Batch</a></li>
    </ul>

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
			<span class="batch_set_depend_options">
				<input type="radio" name="result_batch_items[]" class="result_batch_items" value="me" /> - Show Results
			</span>
            <div style="float: right; margin-top: 4px; margin-right: 30px;">
                <button id="research_assess_update" class="btn btn-success">Update</button>
                <a href="<?php echo base_url();?>index.php/assess/export_assess" class="fileDownloadPromise btn" id="research_assess_export" >Export...</a>
				<a href="#" class="show_filters_configuration_popup2" id="research_batches_columns_export">
					<!-- <img style="width:32px; heihgt: 32px;" src="<?php echo base_url();?>img/settings@2x.png"> -->
                    <img style="width:32px; heihgt: 32px;" src="<?php echo base_url();?>img/gear_32_32.png">
				</a>
            </div>
<!--            <label class="research_assess_flagged"><input type="checkbox" id="research_assess_flagged" > Only show flagged items</label>-->
            <div class="clear"></div>
            <a href="#" onclick="return false;" class="hideShow float_r">
                <img src="<?php echo base_url();?>img/arrow.png" />
            </a>
        </h3>
        <div class="boxes_content">
			<div style="display: none">
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
									<input id="research_assess_title_seo_phrases" type="checkbox" checked>
									Title Keywords
								</label>
								<label class="checkbox">
									<input id="research_assess_images_cmp" type="checkbox" checked>
									Images
								</label>
								<label class="checkbox">
									<input id="research_assess_title_pa" type="checkbox" checked>
									Title
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
			</div>
                <div id="_unmatches"><a href="<?php echo base_url();?>index.php/assess/export_unmatches" class="fileDownloadPromise btn" id="export_unmatches" >Unmatched...</a></div>
                <div style="float: left;">
                    Compare with:
                    <select id="research_assess_compare_batches_customer"></select>
                    <select id="research_assess_compare_batches_batch"></select>

                </div>
                <div style="float: left;" class="ml_5">
                    <button id="research_assess_compare_batches_reset" class="btn">Reset</button>
                </div>
                <div style="float: left; padding-top: 5px; margin-left: 10px;">
                    <input type="checkbox" id="batch_set_toggle" name="batch_set_toggle" /><span style="float: right; padding-left: 10px;">Compare with second set of batches</span>
                </div>

            <div style="clear:both;"></div>
            <div style="float: left;margin-top: 10px;" class="generate_url">
                <button id="generate_url">Share Link</button>
                <input id="generate_url_link" style="margin-bottom:0;" type="text" >
                <input type="checkbox" style="margin: 10px;" id="generate_url_check" checked="checked">Make results columns configurable
                <input type="checkbox" style="margin: 10px;" id="generate_url_Summary">Only share summary data
            </div>
        </div>
    </li>
</ul>

<ul class="research_table_filter_competitor" style="display: none">
    <li class="boxes hideBox">
        <h3>			
            <span class=''>
                Batch:
                <select name="research_assess_customers_competitor" class="mt_10">
                    <?php foreach($customer_list as $customer):?>
                        <option value="<?php echo strtolower($customer); ?>"><?php echo $customer; ?></option>
                    <?php endforeach;?>
                </select>
                <select name="research_assess_batches_competitor" class="mt_10 mr_10 ml_20" style="width: 175px;">
                    <?php foreach($batches_list as $ks => $vs):?>
                        <option value="<?php echo $ks; ?>"><?php echo $vs; ?></option>
                    <?php endforeach;?>
                </select>
            </span>   
			<span class="batch_set_depend_options">
				<input type="radio" name="result_batch_items[]" class="result_batch_items" value="competitor" /> - Show Results
			</span>
            <a href="#" onclick="return false;" class="hideShow float_r">
                <img src="<?php echo base_url();?>img/arrow.png" />
            </a>
        </h3>
        <div class="boxes_content">                       
                     
			<div style="float: left;">
				Compare with:
				<select id="research_assess_compare_batches_customer_competitor"></select>
				<select id="research_assess_compare_batches_batch_competitor"></select>
			</div>
					                   
        </div>
    </li>
</ul>

<div class="modal hide fade ci_hp_modals crawl_launch_panel" id='recipients_control_panel_modal'></div>
<div class="modal hide fade ci_hp_modals" style='top: 20%' id='dep_rep_preview_list_modal'></div>
<div id='custom_batch_create_modal' title="Custom Batch"></div>

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

<!-- column export dialog -->
<div id="research_assess_choiceColumnDialog_export" title="Select Table Columns for Export" style="height: 172px !important; width: 320px !important;">
    <div>
            <div id="columns_checking">
            <ul>
                <li>
                    <p>
                        <input type="checkbox" class="research_assess_choiceColumnDialog_checkbox" id="column_price" data-col_name="price" name="column_price" />
                        <label for="column_price">Price</label>
                    </p>
                </li>
                <li><p>
                    <input type="checkbox" class="research_assess_choiceColumnDialog_checkbox" id="column_snap" data-col_name="snap" name="column_snap_name" />
                    <label for="column_snap">Snapshot</label>
                </p></li><li>
                <p>
                    <input type="checkbox" class="research_assess_choiceColumnDialog_checkbox" id="column_created" data-col_name="created" name="column_created_name"  />
                    <label for="column_editor">Date</label>
                </p></li><li>
                <p>
                    <input type="checkbox" class="research_assess_choiceColumnDialog_checkbox" id="imp_data_id" data-col_name="imp_data_id" name="imp_data_id"  />
                    <label for="imp_data_id">Imported Data ID</label>
                </p></li><li>
                <p>
                    <input type="checkbox" class="research_assess_choiceColumnDialog_checkbox" id="column_product_name" data-col_name="product_name" name="column_product_name_name"  />
                    <label for="column_product_name">Product name</label>
                </p></li><li>
                <p>
                    <input type="checkbox" class="research_assess_choiceColumnDialog_checkbox" id="model" data-col_name="model" name="model"  />
                    <label for="model">Model</label>
                </p></li><li>
                <p>
                    <input type="checkbox" class="research_assess_choiceColumnDialog_checkbox" id="column_url" data-col_name="url" name="column_url_name"  checked="checked" />
                    <label for="column_url">Url</label>
                </p></li><li>
                <p>
                    <input type="checkbox" class="research_assess_choiceColumnDialog_checkbox" id="Page_Load_Time" data-col_name="Page_Load_Time" name="Page_Load_Time"  />
                    <label for="Page_Load_Time">Page Load Time</label>
                </p></li><li>
                <p>
                    <input type="checkbox" class="research_assess_choiceColumnDialog_checkbox" id="Short_Description" data-col_name="Short_Description" name="Short_Description" />
                    <label for="Short_Description">Short Description</label>
                </p></li><li>
                <p>
                    <input type="checkbox" class="research_assess_choiceColumnDialog_checkbox" id="column_short_description_wc" data-col_name="short_description_wc" name="column_short_description_wc_name"  />
                    <label for="column_short_description_wc">Short Description - # Words</label>
                </p></li><li>
                <p>
                    <input type="checkbox" class="research_assess_choiceColumnDialog_checkbox" id="Meta_Keywords" data-col_name="Meta_Keywords" name="Meta_Keywords"  />
                    <label for="Meta_Keywords">Meta Keywords</label>
                </p></li><li>
                <p>
                    <input type="checkbox" class="research_assess_choiceColumnDialog_checkbox" id="column_title_seo_phrases" data-col_name="title_seo_phrases" name="column_title_seo_phrases_name"  />
                    <label for="column_title_seo_phrases">Title Keywords</label>
                    <input id="tk-denisty" type="radio" name="title_keywords" value="density" checked /><label for="tk-denisty">Density</label>
                    <input id="tk-frequency" type="radio" name="title_keywords" value="Frequency"/><label for="tk-frequency">Frequency</label>
                </p></li><li>
                <p>
                    <input type="checkbox" class="research_assess_choiceColumnDialog_checkbox" id="Long_Description" data-col_name="Long_Description" name="Long_Description"  />
                    <label for="Long_Description">Long Description</label>
                </p></li><li>
                <p>
                    <input type="checkbox" class="research_assess_choiceColumnDialog_checkbox" id="column_long_description_wc" data-col_name="long_description_wc" name="column_long_description_wc_name"  />
                    <label for="column_long_description_wc">Long Description - # Words</label>
                </p></li><li>
                <p>
                    <input type="checkbox" class="research_assess_choiceColumnDialog_checkbox" id="Custom_Keywords_Short_Description" data-col_name="Custom_Keywords_Short_Description" name="Custom_Keywords_Short_Description" />
                    <label for="Custom_Keywords_Short_Description">Custom Keywords - Short Description</label>
                </p></li><li>
                <p>
                    <input type="checkbox" class="research_assess_choiceColumnDialog_checkbox" id="Custom_Keywords_Long_Description" data-col_name="Custom_Keywords_Long_Description" name="Custom_Keywords_Long_Description" />
                    <label for="Custom_Keywords_Long_Description">Custom Keywords - Long Description</label>
                </p></li><li>
                <p>
                    <input type="checkbox" class="research_assess_choiceColumnDialog_checkbox" id="Meta_Description" data-col_name="Meta_Description" name="Meta_Description" />
                    <label for="Meta_Description">Meta Description</label>
                </p></li><li>
                <p>
                    <input type="checkbox" class="research_assess_choiceColumnDialog_checkbox" id="H1_Tags" data-col_name="H1_Tags" name="H1_Tags" />
                    <label for="H1_Tags">H1_Tags</label>
                </p></li><li>
                <p>
                    <input type="checkbox" class="research_assess_choiceColumnDialog_checkbox" id="H2_Tags" data-col_name="H2_Tags" name="H2_Tags"  />
                    <label for="H2_Tags">H2_Tags</label>
                </p></li><li>
                <p>
                    <input type="checkbox" class="research_assess_choiceColumnDialog_checkbox" id="column_external_content" data-col_name="column_external_content" name="column_external_content"  />
                    <label for="column_external_content">Third party content</label>
                </p></li><li>
                <p>
                    <input type="checkbox" class="research_assess_choiceColumnDialog_checkbox" id="column_reviews" data-col_name="column_reviews" name="column_reviews"  />
                    <label for="column_reviews">Reviews</label>
                </p></li><li>
                <p>
                    <input type="checkbox" class="research_assess_choiceColumnDialog_checkbox" id="average_review" data-col_name="average_review" name="average_review"  />
                    <label for="average_review">Avg Review</label>
                </p></li><li>
                <p>
                    <input type="checkbox" class="research_assess_choiceColumnDialog_checkbox" id="column_features" data-col_name="column_features" name="column_features"  />
                    <label for="column_features">Features</label>
                </p></li><li>
                <p>
                    <input type="checkbox" class="research_assess_choiceColumnDialog_checkbox" id="column_price_diff" data-col_name="price_diff" name="column_price_diff" />
                    <label for="column_actions">Price difference</label>
                </p></li><li>
                <p>
                    <input type="checkbox" class="research_assess_choiceColumnDialog_checkbox" id="gap" data-col_name="gap" name="gap"  />
                    <label for="column_actions">Gap analysis</label>
                </p></li><li>
                <p>
                    <input type="checkbox" class="research_assess_choiceColumnDialog_checkbox" id="Duplicate_Content" data-col_name="Duplicate_Content" name="Duplicate_Content"  />
                    <label for="column_actions">Duplicate Content</label>
                </p></li><li>
                <p>
                    <input type="checkbox" class="research_assess_choiceColumnDialog_checkbox" id="images_cmp" data-col_name="images_cmp" name="images_cmp"  />
                    <label for="column_actions">Images</label>
                </p></li><li>
                <p>
                    <input type="checkbox" class="research_assess_choiceColumnDialog_checkbox" id="video_count" data-col_name="video_count" name="video_count"  />
                    <label for="column_actions">Videos</label>
                </p></li><li>
                <p>
                    <input type="checkbox" class="research_assess_choiceColumnDialog_checkbox" id="title_pa" data-col_name="title_pa" name="title_pa"  />
                    <label for="column_actions">Title</label>
                </p></li>
            </ul>
            </div>
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
    
        <input type="hidden" id="impdataid" val="" />
    

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

        <!-- <p>
            <label for="assessDetails_ShortSEO">Short SEO:</label>
            <input type="text" id="assessDetails_ShortSEO"/>
        </p> -->

        <div class="parag">
            <span class="labeler">
                <label for="assessDetails_LongDescription">Long Description:</label>
            </span>
            <textarea id="assessDetails_LongDescription"></textarea>
            <div class="bottom-labeler">
                <label><span id="assessDetails_LongDescriptionWC">0</span> words</label>
            </div>
        </div>

        <!-- <p>
            <label for="assessDetails_LongSEO">Long SEO:</label>
            <input type="text" id="assessDetails_LongSEO"/>
        </p> -->
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

        <!-- <p>
            <label for="assessDetails_SEO">Keywords:</label>
            <input style='display: none;' type="text" id="assessDetails_SEO" />
        </p> -->

    </div>

    <div class='assessDetails_keys'>
        <span class="labeler" style='float: left; display: block'>
            <label>Title Keywords:</label>
        </span>
        <div class='assessDetails_SEO_wrap' id="assessDetails_SEO_div">None</div>
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

        <!-- <p>
            <label for="assessDetails_ShortSEO1">Short SEO:</label>
            <input type="text" id="assessDetails_ShortSEO1"/>
        </p> -->

        <div class="parag">
            <span class="labeler">
                <label for="assessDetails_LongDescription1">Long Description:</label>
            </span>
            <textarea id="assessDetails_LongDescription1"></textarea>
            <div class="bottom-labeler">
                <label><span id="assessDetails_LongDescriptionWC1">0</span> words</label>
            </div>
        </div>

        <!-- <p>
            <label for="assessDetails_LongSEO1">Long SEO:</label>
            <input type="text" id="assessDetails_LongSEO1"/>
        </p> -->
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
        <!-- <p>
            <label for="assessDetails_SEO1">Keywords:</label>
            <input type="text" id="assessDetails_SEO1" />
        </p> -->
    </div>

    <div class='assessDetails_keys'>
        <span class="labeler" style='float: left; display: block'>
            <label>Title Keywords:</label>
        </span>
        <div class='assessDetails_SEO_wrap' id="assessDetails_SEO1_div">None</div>
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
		'user_filters' => $user_filters,
		'user_filters_order' => $user_filters_order,
		'wrapper_class' => 'assess_report_compare',
	)) 
?>
<div class="row-fluid">	
    <div id="read" class="ui-tabs-panel ui-widget-content ui-corner-bottom">		
        <div id="records_wrapper" class="dataTables_wrapper block_data_table">			
            <div class="span12" id="dt_tbl">
				<div>
					<div class="tbl_panel_wrapper">
						<div id="assess_tbl_show_case" class="assess_tbl_show_case">                    
							<a id="assess_tbl_show_case_details_compare" data-case="details_compare" title="Details_compare" class="active_link" href="#compare">Results</a> |
							<a id="assess_tbl_show_case_graph" data-case="graph" title="Graph" href="#graph">Charts</a> |
							<a id="assess_tbl_show_case_view" data-case="view" title="Board View" href="#board_view">Board View</a> |
							<a id="assess_tbl_show_case_recommendations" data-case="recommendations" title="Recommendations" href="#recommendations">Recommendations</a>	
							
							<div class="tbl_arrows_and_gear_wrapper">
								<a id="research_batches_columns" style='display: inline' class="" title="Customize..."><img  style="width:32px; heihgt: 32px;"src ="<?php echo base_url() ?>/img/gear_32_32.png"></a>
								<a class='research_arrow research_arrow_assess_tbl_res' onclick='return false;'><img src='<?php echo base_url() ?>img/arrow.png'></a>
							</div>
						</div>
						
					</div>
                    <table id="tblAssess" class="tblDataTable" >
                        <thead>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
                <div id="comare_table"></div>
               
                <!-- <div id="assess_tbl_show_case" class="assess_tbl_show_case">
                    <a id="assess_tbl_show_case_recommendations" data-case="recommendations" title="Recommendations" href="#recommendations"  class="active_link">Recommendations</a> |
                    <a id="assess_tbl_show_case_report" data-case="report" title="Report" href="#summary">Summary</a> |
                    <a id="assess_tbl_show_case_details" data-case="details" title="Details" href="#details">Details</a> |
                    <a id="assess_tbl_show_case_details_compare" data-case="details_compare" title="Details_compare" href="#compare">Compare</a> |
                    <a id="assess_tbl_show_case_graph" data-case="graph" title="Graph" href="#graph">Graph</a> |
                    <a id="assess_tbl_show_case_view" data-case="view" title="Board View" href="#board_view">Board View</a>
                </div> -->
                <!-- <a id="research_batches_columns" style='display: inline' class="ml_5 float_r" title="Customize..."><img  style="width:32px; heihgt: 32px;"src ="<?php echo base_url() ?>/img/settings@2x.png"></a> -->
                

                <div id="assess_view">
					<button class="btn btn-success get_board_view_snap">Get board view snap</button>
					<div class="assess_view_content"></div>
                    <!--<p>No images available for this batch</p>-->
                </div>
                <img id="imgLoader" style="display: none;margin-top: -16px;margin-left: 81px;" src="<?php echo base_url();?>img/img-loader.gif" />
<!-- 			Castro #1119: convert dropdown to static -->
				<div id="assess_graph_dropdown" class="fg-toolbar ui-toolbar ui-widget-header ui-corner-bl ui-corner-br ui-helper-clearfix" style="display:none;">
					<select id="graphDropDown" style="width: 235px">
						<option value="">----Select----</option>
						<option value="total_description_wc">Total Description Word Counts</option>
						<option value="short_description_wc">Short Description Word Counts</option>
						<option value="long_description_wc">Long Description Word Counts</option>
						<option value="h1_word_counts">H1 Character Counts</option>
						<option value="h2_word_counts">H2 Character Counts</option>
						<option value="revision">Reviews</option>
						<option value="Features">Features</option>
					</select>
					<input id="show_over_time" style="width: 30px;" type="checkbox">
					<span id="show_over_time_span">Show changes over time</span>
				</div>
<!-- 			Castro #1119: convert dropdown to static end -->
                <div id="assess_graph">
                    <div id="highChartContainer" style="width: 980px; height: 370px; margin: 20 auto"></div>
                </div>
             
                <script type="text/javascript" src="<?php echo base_url();?>js/jquery.json-2.4.min.js"></script>
                <script type="text/javascript" src="<?php echo base_url();?>js/jquery.fileDownload.js"></script>
				<script type="text/javascript" src="<?php echo base_url();?>js/initdata.js"></script>
                <script type="text/javascript" src="<?php echo base_url();?>js/research_assess.js"></script>
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
</style>
<!-- <a id="research_batches_columns" style='display: inline' class="ml_5 float_r" title="Customize..."><img  style="width:32px; heihgt: 32px;"src ="<?php echo base_url() ?>/img/settings@2x.png"></a> -->
<!-- <a id="research_batches_columns" style='display: inline' class="ml_5 float_r" title="Customize..."><img  style="width:32px; heihgt: 32px;"src ="<?php echo base_url() ?>/img/gear_32_32.png"></a> -->
<script>
	
	$(function() {
			// === add expander for assess results bar (start)
			
			// === add expander for assess results bar (end)

			$('#columns_checking ul').sortable();
			$('.ui-dialog-titlebar-close').html('<span style="margin-top:-5px;">x</span>');
			$('head').find('title').text('Reports');
			// var hardcode_hash = window.location.hash;
			// if(hardcode_hash === '#login_init') {
			//     if($("#assess_tbl_show_case").length < 1) { // === I.L
			//         $('#tblAssess_length').after('<div id="assess_tbl_show_case" class="assess_tbl_show_case">' +
			//             '<a id="assess_tbl_show_case_details_compare" data-case="details_compare" title="Details_compare" class="active_link" href="#compare">Results</a>&nbsp;|&nbsp;' +
			//             '<a id="assess_tbl_show_case_graph" data-case="graph" title="Graph" href="#graph">Charts</a>&nbsp;|&nbsp;' +
			//             '<a id="assess_tbl_show_case_view" data-case="view" title="Board View" href="#board_view">Board View</a>&nbsp;|&nbsp;' +
			//             '<a id="assess_tbl_show_case_recommendations" data-case="recommendations" title="Recommendations" href="#recommendations">Recommendations</a>' +
			//             '</div>');
			//     }
			// }
	});
	          
 </script>
