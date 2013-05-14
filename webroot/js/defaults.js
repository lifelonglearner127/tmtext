var current_product = 0;
var products = '';
var attribs = '';
var rev = [];
var search_id = undefined;
var sentence = '';
var next = 0;
var actions = [];

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

function moveSentence() {
    // there's the desc and the trash
    var $desc = $( "#desc" ),
        $trash = $( "#trash" );

    $( "#desc, #trash" ).sortable({
        connectWith: ".desc",
        revert: "invalid",
        cursor: "move",
    }).disableSelection();

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
    });
}

jQuery(document).ready(function($) {

	$('.new_product #textarea').on('keyup change',function() {
        $('textarea[name="description"]').val($('.new_product #textarea span').text()).trigger('change');
	});

	$('textarea[name="description"]').on('keydown change',function() {
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

	$( ".auto_title #title" ).on('keydown change',function() {
		var _limit = $('input[name="title_length"]').val();
		if($(this).val().length > _limit) {
			var string = $(this).val();
			$(this).val(string.substring(0, _limit));
		}
		$('#tc').html($(this).val().length);
	});

	$("#searchForm").submit(function(event) {
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
			    description.val(products[0]);products
			    description.trigger('change');

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
            console.log(products[current_product-1]);
			description.val(products[current_product-1]);
            descriptionDiv.html('<ul id="desc" class="desc_title desc">'+sentence+' '+'<li><span class="current_product">'+
                products[current_product-1]+'</span><a hef="#" class="ui-icon-trash">x</a></li>').trigger('change');
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
		var description =  $('.new_product #textarea span').text();
		//$('.new_product').find('textarea[name="description"]').val();
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
		var d = $('.new_product #textarea span').text();
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

			console.log(rev);
		 });
	});

    $(document).on("click", "#tageditor_content #items_list li span", function(){
        $("#tageditor_content #items_list li").each(function(){
            $(this).css({'background':'none'});
        });
        $("#tageditor_content #items_list li input").each(function(){
            $(this).parent().html('<span>'+$(this).val()+'</span>');
        });
        $(this).parent().css({'background':'#CAEAFF'});
        $(this).parent().html("<input type='text' name='tagRule[]'value='"+$(this).text()+"'>");
    });

    $(document).on("click", "#tageditor_content #items_list li input", function(){
        $("#tageditor_content #items_list li").each(function(){
            $(this).css({'background':'none'})
        });
        $(this).parent().css({'background':'#CAEAFF'});
    });

    $(document).on("focusout", "#tageditor_content #items_list li", function(){
        $(this).parent().html('<span>'+$(this).val()+'</span>');
    });

    $(document).on("change", "select[name='filename']", function(){
        $.post('admin_tag_editor/file_data', { filename: $("select[name='filename'] option:selected").text() })
            .done(function(data) {
            $('#tageditor_content #items').html(data);
        });
    });

    $(document).on("click", "button#test", function(){
        if($("#tageditor_content #items_list li").find('input')!=''
            && $("#tageditor_content #items_list li input").val()!=undefined && $("#tageditor_content #items_list li input").val()!=''){
            $('span.matches_found').empty();
            var regtext = $("#tageditor_content #items_list li input").val().split(',');
            var querystr = regtext[0].slice(1).slice(0,-1);
            if(querystr != undefined && querystr != ''){
                var result = $('#standart_description').html();
                var reg = new RegExp(querystr, 'gi');
                var n = 0;
                var final_str = result.replace(reg, function(str) {
                    n++;
                    return '<span id="'+n+'" class="highlight">'+str+'</span>';
                });
                $('span.matches_found').html(n+' matches found');
                $('#tageditor_description').html(final_str);
                next=1;
                $('#tageditor_description').scrollTo( 'span#'+next, 500, { easing:'swing', queue:true, axis:'xy' } );
            }
        }
        return false;
    });

    $(document).on("click", "button#save_data", function(){
        var arr = new Array();
        $('#tageditor_content #items_list li').each(function(){
            if($(this).find('input').val()==undefined){
               arr += $(this).text()+"\n";
            } else {
                arr += $(this).find('input').val()+"\n";
            }
        });
        $.post('admin_tag_editor/save_file_data', { data: arr, filename: $("select[name='filename'] option:selected").text() })
            .done(function(data) {
        });
        return false;
    });

    $(document).on("click", "#tageditor_description ul li", function(){
        return false;
    });

    $(document).on("keypress", "#tageditor_content #items_list li input", function(e){
        if(e.keyCode == 13){
            return false;
        }
    });

    $(document).on("focusout", "#tageditor_content #items_list li input", function(){
        return false;
    });

    $(document).on("click", "#tageditor_content button#new", function(){
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

    $(document).on("click", "button#create", function(){
        $('select[name="filename"]').append('<option selected="selected">'+$('input[name="new_file"]').val()+'</option>');
        $('#tageditor_content #items_list').empty();
        $("#tageditor_content button#new").trigger('click');
        return false;
    });

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

    $(document).on("click", "#tageditor_content button#next", function(){
        if($("#tageditor_content #items_list li").find('input')!=''
            && $("#tageditor_content #items_list li input").val()!=undefined && $("#tageditor_content #items_list li input").val()!=''){
            var regtext = $("#tageditor_content #items_list li input").val().split(',');
            var querystr = regtext[0].slice(1).slice(0,-1);
            if(querystr != undefined && querystr !=''){
                var result = $('#standart_description').html();
                var reg = new RegExp(querystr, 'g');
                var n = 0;
                next++;
                final_str = pipe_replace(reg, result, next);
                $('#tageditor_description').html(final_str);
                $('#tageditor_description').scrollTo( 'span#'+next, 500, { easing:'swing', queue:true, axis:'xy' } );
            }
        }
        return false;
    });

    $(document).on("click", "#tageditor_content button#delete", function(){
        $("#tageditor_content #items_list li input").parent().remove();
        return false;
    });

    $(document).on("click", "button#use", function(){
        sentence = $('#textarea ul#desc').html().replace('current_product', '');
        return false;
    });

    $(document).on("click", "button#undo", function(){
        return false;
    });
});
//var start = new Date().getMilliseconds();
//console.log("Executed in " + (new Date().getMilliseconds() - start) + " milliseconds");
