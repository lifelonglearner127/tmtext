<span class="pdf_header">Product Detail View</span><br /><br />
<table class="assess_comparisons" border="0" cellspacing="0" cellpadding="0">
    <tr>
        <td class="row_first"></td>
        <td class="group row_second"><img class="img" src="<?php echo base_url()."img/".$comparison_data->left_product['logo']; ?>" /></td>
        <td class="group row_second"><img class="img" src="<?php echo base_url()."img/".$comparison_data->right_product['logo']; ?>" /></td>
    </tr>
    <tr>
        <td style="font-size: 25px;" class="key_row_name row_name">URL</td>
        <td><a class="url" href="<?php echo $comparison_data->left_product['url']; ?>" target="_blank"><?php echo $comparison_data->left_product['url']; ?></a></td>
        <td><a class="url" href="<?php echo $comparison_data->right_product['url']; ?>" target="_blank"><?php echo $comparison_data->right_product['url']; ?></a></td>
    </tr>
    <tr>
        <td class="key_row_name row_name">Product</td>
        <td><?php echo $comparison_data->left_product['product']; ?></td>
        <td><?php echo $comparison_data->right_product['product']; ?></td>
    </tr>
    <tr>
        <td class="key_row_name row_name">Price</td>
        <td class="<?php if (in_array('price', $comparison_data->red)) echo 'red'; ?>">$<?php echo $comparison_data->left_product['price']; ?></td>
        <td>$<?php echo $comparison_data->right_product['price']; ?></td>
    </tr>
    <tr class="group">
        <td class="key_row_name row_name">Short Description</td>
        <td class="<?php if (in_array('short_description', $comparison_data->red)) echo 'red'; ?>"><?php echo $comparison_data->left_product['short_description']; ?></td>
        <td><?php echo $comparison_data->right_product['short_description']; ?></td>
    </tr>
    <tr>
        <td class="row_name">SEO Keywords</td>
        <td><?php echo $comparison_data->left_product['short_seo_keyword']; ?></td>
        <td><?php echo $comparison_data->right_product['short_seo_keyword']; ?></td>
    </tr>
    <tr>
        <td class="row_name">Duplicate Content</td>
        <td></td>
        <td></td>
    </tr>
    <tr class="group">
        <td class="key_row_name row_name">Long Description</td>
        <td class="<?php if (in_array('long_description', $comparison_data->red)) echo 'red'; ?>"><?php echo $comparison_data->left_product['long_description']; ?></td>
        <td><?php echo $comparison_data->right_product['long_description']; ?></td>
    </tr>
    <tr>
        <td class="row_name">SEO Keywords</td>
        <td><?php echo $comparison_data->left_product['long_seo_keyword']; ?></td>
        <td><?php echo $comparison_data->right_product['long_seo_keyword']; ?></td>
    </tr>
    <tr>
        <td class="row_name">Duplicate Content</td>
        <td></td>
        <td></td>
    </tr>
</table>