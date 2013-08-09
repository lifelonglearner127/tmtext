<link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/smoothness/jquery-ui-1.8.2.custom.css" />
<link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/styles.css" />
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
                <?php echo form_dropdown('research_assess_batches', $batches_list, array(), 'class="mt_10 mr_10" style="width: 175px;margin-left:20px"'); ?>
            </span>
            <span class=''>
                or
            </span>
            <span class=''>
                Category:
                <?php echo form_dropdown('category', $category_list, array(), 'class="category_list mt_10"'); ?>
            </span>
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
                        <input id="research_assess_price_diff" type="checkbox" checked>
                        Price Difference
                    </label>
                </div>
            </div>
            <div class="row-fluid assess_filter_options">
                <div class="span12">
                    <div class="span3" style="height: 50px;">
                        <label class="checkbox">
                            <input id="research_assess_short_check" type="checkbox" checked>
                            Short Descriptions:
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
                <div class="span12">
                    <div class="span3" style="height: 50px;">
                        <label class="checkbox">
                            <input type="checkbox" id="research_assess_long_check" checked>
                            Long Descriptions:
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
            <div>
                <button id="research_assess_update" class="btn btn-success">Update</button>
                <button id="research_assess_export" class="btn">Export</button>
            </div>
        </div>
    </li>
</ul>


<!-- choise column dialog box -->
<div id="research_assess_choiceColumnDialog" title="Select Table Columns">
    <div>
        <form action="" method="post">
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
                <label for="column_short_description_wc">Word Count (S)</label>
            </p>
            <p>
                <input type="checkbox" id="column_short_seo_phrases" data-col_name="short_seo_phrases" name="column_short_seo_phrases_name" <?php echo($columns['short_seo_phrases'] == 'true' ? 'checked="checked"' : ''); ?> />
                <label for="column_short_seo_phrases">SEO Phrases (S)</label>
            </p>
            <p>
                <input type="checkbox" id="column_long_description_wc" data-col_name="long_description_wc" name="column_long_description_wc_name" <?php echo($columns['long_description_wc'] == 'true' ? 'checked="checked"' : ''); ?> />
                <label for="column_short_description_wc">Word Count (L)</label>
            </p>
            <p>
                <input type="checkbox" id="column_long_seo_phrases" data-col_name="long_seo_phrases" name="column_long_seo_phrases_name" <?php echo($columns['long_seo_phrases'] == 'true' ? 'checked="checked"' : ''); ?> />
                <label for="column_long_seo_phrases">SEO Phrases (S)</label>
            </p>
            <p>
                <input type="checkbox" id="column_duplicate_content" data-col_name="duplicate_content" name="column_duplicate_content_name" <?php echo($columns['duplicate_content'] == 'true' ? 'checked="checked"' : ''); ?> />
                <label for="column_batch_name">Duplicate content</label>
            </p>
            <p>
                <input type="checkbox" id="column_price_diff" data-col_name="price_diff" name="column_price_diff" <?php echo($columns['price_diff'] == 'true' ? 'checked="checked"' : ''); ?> />
                <label for="column_actions">Price diff</label>
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
                    Show:
                    <a id="assess_tbl_show_case_report" data-case="report" title="Report" href="#" class="active_link">Report</a> |
                    <a id="assess_tbl_show_case_recommendations" data-case="recommendations" title="Recommendations" href="#">Recommendations</a> |
                    <a id="assess_tbl_show_case_details" data-case="details" title="Details" href="#">Details</a>
                </div>
                <button id="research_batches_columns" class="btn ml_5 float_r">Columns...</button>
                <div id="assess_report">
                    <ul class="ui-sortable">
                        <li class="boxes ui-resizable">
                            <h3>
                                <span>
                                    <a class="hideShow" onclick="return false;" href="#">
                                        <img src="http://tmeditor/img/arrow-down.png" style="width:12px;margin-right: 10px">
                                    </a>
                                    Summary
                                </span>
                                <span style="margin-left: 270px;">
                                    <a id="assess_report_download_pdf" target="_blank">Download PDF</a>
                                </span>
                                <a class="ml_10 research_arrow" href="#">
                                    <img src="http://tmeditor//webroot/img/arrow.png">
                                </a>
                            </h3>
                            <div class="boxes_content" style="padding:0px;">
                                <div class="mt_10 ml_15">
                                    <div class="mr_10"><img src="<?php echo base_url(); ?>img/assess_report_number.png"><span id="assess_report_total_items" class="mr_10"></span>total items</div>
                                </div>
                                <div class="mt_10 ml_15">
                                    <div class="mr_10"><img src="<?php echo base_url(); ?>img/assess_report_dollar.png"><span id="assess_report_items_priced_higher_than_competitors" class="mr_10"></span>items priced higher than competitors</div>
                                </div>
                                <div class="mt_10 ml_15">
                                    <div class="mr_10"><img src="<?php echo base_url(); ?>img/assess_report_D.png"><span id="assess_report_items_have_more_than_50_percent_duplicate_content" class="mr_10"></span>items have more than 50% duplicate content</div>
                                </div>
                                <div class="mt_10 ml_15">
                                    <div class="mr_10"><img src="<?php echo base_url(); ?>img/assess_report_seo.png"><span id="assess_report_items_unoptimized_product_content" class="mr_10"></span>items have unoptimized product content</div>
                                </div>
                                <div class="mt_10 mb_10 ml_15">
                                    <div class="mr_10"><img src="<?php echo base_url(); ?>img/assess_report_arrow_down.png"><span id="assess_report_items_have_product_context_that_is_too_short" class="mr_10"></span>items have product content that is too short</div>
                                </div>
                            </div>
                        </li>
                        <li class="boxes ui-resizable">
                            <h3>
                                <a class="hideShow" onclick="return false;" href="#">
                                    <img src="http://tmeditor/img/arrow-down.png" style="width:12px;margin-right: 10px">
                                </a>
                                Recommendations
                                <a class="ml_10 research_arrow" href="#">
                                    <img src="http://tmeditor//webroot/img/arrow.png">
                                </a>
                            </h3>
                        </li>
                        <li class="boxes ui-resizable">
                            <h3>
                                <a class="hideShow" onclick="return false;" href="#">
                                    <img src="http://tmeditor/img/arrow-down.png" style="width:12px;margin-right: 10px">
                                </a>
                                Pricing Details
                                <a class="ml_10 research_arrow" href="#">
                                    <img src="http://tmeditor//webroot/img/arrow.png">
                                </a>
                            </h3>
                        </li>
                    </ul>
                </div>

                <script type="text/javascript" src="<?php echo base_url();?>js/jquery.dataTables.min.js"></script>
                <script type="text/javascript" src="<?php echo base_url();?>js/jquery.json-2.4.min.js"></script>
                <script type="text/javascript" src="<?php echo base_url();?>js/research_assess.js"></script>

            </div>
        </div>
    </div>
</div>
<script>
            $(function() {
                $('head').find('title').text('Assess');
            });
 </script>