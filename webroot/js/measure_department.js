var readUrl   = base_url + 'index.php/measure/get_best_sellers',
    updateUrl = base_url + 'index.php/measure/',
    delUrl    = base_url + 'index.php/measure/',
    delHref,
    updateHref,
    updateId,
    delId;


$( function() {

    // readBestSellers();
	dataTable = $( '#records' ).dataTable({"bJQueryUI": true});
	dataTableSec = $( '#recordSec' ).dataTable({"bJQueryUI": true});
	
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
			
            $("#hp_boot_drop .btn_caret_sign").text(new_caret);
			  $.post(base_url + 'index.php/measure/getDepartmentsByCustomer', {'customer_name': new_caret}, function(data) {
                $("#departmentDropdown .dropdown-menu").empty();
                if(data.length > 0){
                    $("#departmentDropdown .dropdown-menu").append("<li><a data-item=\"\" data-value=\"All\" href=\"javascript:void(0);\">All</a></li>");
                    for(var i=0; i<data.length; i++){
                        if(i == 0){
							$('#departmentDropdown .btn_caret_sign1').text('Choose Department');
                        }
						$("#departmentDropdown .dropdown-menu").append("<li><a data-item="+data[i].id+" data-value="+data[i].text+" href=\"javascript:void(0);\">"+data[i].text+"</a></li>");
                    }
                } else {
					$('#departmentDropdown .btn_caret_sign1').text('empty');
				}
				var stringNewData = '<table id="records" ><thead><tr><th style="width: 50px !important;word-wrap: break-word;" >Category()</th><th>Items</th><th>Category Description SEO</th><th>Words</th></tr></thead><tbody></tbody></table>';
				$( '#dataTableDiv1' ).html(stringNewData);
				$( '#records' ).dataTable({"bJQueryUI": true});
            });

		});

		$("#departmentDropdown .dropdown-menu > li > a").live('click', function(e) {
			var departmentValue = $.trim($(this).text());
			var department_id = $(this).data('item');
			var site_name=$('.btn_caret_sign').text()
            $("#departmentDropdown .btn_caret_sign1").text(departmentValue);
			readBestSellers(department_id,site_name,'records');
        });
		
		
		//Compare with Begin
		
		
		 $(".hp_boot_drop_sec .dropdown-menu > li > a").bind('click', function(e) {
		 
			var new_caret = $.trim($(this).text());
			var item_id = $(this).data('item');
            $("#hp_boot_drop_sec .btn_caret_sign_sec").text(new_caret);
			  $.post(base_url + 'index.php/measure/getDepartmentsByCustomer', {'customer_name': new_caret}, function(data) {
                $("#departmentDropdownSec .dropdown-menu").empty();
                if(data.length > 0){
                    $("#departmentDropdownSec .dropdown-menu").append("<li><a data-item=\"\" data-value=\"All\" href=\"javascript:void(0);\">All</a></li>");
                    for(var i=0; i<data.length; i++){
                        if(i == 0){
							$('#departmentDropdownSec .btn_caret_sign_sec1').text('Choose Department');
                        }
						$("#departmentDropdownSec .dropdown-menu").append("<li><a data-item="+data[i].id+" data-value="+data[i].text+" href=\"javascript:void(0);\">"+data[i].text+"</a></li>");
                    }
                } else {
					$('#departmentDropdownSec .btn_caret_sign_sec1').text('empty');
				}
				var stringNewData = '<table id="recordSec" ><thead><tr><th style="width: 50px !important;word-wrap: break-word;" >Category()</th><th>Items</th><th>Category Description SEO</th><th>Words</th></tr></thead><tbody></tbody></table>';
				$( '#dataTableDiv2' ).html(stringNewData);
				$( '#recordSec' ).dataTable({"bJQueryUI": true});
            });

		});
		
		$("#departmentDropdownSec .dropdown-menu > li > a").live('click', function(e) {
			var departmentValue = $.trim($(this).text());
			var department_id = $(this).data('item');
			var site_name=$('.btn_caret_sign_sec').text()
            $("#departmentDropdownSec .btn_caret_sign1").text(departmentValue);
			readBestSellers(department_id,site_name,'recordSec');
        });
		//Compare with End
		
        // $(document).on('click', 'table#records tbody tr', function(e){
            // e.preventDefault();
            // window.open($(this).find('td:nth-child(3)').text());
        // });

		$('.changeDensity').live('change',function(){
			var descriptionTitle = $(this).children('option:selected').text();
			var currentVal = $(this).val().trim();
			var densityCheck = '0.0%';
			if($(this).val().trim() == ''){
				$(this).children('option').each(function(){
					if(descriptionTitle.trim().replace('"','').replace('"','').toLowerCase() == $(this).text().toLowerCase())
						densityCheck = $(this).val();
				});
				$(this).next().text('\xa0'+densityCheck+'%');
				
			}else
				$(this).next().text('\xa0'+$(this).val()+'%');
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
				
				tableDataString += '<tr>';
				tableDataString += '<td>'+data[i].text+'<input type="hidden" class="categoryID" value="'+data[i].id+'" ></td>';
				tableDataString += '<td>'+data[i].nr_products+'</td>';
				
				if(data[i].title_keyword_description_density && data[i].description_title) {
					var density = '0.0%';
					var densityObj = $.parseJSON(data[i].title_keyword_description_density);
					var descriptionTitle = data[i].description_title;
					
					for(index in densityObj){
						if(descriptionTitle.replace('"','').replace('"','').toLowerCase().trim() == index.trim().toLowerCase())
							density = densityObj[index]+'%';
					}
				
					tableDataString += '<td><select class="changeDensity" style="width:95px;" >';
					tableDataString += '<option value="" >'+descriptionTitle.trim().replace('"','').replace('"','')+'</option>';
					for(index in densityObj){
						tableDataString += '<option value="'+densityObj[index]+'" >'+index+'</option>';
					}
					tableDataString += '</select><span style="position:absolute";>&nbsp;'+density+'</span><br>';
				} else {
					tableDataString += '<td>';
				}
				var user_seo_keywords = data[i].user_seo_keywords.trim();
				var user_keyword_description_density = data[i].user_keyword_description_density.trim()+'%';
				if(user_seo_keywords == '')
					user_keyword_description_density = 'N/A';
				tableDataString += '<input type="text" style="width: 95px;float: left;margin-right: 5px;" placeholder="Your keyword" onblur="keywordAjax(this);" name="keyword" value="'+user_seo_keywords+'" />';
				tableDataString += '<span style="float: left;" >'+user_keyword_description_density+'</span></td>';
				tableDataString += '<td>'+data[i].description_words+'</td>';
				tableDataString += '</tr>';
			}
			
			var categoryCount = data.length;
			var stringNewData = '<table id="'+table_name+'" ><thead><tr><th style="width: 50px !important;word-wrap: break-word;" >Category('+categoryCount+')</th><th>Items</th><th>Category Description SEO</th><th>Words</th></tr></thead><tbody>'+tableDataString+'</tbody></table>';
			if(table_name == 'records')
				$( '#dataTableDiv1' ).html(stringNewData);
			else
				$( '#dataTableDiv2' ).html(stringNewData);
			$( '#'+table_name ).dataTable({"bJQueryUI": true});
			
            $( '#ajaxLoadAni' ).fadeOut( 'slow' );
        }
    });
}
function keywordAjax(obj) {
	var categoryID = $(obj).parent().parent().find('.categoryID').val();
	$.ajax({
	
			url: base_url + 'index.php/measure/getKeywordByDescriptionText',
			type: 'post',
			data: {'keyword': $(obj).val(),
			       'categoryID': categoryID},
			success: function(data) {
				$(obj).next().text(data);
			}

	});
}