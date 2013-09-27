<div class='comparison_row'>
	<select class='sec_site_chooser' onchange="secSiteChooserHandler(this)">
		<option value='0'>Choose comparison site</option>
		<?php foreach ($sites_list as $val) { ?>
		<option value="<?php echo $val['id']; ?>" data-value="<?php echo $val['name_val']; ?>"><?php echo $val['name']; ?></option>
		<?php } ?>
	</select>
	<select style='display: none;' class='sec_dep_chooser'></select>
	<div style='display: none; margin-bottom: 10px;' class='comparison_row_cnt'>
		<button type='button' class='btn btn-success' onclick="addCompetitorRow(this)">Add Competitor</button>
	</div>
</div>