<?php echo doctype(); ?>
<html lang="en">
<head>
<title><?php echo $title;?></title>
<?php
	$meta = array(
        array('name' => 'description', 'content' => 'Product Description Editor'),
        array('name' => 'keywords', 'content' => 'product description editor'),
		array('name' => 'robots', 'content' => 'no-cache'),
        array('name' => 'Content-type', 'content' => 'text/html; charset=utf-8', 'type' => 'equiv')
    );
	echo meta($meta);
?>
<link href="<?php echo base_url();?>css/defaults.css" type="text/css" rel="stylesheet">
<script src="//ajax.googleapis.com/ajax/libs/jquery/2.0.0/jquery.min.js"></script>
<script src="<?php echo base_url();?>js/defaults.js"></script>

<?php if (isset($js)){ ?>
<script type='text/javascript'>
	<?php echo $js;?>
</script>
<?php } ?>
<?php
if(isset($head) && is_array($head)) {
	foreach ($head as $headObject) {
		echo $headObject;
	}
}
?>
</head>
<body <?php if(isset($onload)){echo "onload=$onload";}?>>
		<div id="mainNav"><?php //$this->load->view('partials/menu.tpl.php');?></div>
		<div id="breadcrumb"><?php //$this->load->view('partials/breadcrumb.tpl.php');?></div>

		<?php echo $content;?>

		<div id="footer">
			<div id="bottomMenu"><?php //$this->load->view('partials/bottom_menu.tpl.php');?></div>
			<div id="copywright"><?php //$this->load->view('partials/copywright.tpl.php');?></div>
		</div>

	<?php $this->load->view('footer.php');?>
</body>
</html>