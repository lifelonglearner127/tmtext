<div class="tabbable">
        <ul class="nav nav-tabs jq-system-tabs">
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system');?>">General</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/sites_view');?>">Sites</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('site_crawler');?>">Site Crawler</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('site_crawler/instances_list');?>">Crawler Instances</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_uploadmatchurls');?>">Upload Match URLs</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_dostatsmonitor');?>">Do_stats Monitor</a></li>
        <li class="active"><a data-toggle="tab" href="<?php echo site_url('brand/import');?>">Brands</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/batch_review');?>">Batch Review</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_compare');?>">Product Compare</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_productsmatch');?>">Product Match</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_reports');?>">Reports</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_logins');?>">Logins</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/keywords');?>">Keywords</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_rankings');?>">Rankings</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_pricing');?>">Pricing </a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/product_models');?>">Product models </a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/snapshot_queue');?>">Snapshot Queue</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/sync_keyword_status');?>">Sync Keyword Status</a></li>
        </ul>
        <div class="tab-content">
                <div id="tab1" class="tab-pane active">
                    <?php echo form_open("brand/save", array("class"=>"form-horizontal", "id"=>"brand_data_save", "enctype"=>"multipart/form-data"));?>
                                <h3>Import Brand/Company Data:</h3>
                                <div class="row-fluid">
                                    <div class="span4">
                                        <h4>Choose Brand Types:</h4>
                                    </div>
                                    <div class="span3">
                                        <select id="brand_types" name="brand_types">
                                            <?php foreach($brand_types as $brand_type) { ?>
                                                    <option value="<?php echo $brand_type->id; ?>"><?php echo $brand_type->name; ?></option>
                                            <?php } ?>
                                        </select>
                                        <input type="hidden" name="brand_data_csv" id="brand_data_csv" value="" />
                                        <input type="hidden" name="company_data_csv" id="company_data_csv" value="" />
                                    </div>
                                    <div class="clearfix"></div>
                                    <div class="span4" style="margin-left:0px;">
                                        <h4>Upload Brand List CSV:</h4>
                                    </div>
                                    <div class="span3">
                                        <span class="btn btn-success fileinput-button">
                                                Upload
                                                <i class="icon-plus icon-white"></i>
                                                <input id="fileupload" type="file" name="files[]">
                                        </span>

                                    </div>
                                    <div class="clearfix"></div>
                                    <div class="span4" style="margin-left:0px;">
                                        <h4>Upload Brand Social Data CSV:</h4>
                                    </div>
                                    <div class="span3">
                                        <span class="btn btn-success fileinput-button">
                                                Upload
                                                <i class="icon-plus icon-white"></i>
                                                <input id="fileupload_company" type="file" name="files[]">
                                        </span>
                                    </div>
                                    <div class="clearfix margin-top-50"></div>
                                    <div class="span4">
                                        <button id="brand_csv_import" class="btn btn-success"><i class="icon-white icon-ok"></i>&nbsp;Import</button>
                                        <input type="reset" name="reset" id="reset" class="hide" />
                                    </div>
                                    <div id="progress" class="progress progress-success progress-striped span3">
                                            <div class="bar"></div>
                                    </div>
                                    <div id="files"></div>
                                    <div class="clearfix"></div>
                                    <div class="span6">
                                        <div class="alert alert-success hide import_success">
                                            <strong>Imported successfully!</strong>
                                            
                                        </div>
                                    </div>
                                </div>
                    <?php echo form_close();?>
                                <h3>Add Brand Type:</h3>
                                <div class="row-fluid">
                                    <?php echo form_open("brand/addtype", array("class"=>"form-horizontal", "id"=>"add_type"));?>
                                    <div class="span3"><input type="text" name="brand_type" id="brand_type" value="" /></div>
                                    <div class="span2"><button id='brand_type_btn' class="btn btn-success"><i class="icon-white icon-ok"></i>&nbsp;Add</button></div>        
                                    <div class="span6">
                                        <div class="alert alert-success hide add_success">
                                            <strong>Added successfully!</strong>
                                        </div>
                                    </div>
                                    <?php echo form_close();?>
                                </div>
                </div>
        </div>
</div>
<script type="text/javascript">
    $(function () {
        var url = '<?php echo site_url('brand/csv_upload');?>';
        $('#fileupload').fileupload({
            url: url,
            dataType: 'json',
            done: function (e, data) {
                $('<p/>').text(data.files[0].name).appendTo('#files');
                $('#brand_data_csv').val(data.files[0].name);
                $('#brand_csv_import').trigger('click');
            },
            progressall: function (e, data) {
                var progress = parseInt(data.loaded / data.total * 100, 10);
                $('#progress .bar').css(
                    'width',
                    progress + '%'
                );
                if (progress == 100) {}
            }
        });
        $('#fileupload_company').fileupload({
            url: url,
            dataType: 'json',
            done: function (e, data) {
                $('<p/>').text(data.files[0].name).appendTo('#files');
                $('#company_data_csv').val(data.files[0].name);
                $('#brand_csv_import').trigger('click');
            },
            progressall: function (e, data) {
                var progress = parseInt(data.loaded / data.total * 100, 10);
                $('#progress .bar').css(
                    'width',
                    progress + '%'
                );
                if (progress == 100) {}
            }
        });
        $('#brand_csv_import').click(function() {
            if($('#brand_data_csv').val() == '' && $('#company_data_csv').val() == '') {
                return false;
            }
            var button = $(this);
            button.attr('disabled', 'disabled');
            var url = $(this).parents().find('form').attr( 'action' ).replace('save', 'csv_import');
            
            $.ajax({
                type: "POST",
                url: url,
                data: $('#brand_data_save').serialize(),
                dataType: 'json',
                success: function(data){
                        $('.import_success').show();
                        $('#reset').trigger('click');
                        $('#brand_data_csv').val('');
                        $('#company_data_csv').val('');
                        button.removeAttr('disabled');
                }
            });
            
            return false;
        });
        
        $('#brand_type_btn').click(function() {
            if($('#brand_type').val() == '') {
                return false;
            }
            var button = $(this);
            button.attr('disabled', 'disabled');
            var url = $(this).parents().find('form').attr( 'action' );
            
            $.ajax({
                type: "POST",
                url: url,
                data: $('#add_type').serialize(),
                dataType: 'json',
                success: function(data){
                        if(data.value != '') {
                            $('.add_success').show();
                            $('#brand_type').val('');
                            button.removeAttr('disabled');
                            $('#brand_types').append('<option value="'+data.value+'">'+data.name+'<option>');
                            $('option:selected', '#brand_types').removeAttr('selected');
                            $("#brand_types option[value='"+data.value+"']").attr('selected', 'selected');
                        }
                }
            });
            
            return false;
        });
        
    });
</script>

