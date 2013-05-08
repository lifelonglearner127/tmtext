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
	
	
					<div class="row-fluid">
						<div class="span9">
						    <form class="form-horizontal" id="product_description">
							    <div class="control-group">
								    <label class="control-label" for="customer_name">Customer name:</label>
								    <div class="controls">
									    <input type="text" id="customer_name" class="span12">
								    </div>
							    </div>
							    <div class="control-group">
								    <label class="control-label" for="csv_directory">CSV Directory:</label>
								    <div class="controls">
									    <input type="text" id="csv_directory" class="span12">
								    </div>
							    </div>
							    <div class="control-group">
								    <label class="control-label" for="databse">Database:</label>
								    <div class="controls">
									    <input type="text" id="databse" class="span12">
								    </div>
							    </div>
						    	<div class="control-group">
								    <label class="control-label" for="title_length">Title length:</label>
								    <div class="controls">
									    <input type="text" id="title_length" class="span2">
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
							    <div class="control-group">
								    <div class="controls">
									    <button type="submit" class="btn btn-danger"><i class="icon-white icon-ok"></i>&nbsp;Save</button>
									    <button type="submit" class="btn ml_20">Restore Default</button>
									    <button type="submit" class="btn ml_50 btn-inverse">Delete</button>
								    </div>
							    </div>
						    </form>	
						</div>
						<div class="span3">
							<div class="title_item_content">
								<button class="btn new_btn btn-primary"><i class="icon-white icon-file"></i>&nbsp;New</button>
								<ul id="trash" class="product_title_content trash">
								</ul>
							</div>	
						</div>				
					</div>