var readUrl   = base_url + 'index.php/measure/get_best_sellers',
updateUrl = base_url + 'index.php/measure/',
delUrl    = base_url + 'index.php/measure/',
delHref,
updateHref,
updateId,
delId;


$( function() {

    // readBestSellers();
    dataTable = $( '#records' ).dataTable({
        "bJQueryUI": true
    });
    dataTableSec = $( '#recordSec' ).dataTable({
        "bJQueryUI": true
    });
	
    // $( '#tabs' ).tabs({
    // fx: { height: 'toggle', opacity: 'toggle' }
    // });
    // $( '#msgDialog' ).dialog({
    // autoOpen: false,

    // buttons: {
    // 'Ok': function() {
    // $( this ).dialog( 'close' );
    // }
    // }
    // });

    // $( '#updateDialog' ).dialog({
    // autoOpen: false,
    // buttons: {
    // 'Update': function() {
    // $( '#ajaxLoadAni' ).fadeIn( 'slow' );
    // $( this ).dialog( 'close' );

    // $.ajax({
    // url: updateHref,
    // type: 'POST',
    // data: $( '#updateDialog form' ).serialize(),

    // success: function( response ) {
    // $( '#msgDialog > p' ).html( response );
    // $( '#msgDialog' ).dialog( 'option', 'title', 'Success' ).dialog( 'open' );

    // $( '#ajaxLoadAni' ).fadeOut( 'slow' );

    // --- update row in table with new values ---
    // var title = $( 'tr#' + updateId + ' td' )[ 2 ];

    // $( title ).html( $( '#title' ).val() );

    // --- clear form ---
    // $( '#updateDialog form input' ).val( '' );

    // } //end success

    // }); //end ajax()
    // },

    // 'Cancel': function() {
    // $( this ).dialog( 'close' );
    // }
    // },
    // width: '350px'
    // }); //end update dialog

    // $( '#delConfDialog' ).dialog({
    // autoOpen: false,

    // buttons: {
    // 'No': function() {
    // $( this ).dialog( 'close' );
    // },

    // 'Yes': function() {
    // display ajax loader animation here...
    // $( '#ajaxLoadAni' ).fadeIn( 'slow' );
    // $( this ).dialog( 'close' );

    // $.ajax({
    // url: delHref,
    // type:'POST',
    // data:{'id': delId},
    // success: function( response ) {
    // hide ajax loader animation here...
    // $( '#ajaxLoadAni' ).fadeOut( 'slow' );

    // $( '#msgDialog > p' ).html( response );
    // $( '#msgDialog' ).dialog( 'option', 'title', 'Success' ).dialog( 'open' );

    // $( 'a[href=' + delHref + ']' ).parents( 'tr' )
    // .fadeOut( 'slow', function() {
    // $( this ).remove();
    // });

    // } //end success
    // });

    // } //end Yes

    // } //end buttons

    // }); //end dialog

    // $( '#records' ).delegate( 'a.updateBtn', 'click', function() {
    // updateHref = $( this ).attr( 'href' );
    // updateId = $( this ).parents( 'tr' ).attr( "id" );

    // $( '#ajaxLoadAni' ).fadeIn( 'slow' );

    // $.ajax({
    // url: base_url + 'index.php/system/getBatchById/' + updateId,
    // dataType: 'json',

    // success: function( response ) {
    // $( 'input#title' ).val( response[0].title );

    // $( '#ajaxLoadAni' ).fadeOut( 'slow' );

    //--- assign id to hidden field ---
    // $( '#userId' ).val( updateId );

    // $( '#updateDialog' ).dialog( 'open' );
    // }
    // });

    // return false;
    // }); //end update delegate

    // $( '#records' ).delegate( 'a.deleteBtn', 'click', function() {
    // delHref = $( this ).attr( 'href' );
    // delId = $( this ).parents( 'tr' ).attr( "id" );
    // $('span.batch_name').text($( 'tr#'+delId+' td:nth-child(3)' ).text());
    // $( '#delConfDialog' ).dialog( 'open' );

    // return false;

    // }); //end delete delegate
	
	
	
    $(".hp_boot_drop .dropdown-menu > li > a").bind('click', function(e) {
        var new_caret = $.trim($(this).text());
        var item_id = $(this).data('item');
        $('#departments_content').html('');
        $("#hp_boot_drop .btn_caret_sign").text(new_caret);
        $("tbody#department_data").empty();
        $("tbody#category_data").empty();
        //$("#departmentDropdown").show();
        $.post(base_url + 'index.php/measure/getDepartmentsByCustomer', {
            'customer_name': new_caret
        }, function(data) {
            $("#departmentDropdown .dropdown-menu").empty();
            if(data.length > 0){
				$("#departmentDropdown").show();
                $(".dashboard").show();
                $("tbody#department_data").show();
                $("#hp_boot_drop_sec_dashboard .btn_caret_sign_sec").text('Departments');
                var site_name=$('#hp_boot_drop .btn_caret_sign').text();
                $.post(base_url + 'index.php/measure/getDashboardDepData', {
                    'site_name': site_name
                }, function(data) {
                    var add_min_text250 = 250 - data.res250_top_wc;
                    var add_max_text250 = 250 - data.res250_low_wc;
                    var add_text250 = '';
                    if(add_min_text250 == add_max_text250){
                        add_text250 = add_min_text250;
                    } else {
                        add_text250 = add_min_text250+' - '+add_max_text250;
                    }
                    var add_min_text200 = 200 - data.res200_top_wc;
                    var add_max_text200 = 200 - data.res200_low_wc;
                    var add_text200 = '';
                    if(add_min_text200 == add_max_text200){
                        add_text200 = add_min_text200;
                    } else {
                        add_text200 = add_min_text200+' - '+add_max_text200;
                    }
                    var add_min_text150 = 150 - data.res150_top_wc;
                    var add_max_text150 = 150 - data.res150_low_wc;
                    var add_text150 = '';
                    if(add_min_text150 == add_max_text150){
                        add_text150 = add_min_text150;
                    } else {
                        add_text150 = add_min_text150+' - '+add_max_text150;
                    }
                    var data_str = '<tr><td nowrap>Total Analyzed:</td><td>'+data.total+'</td><td>&nbsp;</td></tr>';
                    data_str += '<tr><td nowrap>Description text < 250 words:</td><td>'+data.res250+'</td>' +
                        '<td>Add '+add_text250+' more words to '+data.res250+' department descriptions</td></tr>';
                    data_str += '<tr><td nowrap>Description text < 200 words:</td><td>'+data.res200+'</td>' +
                        '<td>Add '+add_text200+' more words to '+data.res200+' department descriptions</td></tr>';
                    data_str += '<tr><td nowrap>Description text < 150 words:</td><td>'+data.res150+'</td>' +
                        '<td>Add '+add_text150+' words to '+data.res150+' more department descriptions</td></tr>';
                    data_str += '<tr><td nowrap>Description text < 250 words:</td><td>'+data.res0+'</td>' +
                        '<td>Add descriptions to '+data.res0+' departments</td></tr>';
                    data_str += '<tr><td nowrap>Need keyword optimization:</td><td>'+data.keyword_optimize+'</td>' +
                        '<td>Keyword optimize '+data.keyword_optimize+' departments</td></tr>';
                    data_str += '<tr><td nowrap>Contain duplicate content:</td><td></td><td>(Coming soon)</td></tr>';
                    $("tbody#department_data").append(data_str);
                });
                //$('#tabs').show();
                $("#departmentDropdown .dropdown-menu").append("<li><a data-item=\"empty\" data-value=\"\" href=\"javascript:void(0);\">Choose department</a></li><li><a data-item=\"\" data-value=\"All\" href=\"javascript:void(0);\">All</a></li>");
                for(var i=0; i<data.length; i++){
                    if(i == 0){
                        $('#departmentDropdown .btn_caret_sign1').text('Choose Department');
                    }
                    $("#departmentDropdown .dropdown-menu").append("<li><a data-item="+data[i].id+" data-value="+data[i].text+" href=\"javascript:void(0);\">"+data[i].text+"</a></li>");
                }
            } else {
                $(".dashboard").hide();
                $('#departmentDropdown').hide();
                $('#departmentDropdown .btn_caret_sign1').text('empty');
                //$('#tabs').hide();
            }
            var stringNewData = '<table id="records" ><thead><tr><th style="width: 112px !important;word-wrap: break-word;" >Categories ()</th>' +
                '<th style="width: 60px !important;" nowrap >Items</th><th style="width:160px!important" nowrap>Keyword Density</th>' +
                '<th style="width: 60px !important;" nowrap>Words</th></tr></thead><tbody></tbody></table>';
            $( '#dataTableDiv1' ).html(stringNewData);
            $( '#records' ).dataTable({
                "bJQueryUI": true
            });
        });

    });

    $("#departmentDropdown .dropdown-menu > li > a").live('click', function(e) {
        var departmentValue = $.trim($(this).text());
        var department_id = $(this).data('item');
        $("input[name='selected_department_id']").val(department_id);
        //console.log(department_id);
        var site_name=$('.btn_caret_sign').text()
        $("#departmentDropdown_first").text(departmentValue);
        readBestSellers(department_id,site_name,'records');

        /*****departmentAjax****/
        if(department_id != '' && department_id != 'empty'){
            departmentAjax(department_id,site_name);
            $('#tabs').show();
            $('.table_results').show();
            $.post(base_url + 'index.php/measure/getUrlByDepartment', {
                'department_id': department_id
            }, function(data) {
                $("a#department_url").attr('href', data[0].url);
                $("a#department_url").show();
            });
        } else if(department_id == 'empty'){
            $('#departments_content').html('');
            $('.table_results').hide();
            $('#tabs').hide();
            $("a#department_url").hide();
        } else {
            $('#tabs').show();
            $('.table_results').show();
            $('#departments_content').html('');
            $("a#department_url").hide();
        }
        
    });
		
		
    //Compare with Begin
		
		
    $(".hp_boot_drop_sec .dropdown-menu > li > a").bind('click', function(e) {
        var new_caret = $.trim($(this).text());
        var item_id = $(this).data('item');
        $("#hp_boot_drop_sec .btn_caret_sign_sec").text(new_caret);
        $("#departmentDropdownSec").show();
        $.post(base_url + 'index.php/measure/getDepartmentsByCustomer', {
            'customer_name': new_caret
        }, function(data) {
            $("#departmentDropdownSec .dropdown-menu").empty();
            if(data.length > 0){
                $("#departmentDropdownSec .dropdown-menu").append("<li><a data-item=\"empty\" data-value=\"\" href=\"javascript:void(0);\">Choose department</a></li><li><a data-item=\"\" data-value=\"All\" href=\"javascript:void(0);\">All</a></li>");
                for(var i=0; i<data.length; i++){
                    if(i == 0){
                        $('#departmentDropdownSec .btn_caret_sign_sec1').text('Choose Department');
                    }
                    $("#departmentDropdownSec .dropdown-menu").append("<li><a data-item="+data[i].id+" data-value="+data[i].text+" href=\"javascript:void(0);\">"+data[i].text+"</a></li>");
                }
            } else {
                $('#departmentDropdownSec .btn_caret_sign_sec1').text('empty');
            }
            var stringNewData = '<table id="recordSec" ><thead><tr><th style="width: 112px !important;word-wrap: break-word;" nowrap>Categories ()</th>' +
                '<th style="width: 60px!important;" nowrap>Items</th>' +
                '<th style="width:160px!important" nowrap>Keyword Density</th><th style="width:60px!important;" nowrap>Words</th></tr></thead><tbody></tbody></table>';
            $( '#dataTableDiv2' ).html(stringNewData);
            $( '#recordSec' ).dataTable({
                "bJQueryUI": true
            });
        });

    });

    $("#departmentDropdownSec .dropdown-menu > li > a").live('click', function(e) {
        var departmentValue = $.trim($(this).text());
        var department_id = $(this).data('item');
        var site_name=$('.btn_caret_sign_sec').text()
        $("#departmentDropdownSec_first").text(departmentValue);
        readBestSellers(department_id,site_name,'recordSec');
        console.log(department_id);
        /*****departmentAjax****/
        if(department_id != ''){
            departmentAjax(department_id,site_name);
            $('.table_results').show();
        } else if(department_id == 'empty'){
            $('#departments_content').html('');
            $('.table_results').hide();
        } else {
            $('.table_results').show();
            $('#departments_content').html('');
        }
    });

    $(".hp_boot_drop_sec_dashboard .dropdown-menu > li > a").bind('click', function(e) {
        var new_caret = $.trim($(this).text());
        var item_id = $(this).data('item');
        $("#hp_boot_drop_sec_dashboard .btn_caret_sign_sec").text(new_caret);
        $("tbody#category_data").empty();
        $("tbody#department_data").empty();
        if(new_caret == "Departments"){
            $("tbody#department_data").show();
            $("tbody#category_data").hide();
            var site_name=$('#hp_boot_drop .btn_caret_sign').text();
            $.post(base_url + 'index.php/measure/getDashboardDepData', {
                'site_name': site_name
            }, function(data) {
                var add_min_text250 = 250 - data.res250_top_wc;
                var add_max_text250 = 250 - data.res250_low_wc;
                var add_text250 = '';
                if(add_min_text250 == add_max_text250){
                    add_text250 = add_min_text250;
                } else {
                    add_text250 = add_min_text250+' - '+add_max_text250;
                }
                var add_min_text200 = 200 - data.res200_top_wc;
                var add_max_text200 = 200 - data.res200_low_wc;
                var add_text200 = '';
                if(add_min_text200 == add_max_text200){
                    add_text200 = add_min_text200;
                } else {
                    add_text200 = add_min_text200+' - '+add_max_text200;
                }
                var add_min_text150 = 150 - data.res150_top_wc;
                var add_max_text150 = 150 - data.res150_low_wc;
                var add_text150 = '';
                if(add_min_text150 == add_max_text150){
                    add_text150 = add_min_text150;
                } else {
                    add_text150 = add_min_text150+' - '+add_max_text150;
                }
                var data_str = '<tr><td nowrap>Total Analyzed:</td><td>'+data.total+'</td><td>&nbsp;</td></tr>';
                data_str += '<tr><td nowrap>Description text < 250 words:</td><td>'+data.res250+'</td>' +
                    '<td>Add '+add_text250+' more words to '+data.res250+' department descriptions</td></tr>';
                data_str += '<tr><td nowrap>Description text < 200 words:</td><td>'+data.res200+'</td>' +
                    '<td>Add '+add_text200+' more words to '+data.res200+' department descriptions</td></tr>';
                data_str += '<tr><td nowrap>Description text < 150 words:</td><td>'+data.res150+'</td>' +
                    '<td>Add '+add_text150+' words to '+data.res150+' more department descriptions</td></tr>';
                data_str += '<tr><td nowrap>Description text 0 words:</td><td>'+data.res0+'</td>' +
                    '<td>Add descriptions to '+data.res0+' departments</td></tr>';
                data_str += '<tr><td nowrap>Need keyword optimization:</td><td>'+data.keyword_optimize+'</td>' +
                    '<td>Keyword optimize '+data.keyword_optimize+' departments</td></tr>';
                data_str += '<tr><td nowrap>Contain duplicate content:</td><td></td><td>(Coming soon)</td></tr>';
                $("tbody#department_data").append(data_str);
            });
        } else {
            $("tbody#department_data").hide();
            $("tbody#category_data").show();
            var site_name=$('#hp_boot_drop .btn_caret_sign').text();
            $.post(base_url + 'index.php/measure/getDashboardCatData', {
                'site_name': site_name
            }, function(data) {
                var add_min_text250 = 250 - data.res250_top_wc;
                var add_max_text250 = 250 - data.res250_low_wc;
                var add_text250 = '';
                if(add_min_text250 == add_max_text250){
                    add_text250 = add_min_text250;
                } else {
                    add_text250 = add_min_text250+' - '+add_max_text250;
                }
                var add_min_text200 = 200 - data.res200_top_wc;
                var add_max_text200 = 200 - data.res200_low_wc;
                var add_text200 = '';
                if(add_min_text200 == add_max_text200){
                    add_text200 = add_min_text200;
                } else {
                    add_text200 = add_min_text200+' - '+add_max_text200;
                }
                var add_min_text150 = 150 - data.res150_top_wc;
                var add_max_text150 = 150 - data.res150_low_wc;
                var add_text150 = '';
                if(add_min_text150 == add_max_text150){
                    add_text150 = add_min_text150;
                } else {
                    add_text150 = add_min_text150+' - '+add_max_text150;
                }
                var data_str = '<tr><td nowrap>Total Analyzed:</td><td>'+data.total+'</td><td>&nbsp;</td></tr>';
                data_str += '<tr><td nowrap>Description text < 250 words:</td><td>'+data.res250+'</td>' +
                    '<td>Add '+add_text250+' more words to '+data.res250+' category descriptions</td></tr>';
                data_str += '<tr><td nowrap>Description text < 200 words:</td><td>'+data.res200+'</td>' +
                    '<td>Add '+add_text200+' more words to '+data.res200+' category descriptions</td></tr>';
                data_str += '<tr><td nowrap>Description text < 150 words:</td><td>'+data.res150+'</td>' +
                    '<td>Add '+add_text150+' words to '+data.res150+' more category descriptions</td></tr>';
                data_str += '<tr><td nowrap>Description text 0 words:</td><td>'+data.res0+'</td>' +
                    '<td>Add descriptions to '+data.res0+' categories</td></tr>';
                data_str += '<tr><td nowrap>Need keyword optimization:</td><td>'+data.keyword_optimize+'</td>' +
                    '<td>Keyword optimize '+data.keyword_optimize+' categories</td></tr>';
                data_str += '<tr><td nowrap>Contain duplicate content:</td><td></td><td>(Coming soon)</td></tr>';
                $("tbody#category_data").append(data_str);
            });
        }
    });
    //Compare with End

    // $(document).on('click', 'table#records tbody tr', function(e){
    // e.preventDefault();
    // window.open($(this).find('td:nth-child(3)').text());
    // });

    $('.changeDensity').live('change',function(){
        var descriptionTitle = $(this).children('option:selected').text();
        var currentVal = $(this).val().trim();
        var densityCheck = '0.0';
        if($(this).val().trim() == ''){
            $(this).children('option').each(function(){
                if(($(this).val().trim() != '') && (descriptionTitle.replace('"','').replace('"','').trim().toLowerCase() == $(this).text().trim().toLowerCase()))
                    densityCheck = $(this).val();
            });
            $(this).next().html('\xa0'+densityCheck+'%');
        } else {
            $(this).next().text('\xa0'+$(this).val()+'%');
        }
    });
    $('input.your_keyword').bind('keypress', function(e) {
        if(e.keyCode==13){
            // Enter pressed... do anything here...
            console.log(111);
        }
    });
}); //end document ready

