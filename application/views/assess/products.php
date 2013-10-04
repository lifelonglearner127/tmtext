<link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/smoothness/jquery-ui-1.8.2.custom.css" />
<link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/styles.css" />
    <ul class="nav nav-tabs jq-measure-tabs">
        <li class=""><a data-toggle="tab" href="<?php echo site_url('assess');?>">Home Pages</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_departments');?>">Categories</a></li>
        <li class="active"><a data-toggle="tab" href="<?php echo site_url('assess/products');?>">Products</a></li>
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
                <select name="research_assess_batches" class="mt_10 mr_10 ml_20" style="width: 175px;">
                    <?php foreach($batches_list as $ks => $vs):?>
                        <option value="<?php echo $ks; ?>"><?php echo $vs; ?></option>
                    <?php endforeach;?>
                </select>
            </span>
            <label class="research_assess_flagged"><input type="checkbox" id="research_assess_flagged" checked > Only show flagged items</label>
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
                <a href="<?php echo base_url();?>index.php/research/export_assess" class="fileDownloadPromise btn" id="research_assess_export" >Export</a>
            </div>
        </div>
    </li>
</ul>


<!-- choise column dialog box -->
<div id="research_assess_choiceColumnDialog" title="Select Table Columns">
    <div>
        <form action="" method="post">
            <p>
                <input type="checkbox" id="column_snap" data-col_name="snap" name="column_snap_name" <?php echo($columns['snap'] == 'true' ? 'checked="checked"' : ''); ?> />
                <label for="column_snap">Snap</label>
            </p>
            <p>
                <input type="checkbox" id="column_created" data-col_name="created" name="column_created_name" <?php echo($columns['created'] == 'true' ? 'checked="checked"' : ''); ?> />
                <label for="column_editor">Date</label>
            </p>
            <p>
                <input type="checkbox" id="column_product_name" data-col_name="product_name" name="column_product_name_name" <?php echo($columns['product_name'] == 'true' ? 'checked="checked"' : ''); ?> />
                <label for="column_product_name">Product name</label>
            </p>
            <p>
                <input type="checkbox" id="column_url" data-col_name="url" name="column_url_name" <?php echo($columns['url'] == 'true' ? 'checked="checked"' : ''); ?> />
                <label for="column_url">Url</label>
            </p>
            <p>
                <input type="checkbox" id="column_short_description_wc" data-col_name="short_description_wc" name="column_short_description_wc_name" <?php echo($columns['short_description_wc'] == 'true' ? 'checked="checked"' : ''); ?> />
                <label for="column_short_description_wc">Words Short</label>
            </p>
            <p>
                <input type="checkbox" id="column_short_seo_phrases" data-col_name="short_seo_phrases" name="column_short_seo_phrases_name" <?php echo($columns['short_seo_phrases'] == 'true' ? 'checked="checked"' : ''); ?> />
                <label for="column_short_seo_phrases">Keywords Short</label>
            </p>
            <p>
                <input type="checkbox" id="column_long_description_wc" data-col_name="long_description_wc" name="column_long_description_wc_name" <?php echo($columns['long_description_wc'] == 'true' ? 'checked="checked"' : ''); ?> />
                <label for="column_long_description_wc">Words Long</label>
            </p>
            <p>
                <input type="checkbox" id="column_long_seo_phrases" data-col_name="long_seo_phrases" name="column_long_seo_phrases_name" <?php echo($columns['long_seo_phrases'] == 'true' ? 'checked="checked"' : ''); ?> />
                <label for="column_long_seo_phrases">Keywords Long</label>
            </p>
            <p>
                <input type="checkbox" id="column_duplicate_content" data-col_name="duplicate_content" name="column_duplicate_content_name" <?php echo($columns['duplicate_content'] == 'true' ? 'checked="checked"' : ''); ?> />
                <label for="column_batch_name">Duplicate content</label>
            </p>
            <p>
                <input type="checkbox" id="column_price_diff" data-col_name="price_diff" name="column_price_diff" <?php echo($columns['price_diff'] == 'true' ? 'checked="checked"' : ''); ?> />
                <label for="column_actions">Price difference</label>
            </p>
        </form>
    </div>
</div>

