<?php
// $menu = array(
//     array('controller' => 'research', 'name' => 'Research & Edit'),
// 	array('controller' => 'editor', 'name' => 'Create'),
//     array('controller' => 'validate', 'name' => 'Validate'),
//     array('controller' => 'measure', 'name' => 'Analysis'),
// 	array('controller' => 'customer', 'name' => 'Settings'),
// );

$menu = array(
//    array('controller' => 'batches', 'name' => 'Batches'),
    array('controller' => 'measure', 'name' => 'COMPETITIVE<br /><span>RESEARCH</span>'),
    array('controller' => 'assess', 'name' => '<span>REPORTS</span>'),
    array('controller' => 'research', 'name' => '<span>EDIT</span>'),
    array('controller' => 'brand', 'name' => '<span>SOCIAL</span>'),
    //array('controller' => 'editor', 'name' => 'Create'),
    //array('controller' => 'validate', 'name' => 'Validate'),
	array('controller' => 'customer', 'name' => '<span>SETTINGS</span>'),
);
$info = $this->ion_auth->get_user_data();
$sub_menu = array(
    array('controller' => 'system', 'name' => 'System'),
    array('controller' => 'admin_customer', 'name' => 'Accounts'),
    /*array('controller' => 'admin_editor', 'name' => 'Editors'),*/
    array('controller' => 'admin_tag_editor', 'name' => 'Tag Editor'),
    /*array('controller' => 'site_crawler', 'name' => 'Site Crawler'),*/
    array('controller' => 'job_board', 'name' => 'Job Board'),
);
?>
<?php if (!empty($menu)) {?>
<ul class="left_nav_content menu ">
<?php foreach ($menu as $item) {?>
					<?php if($this->ion_auth->check_user_permission($item['controller'])){ ?>

					<li<?php echo ($this->router->class==$item['controller']) ? " class=\"active\"":"";?>><a class="jq-<?=$item['controller']?>" href="<?php echo site_url($item['controller']);?>"><?php echo $item['name'];?></a></li>
					<?php } ?>
<?php } ?>
                <li>
                    <a href="#"><span><?php echo $info['username']; ?></span></a>
                    
                   <?php  if (!empty($sub_menu)) {?>
                        <ul class="sub_menu">
                           <?php if ($this->ion_auth->is_admin($this->ion_auth->get_user_id())) {
                             foreach ($sub_menu as $sub_item) {?>
                                <li<?php echo ($this->router->class==$sub_item['controller']) ? " class=\"active\"":"";?>><a href="<?php echo site_url($sub_item['controller']);?>"><span><?php echo $sub_item['name'];?></span></a></li>
                           <?php }} ?>
                            <li><a href="<?php echo site_url('auth/logout');?>">LOG OUT</a></li>
                        </ul>
                   <?php } ?>
                </li>
				</ul>
<?php } ?>
