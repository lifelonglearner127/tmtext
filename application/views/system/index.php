	<script src="http://code.jquery.com/ui/1.10.3/jquery-ui.js"></script>
	
	<script>
	$(function() {
		// there's the gallery and the trash
		var $gallery = $( "#gallery" ),
			$trash = $( "#trash" );
	
		// let the trash be droppable, accepting the gallery items
		$trash.droppable({
			accept: "#gallery > li",
			activeClass: "ui-state-highlight",
			drop: function( event, ui ) {
				deleteImage( ui.draggable );
				setTimeout (function(){
					$("#trash .gallery li").draggable({
						cancel: "a.ui-icon", // clicking an icon won't initiate dragging
						revert: "invalid", // when not dropped, the item will revert back to its initial position
						containment: "document",
						helper: "clone",
						cursor: "move"
					});
				
					$gallery.droppable({
						accept: "#trash .gallery li",
						activeClass: "custom-state-active",
						drop: function( event, ui ) {
							recycleImage( ui.draggable );
						}
					});
				},1000);
			}
		});
		
		// let the gallery be droppable as well, accepting items from the trash
		$gallery.sortable();

		// image deletion function
		var recycle_icon = "<a hef='#' class='ui-icon ui-icon-refresh'>x</a>";
		function deleteImage( $item ) {
			$item.fadeOut(function() {
				var $list = $( "ul", $trash ).length ?
					$( "ul", $trash ) :
					$( "<ul class='gallery ui-helper-reset'/>" ).appendTo( $trash );

				$item.find( "a.ui-icon-trash" ).remove();
				$item.append( recycle_icon ).appendTo( $list ).fadeIn(function() {
					$item
						.animate({ width: "auto" })
						.find( "img" )
							.animate({ height: "auto" });
				});
			});
		}

		// image recycle function
		var trash_icon = "<a hef='#' class='ui-icon ui-icon-trash'>x</a>";
		function recycleImage( $item ) {
			$item.fadeOut(function() {
				$item
					.find( "a.ui-icon-refresh" )
						.remove()
					.end()
					.css( "width", "auto")
					.append( trash_icon )
					.find( "img" )
						.css( "height", "auto" )
					.end()
					.appendTo( $gallery )
					.fadeIn();
			});
		}

		// resolve the icons behavior with event delegation
		$( "ul.gallery > li" ).click(function( event ) {
			var $item = $( this ),
				$target = $( event.target );

			if ( $target.is( "a.ui-icon-trash" ) ) {
				deleteImage( $item );
			} else if ( $target.is( "a.ui-icon-zoomin" ) ) {
				viewLargerImage( $target );
			} else if ( $target.is( "a.ui-icon-refresh" ) ) {
				recycleImage( $item );
			}

			return false;
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
									<ul class="span12 product_title_content gallery ui-helper-reset ui-helper-clearfix" id="gallery">
										<li><span>Channels</span><a hef="#" class="ui-icon ui-icon-trash">x</a></li>
										<li><span>Product Name</span><a hef="#" class="ui-icon ui-icon-trash">x</a></li>
										<li><span>Type</span><a hef="#" class="ui-icon ui-icon-trash">x</a></li>
										<li><span>Item</span><a hef="#" class="ui-icon ui-icon-trash">x</a></li>
										<li><span>Specs</span><a hef="#" class="ui-icon ui-icon-trash">x</a></li>
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
							<div id="trash"></div>		
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