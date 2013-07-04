<div class="tabbable">
<ul class="nav nav-tabs jq-research-tabs">
    <li class="active"><a data-toggle="tab" href="<?php echo site_url('research/create_batch');?>">Create Batch</a></li>
    <li class=""><a data-toggle="tab" href="<?php echo site_url('research');?>">Edit</a></li>
    <li class=""><a data-toggle="tab" href="<?php echo site_url('research/research_batches');?>">Review</a></li>
    <li class=""><a data-toggle="tab" href="<?php echo site_url('research/research_reports');?>">Reports</a></li>
</ul>
<div class="tab-content">

    <div class="row-fluid">
        <div class="span10">
            Batch:
            <?php
            $selected = array();
            if(count($customer_list) == 2){
                array_shift($customer_list);
                $selected = array(0);
            }
            echo form_dropdown('customers', $customer_list, $selected, 'class="mt_10 category_list"'); ?>
            <span class="ml_10">Add new:</span> <input type="text" class="mt_10" style="width:180px" name="new_batch">
            <button id="new_batch" class="btn" type="button" style="margin-left:5px">Create</button>
        </div>
    </div>

    <div class="row-fluid">
        <div class="control-group">
            <div class="controls">
                Add items to batch: <?php echo form_dropdown('batches', $batches_list, array(), 'class="mt_10" style="width: 145px;"'); ?>
                <button id="csv_import" class="btn btn-success"><i class="icon-white icon-ok"></i>&nbsp;Import</button>
            </div>
        </div>
    </div>
    <div class="row-fluid">
        <div class="span6 admin_system_content">
            <div class="controls">
								<span class="btn btn-success fileinput-button">
									Upload
									<i class="icon-plus icon-white"></i>
									<input id="fileupload" type="file" name="files[]" multiple>
								</span>
                <div id="progress" class="progress progress-success progress-striped">
                    <div class="bar"></div>
                </div>
                <div id="files"></div>
                <script>
                   /* $(function () {
                        'use strict';
                        var url = '<?php echo site_url('research/upload_csv');?>';
                        $('#fileupload').fileupload({
                            url: url,
                            dataType: 'json',
                            done: function (e, data) {
                                $.each(data.result.files, function (index, file) {
                                    if (file.error == undefined) {
                                        $('<p/>').text(file.name).appendTo('#files');
                                    }
                                });
                            },
                            progressall: function (e, data) {
                                var progress = parseInt(data.loaded / data.total * 100, 10);
                                $('#progress .bar').css(
                                    'width',
                                    progress + '%'
                                );
                                if (progress == 100) {
                                    $('#csv_import').trigger('click');
                                }
                            }
                        });
                    });*/
                </script>
            </div>
        </div>
    </div>
    <div class="row-fluid">
        A CSV containing one URL or Manufacturer ID per line
    </div>
    <div class="clear"></div>

</div>
</div>