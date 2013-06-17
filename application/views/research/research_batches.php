<div class="tabbable">
    <ul class="nav nav-tabs jq-research-tabs">
        <li class=""><a data-toggle="tab" href="<?php echo site_url('research');?>">General</a></li>
        <li class="active"><a data-toggle="tab" href="<?php echo site_url('research/research_batches');?>">Batches</a></li>
    </ul>
    <div class="tab-content research_batches">
        <link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/smoothness/jquery-ui-1.8.2.custom.css" />
        <link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/styles.css" />
        <div id="research_tab2" class="tab-pane active">
            <div class="row-fluid">
                <div class="span6">
                    Batch: <?php echo form_dropdown('research_batches', $batches_list, array(), 'class="mt_10 mr_10" style="width: 100px;"'); ?>
                    Edit Name:<input type="text" class="mt_10 ml_10" name="batche_name" />
                    <button id="research_batches_save" type="button" class="btn pull-right btn-success mt_10">Save</button>
                    <input type="text" id="research_batches_text" name="research_batches_text" value="" class="span8 ml_0" placeholder=""/>
                    <button id="research_batches_search" type="button" class="btn ml_10">Search</button>
                </div>
                <div class="span6">
                    <div class="control-group">
                        <label class="control-label mt_10" for="customer_name" style="width:70px; float: left">Columns:</label>
                        <div class="controls mt_10">
                            <ul id="gallery" class="product_title_content gallery span10">
                                <li><span>Date</span><a hef="#" class="ui-icon-trash">x</a></li>
                                <li><span>Meta Title</span><a hef="#" class="ui-icon-trash">x</a></li>
                                <li><span>Meta Description</span><a hef="#" class="ui-icon-trash">x</a></li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
            <div class="row-fluid">
                <div id="ajaxLoadAni">
                    <span>Loading...</span>
                </div>

                <div id="tabs">

                    <ul>
                        <li><a href="#read">Read</a></li>
                        <li><a href="#create">Create</a></li>
                    </ul>

                    <div id="read">
                        <table id="records">
                            <thead>
                            <tr>
                                <th>Editor</th>
                                <th>Product Name</th>
                                <th>URL</th>
                                <th>Short Description</th>
                                <th>Long Description</th>
                                <th>Actions</th>
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
                            </p>
                            <p>
                                <label for="long_description">Long Description:</label>
                                <textarea id="long_description" name="long_description" ></textarea>
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

                <script type="text/javascript" src="<?php echo base_url();?>js/jquery-1.4.2.min.js"></script>
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
                        <td><a class="updateBtn" href="${updateLink}">Update</a><br />
                            <a class="deleteBtn" href="${deleteLink}">Delete</a>
                        </td>
                    </tr>
                </script>

                <script type="text/javascript" src="<?php echo base_url();?>js/all.js"></script>
            </div>
            <div class="row-fluid mt_20">
                <button id="research_batches_delete" type="button" class="btn btn-danger ml_10">Delete</button>
                <button id="research_batches_undo" type="button" class="btn ml_10">Undo</button>
            </div>
            <div class="clear mt_40"></div>
        </div>
    </div>
</div>