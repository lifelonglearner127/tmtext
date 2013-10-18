<div class="modal-header">
	<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
	<h3>Departments screenshot reports list</h3>
</div>
<div class="modal-body">
	<table id='dcsr_control_panel_tabel' class='table table-striped'>
		<thead>
			<tr>
				<th><input type='checkbox' checked name="clst_report_ch_all" id="clst_report_ch_all"></th>
				<th>Main</th>
				<th>Competitors</th>
			</tr>
		</thead>
		<tbody>
			<?php if(count($user_dep_rep_sets) > 0) { ?>
				<?php foreach($user_dep_rep_sets as $k => $v) { ?>
				<tr>
					<td>
						<input checked type='checkbox' value="<?php echo $v->id ?>" class='clst_report_ch'>
						<br>
						<button class='btn btn-danger small_custom_icon_btn mt_5' data-id="<?php echo $v->id; ?>" onclick="removeExistedSet(this)"><i class='icon-remove-circle icon-white'></i></button>
					</td>
					<td>
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
						<div>
							<p style='font-weight: bold; font-size: 12px;'><?php echo $cover_text; ?></p>
						</div>
						<div style='margin-bottom: 10px;'><img style='width: 100%' src="<?php echo base_url() ?>webshoots/<?php echo $main_dep_snap['snap_name']; ?>"></div>	
						<div>
							<p style='font-weight: bold; font-size: 12px;'>Description word count: <?php echo $desc_words_data; ?></p>
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
								<ul style='margin-left: 0px;'>
								<?php foreach($k_words as $kw => $vw) { ?>
									<li style='font-size: 12px; list-style: none; list-style-position: inside;'><span><?php echo $vw['w']; ?> : </span><span><?php echo $vw['c']; ?></span> - <span><?php echo $vw['d'] ?>%</span></li>
								<?php } ?>
								</ul>
							<?php } ?>
						</div>
						<?php } else { ?>
						<p>not exist or broken <a href='javascript:void(0)' class='btn btn-success'>re-crawl</a></p>
						<?php } ?>
					</td>
					<td>
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
								<div>
									<p style='font-weight: bold; font-size: 12px;'><?php echo $cover_text; ?></p>
								</div>
								<div style='margin-bottom: 10px;'><img style='width: 100%' src="<?php echo base_url() ?>webshoots/<?php echo $sec_dep_snap['snap_name']; ?>"></div>	
								<div>
									<p style='font-weight: bold; font-size: 12px;'>Description word count: <?php echo $desc_words_data; ?></p>
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
										<ul style='margin-left: 0px;'>
										<?php foreach($k_words as $kw => $vw) { ?>
											<li style='font-size: 12px; list-style: none; list-style-position: inside;'><span><?php echo $vw['w']; ?> : </span><span><?php echo $vw['c']; ?></span> - <span><?php echo $vw['d'] ?>%</span></li>
										<?php } ?>
										</ul>
									<?php } ?>
								</div>
								<?php } else { ?>
								<p>not exists or broken <a href='javascript:void(0)' class='btn btn-success'>re-crawl</a></p>
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
</div>
<div class="modal-footer">
	<button type='button' class='btn btn-success' onclick='viewRecipientsListCats()'>Configure recipients</button>
	<button type='button' class='btn btn-success' onclick='viewCatsScreensCp()'>Add categories</button>
	<button id='btn_dep_rep_send_set' class="btn btn-primary btn-rec-all-send" type="button" onclick="sendDepSnapsReport()">Send report</button>
</div>

<script type='text/javascript'>
	
	$(document).ready(function() {
		$("#clst_report_ch_all").on('change', function(e) {
			if($(e.target).is(":checked")) {
				$('.clst_report_ch').attr('checked', true);
				$('#btn_dep_rep_send_set').removeAttr('disabled');
			} else {
				$('.clst_report_ch').removeAttr('checked');
				$('#btn_dep_rep_send_set').attr('disabled', true);
			}
		});

		$(".clst_report_ch").on('change', function(e) {
			var checked_count = $(".clst_report_ch").length;
			setTimeout(function() {
				var count_s = 0;
				$(".clst_report_ch").each(function(index, val) {
					if($(val).is(':checked')) count_s++;
				});
				if(checked_count == count_s) {
					$("#clst_report_ch_all").attr('checked', true);
				} else {
					$("#clst_report_ch_all").removeAttr('checked');
				}
				if(count_s == 0) {
					$("#clst_report_ch_all").removeAttr('checked');
					$("#btn_dep_rep_send_set").attr('disabled', true);
				} else {
					$('#btn_dep_rep_send_set').removeAttr('disabled');
				} 
			}, 100);
		});

	});

	function removeExistedSet(e) {
		if(confirm('Are you sure?')) {
			var remove_row = $(e).parent().parent();
			var id = $(e).data('id');
			$.post(base_url + 'index.php/measure/delete_dep_rec_set', {id: id}, function(data) {
				remove_row.remove();
				console.log(data);	
			});
		}
	}

	function sendDepSnapsReport() {
		var rep_ids = [];
		$(".clst_report_ch:checked").each(function(index, value) {
			rep_ids.push($(value).val());
		});
		if(rep_ids.length > 0) {
			$("#dep_rep_preview_list_modal").modal('hide');
			$('#loader_dep_sending_rep').modal('show');
			$.post(base_url + 'index.php/measure/send_dep_snaps_report', {rep_ids: rep_ids}, function(data) {
				$('#loader_dep_sending_rep').modal('hide');
				console.log(data);	
			});
		} else {
			alert('No checked items');
		}
	}

</script>
