<link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/smoothness/jquery-ui-1.8.2.custom.css" />
<link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/styles.css" />
<div class="tabbable">
    <?php $this->load->view('system/_tabs', array(
		'active_tab' => 'system/sites_view'
	)) ?>
    <div class="tab-content">
        <script src="<?php echo base_url();?>js/tinysort.js"></script>
        <script type="text/javascript">
            function doconfirm(str)
            {
                var site_name = '';
                if( $("#sites .btn_caret_sign").text() != ''){
                    site_name = ' for ' +  $("#sites .btn_caret_sign").text();
                }
                job=confirm("You are about to delete all "+str+""+site_name+". Are you sure you want to do this?");
                if(job!=true)
                {
                    return false;
                } else {
                   $.post(base_url + 'index.php/system/delete_all', {
                        'site_name':  $("#sites .btn_caret_sign").text(),
                        'site_id':  $("#sites .btn_caret_sign").attr('id'),
                        'type': str
                    }, function(data) {
                        if(str=='categories'){
                            $('select[name="category"]').empty();
                        } else if(str == 'departments') {
                            $('select[name="department"]').empty();
                        } else if(str == 'overall'){
                            $('select[name="best_sellers"]').empty();
                        }
                        //$('.info').append('<p class="alert-success">The '+str+' was successfully deleted</p>').fadeOut(10000);
                    }, 'json');
                    return false;
                }
            }
            function selectOption(){
                $(".hp_boot_drop .dropdown-menu > li > a").bind('click', function(e) {
                    var new_caret = $.trim($(this).text());
                    $("#sites .btn_caret_sign").text(new_caret);
                    $("#sites .btn_caret_sign").attr('id', $.trim($(this).data('value')));
                    $.post(base_url + 'index.php/system/get_site_info', {'site': $(this).data('value') }, function(data){
                        if(data.length > 0){
                            if(data[0].name != ''){
                                $('input#site_name').val(data[0].name);
                            }else{
                                $('input#site_name').val('');
                            }
                            if(data[0].url != ''){
                                $('input#site_url').val(data[0].url);
                            }else{
                                $('input#site_url').val('');
                            }
                            if(data[0].image_url != ''){
                                $('img#site_logo').attr({'src': base_url+'img/'+data[0].image_url });
                            } else {
                                $('img#site_logo').attr({'src': base_url+'img/no-logo.jpg' });
                            }
                        }
                    });
                    $.post(base_url + 'index.php/measure/getDepartmentsByCustomer', {'customer_name': new_caret}, function(data) {
                        $("select[name='department']").empty();
                        if(data.length > 0){
                            for(var i=0; i<data.length; i++){
                                $("select[name='department']").append("<option value='"+data[i].id+"'>"+data[i].text+"</option>");
                            }
                            standaloneDepartmentScreenDetector();
                        }
                    });
                    $.post(base_url + 'index.php/system/getCategoriesBySiteId', {'site_id': $(this).data('value'),
                        'department_id': $('select[name="department"]').find('option:selected').val()}, function(data) {
                        $("select[name='category']").empty();
                        if(data.length > 0 ){
                            for(var i=0; i<data.length; i++){
                                $("select[name='category']").append("<option value='"+data[i].id+"'>"+data[i].text+"</option>");
                            }
                            standaloneCatScreenDetector();
                        }
                    });
                    $.post(base_url + 'index.php/system/getBestSellersBySiteId', {'site_id': $(this).data('value')}, function(data) {
                        $("select[name='best_sellers']").empty();
                        if(data.length > 0 ){
                            for(var i=0; i<data.length; i++){
                                $("select[name='best_sellers']").append("<option value='"+data[i].id+"'>"+data[i].page_title+"</option>");
                            }
                        }
                    });
                });
            }
            selectOption();
            $('button#btn_new_site').click(function(){
                                    
                if($('#new_site').val() != ''){
                    
                    $.post(base_url + 'index.php/system/add_new_site', {'site': $('#new_site').val()}, function(data){
                        $(".info-message").append(data.message);
                        $(".info-message").fadeOut(7000);
                        $(".hp_boot_drop .dropdown-menu").append('<li><a href="javascript:void(0)" data-value="'+data.id+'" data-item="'+data.id+'"><span>'+$('#new_site').val()+'</span></a></li>');
                        selectOption();
                         $(".hp_boot_drop .dropdown-menu li ").tsort('span',{order:'asc'});
                        $('#site_name').val($('#new_site').val());
                        $("#sites .btn_caret_sign").text($('#new_site').val());
                        $('#new_site').val('');
                        $('#site_url').val('');
                       });

                }
                return false;
            });

            $('button#delete_site').click(function(){
                $.post(base_url + 'index.php/system/delete_site', {'site':  $("#sites .btn_caret_sign").attr('id') }, function(data){
                    $("#sites .btn_caret_sign").text('[Choose site]');
                    $(".hp_boot_drop .dropdown-menu li a").each(function(){
                        if($(this).data('value') == $("#sites .btn_caret_sign").attr('id')){
                            $(this).remove();
                        }
                    })
                    $('input#new_site').val('');
                    $('input#site_name').val('');
                    $('input#site_url').val('');
                    $('img#site_logo').attr({'src': base_url+'img/no-logo.jpg' });
                    $(".info-message").html(data.message);
                    $(".info-message").fadeOut(7000);
                });
                return false;
            });

            $('button#sitelogo').click(function(){
                $.post(base_url + 'index.php/system/update_site_logo', {
                    'id':  $("#sites .btn_caret_sign").attr('id'),
                    'logo': $('input[name="sitelogo_file"]').val()
                }, function(data){
                });
                return false;
            });

            $('button#update_site_info').click(function(){
                $.post(base_url + 'index.php/system/update_site_info', {
                    'id': $("#sites .btn_caret_sign").attr('id'),
                    'logo': $('input[name="sitelogo_file"]').val(),
                    'site_name': $('input[name="site_name"]').val(),
                    'site_url': $('input[name="site_url"]').val()
                }, function(data){
                    $("#sites .btn_caret_sign").text($('input[name="site_name"]').val());
                });
                return false;
            });

            $('button#delete_sitelogo').click(function(){
                $.post(base_url + 'index.php/system/delete_sitelogo', {
                    'id':  $("#sites .btn_caret_sign").attr('id'),
                    'logo': 'no-logo.jpg'
                }, function(data){
                    $('img#site_logo').attr({'src': base_url+'img/no-logo.jpg' });
                    $('input[name="sitelogo_file"]').val('no-logo.jpg');
                });
                return false;
            });

            $('button#delete_department').click(function(){
                $.post(base_url + 'index.php/system/delete_department', {
                    'id': $('select[name="department"]').find('option:selected').val()
                }, function(data){
                    $('select[name="department"]').find('option:selected').remove();
                });
                return false;
            });

            $('button#delete_category').click(function(){
                $.post(base_url + 'index.php/system/delete_category', {
                    'id': $('select[name="category"]').find('option:selected').val()
                }, function(data){
                    $('select[name="category"]').find('option:selected').remove();
                });
                return false;
            });

            $('button#delete_overall').click(function(){
                $.post(base_url + 'index.php/system/delete_overall', {
                    'id': $('select[name="best_sellers"]').find('option:selected').val()
                }, function(data){
                    $('select[name="best_sellers"]').find('option:selected').remove();
                });
                return false;
            });
            $("button#add_department").button().click(function(){
                $('#add_department_dialog').dialog('open');
                return false;
            });
            $('#add_department_dialog').dialog({
                autoOpen: false,
                resizable: false,
                modal: true,
                buttons: {
                    'Save': function() {
                        // save params to DB
                        $.ajax({
                            url: base_url + 'index.php/system/save_department',
                            dataType : 'json',
                            type : 'post',
                            data : {
                                department : $("#column_department").val(),
                                url : $("#column_department_url").val(),
                                text : $("#column_department_text").val(),
                                wc : $("#column_department_wc").val(),
                                site_id: $("#sites .btn_caret_sign").attr("id")
                            },
                            success : function( data ) {
                                console.log(data);
                            }
                        });
                        $(this).dialog('close');
                    },
                    'Cancel': function() {
                        $(this).dialog('close');
                    }
                },
                width: '250px'
            });

            $("button#add_category").click(function(){
                $('#add_category_dialog').dialog('open');
                return false;
            });
            $('#add_category_dialog').dialog({
                autoOpen: false,
                resizable: false,
                modal: true,
                buttons: {
                    'Save': function() {
                        // save params to DB
                        $.ajax({
                            url: base_url + 'index.php/system/save_category',
                            dataType : 'json',
                            type : 'post',
                            data : {
                                category : $("#column_category").val(),
                                url : $("#column_category_url").val(),
                                text : $("#column_category_text").val(),
                                wc : $("#column_category_wc").val(),
                                site_id: $("#sites .btn_caret_sign").attr("id"),
                                department_id: $("select[name='department']").find('option:selected').val()
                            },
                            success : function( data ) {
                                console.log(data);
                            }
                        });
                        $(this).dialog('close');
                    },
                    'Cancel': function() {
                        $(this).dialog('close');
                    }
                },
                width: '250px'
            });

            $('select#sites').keypress(function(e){
                if(e.keyCode==38){
                    var opt = $(this).find('option:selected').prev().val();
                } else if(e.keyCode==40){
                    var opt = $(this).find('option:selected').next().val();
                }
                if(e.keyCode==38 || e.keyCode==40){
                      $.post(base_url + 'index.php/system/get_site_info', {'site': opt}, function(data){
                       if(data.length > 0){
                         if(data[0].name != ''){
                           $('input#site_name').val(data[0].name);
                         }else{
                           $('input#site_name').val('');
                         }
                         if(data[0].url != ''){
                           $('input#site_url').val(data[0].url);
                         }else{
                           $('input#site_url').val('');
                         }
                         if(data[0].image_url != ''){
                           $('img#site_logo').attr({'src': data[0].image_url });
                         } else {
                           $('img#site_logo').attr({'src': base_url+'img/no-logo.jpg' });
                         }
                       }
                     });
                }
            });

