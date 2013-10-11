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
            <?php $data = json_decode($row[11]); ?>
            <tr>
                <td class="name"><?php echo $row[2]; ?></td>
                <td class="url"><a href="<?php echo $data->url; ?>" target="_blank"><?php echo implode('<br/>', str_split($data->url, 120)); ?></a></td>
                <td class="recommendations">
                    <table border="0" cellspacing="0" cellpadding="0" style="border-collapse: collapse;border-spacing: 0;">
                        <?php foreach ($data->recommendations as $recommendation) { ?>
                            <tr style="border: 0px;">
                                <td style="border: 0px;">
                                    <?php echo $recommendation->img; ?>
                                </td>
                                <td style="border: 0px;">
                                    <?php echo $recommendation->msg; ?>
                                </td>
                            </tr>
                        <?php } ?>
                    </table>
                </td>
            </tr>
        <?php } ?>
    </tbody>
</table>
<?php
