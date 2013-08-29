<p>Report screenshots in attachment. Preference day: <?php echo $day; ?>.</p>
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
