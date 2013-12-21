<script src="<?php echo base_url();?>js/ajaxupload.js"></script>
<script type="text/javascript">
	$(document).ready(function() {
		$('head').find('title').text('System');

		$("#email_report_config_attach").on("change", function(e) {
			var check = $(e.target).is(':checked');
			var value = 'no';
			if(check) {
				value = 'yes';
			}
			var send_data = {
				type: 'attach',
				value: value
			};
			$("#email_report_config_attach").attr('disabled', true);
			$.post(base_url + 'index.php/system/update_home_pages_config', send_data, function(data) {
				$("#email_report_config_attach").removeAttr('disabled');
			});
		});

	});

	function updateReportConfigSender() {
		var email_pattern = /^([a-z0-9_\-]+\.)*[a-z0-9_\-]+@([a-z0-9][a-z0-9\-]*[a-z0-9]\.)+[a-z]{2,4}$/i;
		var sender = $.trim($("#email_report_config_sender").val());
		if(!email_pattern.test(sender)) {
			$("#fe_ercs").text("Incorrect email format");
	      	$("#fe_ercs").fadeOut("medium", function() {
			    $("#fe_ercs").fadeIn("medium");
		    });
		} else {
			var send_data = {
				type: 'sender',
				value: sender
			};
			$.post(base_url + 'index.php/system/update_home_pages_config', send_data, function(data) {
				$("#email_report_config_sender").val(sender);
			});
		}
		return false;
	}

	function addEmailToBatchNotifyList() {
		var email_pattern = /^([a-z0-9_\-]+\.)*[a-z0-9_\-]+@([a-z0-9][a-z0-9\-]*[a-z0-9]\.)+[a-z]{2,4}$/i;
		var rc = $.trim($("#batch_cr_notify_email").val());
		if(!email_pattern.test(rc)) {
			alert('Incorrect email format');
		} else {
			var send_data = {
				rc: rc
			};
			$.post(base_url + 'index.php/system/add_email_to_batch_notify_list', send_data, function(data) {
				console.log(data);
				if(data.status !== true) {
					alert(data.msg);
				} else {
					$("#batch_cr_notify_email").val("");
					$("#batch_cr_notify_email").blur("");
					alert("Recepient email is successfully added");
				}
			});
		}
		return false;
	}