function readBestSellers(department_id,site_name,table_name) {
    //display ajax loader animation
    $( '#ajaxLoadAni' ).fadeIn( 'slow' );
	
    $.ajax({
        url: base_url + 'index.php/measure/getCategoriesByDepartment',
        dataType: 'json',
        type: "POST",
        data:{ 
            'department_id': department_id,
            'site_name': site_name//$('.btn_caret_sign').text()
        },

        success: function( data ) {
		
            var tableDataString = '';
			
            for(var i=0; i<data.length; i++){
				
                tableDataString += '<tr class="site_categorie">';
                tableDataString += '<td><a href="'+data[i].url+'" target="_blank">'+data[i].text+'</a><input type="hidden" class="categoryID" value="'+data[i].id+'" ></td>';
                tableDataString += '<td>'+data[i].nr_products+'</td>';
				
                if(data[i].title_keyword_description_density && data[i].description_title) {
                    var density = ' - 0.0%';
                    var densityObj = $.parseJSON(data[i].title_keyword_description_density);
                    var descriptionTitle = data[i].description_title;
					
                    /*for(index in densityObj){
                        if(descriptionTitle.replace('"','').replace('"','').toLowerCase().trim() == index.trim().toLowerCase())
                            density = ' - '+densityObj[index]+'%';
                    }*/
				
                    tableDataString += '<td><select class="changeDensity" style="width:95px;" >';
                    //tableDataString += '<option value="" >'+descriptionTitle.trim().replace('"','').replace('"','')+'</option>';

                    for(index in densityObj){
                        tableDataString += '<option value="'+densityObj[index]+'" >'+index+'</option>';
                        if(density == ' - 0.0%'){
                            density = ' - '+densityObj[index]+'%';
                        }
                    }
                    tableDataString += '</select><span style="position:absolute; margin-top:5px;">&nbsp;'+density+'</span><br>';
                } else {
                    tableDataString += '<td>';
                }
                var user_seo_keywords = data[i].user_seo_keywords.trim();
                var user_keyword_description_density = ' - '+data[i].user_keyword_description_density.trim()+'%';
                if(user_seo_keywords == '')
                    user_keyword_description_density = ' -  N/A';
                tableDataString += '<input type="text" style="width: 95px;float: left;margin-right: 5px;" placeholder="Your keyword" onblur="keywordAjax(this);" onkeypress="keywordAjaxCode(this);" name="keyword" value="'+user_seo_keywords+'" />';
                tableDataString += '<span style="float: left;margin-top: 5px" >'+user_keyword_description_density+'</span></td>';
                tableDataString += '<td>'+data[i].description_words+'</td>';
                tableDataString += '</tr>';
                
                /*if( data[i].description_text != '' )
					tableDataString += '<tr count="0" class="category_description_text"><td style="text-align: justify;" colspan="4">'+data[i].description_text+'</td></tr>';
				else
					tableDataString += '<tr count="0" class="category_description_text"><td style="text-align: justify;" colspan="4">None</td></tr>';*/
            }
			
            var categoryCount = data.length;
            var stringNewData = '<table id="'+table_name+'" ><thead><tr><th style="width: 115px !important;word-wrap: break-word;" nowrap>Categories ('+categoryCount+')</th>' +
                '<th style="width:60px!important;" nowrap>Items</th><th style="width:160px!important" nowrap>Keyword Density</th>' +
                '<th style="width:60px!important;" nowrap>Words</th></tr></thead><tbody>'+tableDataString+'</tbody></table>';
            if(table_name == 'records')
                $( '#dataTableDiv1' ).html(stringNewData);
            else
                $( '#dataTableDiv2' ).html(stringNewData);
            $( '#'+table_name ).dataTable({
                "bJQueryUI": true
            });
            $('.changeDensity').trigger('change');
            $( '#ajaxLoadAni' ).fadeOut( 'slow' );
        }
    });
}

