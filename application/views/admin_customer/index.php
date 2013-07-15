<div class="tabbable">
    <ul class="nav nav-tabs jq-customer-tabs">
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_accounts');?>">New Accounts</a></li>
		<li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_roles');?>">Roles</a></li>
		<li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_users');?>">Users</a></li>
        <li class="active"><a data-toggle="tab" href="<?php echo site_url('admin_customer/index');?>">Customer settings</a></li>
    </ul>
    <div class="tab-content">

	<script src="http://code.jquery.com/ui/1.10.3/jquery-ui.js"></script>

	<script>
	$(function() {
		$('head').find('title').text('Customers');
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
					<div class="row-fluid">
						<div class="span9">
						    <?php echo form_open("admin_customer/save", array("class"=>"form-horizontal", "id"=>"customer_settings_save")); ?>
							    <div class="control-group">
								    <label class="control-label" for="customer_name">Customer name:</label>
								    <div class="controls">
									    <input type="text" id="customer_name" name="user_settings[customer_name]" class="span12" value="<?php echo isset($user_settings['customer_name'])? $user_settings['customer_name']:'' ?>">
								    </div>
							    </div>
                                <div class="control-group">
                                    <label class="control-label" for="customer_name">Customer url:</label>
                                    <div class="controls">
                                        <input type="text" id="customer_url" name="customer_url" class="span12" value="">
                                    </div>
                                </div>
                                <div class="row-fluid">
                                    <div class="span6 admin_system_content">
                                        <div class="controls">
                                    <span class="btn btn-success fileinput-button">
                                        Add Logo
                                        <i class="icon-plus icon-white"></i>
                                        <input id="fileupload" type="file" name="files[]" multiple>
                                    </span>
                                            <div id="progress" class="progress progress-success progress-striped">
                                                <div class="bar"></div>
                                            </div>
                                            <div id="files"></div>
                                            <script>
                                                $(function () {
                                                    var url = '<?php echo site_url('admin_customer/upload_csv');?>';
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
                                                                $('#upload_logo').trigger('click');
                                                            }
                                                        }
                                                    });
                                                });
                                            </script>
                                        </div>
                                    </div>
                                </div>
                                <div class="row-fluid">
                                    <div class="control-group">
                                        <div class="controls">
                                            <button id="upload_logo" class="btn btn-success"><i class="icon-white icon-ok"></i>&nbsp;Upload</button>
                                        </div>
                                    </div>
                                </div>
							    <div class="control-group">
								    <label class="control-label" for="csv_directory">CSV Directory:</label>
								    <div class="controls">
									    <input type="text" id="csv_directory" name="user_settings[csv_directories]" class="span12" value="<?php echo isset($user_settings['csv_directories'])? $user_settings['csv_directories']:'' ?>">
								    </div>
							    </div>
<!-- 							    <div class="control-group">
								    <label class="control-label" for="databse">Database:</label>
								    <div class="controls">
									    <input type="text" id="databse" class="span12">
								    </div>
							    </div> -->
							    <div class="control-group">
									<label class="control-label" for="use_files">Use Files</label>
									<div class="controls">
										<?php echo form_checkbox('user_settings[use_files]', 1, (isset($user_settings['use_files'])? $user_settings['use_files']:false), 'id="use_files"');?>
									</div>
							    </div>
							    <div class="control-group">
									<label class="control-label" for="use_database">Use Database</label>
									<div class="controls">
										<?php echo form_checkbox('user_settings[use_database]', 1, (isset($user_settings['use_database'])? $user_settings['use_database']:false), 'id="use_database"');?>
									</div>
								</div>
						    	<div class="control-group">
								    <label class="control-label" for="title_length">Title length:</label>
								    <div class="controls">
									    <input type="text" id="title_length" name="user_settings[title_length]" class="span2" value="<?php echo isset($user_settings['title_length'])? $user_settings['title_length']:'' ?>">
										<p class="title_max">characters max</p>
								    </div>
							    </div>
							    <div class="control-group">
								    <label class="control-label" for="description_length">Description length:</label>
								    <div class="controls">
									    <input type="text" id="description_length" name="user_settings[description_length]" class="span2" value="<?php echo isset($user_settings['description_length'])? $user_settings['description_length']:'' ?>">
										<p class="title_max">words max</p>
								    </div>
							    </div>
								<div class="control-group">
								    <label class="control-label" for="account_title">Title:</label>
								    <div class="controls">
										<ul id="gallery" class="product_title_content gallery">
											<?php
											$all_product_titles = $this->config->item('all_product_titles');

											if (isset($user_settings['product_title'])) {
												foreach($user_settings['product_title'] as $value) {
											?>
												<li><span id="<?php echo $value; ?>"><?php echo $all_product_titles[$value]; ?></span><a hef="#" class="ui-icon-trash">x</a></li>
											<?php
												}
											}
											?>
										</ul>
								    </div>
							    </div>
							    <div class="control-group">
								    <div class="controls">
									    <button type="submit" class="btn btn-success"><i class="icon-white icon-ok"></i>&nbsp;Save</button>
									    <button type="submit" class="btn ml_20">Restore Default</button>
									    <!--  <button type="submit" class="btn ml_50 btn-inverse">Delete</button> -->
								    </div>
							    </div>
						    </form>
						</div>
						<div class="span3">
							<div class="title_item_content">
								<button class="btn new_btn btn-primary"><i class="icon-white icon-file"></i>&nbsp;New</button>
								<ul id="trash" class="product_title_content trash">
									<?php
									foreach($this->config->item('all_product_titles') as $key=>$value) {
										if (!isset($user_settings['product_title']) || !in_array($key, $user_settings['product_title'])) {
									?>
									<li><span id="<?php echo $key; ?>"><?php echo $value; ?></span><a hef="#" class="ui-icon-trash">x</a></li>
									<?php
										}
									}
									?>
								</ul>
							</div>
						</div>
					</div>
    </div>
</div>