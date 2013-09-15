<style type="text/css">
    .dropdown-menu {
        max-height: 350px;
        overflow: hidden;
        overflow-y: auto;
    }
    .tab-content{
        min-height:400px;
    }
    .temp_li{
        display: inline;
        font-size: 18px;
    }
    #departmentDropdown{
        padding-left:31px;
    }
    #departmentDropdownSec{
        margin-right:10px;
    }
    .DataTables_sort_icon  {
        position: absolute;
        right: -4px;
        top: 4px;
    }
    #departments_content div{
        margin-left:10px;
    }
    #departments_content{
        margin-top:10px;
        width:430px;
        display: block;
        overflow: auto;
    }
    #dataTableDiv1 .dataTables_filter input, #dataTableDiv2 .dataTables_filter input { width: 150px }
    #hp_boot_drop_sec{ display: block!important;float:right;padding-right: 31px; }
</style>
<div class="tabbable">
    <ul class="nav nav-tabs jq-measure-tabs">
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure'); ?>">Home Pages</a></li>
        <li class="active"><a data-toggle="tab" href="<?php echo site_url('measure/measure_departments'); ?>">Categories</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_products'); ?>">Products</a></li>
        <!--<li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_social'); ?>">Social</a></li>-->
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_pricing'); ?>">Pricing</a></li>
        <li class='pull_right_navlink'><a href="javascript:void(0)" onclick="viewRecipientsList()">Configure Recipients</a></li>
    </ul>



    <div class="tab-content">


        <div style="text-align: center;"><span style="font-weight: bold; float: right; margin-right: 10px;">Compare with: </span></div>
        <div class="row-fluid home_pages">
            <div class='span12 head_section'>

                <div class='head_line_2'>
                    <!--div class="span2">View Reports for:</div-->
                    <div style="float:left">
                        <!-- <ul class="ml_10 pull-left" style="float:left">
                             <li class="temp_li"><a href="#" style="text-decoration: underline;">Your Watchlists</a></li>
                             <li class="temp_li ml_50"><a href="#">Best-sellers</a></li>
                             <li class="temp_li ml_50"><a href="#">Entire site</a></li>
                         </ul>
                        -->

                        <?php
                        if ($this->ion_auth->is_admin($this->ion_auth->get_user_id())) {
                            if (count($sites_list) > 0) {
                                ?>
                                <div id="hp_boot_drop" style="float:left;margin-left:8px" class="btn-group <?php echo $dropup; ?> hp_boot_drop  mr_10">
                                    <button class="btn btn-danger btn_caret_sign" >Choose Site</button>
                                    <button class="btn btn-danger dropdown-toggle" data-toggle="dropdown">
                                        <span class="caret"></span>
                                    </button>
                                    <ul class="dropdown-menu">
                                        <?php foreach ($sites_list as $val) { ?>
                                            <li><a data-item="<?php echo $val['id']; ?>" data-value="<?php echo $val['name_val']; ?>" href="javascript:void(0)"><?php echo $val['name']; ?></a></li>
        <?php } ?>
                                    </ul>
                                </div>
                            <?php
                            }
                        }
                        ?>
                        <div id="departmentDropdown"  class="btn-group" style="display: none">
                            <button id="departmentDropdown_first" class="btn btn-danger btn_caret_sign1" style="width:165px" >Choose Department</button>
                            <button class="btn btn-danger dropdown-toggle" data-toggle="dropdown">
                                <span class="caret"></span>
                            </button>
                            <ul class="dropdown-menu" >
                            </ul>
                        </div>
                    </div>

                    <!-- Compare with Begin-->



                    <div style="float:right;">
                        <div id="departmentDropdownSec" style="float:right;display: none"  class="btn-group">
                            <button id="departmentDropdownSec_first" class="btn btn-danger btn_caret_sign_sec1" style="width:165px" >Choose Department</button>
                            <button class="btn btn-danger dropdown-toggle" data-toggle="dropdown">
                                <span class="caret"></span>
                            </button>
                            <ul class="dropdown-menu" >
                            </ul>
                        </div>
                        <?php
                        if ($this->ion_auth->is_admin($this->ion_auth->get_user_id())) {
                            if (count($sites_list) > 0) {
                                ?>
                                <div id="hp_boot_drop_sec"  class="btn-group <?php echo $dropup; ?> hp_boot_drop_sec  mr_10">
                                    <button class="btn btn-danger btn_caret_sign_sec" >Choose Site</button>
                                    <button class="btn btn-danger dropdown-toggle" data-toggle="dropdown">
                                        <span class="caret"></span>
                                    </button>
                                    <ul class="dropdown-menu">
                                    <?php foreach ($sites_list as $val) { ?>
                                            <li><a data-item="<?php echo $val['id']; ?>" data-value="<?php echo $val['name_val']; ?>" href="javascript:void(0)"><?php echo $val['name']; ?></a></li>
                                    <?php } ?>
                                    </ul>
                                </div>
                            <?php
                            }
                        }
                        ?>
                    </div>



                    <!--Compare with END -->
                </div>
            </div>
            <div class="clear"></div>
        </div>


        <div id="departments" >
            <div id="departments_content">
            </div>
        </div>



        <div class="row-fluid home_pages">
            <!-- Table for results -->
            <link type="text/css" rel="stylesheet" href="<?php echo base_url(); ?>css/smoothness/jquery-ui-1.8.2.custom.css" />
            <link type="text/css" rel="stylesheet" href="<?php echo base_url(); ?>css/styles.css" />

            <div class="table_results">
                <div id="tabs"  class="mt_10" style="overflow: hidden;display: none;" >

                    <div id="dataTableDiv1" style="width: 48%;float: left;" >
                        <table id="records" >
                            <thead>
                                <tr>
                                    <th>Categories ()</th>
                                    <th>Items</th>
                                    <th>Keyword Density</th>
                                    <th>Words</th>
                                </tr>
                            </thead>
                            <tbody>
                            </tbody>
                        </table>

                    </div>
                    <div id="dataTableDiv2" style="width: 48%;float: left;margin-left: 35px;" >
                        <table id="recordSec"  >
                            <thead>
                                <tr>
                                    <th>Categories ()</th>
                                    <th>Items</th>
                                    <th>Keyword Density</th>
                                    <th>Words</th>
                                </tr>
                            </thead>
                            <tbody>
                            </tbody>
                        </table>
                    </div>

                </div> <!-- end tabs -->

                <div id="ajaxLoadAni">
                    <span>Loading...</span>
                </div>                     <!-- message dialog box -->
                <div id="msgDialog"><p></p></div>

                <script type="text/javascript" src="<?php echo base_url(); ?>js/jquery-templ.js"></script>
                <script type="text/javascript" src="<?php echo base_url(); ?>js/jquery.validate.min.js"></script>
                <script type="text/javascript" src="<?php echo base_url(); ?>js/jquery.dataTables.min.js"></script>

                <!--script type="text/template" id="readTemplate">
                    <tr id="${id}">
                        <td>${rank}</td>
                        <td>${product_name}</td>
                        <td>${url}</td>
                        <td nowrap><a class="updateBtn icon-edit" style="float:left;" href="${updateLink}"></a>
                            <a class="deleteBtn icon-remove ml_5" href="${deleteLink}"></a>
                        </td>
                    </tr>
                </script-->

                <script type="text/javascript" src="<?php echo base_url(); ?>js/measure_department.js"></script>
                <script type='text/javascript' src="<?php echo base_url();?>js/ci_home_pages.js"></script>
            </div>
            <!-- End of table for results -->
            <div class="clear"></div>
        </div>
    </div>
</div>

<!-- MODALS (START) -->
<div class="modal hide fade ci_hp_modals crawl_launch_panel" id='recipients_control_panel_modal'></div>

<div class="modal hide fade ci_hp_modals" id='loader_emailsend_modal'>
    <div class="modal-body">
        <p><img src="<?php echo base_url();?>img/loader_scr.gif">&nbsp;&nbsp;&nbsp;Sending report. Please wait...</p>
    </div>
</div>

<div class="modal hide fade ci_hp_modals" id='success_emailsend_modal'>
    <div class="modal-body">
        <p>Report sent.</p>
    </div>
</div>

<div class="modal hide fade ci_hp_modals" id='configure_email_reports_success'>
    <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
        <h3>Reports Configuration Saved</h3>
    </div>
    <div class="modal-body">
        <p><span>Email configuration successfully saved!</span> <span>Use</span> <a href='javascript:void(0)' onclick='redirectToRecipientsListAfterAdd()' >'Recipients List'</a> <span>button to view results.</span></p>
    </div>
    <div class="modal-footer">
        <a href="javascript:void(0)" class="btn" data-dismiss="modal">Close</a>
    </div>
</div>
<!-- MODALS (END) -->

