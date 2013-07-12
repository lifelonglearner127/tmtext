<div class="tabbable">
    <ul class="nav nav-tabs jq-system-tabs">
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system');?>">General</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_compare');?>">Product Compare Interface</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_productsmatch');?>">Product Match</a></li>
        <li class="active"><a data-toggle="tab" href="<?php echo site_url('site_crawler');?>">Site Crawler</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/batch_review');?>">Batch Review</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/sites_view');?>">Sites</a></li>
    </ul>
	  <div class="tab-content">

	  	<!-- NEW SUB TABS INTERFACE (START) -->
    	<!-- <div class='tabbable'>
    		<ul id='sub_crawl_tabset' class="nav nav-tabs jq-system-tabs">
    			<li class="active"><a data-content="tab1_crawl_tabset" href="javascript:void(0)">Site Crawler</a></li>
    			<li><a data-content="tab2_crawl_tabset" href="javascript:void(0)">Fetch site images</a></li>
			</ul>
			<div class='tab-content' style='border-bottom: none;'>
				<div id="tab1_crawl_tabset" class="tab-pane active">&nbsp;</div>
				<div id="tab2_crawl_tabset" class='tab-pane'>&nbsp;</div>
			</div>
		</div> -->
    	<!-- NEW SUB TABS INTERFACE (END) -->


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
				<ul>
					<lh><span>Status</span><span>Last Crawled</span><span>Category</span><span>URL</span></lh>
				</ul>
				</div>
				<button id="current_list_delete" class="btn new_btn btn-danger mt_10 ml_15" disabled><i class="icon-white icon-ok"></i>&nbsp;Delete</button>
				<button id="crawl_new" class="btn new_btn btn-success mt_10 ml_15" disabled><i class="icon-white icon-ok"></i>&nbsp;Crawl New</button>
				<button id="crawl_all" class="btn new_btn btn-success mt_10 ml_15"><i class="icon-white icon-ok"></i>&nbsp;Crawl All</button>
			</div>
			<div class="row-fluid">
				<div id="Current_List_Pager"></div>
			</div>
		</div>
	  </div>
</div>
<script>
function loadCurrentList(url){
	url = typeof url !== 'undefined' ? url: '<?php echo site_url('site_crawler/all_urls');?>';

	$.get(url, function(data) {
		$('#Current_List ul li').remove();

		if(data.new_urls.length > 0) {
			$("button#crawl_new").removeAttr('disabled');
		} else {
			$("button#crawl_new").attr('disabled', 'disabled');
		}

  		$.each(data.new_urls, function (index, node) {
  	  		var category = '';
  	  		if (node.name != undefined) {
  	  	  		category = node.name;
  	  		}

  	  		if (node.updated == null) {
  	  	  		updated = 'Never';
  	  		} else {
  	  			updated = node.updated;
  	  		}

			$('#Current_List ul').append("<li id=\"id_"+node.id+"\"><span>"+node.status+"</span><span>"+updated+"</span><span>"+category+"</span><span class=\"url ellipsis\">"+node.url+"</span></li>");
		});

  		$('#Current_List_Pager').html(data.pager);
    });
}

function checkAddList(){
	if($('#Add_List').children().length > 0) {
		$("button#add_url_list").removeAttr('disabled');
	} else {
		$("button#add_url_list").attr('disabled', 'disabled');
	}
}

function closeInputs() {
	if($(event.target).parents().index($('#Add_List')) == -1) {
        $("#Add_List > div >input").each(function(i,e){
            if (!$(this).parent('div').hasClass('new')){
            	$(this).parent().html($(this).val());
            }
        });
    }
    if($(event.target).parents().index($('#Current_List')) == -1) {
        $("#Current_List > ul > li > span > input").each(function(){
            $(this).parent().html($(this).val());
            $.post('<?php echo site_url('site_crawler/update');?>', {id: $('#Current_List > ul > li.active').attr('id'), url:$(this).val()}, function(data) {});
        });
    }
    checkAddList();
}

$(function () {
    setTimeout(function(){
        $('title').text("Site Crawler");
    }, 10);
    $(document).click(function(event) {
    	closeInputs();
    });

    $(document).on('change', '#Add_List > div.new > input',  function(){
        $(this).parent().removeClass('new');
    });

    $(document).on("click", "#Add_List", function(){
        if ($(this).find('input').val() == undefined) {
			$(this).append("<div class='new'><input type='text' value=''></div>").focus();
        }
	});

	$(document).on("click", "#Add_List > div", function(){
		$(this).parent('div').find('div').removeClass('active');
		$(this).addClass('active');

		if ($(this).find('input').val() == undefined) {
			$(this).html("<input type='text' value='"+$(this).text()+"'>");
		}
	});

	$(document).on("click", "#Current_List li span.url", function(){
		$(this).parent('ul').find('li').removeClass('active');
		$(this).parent('li').addClass('active');

		if ($(this).find('input').val() == undefined) {
			$(this).html("<input type='text' value='"+$(this).text()+"'>");
		}
	});


	$(document).on("click", "#Add_List > div", function(){
		$('#add_list_delete').removeAttr('disabled');
	});

	$(document).on("click", "#Current_List li", function(){
                $('#Current_List li').removeClass('active');
                $(this).addClass('active');
		$('#current_list_delete').removeAttr('disabled');
	});
        
	$(document).on("click", "#add_list_delete", function(){
		$('#Add_List > div.active').remove();
		$('#add_list_delete').attr('disabled', 'disabled');
	});

	$(document).on("click", "#current_list_delete", function(){
		$('#current_list_delete').attr('disabled', 'disabled');
		$.post('<?php echo site_url('site_crawler/delete');?>', {id: $('#Current_List > ul > li.active').attr('id')}, function(data) {});
		loadCurrentList();
	});
        
        $('html').click(function() {
            if(!$(event.target).is('#current_list_delete')){
                $('#current_list_delete').attr('disabled', 'disabled');
                $('#Current_List li').removeClass('active');
            }
        });

	$(document).on("click", "button#add_url_list", function(){
		closeInputs();

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

	$(document).on("click", "button#crawl_new", function(){
		$.post('<?php echo site_url('site_crawler/crawl_new');?>', function(data) {
			loadCurrentList();
		});
	});

	$(document).on("click", "button#crawl_all", function(){
		$.post('<?php echo site_url('site_crawler/crawl_all');?>', function(data) {
			loadCurrentList();
		});
	});

	$(document).on("click", "#Current_List_Pager a", function(event){
		event.preventDefault();
		loadCurrentList($(this).attr('href'));
	});

	jQuery(document).ready(function($) {
		loadCurrentList();
	});
});
</script>