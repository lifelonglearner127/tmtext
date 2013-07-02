<div class="tabbable">
    <ul class="nav nav-tabs jq-customer-tabs">
        <li class=""><a data-toggle="tab" href="<?php echo site_url('customer');?>"><b>Account Configuration</b></a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('customer/product_description');?>"><b>Product Description Defaults</b></a></li>
        <li class="active"><a data-toggle="tab" href="<?php echo site_url('customer/style_guide');?>"><b>Style Guide</b></a></li>
    </ul>
    <div class="tab-content">
        <div class="main_content_editor">
            <script>
                $(function() {
                    $('head').find('title').text('Settings');
                });
            </script>
            <script src="<?php echo base_url();?>js/styleguide.js"></script>
            
            <span class="span10">Upload Your Style Guide or Type It Into The Edit Box </span>
                  
            
            
            <div class="span4"> 
                <?php echo form_open_multipart('customer/upload_dat');?>
                        
                    <span class="btn btn-success fileinput-button">
			Upload & Save
			<i class="icon-plus icon-white"></i>
			<input id="styleupload" type="file" name="files[]" multiple>
                    </span>
                </form>
                <div id="progress" style="display:none"  class="progress progress-success progress-striped">
                    <div class="bar"></div>
		</div><div id="files"></div>
            </div>        
                    
            <span class="span4">
                <?php
                   if($this->ion_auth->is_admin($this->ion_auth->get_user_id())){
                       $selected = array();
                       if(count($customer_list) == 2){
                           array_shift($customer_list);
                           $selected = array(0);
                       }
                       echo 'Customers: '.form_dropdown('customersStyle', $customer_list, $selected, 'class="mt_10 category_list"');
                   }
                ?>
          </span>
               
            <div class="span10">
                    <div class="controls">
                            <textarea name="style_guide" class="span10 mt_10" style="height: 130px; max-width: 570px;"></textarea>
                    </div>
            </div>
            <div class="span10">
                    <div class="controls span3">
                            <button type="submit" name="saveStyle" class="btn btn-success"><i class="icon-white icon-ok"></i>&nbsp;Save</button>
                            
                    </div>
                <span class="span5" id="responseMess"></span>
            </div>
                
                
        </div>
    </div>
</div>