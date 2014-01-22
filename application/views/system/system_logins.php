<div class="tabbable">
     <?php $this->load->view('system/_tabs', array(
		'active_tab' => 'system/system_logins'
	)) ?>
        
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
