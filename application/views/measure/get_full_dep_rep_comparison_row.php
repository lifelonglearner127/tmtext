<tr data-id="<?php echo $helpers_model->random_string_gen(11); ?>">
	<td>
		<input type='checkbox' class='cat_report_ch'><br>
		<button class='btn btn-danger small_custom_icon_btn mt_5' onclick="removeFullRow(this)"><i class='icon-remove-circle icon-white'></i></button>
	</td>
	<td>
		<?php if (count($sites_list) > 0) { ?>
			<select class='main_site_chooser' onchange="mainSiteChooserHandler(this)">
				<option value='0'>Choose Site</option>
				<?php foreach ($sites_list as $val) { ?>
				<option value="<?php echo $val['id']; ?>" data-value="<?php echo $val['name_val']; ?>"><?php echo $val['name']; ?></option>
				<?php } ?>
			</select>
			<select style='display: none;' class='main_dep_chooser'></select>
		<?php } ?>
	</td>
	<td>
		<div class='comparison_row'>
			<select class='sec_site_chooser' onchange="secSiteChooserHandler(this)">
				<option value='0'>Choose comparison site</option>
				<?php foreach ($sites_list as $val) { ?>
				<option value="<?php echo $val['id']; ?>" data-value="<?php echo $val['name_val']; ?>"><?php echo $val['name']; ?></option>
				<?php } ?>
			</select>
			<select style='display: none;' class='sec_dep_chooser'></select>
			<label style='display: none; margin-top: 0px !important;' class="checkbox"><input type="checkbox"> Select competitor</label>
			<div style='display: none; margin-bottom: 10px;' class='comparison_row_cnt'>
				<button type='button' class='btn btn-success' onclick="addCompetitorRow(this)">Add Competitor</button>
			</div>
		</div>
	</td>
</tr>

<script type='text/javascript'>
	
	$(document).ready(function() {
		$("#cat_report_ch_all").on('change', function(e) {
			if($(e.target).is(":checked")) {
				$('.cat_report_ch').attr('checked', true);
				$('#btn_dep_rep_save_set').removeAttr('disabled');
			} else {
				$('.cat_report_ch').removeAttr('checked');
				$('#btn_dep_rep_save_set').attr('disabled', true);
			}
		});

		$(".cat_report_ch").on('change', function(e) {
			var checked_count = $(".cat_report_ch").length;
			setTimeout(function() {
				var count_s = 0;
				$(".cat_report_ch").each(function(index, val) {
					if($(val).is(':checked')) count_s++;
				});
				if(checked_count == count_s) {
					$("#cat_report_ch_all").attr('checked', true);
				} else {
					$("#cat_report_ch_all").removeAttr('checked');
				}
				if(count_s == 0) {
					$("#cat_report_ch_all").removeAttr('checked');
					$("#btn_dep_rep_save_set").attr('disabled', true);
				} else {
					$('#btn_dep_rep_save_set').removeAttr('disabled');
				}
			}, 100);
		});

	});

</script>