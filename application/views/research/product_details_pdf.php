<span class="pdf_header">Details</span><br /><br />
<table class="product_details" border="0" cellspacing="0" cellpadding="0">
    <thead>
        <tr>
            <th>Snap</th>
            <th>Date</th>
            <th>Product Name</th>
            <th>URL</th>
            <th>Word (S)</th>
            <th>Keywords(S)</th>
            <th>Word (L)</th>
            <th>Keywords(L)</th>
            <th>Duplicate Content</th>
            <th>Price</th>
        </tr>
    </thead>
    <tbody>
    <?php foreach ($report_details as $row) { ?>
        <?php $data = json_decode($row[11]); ?>
        <?php //$data_for_json = json_decode($row[11]); ?>
        <tr>
            <td class="snap"><?php echo (empty($data->snap) ? " " : "<img width='100' src='" . base_url() . "webshoots/" . $data->snap . "' />"); ?></td>
            <td class="date"><?php echo $row[1]; ?></td>
            <td class="name"><?php echo $row[2]; ?></td>
            <td class="url"><a href="<?php echo $data->url; ?>" target="_blank"><?php echo implode('<br/>', str_split($data->url, 90)); ?></a></td>
            <td><?php echo $row[4]; ?></td>
            <td class="seo_phrases"><?php echo $row[5]; ?></td>
            <td><?php echo $row[6]; ?></td>
            <td class="seo_phrases"><?php echo $row[7]; ?></td>
            <td><?php echo $row[8]; ?></td>
            <td class="price<?php if(strpos($row[9], 'hidden') > 0) echo ' red' ?> "><?php echo $row[9]; ?></td>
        </tr>
    <?php } ?>
    </tbody>
</table>