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
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_logins');?>">Logins</a></li>
        <li class="active"><a data-toggle="tab" href="<?php echo site_url('system/keywords');?>">Keywords</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_rankings');?>">Rankings</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_pricing');?>">Pricing </a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/product_models');?>">Product models </a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/snapshot_queue');?>">Snapshot Queue</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_uploadmatchurls');?>">Upload Match URLs</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_dostatsmonitor');?>">Do_stats Monitor</a></li>
    </ul>
        
    <link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/styles.css" />
     <div class="info-message text-success"></div>

    <!--- META KEYWORDS RANKING STUFFS (START) -->
    <div class='row-fluid'>
        <div class='alert' style='margin-bottom: 0px;'>Meta Keywords Ranking Section</div>
        <?php echo form_dropdown('batches_list', $batches_list, array(),' class="sk_batches_list" id="sk_batches_list" style="width: 207px;float:left;margin-right: 20px;margin-top: 10px;"'); ?>
        <select name='kw_show_words_mode' id='kw_show_words_mode' style='display: none; margin-top: 10px;'>
            <option value='title'>Title</option>
            <option value='meta'>Meta</option>
        </select>  
    </div>
    <div id="overall_meta_kw_pager_holder">
        <div id='meta_kw_pager_holder' class='row-fluid pagination'></div>
        <div class='row-fluid' id='sk_batches_list_data'>&nbsp;</div>
    </div>
    <div class='row-fluid'><hr/></div>
    <!--- META KEYWORDS RANKING STUFFS (END) -->

    <div class="row-fluid">
        <div style="float: left;width: 25%;">
        <p>New keyword</p>
        <input type="text" id="new_keyword" name="new_keyword">
        <p>New volume(number)</p>
        <input type="text" style="float: left;" id="new_volume" name="new_volume">
            <p class="heading_text">New search_engine </p>
            <?php  echo form_dropdown('search_engine', $search_engine, array(),' class="search_engine_select" style="width: 207px;float:left;margin-right: 20px;margin-top: 10px;"'); ?>       
        </div>
        <div style="float: left;width: 25%;">

                <p>New region</p>
                <?php  echo form_dropdown('regions_list', $regions, array(),'class="region_select"  style="width: 200px;margin-right:float:left; 20px;"'); ?>

 
                <p>New data_source_name</p>
                <?php  echo form_dropdown('data_source_name_list', $keyword_data_sources, array(),'class="data_source_name_select"  style="width: 200px;margin-right:float:left; 20px;"'); ?>
        
            <button id="btn_new_keyword" style="margin-bottom: 11px;float:left;margin-top: 28px;margin-left: 10px;" class="btn btn-primary" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Add</button>
        </div>    
        
        <div class="clear-fix"></div>
    </div>
    
    
    
    
    <div class="tab-content">
        <div id="tab9" class="tab-pane active">
			<table id="records" style="width: 893px;" class="dataTable" aria-describedby="records_info">
				<thead>
					<tr role="row">
						<th class="ui-state-default" tabindex="0" rowspan="1" colspan="1" aria-label="Product Name: activate to sort column ascending" style="width: 308px;">
							<div class="DataTables_sort_wrapper">keyword</div>
						</th>
						<th class="ui-state-default" tabindex="0" rowspan="1" colspan="1" aria-label="URL: activate to sort column ascending" style="width: 532px; height: 30px;">
							<div class="DataTables_sort_wrapper">volume</div>
						</th>
                                                <th class="ui-state-default" tabindex="0" rowspan="1" colspan="1" aria-label="Product Name: activate to sort column ascending" style="width: 308px;">
							<div class="DataTables_sort_wrapper">search_engine</div>
						</th>
						<th class="ui-state-default" tabindex="0" rowspan="1" colspan="1" aria-label="URL: activate to sort column ascending" style="width: 532px; height: 30px;">
							<div class="DataTables_sort_wrapper">region</div>
						</th>
						<th class="ui-state-default" tabindex="0" rowspan="1" colspan="1" aria-label="URL: activate to sort column ascending" style="width: 532px; height: 30px;">
							<div class="DataTables_sort_wrapper">data_source_name</div>
						</th>                                                
                                               
						<th class="ui-state-default" tabindex="0" rowspan="1" colspan="1" aria-label="URL: activate to sort column ascending" style="width: 532px; height: 30px;">
							<div class="DataTables_sort_wrapper">Date</div>
						</th>
					</tr>
				</thead>                     
					<tbody class="keywords_list" role="alert" aria-live="polite" aria-relevant="all">
					</tbody>
			</table>
	  </div>
      </div>
