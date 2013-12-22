<?php 
	$email_logo = $d['email_logo'];
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
			<td style='padding-top: 10px;'><p>A new batch has been created in Content Analytics.</p></td>
		</tr>
		<tr>
			<td style='padding-top: 10px;'><p>The batch name is: <?php echo $d['batch']; ?></p></td>
		</tr>
		<tr>
			<td style='padding-top: 10px;'><p>The batch was created at: <?php echo date('Y/m/d H:i:s', time()); ?></p></td>
		</tr>
		<tr>
			<td style='padding-top: 10px;'><p>The customer is: <?php echo $d['customer_name']; ?></p></td>
		</tr>
	</tbody>
</table>