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
            <li class="active"><a data-toggle="tab" href="<?php echo site_url('measure/product_models');?>">Product models </a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/snapshot_queue');?>">Snapshot Queue</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/sync_keyword_status');?>">Sync Keyword Status</a></li> 
        </ul>
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
