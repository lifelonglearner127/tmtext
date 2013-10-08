var readUrl   = base_url + 'index.php/system/get_custom_models',
    updateUrl = base_url + 'index.php/system/update_custom_model',
    delUrl    = base_url + 'index.php/system/delete_custom_model',
    delHref,
    updateHref,
    updateId,
    delId;


$( function() {

    $( '#tabs' ).tabs({
        fx: { height: 'toggle', opacity: 'toggle' }
    });
    read_models();
    $( '#msgDialog' ).dialog({
        autoOpen: false,

        buttons: {
            'Ok': function() {
                $( this ).dialog( 'close' );
            }
        }
    });

    $( '#updateDialog1' ).dialog({
        autoOpen: false,
                
        buttons: {
            'Update': function() {
             var aaa = $.post(updateUrl, {model: $( '#updateDialog1 input[name=title]' ).val(), imported_data_id: $( '#updateDialog1 input[name=id]' ).val()}, 'json').done(function(data) {
             delId=$( '#updateDialog1 input[name=id]' ).val();
             $( 'tr#'+delId+' td:nth-child(3)' ).text($( '#updateDialog1 input[name=title]' ).val());
            
        });
         $( this ).dialog( 'close' );
//            console.log($( '#updateDialog1 input[name=title]' ).val());
//            console.log('second');
//            console.log($( '#updateDialog1 input[name=id]' ).val());
            },

            'Cancel': function() {
                $( this ).dialog( 'close' );
            }
        },
        width: '350px'
    }); //end update dialog

    $( '#delConfDialog1' ).dialog({
        autoOpen: false,

        buttons: {
            'No': function() {
                $( this ).dialog( 'close' );
            },

            'Yes': function() {
                //display ajax loader animation here...
//                $( '#ajaxLoadAni' ).fadeIn( 'slow' );
               
                var aaa = $.post(delUrl, {imported_data_id: $('#delConfDialog1 input[name=del_im_id]').val()}, 'json').done(function(data) {
                 $( 'tr#'+delId+' td:nth-child(3)' ).text('');
        });
        $( this ).dialog( 'close' );

            } //end Yes

        } //end buttons

    }); //end dialog

    $( '#records' ).delegate( 'a.updateBtn', 'click', function() {
        updateHref = $( this ).attr( 'href' );
        updateId = $( this ).parents( 'tr' ).attr( "id" );
        
        $( '#updateDialog1 input[name=id]' ).val(updateId);

                $( '#updateDialog1' ).dialog( 'open' );
//            }
//        });

        return false;
    }); //end update delegate

    $( '#records' ).delegate( 'a.deleteBtn', 'click', function() {
        delHref = $( this ).attr( 'href' );
        delId = $( this ).parents( 'tr' ).attr( "id" );
        
        $('#delConfDialog1 input[name=del_im_id]').val(delId);
        $('span.imported_data_id_').text($( 'tr#'+delId+' td:nth-child(3)' ).text());
        $( '#delConfDialog1' ).dialog( 'open' );

        return false;

    }); //end delete delegate

}); //end document ready


function read_models() {
    //display ajax loader animation
    $( '#ajaxLoadAni' ).fadeIn( 'slow' );

    $.ajax({
        url: readUrl,
        dataType: 'json',
        data:{},
        success: function( response ) {
           
            for( var i in response ) {
                response[ i ].updateLink = updateUrl + '/' + response[ i ].imported_data_id;
                response[ i ].deleteLink = delUrl + '/' + response[ i ].imported_data_id;
            }

            //clear old rows
            $( '#records > tbody' ).html( '' );

            //append new rows
            $( '#readTemplate1' ).render( response ).appendTo( "#records > tbody" );

            //apply dataTable to #records table and save its object in dataTable variable
            //if( typeof dataTable == 'undefined' )
               dataTable = $( '#records' ).dataTable({"bJQueryUI": true,"bPaginate": true, "aaSorting": [[ 10, "desc" ]], 'bRetrieve':true});

            //hide ajax loader animation here...
            $( '#ajaxLoadAni' ).fadeOut( 'slow' );
        }
    });
}

