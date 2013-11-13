<link type="text/css" rel="stylesheet" href="<?php echo base_url(); ?>css/styles.css" />
<div class="tabbable">
    <ul class="nav nav-tabs jq-system-tabs">
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system'); ?>">General</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/sites_view'); ?>">Sites</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('site_crawler'); ?>">Site Crawler</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('brand/import'); ?>">Brands</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/batch_review'); ?>">Batch Review</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_compare'); ?>">Product Compare</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_productsmatch'); ?>">Product Match</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_reports'); ?>">Reports</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_logins'); ?>">Logins</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/keywords'); ?>">Keywords</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_rankings'); ?>">Rankings</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_pricing'); ?>">Pricing </a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/product_models'); ?>">Product models </a></li>
        <li class="active"><a data-toggle="tab" href="<?php echo site_url('system/snapshot_queue'); ?>">Snapshot Queue</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_uploadmatchurls');?>">Upload Match URLs</a></li>
    </ul>
    <div class="tab-content">
        <table id="records">
            <thead>
                <tr>
                    <th>Site Name</th>
                    <th>Product/Department Name</th>
                    <th>Url</th>
                    <th>Time Added</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($rows as $row): ?>
                    <tr>
                        <td><?= $row['site_name']; ?></td>
                        <td><?= $row['name']; ?></td>
                        <td><?= $row['url']; ?></td>
                        <td><?= $row['time_added']; ?></td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
</div>
<script type="text/javascript" >
    $(document).ready(function(){
        var snapshotQueueTbl = $( '#records' ).dataTable({"bJQueryUI": true,"bPaginate": true, "aaSorting": [[ 10, "desc" ]], 'bRetrieve':true});
    });
</script>