<div class="tabbable">
		<?php $this->load->view('system/_tabs', array(
			'active_tab' => 'measure/product_models'
		)) ?>
    <div class="tab-content">
        <link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/smoothness/jquery-ui-1.8.2.custom.css" />
        <link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/styles.css" />
        <script type="text/javascript" src="<?php echo base_url();?>js/change_model.js"></script>
        <div class="row-fluid">
            <div id="ajaxLoadAni">
                <span>Loading...</span>
            </div>

            <!-- update form in dialog box -->
            <div id="updateDialog1" title="Update">
                <div>
                    <form action="" method="post">
                        <p>
                            <label for="title">Model:</label>
                            <input type="text" id="title" name="title" />
                        </p>

                        <input type="hidden" id="userId" name="id" />
                    </form>
                </div>
            </div>

            <!-- delete confirmation dialog box -->
            <div id="delConfDialog1" title="Confirm">
                <p>Are you sure you want to delete model<br><span class="imported_data_id_"></span>?</p>
                <input type="hidden" id="" name="del_im_id" />
            </div>


            <!-- message dialog box -->
            <div id="msgDialog"><p></p></div>
            
            
            <table id="tblModels" class="tblDataTable" >
                 <thead>
                 </thead>
                 <tbody>
                 </tbody>
             </table>
        </div>
    </div>
</div>
