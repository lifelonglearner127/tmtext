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
                            <?php echo form_open("brand/save", array("class"=>"form-horizontal", "id"=>"brand_data_save"));?>
					<h3>Import Brand Data:</h3>
                                        <div class="row-fluid">
                                            <div class="span3">
                                                <select id="brand_types" name="brand_types">
                                                    <option>Retail</option>
                                                    <option>CPG</option>
                                                </select>
                                                <input type="hidden" name="brand_data_csv" id="brand_data_csv" value="" />
                                            </div>
                                            <div class="span3">
                                                <span class="btn btn-success fileinput-button">
                                                        Import
                                                        <i class="icon-plus icon-white"></i>
                                                        <input id="fileupload" type="file" name="fileupload">
                                                </span>
                                                <div id="progress" class="progress progress-success progress-striped">
                                                        <div class="bar"></div>
                                                </div>
                                                <div id="files"></div>
                                                <script type="text/javascript">
                                                $(function () {
                                                    var url = '<?php echo site_url('brand/upload_csv');?>';
                                                    $('#fileupload').fileupload({
                                                        url: url,
                                                        dataType: 'json',
                                                        done: function (e, data) {
                                                            $.each(data.result.files, function (index, file) {
                                                                if (file.error == undefined) {
                                                                        $('<p/>').text(file.name).appendTo('#files');
                                                                        $('#brand_data_csv').val(file.name);
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
                                                                    var url = $(this).parents().find('form').attr( 'action' ).replace('save', 'csv_import');
                                                                    $.get(url, function(data) {
                                                                            $('#info').html(data.message);
                                                                            }, 'json');
//                                                                    $('#brand_data_save').trigger('submit');
                                                                }
                                                        }
                                                    });
                                                });
                                                </script>
                                            </div>
                                        </div>
                            <?php echo form_close();?>
			</div>
		</div>
	</div>

