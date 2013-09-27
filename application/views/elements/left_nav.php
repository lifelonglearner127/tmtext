<?php
// $menu = array(
//     array('controller' => 'research', 'name' => 'Research & Edit'),
// 	array('controller' => 'editor', 'name' => 'Create'),
//     array('controller' => 'validate', 'name' => 'Validate'),
//     array('controller' => 'measure', 'name' => 'Analysis'),
// 	array('controller' => 'customer', 'name' => 'Settings'),
// );

$menu = array(
    array('controller' => 'batches', 'name' => 'Batches'),
    array('controller' => 'measure', 'name' => 'Competitive Intelligence'),
    array('controller' => 'assess', 'name' => 'Reports'),
    array('controller' => 'research', 'name' => 'Edit'),
    array('controller' => 'brand', 'name' => 'Social'),
    //array('controller' => 'editor', 'name' => 'Create'),
    //array('controller' => 'validate', 'name' => 'Validate'),
	array('controller' => 'customer', 'name' => 'Settings'),
);

?>
<?php if (!empty($menu)) {?>
<ul class="left_nav_content">
<?php foreach ($menu as $item) {?>
					<?php if($this->ion_auth->check_user_permission($item['controller'])){ ?>
					<li<?php echo ($this->router->class==$item['controller']) ? " class=\"active\"":"";?>><a class="jq-<?=$item['controller']?>" href="<?php echo site_url($item['controller']);?>"><?php echo $item['name'];?></a></li>
					<?php } ?>
<?php } ?>
				</ul>
<?php } ?>