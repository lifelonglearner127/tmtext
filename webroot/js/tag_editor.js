/*----------------------------Tag Editor---------------------------------------------*/
var next = 0;
var action = '';
var last_input = '';
var last_edition = '';
var desc_input = '';

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

jQuery(document).ready(function($) {
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

    $(document).on("change", "select[name='filename']", function(){
        $.post('admin_tag_editor/file_data', { filename: $("select[name='filename'] option:selected").text() })
            .done(function(data) {
                $('#tageditor_content #items').html(data);
            });
    });    
    $("select[name='filename']").trigger("change");
    
    $(document).on("ready", "#tageditor_description", function(){
        $.post('admin_tag_editor/get_product_description', {})
            .done(function(data) {
                var type = typeof data;
                if (type == "object") {
                    var arr = data[0].description.split('\n');
                    var str = '<ul>';
                    for(var i=0; i<arr.length; i++){
                        if(arr[i] != ''){
                            str += '<li class="row">'+arr[i]+'\n</li>';
                        }                        
                    }
                    str += '</ul>';
                    $('#tageditor_description').html(str);
                    $('#standart_description').html(str);
                }  else if (type == "string") {
                    $('#tageditor_description').html(data);
                    $('#standart_description').html(data);
                }                                
        });
        return false;
    });  
    $("#tageditor_description").trigger("ready");
    /*---------------------------Buttons---------------------------------*/
    
    $("a#delete_category").fancybox({ 'beforeShow': function(){ $('#category_name').text($("select[name='filename'] option:selected").text()); } });

    $(document).on("click", "button#yes", function(){
        $.post('admin_tag_editor/delete_file', { filename: $("select[name='filename'] option:selected").text() })
            .done(function(data) {
                $.fancybox.close();
                $("select[name='filename'] option:selected").remove();
                $("select[name='filename']").trigger('change');
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
            $('select[name="filename"] option').each(function(){
                 if($(this).text() == $('input[name="new_file"]').val()){
                     cat_exist = 1;
                 }
            });
            if(cat_exist == 0){
                $('select[name="filename"]').append('<option selected="selected">'+$('input[name="new_file"]').val()+'</option>');
                $('#tageditor_content #items_list').empty();
                $("#tageditor_content button#new").trigger('click');
                var arr = new Array();
                $.post('admin_tag_editor/save_file_data', { data: arr, filename: $('input[name="new_file"]').val() })
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
        $.post('admin_tag_editor/save_file_data', { data: arr, filename: $("select[name='filename'] option:selected").text() })
            .done(function(data) {
        });
        return false;
    });

    $(document).on("click", "button#new_desc", function(){
        $('#tageditor_description').empty();
        return false;
    });

    $(document).on("click", "button#save_desc", function(){
        $.post('admin_tag_editor/save', { description: $('#tageditor_description').text() })
            .done(function(data) {
                $('#standart_description').html($('#tageditor_description').text());
        });
        return false;
    });

    $(document).on("click", "button#delete_desc", function(){
        $.post('admin_tag_editor/delete', { description: $('#tageditor_description').text() })
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
});

/*---------------------------------------------------------------------------------------*/