<script src="<?php echo base_url();?>js/tinysort.js"></script>
<div class="tabbable">
    <ul class="nav nav-tabs jq-customer-tabs">
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_accounts');?>">New Accounts</a></li>
		<li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_roles');?>">Roles</a></li>
		<li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_users');?>">Users</a></li>
        <li class="active"><a data-toggle="tab" href="<?php echo site_url('admin_customer/index');?>">Customer settings</a></li>
    </ul>
    <div class="tab-content">

	<script>
	$(function() {
		$('head').find('title').text('Customers');
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

        $('button#save_customer, #bottom_save').click(function(){
        
            if($("#sites .btn_caret_sign").text()!='[ Select Customer ]'){
            if($('input[name="customer_url"]').val()!=''){ 
               
            $.post(base_url + 'index.php/admin_customer/add_customer', {
                
                'customer_name':$("#sites .btn_caret_sign").text(),
                'customer_url': $('input[name="customer_url"]').val(),
                'logo': $('input[name="customerlogo_file"]').val()
            }, function(data){
                $(".info-message").fadeIn(1000);
                $(".info-message").html(data.message);
                $(".info-message").fadeOut(7000);
                if(data.message!="Customer was updated successfully"){
                    $('input#customer_name').val('');
                     //$('input[name="customer_url"]').val('');
                    //$('img#customer_logo').attr({'src': base_url+'img/no-logo.jpg' });
                }
                
            });
            
            }else{
                 $(".info-message").fadeIn(1000);
                 $(".info-message").html('Customer url is required');
                 $(".info-message").fadeOut(7000);
                
                
                 
            }
            }
            return false;
        });
        
    });
	</script>

					<div id="info"><?php echo $message;?></div>
                    <div class="info-message text-success"></div>
					<div class="row-fluid">
						<div class="span9">
						    <?php echo form_open("admin_customer/save", array("class"=>"form-horizontal", "id"=>"customer_settings_save")); ?>
							    <div class="control-group">
								    <p>New Customer :</p>
								    
                                                                    <div >
									    <input  style="float: left; margin-right: 5px;" type="text" id="customer_name" name="user_settings[customer_name]" class="" value="<?php // echo isset($user_settings['customer_name'])? $user_settings['customer_name']:'' ?>">
                                                                            <button id="add_new_customer" class="btn new_btn btn-primary"><i class="icon-white icon-file"></i>&nbsp;Add</button>
                                                                    </div>
							    </div>
                                                            <div class="clear-fix"></div>
                                                    
                                                    <div class="aclis">
                                                        
                                                                <div style="margin-bottom: 15px;"id="sites" class="btn-group hp_boot_drop mr_10">
                                                                    <button class="btn btn-danger btn_caret_sign" id="" onclick="return false;">[ Select Customer ]</button>
                                                                    <button class="btn btn-danger dropdown-toggle" data-toggle="dropdown">
                                                                        <span class="caret"></span>
                                                                    </button>
                                                                    <ul class="dropdown-menu">
                                                                        
                                                                        <?php foreach($customers as $key => $value) { ?>
                                                                            <li><a data-item="<?php echo $value['url']; ?>" data-value="<?php if($value['image']!='http://tmeditor.dev/img/'){echo $value['image'];}else{ echo "../../img/no-logo.jpg";} ?>" href="javascript:void(0)"><span class="<?php echo $value['value']; ?>"><?php echo $value['value']; ?></span></a></li>
                                                                        <?php } ?>
                                                                            
                                                                    </ul>
                                                                </div>
                                                           
                                                        <div class="clear-fix"></div>
                                                    </div>
                                                    
                                <div class="control-group">
                                    <label class="control-label" for="customer_name">Customer URL:</label> 
                                    <div class="controls">
                                        <input type="text" id="customer_url" name="customer_url" class="span12" value="">
                                    </div>
                                </div>
                                <div class="row-fluid">
                                    <div class="span10 admin_system_content ">
                                        <div class="controls">
                                            <img id="customer_logo" class="mt_10" src="../../img/no-logo.jpg" />
                                            <div class="clear-fix"></div><br />
                                            <span class="btn btn-success fileinput-button pull-left mr_10">
                                                Add Logo
                                                <i class="icon-plus icon-white"></i>
                                                <input id="fileupload" type="file" name="files[]" multiple>
                                            </span>
                                            <div id="progress" class="progress progress-success progress-striped">
                                                <div class="bar"></div>
                                            </div>
                                            <div id="files"></div>
                                            <input type="hidden" name="customerlogo_file" />
                                            <script>
                                                $(function () {
                                                    var url = '<?php echo site_url('admin_customer/upload_img');?>';
                                                    $('#fileupload').fileupload({
                                                        url: url,
                                                        dataType: 'json',
                                                        done: function (e, data) {
                                                            $('input[name="customerlogo_file"]').val(data.result.files[0].name);
                                                            $('img#customer_logo').attr({'src': base_url+'img/'+data.result.files[0].name });
                                                        },
                                                        progressall: function (e, data) {
                                                            var progress = parseInt(data.loaded / data.total * 100, 10);
                                                            $('#progress .bar').css(
                                                                'width',
                                                                progress + '%'
                                                            );
                                                            if (progress == 100) {
                                                            }
                                                        }
                                                    });
                                                });
                                            </script>
                                        </div>
                                    </div>
                                </div>
                                <div class="row-fluid">
                                    <div class="control-group">
                                        <div class="controls">
                                            <button id="save_customer" class="btn btn-success"><i class="icon-white icon-ok"></i>&nbsp;Save</button>
                                        </div>
                                    </div>
                                </div>
                                                            <?php 
                                                            ?>
							    <div class="control-group">
								    <label class="control-label" for="csv_directory">CSV Directory:</label>
								    <div class="controls">
									    <input type="text" id="csv_directory" name="user_settings[csv_directories]" class="span12" value="<?php echo isset($user_settings['csv_directories'])? $user_settings['csv_directories']:'/ebs/sites/client38/web48/opt/trillionmonkeys.com/tm/data' ?>">
								    </div>
							    </div>
