<div class="tabbable">
    <ul class="nav nav-tabs jq-system-tabs">
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system');?>">General</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/sites_view');?>">Sites</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('site_crawler');?>">Site Crawler</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/batch_review');?>">Batch Review</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_compare');?>">Product Compare</a></li>
        <li class=""><a data-toggle="tab" href="<?php echo site_url('system/system_productsmatch');?>">Product Match</a></li>
        <li class="active"><a data-toggle="tab" href="<?php echo site_url('system/system_reports');?>">Reports</a></li>
    </ul>
    <div class="tab-content">
        <div id="tab9" class="tab-pane active">
            <div>
                Report Name
                <select id="system_reports" class="mt_10">
                </select>
                <button id="system_reports_delete" type="button" class="btn btn-danger">Delete</button>
                New:
                <input type="text" id="system_reports_new_txt" class="mt_10">
                <button id="system_reports_create" type="button" class="btn">Create</button>
            </div>
            <div class='tabbable'>
                <ul id='sub_reports_tabset' class="nav nav-tabs jq-system-tabs">
                    <li class="active"><a data-content="cover" href="javascript:void(0)">Cover Page</a></li>
                    <li><a data-content="recommendations" href="javascript:void(0)">Strategic Recommendations Page</a></li>
                    <li><a data-content="about" href="javascript:void(0)">About Content Analytics Page</a></li>
                </ul>
                <div class='tab-content' style='border-bottom: none;'>
                    <div id="tab1_r_tabset" class="tab-pane active">
                        Page Name:
                        <input type="text" id="system_reports_page_name" class="mt_5 mr_10">
                        Page:
                        <select id="system_reports_page_order" style="width: 120px;" class="mt_5 mr_10">
                            <option value="First">First</option>
                            <option value="Second">Second</option>
                            <option value="Second to Last">Second to Last</option>
                            <option value="Last">Last</option>
                        </select>
                        Layout:
                        <select id="system_reports_page_layout" style="width: 120px;" class="mt_5 mr_10">
                            <option value="Landscape">Landscape</option>
                            <option value="Portrait">Portrait</option>
                        </select>
                        <br />
                        <div id="system_reports_page_pnl_edit">
                            Replaced patterns: <b>#date#</b> - current data, <b>#customer name#</b> - customer name
                            <textarea id="system_reports_page_body" style="width: 100%;height: 500px;"></textarea>
                            <button id="system_reports_page_preview" type="button" class="btn btn-primary"><i class="icon-white icon-eye-open"></i>Preview</button>
                            <button id="system_reports_page_save" type="button" class="btn btn-success"><i class="icon-white icon-ok"></i>Save</button>
                        </div>
                        <div id="system_reports_page_pnl_preview">
                            <div id="system_reports_page_body_preview" style="border: 1px solid #CCCCCC"></div>
                            <button id="system_reports_page_edit" type="button" class="btn btn-primary"><i class="icon-white icon-pencil"></i>Edit</button>
                        </div>
                    </div>
                    <div id="tab2_r_tabset" class='tab-pane'>&nbsp;</div>
                    <div id="tab3_r_tabset" class='tab-pane'>&nbsp;</div>
                </div>
            </div>
        </div>
    </div>
</div>
<script type="text/javascript">
    $(function() {
        $('head').find('title').text('Reports');

        var system_reports = $('#system_reports');

        system_reports.change(function() {
            var id = system_reports.val();
            reports_get_by_id(id);
        });

        $("#sub_reports_tabset > li").on('click', function(e) {
            $("#sub_reports_tabset > li").removeClass('active');
            $("#sub_reports_tabset").siblings().find('.tab-pane').removeClass('active');
            $(this).addClass('active');
            $("#sub_reports_tabset").siblings().find('.tab-pane:eq(0)').addClass('active');
            var id = system_reports.val();
            var page = $(this).find('a').attr('data-content');
            reports_get_by_id(id, page);
        });

        $('#system_reports_delete').click(function() {
           if (confirm('Delete this report?')) {
               var id = system_reports.val();
               var data = {
                   'id' : id
               };
               $.post(base_url + 'index.php/system/system_reports_delete', data, function(data){
                   reports_get_all();
               });
           }
        });

        $('#system_reports_create').click(function() {
            var id = system_reports.val();
            var name = $('#system_reports_new_txt').val().trim();
            if (name.length == 0) {
                return;
            }
            var data = {
                'id' : id,
                'name' : name
            };
            $.post(base_url + 'index.php/system/system_reports_create', data, function(data){
                reports_get_all(data.id);
                $(this).val('');
            });
        });

        $('#system_reports_page_preview').click(function() {
            var html_body = $('#system_reports_page_body').val().trim();
            $('#system_reports_page_body_preview').html(html_body);
            $('#system_reports_page_pnl_preview').show();
            $('#system_reports_page_pnl_edit').hide();
        });

        $('#system_reports_page_edit').click(function() {
            $('#system_reports_page_pnl_preview').hide();
            $('#system_reports_page_pnl_edit').show();
            $('#system_reports_page_body').focus();
        });

        $('#system_reports_page_save').click(function() {
            var page = $("#sub_reports_tabset > li.active a").attr('data-content');
            var id = system_reports.val();
            var page_name = $('#system_reports_page_name').val().trim();
            var page_order = $('#system_reports_page_order').val();
            var page_layout = $('#system_reports_page_layout').val();
            var page_body = $('#system_reports_page_body').val().trim();
            if (page_body.length == 0) {
                return;
            }
            var page_page_name = page+'_page_name';
            var page_page_order = page+'_page_order';
            var page_page_layout = page+'_page_layout';
            var page_page_body = page+'_page_body';
            var data = {
                'id' : id
            };
            var params = {};
            params[page_page_name] = page_name;
            params[page_page_order] = page_order;
            params[page_page_layout] = page_layout;
            params[page_page_body] = page_body;
            data['params'] = JSON.stringify(params);
            $.post(base_url + 'index.php/system/system_reports_update', data, function(data){
            });
        });

        function reports_get_all(id_selected) {
            system_reports.empty();
            $.get(base_url + 'index.php/system/system_reports_get_all', {}, function(data){
                $.each(data.data, function(index, value){
                    system_reports.append('<option value="'+value.id+'">'+value.name+'</option>');
                });
                reports_get_by_id(system_reports.val());
            });
            if (id_selected) {
                $('#system_reports option:eq('+id_selected+')').prop('selected', true);
                reports_get_by_id(id_selected);
            }
        }

        function reports_get_by_id(id, page) {
            var data = {
                'id' : id,
                'page' : page
            };
            $.get(base_url + 'index.php/system/system_reports_get_options', data, function(data){
                var page_name = data.page_name;
                var page_order = data.page_order;
                var page_layout = data.page_layout;
                var page_body = data.page_body;
                $('#system_reports_page_name').val(page_name);
                $('#system_reports_page_order').val(page_order).prop('selected', true);
                $('#system_reports_page_layout').val(page_layout).prop('selected', true);
                $('#system_reports_page_body').val(page_body);
                $('#system_reports_page_body').focus();
            });
        }

        reports_get_all();
        $('#system_reports_page_pnl_preview').hide();
        $("#sub_pci_tabset > li:eq(0)").trigger('click');
    });
</script>