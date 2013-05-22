var current_product = 0;
var products = '';
var attribs = '';
var rev = [];
var search_id = undefined;
var sentence = '';
var desc_input = '';

function replaceAt(search, replace, subject, n) {
    return subject.substring(0, n) +subject.substring(n).replace(search, replace);
}

function saveCurrentProduct(text) {
    products[current_product-1] = text;
}

function getPager() {
    var pager = '';
    if (products.length >1) {
        $.each(products, function(index, node) {
            var i = index+1;
            if (i == current_product) {
                pager += '<li><a href="#" class="current_page">'+i+'</a></li>';
            } else if ((i < current_product && i>current_product) || (i > current_product && i<current_product+5)) {
                pager += '<li><a href="#" data-page="'+i+'">'+i+'</a></li>';
            }
        });


        if (current_product == 1) {
            pager  = '<li><a href="#" class="gray_out">&lt;&lt;</a></li>'
                +'<li><a href="#" class="gray_out">&lt;</a></li>'+pager;
        } else {
            pager  = '<li><a href="#" data-page="1">&lt;&lt;</a></li>'
                +'<li><a href="#" data-page="'+(current_product-1)+'">&lt;</a></li>'+pager;
        }
        if (current_product+3 <= products.length) {
            pager += '<li><a href="#" data-page="'+(current_product+1)+'">&gt;</a></li>'
                +'<li><a href="#" data-page="'+(products.length)+'">&gt;&gt;</a></li>';
        }
    }
    return pager;
}

function clearEditorForm() {
    $('.new_product').find('textarea[name="description"]').val('');
    $( ".auto_title #title" ).val('');
    $('#pagination').html('');
    $( "#items" ).html('Original product descriptions');
    // $( "#attributes" ).html('Product attributes'); // EXP
    $('#wc').html('0');
    $('#tc').html('0');
    search_id = undefined;
    rev = [];
}

function moveSentence() {
    // there's the desc and the trash
    var $desc = $( "#desc" ),
        $trash = $( "#trash" );

    $( "#desc, #trash" ).sortable({
        connectWith: ".desc",
        revert: "invalid",
        cursor: "move",
    });

    // resolve the icons behavior with event delegation
    $( "ul.desc_title > li > a" ).click(function( event ) {
        var $item = $( this ),
            $target = $( event.target );

        if($(this).closest("ul").attr('Id')=='desc'){
            $(this).closest("li").fadeOut(function(){
                $(this).closest("li").appendTo("#trash").fadeIn();
            });
        }else if($(this).closest("ul").attr('Id')=='trash'){
            $(this).closest("li").fadeOut(function(){
                $(this).closest("li").appendTo("#desc").fadeIn();
            });
        }

        setTimeout(function(){
            changeTextareaVal();
        },1200)
    });
}

function changeTextareaVal(){
    var val = '';
    $('.new_product #textarea li').each(function(){
        if($(this).find('span').text()!='' && $(this).find('span').text()!=undefined){
            val += $(this).find('span').text();
        }
        if($(this).find('input').val()!='' && $(this).find('input').val()!=undefined){
            val += $(this).find('input').val();
        }
    });
    if(val==''){
        val = $('.new_product #textarea').text();
    }
    $('textarea[name="description"]').val(val).trigger('change');
}

function wrapper(){
    var editor = $('.main_content').find('.main_content_editor');
    if (editor.length == 0) {
       var cont = $('.main_content').html();
       var contWithWrap = '<div class="main_content_other">'+cont+'</div><div class="main_content_editor"></div>';
       $('.main_content').html(contWithWrap);
    }
}

function collectGallery(postData, v) {
    $('#gallery li').each(function() {
    	if ($(this).find('span').attr('id') !== undefined)
    		postData = postData + '&'+escape(v+'[product_title][]')+'=' + escape($(this).find('span').attr('id'));
    });
    return postData;
}