$('.site_categorie').live('click',function(e){
	e.stopPropagation();
	
	$('.category_description_text').each(function(){
		$(this).hide();
	});
	
	if( $(this).next().is(":visible") ){
		$(this).next().fadeOut();
		$(this).attr('count', '0');
	}else
		$(this).next().fadeIn();
});

$('.category_description_text').live('click',function(){
	var count = $(this).attr('count');
	if( count == '0' ){
		$(this).attr('count','1');
	}else{
		$(this).attr('count','0');
		$(this).fadeOut();
	}
});

function keywordAjax(obj) {
    var categoryID = $(obj).parent().parent().find('.categoryID').val();
    $.ajax({
	
        url: base_url + 'index.php/measure/getKeywordByDescriptionText',
        type: 'post',
        data: {
            'keyword': $(obj).val(),
            'categoryID': categoryID
        },
        success: function(data) {
            $(obj).next().text(' - '+   data);
        }

    });
    
}

function keywordAjaxCode(obj) {
    var num = window.event ? event.keyCode : obj.which;
    if(num == 13){
        var categoryID = $(obj).parent().parent().find('.categoryID').val();
        $.ajax({

            url: base_url + 'index.php/measure/getKeywordByDescriptionText',
            type: 'post',
            data: {
                'keyword': $(obj).val(),
                'categoryID': categoryID
            },
            success: function(data) {
                $(obj).next().text(' - '+   data);
            }

        });
    }
}

