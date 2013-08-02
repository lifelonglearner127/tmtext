<div class="main_content_other"></div>
<div class="tabbable">
    <ul class="nav nav-tabs jq-research-tabs">
        <li class=""><a data-toggle="tab" href="<?php echo site_url('research');?>">Edit</a></li>
        <li class="active" id="review"><a data-toggle="tab" href="<?php echo site_url('research/research_batches');?>">Review</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('research/research_reports');?>">Reports</a></li>
    </ul>
    <div class="tab-content research_batches">

        <link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/smoothness/jquery-ui-1.8.2.custom.css" />
        <link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/styles.css" />
        <div id="research_tab2" class="tab-pane active">
            <div class="row-fluid">
                <div class='span12'>
                    Batch:
                    <div id="research_customers" class="customer_dropdown"></div>
                    <?php echo form_dropdown('research_batches', $batches_list, array(), 'class="mt_10 mr_10" style="width: 100px;"'); ?>
                    Edit Name:<input type="text" class="mt_10 ml_10" name="batche_name" />
                    <button id="research_batches_save" type="button" class="btn btn-success ml_5">Save</button>
                    <button id='export_batch_review' type="button" class="btn btn-success ml_5">Export</button>
                </div>
                <div style='margin-left: 0px;' class='span12 mt_10'>
                    <span class='inline_block lh_30 mr_10'>Filter:</span>
                    <input type="text" id="research_batches_text" name="research_batches_text" value="" class="inline_block lh_30 w_286 mb_reset" placeholder=""/>
                    <button id="research_batches_search" type="button" class="btn ml_10" >Search</button>
                    <div class="control-group w_375 float_r">
                        <button id="research_batches_columns" class="btn btn-success ml_5 float_r">Columns...</button>
                    </div>
                </div>

            </div>
            <div class="row-fluid">
                <div id="ajaxLoadAni">
                    <span>Loading...</span>
                </div>

                <div id="tabs" class="mt_10">

                    <ul>
                        <li><a href="#read">Review</a></li>
                        <!--li><a href="#create"></a></li-->
                    </ul>

                    <div id="read">
                        <table id="records">
                            <thead>
                            <tr>
                                <th><div class="draggable">Editor</div></th>
                                <th><div class="draggable">Product Name</div></th>
                                <th><div class="draggable">URL</div></th>
                                <th><div class="draggable">Short Description</div></th>
                                <th><div class="draggable">Words</div></th>
                                <th><div class="draggable">Long Description</div></th>
                                <th><div class="draggable">Words</div></th>
                                <th><div class="draggable">Batch Name</div></th>
                                <th><div class="draggable">Actions</div></th>
                            </tr>
                            </thead>
                            <tbody></tbody>
                        </table>
                    </div>
                    <div id="create">
                    </div>

                </div> <!-- end tabs -->

                <!-- update form in dialog box -->
                <div id="updateDialog" title="Update">
                    <div>
                        <form action="" method="post">
                            <p>
                                <label for="name">Product Name:</label>
                                <input type="text" id="product_name" name="product_name" />
                            </p>

                            <p>
                                <label for="url">Url:</label>
                                <input type="text" id="url" name="url" />
                            </p>
                            <div class="parag">
                                <span class="labeler">
                                    <label for="short_description">Short Description:</label>
                                </span>
                                <textarea id="short_description" name="short_description" ></textarea>
                                <div class="bottom-labeler">
                                    <label><span id="short_description_wc">0</span> words<input type="hidden" name="short_description_wc" /></label>
                                </div>
                            </div>
                            <div class="parag">
                                <span class="labeler">
                                <label for="long_description">Long Description:</label>
                                </span>
                                <textarea id="long_description" name="long_description" ></textarea>
                                <div class="bottom-labeler">
                                    <label><span id="long_description_wc">0</span> words<input type="hidden" name="long_description_wc" /></label>
                                </div>
                            </div>

                            <input type="hidden" id="userId" name="id" />
                        </form>
                    </div>
                </div>

                <!-- delete confirmation dialog box -->
                <div id="delConfDialog" title="Confirm">
                    <p>Are you sure?</p>
                </div>

                <!-- message dialog box -->
                <div id="msgDialog"><p></p></div>

                <!-- choise column dialog box -->
                <div id="choiceColumnDialog" title="Select Table Columns">
                    <div>
                        <form action="" method="post">
                            <p>
                                <input type="checkbox" id="column_editor" name="column_editor_name" <?php echo($columns['editor'] == 'true' ? 'checked="checked"' : ''); ?> />
                                <label for="column_editor">Editor</label>
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
                                <input type="checkbox" id="column_short_description" name="column_short_description_name" <?php echo($columns['short_description'] == 'true' ? 'checked="checked"' : ''); ?> />
                                <label for="column_short_description">Short Description</label>
                            </p>
                            <p>
                                <input type="checkbox" id="column_short_description_wc" name="column_short_description_wc_name" <?php echo($columns['short_description_wc'] == 'true' ? 'checked="checked"' : ''); ?> />
                                <label for="column_short_description_wc">Words</label>
                            </p>
                            <p>
                                <input type="checkbox" id="column_long_description" name="column_long_description_name" <?php echo($columns['long_description'] == 'true' ? 'checked="checked"' : ''); ?> />
                                <label for="column_long_description">Long Description</label>
                            </p>
                            <p>
                                <input type="checkbox" id="column_long_description_wc" name="column_long_description_wc_name" <?php echo($columns['long_description_wc'] == 'true' ? 'checked="checked"' : ''); ?> />
                                <label for="column_long_description_wc">Words</label>
                            </p>
                            <p>
                                <input type="checkbox" id="column_batch_name" name="column_batch_name" <?php echo($columns['batch_name'] == 'true' ? 'checked="checked"' : ''); ?> />
                                <label for="column_batch_name">Batch Name</label>
                            </p>
                            <p>
                                <input type="checkbox" id="column_actions" name="column_actions_name" <?php echo($columns['actions'] == 'true' ? 'checked="checked"' : ''); ?> />
                                <label for="column_actions">Actions</label>
                            </p>
                        </form>
                    </div>
                </div>

                <!-- Table doesnt work without this jQuery include yet -->
                <!-- <script type="text/javascript" src="<?php echo base_url();?>js/jquery-1.4.2.min.js"></script>
                <script type="text/javascript" src="<?php echo base_url();?>js/jquery-ui-1.8.2.min.js"></script> -->
                <script type="text/javascript" src="<?php echo base_url();?>js/jquery-templ.js"></script>
                <script type="text/javascript" src="<?php echo base_url();?>js/jquery.validate.min.js"></script>
                <script type="text/javascript" src="<?php echo base_url();?>js/jquery.dataTables.min.js"></script>
                <script type="text/javascript" src="<?php echo base_url();?>js/jquery.json-2.4.min.js"></script>

                <script type="text/template" id="readTemplate">
                    <tr id="${id}" status="${status}">
                        <td class="column_editor">${user_id}</td>
                        <td class="column_product_name">${product_name}</td>
                        <td class="column_url">${url}</td>
                        <td class="column_short_description">${short_description}</td>
                        <td class="column_short_description_wc">${short_description_wc}</td>
                        <td class="column_long_description">${long_description}</td>
                        <td class="column_long_description_wc">${long_description_wc}</td>
                        <td class="column_batch_name">${batch_name}</td>
                        <td nowrap class="column_actions"><a class="updateBtn icon-edit" style="float:left;" href="${updateLink}"></a>
                            <a class="deleteBtn icon-remove ml_5" href="${deleteLink}"></a>
                        </td>
                    </tr>
                </script>

                <script type="text/javascript" src="<?php echo base_url();?>js/all.js"></script>
            </div>
            <div class="row-fluid mt_20">
                <button id="research_batches_undo" type="button" class="btn ml_10">Undo</button>
            </div>
            <div class="clear mt_40"></div>
        </div>
    </div>
</div>