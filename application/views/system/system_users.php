							<div class="tabbable">
				              <ul class="nav nav-tabs">
				                <li class=""><a data-toggle="tab" href="index">General</a></li>
				                <li class=""><a data-toggle="tab" href="system_accounts">New Accounts</a></li>
				                <li class=""><a data-toggle="tab" href="system_roles">Roles</a></li>
				                <li class="active"><a data-toggle="tab" href="system_users">Users</a></li>
				              </ul>
							  <div class="tab-content">
				                <div id="tab4" class="tab-pane">
									<div class="row-fluid">
										<div class="span9 admin_system_content">
											<p>Name :</p>
											<input type="text" id="user_name" placeholder="Name">
											<div class="clear-fix"></div>
										</div>
										<div class="span9 admin_system_content">
											<p>Email :</p>
											<input type="text" id="user_mail" placeholder="Email">
											<div class="clear-fix"></div>
										</div>
										<div class="span9 admin_system_content">
											<p>Password :</p>
											<input type="text" id="user_password" placeholder="Password">
											<div class="clear-fix"></div>
										</div>
										<div class="span9 admin_system_content aclist">
											<p>Customers :</p>
											<input class="margin-none" type="text" id="user_customerss" onclick="edit_own();" readonly="readonly"/>

											<select id="foo" multiple="multiple" onchange="select_s();" onblur="disappear_own(this);"> 
												<option>Walmart</option>
												<option>Sears</option>
												<option>Staples</option>
											</select>
											<div class="clear-fix"></div>
										</div>
										<div class="span9 admin_system_content">
											<p>Role :</p>
											<select id="user_role"> 
												<option>Editor</option>
												<option>1</option>
												<option>1</option>
											</select>
											<div class="clear-fix"></div>
										</div>
										<div class="span9 admin_system_content">
											<p>Active :</p>
											<input type="checkbox" id="user_active">
											<div class="clear-fix"></div>
										</div>
									</div>
									<div class="row-fluid">
									    <div class="control-group">
										    <div class="controls align_center">
												<button class="btn new_btn btn-primary"><i class="icon-white icon-file"></i>&nbsp;New</button>
											    <button class="btn btn-success" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Update</button>
										    </div>
									    </div>
									</div>
				                </div>
				              </div>
				            </div>
