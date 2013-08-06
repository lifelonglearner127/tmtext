<div class="modal-header">
	<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
	<h3>Recipients Control Panel</h3>
</div>
<div class="modal-body">
	<div id="recipients_control_panel_body" class='recipients_control_panel_body'>
		<?php if(count($rec) > 0) { ?>
			<table class='table table-striped'>
				<thead>
					<tr>
						<th><input type='checkbox' name="send_report_ch_all" id="send_report_ch_all"></th>
						<th>Recipients</th>
						<th>Day</th>
						<th>Controls</th>
					</tr>
				</thead>
				<tbody>
				<?php foreach($rec as $k => $v) { ?>
					<tr class='report_bean_line ready_res' data-id="<?php echo $v->id; ?>" data-email="<?php echo $v->email; ?>" data-day="<?php echo $v->day; ?>">
						<td><input type='checkbox' name="send_report_ch" id="send_report_ch_<?php echo $v->id; ?>"></td>
						<td><span class='recipients_control_panel_txt'><?php echo $v->email; ?></span></td>
						<td><span class='recipients_control_panel_txt'><?php echo ucfirst($v->day); ?></span></td>
						<td>
							<button type='button' onclick="sendRecipientReport('<?php echo $v->id; ?>', '<?php echo $v->email; ?>', '<?php echo $v->day; ?>')" class='btn btn-success btn-rec-ind-send'><i class='icon-fire'></i></button>
							<button type='button' onclick="deleteRecipient('<?php echo $v->id; ?>')" class='btn btn-danger btn-rec-remove'><i class='icon-remove'></i></button>
						</td>
					</tr>
				<?php } ?>
                <tr class="new_row">
                    <td>&nbsp;</td>
                    <td><input type="text" id="recipients_rec" name="recipients_rec" placeholder="recipients.."></td>
                    <td><select id="recipients_week_day" name="recipients_week_day">
                            <option value='monday' selected>Monday</option>
                            <option value='tuesday'>Tuesday</option>
                            <option value='wednesday'>Wednesday</option>
                            <option value='thursday'>Thursday</option>
                            <option value="friday">Friday</option>
                            <option value='saturday'>Saturday</option>
                            <option value='sunday'>Sunday</option>
                        </select></td>
                    <td><a href="javascript:void(0)" class="btn btn-success" onclick="submitEmailReportsConfig()"><i class='icon-plus'></i></a></td>
                </tr>
				</tbody>
			</table>
		<?php } else { ?>
		<p class='bold'>no recipients for reports sending</p>
		<?php } ?>
	</div>
</div>
<div class="modal-footer">
    <button onclick="newRecipient()" type='button' class="btn">New row</button>
	<?php if(count($rec) > 0) { ?>
		<button type='button' href="javascript:void(0)" onclick="sendEmailScreensToSelected()" class="btn btn-success btn-rec-all-send">Send to selected</button>
		<button type='button' href="javascript:void(0)" onclick="sendEmailScreensToAll()" class="btn btn-primary btn-rec-all-send">Send to all</button>
	<?php } else { ?>
		<button type='button' href="javascript:void(0)" class="btn btn-success disabled btn-rec-all-send">Send to selected</button>
		<button type='button' href="javascript:void(0)" class="btn btn-primary disabled btn-rec-all-send">Send to all</button>
	<?php } ?>
</div>

<script type='text/javascript'>
	$(document).ready(function() {
		// --- 'Recipients Control Panel' UI (start)
		var checked_count = $("input[type='checkbox'][name='send_report_ch']").length;
		$("#send_report_ch_all").on('change', function(e) {
			$(".report_bean_line").removeClass('selected');
			if($(e.target).is(":checked")) {
				$("input[type='checkbox'][name'send_report_ch']").attr('checked', true);
				$(".report_bean_line").addClass('selected');
			} else {
				$("input[type='checkbox'][name'send_report_ch']").removeAttr('checked');
				$(".report_bean_line").removeClass('selected');
			}
		});
		$("input[type='checkbox'][name'send_report_ch']").on('change', function(e) {
			setTimeout(function() {
				// ---- mark / unmark tr line as selected (start)
				if($(e.target).is(":checked")) {
					$(e.target).parent().parent().addClass('selected');
				} else {
					$(e.target).parent().parent().removeClass('selected');
				}
				// ---- mark / unmark tr line as selected (end)
				var count_s = 0;
				$("input[type='checkbox'][name='send_report_ch']").each(function(index, val) {
					if($(val).is(':checked')) count_s++;
				});
				if(checked_count == count_s) $("#send_report_ch_all").attr('checked', true);
				if(count_s == 0) $("#send_report_ch_all").removeAttr('checked'); 
			}, 100);
		});
		// --- 'Recipients Control Panel' UI (end)
	});
</script>