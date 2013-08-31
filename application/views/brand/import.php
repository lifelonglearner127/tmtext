<div class="tabbable">
        <ul class="nav nav-tabs jq-system-tabs">
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system');?>">General</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/sites_view');?>">Sites</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('site_crawler');?>">Site Crawler</a></li>
            <li class="active"><a data-toggle="tab" href="<?php echo site_url('brand/import');?>">Brands</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/batch_review');?>">Batch Review</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_compare');?>">Product Compare</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_productsmatch');?>">Product Match</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_reports');?>">Reports</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_logins');?>">Logins</a></li>
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
                                            <option value="Retail">Retail</option>
                                            <option value="CPG">CPG</option>
                                        </select>
                                        <input type="hidden" name="brand_data_csv" id="brand_data_csv" value="" />
                                        <input type="hidden" name="company_data_csv" id="company_data_csv" value="" />
                                    </div>
                                    <div class="clearfix"></div>
                                    <div class="span4" style="margin-left:0px;">
                                        <h4>Upload Brand Data CSV:</h4>
                                    </div>
                                    <div class="span3">
                                        <span class="btn btn-success fileinput-button">
                                                Upload
                                                <i class="icon-plus icon-white"></i>
                                                <input id="fileupload" type="file" name="fileupload">
                                        </span>

                                    </div>
                                    <div class="clearfix"></div>
                                    <div class="span4" style="margin-left:0px;">
                                        <h4>Upload Company Data CSV:</h4>
                                    </div>
                                    <div class="span3">
                                        <span class="btn btn-success fileinput-button">
                                                Upload
                                                <i class="icon-plus icon-white"></i>
                                                <input id="fileupload_company" type="file" name="fileupload_company">
                                        </span>
                                    </div>
                                    <div class="clearfix"></div>
                                    <div id="progress" class="progress progress-success progress-striped">
                                                <div class="bar"></div>
                                    </div>
                                    <div id="files"></div>
                                    <div class="clearfix"></div>
                                    <div class=""><button id="brand_csv_import" class="btn btn-success"><i class="icon-white icon-ok"></i>&nbsp;Import</button></div>
                                </div>
                    <?php echo form_close();?>
                </div>
        </div>
</div>
<script type="text/javascript">
    $(function () {
        var url = '<?php echo site_url('brand/csv_upload');?>';
        $('#fileupload, #fileupload_company').fileupload({
            url: url,
            dataType: 'json',
            done: function (e, data) {
                
                if(typeof data.result.fileupload_company != 'undefined') {
                    $.each(data.result.fileupload_company, function (index, file) {
                        if (file.error == undefined) {
                                $('<p/>').text(file.name).appendTo('#files');
                                $('#company_data_csv').val(file.name);
                        }
                    });
                } else {
                    $.each(data.result.fileupload, function (index, file) {
                        if (file.error == undefined) {
                                $('<p/>').text(file.name).appendTo('#files');
                                $('#brand_data_csv').val(file.name);
                        }
                    });
                }
                
            },
            progressall: function (e, data) {
                var progress = parseInt(data.loaded / data.total * 100, 10);
                $('#progress .bar').css(
                    'width',
                    progress + '%'
                );
                if (progress == 100) {
                    //$('#brand_data_save').trigger('submit');
                }
            }
        });
        
        $('#brand_csv_import').click(function() {
            var url = $(this).parents().find('form').attr( 'action' ).replace('save', 'csv_import');
            
            $.ajax({
                type: "POST",
                url: url,
                data: $('#brand_data_save').serialize(),
                dataType: 'json',
                success: function(data){
                        alert('success');
                }
            });
            return false;
        });
        
    });
</script>

