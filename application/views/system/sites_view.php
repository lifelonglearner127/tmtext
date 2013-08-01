<div class="tabbable">
    <ul class="nav nav-tabs jq-system-tabs">
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system');?>">General</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_compare');?>">Product Compare Interface</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('site_crawler');?>">Site Crawler</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/batch_review');?>">Batch Review</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_productsmatch');?>">Product Match</a></li>
        <li class="active"><a data-toggle="tab" href="<?php echo site_url('system/sites_view');?>">Sites</a></li>
    </ul>
    <div class="tab-content">
        <script type="text/javascript">
            function selectOption(){
                $('#sites option').click(function(){
                        $.post(base_url + 'index.php/system/get_site_info', {'site': $(this).val()}, function(data){
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
                    $.post(base_url + 'index.php/measure/getDepartmentsByCustomer', {'customer_name': $(this).text()}, function(data) {
                        $("select[name='department']").empty();
                        if(data.length > 0){
                            for(var i=0; i<data.length; i++){
                                $("select[name='department']").append("<option value='"+data[i].id+"'>"+data[i].text+"</option>");
                            }
                        }
                    });
                    $.post(base_url + 'index.php/system/getCategoriesBySiteId', {'site_id': $(this).val()}, function(data) {
                        $("select[name='category']").empty();
                        if(data.length > 0 ){
                            for(var i=0; i<data.length; i++){
                                $("select[name='category']").append("<option value='"+data[i].id+"'>"+data[i].text+"</option>");
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
                        $("#sites").append("<option value='"+data.id+"'>"+$('#new_site').val()+"</option>");
                        selectOption();
                        $('#new_site').val('');
                    });

                }
                return false;
            });

            $('button#delete_site').click(function(){
                $.post(base_url + 'index.php/system/delete_site', {'site': $('select#sites').find('option:selected').val()}, function(data){
                    $('select#sites').find('option:selected').remove();
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
                    'id': $('select#sites').find('option:selected').val(),
                    'logo': $('input[name="sitelogo_file"]').val()
                }, function(data){
                });
                return false;
            });

            $('button#update_site_info').click(function(){
                $.post(base_url + 'index.php/system/update_site_info', {
                    'id': $('select#sites').find('option:selected').val(),
                    'logo': $('input[name="sitelogo_file"]').val(),
                    'site_name': $('input[name="site_name"]').val(),
                    'site_url': $('input[name="site_url"]').val()
                }, function(data){
                    $('select#sites').find('option:selected').text($('input[name="site_name"]').val());
                });
                return false;
            });

            $('button#delete_sitelogo').click(function(){
                $.post(base_url + 'index.php/system/delete_sitelogo', {
                    'id': $('select#sites').find('option:selected').val(),
                    'logo': 'no-logo.jpg'
                }, function(data){
                    $('img#site_logo').attr({'src': base_url+'img/no-logo.jpg' });
                });
                return false;
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
                    <div class="aclist">
                        <p>Sites:</p>
                        <select id="sites" data-placeholder="Click to select sites" multiple name="sites[]">
                            <?php
                            foreach ($sites as $key => $value) {
                                print '<option value="'.$key.'">'.$value.'</option>';
                            }
                            ?>
                        </select>
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
                                        'id': $('select#sites').find('option:selected').val(),
                                        'logo': $('input[name="sitelogo_file"]').val()
                                    }, function(data){

                                    });
                                    /*$.each(data.result.files, function (index, file) {
                                        if (file.error == undefined) {
                                         $('<p/>').text(file.name).appendTo('#files');
                                         }
                                    });*/
                                    $('button#sitelogo').trigger('click');
                                    $.post(base_url + 'index.php/system/get_site_info', {'site': $('select#sites').find('option:selected').val()}, function(data){
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
                    <label>Department:</label>
                    <?php  echo form_dropdown('department', $departmens_list, null, 'class="inline_block lh_30 w_375 mb_reset"'); ?>
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
                        $(function () {
                            var url = '<?php echo site_url('system/upload_departments_categories');?>';
                            $('#fileupload1').fileupload({
                                url: url,
                                dataType: 'json',
                                done: function (e, data) {
                                    $('input[name="choosen_file"]').val(data.result.files[0].name);

                                    var url = base_url+'index.php/system/save_departments_categories';
                                    $.post(url, { 'choosen_file': $('input[name="choosen_file"]').val(),
                                            'site_id': $('select#sites').find('option:selected').val(),
                                            'site_name': $('select#sites').find('option:selected').text()
                                        }, function(data) {
                                            //$('<p/>').text(data.message).appendTo('#files1');
                                    }, 'json');
                                }
                            });
                        });
                    </script>

                    <button id="delete_department" class="btn btn-danger" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Delete</button>
                    <button id="delete_all_departments" class="btn btn-danger" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Delete All</button>
                </div>
                <div class="row-fluid mt_10">
                    <label>Categories:</label>
                    <?php echo form_dropdown('category', $category_list ); ?>
                    <button id="delete_category" class="btn btn-danger" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Delete</button>
                    <button id="delete_all_categories" class="btn btn-danger" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Delete All</button>
                </div>
            </div>
            <div class="span12 mt_20 mb_40 general ml_0">
                <div class="row-fluid">
                    <h5>Best Sellers</h5>
                    <label>Overall:</label>
                    <?php  echo form_dropdown('department', $departmens_list, null, 'class="inline_block lh_30 w_375 mb_reset"'); ?>
                    <button id="upload_categories_departments" class="btn btn-primary" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Upload</button>
                    <button id="delete_department_categories" class="btn btn-danger" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Delete</button>
                    <button id="delete_all_departments_categories" class="btn btn-danger" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Delete All</button>
                </div>
                <div class="row-fluid mt_10">
                    <label>Department:</label>
                    <?php  echo form_dropdown('department', $departmens_list, null, 'class="inline_block lh_30 w_375 mb_reset"'); ?>
                    <button id="upload_categories_departments" class="btn btn-primary" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Upload</button>
                    <button id="delete_department" class="btn btn-danger" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Delete</button>
                    <button id="delete_all_departments" class="btn btn-danger" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Delete All</button>
                </div>
                <div class="row-fluid mt_10">
                    <label>Categories:</label>
                    <?php echo form_dropdown('category', $category_list ); ?>
                    <button id="upload_categories_departments" class="btn btn-primary" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Upload</button>
                    <button id="delete_category" class="btn btn-danger" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Delete</button>
                    <button id="delete_all_categories" class="btn btn-danger" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Delete All</button>
                </div>
            </div>
            <?php echo form_close();?>
        </div>
    </div>
</div>