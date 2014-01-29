<?php
//
$this->load->view('system/_tabs', array(
    'active_tab' => 'system/workflow'
))
?>

<div id ="workflow">

    <span id="open_operation" class="btn btn-success fileinput-button" style ="display: block; float: left">Open Operations </span><br>
    <span id="open_processes" class="btn btn-success fileinput-button style" style ="display: block; float: left; margin-left: 5px;margin-top: -19px">Open Processes </span><br>
    <div id ="operations">
        <form name="operations">
            <select id ="sel_op">
                <option value="0">Select Operation</option>
            </select>
            <div id ="">
                <label id ="">Operation Title</label>
                <input type="text" id="opr_title" name="opr_title" />
                <input type="text" id="opr_url" name="opr_url" />
                <select id ="param_type">
                    <option value="0">Select Parameter type</option>
                    <option value="Batch">Batch</option>
                    <option value="File">File</option>
                    <option value="None">None</option>
                </select>
                <span id="create_operation" class="btn btn-success fileinput-button"> Add new</span>
                <button id="update_op" class="btn btn-success" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Update</button>
                <button id="delete_op" class="btn btn-danger" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Delete</button>
                
        </form>    
    </div>
</div>   
<div id ="processes">
    <select id ="processes_list">
        <option value="0">Select Process</option>
    </select>
    <label id ="process_name">Process Name</label>
    <input type="text" id="process_name" name="process_name" />
    <select id ="days">
        <option value="">Select Day</option>
        <option value="0">Sunday</option>
        <option value="1">Monday</option>
        <option value="2">Tuesday</option>
        <option value="3">Wednesday</option>
        <option value="4">Thursday</option>
        <option value="5">Friday</option>
        <option value="6">Saturday</option>
    </select>
    <select id ="actions" multiple="multiple" size="5" >
        <option value="all">All</option>
        <option value="1">Crawling</option>
        <option value="2">URL Import</option>
        <option value="3">Do stats</option>
    </select>
    <select id="workflow_batches" multiple="multiple" size="5">
        <option value="all">All</option>
        <?php
        foreach ($batches as $batch) {
            ?>
            <option value="<?php echo $batch->id; ?>"><?php echo $batch->title; ?></option>
            <?php
        }
        ?>
    </select>
    <select id ="import_file_name">
        <option value="0">Select import file</option>
    </select>

    <span id="create_process" class="btn btn-success fileinput-button"> Create new process </span>
    <button id="update_process" class="btn btn-success" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Update</button>
    <button id="delete_process" class="btn btn-danger" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Delete</button>

</div>
</div>
