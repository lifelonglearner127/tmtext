<?php 
	$file = realpath(BASEPATH . "../webroot/emails_logos/$email_logo");
    $file_size = filesize($file);
    if($file_size === false) {
    	$email_logo = 'default_logo.jpg';
    }
?>

<table>
	<tbody>
		<tr>
			<td>
				<img style='max-width: 240px;' src="<?php echo base_url() ?>/emails_logos/<?php echo $email_logo; ?>">
			</td>
		</tr>
		<tr>
			<td style='padding-top: 10px;'><p><?php echo $batch; ?></p></td>
		</tr>
	</tbody>
</table>