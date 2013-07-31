<div class="tabbable">
    <ul class="nav nav-tabs jq-system-tabs">
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system');?>">General</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_compare');?>">Product Compare Interface</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_productsmatch');?>">Product Match</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('site_crawler');?>">Site Crawler</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/batch_review');?>">Batch Review</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/sites_view');?>">Sites</a></li>
        <li class="active"><a data-toggle="tab" href="<?php echo site_url('system/best_sellers');?>">Best Sellers</a></li>
    </ul>
    <div class="tab-content">
        <div class="row-fluid mt_10">
            <div class="admin_system_content">
                <div class="controls span7">
                    <button class="btn btn-success" id="csv_import_create_batch" style="display:none"><i class="icon-white icon-ok"></i>&nbsp;Import</button>
								<span class="btn btn-success fileinput-button ml_10 pull-left" style="">
									Upload
									<i class="icon-plus icon-white"></i>
									<input type="file" multiple="" name="files[]" id="fileupload">
								</span>
                    <div class="progress progress-success progress-striped span7" id="progress">
                        <div class="bar"></div>
                    </div>
                    <div id="files"></div>
                    <input type="hidden" name="choosen_file" />
                </div>
                <button id="best_sellers_csv" style="display: none"><i class="icon-white icon-ok"></i>&nbsp;Import</button>
                <button class="btn btn-danger" id="delete"><i class="icon-white icon-ok"></i>&nbsp;Delete</button>
                <button class="btn btn-danger" id="delete_all"><i class="icon-white icon-ok"></i>&nbsp;Delete All</button>
                <div class="info ml_10 "></div>
                <script>
                    $(function () {
                        var url = '<?php echo site_url('system/upload_csv');?>';
                        $('#fileupload').fileupload({
                            url: url,
                            dataType: 'json',
                            done: function (e, data) {
                                $('input[name="choosen_file"]').val(data.result.files[0].name);
                                $.each(data.result.files, function (index, file) {
                                    /*if (file.error == undefined) {
                                     $('<p/>').text(file.name).appendTo('#files');
                                     }*/
                                });
                                $('#best_sellers_csv').trigger('click');
                            },
                            progressall: function (e, data) {
                                var progress = parseInt(data.loaded / data.total * 100, 10);
                                $('#progress .bar').css(
                                    'width',
                                    progress + '%'
                                );
                                if (progress == 100) {

                                }
                            }
                        });
                    });
                </script>
            </div>
        </div>
        <div class="row-fluid mt_10">
            <?php
            if(count($customers_list) > 0) { ?>
                    <div id="hp_boot_drop_<?php echo $v; ?>" class="btn-group <?php echo $dropup; ?> hp_boot_drop">
                        <button class="btn btn-danger btn_caret_sign">[ Choose site ]</button>
                        <button class="btn btn-danger dropdown-toggle" data-toggle="dropdown">
                            <span class="caret"></span>
                        </button>
                        <ul class="dropdown-menu">
                            <?php foreach($customers_list as $val) { ?>
                                <li><a data-item="<?php echo $v; ?>" data-value="<?php echo $val['name_val']; ?>" href="javascript:void(0)"><?php echo $val['name']; ?></a></li>
                            <?php } ?>
                        </ul>
                    </div>
                <?php }
            ?>
            <?php  echo form_dropdown('department', $departmens_list, null, 'class="inline_block lh_30 w_375 mb_reset"'); ?>
        </div>

                <link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/smoothness/jquery-ui-1.8.2.custom.css" />
                <link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/styles.css" />
                <script>
                    $(function() {
                        $( ".draggable" ).draggable();
                    });
                </script>
                <div class="row-fluid" style="min-height: 300px">
                        <div id="ajaxLoadAni">
                            <span>Loading...</span>
                        </div>

                        <div id="tabs" class="mt_10">
                            <div id="read">
                                <table id="best_sellers" style="width: 100%;">
                                    <thead></thead>
                                    <tbody></tbody>
                                </table>
                            </div>
                            <div id="create">
                            </div>
                        </div> <!-- end tabs -->

                        <!-- message dialog box -->
                        <div id="msgDialog"><p></p></div>

                        <!-- Table doesnt work without this jQuery include yet -->
                         <script type="text/javascript" src="<?php echo base_url();?>js/jquery-templ.js"></script>
                        <script type="text/javascript" src="<?php echo base_url();?>js/jquery.validate.min.js"></script>
                        <script type="text/javascript" src="<?php echo base_url();?>js/jquery.dataTables.min.js"></script>
                        <script type="text/javascript" src="<?php echo base_url();?>js/jquery.json-2.4.min.js"></script>

                        <script type="text/javascript" src="<?php echo base_url();?>js/research_edit.js"></script>
                </div>
    </div>
</div>
