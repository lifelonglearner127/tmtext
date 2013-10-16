<div class="tabbable">
    <ul class="nav nav-tabs jq-system-tabs">
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system');?>">General</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/sites_view');?>">Sites</a></li>
        <li class="active"><a data-toggle="tab" href="<?php echo site_url('site_crawler');?>">Site Crawler</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('brand/import');?>">Brands</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/batch_review');?>">Batch Review</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_compare');?>">Product Compare</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_productsmatch');?>">Product Match</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_reports');?>">Reports</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_logins');?>">Logins</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/keywords');?>">Keywords</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/measure_pricing');?>">Pricing </a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('measure/product_models');?>">Product models </a></li>
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
				<span id="system_sitecrawler_btnFileUpload" class="btn btn-success fileinput-button ml_15">
					Upload
					<i class="icon-plus icon-white"></i>
				</span>
                <input id="fileupload" type="file" name="files[]" style="display: none;">
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
                    $('#system_sitecrawler_btnFileUpload').click(function(){
                        $('#fileupload').trigger('click');
                    })
				});
				</script>

				<?php echo form_dropdown('category', $category_list, array(), 'id="category" class="mt_30 ml_15" style="width:120px"'); ?>
				<button id="add_url_list" class="btn new_btn btn-success mt_10 ml_15" disabled><i class="icon-white icon-ok"></i>&nbsp;Add</button>
				<button id="add_list_delete" class="btn new_btn btn-danger mt_10 ml_15" disabled><i class="icon-white icon-ok"></i>&nbsp;Delete</button>
			</div>


			<script>
			$('button#crawl').attr("disabled","disabled");

			$('select[name="batch"]').change(function(e){
				$('button#crawl').removeAttr("disabled");
				if($(e.target).val() == "") {
					$('button#snap_selected_batch').attr("disabled", "disabled");
				} else {
					$('button#snap_selected_batch').removeAttr("disabled");
				}
			});

			function submitBatchSnapProcess() {
				var batch_id = $('select[name="batch"] > option:selected').val();
				var send_data = {
	    		batch_id: batch_id
	    	};
	    	$("#loading_crawl_snap_modal").modal('show');
	    	$.post(base_url + 'index.php/measure/batch_snap_process', send_data, function(data) {
	    		console.log("BATCH SNAP PROCESS RESPONSE : ", data);
	    		$("#loading_crawl_snap_modal").modal('hide');
	    		loadCurrentList();
	    	});
			}

      </script>


			<h3 class="span3 current_list_title">Crawl list: <br/><small nowrap></small></h3>

            <select name="batch" class="span4 pull-left mt_15" style="width: 125px;" id="batches">
				<?php foreach($batches_list as $ks => $vs):?>
				<option value="<?php echo $ks; ?>"><?php echo $vs; ?></option>
				<?php endforeach;?>
			</select>
			<button id='snap_selected_batch' onclick="submitBatchSnapProcess()" disabled class='btn btn-success new_btn mt_15 ml_10'>Snap</button>
			<button id="crawl_batch" class="btn new_btn btn-success mt_15 ml_10">Crawl</button>
			<button id="re_crawl_batch" class="btn new_btn btn-success mt_15 ml_10">Re-Crawl</button>
            <input type="text" class="span2 pull-left mt_15 ml_10" name="search_crawl_data" >
            <button id="apply_search_data" class="btn new_btn btn-success mt_15 ml_10"><i class="icon-white icon-ok"></i>&nbsp;Apply</button>
            <button id="clear_search_data" class="btn new_btn btn-success mt_15 ml_10"><i class="icon-white icon-ok"></i>&nbsp;Clear</button>

			<div class="row-fluid mt_5">
				<div class="search_area uneditable-input span10" style="cursor: text; width: 765px; height: 320px; overflow : auto;" id="Current_List">
				<!-- <div id='current_list_tbl_holder'>&nbsp;</div> -->
				<ul>
					<lh><span><input type="checkbox" style='margin-top: -6px;' value="" id="checkAll"/></span><span style='width: 40px;'>&nbsp;</span><span style='width: 60px;'>ID</span><span>Status</span><span>Last Crawled</span><span>Category</span><span>URL</span></lh>
				</ul>
				</div>
				<button id="current_list_delete" class="btn new_btn btn-danger mt_10 ml_15" disabled><i class="icon-white icon-ok"></i>&nbsp;Delete</button>
				<button id="list_failed" class="btn new_btn btn-danger mt_10 ml_15"><i class="icon-white icon-ok"></i>&nbsp;Show Failed</button>
				<button id="crawl_new" class="btn new_btn btn-success mt_10 ml_15" disabled><i class="icon-white icon-ok"></i>&nbsp;Crawl New</button>
				<button id="crawl_all" class="btn new_btn btn-success mt_10 ml_15"><i class="icon-white icon-ok"></i>&nbsp;Crawl All</button>
				<button id="current_crawl" class="btn new_btn btn-success mt_10 ml_15" disabled><i class="icon-white icon-ok"></i>&nbsp;Crawl</button>
				<button id="current_snapshot" onclick="currentSnapshot();" class="btn new_btn btn-success mt_10 ml_15" disabled><i class="icon-white icon-ok"></i>&nbsp;Snapshot</button>
				<button id="current_snapshot_cmd" class="btn new_btn btn-success mt_10 ml_15" disabled><i class="icon-white icon-ok"></i>&nbsp;Snap (cmd)</button>
				<div class="span2 mt_15" style="width: 11%;">
					<input type="checkbox" name="cb_crawl_now" value="1" id="cb_crawl_now" style="width:20px;">
					<label class="control-label" for="use_files" style="display: inline;">immediately</label>
				</div>
				<p class='help-block'>* use checkboxes in table list to activate snapshot button</p>
			</div>
			<div class="row-fluid">
				<div id="Current_List_Pager"></div>
			</div>
		</div>
	  </div>
