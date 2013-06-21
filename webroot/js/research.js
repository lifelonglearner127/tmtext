var research_sentence = '';

function getSearchResult(){
    $.post(base_url + 'index.php/research/search_results', { 'search_data': $('input[name="research_text"]').val(),
        'website': $('input.dd-selected-value').val(),
        'category': $('select[name="category"] option:selected').text(),
        'limit': $('select[name="result_amount"] option:selected').val()
    }, function(data){
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
                str += '<li id="'+data[i].imported_data_id+'"><span class="product_name">'+data[i].product_name.substr(0, 23)+
                    '...</span><span class="url">'+data[i].url.substr(0, 27)+'...</span></li>';
                desc +=  '<li id="'+data[i].imported_data_id+'_name">'+data[i].product_name+'</li>';
                desc +=  '<li id="'+data[i].imported_data_id+'_url">'+data[i].url+'</li>';
                desc +=  '<li id="'+data[i].imported_data_id+'_desc">'+data[i].description+'</li>';
                desc +=  '<li id="'+data[i].imported_data_id+'_long_desc">'+data[i].long_description+'</li>';

            }
            $('ul#research_products').append(str);
            $('.main span:first-child').css({'width':$('ul#research_products li:first-child span:first-child').css('width')});
            $('ul#product_descriptions').append(desc);
            $('#research_products li:eq(0)').trigger('click');
        }
    }, 'json');
}

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

function researchKeywordsAnalizer() {
    var research_primary_ph = $.trim($('input[name="primary"]').val());
    var research_secondary_ph = $.trim($('input[name="secondary"]').val());
    var research_tertiary_ph = $.trim($('input[name="tertiary"]').val());
    if(research_primary_ph !== "") research_primary_ph.replace(/<\/?[^>]+(>|$)/g, "");
    if(research_secondary_ph !== "") research_secondary_ph.replace(/<\/?[^>]+(>|$)/g, "");
    if(research_tertiary_ph !== "") research_tertiary_ph.replace(/<\/?[^>]+(>|$)/g, "");

    if(research_primary_ph !== "" || research_secondary_ph !== "" || research_tertiary_ph !== "") {
        var research_long_desc = $.trim($('textarea[name="short_description"]').html() +' '+ $("#long_description").html());
        if(research_long_desc !== "") research_long_desc.replace(/<\/?[^>]+(>|$)/g, "");

        var research_send_object = {
            primary_ph: research_primary_ph,
            secondary_ph: research_secondary_ph,
            tertiary_ph: research_tertiary_ph,
            short_desc: '',
            long_desc: research_long_desc
        };

        $.post(base_url+'index.php/measure/analyzekeywords', research_send_object, 'json').done(function(data) {
            if(data.length > 0){
                var first = (data['primary'][1].toPrecision(3)*100).toFixed(2);
                var second = (data['secondary'][1].toPrecision(3)*100).toFixed(2);
                var third = (data['tertiary'][1].toPrecision(3)*100).toFixed(2);
                $('input[name="research_primary"]').val(first);
                $('input[name="research_secondary"]').val(second);
                $('input[name="research_tertiary"]').val(third);
            }
        });
    }
}

