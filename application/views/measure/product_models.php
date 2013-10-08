<div class="tabbable">
       <ul class="nav nav-tabs jq-system-tabs">
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system');?>">General</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/sites_view');?>">Sites</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('site_crawler');?>">Site Crawler</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('brand/import');?>">Brands</a></li>
            <li ><a data-toggle="tab" href="<?php echo site_url('system/batch_review');?>">Batch Review</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_compare');?>">Product Compare</a></li>
            <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_productsmatch');?>">Product Match</a></li>
           <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_reports');?>">Reports</a></li>
           <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_logins');?>">Logins</a></li>
           <li class=""><a data-toggle="tab" href="<?php echo site_url('system/keywords');?>">Keywords</a></li>
           <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_rankings');?>">Rankings</a></li>
           <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_pricing');?>">Pricing </a></li>
           <li class="active"><a data-toggle="tab" href="<?php echo site_url('measure/product_models');?>">Product models </a></li>
        </ul>
    <div class="tab-content">
        <link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/smoothness/jquery-ui-1.8.2.custom.css" />
        <link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/styles.css" />
        <div class="row-fluid">
            <div id="ajaxLoadAni">
                <span>Loading...</span>
            </div>

            <div id="tabs" class="mt_10">

                <ul>
                    <li><a href="#read">Review</a></li>
                    <!--li><a href="#create"></a></li-->
                </ul>

                <div id="read">
                    <table id="records">
                        <thead>
                        <tr>
                            <th>Product name</th>
                            <th>URL</th>
                            <th>Model</th>
                                                      
                            <th><div class="draggable">Actions</div></th>
                        </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
                <div id="create">
                </div>

            </div> <!-- end tabs -->

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
 
            <script type="text/template" id="readTemplate1">
                 <tr id="${imported_data_id}">
                    <td class="name-width"><span>${product_name}</span></td>
                    <td class="url-width"><span>${url}</span></td>
                    <td class="modle-width"><span>${model}</span></td>
                 <td nowrap><a class="updateBtn icon-edit" style="float:left;" href="${updateLink}"></a>
                        <a class="deleteBtn icon-remove ml_5" href="${deleteLink}"></a>
                    </td>
                </tr>
            </script>

            <script type="text/javascript" src="<?php echo base_url();?>js/change_model.js"></script>
        </div>
    </div>
</div>
<style>
     /*#records  td{
        width: 100px !important;
        word-wrap: break-word;
    } */
</style>
