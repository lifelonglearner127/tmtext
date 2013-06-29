<div class="tabbable">
  <ul class="nav nav-tabs jq-system-tabs">
	<li class=""><a data-toggle="tab" href="<?php echo site_url('system');?>">General</a></li>
	<li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_accounts');?>">New Accounts</a></li>
	<li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_roles');?>">Roles</a></li>
	<li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_users');?>">Users</a></li>
	<li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_compare');?>">Product Compare Interface</a></li>
	<li class=""><a data-toggle="tab" href="<?php echo site_url('site_crawler');?>">Site Crawler</a></li>
    <li class=""><a data-toggle="tab" href="<?php echo site_url('system/batch_review');?>">Batch Review</a></li>
    <li class="active"><a data-toggle="tab" href="<?php echo site_url('system/system_productsmatch');?>">Product Match</a></li>
  </ul>
  <div class="tab-content">
    <div id="tab8" class="tab-pane active">
    	<table id='pm_data_table' class='pm_data_table'>
    		<tbody>
    			<tr>
    				<td><input class='pm_data_table_tinput pmtt_url' type='text' placeholder='Type URL'></td>
    				<td><input class='pm_data_table_tinput pmtt_sku' type='text' placeholder='Type SKU'></td>
				</tr>
				<tr>
    				<td><input class='pm_data_table_tinput pmtt_url' type='text' placeholder='Type URL'></td>
    				<td><input class='pm_data_table_tinput pmtt_sku' type='text' placeholder='Type SKU'></td>
				</tr>
				<tr>
    				<td><input class='pm_data_table_tinput pmtt_url' type='text' placeholder='Type URL'></td>
    				<td><input class='pm_data_table_tinput pmtt_sku' type='text' placeholder='Type SKU'></td>
				</tr>
				<tr>
    				<td><input class='pm_data_table_tinput pmtt_url' type='text' placeholder='Type URL'></td>
    				<td><input class='pm_data_table_tinput pmtt_sku' type='text' placeholder='Type SKU'></td>
				</tr>
				<tr>
    				<td><input class='pm_data_table_tinput pmtt_url' type='text' placeholder='Type URL'></td>
    				<td><input class='pm_data_table_tinput pmtt_sku' type='text' placeholder='Type SKU'></td>
				</tr>
				<tr>
    				<td colspan='2'>
    					<button type='button' id="pm_tab_newrow_btn" class='btn btn-primary' onclick='addNewProductMatchRow();'>Add New Row</button>
    					<button type='button' id="pm_tab_save_btn" class='btn disabled' disabled='true' onclick='saveProductMatch();'>Save</button>
    				</td>
				</tr>
			</tbody>
		</table>
    </div>
  </div>
</div>

<script type='text/javascript'>

	$(document).ready(function() {

		$("#pm_data_table input[type=text]").keypress(function() {
			if(empty_check_validation()) {
				$("#pm_tab_save_btn").removeClass('disabled');
				$("#pm_tab_save_btn").removeAttr('disabled');
				if(!$("#pm_tab_save_btn").hasClass('btn-success')) {
					$("#pm_tab_save_btn").addClass('btn-success');
				}
			}
		});

		$("#pm_data_table input[type=text]").blur(function() {
			if(empty_check_validation()) {
				$("#pm_tab_save_btn").removeClass('disabled');
				$("#pm_tab_save_btn").removeAttr('disabled');
				if(!$("#pm_tab_save_btn").hasClass('btn-success')) {
					$("#pm_tab_save_btn").addClass('btn-success');
				}
			}
		});

		function empty_check_validation() {
			var res = false;
			$("#pm_data_table tr").each(function(index, value) {
				if( $.trim($("#pm_data_table tr").find('.pmtt_url').val()) !== "" && $.trim($("#pm_data_table tr").find('.pmtt_sku').val()) !== ""  ) {
					res = true;
				}
			});
			return res;
		}

	});
	
	function addNewProductMatchRow() {
		alert('ADD NEW ROW PLACEHOLDER');
	}

	function saveProductMatch() {
		alert('SAVE PLACEHOLDER');
	}
</script>
