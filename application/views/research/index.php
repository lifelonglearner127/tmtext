<script type="text/javascript">
    var measureAnalyzerBaseUrl = "<?php echo base_url(); ?>index.php/measure/analyzestring";

    function getSearchResult(){
        $.post(base_url + 'index.php/research/search_results', { 'search_data': $('input[name="research_text"]').val(), 'website': $('input.dd-selected-value').val() }, function(data){
            $('ul#product_descriptions').empty();
            $('ul#research_products li').each(function(){
                if($(this).attr('class') != 'main' || $(this).attr('class') == undefined){
                    $(this).remove();
                }
            });
            if(data.length > 0){
                var str = '';
                var desc = '';
                for(var i=0; i < data.length; i++){
                    str += '<li id="'+data[i].imported_data_id+'"><span>'+data[i].product_name.substr(0, 23)+
                        '...</span><span>'+data[i].url.substr(0, 27)+'...</span></li>';
                    desc +=  '<li id="'+data[i].imported_data_id+'_name">'+data[i].product_name+'</li>';
                    desc +=  '<li id="'+data[i].imported_data_id+'_url">'+data[i].url+'</li>';
                    desc +=  '<li id="'+data[i].imported_data_id+'_desc">'+data[i].description+'</li>';
                    desc +=  '<li id="'+data[i].imported_data_id+'_long_desc">'+data[i].long_description+'</li>';

                }
                $('.main span:first-child').css({'width':'182px'});
                $('ul#research_products').append(str);
                $('ul#product_descriptions').append(desc);
                $('#research_products li:eq(0)').trigger('click');
            }
        }, 'json');
    }

    $(document).ready(function () {

        $('input[name="research_text"]').focus();
        $( "#sortable1, #sortable2" ).sortable({
            connectWith: ".connectedSortable",
            cursor: 'move',
            revert: "invalid",
            handle: ".handle",
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
        }).bind('click', function(){
          $(this).focus();
        });

        $( "ul#sortable1 li.boxes, ul#sortable2 li.boxes" ).resizable();

        $("#related_keywords").resizable({minWidth: 418, maxWidth:418});
        
        $(document).on("keydown change", 'textarea[name="short_description"]', function() {
            var number = 0;
            var matches = $(this).val().match(/\b/g);
            if(matches) {
                number = matches.length/2;
            }
            $('#wc').html(number);
        });
        
        $(document).on("keydown change", '#long_description', function() {
            var number = 0;
            var matches = $(this).text().match(/\b/g);
            if(matches) {
                number = matches.length/2;
            }
            $('#wc1').html(number);
        });

        $(document).on("click", 'a.clear_all', function() {
            $(this).prev().val('');
            return false;
        });
        $(document).on("keypress", 'input[name="research_text"]', function(e){
            if(e.keyCode == 13){
               getSearchResult();
               return false;
            }
        });
        $(document).on("click", 'button#research_search', function(){
            getSearchResult();
        });

        $(document).on("click", '#related_keywords li', function(){
            $('input[name="'+$(this).attr('class')+'"]').val($(this).text());
        });

        $(document).on("click", '#research_products li', function(){
            $('textarea[name="short_description"]').val('');
            $('textarea[name="long_description"]').val('');
            if($(this).attr('id')!='' && $(this).attr('id')!=undefined){
                var id = $(this).attr('id');
                $("#research_products li").each(function(){
                    $(this).css({'background':'none'});
                });
                $(this).css({'background':'#CAEAFF'});
                $('#rel_keywords').css({'display':'block'});
                $.post(base_url + 'index.php/research/get_research_data', { 'batch': $('select[name="batches"] option:selected').text(),
                'product_name': $('ul#product_descriptions li#'+$(this).attr('id')+'_name').text()},
                function(data){
                        var short_status = 'short';
                        var long_status = 'long';
                        var short_desc_an = '';
                        var long_desc_an = '';
                        if(data.length > 0){
                            $('input[name="product_name"]').val(data[0].product_name);
                            $('input[name="meta_title"]').val(data[0].product_name);
                            $('input[name="meta_keywords"]').val(data[0].meta_keywords);
                            $('input[name="primary"]').val(data[0].keyword1);
                            $('input[name="secondary"]').val(data[0].keyword2);
                            $('input[name="tertiary"]').val(data[0].keyword3);
                            $('input[name="url"]').val(data[0].url);
                            $('input[name="revision"]').val(data[0].revision);
                            short_desc_an = data[0].short_description;
                            long_desc_an = data[0].long_description;
                        } else {
                                $('input[name="product_name"]').val($('ul#product_descriptions li#'+id+'_name').text());
                                $('input[name="meta_title"]').val($('ul#product_descriptions li#'+id+'_name').text());
                                $('input[name="url"]').val($('ul#product_descriptions li#'+id+'_url').text());

                                short_desc_an = $('ul#product_descriptions li#'+id+'_desc').text();
                                long_desc_an = $('ul#product_descriptions li#'+id+'_long_desc').text();
                        }
                        // --- SHORT DESC ANALYZER (START)
                        $('textarea[name="meta_description"]').val(short_desc_an);
                        $('textarea[name="short_description"]').val(short_desc_an);
                        $('textarea[name="short_description"]').trigger('change');
                        short_desc_an = short_desc_an.replace(/\s+/g, ' ');
                        short_desc_an = short_desc_an.trim();
                        var analyzer_short = $.post(measureAnalyzerBaseUrl, { clean_t: short_desc_an }, 'json').done(function(a_data) {
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
                        $('#long_description').text(long_desc_an);
                        $('#long_description').trigger('change');
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

                        $("ul[data-status='seo_an']").show();
                }, 'json');


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


        $(document).on("click", "#validate", function(){
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

        });

        $(document).on("click", "button#new_batch", function(){
            $.post(base_url + 'index.php/research/new_batch', { 'batch': $('input[name="new_batch"]').val() }).done(function(data) {
                    if($('input[name="new_batch"]').val() !='' ){
                        var cat_exist = 0;
                        $('select[name="batches"] option').each(function(){
                            if($(this).text() == $('input[name="new_batch"]').val()){
                                cat_exist = 1;
                            }
                        });
                        if(cat_exist == 0){
                            $('select[name="batches"]').append('<option selected="selected">'+
                                $('input[name="new_batch"]').val()+'</option>');
                            return false;
                        }
                    }
                    return false;
            });
        });

        $(document).on("click", "button#save_in_batch", function(){
            $.post(base_url + 'index.php/research/save_in_batch', {
                'batch': $('select[name="batches"] option:selected').text(),
                'url': $('input[name="url"]').val(),
                'product_name': $('input[name="product_name"]').val(),
                'keyword1': $('input[name="primary"]').val(),
                'keyword2': $('input[name="secondary"]').val(),
                'keyword3': $('input[name="tertiary"]').val(),
                'meta_title': $('input[name="meta_title"]').val(),
                'meta_description': $('textarea[name="meta_description"]').val(),
                'meta_keywords': $('input[name="meta_keywords"]').val(),
                'short_description': $('textarea[name="short_description"]').val(),
                'long_description': $('#long_description').text()
            }).done(function(data) {
                console.log(data);
                return false;
            });
        });

        $(document).on("click", "button#save_next", function(){
            $.post(base_url + 'index.php/research/new_batch', { 'batch': $('input[name="new_batch"]').val() }).done(function(data) {
                if($('input[name="new_batch"]').val() !='' ){
                    var cat_exist = 0;
                    $('select[name="batches"] option').each(function(){
                        if($(this).text() == $('input[name="new_batch"]').val()){
                            cat_exist = 1;
                        }
                    });
                    if(cat_exist == 0){
                        $('select[name="batches"]').append('<option selected="selected">'+
                            $('input[name="new_batch"]').val()+'</option>');
                        return false;
                    }
                }
                return false;
            });
        });

    });

    function getMouseEventCaretRange(evt) {
         var range, x = evt.clientX, y = evt.clientY;

         // Try the simple IE way first
         if (document.body.createTextRange) {
             range = document.body.createTextRange();
             range.moveToPoint(x, y);
         }

         else if (typeof document.createRange != "undefined") {
         // Try Mozilla's rangeOffset and rangeParent properties, which are exactly what we want

             if (typeof evt.rangeParent != "undefined") {
                 range = document.createRange();
                 range.setStart(evt.rangeParent, evt.rangeOffset);
                 range.collapse(true);
             }

             // Try the standards-based way next
             else if (document.caretPositionFromPoint) {
                 var pos = document.caretPositionFromPoint(x, y);
                 range = document.createRange();
                 range.setStart(pos.offsetNode, pos.offset);
                 range.collapse(true);
             }

         // Next, the WebKit way
         else if (document.caretRangeFromPoint) {
            range = document.caretRangeFromPoint(x, y);
         }
        }

        return range;
     }

     function selectRange(range) {
         if (range) {
             if (typeof range.select != "undefined") {
                range.select();
             } else if (typeof window.getSelection != "undefined") {
                 var sel = window.getSelection();
                 sel.removeAllRanges();
                 sel.addRange(range);
             }
         }
     }

     document.getElementById("long_description").onclick = function(evt) {
         evt = evt || window.event;
         this.contentEditable = true;
         this.focus();
         var caretRange = getMouseEventCaretRange(evt);

         // Set a timer to allow the selection to happen and the dust settle first
         window.setTimeout(function() {
            selectRange(caretRange);
         }, 5);
         return false;
     };


</script>
<div class="main_content_other"></div>
<div class="main_content_editor research">
    <div class="row-fluid">
        <?php echo form_open('', array('id'=>'measureForm')); ?>
        <input type="text" id="research_text" name="research_text" value="" class="span8 " placeholder=""/>
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
                <option value="100">100</option>
            </select>
            results in category
            <?php echo form_dropdown('category', $category_list, array(), 'class="mt_10"'); ?>
        </div>
        <div class="span6">
            Batch:
            <?php echo form_dropdown('batches', $batches_list, array(), 'class="mt_10" style="width: 100px;"'); ?>
            <button class="btn" type="button" style="margin-left:5px; margin-right: 10px;">Export</button>
            Add new: <input type="text" class="mt_10" style="width:80px" name="new_batch">
            <button id="new_batch" class="btn" type="button" style="margin-left:5px">New</button>
        </div>

    </div>
    <div class="row-fluid" id="main">
        <div class="span6" id="research" class="connectedMoved"> 
            <h3 class="handle">Research</h3>
            <ul class="research_content connectedSortable" id="sortable1">
                <li class="boxes">
                    <h3>Results</h3>
                    <div class="boxes_content"  style="height: 200px;padding:0px;">
                        <ul class="product_title">
                            <li class="main"><span><b>Product Name</b></span><span><b>URL</b></span></li>
                        </ul>
                        <ul id="research_products" style="height: 170px; overflow: auto;">
                            <li><span>&nbsp;</span><span>&nbsp;</span></li>
                            <li><span>&nbsp;</span><span>&nbsp;</span></li>
                            <li><span>&nbsp;</span><span>&nbsp;</span></li>
                            <li><span>&nbsp;</span><span>&nbsp;</span></li>
                        </ul>
                        <ul id="product_descriptions"></ul>
                    </div>
                </li>
                <li class="boxes mt_10" id="related_keywords">
                    <h3>Related Keywords</h3>
                    <div class="boxes_content">
                        <ul id="rel_keywords">
                            <li class="primary"><span>Televisions</span></li>
                            <li class="secondary"><span>TVs</span></li>
                            <li class="tertiary"><span>LCD TV</span></li>
                            <li class="primary"><span>LED TV</span></li>
                            <li class="secondary"><span>Digital TV</span></li>
                            <li class="tertiary"><span>Internet TV</span></li>
                            <li class="primary"><span>HDTV</span></li>
                            <li class="secondary"><span>3D</span></li>
                            <li class="tertiary"><span>HDMI</span></li>
                            <li class="primary"><span>2D</span></li>
                            <li class="secondary"><span>TFT</span></li>
                            <li class="tertiary"><span>USB</span></li>
                        </ul>
                    </div>
                </li>
                <li class="boxes mt_10">
                    <h3>SEO Phrases</h3>
                    <div class="boxes_content">
                        <ul class='less_b_margin ml_0' data-status='seo_an'>
                        </ul>
                        <ul class='less_b_margin ml_0' data-st-id='short_desc_seo' data-status='seo_an'></ul>
                        <ul class='less_b_margin ml_0' data-st-id='long_desc_seo' data-status='seo_an'></ul>
                    </div>
                </li>
            </ul>
        </div>
        <div class="span6" id="research_edit" class="connectedMoved">
            <h3 class="handle">Edit</h3>
            <ul class="research_content connectedSortable" id="sortable2">
                <li class="boxes" id="keywords">
                    <h3>Keywords</h3>
                    <div class="boxes_content">
                        <p><span>Primary:</span><input class="keywords" type="text" name="primary" value="" /><a href="#" class="clear_all">x</a></p>
                        <p><span>Secondary:</span><input class="keywords" type="text" name="secondary" value="" /><a href="#" class="clear_all">x</a></p>
                        <p><span>Tertiary:</span><input class="keywords" type="text" name="tertiary" value="" /><a href="#" class="clear_all">x</a></p>
                    </div>
                </li>

                <li class="boxes mt_10" id="page_elements">
                    <h3>Page Elements</h3>
                    <div class="boxes_content">
                        <p><button id="generate_product" type="button" class="btn pull-right">Generate</button>
                            <label>Product name:</label><input type="text" class="span11 ml_0" name="product_name"/>
                            <input type="hidden" name="url"/>
                            <input type="hidden" name="revision"/>
                        </p>
                        <p><label>Meta title:</label><input type="text"  class="span11 ml_0" name="meta_title" /></p>
                        <p><label>Meta description:</label><textarea name="meta_description" style="height:100px;" ></textarea></p>
                        <p><button id="generate_keywords" type="button" class="btn pull-right">Generate</button>
                            <label>Meta keywords:</label><input type="text" class="span11 ml_0" name="meta_keywords" /></p>
                    </div>
                </li>
                <li class="boxes mt_10">
                    <h3>Descriptions</h3>
                    <div class="boxes_content">
                        <div class="row-fluid"><label>Short description:</label>
                             <label><span id="wc">0</span> words</label>
                             <button type="button" class="btn" style="float:left;">Generate</button>
                             <textarea type="text" name="short_description" class="span10 mt_10" style="height:100px;"></textarea>
                        </div>
                        <div class="row-fluid"><label>Long description:</label>
                            <label><span id="wc1">0</span> words</label>
                            <div class="search_area uneditable-input ml_10"  id="long_description" onClick="this.contentEditable='true';" style="cursor: text; width: 365px;"></div>

                            <!--div class="search_area uneditable-input" id="long_description"
                                 onclick="this.focus(); " style="cursor: text;height:150px; width:380px;"></div-->
                           <!--textarea type="text" name="long_description" class="span10"  style="height:150px;display:none"></textarea-->
                        </div>
                        <div class="row-fluid mb_20">
                            <button id="validate" type="button" class="btn ml_10">Validate</button>
                            <button id="save_in_batch" type="button" class="btn ml_10 btn-success">Save</button>
                            <button id="save_next" type="button" class="btn ml_10 btn-success">Save & Next</button>
                        </div>
                    </div>
                </li>
            </ul>
        </div>
    </div>
</div>

