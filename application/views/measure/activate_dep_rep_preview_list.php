<div class="modal-header">
	<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
	<h3>Departments screenshot reports list</h3>
</div>
<div class="modal-body">
	<?php // echo var_dump($user_dep_rep_sets); ?>
	<table id='dcsr_control_panel_tabel' class='table table-striped'>
		<thead>
			<tr>
				<th><input type='checkbox' name="clst_report_ch_all" id="clst_report_ch_all"></th>
				<th>Main</th>
				<th>Competitors</th>
			</tr>
		</thead>
		<tbody>
			<?php if(count($user_dep_rep_sets) > 0) { ?>
				<?php foreach($user_dep_rep_sets as $k => $v) { ?>
				<tr>
					<td><input type='checkbox' class='clst_report_ch'></td>
					<td>
						<?php $main_dep_snap = $this->department_members_model->getLatestDepartmentScreen($v->main_choose_dep); ?>
						<?php if($main_dep_snap['img_av_status']) { ?> 
						<div><img style='width: 100%' src="<?php echo base_url() ?>webshoots/<?php echo $main_dep_snap['snap_name']; ?>"></div>	
						<?php } else { ?>
						<p>not exist or broken <a href='javascript:void(0)' class='btn btn-success'>re-crawl</a></p>
						<?php } ?>
					</td>
					<td>
						<?php $decode_com = json_decode($v->json_encode_com); ?>
						<?php if(count($decode_com) > 0) { ?>
							<?php foreach($decode_com as $k => $v) { ?>
								<?php $sec_dep_snap = $this->department_members_model->getLatestDepartmentScreen($v->sec_dep_chooser); ?>
								<?php if($sec_dep_snap['img_av_status']) { ?>
								<div><img style='width: 100%' src="<?php echo base_url() ?>webshoots/<?php echo $sec_dep_snap['snap_name']; ?>"></div>	
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
	<button id='btn_dep_rep_send_set' class="btn btn-primary btn-rec-all-send" disabled="" type="button" onclick="">Send report</button>
</div>