$(document).ready(function () {
    $(document).on("keydown keyup change focusout", 'textarea[name="short_description"]', function() {
        var number = 0;
        var matches = $(this).val().match(/\b/g);
        if(matches) {
            number = matches.length/2;
        }
        $('#research_wc').html(number);
        var num = parseInt($('#research_wc').html())+parseInt($('#research_wc1').html());
        $('#research_total').html(num);
    });

    $(document).on("keydown keyup change focusout", '#long_description', function() {
        var number = 0;
        var matches = $(this).text().match(/\b/g);
        if(matches) {
            number = matches.length/2;
        }
        $('#research_wc1').html(number);
        var num = parseInt($('#research_wc').html())+parseInt($('#research_wc1').html());
        $('#research_total').html(num);
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
        var txt = $(this).text();

        if($('input[name="primary"]').val()==''){
            research_sentence = 'primary';
            $('input[name="primary"]').val(txt)
        } else if($('input[name="primary"]').val()!='' && $('input[name="secondary"]').val()==''){
            research_sentence = 'secondary';
            $('input[name="secondary"]').val(txt);
        } else if($('input[name="primary"]').val()!='' && $('input[name="secondary"]').val()!=''
            && $('input[name="tertiary"]').val()==''){
            research_sentence = 'tertiary';
            $('input[name="tertiary"]').val(txt);
        } else if($('input[name="tertiary"]').val()!='' && $('input[name="primary"]').val()!=''
            && $('input[name="secondary"]').val()!=''){
            if(research_sentence=='tertiary'){
                $('input[name="primary"]').val(txt);
                research_sentence = 'primary';
            } else if(research_sentence == 'primary'){
                $('input[name="secondary"]').val(txt);
                research_sentence = 'secondary';
            } else if(research_sentence == 'secondary'){
                $('input[name="tertiary"]').val(txt);
                research_sentence = 'tertiary';
            }
        }
    });

    $(document).on("click", '#research_products li', function(e){
        $('input[name="product_name"]').val('');
        $('input[name="meta_title"]').val('');
        $('input[name="meta_keywords"]').val('');
        $('input[name="primary"]').val('');
        $('input[name="secondary"]').val('');
        $('input[name="tertiary"]').val('');
        $('input[name="url"]').val('');
        $('textarea[name="short_description"]').val('');
        $('textarea[name="long_description"]').val('');
        $('input[name="revision"]').val('');
        if($(this).attr('id')!='' && $(this).attr('id')!=undefined){
            var id = $(this).attr('id');
            var name_txt = $('ul#product_descriptions li#'+id+'_name').text();
            var url_txt = $('ul#product_descriptions li#'+id+'_url').text();
            var $target = $(e.target);
            if( $target.is("span.url")) {
                if($.trim($target.text()) == $.trim(url_txt)){
                    $target.text(url_txt.substr(0, 27)+'...');
                }else{
                    $target.text(url_txt);
                }
            } else if( $target.is("span.product_name")) {
                if($.trim($target.text()) == $.trim(name_txt)){
                    $target.text(name_txt.substr(0, 23)+'...');
                }else{
                    $target.text(name_txt);
                }
            }
            $("#research_products li").each(function(){
                $(this).css({'background':'none'});
                $(this).removeClass('current_selected');
            });
            $(this).css({'background':'#CAEAFF'});
            $(this).addClass('current_selected');
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
                        $('input[name="product_name"]').val(name_txt);
                        $('input[name="meta_title"]').val(name_txt);
                        $('input[name="url"]').val(url_txt);

                        short_desc_an = $('ul#product_descriptions li#'+id+'_desc').text();
                        long_desc_an = $('ul#product_descriptions li#'+id+'_long_desc').text();
                    }
                    // --- SHORT DESC ANALYZER (START)
                    $('textarea[name="meta_description"]').val(short_desc_an);
                    $('textarea[name="short_description"]').val(short_desc_an);
                    $('textarea[name="short_description"]').trigger('change');
                    short_desc_an = short_desc_an.replace(/\s+/g, ' ');
                    short_desc_an = short_desc_an.trim();
                    var analyzer_short = $.post(base_url + 'index.php/measure/analyzestring', { clean_t: short_desc_an }, 'json').done(function(a_data) {
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
                    var analyzer_long = $.post(base_url + 'index.php/measure/analyzestring', { clean_t: long_desc_an }, 'json').done(function(a_data) {
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
                    var num = parseInt($('#research_wc').html())+parseInt($('#research_wc1').html());
                    $('#research_total').html(num);
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
        $('#long_description').trigger('change');
        $('textarea[name="short_description"]').trigger('change');
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
                return false;
            });
    });

    $(document).on("click", "button#save_next", function(){
        $("button#save_in_batch").trigger("click");
        $('#research_products li.current_selected').next().trigger('click');
    });

    $(document).on("click", "button#research_update_density", function(){
        researchKeywordsAnalizer();
    });

    $(document).on("click", '#long_description', function(evt){
        evt = evt || window.event;
        this.contentEditable = true;
        this.focus();
        var caretRange = getMouseEventCaretRange(evt);

        // Set a timer to allow the selection to happen and the dust settle first
        window.setTimeout(function() {
            selectRange(caretRange);
        }, 10);
        return false;
    });

    $(document).on("change", 'select[name="result_amount"]', function(){
        getSearchResult();
    });

    $(document).on("change", 'select[name="category"]', function(){
        getSearchResult();
    });
    $(document).on("click", "#export_batch", function(){
        window.location.href = base_url + 'index.php/research/export?batch='+$("select[name='batches'] option:selected").text();
    });

    /*----------------------------Research batches--------------------------------------------*/

    $(document).on("change", 'select[name="research_batches"]', function() {
        $('input[name="batche_name"]').val($('select[name="research_batches"] option:selected').text());
    });
    $('select[name="research_batches"]').trigger('change');

    $(document).on("click", '#research_batches_save', function() {
        $.post(base_url + 'index.php/research/change_batch_name', { 'old_batch_name': $('select[name="research_batches"] option:selected').text(),
            'new_batch_name': $('input[name="batche_name"]').val()}, function(data){
            if(data.message == 'success'){
                $('select[name="research_batches"] option:selected').text($('input[name="batche_name"]').val());
            }
        });
    });

    $(document).on("click", '#research_batches_search', function() {

        /*$.post(base_url + 'index.php/research/get_research_info', { 'choosen_batch': $('select[name="research_batches"] option:selected').text(),
                'search_text': $('input[name="research_batches_text"]').val() },
            function(data){
                $('table#research_results tbody').empty();
                if(data.length > 0 ){
                    $( '#readTemplate' ).render( data ).appendTo( "#records" );
                    var str = '';
                    for(var i=0; i < data.length; i++){
                        str += '<tr id="'+data[i].id+'"><td>'+data[i].created+'</td>';
                        str += '<td>'+data[i].user_id+'</td>';
                        str += '<td>'+data[i].product_name+'</td>';
                        str += '<td>'+data[i].url+'</td>';
                        str += '<td>'+data[i].meta_name+'</td>';
                        str += '<td>'+data[i].meta_description+'</td>';
                        str += '<td>'+data[i].short_description+'</td>';
                        str += '<td>'+data[i].long_description+'</td></tr>';
                    }
                    $('table#research_results tbody').append(str);
                } else {
                    $('table#research_results tbody').append('<tr align="center"><td colspan="8">Empty result</td></tr>');
                }
          });*/
        readResearchData();
    });

    /*$(document).on("click", 'table#research_results tr', function() {
        $("table#research_results tr").each(function(){
            $(this).css({'background':'none'});
        });
        $(this).css({'background':'#CAEAFF'});
        $(this).addClass('active');
    });

    $(document).on("click", 'button#research_batches_delete', function() {
        var row_id = '';
        $("table#research_results tr").each(function(){
            if($(this).attr('class') == 'active'){
                row_id = $(this).attr('id');
            }
        });
        $.post(base_url + 'index.php/research/delete_research_data', { 'id': row_id },
            function(data){

        });
    });*/

    $(document).on("click", '.research_arrow', function() {
        if($(this).hasClass('changed') && last_edition != ''){
            $('#main').empty();
            $('#main').html(last_edition);
            $('div#research').css({'width':''});
            $('div#research_edit').css({'width':''});
            $(this).removeClass('changed');
            $('div#long_description').css({'margin-left':'7px'});
            last_edition = '';
            setMovement();
            return false;
        }

        if($(this).parent().parent().parent().attr('id') == 'main'){
            var div = $(this).parent().parent().attr('id');
            if(div == 'research'){
                last_edition = $('#main').html();
                $('div#'+div).css({'width':'99%'});
                $('div#research_edit').css({'width':'99%'});
                $(this).addClass('changed');
                return false;
            }
            if(div == 'research_edit'){
                var research_edit = $('div#'+div);
                var research = $('div#research');
                last_edition = $('#main').html();
                $('div#'+div).css({'width':'99%'});
                $('div#research').css({'width':'99%'});
                $('#main').empty();
                $('#main').append(research_edit).append(research);
                $(this).addClass('changed');
                return false;
            }
        } else {
            var parent_id = $(this).parent().parent().parent().parent().attr('id');
            $('div#long_description').css({'margin-left':'107px'});
            if(parent_id == 'research'){
                last_edition = $('#main').html();
                $(this).parent().parent().parent().prepend($(this).parent().parent());
                $('div#'+parent_id).css({'width':'99%'});
                $('div#research_edit').css({'width':'99%'});
                $(this).addClass('changed');
                return false;
            }
            if(parent_id == 'research_edit'){
                var research_edit = $('div#'+parent_id);
                var research = $('div#research');
                last_edition = $('#main').html();
                $(this).parent().parent().parent().prepend($(this).parent().parent());
                $('div#'+parent_id).css({'width':'99%'});
                $('div#research').css({'width':'99%'});
                $('#main').empty();
                $('#main').append(research_edit).append(research);
                $(this).addClass('changed');
                return false;
            }
        }

    });

});


