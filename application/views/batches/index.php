<link type="text/css" rel="stylesheet" href="<?php echo base_url(); ?>css/smoothness/jquery-ui-1.8.2.custom.css" />
<link type="text/css" rel="stylesheet" href="<?php echo base_url(); ?>css/styles.css" />
<div class="modal-header">
	<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
	<h3>Custom Batch</h3>
</div>
<div class="modal-body" style="overflow: hidden !important;">
    <?php echo form_open("research/save", array("class" => "form-horizontal", "id" => "create_batch_save")); ?>
    <div id="batchesDiv">
        <div class="span12 mb_10">
            <div class="span11" style="width:100%;">
               <span style="float: left; margin-top: 5px;margin-right: 5px;">Batch:</span>
                <div id="customer_dr" style="float: left;" class="customer_dropdown"></div>

                <?php echo form_dropdown('batches', $batches_list, array(), ' style="width: 145px;margin-left:60px;float: left;"'); ?>

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
                    function doupload()
                    {
                        var batch_name = $('select[name="batches"]').find('option:selected').text();
                        if(batch_name == ''){
                            job=confirm("You are about to upload a batch but no batch is selected. The uploaded URLs will be crawled but not associated with any specific batch. Are you sure you want to proceed?");
                            if(job!=true)
                            {
                                return false;
                            }else{
                                $('#fileupload').trigger('click');
                            }
                        }else{
                            $('#fileupload').trigger('click');
                        }
                        return false;
                    }
                </script>
                <button class="btn btn-danger" type="button" style="margin-left: 20px;float: left;" onclick="doconfirm()">Delete</button>
                <span  style="float: left;margin-top: 5px;" class="ml_10">Add new:</span> 
                <input type="text"  style="width:180px;float: left;margin-left: 10px;" name="new_batch">
                <button id="new_batch" class="btn" type="button" style="margin-left:5px;float: left;">Create</button>

            </div>
        </div>

        <div id ="tcrawl" class="row-fluid mt_20" style="display:none;">
            Items will be added to a batch if you choose an existing batch.
            <div class="span11 batch_info mt_10">
            </div>
        </div>

        <div class="row-fluid mt_10">
            <div class="admin_system_content">
                <div class="controls span7">
                    <button class="btn btn-success" id="csv_import_create_batch" style="display:none"><i class="icon-white icon-ok"></i>&nbsp;Import</button>
                    <span class="btn btn-success ml_10 pull-left" style="" onclick="doupload();">Upload<i class="icon-plus icon-white"></i></span>
                    <span class="btn btn-success fileinput-button ml_10 pull-left" style="display: none">
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
                        var url = '<?php echo site_url('research/upload_csv'); ?>';
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
            <!--textarea id="urls" class="span10" style="min-height: 111px"></textarea-->
            <div class="search_area uneditable-input span9" onClick="this.contentEditable='true';" style="cursor: text; min-height: 111px; overflow : auto; float: left;" id="urls"></div>
            <button class="btn ml_10" id="add_to_batch" ><i class="icon-white icon-ok"></i>&nbsp;Add to batch</button>
            <button class="btn ml_10 mt_10" id="rename_batch" ><i class="icon-white icon-ok"></i>&nbsp;Rename</button>
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
                
                $("button#rename_batch").click(function(){
                    var renameBatchValue;
                    var renameBatchId;
                    if($('select[name="batches"] option').is(':selected'))
                    {
                        renameBatchValue = $('select[name="batches"] option:selected').text().trim();
                        renameBatchId = $('select[name="batches"] option:selected').val().trim();
                    } else {
                        renameBatchValue = '';
                        renameBatchId = '';
                    }
                    $('#rename_batch_value').val(renameBatchValue);
                    $('#rename_batch_id').val(renameBatchId);
                    $('#rename_batch_dialog').dialog('open');
                    return false;
                });
                $('#rename_batch_dialog').dialog({
                    autoOpen: false,
                    resizable: false,
                    modal: true,
                    buttons: {
                        'Cancel': function() {
                            $(this).dialog('close');
                        },
                        'Rename': function() {
                            $.ajax({
                                url: base_url + 'index.php/batches/batches_rename',
                                //                                dataType : 'json',
                                type : 'post',
                                data : {
                                    batch_id : $('#rename_batch_id').val().trim(),
                                    batch_name : $('#rename_batch_value').val().trim()
                                }
                            }).done(function(data){
                                $('select[name="batches"] option:selected').text($('#rename_batch_value').val().trim());
                                $('#rename_batch_dialog').dialog('close');
                            });
                        }
                    },
                    width: '250px'
                });
                
            });
        </script>

        <div id="rename_batch_dialog" title="Rename batch">
            <div>
                <p>
                    <label for="column_category">Batch Name:</label>
                    <input type="hidden" id="rename_batch_id" value="" />
                    <input type="text" id="rename_batch_value" value="" />
                </p>
            </div>
        </div>
    </div>
    <?php echo form_close(); ?>
</div>