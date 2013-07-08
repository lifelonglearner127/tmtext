<?php if(isset($c_product) && $c_product !== null && count($c_product) === 2) { ?>
	<?php $keys = array(); ?>
	<?php foreach($c_product as $k => $v) { ?>
		<?php $keys[] = $k; ?>
	<?php } ?>

	<div class='span5'>
		<div class='well'>
			<input type='hidden' name='get_pc' value="<?php echo $keys[0]; ?>">
			<p class='centered'><span class="label label-success">PRODUCT FOR COMPARE</span></p>
			<p class='centered'><span class="label label-info"><?php echo $c_product[$keys[0]]['customer']; ?></span></p>
			<p class='centered'>
				<?php 
					switch ($c_product[$keys[0]]['customer']) {
						case 'bjs.com':
							$img_c_source = base_url()."/img/bjs-logo.gif";
							break;
						case 'sears.com':
							$img_c_source = base_url()."/img/sears-logo.png";
							break;
						case 'walmart.com':
							$img_c_source = base_url()."/img/walmart-logo.png";
							break;
						case 'staples.com':
							$img_c_source = base_url()."/img/staples-logo.png";
							break;
						case 'overstock.com':
							$img_c_source = base_url()."/img/overstock-logo.png";
							break;
						case 'tigerdirect.com':
							$img_c_source = base_url()."/img/tigerdirect-logo.jpg";
							break;
                        case 'amazon.com':
                            $img_c_source = base_url(). "/img/amazon-logo.jpg";
                            break;
						default:
							$img_c_source = "";
							break;
					}
				?>
				<img src="<?php echo $img_c_source; ?>">
			</p>
			<ul class='nav nav-pills nav-stacked'>
				<li class='active'><a data-id="<?php echo $keys[0]; ?>" href='javascript:void(0)'><?php echo $c_product[$keys[0]]['product_name']; ?></a></li>
			</ul>
			<p class='centered'><span class="label label-success">SHORT DESCRIPTION</span></p>
			<ul class='nav nav-pills nav-stacked'>
				<li><?php echo $c_product[$keys[0]]['description']; ?></li>
			</ul>
			<p class='centered'><span class="label label-success">LONG DESCRIPTION</span></p>
			<ul class='nav nav-pills nav-stacked'>
				<li><?php echo $c_product[$keys[0]]['long_description']; ?></li>
			</ul>
		</div>
	</div>

	<div class='span2'>
		<div class='well'>
			<p class='centered'><span class="label label-info">DECISION</span></p>
			<button id='sccb_yes_btn' onclick="productCompareDecision(2);" type='button' disabled='true' class='btn btn-primary icb_systme_compare_btn margin_bottom disabled'>Yes</button>
			<button id='sccb_not_btn' onclick="productCompareDecision(1);" type='button' disabled='true' class='btn btn-danger icb_systme_compare_btn margin_bottom disabled'>No</button>
			<button id='sccb_notsure_btn' onclick="productCompareDecision(0);" type='button' disabled='true' class='btn icb_systme_compare_btn disabled'>Not sure</button>
		</div>
	</div>

	<div class='span5'>
		<div class='well'>
			<input type='hidden' name='get_pc' value="<?php echo $keys[1]; ?>">
			<p class='centered'><span class="label label-success">PRODUCT FOR COMPARE</span></p>
			<p class='centered'><span class="label label-info"><?php echo $c_product[$keys[1]]['customer']; ?></span></p>
			<p class='centered'>
				<?php 
					switch ($c_product[$keys[1]]['customer']) {
						case 'bjs.com':
							$img_c_source = base_url()."/img/bjs-logo.gif";
							break;
						case 'sears.com':
							$img_c_source = base_url()."/img/sears-logo.png";
							break;
						case 'walmart.com':
							$img_c_source = base_url()."/img/walmart-logo.png";
							break;
						case 'staples.com':
							$img_c_source = base_url()."/img/staples-logo.png";
							break;
						case 'overstock.com':
							$img_c_source = base_url()."/img/overstock-logo.png";
							break;
						case 'tigerdirect.com':
							$img_c_source = base_url()."/img/tigerdirect-logo.jpg";
							break;
                        case 'amazon.com':
                            $img_c_source = base_url(). "/img/amazon-logo.jpg";
                            break;
						default:
							$img_c_source = "";
							break;
					}
				?>
				<img src="<?php echo $img_c_source; ?>">
			</p>
			<ul class='nav nav-pills nav-stacked'>
				<li class='active'><a data-id="<?php echo $keys[1]; ?>" href='javascript:void(0)'><?php echo $c_product[$keys[1]]['product_name']; ?></a></li>
			</ul>
			<p class='centered'><span class="label label-success">SHORT DESCRIPTION</span></p>
			<ul class='nav nav-pills nav-stacked'>
				<li><?php echo $c_product[$keys[1]]['description']; ?></li>
			</ul>
			<p class='centered'><span class="label label-success">LONG DESCRIPTION</span></p>
			<ul class='nav nav-pills nav-stacked'>
				<li><?php echo $c_product[$keys[1]]['long_description']; ?></li>
			</ul>
		</div>
	</div>

<?php } ?>
