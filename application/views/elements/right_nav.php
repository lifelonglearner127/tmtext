<?php
$menu = array(
	array('controller' => 'system', 'name' => 'System'),
	array('controller' => '#', 'name' => 'Customers'),
	array('controller' => '#', 'name' => 'Editors'),
);

?>
<?php if (!empty($menu)) {?>
<ul class="right_nav_content">
<?php foreach ($menu as $item) {?>
					<li<?php echo ($this->router->class==$item['controller']) ? " class=\"active\"":"";?>><a href="<?php echo site_url($item['controller']);?>"><?php echo $item['name'];?></a></li>
<?php } ?>
				</ul>
<?php } ?>