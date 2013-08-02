							<div class="tabbable">
                                <ul class="nav nav-tabs jq-system-tabs">
                                    <!--li class=""><a data-toggle="tab" href="<?php echo site_url('system');?>">General</a></li-->
                                    <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_accounts');?>">New Accounts</a></li>
                                    <li class="active"><a data-toggle="tab" href="<?php echo site_url('system/system_roles');?>">Roles</a></li>
                                    <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_users');?>">Users</a></li>
                                    <li class=""><a data-toggle="tab" href="<?php echo site_url('admin_customer/index');?>">Customer settings</a></li>
                                </ul>
				              <div class="tab-content">
				                <div id="tab3" class="tab-pane active">
									<h4> TABS DISPLAYED</h4>
									<div class="info-message"></div>
								<?php echo form_open("system/save_roles", array("class"=>"form-horizontal", "id"=>"system_save_roles"));?>
									<div class="row-fluid">
										<div class="span4 admin_system_content">
											<p>ROLE</p>
											<div class="clear-fix"></div>
											<?php
											foreach ($user_groups as $user_group) {	?>
												<p><?php echo $user_group->description;?></p>
												<div class="clear-fix"></div>
											<?php
												}
											 ?>
										</div>
                                        <div class="span1 admin_system_content">
                                            <p>Batches</p>
                                            <div class="clear-fix"></div>
                                            <?php
                                            foreach ($user_groups as $user_group) {	?>
                                                <input type="checkbox" name="batches_<?php echo $user_group->id;?>" <?php if(isset($checked[$user_group->id]['batches'])){print 'checked';}?> value="1"/>
                                                <div class="clear-fix"></div>
                                            <?php
                                            }
                                            ?>
                                        </div>
                                        <div class="span1 admin_system_content" style="width:85px;">
                                            <p>CI</p>
                                            <div class="clear-fix"></div>
                                            <?php
                                            foreach ($user_groups as $user_group) {	?>
                                                <input type="checkbox" name="measure_<?php echo $user_group->id;?>" <?php if(isset($checked[$user_group->id]['measure'])){print 'checked';}?> value="1"/>
                                                <div class="clear-fix"></div>
                                            <?php
                                            }
                                            ?>
                                        </div>
                                        <div class="span1 admin_system_content">
                                            <p>Assess</p>
                                            <div class="clear-fix"></div>
                                            <?php
                                            foreach ($user_groups as $user_group) {	?>
                                                <input type="checkbox" name="assess_<?php echo $user_group->id;?>" <?php if(isset($checked[$user_group->id]['assess'])){print 'checked';}?> value="1"/>
                                                <div class="clear-fix"></div>
                                            <?php
                                            }
                                            ?>
                                        </div>
										<div class="span1 admin_system_content">
											<p>R&E</p>
											<div class="clear-fix"></div>
											<?php
											foreach ($user_groups as $user_group) {	?>
												<input type="checkbox" name="research_<?php echo $user_group->id;?>" <?php if(isset($checked[$user_group->id]['research'])){print 'checked';}?> value="1"/>
												<div class="clear-fix"></div>
											<?php
												}
											 ?>
										</div>

                                        <!--div class="span1 admin_system_content">
                                            <p>Job Board</p>
                                            <div class="clear-fix"></div>
                                            <?php
                                            foreach ($user_groups as $user_group) {	?>
                                                <input type="checkbox" name="job_board_<?php echo $user_group->id;?>" <?php if(isset($checked[$user_group->id]['job_board'])){print 'checked';}?> value="1"/>
                                                <div class="clear-fix"></div>
                                            <?php
                                            }
                                            ?>
                                        </div-->
										<div class="span1 admin_system_content">
											<p>Settings</p>
											<div class="clear-fix"></div>
											<?php
											foreach ($user_groups as $user_group) {	?>
												<input type="checkbox" name="customer_<?php echo $user_group->id;?>" <?php if(isset($checked[$user_group->id]['customer'])){print 'checked';}?> value="1"/>
												<div class="clear-fix"></div>
											<?php
												}
											 ?>
										</div>
                                        <div class="span1 admin_system_content">
                                            <p>Default</p>
                                            <div class="clear-fix"></div>
                                            <?php
                                            foreach ($user_groups as $user_group) {	?>
                                                <select name="default_<?php echo $user_group->id;?>" class="system_drop">
                                                    <?php foreach($checked_controllers as $checked_controller){ ?>
                                                        <option value="<?php echo $checked_controller; ?>"
                                                            <?php if(isset($checked[$user_group->id]['default_controller']) && $checked[$user_group->id]['default_controller']==$checked_controller){print 'selected';}?>>
                                                            <?php
                                                                if($checked_controller=='editor'){
                                                                    echo 'Create';
                                                                } else if($checked_controller=='batches'){
                                                                    echo 'Batches';
                                                                } else if($checked_controller=='measure'){
                                                                    echo 'CI';
                                                                } else if($checked_controller=='assess'){
                                                                    echo 'Assess';
                                                                } else if($checked_controller=='research'){
                                                                    echo 'R&E';
                                                                } else if($checked_controller=='customer'){
                                                                    echo 'Settings';
                                                                } else if($checked_controller=='job_board'){
                                                                    echo 'Job Board';
                                                                }
                                                            ?>
                                                        </option>
                                                    <?php } ?>

                                                </select>
                                                <div class="clear-fix mt_5"></div>
                                            <?php
                                            }
                                            ?>
                                        </div>
									</div>

									<div class="align_center">
										<div class="clear-fix"></div>
										<button class="btn btn-success" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Save</button>
									</div>
								<?php echo form_close();?>
								</div>

				              </div>
				            </div>