<div id="assessDetailsDialog" title="Details">
    <p>
        <label for="assessDetails_ProductName">Product Name:</label>
        <input type="text" id="assessDetails_ProductName" readonly="true" />
    </p>

    <p>
        <label for="assessDetails_url">URL:</label>
        <input type="text" id="assessDetails_url" readonly="true" />
        <a id="assess_open_url_btn" class="icon-hand-right" target="_blank"></a>
    </p>

    <p>
        <label for="assessDetails_Price">Price:</label>
        <input type="text" id="assessDetails_Price" readonly="true" />
    </p>

    <div id="assessDetails_short_and_long_description_panel">
        <div class="parag">
            <span class="labeler">
                <label for="assessDetails_ShortDescription">Short Description:</label>
            </span>
            <textarea id="assessDetails_ShortDescription" readonly="true"></textarea>
            <div class="bottom-labeler">
                <label><span id="assessDetails_ShortDescriptionWC">0</span> words</label>
            </div>
        </div>

        <p>
            <label for="assessDetails_ShortSEO">Short SEO:</label>
            <input type="text" id="assessDetails_ShortSEO" readonly="true" />
        </p>

        <div class="parag">
            <span class="labeler">
                <label for="assessDetails_LongDescription">Long Description:</label>
            </span>
            <textarea id="assessDetails_LongDescription" readonly="true"></textarea>
            <div class="bottom-labeler">
                <label><span id="assessDetails_LongDescriptionWC">0</span> words</label>
            </div>
        </div>

        <p>
            <label for="assessDetails_LongSEO">Long SEO:</label>
            <input type="text" id="assessDetails_LongSEO" readonly="true" />
        </p>
    </div>
    <div id="assessDetails_description_panel">
        <div class="parag">
            <span class="labeler">
                <label for="assessDetails_Description">Description:</label>
            </span>
            <textarea id="assessDetails_Description" readonly="true"></textarea>
            <div class="bottom-labeler">
                <label><span id="assessDetails_DescriptionWC">0</span> words</label>
            </div>
        </div>

        <p>
            <label for="assessDetails_SEO">SEO:</label>
            <input type="text" id="assessDetails_SEO" readonly="true" />
        </p>
    </div>
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

