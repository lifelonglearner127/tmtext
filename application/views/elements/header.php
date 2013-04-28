<head>
	<title><?php echo $title;?></title>
<?php
	$meta = array(
        array('name' => 'description', 'content' => 'Product Description Editor'),
        array('name' => 'keywords', 'content' => 'product description editor'),
        array('name' => 'author', 'content' => ''),
        array('name' => 'viewport', 'content' => 'width=device-width, initial-scale=1.0'),
		array('name' => 'robots', 'content' => 'no-cache'),
        array('name' => 'Content-type', 'content' => 'text/html; charset=utf-8', 'type' => 'equiv')
    );
	echo meta($meta);
?>

	<link href="<?php echo base_url();?>css/bootstrap.css" rel="stylesheet">
	<link href="<?php echo base_url();?>css/style.css" rel="stylesheet">

	<!--[if lt IE 9]>
		<script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
	<![endif]-->

	<script src="//ajax.googleapis.com/ajax/libs/jquery/2.0.0/jquery.min.js"></script>
	<script src="<?php echo base_url();?>js/defaults.js"></script>
	<!-- script src="<?php echo base_url();?>js/main.js"></script-->
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