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
<div class="tabbable">
  <ul class="nav nav-tabs jq-system-tabs">
	<li class=""><a data-toggle="tab" href="<?php echo site_url('system');?>">General</a></li>
	<li class="active"><a data-toggle="tab" href="<?php echo site_url('system/system_accounts');?>">New Accounts</a></li>
	<li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_roles');?>">Roles</a></li>
	<li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_users');?>">Users</a></li>
	<li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_compare');?>">Product Compare Interface</a></li>
	<li class=""><a data-toggle="tab" href="<?php echo site_url('site_crawler');?>">Site Crawler</a></li>
  </ul>
  <div class="tab-content">
    <div id="tab2" class="tab-pane active">
    	 <?php echo form_open("system/save_account_deafults", array("class"=>"form-horizontal", "id"=>"system_save_account_defaults"));?>
		<div class="row-fluid">
			<div class="span9">
				<h3>New Account Defaults:</h3>
				<div class="info-message"></div>
			    <div class="control-group">
				    <label class="control-label" for="account_title">Title:</label>
				    <div class="controls">
						<ul id="gallery" class="product_title_content gallery">
							<?php
							$all_product_titles = $this->config->item('all_product_titles');

							if (isset($settings['product_title'])) {
								foreach($settings['product_title'] as $value) {
							?>
								<li><span id="<?php echo $value; ?>"><?php echo $all_product_titles[$value]; ?></span><a hef="#" class="ui-icon-trash">x</a></li>
							<?php
								}
							}
							?>
						</ul>
				    </div>
			    </div>
				<div class="span12 ml_0">
				    <div class="control-group">
					    <label class="control-label" for="default_title">Default Title:</label>
					    <div class="controls">
						    <input type="text" id="default_title" name="settings[title_length]" class="span2" value="<?php echo isset($settings['title_length'])? $settings['title_length']:'128' ?>">
							<p class="title_max">characters max</p>
					    </div>
				    </div>
				    <div class="control-group">
					    <label class="control-label" for="description_length">Description length:</label>
					    <div class="controls">
						    <input type="text" id="description_length" name="settings[description_length]" class="span2" value="<?php echo isset($settings['description_length'])? $settings['description_length']:'150' ?>">
							<p class="title_max">words max</p>
					    </div>
				    </div>
				</div>
			</div>
			<div class="span3">
				<ul id="trash" class="product_title_content trash">
					<?php
					foreach($this->config->item('all_product_titles') as $key=>$value) {
						if (!isset($settings['product_title']) || !in_array($key, $settings['product_title'])) {
					?>
					<li><span id="<?php echo $key; ?>"><?php echo $value; ?></span><a hef="#" class="ui-icon-trash">x</a></li>
					<?php
						}
					}
					?>
				</ul>
			</div>
		</div>
		<div class="row-fluid">
			<div class="span6 offset6">
				<div class="control-group">
				    <div class="controls">
					    <button type="submit" class="btn btn-success"><i class="icon-white icon-ok"></i>&nbsp;Save</button>
					    <button type="submit" class="btn ml_20">Restore Default</button>
				    </div>
			    </div>
			</div>
		</div>
		<?php echo form_close();?>
    </div>
  </div>
</div>