<?php if(count($v_producs) > 0) { ?>
	
	<?php foreach($v_producs as $k => $v) { ?>

	<div class='sc_pair_section'>
		<div class='general_top'>
			<span class="label label_c"><?php echo date('jS F, Y', strtotime($v['stamp'])); ?></span>
			<span class="label label_c">
				<?php 
					$rate = $v['rate'];
					switch ($rate) {
						case 2:
							$rate_sign = 'Yes';
							break;
						case 1:
							$rate_sign = 'No';
							break;
						case 0:
							$rate_sign = 'Not sure';
							break;
						
						default:
							$rate_sign = "";
							break;
					}
				?>
				<?php echo $rate_sign; ?>
			</span>
		</div>
		<?php if(count($v['products_data']) > 0) { ?>
			<?php foreach($v['products_data'] as $key => $value) { ?>
				<div class='well general_well_middle'>
					<table class='table'>
						<tbody>
							<tr>
								<td><span class='gwm_label'>Product Name:</span></td>
								<td><p class='gwm_body'><?php echo $value['product_name']; ?></p></td>
							</tr>
							<tr>
								<td><span class='gwm_label'>Url:</span></td>
								<td><p class='gwm_body'><?php echo $value['url']; ?></p></td>
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

	<?php } ?>
	
<?php } ?>
