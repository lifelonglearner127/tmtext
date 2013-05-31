<script type="text/javascript">
    $(document).ready(function () {
        var ddData_first = [
            {
                text: "All",
                value: "",
                description: "",
            },
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

        $(document).on("click", 'a.clear_all', function() {
            $(this).prev().val('');
            return false;
        });

        $(document).on("click", 'button#research_search', function(){
            $.post('research/search_results', { 'search_data': $('input[name="research_text"]').val() }, function(data){
                    if(data.length > 0){
                        $('ul#product_descriptions').empty();
                        $('ul#products li').each(function(){
                            if($(this).attr('class') != 'main' || $(this).attr('class') == undefined){
                                $(this).remove();
                            }
                        });
                        var str = '';
                        var desc = '';
                        for(var i=0; i < data.length; i++){
                            str += '<li id="'+data[i].imported_data_id+'"><span>'+data[i].product_name.substr(0, 23)+
                                '...</span><span>'+data[i].url.substr(0, 27)+'...</span></li>';
                            desc +=  '<li id="'+data[i].imported_data_id+'_desc">'+data[i].description+'</li>';

                        }
                        $('ul#products').append(str);
                        $('ul#product_descriptions').append(desc);
                    }
                }, 'json');
        });

        $(document).on("click", '#related_keywords li', function(){
            var txt = $(this).text();
            if($('input[name="primary"]').val() == ''){
                $('input[name="primary"]').val(txt);
            } else if($('input[name="primary"]').val() != '' && $('input[name="secondary"]').val() == ''){
                $('input[name="secondary"]').val(txt);
            } else if($('input[name="secondary"]').val() != '' && $('input[name="third"]').val() == ''){
                $('input[name="third"]').val(txt);
            }
        });

        $(document).on("click", '#products li', function(){
            $('textarea[name="short_description"]').text('');
            $('textarea[name="long_description"]').text('');
            if($(this).attr('id')!='' && $(this).attr('id')!=undefined){
                var txt = $('ul#product_descriptions li#'+$(this).attr('id')+'_desc').text();
                $('textarea[name="short_description"]').text(txt);
                $('textarea[name="long_description"]').text(txt);
            }
        });
    });
</script>
<div class="main_content_other"></div>
<div class="main_content_editor research">
    <div class="row-fluid">
        <?php echo form_open('', array('id'=>'measureForm')); ?>
        <input type="text" id="research_text" name="research_text" value="UN40E6400" class="span8 " placeholder=""/>
        <div id="research_dropdown"></div>
        <button id="research_search" type="button" class="btn pull-right btn-success">Search</button>
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
                <option value="Batch1">Batch1</option>
                <option value="Batch2">Batch2</option>
                <option value="text3">Batch3</option>
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
                    <div class="boxes_content" style="height: 200px; overflow: auto;">
                        <ul id="products">
                            <li class="main"><span><b>Product Name</b></span><span><b>URL</b></span></li>
                            <li><span>&nbsp;</span><span>&nbsp;</span></li>
                            <li><span>&nbsp;</span><span>&nbsp;</span></li>
                            <li><span>&nbsp;</span><span>&nbsp;</span></li>
                            <li><span>&nbsp;</span><span>&nbsp;</span></li>
                        </ul>
                        <ul id="product_descriptions"></ul>
                    </div>
                </li>
                <li class="boxes mt_10" id="related_keywords">
                    <h3>Related keywords</h3>
                    <div class="boxes_content">
                        <ul id="related_keywords">
                            <li><span>Televisions</span></li>
                            <li><span>TVs</span></li>
                            <li><span>LCD TV</span></li>
                            <li><span>LED TV</span></li>
                        </ul>
                    </div>
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
                        <p><span>Primary:</span><input type="text" name="primary" value="" /><a href="#" class="clear_all">x</a></p>
                        <p><span>Secondary:</span><input type="text" name="secondary" value="" /><a href="#" class="clear_all">x</a></p>
                        <p><span>Third:</span><input type="text" name="third" value="" /><a href="#" class="clear_all">x</a></p>
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
                        <div class="row-fluid mb_20">
                            <button type="button" class="btn ml_10">Validate</button>
                            <button type="button" class="btn ml_10">Save</button>
                            <button type="button" class="btn ml_10">Save & Next</button>
                        </div>
                    </div>
                </li>
            </ul>
        </div>
    </div>
</div>

