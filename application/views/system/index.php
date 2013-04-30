					<h3>Original Descriptions:</h3>
					<div class="row-fluid">
						<div class="span6 admin_system_content">
							<p class="mt_40">CSV Directories:</p>
							<textarea></textarea>
						</div>
						<div class="span6 admin_system_content">
							<p class="mt_40">Database:</p>
							<input type="text" id="database" class="mt_40"/>
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
						<h3>New Account Defaults:</h3>
					    <form class="form-horizontal" id="product_description">
						    <div class="control-group">
							    <label class="control-label" for="account_title">Title:</label>
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