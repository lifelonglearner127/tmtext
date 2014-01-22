<div class="tabbable">
     <?php $this->load->view('system/_tabs', array(
		'active_tab' => 'system/sync_keyword_status'
	)) ?>
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