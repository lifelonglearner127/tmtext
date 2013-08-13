<script>
    $(function() {
        $('head').find('title').text('Brand Index');
    });
</script>
<style type="text/css">
    .outer_block{
        border: 1px solid #333333;
        float: left;
        height: 10px;
        margin-right: 20px;
        margin-top: 3px;
        width: 170px;
        margin-left: 15px;
    }
    .inner_block{
        background: #333333;
        height: 10px;
    }
    .review_distr span{
        float:left;
    }
</style>
<div class="span12">
    <?php echo form_dropdown('brand', $brands_list, array(), 'class="mt_10"'); ?>
</div>
<div class="row-fluid span12">
    <div class="span3">
    </div>
    <div class="span4">
            <select name="brand_customer0" class="mt_10">
                <?php foreach($customer_list as $customer):?>
                    <option value="<?php echo strtolower($customer); ?>"><?php echo $customer; ?></option>
                <?php endforeach;?>
            </select>
    </div>
    <div class="span4">
            <select name="brand_customer1" class="mt_10">
                <?php foreach($customer_list as $customer):?>
                    <option value="<?php echo strtolower($customer); ?>"><?php echo $customer; ?></option>
                <?php endforeach;?>
            </select>
    </div>
</div>
<div class="row-fluid span12 mt_10">
    <div class="span3">Number of Results</div>
    <div class="span4">5,932</div>
    <div class="span4">311</div>
</div>
<div class="row-fluid span12 mt_10">
    <div class="span3">Number of Reviews</div>
    <div class="span4">17</div>
    <div class="span4">4,577</div>
</div>
<div class="row-fluid span12 mt_10">
    <div class="span3">Average Review</div>
    <div class="span4">4.5 Stars</div>
    <div class="span4">4 Stars</div>
</div>
<div class="row-fluid span12 mt_10">
    <div class="span3">Avg Reviews Per Item</div>
    <div class="span4">457</div>
    <div class="span4">218</div>
</div>
<div class="row-fluid span12 mt_10">
    <div class="span3">Review distribution</div>
    <div class="span4 review_distr">
        <div class="mt_10"><span>5 Star</span> <div class="outer_block"><div class="inner_block" style="width:110px;"></div></div> 418</div>
        <div class="mt_10"><span>4 Star</span> <div class="outer_block"><div class="inner_block" style="width:60px;"></div></div> 211</div>
        <div class="mt_10"><span>3 Star</span> <div class="outer_block"><div class="inner_block" style="width:80px;"></div></div> 325</div>
        <div class="mt_10"><span>2 Star</span> <div class="outer_block"><div class="inner_block" style="width:20px;"></div></div> 54</div>
        <div class="mt_10"><span>1 Star</span> <div class="outer_block"><div class="inner_block" style="width:27px;"></div></div> 79</div>
    </div>
    <div class="span4 review_distr">
        <div class="mt_10"><span>5 Star</span> <div class="outer_block"><div class="inner_block" style="width:135px;"></div></div> 511</div>
        <div class="mt_10"><span>4 Star</span> <div class="outer_block"><div class="inner_block" style="width:35px;"></div></div> 109</div>
        <div class="mt_10"><span>3 Star</span> <div class="outer_block"><div class="inner_block" style="width:45px;"></div></div> 163</div>
        <div class="mt_10"><span>2 Star</span> <div class="outer_block"><div class="inner_block" style="width:8px;"></div></div> 15</div>
        <div class="mt_10"><span>1 Star</span> <div class="outer_block"><div class="inner_block" style="width:59px;"></div></div> 208</div>
    </div>
</div>
<div class="row-fluid span12 mt_10">
    <div class="span3">Best Sellers - Avg # of Reviews</div>
    <div class="span4">193</div>
    <div class="span4">467</div>
</div>
<div class="row-fluid span12 mt_10">
    <div class="span3">Best Sellers - Avg Review</div>
    <div class="span4">4.5 Stars</div>
    <div class="span4">3.5 Stars</div>
</div>