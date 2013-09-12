<span class="pdf_header">Recommendations</span><br /><br />
<table class="product_recommendations" border="0" cellspacing="0" cellpadding="0">
    <thead>
        <tr>
            <th>Product Name</th>
            <th>URL</th>
            <th>Recommendations</th>
        </tr>
    </thead>
    <tbody>
        <?php foreach ($report_details as $row) { ?>
            <?php $data = json_decode($row[10]); ?>
            <tr>
                <td class="name"><?php echo $row[1]; ?></td>
                <td class="url"><a href="<?php echo $data->url; ?>" target="_blank"><?php echo implode('<br/>', str_split($data->url, 120)); ?></a></td>
                <td class="recommendations"><?php echo $row[9]; ?></td>
            </tr>
        <?php } ?>
    </tbody>
</table>
<?php
