<div class="tabbable">
       <?php $this->load->view('system/_tabs', array(
		'active_tab' => 'system/bad_matches'
	)) ?>
    <div class="tab-content">
        <link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/smoothness/jquery-ui-1.8.2.custom.css" />
        <link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/styles.css" />
        <script type="text/javascript" src="<?php echo base_url();?>js/bad_matches.js"></script>
        <div class="row-fluid">
<!--            <div id="ajaxLoadAni">
                <span>Loading...</span>
            </div>-->

           
            <!-- delete confirmation dialog box -->
            <div id="delConfDialog1" title="Confirm">
                <p>Are you sure you want to delete this couple<br><span class="imported_data_id_"></span>?</p>
            </div>
            <!-- message dialog box -->
            <div id="msgDialog"><p></p></div>
            <table id="tblMatches" class="tblDataTable" >
                 <thead>
                 </thead>
                 <tbody>
                 </tbody>
             </table>
        </div>
    </div>
</div>
