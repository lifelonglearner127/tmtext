<?php $this->load->view('system/_tabs', array(
		'active_tab' => 'system/workflow'
)) ?>

<div id ="workflow">
    <label id ="process_name">Process Name</label>
    <input type="text" id="process_name" name="process_name" />
    <select id ="weeks">
        <option value="0">Select Day</option>
    </select>
    <select id="workflow_batches" >
        <option value="0">Select Batch</option>
        <?php
            foreach($batches as $batch){
        ?>
        <option value="<?php echo $batch->id;?>"><?php echo $batch->title;?></option>
        <?php
            }
        ?>
   </select>
        <select id ="actions">
            <option value="0">Select Operations</option>
            <option value="1">Crawling</option>
            <option value="2">URL Import</option>
            <option value="2">Do stats</option>
        </select>
    
    <span id="create_process" class="btn btn-success fileinput-button"> Create new process </span>
</div>         