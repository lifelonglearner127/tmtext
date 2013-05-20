	<script src="http://code.jquery.com/ui/1.10.3/jquery-ui.js"></script>
	<style type="text/css">
	.product_title_content li a {
	      float: right;
	      margin: 0 0 0 -5px;
	      padding: 5px;
	  }
	  .gallery li a {
	      float: right;
	      margin: 0 0 0 -16px;
	      padding: 5px;
	      position: absolute;
	  }
	 </style>
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
		    $(this).closest("li").fadeOut(20);
		    $(this).closest("li").fadeOut(function(){
		     $(this).closest("li").appendTo("#trash").fadeIn(20);
		    });
		   }else if($(this).closest("ul").attr('Id')=='trash'){
		    $(this).closest("li").fadeOut(20);
		    $(this).closest("li").fadeOut(function(){
		     $(this).closest("li").appendTo("#gallery").fadeIn(20);
		    });
		   }


		 });
		});
	</script>
							<div class="tabbable">
				              <ul class="nav nav-tabs">
								<li class=""><a data-toggle="tab" href="<?php echo site_url('system');?>">General</a></li>
								<li class="active"><a data-toggle="tab" href="<?php echo site_url('system/system_accounts');?>">New Accounts</a></li>
								<li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_roles');?>">Roles</a></li>
								<li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_users');?>">Users</a></li>
				              </ul>
				              <div class="tab-content">
				                <div id="tab2" class="tab-pane">
									<div class="row-fluid">
										<div class="span9">
											<h3>New Account Defaults:</h3>
										    <!-- form class="form-horizontal" id="product_description"-->
										    <div class="control-group">
											    <label for="account_title" class="control-label">Title:</label>
											    <div class="controls">
													<ul class="product_title_content gallery ui-sortable" id="gallery">
														<li><span>Channels</span><a class="ui-icon-trash" href="#">x</a></li>
														<li><span>Type</span><a class="ui-icon-trash" href="#">x</a></li>
														<li style="" class=""><span>Product Name</span><a class="ui-icon-trash" href="#">x</a></li>
														<li><span>Item</span><a class="ui-icon-trash" href="#">x</a></li>
													</ul>
											    </div>
										    </div>
											<div class="span12 ml_0">
											    <div class="control-group">
												    <label for="default_title" class="control-label">Default Title:</label>
												    <div class="controls">
													    <input type="text" class="span2" id="default_title">
														<p class="title_max">characters max</p>
												    </div>
											    </div>
											    <div class="control-group">
												    <label for="description_length" class="control-label">Description length:</label>
												    <div class="controls">
													    <input type="text" class="span2" id="description_length">
														<p class="title_max">words max</p>
												    </div>
											    </div>
											</div>
										</div>
										<div class="span3">
											<ul class="product_title_content trash ui-sortable" id="trash">
											<li style="" class=""><span>Specs</span><a class="ui-icon-trash" href="#">x</a></li></ul>
										</div>
									</div>
				                </div>
				              </div>
				            </div>




