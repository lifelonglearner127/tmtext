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
<body>