<div class="row-fluid">
    <div id="read" class="ui-tabs-panel ui-widget-content ui-corner-bottom">
        <div id="records_wrapper" class="dataTables_wrapper block_data_table">
            <div class="span12">
                <table id="tblAssess" class="tblDataTable" >
                    <thead>
                    </thead>
                    <tbody></tbody>
                </table>
                <div id="assess_tbl_show_case" class="assess_tbl_show_case">
                    <a id="assess_tbl_show_case_recommendations" data-case="recommendations" title="Recommendations" href="#" class="active_link">Recommendations</a> |
                    <a id="assess_tbl_show_case_report" data-case="report" title="Report" href="#">Summary</a> |
                    <a id="assess_tbl_show_case_details" data-case="details" title="Details" href="#">Details</a> |
                    <a id="assess_tbl_show_case_view" data-case="view" title="Board View" href="#">Board View</a>
                </div>
                <a id="research_batches_columns" class="ml_5 float_r" title="Customize..."><img  style="width:32px; heihgt: 32px;"src ="<?php echo base_url() ?>/img/settings@2x.png"></a>
                <div id="assess_report">
                    <ul class="ui-sortable">
                        <li class="boxes">
                            <h3>
                                <span>
                                    Summary
                                    <!--<span id="summary_message"></span>-->
                                </span>
                                <a class="ml_10 research_arrow hideShow" onclick="return false;" href="#">
                                    <img src="<?php echo base_url();?>img/arrow.png">
                                </a>
                                <span id="assess_report_download_panel" style="float: right;width: 500px;">
                                    Download
                                    <a id="assess_report_download_pdf" target="_blank" data-type="pdf">PDF</a> |
                                    <a id="assess_report_download_doc" target="_blank" data-type="doc">DOC</a>
                                    <button id="assess_report_options_dialog_button" class="btn" style="float: right;margin-top: 7px;" title="Report Options"><img class="other-icon" src="<?php echo base_url();?>img/ico-gear.png" /></button>
                                </span>
                            </h3>
                            <div style="clear: both;"></div>
                            <div class="boxes_content" style="padding:0px;">
                                <div class="mt_10 ml_15">
                                    <div class="mr_10"><img src="<?php echo base_url(); ?>img/assess_report_number.png"><span id="assess_report_total_items" class="mr_10"></span>total items</div>
                                </div>
                                <div class="mt_10 ml_15">
                                    <div class="mr_10"><img src="<?php echo base_url(); ?>img/assess_report_dollar.png"><span id="assess_report_items_priced_higher_than_competitors" class="mr_10"></span>items priced higher than competitors</div>
                                </div>
                                <div class="mt_10 ml_15">
                                    <div class="mr_10"><img src="<?php echo base_url(); ?>img/assess_report_D.png"><span id="assess_report_items_have_more_than_20_percent_duplicate_content" class="mr_10"></span>items have more than 20% duplicate content</div>
                                </div>
                                <div class="mt_10 ml_15">
                                    <div class="mr_10"><img src="<?php echo base_url(); ?>img/assess_report_seo.png"><span id="assess_report_items_unoptimized_product_content" class="mr_10"></span>items have non-keyword optimized product content</div>
                                </div>
                                <div id="assess_report_items_1_descriptions_pnl">
                                    <div class="mt_10 mb_10 ml_15">
                                        <div class="mr_10"><img src="<?php echo base_url(); ?>img/assess_report_arrow_down.png"><span id="assess_report_items_have_product_descriptions_that_are_too_short" class="mr_10"></span>items have descriptions that are less than <span id="assess_report_items_have_product_descriptions_that_are_less_than_value"></span> words</div>
                                    </div>
                                </div>
                                <div id="assess_report_items_2_descriptions_pnl" style="display: none;">
                                    <div id="assess_report_items_2_descriptions_pnl_s" class="mt_10 mb_10 ml_15">
                                        <div class="mr_10"><img src="<?php echo base_url(); ?>img/assess_report_arrow_down.png"><span id="assess_report_items_have_product_short_descriptions_that_are_too_short" class="mr_10"></span>items have short descriptions that are less than <span id="assess_report_items_have_product_short_descriptions_that_are_less_than_value"></span> words</div>
                                    </div>
                                    <div id="assess_report_items_2_descriptions_pnl_l" class="mt_10 mb_10 ml_15">
                                        <div class="mr_10"><img src="<?php echo base_url(); ?>img/assess_report_arrow_down.png"><span id="assess_report_items_have_product_long_descriptions_that_are_too_short" class="mr_10"></span>items have long descriptions that are less than <span id="assess_report_items_have_product_long_descriptions_that_are_less_than_value"></span> words</div>
                                    </div>
                                </div>
                                <div id="assess_report_compare_panel" class="mt_10 mb_10 ml_15">
                                    <div class="mr_10"><img src="<?php echo base_url(); ?>img/assess_report_comparison.png">
                                        <span id="assess_report_absent_items_count" class="mr_10"></span>
                                        items in
                                        <span id="assess_report_compare_customer_name"></span>
                                        -
                                        <span id="assess_report_compare_batch_name"></span>
                                        are absent from
                                        <span id="assess_report_own_batch_name"></span>
                                    </div>
                                </div>
                                <div id="assess_report_numeric_difference" class="mt_10 mb_10 ml_15">
                                    <div class="mr_10"><img src="<?php echo base_url(); ?>img/assess_report_cart.png"><span id="assess_report_numeric_difference_caption" class="mr_10"></span></div>
                                </div>
                            </div>
                        </li>
                        <!--li class="boxes ui-resizable">
                            <h3>
                                <span>
                                    <a class="hideShow" onclick="return false;" href="#">
                                        <img src="<?php echo base_url();?>img/arrow-down.png" style="width:12px;margin-right: 10px">
                                    </a>
                                    Product Comparisons
                                </span>
                            </h3>
                            <div style="clear: both;"></div>
                            <div class="boxes_content" style="padding:0px;">
                                <div id="comparison_detail"></div>
                                <div id="comparison_pagination"></div>
                            </div>
                        </li-->
                    </ul>
                </div>

                <div id="assess_view">
                </div>


                <script type="text/javascript" src="<?php echo base_url();?>js/jquery.dataTables.min.js"></script>
                <script type="text/javascript" src="<?php echo base_url();?>js/jquery.json-2.4.min.js"></script>
                <script type="text/javascript" src="<?php echo base_url();?>js/jquery.fileDownload.js"></script>
                <script type="text/javascript" src="<?php echo base_url();?>js/research_assess.js"></script>
            </div>
        </div>
    </div>
</div>

<div class="modal hide fade ci_hp_modals" id='preview_crawl_snap_modal'>
    <div class="modal-body" style='overflow: hidden'>
        <div class='snap_holder'>&nbsp;</div>
    </div>
    <div class="modal-footer">
        <a href="javascript:void(0)" class="btn" data-dismiss="modal">Close</a>
    </div>
</div>

<script>
            $(function() {
                $('head').find('title').text('Reports');
            });
 </script>
