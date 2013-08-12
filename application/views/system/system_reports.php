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
            Report Name
            <select id="system_reports" class="mt_10">
            </select>
            <button id="system_reports_delete" type="button" class="btn btn-danger">Delete</button>
            New:
            <input type="text" id="system_reports_new_txt" class="mt_10">
            <button id="system_reports_create" type="button" class="btn">Create</button>
            <br />
            Cover page:<br />
            <div id="system_reports_pnl_edit">
                Replaced patterns: <b>#date#</b> - current data, <b>#customer name#</b> - customer name
                <textarea id="system_reports_body" style="width: 100%;height: 500px;"></textarea>
                <button id="system_reports_preview" type="button" class="btn btn-primary"><i class="icon-white icon-eye-open"></i>Preview</button>
                <button id="system_reports_save" type="button" class="btn btn-success"><i class="icon-white icon-ok"></i>Save</button>
            </div>
            <div id="system_reports_pnl_preview">
                <div id="system_reports_body_preview" style="border: 1px solid #CCCCCC"></div>
                <button id="system_reports_edit" type="button" class="btn btn-primary"><i class="icon-white icon-pencil"></i>Edit</button>
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

        $('#system_reports_preview').click(function() {
            var html_body = $('#system_reports_body').val().trim();
            console.log(html_body);
            $('#system_reports_body_preview').html(html_body);
            $('#system_reports_pnl_preview').show();
            $('#system_reports_pnl_edit').hide();
        });

        $('#system_reports_edit').click(function() {
            $('#system_reports_pnl_preview').hide();
            $('#system_reports_pnl_edit').show();
            $('#system_reports_body').focus();
        });

        $('#system_reports_save').click(function() {
            var id = system_reports.val();
            var body = $('#system_reports_body').val().trim();
            if (body.length == 0) {
                return;
            }
            var data = {
                'id' : id,
                'body' : body
            };
            $.post(base_url + 'index.php/system/system_reports_update', data, function(data){
                console.log(data);
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

        function reports_get_by_id(id) {
            var data = {
                'id' : id
            };
            $.get(base_url + 'index.php/system/system_reports_get_body', data, function(data){
                console.log(data.data);
                var body = data.data[0].body;
                $('#system_reports_body').val(body);
                $('#system_reports_body').focus();
            });
        }

        reports_get_all();
        $('#system_reports_pnl_preview').hide();
    });
</script>