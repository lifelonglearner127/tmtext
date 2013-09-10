<!-- <img src="<?php echo base_url() ?>/img/content_analytics_logo.jpg"> -->
<?php 
	$file = realpath(BASEPATH . "../webroot/emails_logos/$email_logo");
    $file_size = filesize($file);
    if($file_size === false) {
    	$email_logo = 'default_logo.jpg';
    }
?>
<img style='max-width: 240px;' src="<?php echo base_url() ?>/emails_logos/<?php echo $email_logo; ?>">

<?php if(count($screens) > 0) { ?>
	<?php 
		$item_per_row = 2;
		$pro_rows = ceil(count($screens)/$item_per_row);
	?>
	<table>
		<tbody>
			<?php for($i = 1; $i <= $pro_rows; $i++) { ?>
			<tr>
				<?php $position = $item_per_row*($i-1); ?>
				<?php $project_row = array_slice($screens, $position, $item_per_row); ?>
				<?php foreach($project_row as $k => $v) { ?>
					<td style='padding: 15px;'><div style='width: 400px;'><img style='width: 100%' src="<?php echo $v['link']; ?>"></div></td>
				<?php } ?>
			</tr>
			<?php } ?>
		</tbody>
	</table>
<?php } ?>
