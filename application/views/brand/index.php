<script>
    $(function() {
        $('head').find('title').text('Brand Index');
    });
</script>
<div class="row-fluid">
    <select name="brand_customer0" class="mt_10">
        <?php foreach($customer_list as $customer):?>
            <option value="<?php echo strtolower($customer); ?>"><?php echo $customer; ?></option>
        <?php endforeach;?>
    </select>
</div>
<div class="row-fluid">
    <select name="brand_customer1" class="mt_10">
        <?php foreach($customer_list as $customer):?>
            <option value="<?php echo strtolower($customer); ?>"><?php echo $customer; ?></option>
        <?php endforeach;?>
    </select>
</div>
<div class="row-fluid">

</div>
