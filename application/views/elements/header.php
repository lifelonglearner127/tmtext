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
    <link href="<?php echo base_url();?>css/jquery.fancybox.css" rel="stylesheet">
	<link href="<?php echo base_url();?>css/bootstrap.css" rel="stylesheet">
	<link href="<?php echo base_url();?>css/style.css" rel="stylesheet">
	<link href="<?php echo base_url();?>css/chosen.css" rel="stylesheet">
	<link href="<?php echo base_url();?>css/fileupload/jquery.fileupload-ui.css" rel="stylesheet">
    <link href="//ajax.googleapis.com/ajax/libs/jqueryui/1.8.17/themes/base/jquery-ui.css" rel="stylesheet">
    <link href="<?php echo base_url();?>css/dd.css" rel="stylesheet">
    <link href="<?php echo base_url();?>css/home-page.css" rel="stylesheet">
    <link href="<?php echo base_url();?>css/bootstrap-lightbox.min.css" rel="stylesheet">
    <link href="<?php echo base_url();?>css/anythingslider.css" rel="stylesheet">
    <link href='//fonts.googleapis.com/css?family=Open+Sans' rel='stylesheet' type='text/css'>
	<link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/styles.css" />

	<!--[if lt IE 9]>
		<script src="//html5shim.googlecode.com/svn/trunk/html5.js"></script>
	<![endif]-->

	<script type='text/javascript'>var base_url = '<?php echo base_url();?>';</script>
    <script src="<?php echo base_url();?>js/jsdiff.js"></script>
	<!--<script src="//ajax.googleapis.com/ajax/libs/jquery/2.0.0/jquery.min.js"></script>-->
	<script src="//ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>
<!--	<script src="http://code.jquery.com/ui/1.10.3/jquery-ui.js"></script>-->
        <script src="<?php echo base_url();?>js/jquery-ui.js"></script>
    <script type='text/javascript' src="<?php echo base_url();?>js/jquery.dd.js"></script>
	<!--<script src="<?php echo base_url();?>js/bootstrap.min.js"></script>-->
	<script src="<?php echo base_url();?>js/bootstrap.js"></script>
	<script src="<?php echo base_url();?>js/underscore.js"></script>
	<script src="<?php echo base_url();?>js/bootstrap-lightbox.min.js"></script>
	<script src="<?php echo base_url();?>js/moment.js"></script>
	<script src="<?php echo base_url();?>js/jquery.anythingslider.min.js"></script>
    <script src="<?php echo base_url();?>js/jquery.scrollTo-1.4.3.1.js"></script>
    <script src="<?php echo base_url();?>js/jquery.fancybox.js"></script>
    
    <script src="<?php echo base_url();?>js/FixedHeader.js"></script>
    <script src="<?php echo base_url();?>js/jquery.cookie.js"></script>
    <script src="<?php echo base_url();?>js/defaults.js"></script>
    <script src="<?php echo base_url();?>js/jquery.expander.js"></script>
    <script src="<?php echo base_url();?>js/chosen.jquery.min.js"></script>
    <script src="<?php echo base_url();?>js/fileupload/vendor/jquery.ui.widget.js"></script>
	<script src="<?php echo base_url();?>js/fileupload/jquery.iframe-transport.js"></script>
	<script src="<?php echo base_url();?>js/fileupload/jquery.fileupload.js"></script>
	<script src="<?php echo base_url();?>js/search_highlight_plug.js"></script>
    <script type='text/javascript' src="<?php echo base_url();?>js/tag_editor.js"></script>
    <script type='text/javascript' src="<?php echo base_url();?>js/research.js"></script>
    <script type='text/javascript' src="<?php echo base_url();?>js/measure.js"></script>
    <script type='text/javascript' src="<?php echo base_url();?>js/jquery.highlight-3.js"></script>
    <script type="text/javascript" src="<?php echo base_url();?>js/jquery-templ.js"></script>
    <script type="text/javascript" src="<?php echo base_url();?>js/jquery.validate.min.js"></script>
    <script type="text/javascript" src="<?php echo base_url();?>js/jquery.dataTables.min.js"></script>
	<script src="<?php echo base_url();?>js/ColReorderWithResize.js"></script>
	<script src="<?php echo base_url();?>js/jquery.floatThead.min.js"></script>
<script type="text/javascript" src="http://code.highcharts.com/stock/highstock.js"></script>
	<script src="http://code.highcharts.com/modules/exporting.js"></script>
    <!-- for compare_results page -->
    <?php  if($_SERVER["REQUEST_URI"]){
        $serv =  $_SERVER["REQUEST_URI"];
        $b = strstr($serv,"compare_results");
        if($b !=''){
     ?>
            <script type="text/javascript" src="<?php echo base_url();?>js/research_assess.js"></script>
     <?php 
        }
    };?>

 
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