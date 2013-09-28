<div class="tabbable">
<!--    <ul class="nav nav-tabs jq-customer-tabs">
        <li class="active"><a data-toggle="tab" href="<?php echo site_url('customer');?>"><b>Account Configuration</b></a></li>
        <?php  if (!$this->ion_auth->is_editor($this->ion_auth->get_user_id())): ?>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('customer/product_description');?>"><b>Product Description Defaults</b></a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('customer/style_guide');?>"><b>Style Guide</b></a></li>
        <?php endif; ?>
    </ul>-->
    <div class="tab-content">
        <div class="main_content_editor">
            <script>
            $(function() {
                $('head').find('title').text('Settings');
            });
            </script>
	
	
					<div class="row-fluid">
						<form class="form-horizontal" id="account_configure">
						    <div class="control-group">
							    <label class="control-label" for="customer_name">Name:</label>
							    <div class="controls">
								    <input type="text" id="customer_name" placeholder="Customer" class="span8" value="<?php echo $email; ?>">
							    </div>
						    </div>
						    <div class="control-group">
							    <label class="control-label" for="login">Login:</label>
							    <div class="controls">
								    <input type="text" id="login" placeholder="Email" class="span8" value="<?php echo $identity; ?>">
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
								    <button type="button" class="btn btn-success"><i class="icon-white icon-ok"></i>&nbsp;Save</button>
							    </div>
						    </div>
					    </form>						
					</div>
        </div>
    </div>
</div>
