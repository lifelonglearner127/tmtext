<!-- <img class='preloader_grids_box_pci' src="<?php echo base_url() ?>/img/grids_boxes_preloader.gif"> -->
<div id="dd_drop_random_r"></div>
<div class='well'>
	<input type='hidden' name='random_r_hidden_c' value="<?php echo $get_random_r['customer']; ?>">
	<input type='hidden' id='get_pc_r' name='get_pc' value="<?php echo $get_random_r['id']; ?>">
	<p class='centered'><span class="label label-success">PRODUCT FOR COMPARE</span></p>
	<p class='centered'><span class="label label-info"><?php echo $get_random_r['customer']; ?></span></p>
	<p class='centered'>
		<?php 
			switch ($get_random_r['customer']) {
				case 'bjs.com':
					$img_c_source = base_url()."img/bjs-logo.gif";
					break;
				case 'sears.com':
					$img_c_source = base_url()."img/sears-logo.png";
					break;
				case 'walmart.com':
					$img_c_source = base_url()."img/walmart-logo.png";
					break;
				case 'staples.com':
					$img_c_source = base_url()."img/staples-logo.png";
					break;
				case 'overstock.com':
					$img_c_source = base_url()."img/overstock-logo.png";
					break;
				case 'tigerdirect.com':
					$img_c_source = base_url()."img/tigerdirect-logo.jpg";
					break;
				
				default:
					$img_c_source = "";
					break;
			}
		?>
		<img src="<?php echo $img_c_source; ?>">
	</p>
	<ul class='nav nav-pills nav-stacked'>
		<li class='active'><a data-id="<?php echo $get_random_r['id']; ?>" href='javascript:void(0)'><?php echo $get_random_r['product_name']; ?></a></li>
	</ul>
	<p class='centered'><span class="label label-success">SHORT DESCRIPTION</span></p>
	<ul class='nav nav-pills nav-stacked'>
		<li><?php echo $get_random_r['description']; ?></li>
	</ul>
	<p class='centered'><span class="label label-success">LONG DESCRIPTION</span></p>
	<ul class='nav nav-pills nav-stacked'>
		<li><?php echo $get_random_r['long_description']; ?></li>
	</ul>
</div>