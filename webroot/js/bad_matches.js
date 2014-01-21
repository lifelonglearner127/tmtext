var delUrl = '';
var readUrl = base_url + 'index.php/system/bad_matches_data';
var  tblMatches;
var delHref;
var columns = [
    {
        "sTitle": "Url1",
        "sName": "url1"
    },
    {
        "sTitle": "Url2",
        "sName": "url2",
        "sClass" : ""
    },
    {
        "sTitle": "Actions",
        "sName": "actions"
    }
];
$(document).ready(function() {
    read_couples();
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

    $('#delConfDialog1').dialog({
        autoOpen: false,
        buttons: {
            'No': function() {
                $(this).dialog('close');
            },
            'Yes': function() {
                //display ajax loader animation here...
//                $( '#ajaxLoadAni' ).fadeIn( 'slow' );
               
                var aaa = $.post( delHref, {}, 'json').done(function(data) {
                   
                });
                $(this).dialog('close');

            } //end Yes

        } //end buttons

    }); //end dialog
    
    $('#tblMatches').delegate('a.deleteBtn', 'click', function() {
        $('#delConfDialog1').dialog('open');
        delHref = $(this).attr('href');
        return false;

    }); //end delete delegate

}); //end document ready


function read_couples() {
    //display ajax loader animation
    $('#ajaxLoadAni').fadeIn('slow');

    tblMatches = $('#tblMatches').dataTable({
        "bJQueryUI": true,
//        "bDestroy": true,
        "bRetrieve":true,
        "sPaginationType": "full_numbers",
        "bProcessing": true,
        "bAutoWidth": false,
        "bServerSide": true,
        "aoColumns": columns,
        "sAjaxSource": readUrl,
//        "fnServerData": function(sSource, aoData, fnCallback) {
//            console.log('response');
//            $.getJSON(sSource, aoData, function(response) {
//                console.log(response);
//                fnCallback(response);
//                 $('#ajaxLoadAni').fadeOut('slow');
//// 
//
//            });
//          
//        },
        "fnRowCallback": function(nRow, aData, iDisplayIndex) {
                //                 $('#ajaxLoadAni').fadeOut('slow');

                return nRow;
                
            },
            "fnDrawCallback": function(oSettings) {
                                 $('#ajaxLoadAni').fadeOut('slow');
                            },

    });

}

