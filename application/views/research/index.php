<script type="text/javascript">
    var measureAnalyzerBaseUrl = "<?php echo base_url(); ?>index.php/measure/analyzestring";
    $(document).ready(function () {
        $( "#sortable1, #sortable2" ).sortable({
            connectWith: ".connectedSortable"
        });
        
        $("#research, #research_edit" ).draggable({
            containment: "#main",
            drag: function( event, ui ) {
               if(ui.originalPosition.left > ui.position.left){
                   if($(this).attr('id')=='research_edit'){
                       $(this).addClass('left_pos');
                       $('#research').css({'float':'right'});
                   } else {
                       $(this).addClass('left_pos');
                       $(this).css({'float':'left'});
                       $('#research_edit').addClass('left_pos');
                       $('#research_edit').css({'float':'right'});
                   }
               } else {
                   if($(this).attr('id')=='research_edit'){
                       $(this).addClass('left_pos');
                       $('#research').css({'float':'left'});
                   } else {
                       $(this).addClass('left_pos');
                       $(this).css({'float':'right'});
                       $('#research_edit').addClass('left_pos');
                       $('#research_edit').css({'float':'right'});
                   }
               }
            }
        });

        $( ".ui-draggable" ).disableSelection();

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
            $.post(base_url + 'index.php/research/search_results', { 'search_data': $('input[name="research_text"]').val() }, function(data){
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
                            desc +=  '<li id="'+data[i].imported_data_id+'_name">'+data[i].product_name+'</li>';
                            desc +=  '<li id="'+data[i].imported_data_id+'_desc">'+data[i].description+'</li>';
                            desc +=  '<li id="'+data[i].imported_data_id+'_long_desc">'+data[i].long_description+'</li>';

                        }
                        $('.main span:first-child').css({'width':'172px'});
                        $('ul#products').append(str);
                        $('ul#product_descriptions').append(desc);
                        $('#products li:eq(0)').trigger('click');
                    }
                }, 'json');
        });

        $(document).on("click", '#related_keywords li', function(){
            var txt = $(this).text();
            var count = 0;
            $('input.keywords').each(function(){
                if($.trim(txt)==$.trim($(this).val())){
                    count++;
                }
            });
            if(count>0){ return false; }
            if($('input[name="primary"]').val() == ''){
                $('input[name="primary"]').val(txt);
            } else if($('input[name="primary"]').val() != '' && $('input[name="secondary"]').val() == ''){
                $('input[name="secondary"]').val(txt);
            } else if($('input[name="secondary"]').val() != '' && $('input[name="third"]').val() == ''){
                $('input[name="third"]').val(txt);
            }
        });

        $(document).on("click", '#products li', function(){
            $('textarea[name="short_description"]').val('');
            $('textarea[name="long_description"]').val('');
            if($(this).attr('id')!='' && $(this).attr('id')!=undefined){
                $("#products li").each(function(){
                    $(this).css({'background':'none'});
                });
                $(this).css({'background':'#CAEAFF'});
                $('#rel_keywords').css({'display':'block'});
                $('input[name="product_name"]').val($('ul#product_descriptions li#'+$(this).attr('id')+'_name').text());
                $('input[name="meta_title"]').val($('ul#product_descriptions li#'+$(this).attr('id')+'_name').text());

                // --- SHORT DESC ANALYZER (START)
                var short_status = 'short';
                var short_desc_an = $('ul#product_descriptions li#'+$(this).attr('id')+'_desc').text();
                $('textarea[name="meta_description"]').val(short_desc_an);
                $('textarea[name="short_description"]').val(short_desc_an);
                $('textarea[name="short_description"]').trigger('change');
                short_desc_an = short_desc_an.replace(/\s+/g, ' ');
                short_desc_an = short_desc_an.trim();
                var analyzer_short = $.post(measureAnalyzerBaseUrl, { clean_t: short_desc_an }, 'json').done(function(a_data) {
                    console.log(a_data);
                    var seo_items = "<li class='long_desc_sep'>Short Description:</li>";
                    var top_style = "";
                    var s_counter = 0;
                    for(var i in a_data) {
                        if(typeof(a_data[i]) === 'object') {
                            s_counter++;
                            if(i == 0) {
                                top_style = "style='margin-top: 5px;'";
                            }
                            seo_items += '<li ' + top_style + '>' + '<span data-status="seo_link" class="word_wrap_li_pr hover_en">' + a_data[i]['ph'] + '</span>' + ' <span class="word_wrap_li_sec">(' + a_data[i]['count'] + ')</span></li>';
                        }
                    }
                    if(s_counter > 0) $("ul[data-st-id='short_desc_seo']").html(seo_items);
                });
                // --- SHORT DESC ANALYZER (END)

                // --- LONG DESC ANALYZER (START)
                var long_status = 'long';
                var long_desc_an = $('ul#product_descriptions li#'+$(this).attr('id')+'_long_desc').text();
                $('#long_description').text(long_desc_an);
                //$('textarea[name="long_description"]').val(long_desc_an);
                //$('textarea[name="long_description"]').trigger('change');
                long_desc_an = long_desc_an.replace(/\s+/g, ' ');
                long_desc_an = long_desc_an.trim();
                var analyzer_long = $.post(measureAnalyzerBaseUrl, { clean_t: long_desc_an }, 'json').done(function(a_data) {
                    var seo_items = "<li class='long_desc_sep'>Long Description:</li>";
                    var top_style = "";
                    var l_counter = 0;
                    for(var i in a_data) {
                        if(typeof(a_data[i]) === 'object') {
                            l_counter++;
                            if(i == 0) {
                                top_style = "style='margin-top: 5px;'";
                            }
                            seo_items += '<li ' + top_style + '>' + '<span data-status="seo_link" class="word_wrap_li_pr hover_en">' + a_data[i]['ph'] + '</span>' + ' <span class="word_wrap_li_sec">(' + a_data[i]['count'] + ')</span></li>';
                            // seo_items += '<li ' + top_style + '>' + '<span data-status="seo_link" data-status-sv="long"  class="word_wrap_li_pr hover_en">' + a_data[i]['ph'] + '</span>' + ' <span class="word_wrap_li_sec">(' + a_data[i]['count'] + ')</span></li>';
                        }
                    }
                    if(l_counter > 0) $("ul[data-st-id='long_desc_seo']").html(seo_items);
                });
                // --- LONG DESC ANALYZER (END)

                $("ul[data-status='seo_an']").fadeOut();
                $("ul[data-status='seo_an']").fadeIn();
            }

        });

        $(document).on("click", 'button#generate_keywords', function(){
           var str = '';
           $('input.keywords').each(function(){
               if($(this).val()!=''){
                   str += $(this).val()+', ';
               }
           });
           str = str.substring(0,str.length-2);
           $('input[name="meta_keywords"]').val(str);
        });


        /*$(document).on("click", "#validate", function(){
            var vbutton = $(this);
            var description = $('#long_description').html();

            vbutton.html('<i class="icon-ok-sign"></i>&nbsp;Validating...');

            $.post(base_url + 'index.php/editor/validate', { description: description }, 'json')
                .done(function(data) {
                    var d = [];
                    if (data['spellcheck'] !== undefined) {
                        $.each(data['spellcheck'], function(i, node) {
                            description = replaceAt(i, '<b>'+i+'</b>', description, parseInt(node.offset));
                        });
                    }
                    vbutton.html('<i class="icon-ok-sign"></i>&nbsp;Validate');
                    $('#long_description').html(description);
                });

        });*/
    });






