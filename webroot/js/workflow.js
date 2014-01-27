 $(document).ready(function() {
        $('#operations').hide();
        $('#processes').hide();
        $("#import_file_name").hide();
        var all_processes_url = base_url + 'index.php/workflow/get_processes';
        var all_operations_url = base_url + 'index.php/workflow/get_operations';

            $.ajax({
                url: all_operations_url,
                type: 'POST',
                success: function(data) {
                    $.each($.parseJSON(data),function(index, val) {
                        $("#sel_op").append("<option selected ='selected' value='" + val.id + "'>" + val.func_title+ "</option>");
                    });
                }
            });
            $.ajax({
                url: all_processes_url,
                type: 'POST',
                success: function(data) {
                    $.each($.parseJSON(data),function(index, val) {
                        $("#processes_list").append("<option selected ='selected' value='" + val.id + "'>" + val.process_name+ "</option>");
                    });
                }
            });
//operations start        
        $('#open_operation').toggle(
                function() {
                    $(this).text('Close Operations');
                    $('#operations').show();
                },
                function() {
                    $(this).text('Open Operations');
                    $('#operations').hide();
                }
        );
        $('#open_processes').toggle(
                function() {
                    $(this).text('Close Processes');
                    $('#processes').show();
                },
                function() {
                    $(this).text('Open Processes');
                    $('#processes').hide();
                }
        );

        $("#create_operation").click(function() {
            var op_name = $.trim($("#opr_title").val());
            var op_url = $.trim($("#opr_url").val());
            if (op_name !== '' && op_url !== '') {
                var url = base_url + 'index.php/workflow/add_operation';

                $.ajax({
                    url: url,
                    type: 'POST',
                    data: {op_name: op_name, op_url: op_url},
                    success: function(data) {
                        $("#sel_op").append("<option selected ='selected' value='" + data + "'>" + op_name + "</option>");
                    }
                });
            }

        });
        $("#update_op").click(function() {
            var op_name = $("#opr_title").val();
            var op_url = $("#opr_url").val();
            if (op_name !== '' && op_url !== '') {

            }

        });
        $("#delete_op").click(function() {
            if ($("#sel_op").val() !== 0) {
                var op_id = $("#sel_op").val();
            }
        });
        //operations end 
        //processes start  
        if ($("#actions").find('option[value = "2"]:selected').val() !== undefined) {
            $("#import_file_name").show();
        }
        else {
            $("#import_file_name").hide();
        }
        $("#create_process").click(function() {
            var process_name = $.trim($("#process_name").val());
            var day =$.trim($("#days").val());
            var ops = $.trim($("#actions").val());
            var url_import_file = $.trim($("#import_file_name").val());
            var batches = $.trim( $("#workflow_batches").val());
            if (true) {
                var url = base_url + 'index.php/workflow/add_process';

                $.ajax({
                    url: url,
                    type: 'POST',
                    data: {process_name: process_name, day: day,ops: ops, url_import_file: url_import_file,batches: batches  },
                    success: function(data) {
                        $("#processes_list").append("<option selected ='selected' value='" + data + "'>" + process_name + "</option>");
                    }
                });

            }
        });

        $("#actions").live('click', function() {
            if ($(this).find('option[value = "2"]:selected').val() !== undefined) {
                $("#import_file_name").show();
            }
            else {
                $("#import_file_name").hide();
            }

        });
        $("#update_process").click(function() {
            var op_name = $("#opr_title").val();
            var op_url = $("#opr_url").val();
            if (op_name !== '' && op_url !== '') {

            }

        });
        $("#delete_process").click(function() {
            if ($("#sel_op").val() !== 0) {
                var op_id = $("#sel_op").val();
            }
        });

    });
    //processes end