<?php
$menu = array(
	array('controller' => 'editor', 'name' => 'Editor'),
	array('controller' => 'customer', 'name' => 'Customer'),
);

?>
<?php if (!empty($menu)) {?>
<ul class="left_nav_content">
<?php foreach ($menu as $item) {?>
					<li<?php echo ($this->router->class==$item['controller']) ? " class=\"active\"":"";?>><a href="<?php echo site_url($item['controller']);?>"><?php echo $item['name'];?></a></li>
<?php } ?>
				</ul>
<?php } ?>
