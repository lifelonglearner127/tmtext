<div id='pci_l_section' class='span5'>
	<!-- <div id="dd_drop_random_l"></div> -->
	<div class='well'>
		<input type='hidden' name='random_l_hidden_c' value="<?php echo $get_random_l['customer']; ?>">
		<input type='hidden' id='get_pc_l' name='get_pc' value="<?php echo $get_random_l['id']; ?>">
		<p class='centered'><span class="label label-success">PRODUCT FOR COMPARE</span></p>
		<p class='centered'><span class="label label-info"><?php echo $get_random_l['customer']; ?></span></p>
		<p class='centered'>
			<?php 
				switch ($get_random_l['customer']) {
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
                    case 'amazon.com':
                        $img_c_source = base_url()."img/amazon-logo.jpg";
                        break;
					default:
						$img_c_source = "";
						break;
				}
			?>
			<img src="<?php echo $img_c_source; ?>">
		</p>
		<ul class='nav nav-pills nav-stacked'>
			<li class='active'><a class='pfc_link_l' data-id="<?php echo $get_random_l['id']; ?>" target="_blank" href="<?php echo $get_random_l['url']; ?>"><?php echo $get_random_l['product_name']; ?></a></li>
		</ul>
		<p class='centered'><span class="label label-success">SHORT DESCRIPTION</span></p>
		<ul class='nav nav-pills nav-stacked'>
			<li><?php echo $get_random_l['description']; ?></li>
		</ul>
		<p class='centered'><span class="label label-success">LONG DESCRIPTION</span></p>
		<ul class='nav nav-pills nav-stacked'>
			<li><?php echo $get_random_l['long_description']; ?></li>
		</ul>
	</div>
</div>

<div class='span2'>
	<div class='well'>
		<p class='centered'><span class="label label-info">DECISION</span></p>
		<button id='sccb_newset_btn' onclick="productCompareNewSet();" type='button' class='btn btn-success icb_systme_compare_btn margin_bottom'>New</button>
		<button id='sccb_yes_btn' onclick="productCompareDecision(2);" type='button' class='btn btn-primary icb_systme_compare_btn margin_bottom'>Yes</button>
		<button id='sccb_not_btn' onclick="productCompareDecision(1);" type='button' class='btn btn-danger icb_systme_compare_btn'>No</button>
	</div>
</div>

<div id='pci_r_section' class='span5'>
	<!-- <div id="dd_drop_random_r"></div> -->
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
                    case 'amazon.com':
                        $img_c_source = base_url()."img/amazon-logo.jpg";
                        break;
					
					default:
						$img_c_source = "";
						break;
				}
			?>
			<img src="<?php echo $img_c_source; ?>">
		</p>
		<ul class='nav nav-pills nav-stacked'>
			<li class='active'><a class='pfc_link_r' data-id="<?php echo $get_random_r['id']; ?>" target="_blank" href="<?php echo $get_random_r['url']; ?>"><?php echo $get_random_r['product_name']; ?></a></li>
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
</div>

<script type='text/javascript'>
	$(document).ready(function(e) {
		// ---- UI tooltips (start)
		$("#sccb_newset_btn").tooltip({
			placement: 'left',
			title: 'Load new set'
		});
		$("#sccb_yes_btn").tooltip({
			placement: 'left',
			title: 'Mark as similar'
		});
		$("#sccb_not_btn").tooltip({
			placement: 'bottom',
			title: 'Mark as different'
		});
		$(".pfc_link_l").tooltip({
			placement: 'left',
			title: 'Press to visit product page'
		});
		$(".pfc_link_r").tooltip({
			placement: 'right',
			title: 'Press to visit product page'
		});
		// ---- UI tooltips (end)
	});
</script>

