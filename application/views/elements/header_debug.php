<head>
	<title><?php echo $title;?></title>
<?php
	$meta = array(
        array('name' => 'description', 'content' => 'Debug Section'),
        array('name' => 'keywords', 'content' => 'debug section'),
        array('name' => 'author', 'content' => ''),
        array('name' => 'viewport', 'content' => 'width=device-width, initial-scale=1.0'),
		array('name' => 'robots', 'content' => 'no-cache'),
        array('name' => 'Content-type', 'content' => 'text/html; charset=utf-8', 'type' => 'equiv')
    );
	echo meta($meta);
?>
	<link href="<?php echo base_url();?>css/bootstrap.css" rel="stylesheet">
	<link href="<?php echo base_url();?>css/style.css" rel="stylesheet">
	<link href="<?php echo base_url();?>css/debug.css" rel="stylesheet">

	<!--[if lt IE 9]>
		<script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
	<![endif]-->

	<script type='text/javascript'>var base_url = '<?php echo base_url();?>';</script>
	<script src="//ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>
	<script src="<?php echo base_url();?>js/bootstrap.min.js"></script>
	<script src="<?php echo base_url();?>js/underscore.js"></script>
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