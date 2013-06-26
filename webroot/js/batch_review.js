var readUrl   = base_url + 'index.php/system/get_batch_review',
    updateUrl = base_url + 'index.php/system/update_batch_review',
    delUrl    = base_url + 'index.php/system/delete_batch_review',
    delHref,
    updateHref,
    updateId;


$( function() {

    $( '#tabs' ).tabs({
        fx: { height: 'toggle', opacity: 'toggle' }
    });
    readBatchReview();
    $( '#msgDialog' ).dialog({
        autoOpen: false,

        buttons: {
            'Ok': function() {
                $( this ).dialog( 'close' );
            }
        }
    });

    $( '#updateDialog' ).dialog({
        autoOpen: false,
        buttons: {
            'Update': function() {
                $( '#ajaxLoadAni' ).fadeIn( 'slow' );
                $( this ).dialog( 'close' );

                $.ajax({
                    url: updateHref,
                    type: 'POST',
                    data: $( '#updateDialog form' ).serialize(),

                    success: function( response ) {
                        $( '#msgDialog > p' ).html( response );
                        $( '#msgDialog' ).dialog( 'option', 'title', 'Success' ).dialog( 'open' );

                        $( '#ajaxLoadAni' ).fadeOut( 'slow' );

                        //--- update row in table with new values ---
                        var title = $( 'tr#' + updateId + ' td' )[ 1 ];

                        $( title ).html( $( '#title' ).val() );

                        //--- clear form ---
                        $( '#updateDialog form input' ).val( '' );

                    } //end success

                }); //end ajax()
            },

            'Cancel': function() {
                $( this ).dialog( 'close' );
            }
        },
        width: '350px'
    }); //end update dialog

    $( '#delConfDialog' ).dialog({
        autoOpen: false,

        buttons: {
            'No': function() {
                $( this ).dialog( 'close' );
            },

            'Yes': function() {
                //display ajax loader animation here...
                $( '#ajaxLoadAni' ).fadeIn( 'slow' );

                $( this ).dialog( 'close' );

                $.ajax({
                    url: delHref,

                    success: function( response ) {
                        //hide ajax loader animation here...
                        $( '#ajaxLoadAni' ).fadeOut( 'slow' );

                        $( '#msgDialog > p' ).html( response );
                        $( '#msgDialog' ).dialog( 'option', 'title', 'Success' ).dialog( 'open' );

                        $( 'a[href=' + delHref + ']' ).parents( 'tr' )
                            .fadeOut( 'slow', function() {
                                $( this ).remove();
                            });

                    } //end success
                });

            } //end Yes

        } //end buttons

    }); //end dialog

    $( '#records' ).delegate( 'a.updateBtn', 'click', function() {
        updateHref = $( this ).attr( 'href' );
        updateId = $( this ).parents( 'tr' ).attr( "id" );

        $( '#ajaxLoadAni' ).fadeIn( 'slow' );

        $.ajax({
            url: base_url + 'index.php/system/getBatchById/' + updateId,
            dataType: 'json',

            success: function( response ) {
                console.log(response[0].title);
                $( 'input#title' ).val( response[0].title );

                $( '#ajaxLoadAni' ).fadeOut( 'slow' );

                //--- assign id to hidden field ---
                $( '#userId' ).val( updateId );

                $( '#updateDialog' ).dialog( 'open' );
            }
        });

        return false;
    }); //end update delegate

    $( '#records' ).delegate( 'a.deleteBtn', 'click', function() {
        delHref = $( this ).attr( 'href' );

        $( '#delConfDialog' ).dialog( 'open' );

        return false;

    }); //end delete delegate

}); //end document ready


function readBatchReview() {
    //display ajax loader animation
    $( '#ajaxLoadAni' ).fadeIn( 'slow' );

    $.ajax({
        url: readUrl,
        dataType: 'json',
        data:{},
        success: function( response ) {
            for( var i in response ) {
                response[ i ].updateLink = updateUrl + '/' + response[ i ].id;
                response[ i ].deleteLink = delUrl + '/' + response[ i ].id;
            }

            //clear old rows
            $( '#records > tbody' ).html( '' );

            //append new rows
            $( '#readTemplate' ).render( response ).appendTo( "#records > tbody" );

            //apply dataTable to #records table and save its object in dataTable variable
            if( typeof dataTable == 'undefined' )
                dataTable = $( '#records' ).dataTable({"bJQueryUI": true});

            //hide ajax loader animation here...
            $( '#ajaxLoadAni' ).fadeOut( 'slow' );
        }
    });
}