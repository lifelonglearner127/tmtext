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
            'Cancel': function() {
                $( this ).dialog( 'close' );
            },
            'Save & Next':
                function() {
                    if($('#ajaxLoadAni').css('display') == 'none') {
                        $( '#ajaxLoadAni' ).fadeIn( 'slow' );
                    }
                    $( this ).dialog( 'close' );
                    $.ajax({
                        url: updateHref,
                        type: 'POST',
                        data: $( '#updateDialog form' ).serialize(),
                        success: function( response ) {
                            $( '#msgDialog > p' ).html( response );
                            $( '#ajaxLoadAni' ).fadeOut( 'slow' );
                            updateTableRow();
                            //--- clear form ---
                            $( '#updateDialog form input' ).val( '' );
                            updateNextDialog(updateId);
                        } //end success
                    }); //end ajax()
            },
            'Save':
                function() {
                    if($('#ajaxLoadAni').css('display') == 'none') {
                        $( '#ajaxLoadAni' ).fadeIn( 'slow' );
                    }
                    $( this ).dialog( 'close' );
                    $.ajax({
                        url: updateHref,
                        type: 'POST',
                        data: $( '#updateDialog form' ).serialize(),

                        success: function( response ) {
                            $( '#msgDialog > p' ).html( response );
                            $( '#ajaxLoadAni' ).fadeOut( 'slow' );
                            updateTableRow();
                            //--- clear form ---
                            $( '#updateDialog form input' ).val( '' );
                        } //end success
                    }); //end ajax()
            }, 
            'Reject':
                function(){}
        },
        width: '600px'
    });

    function updateTableRow() {
        //--- update row in table with new values ---
        var columns_checkboxes = $('#choiceColumnDialog input[type=checkbox]');
        $(columns_checkboxes).each(function(i) {
            switch($(this).attr('id')) {
                case 'column_product_name' : {
                    if($(this).attr('checked') == true) {
                        var product_name = $( 'tr#' + updateId + ' td.column_product_name' );
                        $(product_name).html( $( '#product_name' ).val() );
                    }
                    break;
                }
                case 'column_url' : {
                    if($(this).attr('checked') == true) {
                        var url = $( 'tr#' + updateId + ' td.column_url' );
                        $(url).html( $( '#url' ).val() );
                    }
                    break;
                }
                case 'column_short_description' : {
                    if($(this).attr('checked') == true) {
                        var short_description = $( 'tr#' + updateId + ' td.column_short_description' );
                        $(short_description).html( $( '#short_description' ).val() );
                    }
                    break;
                }
                case 'column_short_description_wc' : {
                    if($(this).attr('checked') == true) {
                        var short_description_wc = $( 'tr#' + updateId + ' td.column_short_description_wc' );
                        var short_description_wc_text = $( '#short_description_wc' ).text();
                        if(short_description_wc_text == '0') {
                            short_description_wc_text = '-';
                        }
                        $(short_description_wc).html(short_description_wc_text);
                    }
                    break;
                }
                case 'column_long_description' : {
                    if($(this).attr('checked') == true) {
                        var long_description = $( 'tr#' + updateId + ' td.column_long_description' );
                        $(long_description).html( $( '#long_description' ).val() );
                    }
                    break;
                }
                case 'column_long_description_wc' : {
                    if($(this).attr('checked') == true) {
                        var long_description_wc = $( 'tr#' + updateId + ' td.column_long_description_wc');
                        var long_description_wc_text = $( '#long_description_wc' ).text();
                        if(long_description_wc_text == '0') {
                            long_description_wc_text = '-';
                        }
                        $(long_description_wc).html(long_description_wc_text);
                    }
                    break;
                }
            }
        });
    }//end update dialog

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

    $("#updateDialog #long_description").click(function(e){
        e.stopPropagation(); // return click to long desc field
    });
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
                $( '#updateDialog' ).dialog( "option", "title", "Update - Item "+response[0].id );
                $("#updateDialog").parent().find("div.ui-dialog-buttonpane button").not(":eq(0)").addClass("researchReviewUpdate");
                $("#updateDialog").parent().find("div.ui-dialog-buttonpane button").eq(3).replaceWith('<div class="reject"><label><input type="checkbox" id="check1" /> Reject</label></div>');
                shortDescriptionWordCount();
                longDescriptionWordCount();
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
        modal: true,
        buttons: {
            'Save': function() {
                // get columns params
                var columns = {
                    editor : $("#column_editor").attr('checked') == 'checked',
                    product_name : $("#column_product_name").attr('checked') == 'checked',
                    url : $("#column_url").attr('checked') == 'checked',
                    short_description : $("#column_short_description").attr('checked') == 'checked',
                    short_description_wc : $("#column_short_description_wc").attr('checked') == 'checked',
                    long_description : $("#column_long_description").attr('checked') == 'checked',
                    long_description_wc : $("#column_long_description_wc").attr('checked') == 'checked',
                    batch_name : $("#column_batch_name").attr('checked') == 'checked',
                    actions : $("#column_actions").attr('checked') == 'checked',
                    kw_long : $("#column_kw_long").attr('checked') == 'checked',
                    kw_short : $("#column_kw_short").attr('checked') == 'checked'
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
        width: '250px'
    });

    $( document ).delegate( '#research_batches_columns', 'click', function() {
        $( '#choiceColumnDialog' ).dialog( 'open' );
        $('#choiceColumnDialog').parent().find('button:first').addClass("popupGreen");
    });

    // Short descriptin Word count in update dialog
    function shortDescriptionWordCount() {
        var number = 0;
        var matches = $('#short_description').val().match(/\b/g);
        if(matches) {
            number = matches.length/2;
        }
        $('#short_description_wc').html(number);
        $('input[name="short_description_wc"]').val(number);
    }
    $('#short_description').live("keydown keyup change focusout", function() {
        shortDescriptionWordCount();
    });

    // Long descriptin Word count in update dialog
    function longDescriptionWordCount() {
        var number = 0;
//        console.log($('textarea[name=long_description]').val());
        var matches = $('#long_description').val().match(/\b/g);
        if(matches) {
            number = matches.length/2;
        }
//        console.log("text: " + number);
        $('#long_description_wc').html(number);
        $('input[name="long_description_wc"]').val(number);
    }
    $('#long_description').live("keydown keyup change focusout", function() {
        longDescriptionWordCount()
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
        data:{ 'search_text': $('input[name="research_batches_text"]').val(),
            'batch_name': $('select[name="research_batches"]').find('option:selected').text()
        },
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
                dataTable = $( '#records' ).dataTable({
                    "bJQueryUI": true,
                    "bDestroy": true,
                    "oLanguage": {
                        "sInfo": "Showing _START_ to _END_ of _TOTAL_ records",
                        "sInfoEmpty": "Showing 0 to 0 of 0 records",
                        "sInfoFiltered": ""
                    },
                   "aoColumns": [
                         null, null, null, null, null, null, null, null, null
                    ]
                });
            }

            dataTable.fnFilter( $('select[name="research_batches"]').find('option:selected').text(), 7);
            //hide ajax loader animation here...
            $( '#ajaxLoadAni' ).fadeOut( 'slow' );

            // get visible columns status
            var columns_checkboxes = $('#choiceColumnDialog input[type=checkbox]');
            $(columns_checkboxes).each(function(i) {
                if($(this).attr('checked') != 'checked' && i<9) {
                    dataTable.fnSetColumnVis( i, false, true );
                }

            });

            $('#records tbody tr').each( function() {



                if ($(this).attr('status') == 'reviewed') {
                    $(this).removeClass('odd even');
                    $(this).addClass('reviewed');
                }


                //console.log();
            });
        }
    });
}