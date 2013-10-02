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
						<?php if($md_data !== null) { ?>
						<a href="<?php echo $md_data->url; ?>"><img style='width: 100%; cursor: pointer' src="<?php echo base_url() ?>webshoots/<?php echo $main_dep_snap['snap_name']; ?>"></a>
						<?php } else { ?>
						<img style='width: 100%' src="<?php echo base_url() ?>webshoots/<?php echo $main_dep_snap['snap_name']; ?>">
						<?php } ?>
					</div>
					<div style='width: 400px;'>
						<p style='font-weight: bold;'>Description word count: <?php echo $desc_words_data; ?></p>
						<?php 
							if($md_data !== null) {
								$k_words = array();
								$tkdc_decoded = json_decode($md_data->title_keyword_description_count);
								if(count($tkdc_decoded) > 0) {
									foreach($tkdc_decoded as $ki => $vi) {
										$mid = array(
											'w' => $ki,
											'c' => $vi,
											'd' => 0
										);
										$k_words[] = $mid;
									}
								}
								if(count($k_words) > 0) { 
									$tkdd_decoded = json_decode($md_data->title_keyword_description_density);
									if(count($tkdd_decoded) > 0) {
										foreach($tkdd_decoded as $kd => $vd) { // === search for density
											foreach ($k_words as $ks => $vs) {
												if($vs['w'] == $kd) {
													$k_words[$ks]['d'] = $vd;
												}
											}
										}
									}
								}
							}
						?>
						<?php if(count($k_words) > 0) { ?>
							<p style='font-weight: bold; font-size: 12px;'>Keywords (frequency, density):</p>
							<?php foreach($k_words as $kw => $vw) { ?>
								<p style='font-size: 12px;'><span><?php echo $vw['w']; ?> : </span><span><?php echo $vw['c']; ?></span> - <span><?php echo $vw['d'] ?>%</span></p>
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
								<?php if($sd_data !== null) { ?>
								<a href="<?php echo $sd_data->url ?>"><img style='width: 100%; cursor: pointer' src="<?php echo base_url() ?>webshoots/<?php echo $sec_dep_snap['snap_name']; ?>"></a>
								<?php } else { ?>
								<img style='width: 100%' src="<?php echo base_url() ?>webshoots/<?php echo $sec_dep_snap['snap_name']; ?>">
								<?php } ?>
							</div>
							<div style='width: 400px;'>
								<p style='font-weight: bold;'>Description word count: <?php echo $desc_words_data; ?></p>
								<?php 
									if($sd_data !== null) {
										$k_words = array();
										$tkdc_decoded = json_decode($sd_data->title_keyword_description_count);
										if(count($tkdc_decoded) > 0) {
											foreach($tkdc_decoded as $ki => $vi) {
												$mid = array(
													'w' => $ki,
													'c' => $vi,
													'd' => 0
												);
												$k_words[] = $mid;
											}
										}
										if(count($k_words) > 0) { 
											$tkdd_decoded = json_decode($sd_data->title_keyword_description_density);
											if(count($tkdd_decoded) > 0) {
												foreach($tkdd_decoded as $kd => $vd) { // === search for density
													foreach ($k_words as $ks => $vs) {
														if($vs['w'] == $kd) {
															$k_words[$ks]['d'] = $vd;
														}
													}
												}
											}
										}
									}
								?>
								<?php if(count($k_words) > 0) { ?>
									<p style='font-weight: bold; font-size: 12px;'>Keywords (frequency, density):</p>
									<?php foreach($k_words as $kw => $vw) { ?>
										<p style='font-size: 12px;'><span><?php echo $vw['w']; ?> : </span><span><?php echo $vw['c']; ?></span> - <span><?php echo $vw['d'] ?>%</span></p>
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
