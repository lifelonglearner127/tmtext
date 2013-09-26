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
				<td style='vertical-align: top'>
					<?php $main_dep_snap = $this->department_members_model->getLatestDepartmentScreen($v->main_choose_dep); ?>
					<?php if($main_dep_snap['img_av_status']) { ?> 
					<div><img style='width: 100%' src="<?php echo base_url() ?>webshoots/<?php echo $main_dep_snap['snap_name']; ?>"></div>
					<?php } else { ?>
					<p>not exist or broken</p>
					<?php } ?>
				</td>
				<td style='vertical-align: top'>
					<?php $decode_com = json_decode($v->json_encode_com); ?>
					<?php if(count($decode_com) > 0) { ?>
						<?php foreach($decode_com as $k => $v) { ?>
							<?php $sec_dep_snap = $this->department_members_model->getLatestDepartmentScreen($v->sec_dep_chooser); ?>
							<?php if($sec_dep_snap['img_av_status']) { ?>
							<div style='margin-bottom: 10px;'><img style='width: 100%' src="<?php echo base_url() ?>webshoots/<?php echo $sec_dep_snap['snap_name']; ?>"></div>	
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