<!-- 							    <div class="control-group">
								    <label class="control-label" for="databse">Database:</label>
								    <div class="controls">
									    <input type="text" id="databse" class="span12">
								    </div>
							    </div> -->
							    <div class="control-group">
									<label class="control-label" for="use_files">Use Files</label>
									<div class="controls">
										<?php echo form_checkbox('user_settings[use_files]', 1, (isset($user_settings['use_files'])? $user_settings['use_files']:false), 'id="use_files"');?>
									</div>
							    </div>
							    <div class="control-group">
									<label class="control-label" for="use_database">Use Database</label>
									<div class="controls">
										<?php echo form_checkbox('user_settings[use_database]', 1, (isset($user_settings['use_database'])? $user_settings['use_database']:false), 'id="use_database"');?>
									</div>
								</div>
						    	<div class="control-group">
								    <label class="control-label" for="title_length">Title length:</label>
								    <div class="controls">
									    <input type="text" id="title_length" name="user_settings[title_length]" class="span2" value="<?php  echo "40";// echo isset($user_settings['title_length'])? $user_settings['title_length']:'' ?>">
										<p class="title_max">characters max</p>
								    </div>
							    </div>
							    <div class="control-group">
								    <label class="control-label" for="description_length">Description length:</label>
								    <div class="controls">
									    <input  type="text" id="description_length" name="user_settings[description_length]" class="span2" value="<?php echo "150"; // echo isset($user_settings['description_length'])? $user_settings['description_length']:'' ?>">
										<p class="title_max">words max</p>
								    </div>
							    </div>
								<div class="control-group">
								    <label class="control-label" for="account_title">Title:</label>
								    <div class="controls">
										<ul id="gallery" class="product_title_content gallery">
											<?php
											$all_product_titles = $this->config->item('all_product_titles');

											if (isset($user_settings['product_title'])) {
												foreach($user_settings['product_title'] as $value) {
											?>
												<li><span id="<?php echo $value; ?>"><?php echo $all_product_titles[$value]; ?></span><a hef="#" class="ui-icon-trash">x</a></li>
											<?php
												}
											}
											?>
										</ul>
								    </div>
							    </div>
							    <div class="control-group">
								    <div class="controls">
									    <button id="bottom_save" type="submit" class="btn btn-success"><i class="icon-white icon-ok"></i>&nbsp;Save</button>
									    <button type="submit" class="btn ml_20">Restore Default</button>
									    <!--  <button type="submit" class="btn ml_50 btn-inverse">Delete</button> -->
								    </div>
							    </div>
						    </form>
						</div>
						<div class="span3">
							<div class="title_item_content">
