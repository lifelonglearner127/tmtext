<span class="pdf_header">Details</span><br /><br />
<table class="product_details" border="0" cellspacing="0" cellpadding="0">
    <thead>
        <tr>
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
        <?php $data = json_decode($row[10]); ?>
        <tr>
            <td class="date"><?php echo $row[0]; ?></td>
            <td class="name"><?php echo $row[1]; ?></td>
            <td class="url"><a href="<?php echo $data->url; ?>" target="_blank"><?php echo implode('<br/>', str_split($data->url, 135)); ?></a></td>
            <td><?php echo $row[3]; ?></td>
            <td class="seo_phrases"><?php echo $row[4]; ?></td>
            <td><?php echo $row[5]; ?></td>
            <td class="seo_phrases"><?php echo $row[6]; ?></td>
            <td><?php echo $row[7]; ?></td>
            <td class="price<?php if(strpos($row[8], 'hidden') > 0) echo ' red' ?> "><?php echo $row[8]; ?></td>
        </tr>
    <?php } ?>
    </tbody>
</table>
