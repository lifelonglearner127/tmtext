<link type="text/css" rel="stylesheet" href="<?php echo base_url(); ?>css/styles.css" />
<div class="tabbable">
    <?php $this->load->view('system/_tabs', array(
		'active_tab' => 'system/snapshot_queue'
	)) ?>
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