<!--								<button class="btn new_btn btn-primary"><i class="icon-white icon-file"></i>&nbsp;New</button>-->
								<ul id="trash" class="product_title_content trash">
									<?php
									foreach($this->config->item('all_product_titles') as $key=>$value) {
										if (!isset($user_settings['product_title']) || !in_array($key, $user_settings['product_title'])) {
									?>
									<li><span id="<?php echo $key; ?>"><?php echo $value; ?></span><a hef="#" class="ui-icon-trash">x</a></li>
									<?php
										}
									}
									?>
								</ul>
							</div>
						</div>
					</div>
    </div>
</div>
<script>
function selectOption(){
                $(".hp_boot_drop .dropdown-menu > li > a").bind('click', function(e) {
                    var new_caret = $.trim($(this).text());
                    $("#sites .btn_caret_sign").text(new_caret);
                    $("#sites .btn_caret_sign").attr('id', $.trim($(this).data('value')));
                    var url='';
                    
                    if(new_caret!=='Select Customer'){
                        
                    $("span").each(function(){
                        if($(this).hasClass(new_caret)){
                            url=$(this).closest('a').attr('data-item');
                             var image=$(this).closest('a').attr('data-value');
                             $('#customer_url').val(url);
                             $("#customer_logo").attr('src',image);
                        }
                    })
//                      url=$("span[class='"+new_caret+"']").closest('a').attr('data-item');
//                      var image=$("span[class='"+new_caret+"']").closest('a').attr('data-value');
                      
                    }else{
                        $("#customer_logo").attr('src',"../../img/no-logo.jpg");
                        $('#customer_url').val('');
                    }
                    
                });
            }
            selectOption();
            
            
            
            
            
            $('#add_new_customer').click(function(){
                                    
                if($('#new_site').val() != ''){
                    var customerName=$('#customer_name').val();
                    $("#sites .btn_caret_sign").text(customerName);
                    $(".hp_boot_drop .dropdown-menu").append('<li><a href="javascript:void(0)" data-value="" data-item=""><span>'+customerName+'</span></a></li>');
                    selectOption();
                    
                    $(".hp_boot_drop .dropdown-menu li ").tsort('span',{order:'asc'});
                    $(".hp_boot_drop .dropdown-menu li:last").remove();                
                    $(".hp_boot_drop .dropdown-menu").prepend('<li><a data-item="" data-value="" ><span>Select Customer</span></a></li>');
                    $('#customer_name').val('');
                    $('#customer_url').val('');
                    $("#customer_logo").attr('src',"../../img/no-logo.jpg");
                    

                }
                return false;
            });
   $(document).ready(function(){
   $(".hp_boot_drop .dropdown-menu li ").tsort('span',{order:'asc'});
   
   $(".hp_boot_drop .dropdown-menu").prepend('<li><a data-item="" data-value="" href="javascript:void(0)"><span>Select Customer</span></a></li>');
   });
            
            </script>
