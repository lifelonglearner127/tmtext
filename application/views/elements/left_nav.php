<?php
// $menu = array(
//     array('controller' => 'research', 'name' => 'Research & Edit'),
// 	array('controller' => 'editor', 'name' => 'Create'),
//     array('controller' => 'validate', 'name' => 'Validate'),
//     array('controller' => 'measure', 'name' => 'Analysis'),
// 	array('controller' => 'customer', 'name' => 'Settings'),
// );

$menu = array(
    //array('controller' => 'batches', 'name' => 'Batches'),
    array('controller' => 'assess', 'name' => '<span>REPORTS</span>'),
    array('controller' => 'measure', 'name' => 'COMPETITIVE<br /><span>RESEARCH</span>'),
    array('controller' => 'research', 'name' => '<span>EDIT</span>'),
    array('controller' => 'brand', 'name' => '<span>SOCIAL</span>'),
    //array('controller' => 'editor', 'name' => 'Create'),
    //array('controller' => 'validate', 'name' => 'Validate'),
);
$info = $this->ion_auth->get_user_data();
$is_admin = $this->ion_auth->is_admin($this->ion_auth->get_user_id());
if($is_admin) {
    $sub_menu = array(
        array('controller' => 'customer', 'name' => 'Settings'),
        array('controller' => 'system', 'name' => 'System'),
        array('controller' => 'admin_customer', 'name' => 'Accounts'),
        array('controller' => 'admin_tag_editor', 'name' => 'Tag Editor')
    );
} else {
    $sub_menu = array(
        array('controller' => 'customer', 'name' => 'Settings')
    );
}
?>
<?php if (!empty($menu)) {?>
<ul class="left_nav_content menu ">
<?php foreach ($menu as $item) {?>
        <?php if($this->ion_auth->check_user_permission($item['controller'])){ 
            if($item['controller'] == "assess"){ ?>
                 <li<?php echo ($this->router->class==$item['controller']) ? " class=\"active\"":"";?>><a class="jq-<?=$item['controller']?>" href="<?php echo site_url("assess/products");?>"><?php echo $item['name'];?></a></li>
        <?php }else{ ?>  
                <li<?php echo ($this->router->class==$item['controller']) ? " class=\"active\"":"";?>><a class="jq-<?=$item['controller']?>" href="<?php echo site_url($item['controller']);?>"><?php echo $item['name'];?></a></li>
       
        <?php }} ?>
<?php } ?>
                <li>
                    <a href="#"><span><?php echo $info['username']; ?></span></a>
                    
                   <?php  if (!empty($sub_menu)) {?>
                        <ul class="sub_menu">
                          <?php  foreach ($sub_menu as $sub_item) {
                            if($this->ion_auth->check_user_permission($sub_item['controller'])){ ?>
                             
                                <li<?php echo ($this->router->class==$sub_item['controller']) ? " class=\"active\"":"";?>><a href="<?php echo site_url($sub_item['controller']);?>"><span><?php echo $sub_item['name'];?></span></a></li>
                           <?php }} ?>
                        <?php if ($is_admin) { ?>
                            <li<?php echo ($this->router->class=='job_board') ? " class=\"active\"":"";?>><a href="<?php echo site_url('job_board');?>"><span>Job Board</span></a></li>
                        <?php }?>    
                        <li><a href="<?php echo site_url('auth/logout');?>">LOG OUT</a></li>
                        </ul>
                   <?php } ?>
                </li>
				</ul>
<?php } ?>
