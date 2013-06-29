<div class="main_content_other"></div>
<div class="tabbable">
    <ul class="nav nav-tabs jq-research-tabs">
        <li class=""><a data-toggle="tab" href="<?php echo site_url('research');?>">Edit</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('research/research_batches');?>">Review</a></li>
        <li class="active"><a data-toggle="tab" href="<?php echo site_url('research/research_reports');?>">Reports</a></li>
    </ul>
    <div class="tab-content research_batches">
        <link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/smoothness/jquery-ui-1.8.2.custom.css" />
        <link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/styles.css" />
        <script>

            $(function() {
                $( ".draggable" ).draggable();
            });
        </script>
   </div>      

