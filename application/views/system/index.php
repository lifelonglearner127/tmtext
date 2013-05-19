	<script src="http://code.jquery.com/ui/1.10.3/jquery-ui.js"></script>

	<script>
	$(function() {
		// there's the gallery and the trash
		var $gallery = $( "#gallery" ),
			$trash = $( "#trash" );

		$( "#gallery, #trash" ).sortable({
			connectWith: ".product_title_content",
			revert: "invalid",
			cursor: "move"
		}).disableSelection();

		// resolve the icons behavior with event delegation
		$( "ul.product_title_content > li > a" ).click(function( event ) {
			var $item = $( this ),
				$target = $( event.target );

			if($(this).closest("ul").attr('Id')=='gallery'){
				$(this).closest("li").fadeOut(function(){
					$(this).closest("li").appendTo("#trash").fadeIn();
				});
			}else if($(this).closest("ul").attr('Id')=='trash'){
				$(this).closest("li").fadeOut(function(){
					$(this).closest("li").appendTo("#gallery").fadeIn();
				});
			}
		});
	});
	</script>

				<div id="info"><?php echo $message;?></div>
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
							<input type="text" id="python_input"/>
							<div class="clear-fix"></div>
							<p>Java input:</p>
							<input type="text" id="java_input"/>
						</div>
					</div>
					<div class="row-fluid">
						<div class="span9">
							<h3>New Account Defaults:</h3>
						    <!-- form class="form-horizontal" id="product_description"-->
						    <div class="control-group">
							    <label class="control-label" for="account_title">Title:</label>
							    <div class="controls">
									<ul id="gallery" class="product_title_content gallery">
										<li><span>Channels</span><a hef="#" class="ui-icon-trash">x</a></li>
										<li><span>Product Name</span><a hef="#" class="ui-icon-trash">x</a></li>
										<li><span>Type</span><a hef="#" class="ui-icon-trash">x</a></li>
										<li><span>Item</span><a hef="#" class="ui-icon-trash">x</a></li>
										<li><span>Specs</span><a hef="#" class="ui-icon-trash">x</a></li>
									</ul>
							    </div>
						    </div>
							<div class="span12 ml_0">
							    <div class="control-group">
								    <label class="control-label" for="default_title">Default Title:</label>
								    <div class="controls">
									    <input type="text" id="default_title" class="span2">
										<p class="title_max">characters max</p>
								    </div>
							    </div>
							    <div class="control-group">
								    <label class="control-label" for="description_length">Description length:</label>
								    <div class="controls">
									    <input type="text" id="description_length" class="span2">
										<p class="title_max">words max</p>
								    </div>
							    </div>
							</div>
						</div>
						<div class="span3">
							<ul id="trash" class="product_title_content trash">
							</ul>
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


				    <?php echo form_close();?>