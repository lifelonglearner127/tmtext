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
	
	
					<div class="row-fluid">
						<h3>Account Configuration:</h3>
					    <form class="form-horizontal" id="account_configure">
						    <div class="control-group">
							    <label class="control-label" for="customer_name">Customer name:</label>
							    <div class="controls">
								    <input type="text" id="customer_name" placeholder="Customer" class="span8">
							    </div>
						    </div>
						    <div class="control-group">
							    <label class="control-label" for="login">Login:</label>
							    <div class="controls">
								    <input type="password" id="login" placeholder="Email" class="span8">
							    </div>
						    </div>
						    <div class="control-group">
							    <label class="control-label" for="password">Password:</label>
							    <div class="controls">
								    <input type="password" id="password" placeholder="Password" class="span4">
								    <input type="password" id="confirm_password" placeholder="Confirm Password" class="span4">
							    </div>
						    </div>
						    <div class="control-group">
							    <div class="controls">
								    <button type="submit" class="btn btn-danger"><i class="icon-white icon-ok"></i>&nbsp;Save</button>
							    </div>
						    </div>
					    </form>						
					</div>
					<div class="row-fluid">
						<div class="span9">
							<h3>Product Description Defaults:</h3>
						    <form class="form-horizontal" id="product_description">
							    <div class="control-group">
								    <label class="control-label" for="customer_name">Product Title:</label>
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
							    <div class="control-group">
								    <label class="control-label" for="login">Title length:</label>
								    <div class="controls">
									    <input type="text" id="login" class="span2">
										<p class="title_max">characters max</p>
								    </div>
							    </div>
							    <div class="control-group">
								    <label class="control-label" for="password">Description length:</label>
								    <div class="controls">
									    <input type="text" id="login" class="span2">
										<p class="title_max">words max</p>
								    </div>
							    </div>
							    <div class="control-group">
								    <div class="controls">
									    <button type="submit" class="btn btn-danger"><i class="icon-white icon-ok"></i>&nbsp;Save</button>
									    <button type="submit" class="btn ml_20">Restore Default</button>
								    </div>
							    </div>
						    </form>	
						</div>
						<div class="span3">
							<div id="trash"></div>		
						</div>			
					</div>