<?php echo doctype(); ?>
<html lang="en">
<head>
<?php
	$meta = array(
        array('name' => 'robots', 'content' => 'no-cache'),
        array('name' => 'description', 'content' => 'Product Description Editor'),
        array('name' => 'keywords', 'content' => 'product description editor'),
        array('name' => 'robots', 'content' => 'no-cache'),
        array('name' => 'Content-type', 'content' => 'text/html; charset=utf-8', 'type' => 'equiv')
    );

	echo meta($meta);
	?>
<title><?php echo $title;?></title>
<link href="/css/defaults.css" type="text/css" rel="stylesheet">
<script src="//ajax.googleapis.com/ajax/libs/jquery/2.0.0/jquery.min.js"></script>
<script src="/js/defaults.js"></script>
</head>
<body>
