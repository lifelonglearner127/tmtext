<?php if(count($v_producs) > 0) { ?>
	
	<?php foreach($v_producs as $k => $v) { ?>

	<?php 
		$pair_id = $v['id'];
		$im_pr_f = $v['im_pr_f'];
		$im_pr_s = $v['im_pr_s'];
	?>

	<div class='sc_pair_section'>
		<div class='general_top'>
			<span class="label label_c"><?php echo date('jS F, Y, G:i:s', strtotime($v['stamp'])); ?></span>
			<?php 
				$rate = $v['rate'];
				switch ($rate) {
					case 2:
						$rate_sign = 'Yes';
						$bage_class = 'label-info';
						break;
					case 1:
						$rate_sign = 'No';
						$bage_class = 'label-important';
						break;
					case 0:
						$rate_sign = 'Not sure';
						$bage_class = "";
						break;
					
					default:
						$rate_sign = "";
						$bage_class = "";
						break;
				}
			?>
			<span class="label <?php echo $bage_class; ?> label_c">
				<?php echo $rate_sign; ?>
			</span>
			<a href='javascript:void(0)' onclick="reComparePair('<?php echo $im_pr_f; ?>', '<?php echo $im_pr_s; ?>')" class='btn btn-primary'><i class="icon-edit icon-white"></i>&nbsp;Re-compare</a>
			<a href='javascript:void(0)' onclick="deleteComparePair('<?php echo $pair_id; ?>')" class='btn btn-danger'><i class="icon-remove-circle icon-white"></i>&nbsp;Delete</a>
		</div>
		<?php if(count($v['products_data']) > 0) { ?>
			<?php foreach($v['products_data'] as $key => $value) { ?>
				<div class='well general_well_middle'>
					<table class='table'>
						<tbody>
							<tr>
								<td><span class='gwm_label'>Customer:</span></td>
								<td>
									<?php 
										switch ($value['customer']) {
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
											default:
												$img_c_source = "";
												break;
										}
									?>
									<img src="<?php echo $img_c_source; ?>">
								</td>
							</tr>
							<tr>
								<td><span class='gwm_label'>Product Name:</span></td>
								<td><p class='gwm_body'><a target="_blank" href="<?php echo $value['url']; ?>"><?php echo $value['product_name']; ?></a></p></td>
							</tr>
							<tr>
								<td><span class='gwm_label'>Short Description:</span></td>
								<td><p class='gwm_body'><?php echo $value['description']; ?></p></td>
							</tr>
							<tr>
								<td><span class='gwm_label'>Long Description:</span></td>
								<td><p class='gwm_body'><?php echo $value['long_description']; ?></p></td>
							</tr>
						</tbody>
					</table>
				</div>
			<?php } ?>
		<?php } ?>
	</div>

	<hr class='pci_list_sep'>

	<?php } ?>
	
<?php } ?>
