<?php if(count($rec) > 0) { ?>
	<table class='table table-striped'>
		<thead>
			<tr>
				<th>Recipients</th>
				<th>Day</th>
				<th>Controls</th>
			</tr>
		</thead>
		<tbody>
		<?php foreach($rec as $k => $v) { ?>
			<tr data-id="<?php echo $v->id; ?>">
				<td><span class='recipients_control_panel_txt'><?php echo $v->email; ?></span></td>
				<td><span class='recipients_control_panel_txt'><?php echo $v->day; ?></span></td>
				<td>
					<button type='button' onclick="sendRecipientReport('<?php echo $v->id; ?>', '<?php echo $v->email; ?>', '<?php echo $v->day; ?>')" class='btn btn-success btn-rec-ind-send'><i class='icon-fire'></i></button>
					<button type='button' onclick="deleteRecipient('<?php echo $v->id; ?>')" class='btn btn-danger btn-rec-remove'><i class='icon-remove'></i></button>
				</td>
			</tr>
		<?php } ?>
		</tbody>
	</table>
<?php } else { ?>
<p>no recipients</p>
<?php } ?>