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
	
	
				<?php echo form_open("system/save", array("class"=>"form-horizontal", "id"=>"product_description"));?>
					<h3>Original Descriptions:</h3>
					<div class="row-fluid">
						<div class="span6 admin_system_content">
							<p class="mt_40">CSV Directories:</p>
							<textarea></textarea>
						</div>
						<div class="span6 admin_system_content">
							<p class="mt_40">Database:</p>
							<input type="text" id="database" class="mt_30"/>
						</div>
					</div>
					<h3>Generator Paths:</h3>
					<div class="row-fluid">
						<div class="span6 admin_system_content">
							<p>Python script:</p>
							<input type="text" id="python_script"/>
							<div class="clear-fix"></div>
							<p>Java tools:</p>
							<input type="text" id="java_tool"/>
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
					    <?php foreach ($this->config->item('generators') as $key => $generator) {?>
				    		<div class="control-group">
								<label class="control-label" for="java_generator"><?php echo $generator[0];?></label>
								<div class="controls">
									<?php echo form_checkbox($generator[1], 1, $generator[2], 'id="'.$generator[1].'"'.(($generator[1]=='python_generator1')?' disabled':''));?>
								</div>
							</div>
						<?php } ?>
						    <div class="control-group">
							    <div class="controls">
								    <button type="submit" class="btn btn-danger"><i class="icon-white icon-ok"></i>&nbsp;Save</button>
								    <button type="submit" class="btn ml_20">Restore Default</button>
							    </div>
						    </div>
					</div>
				    <?php echo form_close();?>