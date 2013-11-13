<div class="tabbable">
    <ul class="nav nav-tabs jq-system-tabs">
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system');?>">General</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/sites_view');?>">Sites</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('site_crawler');?>">Site Crawler</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('brand/import');?>">Brands</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/batch_review');?>">Batch Review</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_compare');?>">Product Compare</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_productsmatch');?>">Product Match</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_reports');?>">Reports</a></li>
        <li class="active"><a data-toggle="tab" href="<?php echo site_url('system/system_logins');?>">Logins</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/keywords');?>">Keywords</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_rankings');?>">Rankings</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_pricing');?>">Pricing </a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/product_models');?>">Product models </a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/snapshot_queue');?>">Snapshot Queue</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_uploadmatchurls');?>">Upload Match URLs</a></li>
    </ul>
        
    <link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/styles.css" />
    <div class="tab-content">
        <div id="tab9" class="tab-pane active">
			<table id="records" style="width: 893px;" class="dataTable" aria-describedby="records_info">
				<thead>
					<tr role="row">
						<th class="ui-state-default" tabindex="0" rowspan="1" colspan="1" aria-label="Product Name: activate to sort column ascending" style="width: 308px;">
							<div class="DataTables_sort_wrapper">First Name</div>
						</th>
						<th class="ui-state-default" tabindex="0" rowspan="1" colspan="1" aria-label="URL: activate to sort column ascending" style="width: 532px; height: 30px;">
							<div class="DataTables_sort_wrapper">Email</div>
						</th>
						<th class="ui-state-default" tabindex="0" rowspan="1" colspan="1" aria-label="URL: activate to sort column ascending" style="width: 532px; height: 30px;">
							<div class="DataTables_sort_wrapper">Date</div>
						</th>
					</tr>
				</thead>                     
					<tbody class="logins_list" role="alert" aria-live="polite" aria-relevant="all">
					</tbody>
			</table>
		</div>
	</div>
</div>

<script type="text/javascript">
	$(function() {
		function last_logins() {
			$.get(base_url + 'index.php/system/system_last_logins', {}, function(data){
				var tr_class = 'even';
				$.each(data.data, function(index, value){
					if( tr_class == 'odd' ) tr_class = 'even';
					else	tr_class = 'odd';
					
					var time = value.last_login
					var curdate = new Date(null);
					curdate.setTime( time*1000 );
					var date_login = curdate.toLocaleString();
					
					var logins = '<tr class="'+tr_class+'"><td>'+value.first_name+'</td><td>'+value.email+'</td><td>'+date_login+'</td></tr>';
					$('.logins_list').append(logins);
				});
			});
		}
		last_logins();
	});
</script>
