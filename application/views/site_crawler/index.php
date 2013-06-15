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
				}
			});
		});
		</script>
		<button id="add_url_list" class="btn new_btn btn-success mt_10 ml_15"><i class="icon-white icon-ok"></i>&nbsp;Add</button>
		<button id="add_list_delete" class="btn new_btn btn-danger mt_10 ml_15" disabled><i class="icon-white icon-ok"></i>&nbsp;Delete</button>
	</div>
	<h3>Current list:</h3>
	<div class="row-fluid">
		<div class="search_area uneditable-input span10" style="cursor: text; width: 765px; height: 250px; overflow : auto;" id="Current_List">
		</div>
		<button id="current_list_delete" class="btn new_btn btn-danger mt_10 ml_15" disabled><i class="icon-white icon-ok"></i>&nbsp;Delete</button>
	</div>
</div>
<script>
function loadCurrentList(){
	$.get('<?php echo site_url('site_crawler/new_urls');?>', function(data) {
  		$('#Current_List').html('');
  		$.each(data.new_urls, function (index, node) {
			$('#Current_List').append("<div id=\"id_"+node.id+"\">"+node.url+"</div>");
		});
    });
}

$(function () {
//	$(document).on('focusout', "#Add_List > div >input , #Current_List > div >input", function(){
//		 $(this).parent().html($(this).val());
//		 console.log( $(this).parents('#Current_List') );
		 //$.post('<?php echo site_url('site_crawler/delete');?>', {id: $('#Current_List > div.active').attr('id')}, function(data) {});

//	});

    $(document).click(function(event) {
        if($(event.target).parents().index($('#Add_List')) == -1) {
            $("#Add_List > div >input").each(function(){
                $(this).parent().html($(this).val());
            });
        }
        if($(event.target).parents().index($('#Current_List')) == -1) {
            $("#Current_List > div >input").each(function(){
                $(this).parent().html($(this).val());
                $.post('<?php echo site_url('site_crawler/update');?>', {id: $('#Current_List > div.active').attr('id'), url:$(this).val()}, function(data) {});
            });
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
	});

	$(document).on("click", "#current_list_delete", function(){
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
		  	$.post('<?php echo site_url('site_crawler/add');?>', {urls: list}, function(data) {
		  		loadCurrentList();
	        });
		}
		$('#Add_List').html('');
		$('#add_list_delete').attr('disabled', 'disabled');
	});


	jQuery(document).ready(function($) {
		loadCurrentList();
	});
});
</script>