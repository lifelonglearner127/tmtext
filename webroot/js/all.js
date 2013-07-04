var readUrl   = base_url + 'index.php/research/get_research_info',
    updateUrl = base_url + 'index.php/research/update_research_info',
    delUrl    = base_url + 'index.php/research/delete_research_info',
    delHref,
    updateHref,
    updateId;


$( function() {

    $( '#tabs' ).tabs({
        fx: { height: 'toggle', opacity: 'toggle' }
    });
    readResearchData();
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
            'Update & Next':
                function() {
                    $( '#ajaxLoadAni' ).fadeIn( 'slow' );
                    $( this ).dialog( 'close' );

                    $.ajax({
                        url: updateHref,
                        type: 'POST',
                        data: $( '#updateDialog form' ).serialize(),

                        success: function( response ) {
                            $( '#msgDialog > p' ).html( response );

//                            $( '#msgDialog' ).dialog( 'option', 'title', 'Success' ).dialog( 'open' );

                            $( '#ajaxLoadAni' ).fadeOut( 'slow' );

                            //--- update row in table with new values ---
                            var productname = $( 'tr#' + updateId + ' td' )[ 1 ];
                            var url = $( 'tr#' + updateId + ' td' )[ 2 ];
                            var short_description = $( 'tr#' + updateId + ' td' )[ 3];
                            var long_description = $( 'tr#' + updateId + ' td' )[ 4 ];

                            $( productname ).html( $( '#product_name' ).val() );
                            $( url ).html( $( '#url' ).val() );
                            $( short_description ).html( $( '#short_description' ).val() );
                            $( long_description ).html( $( '#long_description' ).val() );

                            //--- clear form ---
                            $( '#updateDialog form input' ).val( '' );

                            updateNextDialog(updateId);

                        } //end success

                    }); //end ajax()
                },

            'Update':
                function() {
                    $( '#ajaxLoadAni' ).fadeIn( 'slow' );
                    $( this ).dialog( 'close' );

                    $.ajax({
                        url: updateHref,
                        type: 'POST',
                        data: $( '#updateDialog form' ).serialize(),

                        success: function( response ) {
                            $( '#msgDialog > p' ).html( response );

//                            $( '#msgDialog' ).dialog( 'option', 'title', 'Success' ).dialog( 'open' );

                            $( '#ajaxLoadAni' ).fadeOut( 'slow' );

                            //--- update row in table with new values ---
                            var productname = $( 'tr#' + updateId + ' td' )[ 1 ];
                            var url = $( 'tr#' + updateId + ' td' )[ 2 ];
                            var short_description = $( 'tr#' + updateId + ' td' )[ 3];
                            var long_description = $( 'tr#' + updateId + ' td' )[ 4 ];

                            $( productname ).html( $( '#product_name' ).val() );
                            $( url ).html( $( '#url' ).val() );
                            $( short_description ).html( $( '#short_description' ).val() );
                            $( long_description ).html( $( '#long_description' ).val() );

                            //--- clear form ---
                            $( '#updateDialog form input' ).val( '' );

                        } //end success

                    }); //end ajax()
            },

            'Cancel': function() {
                $( this ).dialog( 'close' );
            }
        },
        width: '600px'
    });

    //end update dialog

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
            url: base_url + 'index.php/research/getById/' + updateId,
            dataType: 'json',

            success: function( response ) {
                $( '#product_name' ).val( response[0].product_name );
                $( '#url' ).val( response[0].url );
                $( '#short_description' ).val( response[0].short_description );
                $( '#short_description_wc' ).val( response[0].short_description_wc );
                $( '#long_description' ).val( response[0].long_description);
                $( '#long_description_wc' ).val( response[0].long_description_wc);

                $( '#ajaxLoadAni' ).fadeOut( 'slow' );

                //--- assign id to hidden field ---
                $( '#userId' ).val( updateId );

                $( '#updateDialog' ).dialog( 'open' );
                $("#updateDialog").parent().find("div.ui-dialog-buttonpane button").not(":eq(2)").addClass("researchReviewUpdate");
            }
        });

        return false;
    }); //end update delegate

    $( '#records' ).delegate( 'a.deleteBtn', 'click', function() {
        delHref = $( this ).attr( 'href' );

        $( '#delConfDialog' ).dialog( 'open' );

        return false;

    }); //end delete delegate

    function updateNextDialog(updateId) {
        // Click on next btn update for update
        $("tr#" + updateId).next().find("a.updateBtn").click();

    }

    // choice column dialog
    $( '#choiceColumnDialog' ).dialog({
        autoOpen: false,

        buttons: {
            'Save': function() {
                // get columns params
                var columns = {
                    editor : $("#column_editor").attr('checked'),
                    product_name : $("#column_product_name").attr('checked'),
                    url : $("#column_url").attr('checked'),
                    short_description : $("#column_short_description").attr('checked'),
                    short_description_wc : $("#column_short_description_wc").attr('checked'),
                    long_description : $("#column_long_description").attr('checked'),
                    long_description_wc : $("#column_long_description_wc").attr('checked'),
                    actions : $("#column_actions").attr('checked')
                };

                // save params to DB
                $.ajax({
                    url: base_url + 'index.php/settings/save_columns_state/',
                    dataType: 'json',
                    type : 'post',
                    data : {
                        key : 'research_review',
                        value : columns
                    },
                    success: function( data ) {
                        if(data == true) {
                            dataTable.fnDestroy();
                            dataTable = undefined;
                            readResearchData();
                        }
                    }
                });

                $(this).dialog('close');
            },
            'Cancel': function() {
                $(this).dialog('close');
            }
        },
        width: '180px'
    });

    $( document ).delegate( '#research_batches_columns', 'click', function() {
        $( '#choiceColumnDialog' ).dialog( 'open' );
        $('#choiceColumnDialog').parent().find('button:first').addClass("popupGreen");
    });


    // --- Create Record with Validation ---
    /*$( '#create form' ).validate({
        rules: {
            cName: { required: true },
            cEmail: { required: true, email: true }
        },

        /*
        //uncomment this block of code if you want to display custom messages
        messages: {
            cName: { required: "Name is required." },
            cEmail: {
                required: "Email is required.",
                email: "Please enter valid email address."
            }
        },
        /

        submitHandler: function( form ) {
            $( '#ajaxLoadAni' ).fadeIn( 'slow' );

            $.ajax({
                url: 'index.php/home/create',
                type: 'POST',
                data: $( form ).serialize(),

                success: function( response ) {
                    $( '#msgDialog > p' ).html( 'New user created successfully!' );
                    $( '#msgDialog' ).dialog( 'option', 'title', 'Success' ).dialog( 'open' );

                    //clear all input fields in create form
                    $( 'input', this ).val( '' );

                    //refresh list of users by reading it
                    dataTable.fnAddData([
                        response,
                        $( '#cName' ).val(),
                        $( '#cEmail' ).val(),
                        '<a class="updateBtn" href="' + updateUrl + '/' + response + '">Update</a> | <a class="deleteBtn" href="' + delUrl + '/' + response + '">Delete</a>'
                    ]);

                    //open Read tab
                    $( '#tabs' ).tabs( 'select', 0 );

                    $( '#ajaxLoadAni' ).fadeOut( 'slow' );
                }
            });

            return false;
        }
    });*/

}); //end document ready

