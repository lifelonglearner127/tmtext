<script type="text/javascript">
    $(document).ready(function () {
        var ddData_first = [
            {
                text: "",
                value: "Walmart.com",
                description: "",
                imageSrc: "<?php echo base_url(); ?>img/walmart-logo.png"
            },
            {
                text: "",
                value: "Sears.com",
                description: "",
                imageSrc: "<?php echo base_url(); ?>img/sears-logo.png"
            },
            {
                text: "",
                value: "TigerDirect.com",
                description: "",
                imageSrc: "<?php echo base_url(); ?>img/tigerdirect-logo.png"
            },
        ];

        $('#research_dropdown').ddslick({
            data: ddData_first,
            defaultSelectedIndex: 0
        });
        $( "#sortable1, #sortable2" ).sortable({
            connectWith: ".connectedSortable"
        }).disableSelection();
        $( "ul#sortable1 li.boxes, ul#sortable2 li.boxes" ).resizable();
    });
</script>
<div class="main_content_other"></div>
<div class="main_content_editor research">
    <div class="row-fluid">
        <?php echo form_open('', array('id'=>'measureForm')); ?>
        <input type="text" id="research_text" name="research_text" value="UN40E6400" class="span8 " placeholder=""/>
        <div id="research_dropdown"></div>
        <button type="button" class="btn pull-right">Search</button>
        <?php echo form_close();?>
    </div>
    <div class="clear"></div>
    <div class="row-fluid mt_10">
        <div class="span7">
            Show <select name="result_amount" style="width:50px;">
                    <option value="10">10</option>
                    <option value="20">20</option>
                    <option value="50">50</option>
                 </select>
            results in category
                <select name="category">
                    <option value="category1">category1</option>
                    <option value="category2">category2</option>
                    <option value="category3">category3</option>
                </select>
        </div>
        <div class="span4">
            Boxes:
            <select name="text">
                <option value="text1">text1</option>
                <option value="text2">text2</option>
                <option value="text3">text3</option>
            </select>
        </div>
        <button type="button" class="btn pull-right">Export</button>
    </div>
    <div class="row-fluid" id="main">
        <div class="span6" id="research">
            <h3>Research</h3>
            <ul class="research_content connectedSortable" id="sortable1">
                <li class="boxes">
                    <h3>Results</h3>
                    <div class="boxes_content"></div>
                </li>
                <li class="boxes mt_10">
                    <h3>Related keywords</h3>
                    <div class="boxes_content"></div>
                </li>
                <li class="boxes mt_10">
                    <h3>SEO Phrases</h3>
                    <div class="boxes_content"></div>
                </li>
            </ul>
        </div>
        <div class="span6" id="research_edit">
            <h3>Edit</h3>
            <ul class="research_content connectedSortable" id="sortable2">
                <li class="boxes">
                    <h3>Keywords</h3>
                    <div class="boxes_content"></div>
                </li>

                <li class="boxes mt_10 ">
                    <h3>Page elements</h3>
                    <div class="boxes_content">
                        <p><button type="button" class="btn pull-right">Generate</button>
                            <label>Product name:</label><input type="text" name="product_name"/>
                        </p>
                        <p><label>Meta title:</label><input type="text" name="meta_title" /></p>
                        <p><label>Meta description:</label><input type="text" name="meta_description" /></p>
                        <p><label>Meta keywords:</label><input type="text" name="meta_keywords" /></p>
                    </div>
                </li>
                <li class="boxes mt_10">
                    <h3>Descriptions</h3>
                    <div class="boxes_content"></div>
                </li>
            </ul>
        </div>
    </div>
</div>

