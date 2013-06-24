<div class="tabbable">
      <ul class="nav nav-tabs jq-system-tabs">
		<li class=""><a data-toggle="tab" href="<?php echo site_url('system');?>">General</a></li>
		<li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_accounts');?>">New Accounts</a></li>
		<li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_roles');?>">Roles</a></li>
		<li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_users');?>">Users</a></li>
		<li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_compare');?>">Product Compare Interface</a></li>
		<li class="active"><a data-toggle="tab" href="<?php echo site_url('site_crawler');?>">Site Crawler</a></li>
	  </ul>
	  <div class="tab-content">
		<div class="info-message"></div>
		<div class="site_crawler_content">
			<h3>Add to list:</h3>
			<div class="row-fluid">
				<div class="search_area uneditable-input span10" onClick="this.contentEditable='false';" style="cursor: text; width: 765px; height: 250px; overflow : auto;" id="Add_List">
				</div>
				<span class="btn btn-success fileinput-button ml_15">
					Upload
					<i class="icon-plus icon-white"></i>
					<input id="fileupload" type="file" name="files[]">
				</span>
				<script>
				$(function () {
					var url = '<?php echo site_url('site_crawler/upload');?>';
					$('#fileupload').fileupload({
						url: url,
						dataType: 'json',
						done: function (e, data) {
							$.each(data.result.urls, function (index, url) {
								$('#Add_List').append("<div>"+url+"</div>");
							});
							checkAddList();
						}
					});
				});
				</script>

				<?php echo form_dropdown('category', $category_list, array(), 'id="category" class="mt_30 ml_15" style="width:120px"'); ?>
				<button id="add_url_list" class="btn new_btn btn-success mt_10 ml_15" disabled><i class="icon-white icon-ok"></i>&nbsp;Add</button>
				<button id="add_list_delete" class="btn new_btn btn-danger mt_10 ml_15" disabled><i class="icon-white icon-ok"></i>&nbsp;Delete</button>
			</div>
			<h3>Current list:</h3>
			<div class="row-fluid">
				<div class="search_area uneditable-input span10" style="cursor: text; width: 765px; height: 250px; overflow : auto;" id="Current_List">
				</div>
				<button id="current_list_delete" class="btn new_btn btn-danger mt_10 ml_15" disabled><i class="icon-white icon-ok"></i>&nbsp;Delete</button>
				<button id="crawl_now" class="btn new_btn btn-success mt_10 ml_15" disabled><i class="icon-white icon-ok"></i>&nbsp;Crawl Now</button>
			</div>
		</div>
	  </div>
</div>
<script>
function loadCurrentList(){
	$.get('<?php echo site_url('site_crawler/new_urls');?>', function(data) {
  		$('#Current_List').html('');

		if(data.new_urls.length > 0) {
			$("button#crawl_now").removeAttr('disabled');
		} else {
			$("button#crawl_now").attr('disabled', 'disabled');
		}

  		$.each(data.new_urls, function (index, node) {
			$('#Current_List').append("<div id=\"id_"+node.id+"\">"+node.url+"</div>");
		});
    });
}

function checkAddList(){
	if($('#Add_List').children().length > 0) {
		$("button#add_url_list").removeAttr('disabled');
	} else {
		$("button#add_url_list").attr('disabled', 'disabled');
	}
}

$(function () {
    setTimeout(function(){
        $('title').text("Site Crawler");
    }, 10);
    $(document).click(function(event) {
        if($(event.target).parents().index($('#Add_List')) == -1) {
            $("#Add_List > div >input").each(function(i,e){
                if (!$(this).parent('div').hasClass('new')){
                	$(this).parent().html($(this).val());
                }
            });
        }
        if($(event.target).parents().index($('#Current_List')) == -1) {
            $("#Current_List > div >input").each(function(){
                $(this).parent().html($(this).val());
                $.post('<?php echo site_url('site_crawler/update');?>', {id: $('#Current_List > div.active').attr('id'), url:$(this).val()}, function(data) {});
            });
        }
        checkAddList();
    });

    $(document).on('change', '#Add_List > div.new > input',  function(){
        $(this).parent().removeClass('new');
    });

    $(document).on("click", "#Add_List", function(){
        if ($(this).find('input').val() == undefined) {
			$(this).append("<div class='new'><input type='text' value=''></div>").focus();
        }
	});

	$(document).on("click", "#Add_List > div, #Current_List > div", function(){
		$(this).parent('div').find('div').removeClass('active');
		$(this).addClass('active');

		if ($(this).find('input').val() == undefined) {
			$(this).html("<input type='text' value='"+$(this).text()+"'>");
		}
	});

	$(document).on("click", "#Add_List > div", function(){
		$('#add_list_delete').removeAttr('disabled');
	})

	$(document).on("click", "#Current_List > div", function(){
		$('#current_list_delete').removeAttr('disabled');
	})

	$(document).on("click", "#add_list_delete", function(){
		$('#Add_List > div.active').remove();
		$('#add_list_delete').attr('disabled', 'disabled');
	});

	$(document).on("click", "#current_list_delete", function(){
		$('#current_list_delete').attr('disabled', 'disabled');
		$.post('<?php echo site_url('site_crawler/delete');?>', {id: $('#Current_List > div.active').attr('id')}, function(data) {});
		loadCurrentList();
	});

	$(document).on("click", "button#add_url_list", function(){
		var list = [];
		$('#Add_List div').each(function(index, node) {
			var url = $(node).text();
			list.push(url);
		});

		if (list.length>0) {
		  	$.post('<?php echo site_url('site_crawler/add');?>', {urls: list, category_id: $('#category option:selected').val() }, function(data) {
		  		loadCurrentList();
	        });
		}
		$('#Add_List').html('');
		$('#add_list_delete').attr('disabled', 'disabled');
	});

	$(document).on("click", "button#crawl_now", function(){
		$.post('<?php echo site_url('site_crawler/crawl_now');?>', function(data) {
			loadCurrentList();
		});
	});


	jQuery(document).ready(function($) {
		loadCurrentList();
	});
});
</script>