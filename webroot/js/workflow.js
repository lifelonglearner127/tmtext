$(document).ready(function() {
    $('#operations').hide();
    $('#processes').hide();
    $("#import_file_name").hide();
    var all_processes_url = base_url + 'index.php/workflow/get_processes';
    var all_operations_url = base_url + 'index.php/workflow/get_operations';
    var update_op = base_url + 'index.php/workflow/update_operation';

    $.ajax({
        url: all_operations_url,
        type: 'POST',
        success: function(data) {
            $.each($.parseJSON(data), function(index, val) {
                $("#sel_op").append("<option  value='" + val.id + "'>" + val.func_title + "</option>");
                $("#actions").append("<option  value='" + val.id + "'>" + val.func_title + "</option>");
            });
        }
    });

    $("#sel_op").change(function() {
        var sel_op_id = $(this).val();
        $.ajax({
            url: all_operations_url,
            type: 'POST',
            data: {id: sel_op_id},
            success: function(data) {
                data = $.parseJSON(data);
                  $("#opr_title").val(data[0].func_title);
                  $("#opr_url").val(data[0].func_url);
            }
        });
    });
    $.ajax({
        url: all_processes_url,
        type: 'POST',
        success: function(data) {
            $.each($.parseJSON(data), function(index, val) {
                $("#processes_list").append("<option selected ='selected' value='" + val.id + "'>" + val.process_name + "</option>");
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
        var param_type = $.trim($("#param_type").val());
        if(param_type == 0){
            alert('Please select parameter type');
            return false;
        }
        
        if (op_name !== '' && op_url !== '' && param_type != 0) {
            var url = base_url + 'index.php/workflow/add_operation';

            $.ajax({
                url: url,
                type: 'POST',
                data: {op_name: op_name, op_url: op_url, param_type: param_type},
                success: function(data) {
                    $("#sel_op").append("<option selected ='selected' value='" + data + "'>" + op_name + "</option>");
                    $("#actions").append("<option value='" + data + "'>" + op_name + "</option>");

                }
            });
        }

    });
    $("#update_op").click(function(e) {
        e.preventDefault();
        var oper_id  = $("#sel_op").val();
        var op_name = $("#opr_title").val();
        var op_url = $("#opr_url").val();
        if (op_name !== '' && op_url !== '') {
            $.ajax({
                url: update_op,
                type: 'POST',
                data: {op_name: op_name, op_url: op_url, id: oper_id},
                success: function(data) {
                    $('#sel_op').find('option[value="'+oper_id+'"]').text(op_name);
                }
            });
        }

    });
    $("#delete_op").click(function(e) {
        e.preventDefault();
        if ($("#sel_op").val() !== 0) {
            var op_id = $("#sel_op").val();
            url = base_url + 'index.php/workflow/delete_operation';
            if (op_id) {
                $.ajax({
                    url: url,
                    type: 'POST',
                    data: {id: op_id},
                    success: function(data) {
                        $("#sel_op").find('option[value="' + op_id + '"]').remove();
                        $("#actions").find('option[value="' + op_id + '"]').remove();
                        $("#opr_title").val("");
                        $("#opr_url").val("");
                    }
                });
            }
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
        var day = $.trim($("#days").val());
        var ops = $.trim($("#actions").val());
        var url_import_file = $.trim($("#import_file_name").val());
        var batches = $.trim($("#workflow_batches").val());
        if (ops !== null && day !== 0 && !($("#actions").find('option[value = "2"]:selected').val() !== undefined && url_import_file == 0) && process_name != '') {
            var url = base_url + 'index.php/workflow/add_prc';
            $.ajax({
                url: url,
                type: 'POST',
                data: {process_name: process_name, day: day, ops: ops, url_import_file: url_import_file, batches: batches},
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
        var selected_actions = $("#actions").val();
        var process_name = $("#processes_list").val();
        var day = $("#days").val();
        var batches = $("#workflow_batches").val();
        var import_file_name = $("#import_file_name").val();
        if (selected_actions !== null && day !== 0 && !($("#actions").find('option[value = "2"]:selected').val() !== undefined && import_file_name == 0) && process_name != '') {

        }

    });
    $("#delete_process").click(function() {
        if ($("#processes_list").val() !== 0) {
            var op_id = $("#processes_list").val();
            e.preventDefault();
            url = base_url + 'index.php/workflow/delete_prc';
            if (op_id) {
                $.ajax({
                    url: url,
                    type: 'POST',
                    data: {id: op_id},
                    success: function(data) {
                        $(this).find('option[value="' + op_id + '"]').remove();

                    }
                });
            }

        }
    });

});
//processes end