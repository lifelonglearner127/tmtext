$(document).ready(function () {
    $(function () {
        'use strict';
        var url = base_url+'index.php/customer/upload_style';
        $('#styleupload').fileupload({
            url: url,
            dataType: 'json',
            done: function (e, data) {
                $.each(data.result.files, function (index, file) {
                    if (file.error == undefined) {
                        var customerName = $("select[name='customersStyle']").find('option:selected').text() ? $("select[name='customersStyle']").find('option:selected').text() : 0;
                        $.post(base_url + 'index.php/customer/getStyleByCustomer',{'customer_name':customerName}, function(data){
                            $("textarea[name='style_guide']").val(data);
                        });
                        $('#files').text(file.name);
                    }else{
                        $('#files').text(file.error);
                    }
                });
            },
            progressall: function (e, data) {
                var progress = parseInt(data.loaded / data.total * 100, 10);
                $('#progress .bar').css('width',progress + '%');
                if (progress == 100) {
                       //$('#progress .bar').css('display','none');
                    }
            }
        }).bind('fileuploadsubmit', function (e, data) {
                data.formData = {
                    'customerName':$("select[name='customersStyle']").find('option:selected').text()
                };
        });
    });
    
    
    var customer_name = $("select[name='customersStyle']").find("option:selected").text();
    if(customer_name!=='Select Customer'){
        $.post(base_url+'index.php/customer/getStyleByCustomer', { 'customer_name': customer_name}, function(data){
                $("textarea[name='style_guide']").val('');
                $("textarea[name='style_guide']").val(data);;
        });
    }
    
    
    if(customer_name=='Select Customer'){
            $("button[name='saveStyle']").attr("disabled", "disabled");
            $("input[type='file']").addClass('disabled');
            $("input[type='file']").attr("disabled", "disabled");
        }
    
    
    
    $("button[name='saveStyle']").click(function(){
       var txtcontent = $("textarea[name='style_guide']").val();
       var customerName = $("select[name='customersStyle']").find('option:selected').text() ? $("select[name='customersStyle']").find('option:selected').text() : 0;
       if(customerName!=='Select Customer'){
            $.post(base_url+'index.php/customer/saveTheStyle', { 'txtcontent': txtcontent, 'customerName':customerName}, function(data){
                $('#responseMess').text(data);
                setTimeout(function () { $('#responseMess').empty(); }, 2000);
            });
       }
    });
    
    $(document).on("change", 'select[name="customersStyle"]', function(){
        var customerName = $("select[name='customersStyle']").find('option:selected').text();
        if(customerName=='Select Customer'){
            $("button[name='saveStyle']").attr("disabled", "disabled");
            $("input[type='file']").addClass('disabled');
            $("input[type='file']").attr("disabled", "disabled");
        }else{
            $("button[name='saveStyle']").removeAttr("disabled");
            $("input[type='file']").removeClass('disabled');
            $("input[type='file']").removeAttr("disabled");
        }
    });
});

