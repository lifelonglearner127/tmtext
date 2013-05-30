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
        });
        
        $( "#research, #research_edit" ).draggable({containment: "#main"});

        $( "ul#sortable1 li.boxes, ul#sortable2 li.boxes" ).resizable();

        $("#related_keywords").resizable({minWidth: 418, maxWidth:418});
        
        $(document).on("keydown change", 'textarea[name="short_description"]', function() {
            var number = 0;
            var matches = $(this).val().match(/\b/g);
            if(matches) {
                number = matches.length/2;
            }

            var _limit = $('input[name="description_length"]').val();

            if (number>_limit) {
                var limited = $.trim($(this).val()).split(" ", _limit);
                limited = limited.join(" ");
                $(this).val(limited);
            }
            $('#wc').html(number);
        });
        
        $(document).on("keydown change", 'textarea[name="long_description"]', function() {
            var number = 0;
            var matches = $(this).val().match(/\b/g);
            if(matches) {
                number = matches.length/2;
            }

            var _limit = $('input[name="long_description_length"]').val();

            if (number>_limit) {
                var limited = $.trim($(this).val()).split(" ", _limit);
                limited = limited.join(" ");
                $(this).val(limited);
            }
            $('#wc1').html(number);
        });
    });
</script>
<div class="main_content_other"></div>
<div class="main_content_editor research">
    <div class="row-fluid">
        <?php echo form_open('', array('id'=>'measureForm')); ?>
        <input type="text" id="research_text" name="research_text" value="UN40E6400" class="span8 " placeholder=""/>
        <div id="research_dropdown"></div>
        <button type="button" class="btn pull-right btn-success">Search</button>
        <?php echo form_close();?>
    </div>
    <div class="clear"></div>
    <div class="row-fluid">
        <div class="span6">
            Show <select class="mt_10" style="width:50px;" name="result_amount">
                <option value="10">10</option>
                <option value="20">20</option>
                <option value="50">50</option>
            </select>
            results in category
            <?php echo form_dropdown('category', $category_list, array(), 'class="mt_10"'); ?>
        </div>
        <div class="span6">
            Batch:
            <select class="mt_10" style="width: 100px;" name="text">
                <option value="text1">text1</option>
                <option value="text2">text2</option>
                <option value="text3">text3</option>
            </select>
            <button class="btn" type="button" style="margin-left:5px; margin-right: 10px;">Export</button>
            Add new: <input type="text" class="mt_10" style="width:80px" name="new_batch">
            <button class="btn" type="button" style="margin-left:5px">New</button>
        </div>

    </div>
    <div class="row-fluid" id="main">
        <div class="span6" id="research" class="connectedMoved"> 
            <h3>Research</h3>
            <ul class="research_content connectedSortable" id="sortable1">
                <li class="boxes">
                    <h3>Results</h3>
                    <div class="boxes_content"></div>
                </li>
                <li class="boxes mt_10" id="related_keywords">
                    <h3>Related keywords</h3>
                    <div class="boxes_content"></div>
                </li>
                <li class="boxes mt_10">
                    <h3>SEO Phrases</h3>
                    <div class="boxes_content"></div>
                </li>
            </ul>
        </div>
        <div class="span6" id="research_edit" class="connectedMoved">
            <h3>Edit</h3>
            <ul class="research_content connectedSortable" id="sortable2">
                <li class="boxes" id="keywords">
                    <h3>Keywords</h3>
                    <div class="boxes_content">
                        <p><span>Primary:</span><input type="text" name="primary"/></p>
                        <p><span>Secondary:</span><input type="text" name="secondary"/></p>
                        <p><span>Text:</span><input type="text" name="txt"/></p>                       
                    </div>
                </li>

                <li class="boxes mt_10 ">
                    <h3>Page elements</h3>
                    <div class="boxes_content">
                        <p><button type="button" class="btn pull-right">Generate</button>
                            <label>Product name:</label><input type="text" name="product_name"/>
                        </p>
                        <p><label>Meta title:</label><input type="text" name="meta_title" /></p>
                        <p><label>Meta description:</label><input type="text" name="meta_description" /></p>
                        <p><button type="button" class="btn pull-right">Generate</button>
                            <label>Meta keywords:</label><input type="text" name="meta_keywords" /></p>
                    </div>
                </li>
                <li class="boxes mt_10">
                    <h3>Descriptions</h3>
                    <div class="boxes_content">
                        <div class="row-fluid"><label>Short description:</label>
                             <button type="button" class="btn" style="float:left;">Generate</button>
                             <label><span id="wc">0</span> words</label>
                             <input type="hidden" name="description_length" value="50" class="span3"/>
                           <textarea type="text" name="short_description" class="span10 mt_10"></textarea>
                        </div>
                        <div class="row-fluid"><label>Long description:</label>
                           <input type="hidden" name="long_description_length" value="100" class="span3"/>
                           <label><span id="wc1">0</span> words</label>
                           <textarea type="text" name="long_description" class="span10"></textarea>
                        </div>
                    </div>
                </li>
            </ul>
        </div>
    </div>
</div>

