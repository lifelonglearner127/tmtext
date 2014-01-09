<div class="tabbable">
    <ul class="nav nav-tabs jq-system-tabs">
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system');?>">General</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/sites_view');?>">Sites</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('site_crawler');?>">Site Crawler</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('site_crawler/instances_list');?>">Crawler Instances <?php $this->load->helper("crawler_instances_helper"); echo crawler_instances_number();?></a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_uploadmatchurls');?>">Upload Match URLs</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_dostatsmonitor');?>">Do_stats Monitor</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('brand/import');?>">Brands</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/batch_review');?>">Batch Review</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_compare');?>">Product Compare</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_productsmatch');?>">Product Match</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_reports');?>">Reports</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_logins');?>">Logins</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/keywords');?>">Keywords</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_rankings');?>">Rankings</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_pricing');?>">Pricing </a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/product_models');?>">Product models </a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/snapshot_queue');?>">Snapshot Queue</a></li>
            <li class="active"><a data-toggle="tab" href="<?php echo site_url('system/sync_keyword_status');?>">Sync Keyword Status</a></li>   
    </ul>
    <div class="tab-content">
            <?php echo form_dropdown('batches_list', $batches_list, array(), ' class="sk_batches_list" id="sk_batches_list" style="width: 207px;float:left;margin-right: 20px;margin-top: 10px;"'); ?>
            <button type="button" class="btn btn-success" onclick="kwCommonAddToQueue();" >Start</button>
            <button type="button" class="btn btn-success" onclick="stopQueue();" >Stop</button>
            <span id="queueCount" style="display: none;" ></span>
    </div>
</div>
<script type="text/javascript" >
    function kwCommonAddToQueue() {
        $('#queueCount').html('');
        var bid = $("#sk_batches_list > option:selected").val();
        if(bid != '0'){
            $.post(base_url + 'index.php/system/kw_common_add_to_queu', {'cpage': 1, 'bid': bid, 'q_mode': 'all', shell_queue: 'true'}, function(data) {
                console.log('data11111111111');
            });	
        }
        setTimeout(function(){
            var intervalClear = setInterval(function(){
                $.post(base_url + 'index.php/system/check_queue_count', {}, function(data) {
                    if(data.trim() == 'Remaining 0 items.'){
                        clearInterval(intervalClear);
                        data = 'Done';
                    }
                    $('#queueCount').html(data);
                    $('#queueCount').show();
                });	
            },1000);
        },3000);
    }
    function stopQueue(){
        $.post(base_url + 'index.php/system/stopQueue', {}, function(data) {
            console.log('data2222222222');
        });
    }
</script>