//            $("#department_snapshot").click(function(){
//                $("#loading_crawl_snap_modal").modal('show');
//                $.post(base_url + 'index.php/system/system_sites_department_snap', {
//                    'id': $('select[name="department"]').find('option:selected').val()
//                }, function(data){
//                    $("#loading_crawl_snap_modal").modal('hide');
//                    if(data['status']) {
//                        showSnap("<img src='" + data['snap'] + "'>");
//                        standaloneDepartmentScreenDetector();
//                    } else {
//                        showSnap("<p>" + data['msg'] + "</p>");
//                    }
//                });
//                return false;
//            });

            var ids = new Array();
            var refreshIntervalId = 0;
            $("#department_snapshot").click(function(){
                $('#department_snapshot').hide();
                $('#add_snapshot_queue').hide();
                $('#department_snapshot_process').show();
                $('#department_loader').show();
                if(ids.length > 0){
                    refreshIntervalId = setInterval(function(){
                        $.ajax({
                            type: "POST",
                            url: base_url + 'index.php/system/department_snaps_ajax',
                            data: { ajax: "ajax" },
                            dataType: 'json'
                        }).done(function( data ) {
                            $('#department_snapshot_process').text('In process: '+data.process+' Done: '+data.done);
                        });
                    },500);
                    $.post(base_url + 'index.php/system/system_sites_department_snaps', {
                        'ids': ids
                }, function(data){
                        clearInterval(refreshIntervalId);
                        ids = new Array();
                        $('#department_snapshot_process').hide();
                        $('#department_loader').hide();
                        $('#department_snapshot').show();
                        $('#department_snapshot').attr('disabled',true);
                        $('#add_snapshot_queue').show();
                        $( "select[name='department']" ).trigger( "change" );
                    });
                    }
                return false;
                });
            $('#add_snapshot_queue').click(function(){
            
                $('#department_snapshot').removeAttr('disabled');
                var departmentValue = $('select[name="department"]').children('option:selected').val();
                if($.inArray(departmentValue, ids) == -1)
                    ids.push(departmentValue);
                var snapshot_arr = [];
                snapshot_arr[0] = [];
                snapshot_arr[0][0] = departmentValue;
                $.ajax({
                    type: "POST",
                    url: base_url + 'index.php/system/add_snapshot_queue',
                    data: { snapshot_arr: snapshot_arr,type: 'sites_view_snapshoot' }
                }).done(function( data ) {
                });
                
                return false;
            });

            $("#category_snapshot").click(function(){
                $("#loading_crawl_snap_modal").modal('show');
                $.post(base_url + 'index.php/system/system_sites_category_snap', {
                    'id': $('select[name="category"]').find('option:selected').val()
                }, function(data){
                    $("#loading_crawl_snap_modal").modal('hide');
                    console.log(data);
                    if(data['status']) {
                        showSnap("<img src='" + data['snap'] + "'>");
                        standaloneCatScreenDetector();
                    } else {
                        showSnap("<p>" + data['msg'] + "</p>");
                    }
                });
                return false;
            });
            function showSnap(data) {
                $("#preview_crawl_snap_modal").modal('show');
                $("#preview_crawl_snap_modal .snap_holder").html(data);
            }

            $("select#category_sites_frow").change(function() {
                standaloneCatScreenDetector();
            });

            $("select[name='department']").change(function(){
                if($(this).attr('id') =='second_department'){
                    var select_opt = $(this).val();
                    $("select#first_department option").each(function(){
                       if($(this).val() == select_opt){
                           $(this).attr('selected','selected');
                       }
                    });
                } else {
                    var select_opt = $(this).val();
                    $("select#second_department option").each(function(){
                        if($(this).val() == select_opt){
                            $(this).attr('selected','selected');
                        }
                    });
                }
                $.post(base_url + 'index.php/system/getCategoriesBySiteId', {'site_id': $("#sites .btn_caret_sign").attr('id'),
                    'department_id': $(this).val()}, function(data) {
                    departmentScreenDetector(data.snap_data); // ===== monitor icon and screenshot availability decision
                    var data = data.result;
                    $("select[name='category']").empty();
                    if(data.length > 0 ){
                        for(var i=0; i<data.length; i++){
                            $("select[name='category']").append("<option value='"+data[i].id+"'>"+data[i].text+"</option>");
                        }
                    }
                });
            });
            
            function departmentScreenDetector(snap_data) {
                if(snap_data.dep_id !== "") {
                    $("#dep_monitor").fadeOut('medium', function() {
                        $("#dep_monitor").fadeIn('medium');
                    });
                    $("#dep_monitor").on('mouseover', function() { departmentScreenDetectorMouseOver(snap_data); } );
                } else {
                    $("#dep_monitor").hide();
                }
            }

            function departmentScreenDetectorMouseOver(snap_data) {
                if(snap_data.img_av_status) {
                    showSnap("<img src='" + snap_data['snap_path'] + "'>");
                } else {
                    showSnap("<p>Snapshot image not exists on server</p>");
                }
            }

            function standaloneDepartmentScreenDetector() {
                var dep_id = $("select[name='department'] > option:selected").val();
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

            function standaloneCatScreenDetector() {
                var cat_id = $("select#category_sites_frow > option:selected").val();
                $.post(base_url + 'index.php/system/scanForCatSnap', {'cat_id': cat_id}, function(data) {
                    if(data.cat_id !== "") {
                        $("#cat_monitor").fadeOut('medium', function() {
                            $("#cat_monitor").fadeIn('medium');
                        });
                        $("#cat_monitor").on('mouseover', function() { departmentScreenDetectorMouseOver(data); } );
                    } else {
                        $("#cat_monitor").hide();
                    }
                });
            }

            standaloneDepartmentScreenDetector();
            standaloneCatScreenDetector();
            
        </script>


        <div class="tab-pane active">
            <div class="info-message text-success"></div>
            <?php echo form_open("system/save_new_site", array("class"=>"form-horizontal", "id"=>"system_save_new_site"));?>
            <div class="span5">
                <div class="row-fluid">
                        <p>New site:</p>
                        <input type="text" id="new_site" name="new_site">
                        <button id="btn_new_site" class="btn btn-primary" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Add</button>
                        <div class="clear-fix"></div>
                </div>
                <div class="row-fluid mt_10">
                    <div class="aclis">
                        <?php
                            if(count($sites) > 0) { ?>
                                <div id="sites" class="btn-group hp_boot_drop mr_10">
                                    <button class="btn btn-danger btn_caret_sign" id="" onclick="return false;">[ Choose site ]</button>
                                    <button class="btn btn-danger dropdown-toggle" data-toggle="dropdown">
                                        <span class="caret"></span>
                                    </button>
                                    <ul class="dropdown-menu">
                                        <?php foreach($sites as $key => $value) { ?>
                                            <li><a data-item="<?php echo $key; ?>" data-value="<?php echo $key; ?>" href="javascript:void(0)"><span><?php echo $value; ?></span></a></li>
                                        <?php } ?>
                                    </ul>
                                </div>
                            <?php } ?>
                        <div class="clear-fix"></div>
                    </div>
                </div>
            </div>
            <div class="span6">
                <div class="row-fluid">
                        <p>Name:</p>
                        <input type="text" id="site_name" name="site_name">
                        <button id="update_site_info" class="btn btn-success" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Update</button>
                        <button id="delete_site" class="btn btn-danger" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Delete</button>
                        <div class="clear-fix"></div>
                </div>
                <div class="row-fluid mt_10">
                        <p>Url:</p>
                        <input type="text" id="site_url" name="site_url">
                        <div class="clear-fix"></div>
                </div>
                <div class="row-fluid">
                    <div class="controls span12 mt_20">
                        <img id="site_logo" class="mt_10" src="../../img/no-logo.jpg" />
                        <div class="clear-fix"></div><br />
                        <button class="btn btn-success" id="sitelogo" style="display:none"><i class="icon-white icon-ok"></i>&nbsp;Import</button>
								<span class="btn btn-success fileinput-button pull-left" style="">
									Upload
									<i class="icon-plus icon-white"></i>
									<input type="file" multiple="" name="files[]" id="fileupload">
								</span>
                        <div class="progress progress-success progress-striped span6" id="progress">
                            <div class="bar"></div>
                        </div>
                        <div id="files"></div>
                        <input type="hidden" name="sitelogo_file" />
                        <button id="delete_sitelogo" class="btn btn-danger ml_10" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Delete</button>
                    </div>
                    <div class="info ml_10 "></div>
                    <script>
                        $(function () {
                            var url = '<?php echo site_url('system/upload_img');?>';
                            $('#fileupload').fileupload({
                                url: url,
                                dataType: 'json',
                                done: function (e, data) {
                                    $('input[name="sitelogo_file"]').val(data.result.files[0].name);
                                    $.post(base_url + 'index.php/system/update_site_logo', {
                                        'id':  $("#sites .btn_caret_sign").attr('id'),
                                        'logo': $('input[name="sitelogo_file"]').val()
                                    }, function(data){

                                    });
                                    /*$.each(data.result.files, function (index, file) {
                                        if (file.error == undefined) {
                                         $('<p/>').text(file.name).appendTo('#files');
                                         }
                                    });*/
                                    $('button#sitelogo').trigger('click');
                                    $.post(base_url + 'index.php/system/get_site_info', {'site':  $("#sites .btn_caret_sign").attr('id')}, function(data){
                                        if(data.length > 0){
                                            if(data[0].name != ''){
                                                $('input#site_name').val(data[0].name);
                                            }else{
                                                $('input#site_name').val('');
                                            }
                                            if(data[0].url != ''){
                                                $('input#site_url').val(data[0].url);
                                            }else{
                                                $('input#site_url').val('');
                                            }
                                            if(data[0].image_url != ''){
                                                $('img#site_logo').attr({'src': base_url+'img/'+data[0].image_url });
                                            } else {
                                                $('img#site_logo').attr({'src': base_url+'img/no-logo.jpg' });
                                            }
                                        }
                                    });
                                },
                                progressall: function (e, data) {
                                    var progress = parseInt(data.loaded / data.total * 100, 10);
                                    $('#progress .bar').css(
                                        'width',
                                        progress + '%'
                                    );
                                    if (progress == 100) {

                                    }
                                }
                            });
                        });
                    </script>
                </div>
            </div>
            <div class="span12 mt_20 general ml_0">
                <div class="row-fluid">
                    <input type='hidden' name='update_mark' name='update_mark' value='4'>
                    <label>Department:</label>
                    <?php  echo form_dropdown('department', $departmens_list, null, 'class="inline_block lh_30 w_375 mb_reset" id="second_department"'); ?>
                    <img class='monitor_icon hidden' id='dep_monitor' src="<?php echo base_url() ?>/img/monitor.png">
                    <button class="btn btn-success" id="csv_import_create_batch" style="display:none"><i class="icon-white icon-ok"></i>&nbsp;Import</button>
								<span class="btn btn-success fileinput-button ml_10">
									Upload
									<i class="icon-plus icon-white"></i>
									<input type="file" multiple="" name="files[]" id="fileupload1">
								</span>
                    <div id="files1" style="float:left"></div>
                    <input type="hidden" name="choosen_file" />
                    <div class="info ml_10" style="float:left"></div>
                    <script>
                        //after upload, show deparnments for current site
                        function setDepartmentstCategories()
                        {
                            $.post(base_url + 'index.php/measure/getDepartmentsByCustomer', {'customer_name':  $("#sites .btn_caret_sign").text()}, function(data) {
                                $("select[name='department']").empty();
                                if(data.length > 0){
                                    for(var i=0; i<data.length; i++){
                                        $("select[name='department']").append("<option value='"+data[i].id+"'>"+data[i].text+"</option>");
                                    }
                                }
                            });
                            $.post(base_url + 'index.php/system/getCategoriesBySiteId', {'site_id': $("#sites .btn_caret_sign").attr('id'),
                                'department_id': $('select[name="department"]').find('option:selected').val()}, function(data) {
                                $("select[name='category']").empty();
                                if(data.length > 0 ){
                                    for(var i=0; i<data.length; i++){
                                        $("select[name='category']").append("<option value='"+data[i].id+"'>"+data[i].text+"</option>");
                                    }
                                }
                            });
                        }
                        $(function () {
                            var url = '<?php echo site_url('system/upload_departments_categories');?>';
                            $('#fileupload1').fileupload({
                                url: url,
                                dataType: 'json',
                                //add preloader
                                change: function(){$("#second_department").parent().prepend("<img id='preloader-dc' src='"+base_url+"/img/loader_scr.gif'/>");},
                                done: function (e, data) {
          
                                    $('input[name="choosen_file"]').val(data.result.files[0].name);

                                    var url = base_url+'index.php/system/save_departments_categories';
                                    $.post(
                                        url, 
                                        { 
                                            'choosen_file': $('input[name="choosen_file"]').val(),
                                            'site_id':  $("#sites .btn_caret_sign").attr('id'),
                                            'site_name':  $("#sites .btn_caret_sign").text()
                                        }, 
                                        function(data) {
                                            //console.log("fail");
                                        }
                                    ).fail( function(xhr, textStatus, errorThrown) {
                                        console.log(xhr);
                                        console.log(textStatus);
                                        console.log(errorThrown);
                                    }).done(function (e, data) {
                                        //setDepartmentstCategories();
                                        //remove preloader
                                       $("#preloader-dc").hide(2000,function(){
                                            //setDepartmentstCategories();
                                            $("#second_department").parent().prepend("<span style='color:red;'>The file is being processed. It will take time.</span>");
                                            $("#preloader-dc").remove();
                                       });
                                        
                                    }); 
                                }
                            });
                            
                            $('#modify_department').click(function(){
                                $.ajax({
                                    url: base_url + 'index.php/system/get_department',
                                    dataType : 'json',
                                    type : 'post',
                                    data : {
                                        id: $('#second_department').val()
                                    }
                                }).done(function(data){
                                    console.log(data);
                                    $("#modify_department_name").val(data[0].text);
                                    $("#modify_department_url").val(data[0].url);
                                    $("#modify_department_text").val(data[0].description_text);
                                    $("#modify_department_wc").val(data[0].description_words);
                                    $('#modify_department_dialog').dialog('open');
                                });
                                return false;
                            });
                            
                            $('#modify_department_dialog').dialog({
                                autoOpen: false,
                                resizable: false,
                                modal: true,
                                buttons: {
                                    'Save': function() {
                                        $.ajax({
                                            url: base_url + 'index.php/system/edit_department',
                                            dataType : 'json',
                                            type : 'post',
                                            data : {
                                                text : $("#modify_department_name").val(),
                                                url : $("#modify_department_url").val(),
                                                description_text : $("#modify_department_text").val(),
                                                description_words : $("#modify_department_wc").val(),
                                                id: $('#second_department').val()
                                            }
                                        }).done(function(){
                                            $('#second_department option:selected').text($("#modify_department_name").val());
                                        });
                                        $(this).dialog('close');
                                    },
                                    'Cancel': function() {
                                        $(this).dialog('close');
                                    }
                                },
                                width: '250px'
                            });
                        });
                    </script>

                    <button id="delete_department" class="btn btn-danger" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Delete</button>
                    <button class="btn btn-danger" onclick="doconfirm('departments');return false;"><i class="icon-white icon-ok"></i>&nbsp;Delete All</button>
                    <button id="department_snapshot" class="btn btn-success" disabled="disabled" ><i class="icon-white icon-ok"></i>&nbsp;Snapshot</button>
                    <span id="department_snapshot_process" style="width: 30px;height: 104px;display: none;font-weight: bold;" ></span>
                    <button id="add_snapshot_queue" style="height: 30px;" class="btn btn-success"><i class="icon-plus icon-white"></i></button>
                    <span id="department_loader" style="display: none;width: 40px;height: 30px;" ><img style="margin-left: 10px;" src="<?php echo base_url(); ?>webroot/img/ajax-loader.gif" /></span>
                    <button id="add_department" class="btn btn-success"><i class="icon-white icon-ok"></i>&nbsp;Add...</button>
                    <button id="modify_department" class="btn btn-success"><i class="icon-white icon-ok"></i>&nbsp;Modify...</button>
                </div>
                <div class="row-fluid mt_10">
                    <label>Categories:</label>
                    <?php echo form_dropdown('category', $category_list ); ?>
                    <?php if(count($category_list) > 0) { ?>
                        <select id='category_sites_frow' name='category'>
                        <?php foreach($category_list as $kc => $kv) { ?>
                            <option value="<?php echo $kv['id']; ?>"><?php echo $kv['text']; ?></option>
                        <?php } ?>
                        </select>
                    <?php } ?>
                    <img class='monitor_icon hidden mr10' id='cat_monitor' src="<?php echo base_url() ?>/img/monitor.png">
                    <button id="delete_category" class="btn btn-danger" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Delete</button>
                    <button id="delete_all_categories" class="btn btn-danger" onclick="doconfirm('categories');return false;"><i class="icon-white icon-ok"></i>&nbsp;Delete All</button>
                    <button id="category_snapshot" class="btn btn-success"><i class="icon-white icon-ok"></i>&nbsp;Snapshot</button>
                    <button id="add_category" class="btn btn-success"><i class="icon-white icon-ok"></i>&nbsp;Add...</button>
                </div>
            </div>
            <div class="span12 mt_20 mb_40 general ml_0">
                <div class="row-fluid">
                    <h5>Best Sellers</h5>
                    <label>Overall:</label>
                    <?php  echo form_dropdown('best_sellers', $best_sellers_list, null, 'class="inline_block lh_30 w_375 mb_reset"'); ?>
                    <span class="btn btn-success fileinput-button ml_10">Upload<i class="icon-plus icon-white"></i>
                        <input type="file" multiple="" name="files[]" id="overall_fileupload">
					</span>
                    <div id="overall_files" style="float:left"></div>
                    <input type="hidden" name="overall_choosen_file" />
                    <script>
                        $(function () {
                            var url = '<?php echo site_url('system/upload_departments_categories');?>';
                            $('#overall_fileupload').fileupload({
                                url: url,
                                dataType: 'json',
                                done: function (e, data) {
                                    $('input[name="overall_choosen_file"]').val(data.result.files[0].name);

                                    var url = base_url+'index.php/system/save_best_sellers';
                                    $.post(url, { 'overall_choosen_file': $('input[name="overall_choosen_file"]').val(),
                                        'site_id':  $("#sites .btn_caret_sign").attr('id'),
                                        'site_name':  $("#sites .btn_caret_sign").text()
                                    }, function(data) {
                                        $.post(base_url + 'index.php/measure/getDepartmentsByCustomer', {'customer_name':  $("#sites .btn_caret_sign").text()}, function(data) {
                                            $("select[name='department']").empty();
                                            if(data.length > 0){
                                                for(var i=0; i<data.length; i++){
                                                    $("select[name='department']").append("<option value='"+data[i].id+"'>"+data[i].text+"</option>");
                                                }
                                            }
                                        });
                                        $.post(base_url + 'index.php/system/getCategoriesBySiteId', {'site_id': $("#sites .btn_caret_sign").attr('id'),
                                            'department_id': $('select[name="department"]').find('option:selected').val()}, function(data) {
                                            $("select[name='category']").empty();
                                            if(data.length > 0 ){
                                                for(var i=0; i<data.length; i++){
                                                    $("select[name='category']").append("<option value='"+data[i].id+"'>"+data[i].text+"</option>");
                                                }
                                            }
                                        });
                                        $.post(base_url + 'index.php/system/getBestSellersBySiteId', {'site_id':  $("#sites .btn_caret_sign").attr('id')}, function(data) {
                                            $("select[name='best_sellers']").empty();
                                            if(data.length > 0 ){
                                                for(var i=0; i<data.length; i++){
                                                    $("select[name='best_sellers']").append("<option value='"+data[i].id+"'>"+data[i].page_title+"</option>");
                                                }
                                            }
                                        });
                                    }, 'json');
                                }
                            });
                        });
                    </script>
                    <button id="delete_overall" class="btn btn-danger"><i class="icon-white icon-ok"></i>&nbsp;Delete</button>
                    <button id="delete_all_overall" class="btn btn-danger" onclick="doconfirm('overall'); return false;"><i class="icon-white icon-ok"></i>&nbsp;Delete All</button>
                </div>
                <div class="row-fluid mt_10">
                    <label>Department:</label>
                    <?php  echo form_dropdown('department', $departmens_list, null, 'class="inline_block lh_30 w_375 mb_reset" id="first_department"'); ?>
                    <span class="btn btn-success fileinput-button ml_10">Upload<i class="icon-plus icon-white"></i>
                        <input type="file" multiple="" name="best_sellers_department_files[]" id="best_sellers_department_fileupload">
					</span>
                    <div id="best_sellers_department_files" style="float:left"></div>
                    <input type="hidden" name="best_sellers_department_choosen_file" />
                    <button id="delete_department" class="btn btn-danger" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Delete</button>
                    <button id="delete_all_departments" class="btn btn-danger" onclick="doconfirm('departments');return false;"><i class="icon-white icon-ok"></i>&nbsp;Delete All</button>
                </div>
                <div class="row-fluid mt_10">
                    <label>Categories:</label>
                    <?php echo form_dropdown('category', $category_list ); ?>
                    <span class="btn btn-success fileinput-button ml_10">Upload<i class="icon-plus icon-white"></i>
                        <input type="file" multiple="" name="best_sellers_category_files[]" id="best_sellers_category_fileupload">
					</span>
                    <div id="best_sellers_category_files" style="float:left"></div>
                    <input type="hidden" name="best_sellers_category_choosen_file" />
                    <button id="upload_categories_departments" class="btn btn-primary" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Upload</button>
                    <button id="delete_category" class="btn btn-danger" ><i class="icon-white icon-ok"></i>&nbsp;Delete</button>
                    <button id="delete_all_categories" class="btn btn-danger"  onclick="doconfirm('categories');return false;"><i class="icon-white icon-ok"></i>&nbsp;Delete All</button>
                </div>
            </div>
            <?php echo form_close();?>
        </div>
    </div>
</div>

<!-- MODALS (START) -->
<div class="modal hide fade ci_hp_modals" id='loading_crawl_snap_modal'>
    <div class="modal-body">
        <p><img src="<?php echo base_url();?>img/loader_scr.gif">&nbsp;&nbsp;&nbsp;Generating snapshot. Please wait...</p>
    </div>
</div>

<div class="modal hide fade ci_hp_modals" id='preview_crawl_snap_modal'>
    <div class="modal-body" style='overflow: hidden'>
        <div class='snap_holder'>&nbsp;</div>
    </div>
    <div class="modal-footer">
        <a href="javascript:void(0)" class="btn" data-dismiss="modal">Close</a>
    </div>
</div>
<!-- MODALS (END) -->

<script type="text/javascript">
    $(function() {
        $(".hp_boot_drop .dropdown-menu > li > a").bind('click', function(e) {
            var new_caret = $.trim($(this).text());
            $("#sites .btn_caret_sign").text(new_caret);
        });
    });
</script>

<div id="add_department_dialog" title="Add new department">
    <div>
        <form action="" method="post">
            <p>
                <label for="column_department">Department:</label>
                <input type="text" id="column_department" data-col_name="department" name="column_department" />
            </p>
            <p>
                <label for="column_url">URL:</label>
                <input type="text" id="column_department_url" data-col_name="url" name="column_url" />
            </p>
            <p>
                <label for="column_text">Text:</label>
                <textarea cols="10" rows="5" id="column_department_text" data-col_name="text" name="column_text"></textarea>
            </p>
            <p>
                <label for="column_wc">Word count:</label>
                <input type="text" id="column_department_wc" data-col_name="wc" name="column_wc" />
            </p>
        </form>
    </div>
</div>

<div id="modify_department_dialog" title="Modify department">
    <div>
        <form action="" method="post">
            <p>
                <label for="column_department">Department:</label>
                <input type="text" id="modify_department_name" data-col_name="department" name="modify_department" />
            </p>
            <p>
                <label for="column_url">URL:</label>
                <input type="text" id="modify_department_url" data-col_name="url" name="modify_url" />
            </p>
            <p>
                <label for="column_text">Text:</label>
                <textarea cols="10" rows="5" id="modify_department_text" data-col_name="text" name="modify_text"></textarea>
            </p>
            <p>
                <label for="column_wc">Word count:</label>
                <input type="text" id="modify_department_wc" data-col_name="wc" name="modify_wc" />
            </p>
        </form>
    </div>
</div>

<div id="add_category_dialog" title="Add new category">
    <div>
        <form action="" method="post">
            <p>
                <label for="column_category">Category:</label>
                <input type="text" id="column_category" data-col_name="category" name="column_category" />
            </p>
            <p>
                <label for="column_url">URL:</label>
                <input type="text" id="column_category_url" data-col_name="url" name="column_url" />
            </p>
            <p>
                <label for="column_text">Text:</label>
                <textarea cols="10" rows="5" id="column_category_text" data-col_name="text" name="column_text"></textarea>
            </p>
            <p>
                <label for="column_wc">Word count:</label>
                <input type="text" id="column_category_wc" data-col_name="wc" name="column_wc" />
            </p>
        </form>
    </div>
</div>



