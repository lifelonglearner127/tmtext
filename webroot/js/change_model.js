var readUrl = base_url + 'index.php/system/get_custom_models',
updateUrl = base_url + 'index.php/system/update_custom_model',
delUrl = base_url + 'index.php/system/delete_custom_model',
delHref,
updateHref,
updateId,
delId,
row_id;
var tblModels;
var columns = [
    {
        "sTitle": "Product_name",
        "sName": "product_name"
    },
    {
        "sTitle": "Model",
        "sName": "model",
        "sClass" : "model"
    },
    {
        "sTitle": "Actions",
        "sName": "actions"
    }
];
$(document).ready(function() {
    read_models();
    $('#tabs').tabs({
        fx: {height: 'toggle', opacity: 'toggle'}
    });
    
    $('#msgDialog').dialog({
        autoOpen: false,
        buttons: {
            'Ok': function() {
                $(this).dialog('close');
            }
        }
    });

    $('#updateDialog1').dialog({
        autoOpen: false,
        buttons: {
            'Update': function() {
                var aaa = $.post(updateUrl, {model: $('#updateDialog1 input[name=title]').val(), imported_data_id: $('#updateDialog1 input[name=id]').val()}, 'json').done(function(data) {
                    console.log($('#'+row_id).closest('tr').find('.model').text());
                    $('#'+row_id).closest('tr').find('.model').text($('#updateDialog1 input[name=title]').val());

                });
                $(this).dialog('close');
//            console.log($( '#updateDialog1 input[name=title]' ).val());
//            console.log('second');
//            console.log($( '#updateDialog1 input[name=id]' ).val());
            },
            'Cancel': function() {
                $(this).dialog('close');
            }
        },
        width: '350px'
    }); //end update dialog

    $('#delConfDialog1').dialog({
        autoOpen: false,
        buttons: {
            'No': function() {
                $(this).dialog('close');
            },
            'Yes': function() {
                //display ajax loader animation here...
//                $( '#ajaxLoadAni' ).fadeIn( 'slow' );

                var aaa = $.post(delUrl, {imported_data_id: $('#delConfDialog1 input[name=del_im_id]').val()}, 'json').done(function(data) {
                    $('#'+row_id).closest('tr').find('.model').text('');
                });
                $(this).dialog('close');

            } //end Yes

        } //end buttons

    }); //end dialog

    $('#tblModels').delegate('a.updateBtn', 'click', function() {
        updateHref = $(this).attr('href');
        updateId = $(this).data('value');
        row_id = $(this).data('value');
        $('#updateDialog1 input[name=id]').val(updateId);
        $('#updateDialog1 input[name=title]').val($('#'+row_id).closest('tr').find('.model').text());
        
        $('#updateDialog1').dialog('open');
//            }
//        });

        return false;
    }); //end update delegate

    $('#tblModels').delegate('a.deleteBtn', 'click', function() {
        delHref = $(this).attr('href');
        delId = $(this).data('value');
        row_id = $(this).data('value');
        $('#delConfDialog1 input[name=del_im_id]').val(row_id);
        $('span.imported_data_id_').text($('#'+row_id).closest('tr').find('.model').text());
        $('#delConfDialog1').dialog('open');

        return false;

    }); //end delete delegate

}); //end document ready


function read_models() {
    //display ajax loader animation
    $('#ajaxLoadAni').fadeIn('slow');

    tblModels = $('#tblModels').dataTable({
        "bJQueryUI": true,
        "bDestroy": true,
        "sPaginationType": "full_numbers",
        "bProcessing": true,
       // "aaSorting": [[5, "desc"]],
        "bAutoWidth": false,
        "bServerSide": true,
        "aoColumns": columns,
        "sAjaxSource": readUrl,
        "fnServerData": function(sSource, aoData, fnCallback) {
            console.log('response');
            $.getJSON(sSource, aoData, function(response) {
                console.log(response);
                fnCallback(response);
                 $('#ajaxLoadAni').fadeOut('slow');
            });
          
        },
        "fnDrawCallback": function () {
            
              
        }

    });

}