function keywordAjaxDepartment(obj){
  
  var departmentID = $('.departmentID').val();
    $.ajax({
	
        url: base_url + 'index.php/measure/getKeywordDepartmentByDescriptionText',
        type: 'post',
        data: {
            'keyword': $(obj).val(),
            'departmentID': departmentID
        },
        success: function(data) {
            $(obj).next().text(' - '+data);
            
        }

    });
    
}

function departmentAjax(department_id,site_name){
 
    $.ajax({
        url: base_url + 'index.php/measure/getDataByDepartment',
        dataType: 'json',
        type: "POST",
        data:{ 
            'department_id': department_id,
            'site_name': site_name//$('.btn_caret_sign').text()
        },
        success:function(data){
            var dataString = '';
			
            for(var i=0; i<data.length; i++){
				
                // tableDataString += '<td>'+data[i].text+'<input type="hidden" class="categoryID" value="'+data[i].id+'" ></td>';
                
                dataString = '<div><span style="font-weight: bold;float:left;width: 124px;">Keyword Density:</span></div>';
                if(data[i].title_keyword_description_density && data[i].description_title) {
                    var density = ' - 0.0%';
                    var densityObj = $.parseJSON(data[i].title_keyword_description_density);
                    var descriptionTitle = data[i].description_title;
					
                    for(index in densityObj){
                        if(descriptionTitle.replace('"','').replace('"','').toLowerCase().trim() == index.trim().toLowerCase())
                            density = ' - '+densityObj[index]+'%';
                    }
		    dataString += '<input type="hidden" class="departmentID" value="'+data[i].id+'" >';		
                    dataString += '<select class="changeDensity" style="width:239px;margin-left: 2px;" >';
                    dataString += '<option value="" >'+descriptionTitle.trim().replace('"','').replace('"','')+'</option>';
                    for(index in densityObj){
                        dataString += '<option value="'+densityObj[index]+'" >'+index+'</option>';
                    }
                    dataString += '</select><span>&nbsp;'+density+'</span>';
                } 
                var user_seo_keywords = data[i].user_seo_keywords.trim();
                var user_keyword_description_density = ' - '+data[i].user_keyword_description_density.trim()+'%';
                if(user_seo_keywords == '')
                    user_keyword_description_density = ' N/A';
                dataString += '<div style="';
                if(data[i].title_keyword_description_density && data[i].description_title) {
                    dataString += 'margin-right:20px;';
                }
                dataString += 'float: right;"><input type="text" style="width: 237px;float: left;" placeholder="Your keyword" onblur="keywordAjaxDepartment(this);" name="keyword" value="'+user_seo_keywords+'" />';
                dataString += '<span style="float: left;margin-top: 4px;margin-left:4px;" > - '+user_keyword_description_density+'</span></div>';
                
            }
            $('#departments_content').html(dataString);
           
        }  
    });      
}

function showSnap(data) {
    $("#preview_crawl_snap_modal").modal('show');
    $("#preview_crawl_snap_modal .snap_holder").html(data);
}

function departmentScreenDetectorMouseOver(snap_data) {
    if(snap_data.img_av_status) {
        showSnap("<img src='" + snap_data['snap_path'] + "'>");
    } else {
        showSnap("<p>Snapshot image not exists on server</p>");
    }
}

function standaloneDepartmentScreenDetector() {
    var dep_id = $("input[name='selected_department_id']").val();
    $.post(base_url + 'index.php/system/scanForDepartmentSnap', {'dep_id': dep_id}, function(data) {
        if(data.dep_id !== "") {
            $("#dep_monitor").fadeOut('medium', function() {
                $("#dep_monitor").fadeIn('medium');
            });
            $("#dep_monitor").on('mouseover', function() { departmentScreenDetectorMouseOver(data); } );
        } else {
            $("#dep_monitor").hide();
        }
    });
}
standaloneDepartmentScreenDetector();
