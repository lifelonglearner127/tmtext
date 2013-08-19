        <?php echo form_open("research/save", array("class"=>"form-horizontal", "id"=>"create_batch_save"));?>
        <div class="row-fluid">
            <div class="span12">
                Batch:
                <div id="product_customers" class="customer_dropdown" style="display: inline;width: 160px;"></div>
                <?php echo form_dropdown('product_batches', $batches_list, array(), ' id="batchess" style="width: 145px;margin-left:20px"'); ?>
                <script>
                    function doconfirm()
                    {
                        var batch_name = $('select[name="batches"]').find('option:selected').text();
                        job=confirm("You are about to delete batch "+batch_name+". Are you sure you want to delete this batch?");
                        if(job!=true)
                        {
                            return false;
                        } else {
                            var oDropdown = $("#customer_dr").msDropdown().data("dd");
                            $.post(base_url + 'index.php/research/delete_batch', {
                                'batch_name': batch_name
                            }, function(data) {
                                oDropdown.setIndexByValue('All customers');
                                $('select[name="batches"] option').each(function(){
                                    if($(this).text() == batch_name){
                                        $(this).remove();
                                    }
                                });
                                $('.info').append('<p class="alert-success">The batch was successfully deleted</p>').fadeOut(10000);
                            }, 'json');
                        }
                    }
                </script>
                <button class="btn btn-danger" type="button" style="margin-left:5px" onclick="doconfirm()">Delete</button>
                <span class="ml_10">Add new:</span> <input type="text"  style="width:180px" name="new_batch">
                <button id="new_batch" class="btn" type="button" style="margin-left:5px">Create</button>

            </div>
        </div>

        <div class="row-fluid mt_20">
            Items will be added to a batch if you choose an existing batch.
            <div class="span11 batch_info mt_10">
            </div>
        </div>

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
                <div class="info ml_10 "></div>
                <script>
                    $(function () {
                        var url = '<?php echo site_url('research/upload_csv');?>';
                        $('#fileupload').fileupload({
                            url: url,
                            dataType: 'json',
                            start:function(e, data){
                                $('#progress .bar').show();
                            },
                            done: function (e, data) {
                                $('input[name="choosen_file"]').val(data.result.files[0].name);
                                $.each(data.result.files, function (index, file) {
                                    /*if (file.error == undefined) {
                                     $('<p/>').text(file.name).appendTo('#files');
                                     }*/
                                });
                                $('#csv_import_create_batch').trigger('click');
                                setTimeout(function(){
                                    //$('#progress .bar').css({'width':'0%'});
                                    $('#progress .bar').hide();
                                }, 1000);

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
        <div class="row-fluid mt_20">
            <textarea id="urls" class="span10" style="min-height: 100px"></textarea >
            <button class="btn ml_10" id="add_to_batch" ><i class="icon-white icon-ok"></i>&nbsp;Add to batch</button>
            <button class="btn btn-danger ml_10 mt_10" id="delete_from_batch"><i class="icon-white icon-ok"></i>&nbsp;Delete</button>
        </div>
        <div class="row-fluid mt_20">
            <div class="controls span7">
                <button class="btn btn-success ml_10" id="import_from_sitemap"><i class="icon-white icon-ok"></i>&nbsp;Import Sitemap</button>
                <div class="info ml_10" id="import_sitemap"></div>
            </div>
        </div>
        <div class="clear"></div>
        <div class="info-message text-success mt_10"></div>
        <script>
            $(function() {
                $('head').find('title').text('Batches');
            });
        </script>
        <?php echo form_close();?>