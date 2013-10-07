var readUrl   = base_url + 'index.php/system/get_custom_models',
    updateUrl = base_url + 'index.php/system/update_model',
    delUrl    = base_url + 'index.php/system/delete_model',
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
//                $( '#ajaxLoadAni' ).fadeIn( 'slow' );
//                $( this ).dialog( 'close' );
//
//                $.ajax({
//                    url: updateHref,
//                    type: 'POST',
//                    data: $( '#updateDialog1 form' ).serialize(),
//
//                    success: function( response ) {
//                        
//                    } //end success
//
//                }); //end ajax()
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
                $( '#ajaxLoadAni' ).fadeIn( 'slow' );
                $( this ).dialog( 'close' );

//                $.ajax({
//                    url: delHref,
//                    type:'POST',
//                    data:{'id': delId},
//                    success: function( response ) {
//                        //hide ajax loader animation here...
//                        $( '#ajaxLoadAni' ).fadeOut( 'slow' );
//
//                        //$( '#msgDialog > p' ).html( response );
//                        //$( '#msgDialog' ).dialog( 'option', 'title', 'Success' ).dialog( 'open' );
//
//                        $( 'a[href=' + delHref + ']' ).parents( 'tr' )
//                            .fadeOut( 'slow', function() {
//                                $( this ).remove();
//                            });
//
//                    } //end success
//                });

            } //end Yes

        } //end buttons

    }); //end dialog

    $( '#records' ).delegate( 'a.updateBtn', 'click', function() {
        updateHref = $( this ).attr( 'href' );
        updateId = $( this ).parents( 'tr' ).attr( "ipmorted_data_id" );

//        $( '#ajaxLoadAni' ).fadeIn( 'slow' );
//
//        $.ajax({
//            url: base_url + 'index.php/system/getBatchById/' + updateId,
//            dataType: 'json',
//
//            success: function( response ) {
//                
//                $( 'input#model' ).val( response[0].model );
//
//                $( '#ajaxLoadAni' ).fadeOut( 'slow' );
//
//                //--- assign id to hidden field ---
//                
                $( '#updateDialog1' ).dialog( 'open' );
//            }
//        });

        return false;
    }); //end update delegate

    $( '#records' ).delegate( 'a.deleteBtn', 'click', function() {
        delHref = $( this ).attr( 'href' );
        delId = $( this ).parents( 'tr' ).attr( "id" );
        $('span.batch_name').text($( 'tr#'+delId+' td:nth-child(3)' ).text());
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
           console.log(response);
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