</div>

<!-- MODALS (START) -->
<div class="modal hide fade ci_hp_modals" id='loading_crawl_snap_modal'>
	<div class="modal-body">
		<p><img src="<?php echo base_url();?>img/loader_scr.gif">&nbsp;&nbsp;&nbsp;Generating snapshots. Please wait...</p>
	</div>
</div>
<div class="modal hide fade ci_hp_modals" id='preview_crawl_snap_modal'>
	<div class="modal-body" style='overflow: hidden'>
		<div class='snap_holder'>&nbsp;</div>
	</div>
	<div class="modal-footer">
		<a href="javascript:void(0)" class="btn" data-dismiss="modal">Close</a>
		<a href="javascript:void(0)" id="snap_modal_refresh" class="btn btn-success" onclick="return false">Refresh snapshot</a>
	</div>
</div>
<!-- MODALS (END) -->

<script>
function showSnap(snap, id, url) {
	$("#preview_crawl_snap_modal").modal('show');
	var snap = "webshoots/" + snap;
	$("#preview_crawl_snap_modal .snap_holder").html("<img src='" + base_url +  snap + "'>");
	$("#preview_crawl_snap_modal #snap_modal_refresh").attr("onclick", "snapshotIt('" + id + "', '" + url + "', true)");
}

function loadCurrentList(url,failed) {
	$("#checkAll").removeAttr('checked');
	url = typeof url !== 'undefined' ? url: '<?php echo site_url('site_crawler/all_urls');?>';
	failed = typeof failed !== 'undefined' ? 1 : 0;

    var search_crawl_data = '';
    if($('input[name="search_crawl_data"]').val() != ''){
        search_crawl_data = $('input[name="search_crawl_data"]').val();
    }

    var batch_id = 0;
    if($('select[name="batch"]').val() != ''){
    	batch_id = $('select[name="batch"]').val();
    }

	$.get(url, {'search_crawl_data': search_crawl_data, 'batch_id': batch_id, 'failed':failed}, function(data) {
		$('#Current_List ul li').remove();
//                console.log(data);
		if(data.new_urls.length > 0) {
			$("button#crawl_new").removeAttr('disabled');
		} else {
			$("button#crawl_new").attr('disabled', 'disabled');
		}

		$("h3 small").html(data.total + ' items Total -- '+ data.new+ ' New');
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
            if(node.imported_data_id == null){
                imported_data_id = '';
            }else{
                imported_data_id = node.imported_data_id;
            }

            var snap_line = "<a class='btn btn-primary btn-small btn-make-snap' href='javascript:void(0)' onclick=\"snapshotIt('" + node.id + "', '" + node.url + "', false);\"><i class='icon-screenshot icon-white'></i></a>";
            if(node.snap !== null && node.snap !== "") {
            	snap_line = "<a class='btn btn-success btn-small btn-snap-done' href='javascript:void(0)' onclick=\"showSnap('" + node.snap + "', '" + node.id + "', '" + node.url + "');\"><i class='icon-ok icon-white'></i></a>";
            }

			$('#Current_List ul').append("<li id=\"id_"+node.id+"\"><span><input data-url=\""+node.url+"\" data-id=\""+node.id+"\" type=\"checkbox\" name=\"ids[]\" value=\""+node.id+"\"/></span><span style='width: 40px;'>" + snap_line + "</span><span style='width: 60px;'>"+imported_data_id+"</span><span>"+node.status + "</span><span>"+updated+"</span><span>"+category+"</span><span class=\"url ellipsis\">"+node.url+"</span></li>");

			$(".btn-make-snap").tooltip({
				placement: 'left',
				title: 'Make snapshot'
			});

			if(node.snap !== null && node.snap !== "") {
				// console.log(node.snap_date);
				// var test_date = new Date(2013, 08, 26, 23, 46, 55);
				// console.log("TEST : ", test_date.getHours());
				if(typeof(node.snap_date) !== 'undefined') {
					var hours = new Date(node.snap_date).getHours();
					var minutes = new Date(node.snap_date).getMinutes();
					var seconds = new Date(node.snap_date).getSeconds();
					var hours_min_sec = node.snap_date.substring(11, node.snap_date.length) ; // === cause for some reasons normal way don't work any more !
					$(".btn-snap-done").tooltip({
						placement: 'left',
						// title: moment(node.snap_date).format('MMMM Do, YYYY') + ", " + hours + ":" + minutes + ":" + seconds
						title: moment(node.snap_date).format('MMMM Do, YYYY') + ", " + hours_min_sec
					});
				}
			}
		});
  		$('#Current_List_Pager').html(data.pager);

                if (urls.length > 0) {
                    $('#current_snapshot').attr('disabled', true);
                    $('#current_snapshot_cmd').attr('disabled', true);
                    for(var i = 0;i < urls.length; i++){
                        $('#id_'+urls[i].id).find('a').attr('disabled',true);
                        $('#id_'+urls[i].id).find('a').attr('onclick','return false;');
                    }
                    currentSnapshotAjax();
                } else {
                    $('#current_snapshot').removeAttr('disabled');
                    $('#current_snapshot_cmd').removeAttr('disabled');
                }
    });
}