</script>
	<div class="tabbable">
		<ul class="nav nav-tabs jq-system-tabs">
                    <li class="active"><a data-toggle="tab" href="<?php echo site_url('system');?>">General</a></li>
                    <li class=""><a data-toggle="tab" href="<?php echo site_url('system/sites_view');?>">Sites</a></li>
                    <li class=""><a data-toggle="tab" href="<?php echo site_url('site_crawler');?>">Site Crawler</a></li>
                    <li class=""><a data-toggle="tab" href="<?php echo site_url('site_crawler/instances_list');?>">Crawler Instances</a></li>
                    <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_uploadmatchurls');?>">Upload Match URLs</a></li>
                    <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_dostatsmonitor');?>">Do_stats Monitor</a></li>
                    <li class=""><a data-toggle="tab" href="<?php echo site_url('brand/import');?>">Brands</a></li>
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

				<div class="info-message"></div>

				<h3>Home Pages:</h3>
				<div class="row-fluid">
					<div class='email_rep_upload_sec'>
						<?php 
							$file = realpath(BASEPATH . "../webroot/emails_logos/$email_report_config_logo");
			                $file_size = filesize($file);
			                if($file_size === false) {
			                	$email_report_config_logo = 'default_logo.jpg';
			                }
						?>
						<img id='fileupload_emailrep_logo_holder' src="<?php echo base_url(); ?>emails_logos/<?php echo $email_report_config_logo ?>">
						<span id='fileupload_emailrep_logo' class="btn btn-success fileinput-button fileinput-button-elogo">Upload<i class="icon-plus icon-white"></i></span>
						<script>
						$(function () {
							var url = '<?php echo site_url('system/upload_email_logo');?>';
							var em_logo_btn = $("#fileupload_emailrep_logo");
						    new AjaxUpload(em_logo_btn, {
						      action: url,
						      name: 'logoemail',
						      responseType: 'json',
						      onSubmit: function() {
						      	console.log('email logo upload start');
						      },
						      onComplete: function(file, response) {
						      	console.log(response);
						      	if(response.filename == "") {
						      		alert('Internal Server Error (check out console).' + response.msg);
						      	} else {
						      		$("#fileupload_emailrep_logo_holder").attr('src', base_url + "emails_logos/" + response.filename);
						      	} 
						      }
						    });
						});
						</script>
					</div>
					<form class="form-inline" method='post' action='' enctype="multipart/form-data">
						<input type="text" id='email_report_config_sender' class="input-large" value="<?php echo $email_report_config_sender; ?>" placeholder="Email">
						<button type="submit" onclick='return updateReportConfigSender();' class="btn btn-success">Update</button>
						<p class='help-block form_error mt5' id='fe_ercs'>test</p>
					</form>
					<form class="form-inline" method='post' action='' enctype="multipart/form-data">
						<label class="checkbox">
							<?php if($email_report_config_attach == 'yes') { $checked = 'checked'; } else { $checked = ''; } ?>
							<input id='email_report_config_attach' <?php echo $checked; ?> type="checkbox">&nbsp;&nbsp;Include image attachments
						</label>
					</form>
				</div>		

				<?php echo form_open("system/save", array("class"=>"form-horizontal", "id"=>"system_save"));?>
					<h3>Original Descriptions:</h3>
					<div class="row-fluid">
						<div class="span6 admin_system_content">
							<p class="mt_40">CSV Directories:</p>
							<textarea name="settings[csv_directories]"><?php echo isset($settings['csv_directories'])? $settings['csv_directories']:'' ?></textarea>
						</div>
						<!--<div class="span6 admin_system_content">
						<div class="span6 admin_system_content extra_up">
							<p class="mt_40">Database:</p>
							<input type="text" id="database" class="mt_30"/>
						</div> -->
						<div class="span6 admin_system_content">
							<label class="control-label" for="use_files">Use Files</label>
							<div class="controls">
								<?php echo form_checkbox('settings[use_files]', 1, (isset($settings['use_files'])? $settings['use_files']:false), 'id="use_files"');?>
							</div>
							<label class="control-label" for="use_database">Use Database</label>
							<div class="controls">
								<?php echo form_checkbox('settings[use_database]', 1, (isset($settings['use_database'])? $settings['use_database']:false), 'id="use_database"');?>
							</div>
						</div>
					</div>
					<h3></h3>
					<div class="row-fluid">
						<div class="control-group">
						    <div class="controls">
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
								$(function () {
								    var url = '<?php echo site_url('system/upload_csv');?>';
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
								});
								</script>
							</div>
						</div>
					</div>
					<div class="row-fluid">
						<div class="span6 admin_system_content">
							<p class="mt_40">Tag Rules:</p>
							<textarea type="text" class='tag_rules_settings' id="tar_rules" name="settings[tag_rules_dir]"><?php echo isset($settings['tag_rules_dir'])? $settings['tag_rules_dir']:'' ?></textarea>
						</div>
					</div>
					<h3>Generator Paths:</h3>
					<div class="row-fluid">
						<div class="span6 admin_system_content">
							<p>Python script:</p>
							<input type="text" name="settings[python_cmd]" id="python_script" value="<?php echo isset($settings['python_cmd'])? $settings['python_cmd']:'' ?>"/>
							<div class="clear-fix"></div>
							<p>Java tools:</p>
							<input type="text" name="settings[java_cmd]" id="java_tool" value="<?php echo isset($settings['java_cmd'])? $settings['java_cmd']:'' ?>"/>
						</div>
						<div class="span6 admin_system_content">
							<p>Python input:</p>
							<input type="text" id="python_input" name="settings[python_input]" value="<?php echo isset($settings['python_input'])? $settings['python_input']:'' ?>"/>
							<div class="clear-fix"></div>
							<p>Java input:</p>
							<input type="text" id="java_input" name="settings[java_input]" value="<?php echo isset($settings['java_input'])? $settings['java_input']:'' ?>"/>
						</div>
					</div>
                    <h3>Assess data table:</h3>
                    <div class="row-fluid">
                        <div class="span6 admin_system_content">
                            <input type="radio" name="settings[statistics_table]" id="statistics" value="statistics" <?php if(!isset($settings['statistics_table']) or $settings['statistics_table']=="statistics"){ echo 'checked'; } ?> />
                            <p>statistics</p>
                            <div class="clear-fix"></div>
                            <input type="radio" name="settings[statistics_table]" id="statistics_new" value="statistics_new" <?php echo ($settings['statistics_table']=="statistics_new")? 'checked':'' ?>/>
                            <p>statistics_new</p>
                        </div>
                    </div>
					<div class="row-fluid">
						<h3>Description Generators:</h3>
			    		<div class="control-group">
							<label class="control-label" for="java_generator">Java Generator</label>
							<div class="controls">
								<?php echo form_checkbox('settings[java_generator]', 1, (isset($settings['java_generator'])? $settings['java_generator']:false), 'id="java_generator"');?>
							</div>
						</div>
			    		<div class="control-group">
							<label class="control-label" for="python_generator">Python Generator</label>
							<div class="controls">
								<?php echo form_checkbox('settings[python_generator]', 1, (isset($settings['python_generator'])? $settings['python_generator']:false), 'id="python_generator"');?>
							</div>
						</div>
					</div>
					<h3>Website titles:</h3>
					<div class="row-fluid">
						<div class="span6 admin_system_content">
							<p>Site name:</p>
							<input type="text" name="settings[site_name]" value="<?php echo isset($settings['site_name'])? $settings['site_name']:'' ?>" id="site_name"/>
							<div class="clear-fix"></div>
							<p>Company name:</p>
							<input type="text" name="settings[company_name]" value="<?php echo isset($settings['company_name'])? $settings['company_name']:'' ; ?>" id="company_name"/>
						</div>
					</div>
					<div class="row-fluid">
					    <div class="control-group">
						    <div class="controls">
							    <button type="submit" class="btn btn-success"><i class="icon-white icon-ok"></i>&nbsp;Save</button>
							    <button type="submit" class="btn ml_20">Restore Default</button>
						    </div>
					    </div>
					</div>
			</div>
		</div>
	</div>

	<?php echo form_close();?>

	<!-- ADD ADMIN NOTIFICATORS (START) -->
	<h3>New Batch Creation Notifications List:</h3>
	<form id='batch_cr_notify_form' method='post' action='' enctype="multipart/form-data">
		<div class="row-fluid">
			<div class="span6 admin_system_content">
				<p>Email:</p>
				<input type="text" name="batch_cr_notify_email" id="batch_cr_notify_email" placeholder="Email..."/>
				<div class="clear-fix"></div>
			</div>
		</div>
		<div class="row-fluid">
		    <div class="control-group">
			    <div class="controls">
				    <button type="submit" onclick="return addEmailToBatchNotifyList()" class="btn btn-success"><i class="icon-white icon-ok"></i>&nbsp;Add</button>
				    <button type="button" class="btn ml_20">Show Recepients</button>
			    </div>
		    </div>
		</div>
	</form>
	<!-- ADD ADMIN NOTIFICATORS (END) -->
