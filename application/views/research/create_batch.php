<div class="tabbable">
<ul class="nav nav-tabs jq-research-tabs">
    <li class="active"><a data-toggle="tab" href="<?php echo site_url('research/create_batch');?>">Create Batch</a></li>
    <li class=""><a data-toggle="tab" href="<?php echo site_url('research/research_assess');?>">Assess</a></li>
    <li class=""><a data-toggle="tab" href="<?php echo site_url('research');?>">Edit</a></li>
    <li class=""><a data-toggle="tab" href="<?php echo site_url('research/research_batches');?>">Review</a></li>
    <li class=""><a data-toggle="tab" href="<?php echo site_url('research/research_reports');?>">Reports</a></li>
</ul>
<div class="tab-content">
    <?php echo form_open("research/save", array("class"=>"form-horizontal", "id"=>"create_batch_save"));?>
    <div class="row-fluid">
        <div class="span11">
            Batch:
            <div id="customer_dr" class="customer_dropdown"></div>
            <?php echo form_dropdown('batches', $batches_list, array(), ' style="width: 145px;margin-left:20px"'); ?>
            <span class="ml_10">Add new:</span> <input type="text"  style="width:180px" name="new_batch">
            <button id="new_batch" class="btn" type="button" style="margin-left:5px">Create</button>
            <button id="delete_batch" class="btn btn-danger" type="button" style="margin-left:5px">Delete</button>
        </div>
    </div>

    <div class="row-fluid mt_20">
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
            <div class="info ml_10 "></div>
            <script>
                   $(function () {
                        var url = '<?php echo site_url('research/upload_csv');?>';
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
                                $('#csv_import_create_batch').trigger('click');
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
    <div class="row-fluid">
        A CSV containing one URL or Manufacturer ID per line
    </div>
    <div class="clear"></div>
    <?php echo form_close();?>
</div>
</div>