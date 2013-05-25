<?php
$menu = array(
    array('controller' => 'research', 'name' => 'Research & Edit'),
	array('controller' => 'editor', 'name' => 'Create'),
    array('controller' => 'validate', 'name' => 'Validate'),
    array('controller' => 'measure', 'name' => 'Analysis'),
	array('controller' => 'customer', 'name' => 'Customer'),
);

?>
<?php if (!empty($menu)) {?>
<ul class="left_nav_content">
<?php foreach ($menu as $item) {?>
					<li<?php echo ($this->router->class==$item['controller']) ? " class=\"active\"":"";?>><a class="jq-<?=$item['controller']?>" href="<?php echo site_url($item['controller']);?>"><?php echo $item['name'];?></a></li>
<?php } ?>
				</ul>
<?php } ?>
