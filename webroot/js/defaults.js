var current_product = 0;
var products = '';
var attribs = '';
var rev = [];
var search_id = undefined;
var sentence = new Array();
var desc_input = '';
var action = '';

function getCustomerDropdown(){
    var customers_list_ci = $.post(base_url + 'index.php/measure/getcustomerslist_new', {}, function(c_data) {
        var jsn = $('.customer_dropdown').msDropDown({byJson:{data:c_data, name:'customers_list'}}).data("dd");
    }, 'json');
}
function getWebsiteDropdown(){
    var websites_list_ci = $.post(base_url + 'index.php/measure/getsiteslist_new', {}, function(c_data) {
        var jsn = $('.website_dropdown').msDropDown({byJson:{data:c_data, name:'websites_list'}}).data("dd");
    }, 'json');
}

function refreshHeaderTitle(t) {
    $.post("/editor/refreshheader", { t: t}, 'html').done(function(f) {
        $("head").find("title").replaceWith(f);
    });
}

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
    $( "#attributes" ).html('Product attributes');
    $('#wc').html('0');
    $('#tc').html('0');
    search_id = undefined;
    rev = [];
}

//This prototype function allows you to remove even array from array
Array.prototype.remove = function(x) {
    for(i in this){
        if(this[i].toString() == x.toString()){
            this.splice(i,1)
        }
    }
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

        var txt = $(this).parent().find('span').html();
        if(sentence.length > 0){
            for(var i=0; i<sentence.length; i++){
                if($.trim(sentence[i]) == $.trim(txt)){
                    sentence.remove(sentence[i]);
                }
            }
        }

        if($.trim(desc_input) == $.trim(txt)){
            desc_input = '';
        }

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

function htmlspecialchars(str) {
    if (typeof(str) == "string") {
        str = str.replace(/&/g, "&amp;"); /* must do &amp; first */
        str = str.replace(/"/g, "&quot;");
        str = str.replace(/'/g, "&#039;");
        str = str.replace(/</g, "&lt;");
        str = str.replace(/>/g, "&gt;");
    }
    return str;
}

function cleanNewUserForm(){
    $( "#user_name" ).val('');
    $( "#user_mail" ).val('');
    $( "#user_password" ).val('');
    $( "#user_customers" ).val('').trigger("liszt:updated");
    $( "#user_role" ).val('').trigger("liszt:updated");
    $( ".user_id" ).html('');
    $( ".user_active" ).prop('checked', true);
    $( '#btn_system_update_user' ).attr('disabled', 'disabled');
}

function afterAutocomplete(loadData){

    var postData = {id: loadData.item.id};
    var getuserURL = $('#auth_getuser').attr('action');
    var posting = $.post(getuserURL, postData, function(data) {
        cleanNewUserForm();
        $("#user_name").val(data.username);
        $("#user_mail").val(data.email);
        $("#user_customers").val(data.customers).trigger("liszt:updated");
        $("#user_role").val(data.role.group_id).trigger("liszt:updated");
        if(data.active == 1){
            $(".user_active").prop('checked', true);
        }else{
            $(".user_active").prop('checked', false);
        };
        $('<input type="hidden" name="user_id" id="user_id" value="'+data.id+'" />').appendTo('.user_id');
        $( '#btn_system_update_user' ).removeAttr('disabled');
    });
}

jQuery(document).ready(function($) {
    
    function getCustomerDropdown(){
        setTimeout(function() {
            var customers_list_ci = $.post(base_url + 'index.php/measure/getcustomerslist_new', { }, function(c_data) {
                var jsn = $('.customer_dropdown').msDropDown({byJson:{data:c_data, name:'customers_list'}}).data("dd");
                if(jsn != undefined){
                    jsn.on("change", function(res) {
                        if($('.customer_dropdown').attr('id') == 'research_customers'){
                            $.post(base_url + 'index.php/research/filterBatchByCustomer', { 'customer_name': res.target.value}, function(data){
                                if(data.length>0){
                                    $("select[name='research_batches']").empty();
                                    for(var i=0; i<data.length; i++){
                                        $("select[name='research_batches']").append('<option>'+data[i]+'</option>');
                                    }
                                } else if(data.length==0 && res.target.value !="All customers"){
                                    $("select[name='research_batches']").empty();
                                }
                            });
                            readResearchData();
                            dataTable.fnFilter( $('select[name="research_batches"]').find('option:selected').text(), 7);
                        } else if ($('.customer_dropdown').attr('id') == 'product_customers') {
                            $.post(base_url + 'index.php/research/filterBatchByCustomer', { 'customer_name': res.target.value}, function(data){
                                if(data.length>0){
                                    //Max
                                    $("select[name='product_batches']").empty();
                                    $("select[name='product_batches']").append('<option value="0">Choose Batch</option>');
                                    for(var i=0; i<data.length; i++){
                                       $("select[name='product_batches']").append('<option value="'+data[i]+'">'+data[i]+'</option>');
                                    }
                                } else if(data.length==0 && res.target.value !="All customers"){
                                    $("select[name='product_batches']").empty();
                                    $("select[name='product_batches']").append('<option value="0">Choose Batch</option>');
                                }
                                //Max
                            });
                        } else if ($('.customer_dropdown').attr('id') == 'customers' || $('.customer_dropdown').attr('id') == 'customer_dr') {
                            // get customer name here
                            var oDropdown = $("#customers").msDropdown().data("dd");
                            if(oDropdown==undefined){
                                oDropdown = $("#customer_dr").msDropdown().data("dd");
                            }
                            var customer_name = oDropdown.getData().data.value;
                            // post data to server and fetch styel guide
                            $.post(base_url + 'index.php/research/filterStyleByCustomer',
                                { 'customer_name': customer_name },
                                function(data){
                                    $('li#styleguide').find('.boxes_content').empty();
                                    $('li#styleguide').find('.boxes_content').text(data);
                                }
                            );
                            // populate batches dropdown
                            $.post(
                                base_url + 'index.php/research/filterBatchByCustomer',
                                { 'customer_name': customer_name},
                                function(data){
                                   if(data.length>0){
                                        $("select[name='batches']").empty();
                                        for(var i=0; i<data.length; i++){
                                            $("select[name='batches']").append('<option>'+data[i]+'</option>');
                                        }
                                   } else if(data.length==0 && $("select[name='customers']").find("option:selected").text()!="All customers"){
                                       $("select[name='batches']").empty();
                                   }
                                }
                        );
                        }
                    });
                }
            }, 'json');
        }, 100);
    }

    function getWebsiteDropdown(){
        setTimeout(function() {
            var websites_list_ci = $.post(base_url + 'index.php/measure/getsiteslist_new', { }, function(c_data) {
                var jsn = $('.website_dropdown').msDropDown({byJson:{data:c_data, name:'websites_list'}}).data("dd");
            }, 'json');
        }, 100);
    }

    wrapper();

    // --- destroy search strings from cookie ('Competitive Intelligence' and 'Validate' tabs) (start)
    $(window).unload(function() {
        var com_intel_search_str = $.cookie('com_intel_search_str');
        if(typeof(com_intel_search_str) !== 'undefined' && com_intel_search_str !== null && com_intel_search_str !== "") {
            $.removeCookie('com_intel_search_str', { path: '/' });
        }

        var validate_search_str = $.cookie('validate_search_str');
        if(typeof(validate_search_str) !== 'undefined' && validate_search_str !== null && validate_search_str !== "") {
            $.removeCookie('validate_search_str', { path: '/' });
        }
    });
    // --- destroy search strings from cookie ('Competitive Intelligence' and 'Validate' tabs) (end)

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
        if($('.new_product #textarea ul').html() != undefined){
            saveCurrentProduct($('.new_product #textarea span.current_product').text());
        }
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
            form_id = $form.find("input[type='hidden'][id='form_id']").val('validate_form'),
            url = $form.attr( 'action' );

        // --- record search term to cookie storage (start)
        if(typeof(form_id) !== 'undefined' && form_id !== null && form_id !== "") {
            if(term !== "") {
                var cookie_search_str = $.cookie('validate_search_str');
                if(typeof(cookie_search_str) !== 'undefined') {
                    $.removeCookie('validate_search_str', { path: '/' }); // destroy
                    $.cookie('validate_search_str', term, { expires: 7, path: '/' }); // re-create
                } else {
                    $.cookie('validate_search_str', term, { expires: 7, path: '/' }); // create
                }
            }
        }
        // --- record search term to cookie storage (end)

        var posting = $.post( url, { s: term } );

        posting.done(function( data ) {
            action = 'search';
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
                descriptionDiv.text(products[0]);
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
            desc_input = products[current_product-1];

            if($('#textarea ul').html()!=undefined){
                var str = '';
                for(var i=0; i< sentence.length; i++){
                    str += '<li><span>'+sentence[i]+'</span><a hef="#" class="ui-icon-trash">x</a></li>';
                }
                descriptionDiv.html('<ul id="desc" class="desc_title desc">'+str+'<li><span class="current_product">'+
                    products[current_product-1]+'</span><a hef="#" class="ui-icon-trash">x</a></li></ul>').trigger('change');
            } else {
                var str = '';
                for(var i=0; i< sentence.length; i++){
                    str += sentence[i]+' ';
                }
                descriptionDiv.html(str+' '+products[current_product-1]).trigger('change');
            }

            moveSentence();
            $('#pagination').html(getPager());

        }
    });

    $(document).ajaxStart(function(){
        $('html').addClass('busy');
    }).ajaxStop(function(){
            $('html').removeClass('busy');
        });

    $(document).on("click", "#validate", function(){
        if($('input[type=checkbox]').is(':checked')){
            $('input[type=checkbox]').attr('checked',false);
        }
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
            //description = $('.new_product').find('textarea[name="description"]').val();
            description = $('.new_product #textarea').text();
        } else {
            var str = '';
            for(var i=0; i<sentence.length; i++){
                str += sentence[i];
            }
            description = str + ' ' +description;
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
        if($('#textarea ul').html() != undefined) {
            $('.new_product #textarea li').each(function(){
                if($(this).find('span').text()!='' && $(this).find('span').text()!=undefined){
                    el = $(this).find('span').text().replace('current_product', '')+' ';
                }
            });
        } else {
            if(sentence.length > 0) {
                var el = $('.new_product #textarea').text();
                for(var i=0; i< sentence.length; i++){
                    el = htmlspecialchars(el).replace(htmlspecialchars(sentence[i]), '');
                }
            } else {
                el = $('.new_product #textarea').text();
            }
        }
        sentence.push(el);
        return false;
    });

    $(document).on("click", "button#new_clear", function(){
        sentence = new Array();
        if (current_product!==undefined && current_product!==0) {
            current_product = 1;
            var description = $('.new_product').find('textarea[name="description"]');
            var descriptionDiv = $('.new_product #textarea');
            description.val(products[current_product-1]);
            if($('input[type=checkbox]').is(':checked')) {
                descriptionDiv.html('<ul id="desc" class="desc_title desc"><li><span class="current_product">'+
                    products[current_product-1]+'</span><a hef="#" class="ui-icon-trash">x</a></li>').trigger('change');
            } else {
                descriptionDiv.html(products[current_product-1]);
            }
            moveSentence();
            $('#pagination').html(getPager());
        }
        return false;
    });

    $(document).on("click", ".left_nav_content li a, .right_nav_content li a", function(e){
        e.preventDefault();
        if($(this).parent().hasClass('active')){
//            if($(this).hasClass('jq-measure')){
//                $('title').text("Competitive Intelligence");
//            }
//            var editorCont = $('.main_content_editor').html();
//            if (editorCont.length == 0) {
//                var url = $(this).attr('href');
//                var posting = $.post(url+"?ajax=true", function(data) {
//                    var response_data = $.parseJSON( data );
//                    $('.main_content_editor').html(response_data.ajax_data);
//                    $('.main_content > .main_content_editor').html($('.main_content .main_content_editor .main_content_editor').html());
//                });
//            }
//            $('.main_content_other').css('display', 'none');
//            $('.main_content_editor').css('display', 'block');
//
//            $(".left_nav_content li, .right_nav_content li").removeClass('active');
//            $(this).parent('li').addClass('active');
        }else{
            if($(this).hasClass('jq-validate')){
                $('title').text("Validate");
            }else if($(this).hasClass('jq-research')){
                $('title').text('Research & Edit');
            }
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
        getCustomerDropdown();
        getWebsiteDropdown();

        if($("#an_search").length > 0) $("#an_search").removeAttr('disabled');
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
                if(data.success == 1){
                    $( '.info-message' ).html('<p class="text-success">'+data.message+'</p>');
                }else{
                    $( '.info-message' ).html('<p class="text-error">'+data.message+'</p>');
                }
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

    $(document).on("click", ".jq-customer-tabs li a", function(e){
        e.preventDefault();
        var url = $(this).attr('href');
        var posting = $.post(url+"?ajax=true", function(data) {
            var response_data = $.parseJSON( data );
            $('.main_content_other').html(response_data.ajax_data);
        });
    });

    $(document).on("click", ".jq-research-tabs li a", function(e){
        if( typeof dataTable == 'object' ){
            dataTable = undefined;
        }
        e.preventDefault();
        var url = $(this).attr('href');
        var li_id = $(this).parent().attr('id');
        var posting = $.post(url+"?ajax=true", function(data) {
            var response_data = $.parseJSON( data );
            $('.main_content_other').html(response_data.ajax_data);
            if($('.customer_dropdown').length > 0){
                getCustomerDropdown();
            }
            if($('.website_dropdown').length > 0){
                getWebsiteDropdown();
            }
        });

    });

    $(document).on("click", ".jq-job-board-tabs li a", function(e){
        e.preventDefault();
        var url = $(this).attr('href');
        var posting = $.post(url+"?ajax=true", function(data) {
            var response_data = $.parseJSON( data );
            $('.main_content_other').html(response_data.ajax_data);
        });
    });

    $(document).on("click", ".jq-measure-tabs li a", function(e){
        e.preventDefault();
        var url = $(this).attr('href');
        var posting = $.post(url+"?ajax=true", function(data) {
            var response_data = $.parseJSON( data );
            $('.main_content_other').html(response_data.ajax_data);
            if($('.customer_dropdown').length > 0){
                getCustomerDropdown();
            }
            if($('.website_dropdown').length > 0){
                getWebsiteDropdown();
            }
        });
    });


    $(document).on("click", "#btn_system_new_user", function(e){
        e.preventDefault();
        if($("#user_id").length>0){
            cleanNewUserForm();
        }
        else
        {
            var postData = $( "#system_save_new_user" ).serialize();
            var url = $( "#system_save_new_user" ).attr( 'action' );
            var posting = $.post(url, postData, function(data) {
                if(data.success == 1){
                    cleanNewUserForm();
                    $( '.info-message' ).html('<p class="text-success">'+data.message+'</p>');
                }else{
                    $( '.info-message' ).html(data.message);
                    $( '.info-message p' ).addClass('text-error');
                }
            });
        }
    });

    $(document).on("click", "#btn_system_update_user", function(e){
        e.preventDefault();
        var postData = $( "#system_save_new_user" ).serialize();
        var url = base_url + 'index.php/system/update_user';
        var posting = $.post(url, postData, function(data) {
            if(data.success == 1){
                cleanNewUserForm();
                $( '.info-message' ).html('<p class="text-success">'+data.message+'</p>');
            }else{
                $( '.info-message' ).html(data.message);
                $( '.info-message p' ).addClass('text-error');
            }
        });
    });


    $(document).on("click", "input:checkbox", function(){
        if(action == 'search'){
            var $this = $(this);
            if ($this.is(':checked')) {
                // the checkbox was checked
                var descriptionDiv = $('.new_product #textarea');
                var str = '';
                if(sentence.length>0){
                    for(var i=0; i<sentence.length; i++){
                        if($.trim(sentence[i])==$.trim(desc_input)){
                            desc_input = '';
                        }
                        str += "<li><span>"+sentence[i]+"</span><a hef='#' class='ui-icon-trash'>x</a></li>";
                    }
                }
                fulltext = '<ul id="desc" class="desc_title desc">'+str;
                if(desc_input!=''){
                    fulltext += '<li><span class="current_product">'+desc_input+'</span><a hef="#" class="ui-icon-trash">x</a></li>';
                }
                fulltext += '</ul>';
                descriptionDiv.html(fulltext);
                moveSentence();
            } else {
                // the checkbox was unchecked

                var description = '';
                if(sentence.length>0){
                    for(var i=0; i<sentence.length; i++){
                        if($.trim(sentence[i])==$.trim(desc_input)){
                            desc_input = '';
                        }
                        description += sentence[i]+" ";
                    }
                }
                if(desc_input!=''){
                    description += desc_input+" ";
                }
                $('.new_product #textarea').html(description).trigger('change');
            }
        }
    });

    $(document).on("submit", "#system_save_roles", function(e){
        e.preventDefault();
        var postData = $(this).serialize();
        var url = $( this ).attr( 'action' );
        var posting = $.post(url, postData, function(data) {
            if(data.success == 1){
                $( '.info-message' ).html('<p class="text-success">'+data.message+'</p>');
            }else{
                $( '.info-message' ).html('<p class="text-error">'+data.message+'</p>');
            }
        });
    });

    $(document).on("submit", "#system_save_account_defaults", function(e){
        e.preventDefault();
        var postData = collectGallery( $(this).serialize() , 'settings' );

        var url = $( this ).attr( 'action' );
        var posting = $.post(url, postData, function(data) {
                if(data.success == 1){
                    $( '.info-message' ).html('<p class="text-success">'+data.message+'</p>');
                }else{
                    $( '.info-message' ).html('<p class="text-error">'+data.message+'</p>');
                }
            });
    });


    $(document).on("click", 'button#research_generate', function(){
        var attributes = $.post( base_url+'index.php/editor/attributes', { s: $('input[name="research_text"]').val() }, 'json' );
        attributes.done(function( data ) {
            products = data['product_descriptions'];

            var description = $('.boxes').find('textarea[name="short_description"]');
            description.removeAttr('disabled');
            description.val(products[0]);
            description.trigger('change');
            current_product = 1;
            $('#pagination').html(getPager());
        });
        return false;
    });

    $(document).on("click", ".boxes_content #pagination a", function(event){
        event.preventDefault();
        current_product = $(this).data('page');
        if ($(this).data('page')!==undefined) {
            var description = $('.boxes').find('textarea[name="short_description"]');
            description.val(products[current_product-1]);
            description.trigger('change');
            $('#pagination').html(getPager());
        }
    });
});
//var start = new Date().getMilliseconds();
//console.log("Executed in " + (new Date().getMilliseconds() - start) + " milliseconds");