<div class="tabbable">
    <ul class="nav nav-tabs jq-system-tabs">
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system');?>">General</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/sites_view');?>">Sites</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('site_crawler');?>">Site Crawler</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/batch_review');?>">Batch Review</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_compare');?>">Product Compare</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_productsmatch');?>">Product Match</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_reports');?>">Reports</a></li>
        <li class="active"><a data-toggle="tab" href="<?php echo site_url('system/system_logins');?>">Logins</a></li>
    </ul>
    
    <div class="tab-content">
        <div id="tab9" class="tab-pane active">
			echo 111
		</div>
	</div>
    
    <script type="text/javascript">
		$(function() {
			function last_logins(id_selected) {
				system_reports.empty();
				$.get(base_url + 'index.php/system/system_reports_get_all', {}, function(data){
					$.each(data.data, function(index, value){
						system_reports.append('<option value="'+value.id+'">'+value.name+'</option>');
					});
					reports_get_by_id(system_reports.val());
				});
				if (id_selected) {
					$('#system_reports option:eq('+id_selected+')').prop('selected', true);
					reports_get_by_id(id_selected);
				}
			}
		});
    </script>
    
</div>
