<?php 
	$file = realpath(BASEPATH . "../webroot/emails_logos/$email_logo");
  $file_size = filesize($file);
  if($file_size === false) {
  	$email_logo = 'default_logo.jpg';
  }
?>
<img style='max-width: 240px;' src="<?php echo base_url() ?>/emails_logos/<?php echo $email_logo; ?>">

<table>
	<tbody>
		<?php if(count($reports) > 0) { ?>
			<?php foreach($reports as $k => $v) { ?>
			<tr>
				<td style='vertical-align: top; padding-bottom: 15px;'>
					<?php 
						$main_dep_data = $this->department_members_model->get($v->main_choose_dep); 
						if(count($main_dep_data) > 0) {
							$md_data = $main_dep_data[0];
							$cover_text = $md_data->text;
							$desc_words_data = $md_data->description_words;
						} else {
							$md_data = null;
							$cover_text = "no name";
							$desc_words_data = "no data";
						}
					?>
					<?php $main_dep_snap = $this->department_members_model->getLatestDepartmentScreen($v->main_choose_dep); ?>
					<?php if($main_dep_snap['img_av_status']) { ?>
					<div style='width: 400px;'>
						<p style='font-weight: bold;'><?php echo $cover_text; ?></p>
					</div> 
					<div style='width: 400px;'>
						<img style='width: 100%' src="<?php echo base_url() ?>webshoots/<?php echo $main_dep_snap['snap_name']; ?>">
					</div>
					<div style='width: 400px;'>
						<p style='font-weight: bold;'>Description words count: <?php echo $desc_words_data; ?></p>
						<?php if($md_data !== null) { ?>
								<?php $tkdc_decoded = json_decode($md_data->title_keyword_description_count); ?>
								<?php if(count($tkdc_decoded) > 0) { ?>
									<p style='font-weight: bold;'>Title Description Keywords:</p>
									<ul>
									<?php foreach($tkdc_decoded as $ki => $vi) { ?>
										<li><?php echo $ki." : ".$vi ?></li>
									<?php } ?>
									</ul>
								<?php } ?>

								<?php $tkdd_decoded = json_decode($md_data->title_keyword_description_density); ?>
								<?php if(count($tkdd_decoded) > 0) { ?>
									<p style='font-weight: bold;'>Title Description Keywords Density:</p>
									<ul>
									<?php foreach($tkdd_decoded as $kd => $vd) { ?>
										<li><?php echo $kd." : ".$vd ?></li>
									<?php } ?>
									</ul>
								<?php } ?>
						<?php } ?>
					</div>
					<?php } else { ?>
					<p>not exist or broken</p>
					<?php } ?>
				</td>
				<td style='vertical-align: top; padding-bottom: 15px;'>
					<?php $decode_com = json_decode($v->json_encode_com); ?>
					<?php if(count($decode_com) > 0) { ?>
						<?php foreach($decode_com as $k => $v) { ?>
							<?php 
								$sec_dep_data = $this->department_members_model->get($v->sec_dep_chooser);
								if(count($sec_dep_data) > 0) {
									$sd_data = $sec_dep_data[0];
									$cover_text = $sd_data->text;
									$desc_words_data = $sd_data->description_words;
								} else {
									$sd_data = null;
									$cover_text = "no name";
									$desc_words_data = "no data";
								}
							?>
							<?php $sec_dep_snap = $this->department_members_model->getLatestDepartmentScreen($v->sec_dep_chooser); ?>
							<?php if($sec_dep_snap['img_av_status']) { ?>
							<div style='width: 400px;'>
								<p style='font-weight: bold;'><?php echo $cover_text; ?></p>
							</div>
							<div style='margin-bottom: 10px; width: 400px;'>
								<img style='width: 100%' src="<?php echo base_url() ?>webshoots/<?php echo $sec_dep_snap['snap_name']; ?>">
							</div>
							<div style='width: 400px;'>
								<p style='font-weight: bold;'>Description words count: <?php echo $desc_words_data; ?></p>
								<?php if($sd_data !== null) { ?>
										<?php $tkdc_decoded = json_decode($sd_data->title_keyword_description_count); ?>
										<?php if(count($tkdc_decoded) > 0) { ?>
											<p style='font-weight: bold;'>Title Description Keywords:</p>
											<ul>
											<?php foreach($tkdc_decoded as $ki => $vi) { ?>
												<li><?php echo $ki." : ".$vi ?></li>
											<?php } ?>
											</ul>
										<?php } ?>

										<?php $tkdd_decoded = json_decode($sd_data->title_keyword_description_density); ?>
										<?php if(count($tkdd_decoded) > 0) { ?>
											<p style='font-weight: bold;'>Title Description Keywords Density:</p>
											<ul>
											<?php foreach($tkdd_decoded as $kd => $vd) { ?>
												<li><?php echo $kd." : ".$vd ?></li>
											<?php } ?>
											</ul>
										<?php } ?>

								<?php } ?>
							</div>	
							<?php } else { ?>
							<p>not exists or broken</p>
							<?php } ?>
						<?php } ?>
					<?php } else { ?>
					<p>no any report sets</p>
					<?php } ?>
				</td>
			</tr>
			<?php } ?>
		<?php } else { ?>
		<tr><td colspan='3'><p>no any report sets</p></td></tr>
		<?php } ?>
	</tbody>
</table>
