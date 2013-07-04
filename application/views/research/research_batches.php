<div class="main_content_other"></div>
<div class="tabbable">
    <ul class="nav nav-tabs jq-research-tabs">
        <li class=""><a data-toggle="tab" href="<?php echo site_url('research/create_batch');?>">Create Batch</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('research');?>">Edit</a></li>
        <li class="active"><a data-toggle="tab" href="<?php echo site_url('research/research_batches');?>">Review</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('research/research_reports');?>">Reports</a></li>
    </ul>
    <div class="tab-content research_batches">
        <link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/smoothness/jquery-ui-1.8.2.custom.css" />
        <link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/styles.css" />
        <script>

            $(function() {
                $( ".draggable" ).draggable();
            });
        </script>
        <div id="research_tab2" class="tab-pane active">
            <div class="row-fluid">
                <!-- NEW STUFF (START) -->
                <div class='span12'>
                    Batch:
                    <?php
                        $selected = array();
                        if(count($customer_list) == 2){
                            array_shift($customer_list);
                            $selected = array(0);
                        }
                        echo form_dropdown('research_customers', $customer_list, $selected, 'class="mt_10 category_list"');
                    ?>
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
                        <label class="control-label mt_10" for="customer_name" style="width:70px; float: left">Columns:</label>
                        <div class="controls">
                            <ul id="gallery" class="product_title_content gallery w_300 pull-right">
                                <li><span>Date</span><a hef="#" class="ui-icon-trash">x</a></li>
                                <li><span>Meta Title</span><a hef="#" class="ui-icon-trash">x</a></li>
                                <li><span>Meta Description</span><a hef="#" class="ui-icon-trash">x</a></li>
                            </ul>
                        </div>
                    </div>
                </div>
                <!-- NEW STUFF (END) -->

                <!-- OLD STUFF (START) -->
                <!-- <div class="span6">
                    Batch:
                    <?php echo form_dropdown('research_customers', $customer_list, array(), 'class="mt_10 category_list"'); ?>
                    <?php echo form_dropdown('research_batches', $batches_list, array(), 'class="mt_10 mr_10" style="width: 100px;"'); ?><br />
                    Edit Name:<input type="text" class="mt_10 ml_10" name="batche_name" />
                    <button id="research_batches_save" type="button" class="btn btn-success ml_5">Save</button>
                </div> -->
                <!-- <div class="span6">
                    <button id="research_batches_search" type="button" class="btn ml_10 pull-right mt_10" >Filter</button>
                    <input type="text" id="research_batches_text" name="research_batches_text" value="" class="span8 ml_0 pull-right mt_10" placeholder=""/>
                    <div class="control-group">
                        <label class="control-label mt_50" for="customer_name" style="width:70px; float: left">Columns:</label>
                        <div class="controls mt_10">
                            <ul id="gallery" class="product_title_content gallery span10 pull-right">
                                <li><span>Date</span><a hef="#" class="ui-icon-trash">x</a></li>
                                <li><span>Meta Title</span><a hef="#" class="ui-icon-trash">x</a></li>
                                <li><span>Meta Description</span><a hef="#" class="ui-icon-trash">x</a></li>
                            </ul>
                        </div>
                    </div>
                </div> -->
                <!-- OLD STUFF (END) -->

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
                                <th><div class="draggable">Long Description</div></th>
                                <th><div class="draggable">BatchName</div></th>
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
                            <p>
                                <label for="short_description">Short Description:</label>
                                <textarea id="short_description" name="short_description" ></textarea>
                                <label><span id="research_wc">0</span> words<input type="hidden" name="short_description_wc" /></label>
                            </p>
                            <p>
                                <label for="long_description">Long Description:</label>
                                <textarea id="long_description" name="long_description" ></textarea>
                                <label><span id="research_wc1">0</span> words<input type="hidden" name="long_description_wc" /></label>
                            </p>

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
                
                <!-- This prevents jquery fileupload
                <script type="text/javascript" src="<?php //echo base_url();?>js/jquery-1.4.2.min.js"></script>
                     this prevents jquery fileupload -->
                
                <script type="text/javascript" src="<?php echo base_url();?>js/jquery-ui-1.8.2.min.js"></script>
                <script type="text/javascript" src="<?php echo base_url();?>js/jquery-templ.js"></script>
                <script type="text/javascript" src="<?php echo base_url();?>js/jquery.validate.min.js"></script>
                <script type="text/javascript" src="<?php echo base_url();?>js/jquery.dataTables.min.js"></script>

                <script type="text/template" id="readTemplate">
                    <tr id="${id}">
                        <td>${user_id}</td>
                        <td>${product_name}</td>
                        <td>${url}</td>
                        <td>${short_description}</td>
                        <td>${long_description}</td>
                        <td>${batch_name}</td>
                        <td nowrap><a class="updateBtn icon-edit" style="float:left;" href="${updateLink}"></a>
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