jQuery(document).ready(function($) {

    wrapper();

    $(document).on("keyup change", '.new_product #textarea', function() {
        changeTextareaVal();
    });

    $(document).on("keydown change", 'textarea[name="description"]', function() {
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
        saveCurrentProduct($('.new_product #textarea span.current_product').text());
    });

    $(document).on("keydown change", ".auto_title #title", function() {
        var _limit = $('input[name="title_length"]').val();
        if($(this).val().length > _limit) {
            var string = $(this).val();
            $(this).val(string.substring(0, _limit));
        }
        $('#tc').html($(this).val().length);
    });

    $(document).on("submit", "#searchForm", function(event) {
        event.preventDefault();

        clearEditorForm();

        var $form = $( this ),
            term = $form.find( 'input[name="s"]' ).val(),
            url = $form.attr( 'action' );

        var posting = $.post( url, { s: term } );

        posting.done(function( data ) {
            $( "#items" ).html( $(data).find('#content') );
            $( "#items #items_list li" ).expander({
                slicePoint: 150,
                expandText: '[&hellip;]',
                expandPrefix: ' ',
                userCollapseText: '[^]',
                expandEffect : 'show',
                collapseEffect : 'hide',
                expandSpeed: 0,
                collapseSpeed: 0,
                afterExpand: function() {
                    $(this).find('.details').css('display', 'inline');
                }
            });

            $("#content #items_list li:first").css({'background':'#CAEAFF'});

            url = $('#attributesForm').attr( 'action' );

            var attributes = $.post( url, { s: term }, 'json' );

            attributes.done(function( data ) {
                var a = "<ul>";
                $.each(data.attributes, function(i,e){
                    a += "<li>"+i+" "+e+"</li>";
                });
                a += "</ul>";
                $( "#attributes" ).html( a );
                attribs = data['attributes'];

                var title = $( ".auto_title #title" );
                title.val( data['product_title'] ).trigger('change');

                products = data['product_descriptions'];

                var description = $('.new_product').find('textarea[name="description"]');
                description.removeAttr('disabled');
                description.val(products[0]);
                description.trigger('change');
                desc_input = products[0];

                var descriptionDiv = $('.new_product #textarea');

                fulltext = '<ul id="desc" class="desc_title desc"><li>' +
                    '<span class="current_product">'+products[0]+'</span><a hef="#" class="ui-icon-trash">x</a></li></ul>';
                descriptionDiv.html(fulltext);
                //descriptionDiv.text(products[0]);
                descriptionDiv.trigger('change');

                moveSentence();

                current_product = 1;

                $('#pagination').html(getPager());
            });
        });
    });

    $(document).on("click", "#pagination a", function(event){
        event.preventDefault();
        current_product = $(this).data('page');

        if ($(this).data('page')!==undefined) {
            var description = $('.new_product').find('textarea[name="description"]');
            var descriptionDiv = $('.new_product #textarea');
            description.val(products[current_product-1]);
            descriptionDiv.html('<ul id="desc" class="desc_title desc">'+sentence+' '+'<li><span class="current_product">'+
                products[current_product-1]+'</span><a hef="#" class="ui-icon-trash">x</a></li>').trigger('change');
            desc_input = products[current_product-1];
            moveSentence();
            //descriptionDiv.html(products[current_product-1]).trigger('change');

            $('#pagination').html(getPager());

        }
    });

    $(document).ajaxStart(function(){
        $('html').addClass('busy');
    }).ajaxStop(function(){
            $('html').removeClass('busy');
        });

    $(document).on("click", "#validate", function(){
        var vbutton = $(this);
        var description = '';
        $('.new_product #textarea li').each(function(){
            if($(this).find('span').text()!='' && $(this).find('span').text()!=undefined){
                description += $(this).find('span').text()+' ';
            }
            if($(this).find('input').val()!='' && $(this).find('input').val()!=undefined){
                description += $(this).find('input').val()+' ';
            }
        });
        if(description==''){
            description = $('.new_product').find('textarea[name="description"]').val();
        }

        var url =  $('#attributesForm').attr( 'action' ).replace('attributes', 'validate');

        vbutton.html('<i class="icon-ok-sign"></i>&nbsp;Validating...');

        $.post(url, { description: description }, 'json')
            .done(function(data) {
                var d = [];
                if (data['spellcheck'] !== undefined) {
                    $.each(data['spellcheck'], function(i, node) {
                        description = replaceAt(i, '<b>'+i+'</b>', description, parseInt(node.offset));
                    });
                }

                if (data['attributes'] !== undefined) {
                    var textAttribs = data['attributes']['description']['attributes']['attribute'];
                    if (textAttribs !== undefined ) {
                        $.each(textAttribs, function(i,e){
                            if (attribs[e['@attributes']['tagName']] !== undefined) {
                                var attrInDescription = '';
                                var _equal = false;

                                $.each(e['@attributes']['value'], function(idx, obj) {
                                    if (description.indexOf(obj) > -1) {
                                        attrInDescription = obj;
                                    }

                                    if (attribs[e['@attributes']['tagName']] == obj) {
                                        _equal = true;
                                    }
                                });

                                if (!_equal) {
                                    description = replaceAt(attrInDescription, '<b>'+attrInDescription+'</b>', description, e['@attributes']['startCharOrig']);
                                }
                            };
                        });
                    }
                }
                vbutton.html('<i class="icon-ok-sign"></i>&nbsp;Validate');
                $('.new_product #textarea').html(description).trigger('change');
                changeTextareaVal();
            });

    });

    $(document).on("click", "#content #items_list li", function(){
        $("#content #items_list li").each(function(){
            $(this).css({'background':'none'})
        });
        $(this).css({'background':'#CAEAFF'});
    });

    $(document).on("click", "#attributes ul li", function(){
        $("#attributes ul li").each(function(){
            $(this).css({'background':'none'})
        });
        $(this).css({'background':'#CAEAFF'});
    });

    $(document).on("click", "#save", function(){
        var url =  $('#attributesForm').attr( 'action' ).replace('attributes', 'save');
        //var d = $('.new_product #textarea span').text();
        var d = '';
        $('.new_product #textarea li').each(function(){
            if($(this).find('span').text()!='' && $(this).find('span').text()!=undefined){
                d += $(this).find('span').text();
            }
            if($(this).find('input').val()!='' && $(this).find('input').val()!=undefined){
                d += $(this).find('input').val();
            }
        });
        if(d==''){
            d = $('.new_product #textarea').text();
        }
        var t = $( ".auto_title #title" ).val();
        var s = $("#searchForm").find( 'input[name="s"]' ).val();
        var revision = 0;
        var post = { attribs: attribs , search: s , current: current_product, title: t, description: d, search_id:search_id };


        if (search_id !== undefined) {
            post.search_id = search_id;
        }

        if (rev[current_product-1] !== undefined ) {
            var obj = rev[current_product-1];
            post.revision = parseInt(obj.revision)+1;
            post.parent_id = obj.parent_id;
        }

        $.post(url, post, 'json')
            .done(function(data) {
                search_id = data.search_id;
                rev[current_product-1] = {
                    parent_id: data.parent_id,
                    revision: data.revision,
                };

                //console.log(rev);
            });
    });    
   
    $(document).on("click", "button#use", function(){
        sentence = $('#textarea ul#desc').html().replace('current_product', '');
        return false;
    });

    $(document).on("click", "button#new_clear", function(){
        sentence = '';
        if (current_product!==undefined && current_product!==0) {
            current_product = 1;
            var description = $('.new_product').find('textarea[name="description"]');
            var descriptionDiv = $('.new_product #textarea');
            description.val(products[current_product-1]);
            descriptionDiv.html('<ul id="desc" class="desc_title desc">'+sentence+' '+'<li><span class="current_product">'+
                products[current_product-1]+'</span><a hef="#" class="ui-icon-trash">x</a></li>').trigger('change');
            moveSentence();
            $('#pagination').html(getPager());
        }
        return false;
    });

    $(document).on("click", ".left_nav_content li a, .right_nav_content li a", function(e){
        e.preventDefault();

        if($(this).hasClass('jq-editor')){
            var editorCont = $('.main_content_editor').html();
            if (editorCont.length == 0) {
                var url = $(this).attr('href');
                var posting = $.post(url+"?ajax=true", function(data) {
                    var response_data = $.parseJSON( data );
                    $('.main_content_editor').html(response_data.ajax_data);
                    $('.main_content > .main_content_editor').html($('.main_content .main_content_editor .main_content_editor').html());
                });
            }
            $('.main_content_other').css('display', 'none');
            $('.main_content_editor').css('display', 'block');
            $(".left_nav_content li, .right_nav_content li").removeClass('active');
            $(this).parent('li').addClass('active');
        }else{
            var url = $(this).attr('href');
            var posting = $.post(url+"?ajax=true", function(data) {
                var response_data = $.parseJSON( data );
                $('.main_content_other').html(response_data.ajax_data);
            });
            $(".left_nav_content li, .right_nav_content li").removeClass('active');
            $(this).parent('li').addClass('active');
            $('.main_content_other').css('display', 'block');
            $('.main_content_editor').css('display', 'none');
        }
    });

    $(document).on("click", "#textarea #desc li span", function(){
        var sentence_class = '';
        if($(this).attr('class')=='current_product') {
            sentence_class += 'current_product';
        }
        $("#textarea #desc li input").each(function(){
            var sentence_class = '';
            if($(this).attr('class')=='current_product') {
                sentence_class += 'current_product';
            }
            $(this).parent().html('<span class="'+sentence_class+'">'+$(this).val()+'</span><a hef="#" class="ui-icon-trash">x</a>');
        });
        var txt = $(this).text();
        $(this).parent().html('<input type="text" class="'+sentence_class+'" name="sentences[]" value="'+txt+'" />' +
            '<a hef="#" class="ui-icon-trash">x</a>');

        var value = $("#textarea #desc li input").val();
        var size  = value.length;
        // playing css width
        size = size*2.3;
        $("#textarea #desc li input").css('width',size*3);
        $("#textarea #desc li:has(input)").css('width',size*3);

        var el = $("#textarea #desc li input:text").get(0);
        var elemLen = el.value.length;
        el.selectionStart = elemLen;
        el.selectionEnd = elemLen;
        el.focus();

        moveSentence();
        return false;
    });

    $(document).on("change", "#textarea ul#desc li input", function() {
        changeTextareaVal();
        return false;
    });
    $(document).on("blur", "#textarea ul#desc li input", function() {
        var str_input= desc_input;
        var str_output= $(this).val();
        var splitinput = str_input.split("\n");
        var splitoutput = str_output.split("\n");
        var inlines=splitinput.length;
        var outlines=splitoutput.length;
        var lines;
        if (outlines>inlines) {
            lines=outlines;
        } else {
            lines=inlines;
        }
        var buildoutput="";

        for (i=0; i<lines; i++) {
            var testundefined = false;
            if (splitinput[i] == undefined) {
                buildoutput = buildoutput+diffString("",splitoutput[i]);
                testundefined = true;
            }

            if (splitoutput[i] == undefined) {
                buildoutput = buildoutput+diffString(splitinput[i],"");
                testundefined = true;
            }

            if (testundefined==false) {
                buildoutput = buildoutput+diffString(splitinput[i],splitoutput[i]);
            }
        }

        var sentence_class = '';
        if($(this).attr('class')=='current_product') {
            sentence_class += 'current_product';
        }
        $("#textarea #desc li input").each(function(){
            var sentence_class = '';
            if($(this).attr('class')=='current_product') {
                sentence_class += 'current_product';
            }
            $(this).parent().html('<span class="'+sentence_class+'">'+buildoutput+'</span><a hef="#" class="ui-icon-trash">x</a>');
        });
        $("#textarea #desc li").css('width','auto');
        moveSentence();
        changeTextareaVal();
        return false;
    });

    
    $(document).on("click", "button#csv_import", function(event){
    	event.preventDefault();

    	var url = $(this).parents().find('form').attr( 'action' ).replace('save', 'csv_import');

    	$.get(url, function(data) {
    		$('#info').html(data.message);
		}, 'json');

        return false;
    });

    $(document).on("submit", "#system_save", function(e){
        e.preventDefault();
        var postData = collectGallery( $(this).serialize() , 'settings' );

        var url = $( this ).attr( 'action' );
        var posting = $.post(url+"?ajax=true", postData, function(data) {
                var response_data = $.parseJSON( data );
                $('.main_content_other').html(response_data.ajax_data);
            });
    });

    $(document).on("submit", "#customer_settings_save", function(e){
        e.preventDefault();
        var postData = collectGallery( $(this).serialize() , 'user_settings' );

        var url = $( this ).attr( 'action' );
        var posting = $.post(url+"?ajax=true", postData, function(data) {
                var response_data = $.parseJSON( data );
                $('.main_content_other').html(response_data.ajax_data);
            });
    });

    $(document).on("click", ".jq-system-tabs li a", function(e){
        e.preventDefault();
        var url = $(this).attr('href');
        var posting = $.post(url+"?ajax=true", function(data) {
            var response_data = $.parseJSON( data );
            $('.main_content_other').html(response_data.ajax_data);
        });
    });

});
//var start = new Date().getMilliseconds();
//console.log("Executed in " + (new Date().getMilliseconds() - start) + " milliseconds");