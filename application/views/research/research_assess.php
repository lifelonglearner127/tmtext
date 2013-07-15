<div class="main_content_other"></div>
<div class="research">
    <ul class="nav nav-tabs jq-research-tabs">
        <li class=""><a data-toggle="tab" href="<?php echo site_url('research/create_batch');?>">Create Batch</a></li>
        <li class="active" id="review"><a data-toggle="tab" href="<?php echo site_url('research/research_assess');?>">Assess</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('research');?>">Edit</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('research/research_batches');?>">Review</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('research/research_reports');?>">Reports</a></li>
    </ul>
    <div class="tab-content research_assess">

        <link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/smoothness/jquery-ui-1.8.2.custom.css" />
        <link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/styles.css" />
        <ul class="research_content connectedSortable" id="sortable1">
            <li class="boxes mt_10" id="related_keywords">
                <h3>
                    <span>
                        Batch:
                        <div id="research_customers" class="customer_dropdown"></div>
                        <?php echo form_dropdown('research_batches', $batches_list, array(), 'class="mt_10 mr_10" style="width: 100px;"'); ?>
                    </span>
                    <span class=''>
                        or
                    </span>
                    <span class=''>
                        Category:
                        <?php echo form_dropdown('category', $category_list, array(), 'class="category_list mt_10"'); ?>
                    </span>
                    <a href="#" onclick="return false;" class="mr_10 hideShow">
                        <img style="float: right;" src="<?php echo base_url();?>img/arrow.png" />
                    </a>
                </h3>
                <div class="boxes_content">
                    <div class="row-fluid">
                        <div class="span6">
                            Text:
                            <input id="assess_filter_text" type="text" id="assess_filter_text" class="mt_10 w_286"/>
                            <button id="research_assess_filter" class="btn">Filter</button>
                        </div>
                        <div class="span6">
                            Date Range:
                            <input id="assess_filter_datefrom" type="text" class="mt_10" value="01/15/2010" style="width: 100px;"/>
                            &nbsp-&nbsp
                            <input id="assess_filter_dateto" type="text" class="mt_10" value="02/16/2014" style="width: 100px;"/>
                            <button id="assess_filter_claear_dates" class="btn">Clear</button>
                        </div>
                    </div>
                    <div class="row-fluid">
                        <div class="span12">
                            <div class="span3">
                                <label class="checkbox">
                                    <input id="research_assess_short_check" type="checkbox" checked>
                                    Short Descriptions:
                                </label>
                            </div>
                            <div id="research_assess_short_params">
                                <div class="span4">
                                    <input id="research_assess_short_less_check" type="checkbox" checked>
                                    &#60;
                                    <input id="research_assess_short_less" type="text" class="mt_10" style="width: 50px;" value="100"/>
                                    words
                                    &nbsp &nbsp &nbsp
                                    <input id="research_assess_short_more_check" type="checkbox" checked>
                                    &#62;
                                    <input id="research_assess_short_more" type="text" class="mt_10" style="width: 50px;" value="200"/>
                                    words
                                </div>
                                <div class="span4 offset1">
                                    <label class="checkbox">
                                        <input id="research_assess_short_duplicate_context" type="checkbox" checked>
                                        Duplicate content
                                    </label>
                                    <label class="checkbox">
                                        <input id="research_assess_short_misspelling" type="checkbox" checked>
                                        Mis spellings
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="row-fluid">
                        <div class="span12">
                            <div class="span3">
                                <label class="checkbox">
                                    <input type="checkbox" id="research_assess_long_check" checked>
                                    Long Descriptions:
                                </label>
                            </div>
                            <div id="research_assess_long_params">
                                <div class="span4">
                                    <input id="research_assess_long_less_check" type="checkbox" checked>
                                    &#60;
                                    <input id="research_assess_long_less" type="text" class="mt_10" style="width: 50px;" value="100"/>
                                    words
                                    &nbsp &nbsp &nbsp
                                    <input id="research_assess_long_more_check" type="checkbox" checked>
                                    &#62;
                                    <input id="research_assess_long_more" type="text" name="assess_filter_" style="width: 50px;" value="200"/>
                                    words
                                </div>
                                <div class="span4 offset1">
                                    <label class="checkbox">
                                        <input id="research_assess_long_duplicate_context" type="checkbox" checked>
                                        Duplicate content
                                    </label>
                                    <label class="checkbox">
                                        <input id="research_assess_long_misspelling" type="checkbox" checked>
                                        Mis spellings
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div>
                        <button id="research_assess_update" class="btn">Update</button>
                        <button id="research_assess_export" class="btn">Export</button>
                    </div>
                </div>
            </li>
            <div class='span11'>
                <div class="control-group w_375 float_r mt_20">
                    <button id="research_batches_columns" class="btn btn-success ml_5 float_r">Columns...</button>
                </div>
            </div>
        </ul>


        <!-- choise column dialog box -->
        <div id="research_asses_choiceColumnDialog" title="Select Table Columns">
            <div>
                <form action="" method="post">
                    <p>
                        <input type="checkbox" id="column_created" name="column_created_name" <?php echo($columns['created'] == 'true' ? 'checked="checked"' : ''); ?> />
                        <label for="column_editor">Created</label>
                    </p>
                    <p>
                        <input type="checkbox" id="column_product_name" name="column_product_name_name" <?php echo($columns['product_name'] == 'true' ? 'checked="checked"' : ''); ?> />
                        <label for="column_product_name">Product name</label>
                    </p>
                    <p>
                        <input type="checkbox" id="column_url" name="column_url_name" <?php echo($columns['url'] == 'true' ? 'checked="checked"' : ''); ?> />
                        <label for="column_url">Url</label>
                    </p>
                    <p>
                        <input type="checkbox" id="column_short_description_wc" name="column_short_description_wc_name" <?php echo($columns['short_description_wc'] == 'true' ? 'checked="checked"' : ''); ?> />
                        <label for="column_short_description_wc">Short Description words count</label>
                    </p>
                    <p>
                        <input type="checkbox" id="column_long_description_wc" name="column_long_description_wc_name" <?php echo($columns['long_description_wc'] == 'true' ? 'checked="checked"' : ''); ?> />
                        <label for="column_short_description_wc">Long Description words count</label>
                    </p>
                    <p>
                        <input type="checkbox" id="column_duplicate_context" name="column_duplicate_context_name" <?php echo($columns['duplicate_context'] == 'true' ? 'checked="checked"' : ''); ?> />
                        <label for="column_batch_name">Duplicate context</label>
                    </p>
                    <p>
                        <input type="checkbox" id="column_misspelling" name="column_misspelling_name" <?php echo($columns['misspelling'] == 'true' ? 'checked="checked"' : ''); ?> />
                        <label for="column_actions">Misspelling</label>
                    </p>
                </form>
            </div>
        </div>


        <div class="row-fluid">
            <div id="read" class="ui-tabs-panel ui-widget-content ui-corner-bottom">
                <div id="records_wrapper" class="dataTables_wrapper">
                    <div class="span12">
                        <table id="records">
                            <thead>
                            <tr>
                                <th><div class="draggable">Date</div></th>
                                <th><div class="draggable">Product Name</div></th>
                                <th><div class="draggable">URL</div></th>
                                <th><div class="draggable">Short Words Count</div></th>
                                <th><div class="draggable">Long  Words Count</div></th>
                                <th><div class="draggable">Duplicate Context</div></th>
                                <th><div class="draggable">Mis-Spelling</div></th>
                            </tr>
                            </thead>
                            <tbody></tbody>
                        </table>

                        <!-- Table doesnt work without this jQuery include yet -->
                        <!-- <script type="text/javascript" src="<?php echo base_url();?>js/jquery-1.4.2.min.js"></script>
                        <script type="text/javascript" src="<?php echo base_url();?>js/jquery-ui-1.8.2.min.js"></script> -->
                        <script type="text/javascript" src="<?php echo base_url();?>js/jquery-templ.js"></script>
                        <script type="text/javascript" src="<?php echo base_url();?>js/jquery.validate.min.js"></script>
                        <script type="text/javascript" src="<?php echo base_url();?>js/jquery.dataTables.min.js"></script>
                        <script type="text/javascript" src="<?php echo base_url();?>js/jquery.json-2.4.min.js"></script>

                        <script type="text/template" id="readTemplate">
                            <tr id="${id}">
                                <td class="column_editor">${created}</td>
                                <td class="column_product_name">${product_name}</td>
                                <td class="column_url">${url}</td>
                                <td class="column_short_description_wc">${short_description_wc}</td>
                                <td class="column_long_description_wc">${long_description_wc}</td>
                                <td class="column_duplicate_context">?</td>
                                <td class="column_misspelling">?</td>
                            </tr>
                        </script>


                        <script type="text/javascript" src="<?php echo base_url();?>js/research_assess.js"></script>

                    </div>
                </div>
            </div>
        </div>
    </div>

</div>