function readResearchData() {
    //display ajax loader animation
    $( '#ajaxLoadAni' ).fadeIn( 'slow' );

    $.ajax({
        url: readUrl,
        dataType: 'json',
        data:{ 'search_text': $('input[name="research_batches_text"]').val() },
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
            if( typeof dataTable == 'undefined' ){
                dataTable = $( '#records' ).dataTable({"bJQueryUI": true, "bDestroy": true,
                    "oLanguage": {
                        "sInfo": "Showing _START_ to _END_ of _TOTAL_ records",
                        "sInfoEmpty": "Showing 0 to 0 of 0 records",
                        "sInfoFiltered": "",
                    },
                    "aoColumns": [
                         null, null, null, null, null, null, null, null, null
                    ]
                });
            }

            dataTable.fnFilter( $('select[name="research_batches"]').find('option:selected').text(), 5);

            // get visible columns status
            var columns_checkboxes = $('#choiceColumnDialog input[type=checkbox]');

//            console.log(columns_checkboxes);
            $(columns_checkboxes).each(function(i) {
                if(i >= 7) {  // for Batch Name column
                    i++;
                }
//                console.log("i = " + i + " value = " + $(this).attr('checked'));
                if($(this).attr('checked') == true) {
                    dataTable.fnSetColumnVis( i, true, true );
                } else {
                    dataTable.fnSetColumnVis( i, false, true );
                }
            });



//            var column_editor = $('#column_editor').attr('checked');
//            var column_editor = $('#column_editor').attr('checked');
//            var column_editor = $('#column_editor').attr('checked');
//            var column_editor = $('#column_editor').attr('checked');
//            var column_editor = $('#column_editor').attr('checked');
//            var column_editor = $('#column_editor').attr('checked');
//            dataTable.fnSetColumnVis( 2, false, true );
//            dataTable.fnSetColumnVis( 8, false, true );

            //hide ajax loader animation here...
            $( '#ajaxLoadAni' ).fadeOut( 'slow' );
        }
    });
}