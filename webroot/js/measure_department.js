var readUrl   = base_url + 'index.php/measure/get_best_sellers',
updateUrl = base_url + 'index.php/measure/',
delUrl    = base_url + 'index.php/measure/',
delHref,
updateHref,
updateId,
delId;
var oTable;

/* Formating function for row details */
function fnFormatDetails ( nTr )
{
    var aData = oTable.fnGetData( nTr );
    var sOut = '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">';
    sOut += '<tr><td>Rendering engine:</td><td>'+aData[2]+' '+aData[5]+'</td></tr>';
    sOut += '<tr><td>Link to source:</td><td>Could provide a link here</td></tr>';
    sOut += '<tr><td>Extra info:</td><td>And any further details here (images etc)</td></tr>';
    sOut += '</table>';

    return sOut;
}


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
        if(new_caret != 'Choose Site'){
            var checking = false;
            $(".hp_boot_drop .dropdown-menu > li > a").each(function(){
                if($(this).text() == 'Choose Site'){
                    checking = true;
                }
            });
            if(checking == false){
                $(".hp_boot_drop .dropdown-menu").prepend("<li><a data-item=\"\" data-value=\"\" href=\"javascript:void(0);\">Choose Site</a></li>");
            }
            $(".hp_boot_drop .dropdown-menu > li > a").bind('click', function(e) {
                var new_caret = $.trim($(this).text());
                if(new_caret == 'Choose Site'){
                    $(".dashboard").hide();
                    $('#tabs').hide();
                    $('#department_url').hide();
                    $('#departmentDropdown .btn_caret_sign1').text('Choose Department');
                    $("#hp_boot_drop .btn_caret_sign").text(new_caret);
                    $('#departments_content').html('');
                }
            });
        }else{
            $(".dashboard").hide();
            $('#departmentDropdown .btn_caret_sign1').text('Choose Department');
            $('#departments_content').html('');
        }

        $("tbody#department_data").empty();
        $("tbody#category_data").empty();
        //$("#departmentDropdown").show();
        $.post(base_url + 'index.php/measure/getDepartmentsByCustomer', {
            'customer_name': new_caret
        }, function(data) {
            $("#departmentDropdown .dropdown-menu").empty();
            if(data.length > 0){
				$("#departmentDropdown").show();
                $("#departmentDropdown .dropdown-menu").append("<li><a data-item=\"empty\" data-value=\"\" href=\"javascript:void(0);\">Choose department</a></li><li><a data-item=\"\" data-value=\"All\" href=\"javascript:void(0);\">All</a></li>");
                for(var i=0; i<data.length; i++){
                    if(i == 0){
                        $('#departmentDropdown .btn_caret_sign1').text('Choose Department');
                    }
                    $("#departmentDropdown .dropdown-menu").append("<li><a data-item="+data[i].id+" data-value="+data[i].text+" href=\"javascript:void(0);\">"+data[i].text+"</a></li>");
                }
                $(".dashboard").show();
                $("tbody#department_data").show();
                $("tbody#category_data").empty();
                $("tbody#department_data").empty();
                if($("#hp_boot_drop_sec .btn_caret_sign_sec").text() != 'Choose comparison site'){
                    var site_name_sec = $("#hp_boot_drop_sec .btn_caret_sign_sec").text();
                    $("#dashboard_recommend").hide();

                    var selected_type = $('#hp_boot_drop_sec_dashboard .btn_caret_sign_sec').text();
                    if(selected_type == "Departments"){
                        $("tbody#department_data").show();
                        $("tbody#category_data").hide();
                        allDepDashboard(new_caret, site_name_sec);
                    } else {
                        $("tbody#department_data").hide();
                        $("tbody#category_data").show();
                        allCatDashboard(new_caret, site_name_sec);
                    }
                } else {
                    $("#hp_boot_drop_sec_dashboard .btn_caret_sign_sec").text('Departments');
                    globalDepDashboard(new_caret);
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
        $(".dashboard").hide();
        var site_name=$('.btn_caret_sign').text();
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
            standaloneDepartmentScreenDetector();
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
            standaloneDepartmentScreenDetector();
        }

    });
		
		
    //Compare with Begin
		
		
    $(".hp_boot_drop_sec .dropdown-menu > li > a").bind('click', function(e) {
        var new_caret = $.trim($(this).text());
        $("#hp_boot_drop_sec .btn_caret_sign_sec").text(new_caret);
        var site_name=$('#hp_boot_drop .btn_caret_sign').text();
        var item_id = $(this).data('item');
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
        var selected_type = $('#hp_boot_drop_sec_dashboard .btn_caret_sign_sec').text();
        if($("#hp_boot_drop .btn_caret_sign").text() != 'Choose Site'){
            $(".dashboard").show();
            $("#dashboard_recommend").hide();
            $("tbody#category_data").empty();
            $("tbody#department_data").empty();
            if(selected_type == "Departments"){
                $("tbody#department_data").show();
                $("tbody#category_data").hide();
                allDepDashboard(site_name, new_caret);
            } else {
                $("tbody#department_data").hide();
                $("tbody#category_data").show();
                allCatDashboard(site_name, new_caret);
            }
        }

        if(new_caret != 'Choose comparison site'){
            var checking = false;
            $(".hp_boot_drop_sec .dropdown-menu > li > a").each(function(){
                if($(this).text() == 'Choose comparison site'){
                    checking = true;
                }
            });
            if(checking == false){
                $(".hp_boot_drop_sec .dropdown-menu").prepend("<li><a data-item=\"\" data-value=\"\" href=\"javascript:void(0);\">Choose comparison site</a></li>");
            }
            $(".hp_boot_drop_sec .dropdown-menu > li > a").bind('click', function(e) {
                var new_caret = $.trim($(this).text());
                if(new_caret == 'Choose comparison site'){
                    $("#departmentDropdownSec_first").text('Choose Department');
                    $("#hp_boot_drop_sec .btn_caret_sign_sec").text(new_caret);
                    $('#departments_content').html('');
                    $("tbody#category_data").empty();
                    $("tbody#department_data").empty();
                    if(selected_type == "Departments"){
                        $('#dashboard_recommend').show();
                        globalDepDashboard(site_name);
                    } else {
                        $('#dashboard_recommend').show();
                        globalCatDashboard(site_name);
                    }
                }
            });
        }else{
            $("#departmentDropdownSec_first").text('Choose Department');
            $('#departments_content').html('');
        }
    });

    $("#departmentDropdownSec .dropdown-menu > li > a").live('click', function(e) {
        var departmentValue = $.trim($(this).text());
        var department_id = $(this).data('item');
        var site_name=$('#hp_boot_drop_sec .btn_caret_sign_sec').text();
        $("#departmentDropdownSec_first").text(departmentValue);
        readBestSellers(department_id,site_name,'recordSec');
        $(".dashboard").hide();
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
        $("#hp_boot_drop_sec_dashboard .btn_caret_sign_sec").text(new_caret);
        var item_id = $(this).data('item');
        var site_name = $('#hp_boot_drop .btn_caret_sign').text();
        var site_name_sec = $('#hp_boot_drop_sec .btn_caret_sign_sec').text();
        $('#departments_content').html('');
        $("tbody#category_data").empty();
        $("tbody#department_data").empty();
        if(new_caret == "Departments"){
            $("tbody#department_data").show();
            $("tbody#category_data").hide();
            if(site_name_sec != 'Choose comparison site'){
                allDepDashboard(site_name, site_name_sec);
            } else {
                $('#dashboard_recommend').show();
                globalDepDashboard(site_name);
            }
        } else {
            $("tbody#department_data").hide();
            $("tbody#category_data").show();
            if(site_name_sec != 'Choose comparison site'){
                allCatDashboard(site_name, site_name_sec);
            } else {
                $('#dashboard_recommend').show();
                globalCatDashboard(site_name);
            }
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

function globalDepDashboard(site_name){
    $.post(base_url + 'index.php/measure/getDashboardDepData', {
        'site_name': site_name
    }, function(data) {
        var dep_content = data.total - data.res_more_than_0;
        var dep_optimize = data.res_more_than_0 - data.keyword_optimize;

        var data_str = '<tr><td nowrap><span class="dep_left_part">Departments Analyzed:</span> <span class="dep_total_numbers">'+data.total+'</span></td><td>&nbsp;</td></tr>';
        data_str += '<tr><td nowrap class="dep_first_part span6"><span class="dep_title"><span class="dep_left_part">Departments that have content:  </span>' +
            '<span class="dep_total_numbers">'+data.res_more_than_0+'/'+data.total+'</span></span>';
        if(data.res_data_more_than_0.length > 0){
            data_str += '<ul>';
            data_str += '<li class="dep_header"><span class="dep_text">CATEGORY</span><span class="dep_numbers">WORDS</span><span class="dep_keywords">KEYWORDS - DENSITY</span></li>';
            for(var j=0; j<data.res_data_more_than_0.length; j++){
                var json = data.res_data_more_than_0[j].title_keyword_description_density;
                if(json != ''){
                    var keywords = $.parseJSON(json.replace(/&quot;/ig, '"'));
                }
                data_str += '<li><span class="dep_text"><a href="'+data.res_data_more_than_0[j].url+'" target="_blank">'+data.res_data_more_than_0[j].text+'</a></span><span class="dep_numbers">' +
                    data.res_data_more_than_0[j].description_words+'</span><span class="dep_keywords">';
                if(json != ''){
                    jQuery.each(keywords, function(i, val) {
                        data_str += i+' - '+val+'%<br />';
                    });
                } else {
                    data_str += ' - ';
                }
                data_str += '</span></li>';
            }
            data_str += '</ul>';
        }
        data_str += '</td>';
        data_str += '<td class="dep_second_part span6"><span class="dep_title">Create content for '+dep_content+' departments</span>';
        if(data.result0.length > 0){
            data_str += '<ul>';
            for(var j=0; j<data.result0.length; j++){
                data_str += '<li>';
                var json = data.result0[j].title_keyword_description_density;
                if(json != ''){
                    var keywords = $.parseJSON(json.replace(/&quot;/ig, '"'));
                }
                data_str += '<span class="dep_text"><a href="'+data.result0[j].url+'" target="_blank">'+data.result0[j].text+'</a></span><span class="dep_numbers">'
                    +data.result0[j].description_words+'</span><span class="dep_keywords">';
                if(json != ''){
                    jQuery.each(keywords, function(i, val) {
                        data_str += i+' - '+val+'%<br />';
                    });
                } else {
                    data_str += ' - ';
                }
                data_str += '</span></li>';
            }
            data_str += '</ul>';
        }
        data_str += '</td></tr>';

        data_str += '<tr><td nowrap class="span6 dep_first_part"><span class="dep_title"><span class="dep_left_part">Average content word count: </span>' +
            '<span class="dep_total_numbers">'+data.res_avg+'</span></span>';
        if(data.res_more_data.length > 0){
            data_str += '<ul>';
            data_str += '<li class="dep_header"><span class="dep_text">CATEGORY</span><span class="dep_numbers">WORDS</span><span class="dep_keywords">KEYWORDS - DENSITY</span></li>';
            for(var j=0; j<data.res_more_data.length; j++){
                var json = data.res_more_data[j].title_keyword_description_density;
                if(json != ''){
                    var keywords = $.parseJSON(json.replace(/&quot;/ig, '"'));
                }
                data_str += '<li><span class="dep_text"><a href="'+data.res_more_data[j].url+'" target="_blank">'+data.res_more_data[j].text+'</a></span><span class="dep_numbers">'
                    +data.res_more_data[j].description_words+'</span><span class="dep_keywords">';
                if(json != ''){
                    jQuery.each(keywords, function(i, val) {
                        data_str += i+' - '+val+'%<br />';
                    });
                } else {
                    data_str += ' - ';
                }
                data_str += '</span></li>';
            }
            data_str += '</ul>';
        }
        data_str += '</td>';
        data_str += '<td class="span6 dep_second_part"><span class="dep_title">Add more words to '+data.res_more+' departments</span>';
        if(data.res_more_data.length > 0){
            data_str += '<ul>';
            for(var j=0; j<data.res_more_data.length; j++){
                var json = data.res_more_data[j].title_keyword_description_density;
                if(json != ''){
                    var keywords = $.parseJSON(json.replace(/&quot;/ig, '"'));
                }
                data_str += '<li><span class="dep_text"><a href="'+data.res_more_data[j].url+'" target="_blank">'+data.res_more_data[j].text+'</a></span><span class="dep_numbers">'
                    +data.res_more_data[j].description_words+'</span><span class="dep_keywords">';
                if(json != ''){
                    jQuery.each(keywords, function(i, val) {
                        data_str += i+' - '+val+'%<br />';
                    });
                } else {
                    data_str += ' - ';
                }
                data_str += '</span></li>';
            }
            data_str += '</ul>';
        }
        data_str += '</td></tr>';


        data_str += '<tr><td><span class="dep_title"><span class="dep_left_part">Departments optimized: </span>' +
            '<span class="dep_total_numbers">'+data.keyword_optimize+'/'+data.res_more_than_0+'</span></span>';
        if(data.keyword_optimize_data.length > 0){
            data_str += '<ul>';
            data_str += '<li class="dep_header"><span class="dep_text">CATEGORY</span><span class="dep_numbers">WORDS</span><span class="dep_keywords">KEYWORDS - DENSITY</span></li>';
            for(var j=0; j<data.keyword_optimize_data.length; j++){
                var json = data.keyword_optimize_data[j].title_keyword_description_density;
                if(json != ''){
                    var keywords = $.parseJSON(json.replace(/&quot;/ig, '"'));
                }
                data_str += '<li><span class="dep_text"><a href="'+data.keyword_optimize_data[j].url+'" target="_blank">'+data.keyword_optimize_data[j].text+'</a></span><span class="dep_numbers">'
                    +data.keyword_optimize_data[j].description_words+'</span><span class="dep_keywords">';
                if(json != ''){
                    jQuery.each(keywords, function(i, val) {
                        data_str += i+' - '+val+'%<br />';
                    });
                } else {
                    data_str += ' - ';
                }
                data_str += '</span></li>';
            }
            data_str += '</ul>';
        }
        data_str += '</td>';
        data_str += '<td><span class="dep_title">Optimize '+dep_optimize+' departments</span>';
        if(data.dep_optimize.length > 0){
            data_str += '<ul>';
            for(var j=0; j<data.dep_optimize.length; j++){
                var json = data.dep_optimize[j].title_keyword_description_density;
                if(json != ''){
                    var keywords = $.parseJSON(json.replace(/&quot;/ig, '"'));
                }
                data_str += '<li><span class="dep_text"><a href="'+data.dep_optimize[j].url+'" target="_blank">'+data.dep_optimize[j].text
                    +'</a></span><span class="dep_numbers">'
                    +data.dep_optimize[j].description_words+'</span><span class="dep_keywords">';
                if(json != ''){
                    jQuery.each(keywords, function(i, val) {
                        data_str += i+' - '+val+'%<br />';
                    });
                } else {
                    data_str += ' - ';
                }
                data_str += '</span></li>';
            }
            data_str += '<ul>';
        }
        data_str += '</td></tr>';

        $("tbody#department_data").append(data_str);
        $("tbody#department_data tr td span.dep_title").click(function() {
            var el = $(this).parent().find('ul');
            if(el.css('display') == 'none'){
                $(this).css({'border-bottom':'1px solid #000'});
                el.css({'display':'block'});
            } else {
                el.css({'display':'none'});
            }
        });
        $("tbody#department_data tr td span.dep_title").mouseover(function() {
            $("tbody#department_data tr td span.dep_title").each(function(){
                $(this).css({'border-bottom':'none'});
            })
            $(this).css({'border-bottom':'1px solid #000'});
        });
    });
}

function globalCatDashboard(site_name){
    $.post(base_url + 'index.php/measure/getDashboardCatData', {
        'site_name': site_name
    }, function(data) {
        var dep_content = data.total - data.res_more_than_0;
        var dep_optimize = data.res_more_than_0 - data.keyword_optimize;
        var data_str = '<tr><td nowrap><span class="dep_title"><span class="dep_left_part">Categories Analyzed: </span><span class="dep_total_numbers">'+data.total+'</span></span></td><td>&nbsp;</td></tr>';
        data_str += '<tr><td nowrap class="dep_first_part span6" onclick="getCatData(\''+site_name+'\', this, \'`description_words` > 0\', 1);">' +
            '<span class="dep_title"><span class="dep_left_part">Categories that have content:  </span>' +
            '<span class="dep_total_numbers">'+data.res_more_than_0+'/'+data.total+'</span></span>';
        data_str += '<ul></ul></td>';
        data_str += '<td class="dep_second_part span6" onclick="getCatData(\''+site_name+'\', this, \'`description_words` = 0\', 0);"><span class="dep_title">Create content for '+dep_content+' categories</span>';
        data_str += '<ul></ul></td></tr>';

        data_str += '<tr><td nowrap class="span6 dep_first_part" onclick="getCatData(\''+site_name+'\', this, \'(`description_words`>0 and `description_words`<250)\', 1);"><span class="dep_title"><span class="dep_left_part">Average content word count: </span>' +
            '<span class="dep_total_numbers">'+data.res_avg+'</span></span>';
        data_str += '<ul></ul></td>';
        data_str += '<td class="span6 dep_second_part" onclick="getCatData(\''+site_name+'\', this, \'(`description_words`>0 and `description_words`<250)\', 0);"><span class="dep_title">Add more words to '+data.res_more+' categories</span>';
        data_str += '<ul></ul></td></tr>';

        data_str += '<tr><td><span class="dep_title">Categories optimized: <span class="dep_total_numbers">'+data.keyword_optimize+'/'+data.res_more_than_0+'</span></span>';
        if(data.keyword_optimize_data.length > 0){
            data_str += '<ul>';
            data_str += '<li class="cat_header"><span class="dep_text">CATEGORY</span><span class="dep_numbers">WORDS</span><span class="dep_keywords">KEYWORDS - DENSITY</span></li>';
            for(var j=0; j<data.keyword_optimize_data.length; j++){
                var json = data.keyword_optimize_data[j].title_keyword_description_density;
                if(json != ''){
                    var keywords = $.parseJSON(json.replace(/&quot;/ig, '"'));
                }
                data_str += '<li><span class="dep_text"><a href="'+data.keyword_optimize_data[j].url+'" target="_blank">'+data.keyword_optimize_data[j].text+'</a></span><span class="dep_numbers">'
                    +data.keyword_optimize_data[j].description_words+'</span><span class="dep_keywords">';
                if(json != ''){
                    jQuery.each(keywords, function(i, val) {
                        data_str += i+' - '+val+'%<br />';
                    });
                } else {
                    data_str += ' - ';
                }
                data_str += '</span></li>';
            }
            data_str += '</ul>';
        }
        data_str += '</td>';
        data_str += '<td><span class="dep_title">Optimize '+dep_optimize+' categories</span>';
        if(data.dep_optimize.length > 0){
            data_str += '<ul>';
            for(var j=0; j<data.dep_optimize.length; j++){
                var json = data.dep_optimize[j].title_keyword_description_density;
                if(json != ''){
                    var keywords = $.parseJSON(json.replace(/&quot;/ig, '"'));
                }
                data_str += '<li><span class="dep_text"><a href="'+data.dep_optimize[j].url+'" target="_blank">'+data.dep_optimize[j].text+'</a></span><span class="dep_numbers">'
                    +data.dep_optimize[j].description_words+'</span><span class="dep_keywords">';
                if(json != ''){
                    jQuery.each(keywords, function(i, val) {
                        data_str += i+' - '+val+'%<br />';
                    });
                } else {
                    data_str += ' - ';
                }
                data_str += '</span></li>';
            }
            data_str += '<ul>';
        }
        data_str += '</td></tr>';

        $("tbody#category_data").append(data_str);
        $("tbody#category_data tr td span.dep_title").click(function() {
            var el = $(this).parent().find('ul');
            if(el.css('display') == 'none'){
                $(this).css({'border-bottom':'1px solid #000'});
                el.css({'display':'block'});
            } else {
                el.css({'display':'none'});
                $(this).css({'border-bottom':'none'});
            }
        });
    });
}

function allDepDashboard(site_name, site_name_sec){
    var header_first_table = '';
    var first_part_table = '';
    var second_part_table = '';
    var third_part_table = '';
    $.post(base_url + 'index.php/measure/getDashboardDepData', {
        'site_name': site_name
    }, function(data) {
        var dep_content = data.total - data.res_more_than_0;
        var dep_optimize = data.res_more_than_0 - data.keyword_optimize;
        header_first_table += '<tr><td nowrap><span class="dep_left_part">Departments Analyzed:</span> <span class="dep_total_numbers">'+data.total+'</span></td>';
        first_part_table += '<tr><td nowrap class="dep_first_part span6"><span class="dep_title"><span class="dep_left_part">Departments that have content:  </span>' +
            '<span class="dep_total_numbers">'+data.res_more_than_0+'/'+data.total+'</span></span>';
        if(data.res_data_more_than_0.length > 0){
            first_part_table += '<ul><li class="dep_header"><span class="dep_text">CATEGORY</span><span class="dep_numbers">WORDS</span><span class="dep_keywords">KEYWORDS - DENSITY</span></li>';
            for(var j=0; j<data.res_data_more_than_0.length; j++){
                var json = data.res_data_more_than_0[j].title_keyword_description_density;
                if(json != ''){
                    var keywords = $.parseJSON(json.replace(/&quot;/ig, '"'));
                }
                first_part_table += '<li><span class="dep_text"><a href="'+data.res_data_more_than_0[j].url+'" target="_blank">'+data.res_data_more_than_0[j].text+'</a></span><span class="dep_numbers">' +
                    data.res_data_more_than_0[j].description_words+'</span><span class="dep_keywords">';
                if(json != ''){
                    jQuery.each(keywords, function(i, val) {
                        first_part_table += i+' - '+val+'%<br />';
                    });
                } else {
                    first_part_table += ' - ';
                }
                first_part_table += '</span></li>';
            }
            first_part_table += '</ul>';
        }
        first_part_table += '</td>';

        second_part_table += '<tr><td nowrap class="span6 dep_first_part"><span class="dep_title"><span class="dep_left_part">Average content word count: </span>' +
            '<span class="dep_total_numbers">'+data.res_avg+'</span></span>';
        if(data.res_more_data.length > 0){
            second_part_table += '<ul><li class="dep_header"><span class="dep_text">CATEGORY</span><span class="dep_numbers">WORDS</span><span class="dep_keywords">KEYWORDS - DENSITY</span></li>';
            for(var j=0; j<data.res_more_data.length; j++){
                var json = data.res_more_data[j].title_keyword_description_density;
                if(json != ''){
                    var keywords = $.parseJSON(json.replace(/&quot;/ig, '"'));
                }
                second_part_table += '<li><span class="dep_text"><a href="'+data.res_more_data[j].url+'" target="_blank">'+data.res_more_data[j].text+'</a></span><span class="dep_numbers">'
                    +data.res_more_data[j].description_words+'</span><span class="dep_keywords">';
                if(json != ''){
                    jQuery.each(keywords, function(i, val) {
                        second_part_table += i+' - '+val+'%<br />';
                    });
                } else {
                    second_part_table += ' - ';
                }
                second_part_table += '</span></li>';
            }
            second_part_table += '</ul>';
        }
        second_part_table += '</td>';

        third_part_table += '<tr><td><span class="dep_title"><span class="dep_left_part">Departments optimized: </span>' +
            '<span class="dep_total_numbers">'+data.keyword_optimize+'/'+data.res_more_than_0+'</span></span>';
        if(data.keyword_optimize_data.length > 0){
            third_part_table += '<ul><li class="dep_header"><span class="dep_text">CATEGORY</span><span class="dep_numbers">WORDS</span><span class="dep_keywords">KEYWORDS - DENSITY</span></li>';
            for(var j=0; j<data.keyword_optimize_data.length; j++){
                var json = data.keyword_optimize_data[j].title_keyword_description_density;
                if(json != ''){
                    var keywords = $.parseJSON(json.replace(/&quot;/ig, '"'));
                }
                third_part_table += '<li><span class="dep_text"><a href="'+data.keyword_optimize_data[j].url+'" target="_blank">'+data.keyword_optimize_data[j].text+'</a></span><span class="dep_numbers">'
                    +data.keyword_optimize_data[j].description_words+'</span><span class="dep_keywords">';
                if(json != ''){
                    jQuery.each(keywords, function(i, val) {
                        third_part_table += i+' - '+val+'%<br />';
                    });
                } else {
                    third_part_table += ' - ';
                }
                third_part_table += '</span></li>';
            }
            third_part_table += '</ul>';
        }
        third_part_table += '</td>';
        $.post(base_url + 'index.php/measure/getDashboardDepData', {
            'site_name': site_name_sec
        }, function(data) {
            var dep_content = data.total - data.res_more_than_0;
            var dep_optimize = data.res_more_than_0 - data.keyword_optimize;

            header_first_table += '<td nowrap><span class="dep_left_part">Departments Analyzed:</span> <span class="dep_total_numbers">'+data.total+'</span></td></tr>';
            first_part_table += '<td nowrap class="dep_first_part span6"><span class="dep_title"><span class="dep_left_part">Departments that have content:  </span>' +
                '<span class="dep_total_numbers">'+data.res_more_than_0+'/'+data.total+'</span></span>';
            if(data.res_data_more_than_0.length > 0){
                first_part_table += '<ul><li class="dep_header"><span class="dep_text">CATEGORY</span><span class="dep_numbers">WORDS</span><span class="dep_keywords">KEYWORDS - DENSITY</span></li>';
                for(var j=0; j<data.res_data_more_than_0.length; j++){
                    var json = data.res_data_more_than_0[j].title_keyword_description_density;
                    if(json != ''){
                        var keywords = $.parseJSON(json.replace(/&quot;/ig, '"'));
                    }
                    first_part_table += '<li><span class="dep_text"><a href="'+data.res_data_more_than_0[j].url+'" target="_blank">'+data.res_data_more_than_0[j].text+'</a></span><span class="dep_numbers">' +
                        data.res_data_more_than_0[j].description_words+'</span><span class="dep_keywords">';
                    if(json != ''){
                        jQuery.each(keywords, function(i, val) {
                            first_part_table += i+' - '+val+'%<br />';
                        });
                    } else {
                        first_part_table += ' - ';
                    }
                    first_part_table += '</span></li>';
                }
                first_part_table += '</ul>';
            }
            first_part_table += '</td></tr>';

            second_part_table += '<td nowrap class="span6 dep_first_part"><span class="dep_title"><span class="dep_left_part">Average content word count: </span>' +
                '<span class="dep_total_numbers">'+data.res_avg+'</span></span>';
            if(data.res_more_data.length > 0){
                second_part_table += '<ul><li class="dep_header"><span class="dep_text">CATEGORY</span><span class="dep_numbers">WORDS</span><span class="dep_keywords">KEYWORDS - DENSITY</span></li>';
                for(var j=0; j<data.res_more_data.length; j++){
                    var json = data.res_more_data[j].title_keyword_description_density;
                    if(json != ''){
                        var keywords = $.parseJSON(json.replace(/&quot;/ig, '"'));
                    }
                    second_part_table += '<li><span class="dep_text"><a href="'+data.res_more_data[j].url+'" target="_blank">'+data.res_more_data[j].text+'</a></span><span class="dep_numbers">'
                        +data.res_more_data[j].description_words+'</span><span class="dep_keywords">';
                    if(json != ''){
                        jQuery.each(keywords, function(i, val) {
                            second_part_table += i+' - '+val+'%<br />';
                        });
                    } else {
                        second_part_table += ' - ';
                    }
                    second_part_table += '</span></li>';
                }
                second_part_table += '</ul>';
            }
            second_part_table += '</td></tr>';

            third_part_table += '<td><span class="dep_title"><span class="dep_left_part">Departments optimized: </span>' +
                '<span class="dep_total_numbers">'+data.keyword_optimize+'/'+data.res_more_than_0+'</span></span>';
            if(data.keyword_optimize_data.length > 0){
                third_part_table += '<ul><li class="dep_header"><span class="dep_text">CATEGORY</span><span class="dep_numbers">WORDS</span><span class="dep_keywords">KEYWORDS - DENSITY</span></li>';
                for(var j=0; j<data.keyword_optimize_data.length; j++){
                    var json = data.keyword_optimize_data[j].title_keyword_description_density;
                    if(json != ''){
                        var keywords = $.parseJSON(json.replace(/&quot;/ig, '"'));
                    }
                    third_part_table += '<li><span class="dep_text"><a href="'+data.keyword_optimize_data[j].url+'" target="_blank">'+data.keyword_optimize_data[j].text+'</a></span><span class="dep_numbers">'
                        +data.keyword_optimize_data[j].description_words+'</span><span class="dep_keywords">';
                    if(json != ''){
                        jQuery.each(keywords, function(i, val) {
                            third_part_table += i+' - '+val+'%<br />';
                        });
                    } else {
                        third_part_table += ' - ';
                    }
                    third_part_table += '</span></li>';
                }
                third_part_table += '</ul>';
            }
            third_part_table += '</td></tr>';
            var data_str = header_first_table + first_part_table + second_part_table + third_part_table;
            $("tbody#department_data").append(data_str);
            $("tbody#department_data tr td span.dep_title").click(function() {
                var el = $(this).parent().find('ul');
                if(el.css('display') == 'none'){
                    $(this).css({'border-bottom':'1px solid #000'});
                    el.css({'display':'block'});
                } else {
                    el.css({'display':'none'});
                }
            });
            $("tbody#department_data tr td span.dep_title").mouseover(function() {
                $("tbody#department_data tr td span.dep_title").each(function(){
                    $(this).css({'border-bottom':'none'});
                })
                $(this).css({'border-bottom':'1px solid #000'});
            });
        });
    });
}


function allCatDashboard(site_name, site_name_sec){
    var header_first_table = '';
    var first_part_table = '';
    var second_part_table = '';
    var third_part_table = '';
    $.post(base_url + 'index.php/measure/getDashboardCatData', {
        'site_name': site_name
    }, function(data) {
        var dep_content = data.total - data.res_more_than_0;
        var dep_optimize = data.res_more_than_0 - data.keyword_optimize;
        header_first_table += '<tr><td nowrap><span class="dep_title"><span class="dep_left_part">Categories Analyzed: </span><span class="dep_total_numbers">'+data.total+'</span></span></td>';
        first_part_table += '<tr><td nowrap class="dep_first_part span6" onclick="getCatData(\''+site_name+'\', this, \'`description_words` > 0\', 1);">' +
            '<span class="dep_title"><span class="dep_left_part">Categories that have content:  </span>' +
            '<span class="dep_total_numbers">'+data.res_more_than_0+'/'+data.total+'</span></span>';
        first_part_table += '<ul></ul></td>';

        second_part_table += '<tr><td nowrap class="span6 dep_first_part" onclick="getCatData(\''+site_name+'\', this, \'(`description_words`>0 and `description_words`<250)\', 1);"><span class="dep_title"><span class="dep_left_part">Average content word count: </span>' +
            '<span class="dep_total_numbers">'+data.res_avg+'</span></span>';
        second_part_table += '<ul></ul></td>';

        third_part_table += '<tr><td><span class="dep_title">Categories optimized: <span class="dep_total_numbers">'+data.keyword_optimize+'/'+data.res_more_than_0+'</span></span>';
        if(data.keyword_optimize_data.length > 0){
            third_part_table += '<ul><li class="cat_header"><span class="dep_text">CATEGORY</span><span class="dep_numbers">WORDS</span><span class="dep_keywords">KEYWORDS - DENSITY</span></li>';
            for(var j=0; j<data.keyword_optimize_data.length; j++){
                var json = data.keyword_optimize_data[j].title_keyword_description_density;
                if(json != ''){
                    var keywords = $.parseJSON(json.replace(/&quot;/ig, '"'));
                }
                third_part_table += '<li><span class="dep_text"><a href="'+data.keyword_optimize_data[j].url+'" target="_blank">'+data.keyword_optimize_data[j].text+'</a></span><span class="dep_numbers">'
                    +data.keyword_optimize_data[j].description_words+'</span><span class="dep_keywords">';
                if(json != ''){
                    jQuery.each(keywords, function(i, val) {
                        third_part_table += i+' - '+val+'%<br />';
                    });
                } else {
                    third_part_table += ' - ';
                }
                third_part_table += '</span></li>';
            }
            third_part_table += '</ul>';
        }
        third_part_table += '</td>';

        $.post(base_url + 'index.php/measure/getDashboardCatData', {
            'site_name': site_name_sec
        }, function(data) {
            var dep_content = data.total - data.res_more_than_0;
            var dep_optimize = data.res_more_than_0 - data.keyword_optimize;
            header_first_table += '<td nowrap><span class="dep_title"><span class="dep_left_part">Categories Analyzed: </span><span class="dep_total_numbers">'+data.total+'</span></span></td></tr>';
            first_part_table += '<td nowrap class="dep_first_part span6" onclick="getCatData(\''+site_name_sec+'\', this, \'`description_words` > 0\', 1);">' +
                '<span class="dep_title"><span class="dep_left_part">Categories that have content:  </span>' +
                '<span class="dep_total_numbers">'+data.res_more_than_0+'/'+data.total+'</span></span>';
            first_part_table += '<ul></ul></td></tr>';

            second_part_table += '<td nowrap class="span6 dep_first_part" onclick="getCatData(\''+site_name_sec+'\', this, \'(`description_words`>0 and `description_words`<250)\', 1);"><span class="dep_title"><span class="dep_left_part">Average content word count: </span>' +
                '<span class="dep_total_numbers">'+data.res_avg+'</span></span>';
            second_part_table += '<ul></ul></td></tr>';

            third_part_table += '<td><span class="dep_title">Categories optimized: <span class="dep_total_numbers">'+data.keyword_optimize+'/'+data.res_more_than_0+'</span></span>';
            if(data.keyword_optimize_data.length > 0){
                third_part_table += '<ul><li class="cat_header"><span class="dep_text">CATEGORY</span><span class="dep_numbers">WORDS</span><span class="dep_keywords">KEYWORDS - DENSITY</span></li>';
                for(var j=0; j<data.keyword_optimize_data.length; j++){
                    var json = data.keyword_optimize_data[j].title_keyword_description_density;
                    if(json != ''){
                        var keywords = $.parseJSON(json.replace(/&quot;/ig, '"'));
                    }
                    third_part_table += '<li><span class="dep_text"><a href="'+data.keyword_optimize_data[j].url+'" target="_blank">'+data.keyword_optimize_data[j].text+'</a></span><span class="dep_numbers">'
                        +data.keyword_optimize_data[j].description_words+'</span><span class="dep_keywords">';
                    if(json != ''){
                        jQuery.each(keywords, function(i, val) {
                            third_part_table += i+' - '+val+'%<br />';
                        });
                    } else {
                        third_part_table += ' - ';
                    }
                    third_part_table += '</span></li>';
                }
                third_part_table += '</ul>';
            }
            third_part_table += '</td></tr>';
            var data_str = header_first_table + first_part_table + second_part_table + third_part_table;
            $("tbody#category_data").append(data_str);
            $("tbody#category_data tr td span.dep_title").click(function() {
                var el = $(this).parent().find('ul');
                if(el.css('display') == 'none'){
                    $(this).css({'border-bottom':'1px solid #000'});
                    el.css({'display':'block'});
                } else {
                    el.css({'display':'none'});
                    $(this).css({'border-bottom':'none'});
                }
            });
        });
    });
}


function getCatData(site_name, obj, condition, state){
    $.post(base_url + 'index.php/measure/getDashboardCatDetails', {
        'site_name': site_name,
        'condition':condition
    }, function(data) {
        if(data.length > 0){
            if(state == 1){
                var data_str = '<li class="cat_header"><span class="dep_text">CATEGORY</span><span class="dep_numbers">WORDS</span><span class="dep_keywords">KEYWORDS - DENSITY</span></li>';
            } else {
                var data_str = '';
            }
            for(var j=0; j<data.length; j++){
                var json = data[j].title_keyword_description_density;
                if(json != ''){
                    var keywords = $.parseJSON(json.replace(/&quot;/ig, '"'));
                }
                data_str += '<li><span class="dep_text">';
                if(state == 1){
                    data_str += '<a href="'+data[j].url+'" target="_blank">';
                }
                data_str += data[j].text;
                if(state == 1){
                    data_str += '</a>';
                }
                data_str += '</span><span class="dep_numbers">' +
                    data[j].description_words+'</span><span class="dep_keywords">';
                if(json != ''){
                    jQuery.each(keywords, function(i, val) {
                        data_str += i+' - '+val+'%<br />';
                    });
                } else {
                    data_str += ' - ';
                }
                data_str += '</span></li>';
            }
            var el = $(obj).find('ul');
            el.html(data_str);
        }

    });
}


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
                tableDataString += '<td>';
                if( data[i].description_text != '' && data[i].description_words > 0){
                    tableDataString += '<div class="cat_desc" style="display:none">'+data[i].description_text+'</div>';
                }
                tableDataString += data[i].description_words+'</td>';
                tableDataString += '</tr>';
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

$('.site_categorie').live('click',function(){
	//e.stopPropagation();
    var txt = $(this).find('div.cat_desc').text();
    if(txt != ''){
        $("#mypopup").dialog().empty().append(txt);
    }
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