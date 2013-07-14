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
                        $('input#site_name').val($(this).text());
                        $.post(base_url + 'index.php/system/get_site_info', {'site': $(this).val()}, function(data){
                            if(data.length > 0){
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
                    $(".info-message").html(data.message);
                    $(".info-message").fadeOut(7000);
                });
                return false;
            });

            $('button#sitelogo').click(function(){
                $.post(base_url + 'index.php/system/update_site', {
                    'id': $('select#sites').find('option:selected').val(),
                    'logo': $('input[name="sitelogo_file"]').val()
                }, function(data){
                });
                return false;
            });

            $('select#sites').keypress(function(e){
                console.log(e.keyCode);

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
            <div class="span6 mb_40">
                <div class="row-fluid">
                        <p>Name:</p>
                        <input type="text" id="site_name" name="site_name">
                        <button id="update_site" class="btn btn-success" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Update</button>
                        <button id="delete_site" class="btn btn-danger" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Delete</button>
                        <div class="clear-fix"></div>
                </div>
                <div class="rdmin_tag_editorow-fluid mt_10">
                        <p>Url:</p>
                        <input type="text" id="site_url" name="site_url">
                        <div class="clear-fix"></div>
                </div>
                <div class="row-fluid">
                    <div clasdmin_tag_editors="controls span7 mt_20">
                        <img id="site_logo" class="mt_10" src="../../img/no-logo.jpg" />
                        <div class="clear-fix"></div><br />
                        <button class="btn btn-success" id="sitelogo" style="display:none"><i class="icon-white icon-ok"></i>&nbsp;Import</button>
								<span class="btn btn-success fileinput-button pull-left" style="">
									Upload
									<i class="icon-plus icon-white"></i>
									<input type="file" multiple="" name="files[]" id="fileupload">
								</span>
                        <div class="progress progress-success progress-striped span7" id="progress">
                            <div class="bar"></div>
                        </div>
                        <div id="files"></div>
                        <input type="hidden" name="sitelogo_file" />
                        <button id="delete_sitelogo" class="btn btn-danger pull-right" type="submit"><i class="icon-white icon-ok"></i>&nbsp;Delete</button>
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
                                    $.post(base_url + 'index.php/system/update_site', {
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
            <?php echo form_close();?>
        </div>
    </div>
</div>