function checkAddList(){
	if($('#Add_List').children().length > 0) {
		$("button#add_url_list").removeAttr('disabled');
	} else {
		$("button#add_url_list").attr('disabled', 'disabled');
	}
}

function closeInputs(event) {
	if($(event.target).parents().index($('#Add_List')) == -1) {
        $("#Add_List > div >input[type='text']").each(function(i,e){
            if (!$(this).parent('div').hasClass('new')){
            	$(this).parent().html($(this).val());
            }
        });
    }
    if($(event.target).parents().index($('#Current_List')) == -1) {
        $("#Current_List > ul > li > span > input[type='text']").each(function(){
            $(this).parent().html($(this).val());
            $.post('<?php echo site_url('site_crawler/update');?>', {id: $('#Current_List > ul > li.active').attr('id'), url:$(this).val()}, function(data) {});
        });
    }
    checkAddList();
}

function snapshotIt(id, url, modal_close) {
	if(modal_close)
            $("#preview_crawl_snap_modal").modal('hide');
        $('#id_'+id).children().eq(1).children('a').hide();
        $('#id_'+id).children().eq(1).append('<img style="margin-left: 10px;" src="'+base_url+'webroot/img/ajax-loader.gif" />');
	var urls = [];
	var mid = {
		id: id,
		url: url
	}
	var send_data = {
		url: mid
	};
//	$("#loading_crawl_snap_modal").modal('show');
	$.post(base_url + 'index.php/measure/crawlsnapshoot', send_data, function(data) {
//		$("#loading_crawl_snap_modal").modal('hide');
		$('#current_snapshot').attr('disabled', 'disabled');
                var curUrl;
                var currentPage = $('#Current_List_Pager').children('strong').text();
                if(currentPage == '1')
                    curUrl = base_url + 'index.php/site_crawler/all_urls/';
                else
                    curUrl = base_url + 'index.php/site_crawler/all_urls/'+(currentPage-1)+'0';
		loadCurrentList(curUrl);
	});
}

