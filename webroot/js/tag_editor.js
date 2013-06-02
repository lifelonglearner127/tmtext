/*----------------------------Tag Editor---------------------------------------------*/
var next = 0;
var action = '';
var last_input = '';
var last_edition = '';
var desc_input = '';
var max_prod_desc = 0;
var random_descriptions = false;

function cursorEnd(){
    var el = $("#tageditor_content #items_list li input:text").get(0);
    if(el!=undefined){
        var elemLen = el.value.length;
        el.selectionStart = elemLen;
        el.selectionEnd = elemLen;
        el.focus();
    }
}

function pipe_replace(reg, str,n) {
    m = 0;
    return str.replace(reg, function (x) {
        //was n++ should have been m++
        m++;
        if (n==m) {
            return '<span class="highlight" id="'+n+'">'+x+'</span>';
        } else {
            return x;
        }
    });
}

$(document).ready(function() {
    $('html').click(function(event) {
        if($(event.target).parents().index($('#tageditor_content')) == -1) {
            $("#tageditor_content #items_list li").each(function(){
                $(this).css({'background':'none'})
            });
            $("#tageditor_content #items_list li input").each(function(){
                $(this).parent().html('<span>'+$(this).val()+'</span>');
            });
        }
    });

    $(document).on("click", "#tageditor_description ul li", function(){
        return false;
    });

    $(document).on("focusout", "#tageditor_content #items_list li", function(){
        $(this).parent().html('<span>'+$(this).val()+'</span>');
    });

    $(document).on("focusout", "#tageditor_content #items_list li input", function(){
        return false;
    });

    $(document).on("click", "#tageditor_content #items_list li input", function(){
        $("#tageditor_content #items_list li").each(function(){
            $(this).css({'background':'none'})
        });
        $(this).parent().css({'background':'#CAEAFF'});
    });

    $(document).on("keypress", "#tageditor_content #items_list li input", function(e){
        action = 'edit';
        if(e.keyCode == 13 || e.keyCode == 8){
            $("#tageditor_content #items_list li").each(function(){
                $(this).css({'background':'none'})
            });
            $("#tageditor_content #items_list li input").each(function(){
                $(this).parent().html('<span>'+$(this).val()+'</span>');
            });
        } else {
            if(e.keyCode == 38){
                if($(this).parent().prev().length > 0) {
                    $("#tageditor_content #items_list li").each(function(){
                        $(this).css({'background':'none'});
                    });
                    $(this).parent().prev().css({'background':'#CAEAFF'});
                    $(this).parent().prev().html("<input type='text' name='tagRule[]' value='"+$(this).parent().prev().text()+"'>");
                    $(this).parent().html('<span>'+$(this).val()+'</span>');
                }
            }
            if(e.keyCode == 40){
                if($(this).parent().next().length > 0) {
                    $("#tageditor_content #items_list li").each(function(){
                        $(this).css({'background':'none'});
                    });
                    $(this).parent().next().css({'background':'#CAEAFF'});
                    $(this).parent().next().html("<input type='text' name='tagRule[]' value='"+$(this).parent().next().text()+"'>");
                    $(this).parent().html('<span>'+$(this).val()+'</span>');
                }
            }
            cursorEnd();
            last_edition = $(this).val();
        }
    });

    $(document).on("click", "#tageditor_content #items_list li span", function(){
        action = 'edit_input';
        last_edition = $("#tageditor_content #items_list li input").val();
        $("#tageditor_content #items_list li").each(function(){
            $(this).css({'background':'none'});
        });
        $("#tageditor_content #items_list li input").each(function(){
            $(this).parent().html('<span>'+$(this).val()+'</span>');
        });
        $(this).parent().css({'background':'#CAEAFF'});
        last_input = $(this).text();
        $(this).parent().html("<input type='text' name='tagRule[]'value='"+$(this).text()+"'>");
        if($(this).parent().find('input')){
            cursorEnd();
        }
    });

    $(document).on("change ready", "select[name='category']", function(){
        $.post(base_url + 'index.php/admin_tag_editor/file_data', { category: $("select[name='category'] option:selected").text() })
            .done(function(data) {
                $('#tageditor_content #items').html(data);
                $("#tageditor_description").trigger("file_data_ready");  // ready sometimes doesn't work
            });
    });
    $("select[name='category']").trigger("change");

    $(document).on("file_data_ready", "#tageditor_description", function(){
        $.post(base_url + 'index.php/admin_tag_editor/get_product_description', { category: $("select[name='category'] option:selected").text() , limit:$('#description_limit').val(), random: random_descriptions })
            .done(function(data) {
                var type = typeof data;
                if (type == "object") {
                	var str = '';
                	if ( data.descriptions !== undefined ) {
	                	str = '<ul id="desc_count_'+data.desc_count+'">';

	                	$.each(data.descriptions, function(i,e){
	                		str += "<li>"+e+"\n</li>";
	                    });
	                    str += '</ul>';

	                    max_prod_desc = data.quantity;
                	} else {
	                	str = '<ul>';
	                    if(data.length == 1){
	                        var arr = data[0].description.split('\n');
	                        for(var i=0; i<arr.length; i++){
	                            if(arr[i] != ''){
	                                str += '<li class="row">'+arr[i]+'\n</li>';
	                            }
	                        }
	                    } else {
	                        for(var i=0; i < data.length; i++){
	                            for(var j=0; j<data[i].length; j++){
	                                if(data[i][j].description != ''){
	                                    str += '<li class="row">'+data[i][j].description+'\n</li>';
	                                }
	                            }
	                        }
	                    }
	                    str += '</ul>';
                	}

                    $('#tageditor_description').html(str);
                    $('#standart_description').html(str);
                }  else if (type == "string") {
                    $('#tageditor_description').html(data);
                    $('#standart_description').html(data);
                }
                random_descriptions = false;
            });
        return false;
    });

    $("#tageditor_description").trigger("ready");
    /*---------------------------Buttons---------------------------------*/

    $("a#delete_category").fancybox({ 'beforeShow': function(){ $('#category_name').text($("select[name='category'] option:selected").text()); } });

    $(document).on("click", "button#yes", function(){
        $.post(base_url + 'index.php/admin_tag_editor/delete_file', { category: $("select[name='category'] option:selected").text() })
            .done(function(data) {
                $.fancybox.close();
                $("select[name='category'] option:selected").remove();
                $("select[name='category']").trigger('change');
            });
        return false;
    });

    $(document).on("click", "button#no", function(){
        $.fancybox.close();
        return false;
    });

    $(document).on("click", "button#create", function(){
        if($('input[name="new_file"]').val() !='' ){
            var cat_exist = 0;
            $("#tageditor_description").html('');
            $('select[name="category"] option').each(function(){
                 if($(this).text() == $('input[name="new_file"]').val()){
                     cat_exist = 1;
                 }
            });
            if(cat_exist == 0){
                $('select[name="category"]').append('<option selected="selected">'+$('input[name="new_file"]').val()+'</option>');
                $('#tageditor_content #items_list').empty();
                $("#tageditor_content button#new").trigger('click');
                var arr = new Array();
                $.post(base_url + 'index.php/admin_tag_editor/save_file_data', { data: arr, category: $('input[name="new_file"]').val() })
                    .done(function(data) {
                    });
                return false;
            }
        }
        return false;
    });

    $(document).on("click", "button#test", function(){
        if($("#tageditor_content #items_list li").find('input')!=''
            && $("#tageditor_content #items_list li input").val()!=undefined && $("#tageditor_content #items_list li input").val()!=''){
            $('span.matches_found').empty();
            var regtext = $("#tageditor_content #items_list li input").val();
            var re = new RegExp('"(.*)"\,', 'gi');
            var regexp = regtext.split(re);
            var querystr = regexp[1];
            if(querystr != undefined && querystr != ''){
                var reg = new RegExp(querystr, 'gi');
                var result = $('#standart_description').html();
                var desc_count = 0;
                $('#standart_description ul li.row').each(function(){
                    if($(this).text() != ''){
                        if(reg.test($(this).text())){
                            desc_count++;
                        }
                    }
                });

                var n = 0;
                var final_str = result.replace(reg, function(str) {
                    n++;
                    return '<span id="'+n+'" class="highlight">'+str+'</span>';
                });
                if($('#tageditor_description ul').attr('id')!='' && $('#tageditor_description ul').attr('id')!=undefined){
                    desc_count = parseInt($('#tageditor_description ul').attr('id').replace('desc_count_', ''));
                }
                if(desc_count > 1){
                    str = desc_count + ' descriptions';
                } else {
                    str = desc_count + ' description';
                }
                $('span.matches_found').html(n+' matches found in '+ str);
                $('#tageditor_description').html(final_str);
                next=1;
                $('#tageditor_description').scrollTo( 'span#'+next, 500, { easing:'swing', queue:true, axis:'xy' } );
            }
        }
        return false;
    });

    $(document).on("click", "button#next", function(){
        if($("#tageditor_content #items_list li").find('input')!=''
            && $("#tageditor_content #items_list li input").val()!=undefined && $("#tageditor_content #items_list li input").val()!=''){
            var regtext = $("#tageditor_content #items_list li input").val();
            var re = new RegExp('"(.*)"\,', 'gi');
            var regexp = regtext.split(re);
            var querystr = regexp[1];
            if(querystr != undefined && querystr !=''){
                var result = $('#standart_description').html();
                var reg = new RegExp(querystr, 'gi');
                var n = 0;
                next++;
                final_str = pipe_replace(reg, result, next);
                if (final_str.indexOf('span') == -1)  {
                    next = 1;
                    final_str = pipe_replace(reg, result, next);
                }
                $('#tageditor_description').html(final_str);
                $('#tageditor_description').scrollTo( 'span#'+next, 500, { easing:'swing', queue:true, axis:'xy' } );
            }
        }
        return false;
    });

    $(document).on("click", "button#new", function(){
        $("button#save_data").trigger('click');
        $("#tageditor_content #items_list li").each(function(){
            $(this).css({'background':'none'});
        });
        $("#tageditor_content #items_list li input").each(function(){
            $(this).parent().html('<span>'+$(this).val()+'</span>');
        });
        $('#tageditor_content #items_list').append("<li><input type='text' name='tagRule[]'value=''></li>");
        $('#tageditor_content #items_list li:last-child').css({'background':'#CAEAFF'});
        $('#tageditor_content #items_list li:last-child input').focus();
        return false;
    });

    $(document).on("click", "button#delete", function(){
        action = 'delete';
        $("#tageditor_content #items_list li input").parent().addClass('hidden_class');
        $("#tageditor_content #items_list li input").parent().show().fadeOut("slow");
        return false;
    });

    $(document).on("click", "button#undo", function(){
        if(action == ''){
            return false;
        }
        if(action == 'delete'){
            $("#tageditor_content #items_list li input").parent().removeClass('hidden_class');
            $("#tageditor_content #items_list li input").parent().show().fadeIn("slow");
        } else if(action == 'edit'){
            $("#tageditor_content #items_list li input").val(last_input);
        } else if(action == 'edit_input'){
            if(last_edition == undefined) {
                return false;
            }

            $("#tageditor_content #items_list li").each(function(){
                if($(this).find("span").text() == last_edition){
                    $(this).css({'background':'#CAEAFF'});
                    $(this).html("<input type='text' name='tagRule[]'value='"+last_edition+"'>");
                }
                if($(this).find("input").val() == last_input){
                    $(this).css({'background':'none'});
                    $(this).html('<span>'+last_input+'</span>');
                }
            });
        }
        cursorEnd();
        action = '';
        return false;
    });

    $(document).on("click", "button#save_data", function(){
        var arr = new Array();
        $('#tageditor_content #items_list li').each(function(){
                if($(this).attr('class') != 'hidden_class'){
                    if($(this).find('input').val()!=undefined){
                        arr += $(this).find('input').val();
                    } else {
                        arr += $(this).text();
                    }
                    arr += '\n';
                }
        });
        $.post(base_url + 'index.php/admin_tag_editor/save_file_data', { data: arr, category: $("select[name='category'] option:selected").text() })
            .done(function(data) {
        });
        return false;
    });

    $(document).on("click", "button#export", function(e){
        e.preventDefault();
        if($("select[name='category'] option:selected").text() != 'All'){
            window.location.href = base_url + 'index.php/admin_tag_editor/export_rules?category='+$("select[name='category'] option:selected").text();
        }
        return false;
    });

    $(document).on("click", "button#new_desc", function(){
        $('#tageditor_description').empty();
        return false;
    });

    $(document).on("click", "button#save_desc", function(){
        $.post(base_url + 'index.php/admin_tag_editor/save', { description: $('#tageditor_description').text(), category: $("select[name='category'] option:selected").text() })
            .done(function(data) {
                $('#standart_description').html($('#tageditor_description').text());
        });
        return false;
    });

    $(document).on("click", "button#delete_desc", function(){
        $.post(base_url + 'index.php/admin_tag_editor/delete', { description: $('#tageditor_description').text(), category: $("select[name='category'] option:selected").text() })
            .done(function(data) {
                $('#tageditor_description').empty();
            });
        return false;
    });

    $(document).on("click", "#items", function(event){
        var str = '';
        $('#tageditor_content #items_list li').each(function(){
            if($(this).attr('class') != 'hidden_class'){
                if($(this).find('input').val()!=undefined){
                    str += $(this).find('input').val();
                } else {
                    str += $(this).text();
                }
            }
        });

        if($(event.target).index($('div#items.span10')) != -1 && str != ""
            && $('#tageditor_content #items_list li').find('input').val()!=undefined){
            $("button#save_data").trigger('click');
            $("#tageditor_content #items_list li").each(function(){
                $(this).css({'background':'none'})
            });
            $("#tageditor_content #items_list li input").each(function(){
                $(this).parent().html('<span>'+$(this).val()+'</span>');
            });
        } else if(str == "" || $('#tageditor_content #items_list li').find('input').val()==undefined){
            $("button#new").trigger('click');
        }
        return false;
    });

    $(document).on("click", "#input_fln_up, #input_fln_down", function(event){
    	var inp = $(this).parent().find('input');
    	if ( $(this).attr('id') == 'input_fln_up' && parseInt(inp.val()) < max_prod_desc ) {
    		inp.val(parseInt(inp.val())+1);
    	} else if ( $(this).attr('id') == 'input_fln_down' && parseInt(inp.val()) > 1 ) {
    		inp.val(parseInt(inp.val())-1);
    	}
    	return false;
    });

    $(document).on("click", "#new_test_set", function(event){
    	 random_descriptions = true;
    	 $("#tageditor_description").trigger("file_data_ready");

    	 return false;
    });

});

/*---------------------------------------------------------------------------------------*/