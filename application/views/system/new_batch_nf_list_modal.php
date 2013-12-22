<div class="modal-header">
	<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
	<h3 style="background-color: #fff;">Batch Creation Recepients List</h3>
</div>
<div class="modal-body" style="overflow: hidden !important;">
	<?php if(count($rec_list) > 0) { ?>
		<table>
			<tbody>
				<?php foreach($rec_list as $k => $v) { ?>
					<tr>
						<td style='padding-bottom: 15px;'><?php echo $v; ?></td>
					</tr>
				<?php } ?>
			</tbody>
		</table>
	<?php } else { ?>
		<p>no any recepients</p>
	<?php } ?>
</div>