</div>

<div class="modal hide fade ci_hp_modals" id='loading_kw_meta_selection'>
    <div class="modal-body">
        <p><img src="<?php echo base_url();?>img/loader_scr.gif">&nbsp;&nbsp;&nbsp;Please wait...</p>
    </div>
</div>

<script type="text/javascript">
	$(function() {

        // === META KEYWORDS RANKING STUFFS (START)
        function getMetaKeysBatchData(bid, cpage) {
            cpage = parseInt(cpage);
            var v_mode_option = $("#kw_show_words_mode > option:selected").val();
            $.post(base_url + 'index.php/system/system_get_mkw_info', {'bid': bid, 'cpage': cpage, 'v_mode_option': v_mode_option}, function(d) {
                $("#loading_kw_meta_selection").modal('hide');
                $("#overall_meta_kw_pager_holder").html(d);
                $("#kw_show_words_mode").show();
            });
        }
        $("#sk_batches_list").change(function(e) {
            var bid = $(e.target).val();
            $("#loading_kw_meta_selection").modal('show');
            getMetaKeysBatchData(bid, 1);
        });
        $("#kw_show_words_mode").change(function(e) {
            $(".title_keys_kw_section, .meta_keys_kw_section").hide();
            if($(this).val() === 'meta') {
                $(".meta_keys_kw_section").show();
            } else if($(this).val() === 'title') {
                $(".title_keys_kw_section").show();
            }
        });
        // === META KEYWORDS RANKING STUFFS (END)

        var tr_class = 'even';
        
		function system_keywords() {
			$.get(base_url + 'index.php/system/system_keywords', {}, function(data){
				
				$.each(data.data, function(index, value){
					if( tr_class == 'odd' ) tr_class = 'even';
					else	tr_class = 'odd';
					
					var time = value.create_date
					var curdate = new Date(null);
					curdate.setTime( time*1000 );
					var date_keyword = curdate.toLocaleString();
					
					var keywords = '<tr class="'+tr_class+'"><td>'+value.keyword+'</td><td>'+value.volume+'</td><td>'+value.search_engine+'</td><td>'+value.region+'</td><td>'+value.data_source_name+'</td><td>'+date_keyword+'</td></tr>';
					$('.keywords_list').append(keywords);
				});
			});
		}
		system_keywords();
                
                
	var new_search_engine = 1;
        $(".search_engine_select").live('change', function() {  
            new_search_engine = $(this).val();
        });
	var new_region = 1;
        $(".region_select").live('change', function() {       
            new_region = $(this).val();
        });  
        var new_data_source_name = 1;
        $(".data_source_name_select").live('change', function() {       
            new_data_source_name = $(this).val();
        });
        
        
        $('button#btn_new_keyword').click(function(){

            var new_keyword = $.trim($('#new_keyword').val());
            var new_volume = $.trim($('#new_volume').val());
            if(new_keyword !== "") new_keyword.replace(/<\/?[^>]+(>|$)/g, "");
            if(new_volume !== "") new_volume.replace(/<\/?[^>]+(>|$)/g, "");           
            if($('#new_keyword').val() != '' || $('#new_volume').val() != ''){  
                var new_keywords = {
                    new_keyword: new_keyword,
                    new_volume: new_volume,
                    new_search_engine: new_search_engine,
                    new_region: new_region,
                    new_data_source_name: new_data_source_name
                   
                };
                    
                    $.post(base_url + 'index.php/system/add_new_keywords',new_keywords, function(data){
                        $(".info-message").append(data.message);
                        $(".info-message").fadeOut(7000);
                      if( tr_class == 'odd' ) tr_class = 'even';
			else	tr_class = 'odd';
                       
                        $.each(data.data, function(index, value){
                            var time = value.create_date;
                            var curdate = new Date(null);
                            curdate.setTime( time*1000 );
                            var date_keyword = curdate.toLocaleString();
                            var keywords = '<tr class="'+tr_class+'"><td>'+value.keyword+'</td><td>'+value.volume+'</td><td>'+value.search_engine+'</td><td>'+value.region+'</td><td>'+value.data_source_name+'</td><td>'+date_keyword+'</td></tr>';
                            $('.keywords_list').prepend(keywords);  
                        });
                        
                       });
                $('#new_keyword').val('');
                $('#new_volume').val('');                                                  
                }else{                  
                $(".info-message").append("keyword was not added");
                $(".info-message").fadeOut(7000);                
                }

                 
                return false;
            });
       });     
        
</script>
