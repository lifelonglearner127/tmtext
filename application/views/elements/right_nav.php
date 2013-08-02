<?php
$menu = array(
	array('controller' => 'system', 'name' => 'System'),
	array('controller' => 'admin_customer', 'name' => 'Accounts'),
	/*array('controller' => 'admin_editor', 'name' => 'Editors'),*/
    array('controller' => 'admin_tag_editor', 'name' => 'Tag Editor'),
    /*array('controller' => 'site_crawler', 'name' => 'Site Crawler'),*/
    array('controller' => 'job_board', 'name' => 'Job Board'),
);

?>
<?php if (!empty($menu)) {?>
<ul class="right_nav_content">
<?php foreach ($menu as $item) {?>
					<li<?php echo ($this->router->class==$item['controller']) ? " class=\"active\"":"";?>><a href="<?php echo site_url($item['controller']);?>"><?php echo $item['name'];?></a></li>
<?php } ?>
				</ul>
<?php } ?>