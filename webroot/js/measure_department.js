var readUrl   = base_url + 'index.php/measure/get_best_sellers',
    updateUrl = base_url + 'index.php/measure/',
    delUrl    = base_url + 'index.php/measure/',
    delHref,
    updateHref,
    updateId,
    delId;


$( function() {

    $( '#tabs' ).tabs({
        fx: { height: 'toggle', opacity: 'toggle' }
    });
    readBestSellers();
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
                        var title = $( 'tr#' + updateId + ' td' )[ 2 ];

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
                    type:'POST',
                    data:{'id': delId},
                    success: function( response ) {
                        //hide ajax loader animation here...
                        $( '#ajaxLoadAni' ).fadeOut( 'slow' );

                        //$( '#msgDialog > p' ).html( response );
                        //$( '#msgDialog' ).dialog( 'option', 'title', 'Success' ).dialog( 'open' );

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
        delId = $( this ).parents( 'tr' ).attr( "id" );
        $('span.batch_name').text($( 'tr#'+delId+' td:nth-child(3)' ).text());
        $( '#delConfDialog' ).dialog( 'open' );

        return false;

    }); //end delete delegate

}); //end document ready


function readBestSellers() {
    //display ajax loader animation
    $( '#ajaxLoadAni' ).fadeIn( 'slow' );

    $.ajax({
        url: readUrl,
        dataType: 'json',
        type: "POST",
        data:{ 'site': $(".btn_caret_sign").text() },
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