$(function () {
    $.fn.setCursorToTextEnd = function() {
        $initialVal = this.val();
        this.val('');
        this.val($initialVal);
    };

    $("#current_snapshot_cmd").click(function(e) { // ==== !!! EXPREIMENTAL OPTION !!!
    	var urls = [];
    	$("#Current_List > ul > li input[type='checkbox']:checked").each(function(index, value) {
    		var mid = {
    			id: $(value).data('id'),
    			url: $(value).data('url')
    		}
    		urls.push(mid);
    	});
    	var send_data = {
    		urls: urls
    	};
    	$("#loading_crawl_snap_modal").modal('show');
    	$.post(base_url + 'index.php/measure/crawlsnapshootcmd', send_data, function(data) {
    		console.log("CMD PATH: ", data);
    		$("#loading_crawl_snap_modal").modal('hide');
    		$('#current_snapshot').attr('disabled', 'disabled');
    		$('#current_snapshot_cmd').attr('disabled', 'disabled');
    		loadCurrentList();
    	});
    });
    
    
//    $("#current_snapshot_cmd").click(function(e) { // ==== !!! EXPREIMENTAL OPTION !!!
//    	var dep_id_arr = [];
//    	$("#Current_List > ul > li input[type='checkbox']:checked").each(function(index, value) {
//    		dep_id_arr.push($(value).data('id'));
//    	});
//        $.ajax({
//            type: "POST",
//            url: base_url + 'index.php/system/add_snapshot_queue',
//            data: { dep_id_arr: dep_id_arr }
//        }).done(function( data ) {
//            loadCurrentList();
//        });
//        
//    });

    setTimeout(function(){
        $('title').text("Site Crawler");
    }, 10);

    $(document).click(function(event) {
    	if(!$(event.target).is('#current_list_delete') && !$(event.target).is('#current_crawl')){
        	closeInputs(event);
    	}
    });

    $(document).on('change', '#Add_List > div.new > input',  function(){
        $(this).parent().removeClass('new');
    });

    $(document).on("click", "#Add_List", function(event){
        if(event.target.tagName.toUpperCase() == 'DIV') {
            if ($(event.target).hasClass('item')) {
                return;
            }
        }
        if ($(this).find('input').val() == undefined || $(this).find('div:last-child input').val().length != 0) {
			$(this).append("<div class='new item'><input type='text' value=''></div>");
            $(this).find('div:last-child input').focus();
        }
	});

	$(document).on("click", "#Add_List > div", function(){
		$(this).parent('div').find('div').removeClass('active');
		$(this).addClass('active');

		if ($(this).find('input').val() == undefined) {
			$(this).html("<input type='text' value='"+$(this).text()+"'>");
            $(this).find('input').focus();
            $(this).find('input').setCursorToTextEnd();
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
		$('#current_crawl').removeAttr('disabled');
		// $('#current_snapshot').removeAttr('disabled');
	});

	$(document).on("click", "#Current_List > ul > li input[type='checkbox']", function(e) {
		if( $("#Current_List > ul > li input[type='checkbox']:checked").length > 0 ) {
			$('#current_snapshot').removeAttr('disabled');
			$('#current_snapshot_cmd').removeAttr('disabled');
		} else {
			$('#current_snapshot').attr('disabled', 'disabled');
			$('#current_snapshot_cmd').attr('disabled', 'disabled');
		}
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

	$(document).on("click", 'button#current_crawl', function(){
		//$('button#current_crawl').attr('disabled', 'disabled');
		//$.post('<?php echo site_url('site_crawler/crawl_all');?>', {id: $('#Current_List > ul > li.active').attr('id')}, function(data) {});

		var ids = [];
		$("#Current_List > ul > li input[name='ids[]']:checked").each(function () {
			ids.push(parseInt($(this).val()));
		});

		if (ids.length==0) {
			$('button#current_crawl').attr('disabled', 'disabled');
		} else {
			$.post('<?php echo site_url('site_crawler/crawl_all');?>', {ids: ids, crawl: $('#cb_crawl_now').is(':checked') }, function(data) {
				loadCurrentList();
			});
		}
	});

	$(document).on("click", "button#add_url_list", function(event){
		closeInputs(event);

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
		$.post('<?php echo site_url('site_crawler/crawl_all');?>', { crawl: $('#cb_crawl_now').is(':checked') } , function(data) {
			loadCurrentList();
		});
	});

	$(document).on("click", "button#crawl_batch", function(){
		$.post('<?php echo site_url('site_crawler/crawl_all');?>', {batch_id: $('#batches option:selected').val(), crawl: $('#cb_crawl_now').is(':checked') }, function(data) {
			loadCurrentList();
		});
	});

	$(document).on("click", "button#re_crawl_batch", function(){
		$.post('<?php echo site_url('site_crawler/crawl_all');?>', {recrawl: 1, batch_id: $('#batches option:selected').val(), crawl: $('#cb_crawl_now').is(':checked') }, function(data) {
			loadCurrentList();
		});
	});

	$(document).on("click", "#Current_List_Pager a", function(event){
		event.preventDefault();
		loadCurrentList($(this).attr('href'));
	});

    $(document).on("click", "button#clear_search_data", function(){
        $('input[name="search_crawl_data"]').val('');
        loadCurrentList();
    });

    $(document).on("click", "button#apply_search_data", function(){
        if($('input[name="search_crawl_data"]').val()!=''){
            loadCurrentList();
        }
    });

    $(document).on("click", "button#list_failed", function(){
    	loadCurrentList(undefined, true);
    });

	jQuery(document).ready(function($) {
		loadCurrentList();
	});

	$(document).on('click', 'input#checkAll', function(){
		$("#Current_List > ul > li input[type='checkbox']").each(function(index, value) {
			$(this).attr('checked', $('input#checkAll').is(':checked'));
    	});

		if ($('input#checkAll').is(':checked')) {
			$('button#current_snapshot').removeAttr('disabled');
			$('button#current_snapshot_cmd').removeAttr('disabled');
			$('button#current_crawl').removeAttr('disabled');
		} else {
			$('button#current_snapshot').attr('disabled', 'disabled');
			$('button#current_snapshot_cmd').attr('disabled', 'disabled');
			$('button#current_crawl').attr('disabled', 'disabled');
		}
	});

	$(document).on('change', 'select#batches', function(){
		loadCurrentList();
	});
});

var urls = [];

function currentSnapshot(){
        $('#current_snapshot').attr('disabled', true);
        $('#current_snapshot_cmd').attr('disabled', true);
    	$("#Current_List > ul > li input[type='checkbox']:checked").each(function(index, value) {
    		var mid = {
    			id: $(value).data('id'),
    			url: $(value).data('url')
    		}
    		urls.push(mid);
                $(value).parent().next().children('a').attr('disabled',true);
                $(value).parent().next().children('a').attr('onclick','return false;')
    	});

        currentSnapshotAjax();
}

function currentSnapshotAjax() {
    var url = urls.shift();
    $('#id_'+url.id).children().eq(1).children('a').hide();
    $('#id_'+url.id).children().eq(1).append('<img style="margin-left: 10px;" src="'+base_url+'webroot/img/ajax-loader.gif" />');
    $('#current_snapshot').attr('disabled', true);
    $('#current_snapshot_cmd').attr('disabled', true);
    $.ajax({
        type: "POST",
        url: base_url + 'index.php/measure/crawlsnapshoot',
        data: { url: url }
    }).done(function(){
        var curUrl;
        var currentPage = $('#Current_List_Pager').children('strong').text();
        if(currentPage == '1')
            curUrl = base_url + 'index.php/site_crawler/all_urls/';
        else
            curUrl = base_url + 'index.php/site_crawler/all_urls/'+(currentPage-1)+'0';
        loadCurrentList(curUrl);
    });
}
//function loadCurrentRow(url) {
//    $.ajax({
//        type: "POST",
//        url: '<?php echo site_url('site_crawler/current_url'); ?>',
//        data: { url: url }
//    }).done(function(){
//
//    });
//}
</script>