</script>
<div class="main_content_other"></div>
<div class="main_content_editor research">
    <div class="row-fluid">
        <?php echo form_open('', array('id'=>'measureForm')); ?>
        <input type="text" id="research_text" name="research_text" value="UN40E6400" class="span8 " placeholder=""/>
        <div id="res_dropdown" class="ddslick_dropdown"></div>
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
                    <div class="boxes_content"  style="height: 200px;">
                        <ul class="product_title">
                            <li class="main"><span><b>Product Name</b></span><span><b>URL</b></span></li>
                        </ul>
                        <ul id="products" style="height: 170px; overflow: auto;">
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
                        <ul id="rel_keywords">
                            <li><span>Televisions</span></li>
                            <li><span>TVs</span></li>
                            <li><span>LCD TV</span></li>
                        </ul>
                    </div>
                </li>
                <li class="boxes mt_10">
                    <h3>SEO Phrases</h3>
                    <div class="boxes_content">
                        <ul class='less_b_margin' data-status='seo_an'>
                            <li><a href='javascript:void(0)'>SEO Phrases</a></li>
                        </ul>
                        <ul class='less_b_margin' data-st-id='short_desc_seo' data-status='seo_an'></ul>
                        <ul class='less_b_margin' data-st-id='long_desc_seo' data-status='seo_an'></ul>
                    </div>
                </li>
            </ul>
        </div>
        <div class="span6" id="research_edit" class="connectedMoved">
            <h3>Edit</h3>
            <ul class="research_content connectedSortable" id="sortable2">
                <li class="boxes" id="keywords">
                    <h3>Keywords</h3>
                    <div class="boxes_content">
                        <p><span>Primary:</span><input class="keywords" type="text" name="primary" value="" /><a href="#" class="clear_all">x</a></p>
                        <p><span>Secondary:</span><input class="keywords" type="text" name="secondary" value="" /><a href="#" class="clear_all">x</a></p>
                        <p><span>Tertiary:</span><input class="keywords" type="text" name="third" value="" /><a href="#" class="clear_all">x</a></p>
                    </div>
                </li>

                <li class="boxes mt_10 ">
                    <h3>Page elements</h3>
                    <div class="boxes_content">
                        <p><button id="generate_product" type="button" class="btn pull-right">Generate</button>
                            <label>Product name:</label><input type="text" name="product_name"/>
                        </p>
                        <p><label>Meta title:</label><input type="text" name="meta_title" /></p>
                        <p><label>Meta description:</label><textarea name="meta_description" style="height:100px;" ></textarea></p>
                        <p><button id="generate_keywords" type="button" class="btn pull-right">Generate</button>
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
                           <textarea type="text" name="short_description" class="span10 mt_10" style="height:100px;"></textarea>
                        </div>
                        <div class="row-fluid"><label>Long description:</label>
                           <input type="hidden" name="long_description_length" value="100" class="span3"/>
                           <label><span id="wc1">0</span> words</label>
                            <div class="search_area uneditable-input" id="long_description" onClick="this.contentEditable='true';" style="cursor: text;height:150px; width:380px;"></div>
                           <!--textarea type="text" name="long_description" class="span10"  style="height:150px;display:none"></textarea-->
                        </div>
                        <div class="row-fluid mb_20">
                            <button type="button" class="btn ml_10">Validate</button>
                            <button type="button" class="btn ml_10 btn-success">Save</button>
                            <button type="button" class="btn ml_10 btn-success">Save & Next</button>
                        </div>
                    </div>
                </li>
            </ul>
        </div>
    </div>
</div>

