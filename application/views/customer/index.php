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
						<h3>Product Description Defaults:</h3>
					    <form class="form-horizontal" id="product_description">
						    <div class="control-group">
							    <label class="control-label" for="customer_name">Product Title:</label>
							    <div class="controls">
									<ul class="span12 product_title_content">
										<li><span>Channels</span><a hef="#">x</a></li>
										<li><span>Product Name</span><a hef="#">x</a></li>
										<li><span>Type</span><a hef="#">x</a></li>
										<li><span>Item</span><a hef="#">x</a></li>
										<li><span>Specs</span><a hef="#">x</a></li>
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
						<div class="title_item_content">
							<textarea placeholder="Title Item List"></textarea>
						</div>					
					</div>