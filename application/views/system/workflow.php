<?php
$this->load->view('system/_tabs', array(
    'active_tab' => 'system/workflow'
))
?>

<div id ="workflow">

    <span id="open_operation" class="btn btn-success fileinput-button" style ="display: block; float: left"> Operations </span><br>
    <span id="open_processes" class="btn btn-success fileinput-button style" style ="display: block; float: left; margin-left: 5px;margin-top: -19px"> Processes </span><br>
    <div id ="operations">
        <select id ="sel_op">
            <option value="0">Select Operation</option>
        </select>
        <div id ="">
            <label id ="">Operation Title</label>
            <input type="text" id="opr_title" name="opr_title" />
            <input type="text" id="opr_url" name="opr_url" />
            <span id="create_operation" class="btn btn-success fileinput-button"> Add new</span>
            <button id="update_op" class="btn btn-success" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Update</button>
            <button id="delete_op" class="btn btn-danger" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Delete</button>
        </div>
    </div>   
    <div id ="processes">
        <select id ="processes_list">
            <option value="0">Select Process</option>
        </select>
        <label id ="process_name">Process Name</label>
        <input type="text" id="process_name" name="process_name" />
        <select id ="weeks">
            <option value="0">Select Day</option>
        </select>
        <select id ="actions" multiple="multiple" size="5">
<!--            <option value="0">Select Operations</option>-->
            <option value="1">Crawling</option>
            <option value="2">URL Import</option>
            <option value="2">Do stats</option>
        </select>
        <select id="workflow_batches" multiple="multiple" size="5">
<!--            <option value="0">Select Batch</option>-->
            <?php
            foreach ($batches as $batch) {
                ?>
                <option value="<?php echo $batch->id; ?>"><?php echo $batch->title; ?></option>
                <?php
            }
            ?>
        </select>
       

        <span id="create_process" class="btn btn-success fileinput-button"> Create new process </span>
        <button id="update_op" class="btn btn-success" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Update</button>
        <button id="delete_op" class="btn btn-danger" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Delete</button>

    </div>
</div>
<script>
    $(document).ready(function() {
        $('#operations').hide();
        $('#processes').hide();
        $('#open_operation').toggle(
                function() {
                    $('#operations').show();
                },
                function() {
                    $('#operations').hide();
                }
        );
        $('#open_processes').toggle(
                function() {
                    $('#processes').show();
                },
                function() {
                    $('#processes').hide();
                }
        );
            
        $("#create_operation").click(function(){
            var op_name = $("#opr_title").val();
            var op_url = $("#opr_url").val();
            if(op_name !== '' &&  op_url !== ''){
                
            }
            
        });
        $("#update_op").click(function(){
            var op_name = $("#opr_title").val();
            var op_url = $("#opr_url").val();
            if(op_name !== '' &&  op_url !== ''){
                
            }
            
        });
        $("#delete_op").click(function(){
            if($("#sel_op").val() !== 0){
                var op_id = $("#sel_op").val();
            }
        });
        
    });
</script>