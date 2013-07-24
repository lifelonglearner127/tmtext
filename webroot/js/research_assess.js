var readAssessUrl = base_url + 'index.php/research/get_assess_info';

$(function () {
    $('#assess_filter_datefrom').datepicker({
        format: 'mm-dd-yyyy'
    });

    $('#assess_filter_dateto').datepicker({
        format: 'mm-dd-yyyy'
    });

    $('#research_assess_short_check').live('click', function() {
        var enabled = $(this).is(':checked');
        if (enabled) {
            $('#research_assess_short_params').find('checkbox').removeAttr('disabled');
            $('#research_assess_short_params').find('input').removeAttr('disabled');
        }
        else {
            $('#research_assess_short_params').find('checkbox').attr('disabled', 'disabled');
            $('#research_assess_short_params').find('input').attr('disabled', 'disabled');
        }
    });

    $('#research_assess_long_check').live('click', function() {
        var enabled = $(this).is(':checked');
        if (enabled) {
            $('#research_assess_long_params').find('checkbox').removeAttr('disabled');
            $('#research_assess_long_params').find('input').removeAttr('disabled');
        }
        else {
            $('#research_assess_long_params').find('checkbox').attr('disabled', 'disabled');
            $('#research_assess_long_params').find('input').attr('disabled', 'disabled');
        }
    });

    $('#assess_filter_clear_dates').live('click', function() {
        $('#assess_filter_datefrom').val('');
        $('#assess_filter_dateto').val('');
    });

    $('#research_assess_update').live('click', function() {
    });

    $('#research_assess_filter').live('click', function() {
        if (dataTable) {
            dataTable.fnDestroy();
            dataTable = undefined;
        }
        readAssessData();
    });

    // choice column dialog
    $('#research_assess_choiceColumnDialog').dialog({
        autoOpen: false,
        modal: true,
        buttons: {
            'Save': function() {
                // get columns params
                var columns = {
                    created : $("#column_created").attr('checked') == 'checked',
                    product_name : $("#column_product_name").attr('checked') == 'checked',
                    url : $("#column_url").attr('checked') == 'checked',
                    short_description_wc : $("#column_short_description_wc").attr('checked') == 'checked',
                    short_seo_phrases : $("#column_short_seo_phrases").attr('checked') == 'checked',
                    long_description_wc : $("#column_long_description_wc").attr('checked') == 'checked',
                    long_seo_phrases : $("#column_long_seo_phrases").attr('checked') == 'checked',
                    duplicate_content : $("#column_duplicate_content").attr('checked') == 'checked',
                    price_diff : $("#column_price_diff").attr('checked') == 'checked'
                };

                // save params to DB
                $.ajax({
                    url: base_url + 'index.php/research/assess_save_columns_state',
                    dataType : 'json',
                    type : 'post',
                    data : {
                        value : columns
                    },
                    success : function( data ) {
                        if(data == true) {
                            dataTable.fnDestroy();
                            dataTable = undefined;
                            readAssessData();
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

    $('#research_batches_columns').live('click', function() {
        $('#research_assess_choiceColumnDialog').dialog('open');
        $('#research_assess_choiceColumnDialog').parent().find('button:first').addClass("popupGreen");
    });

    //readAssessData();

});

function readAssessData() {
    var data = {};

    data.search_text =  $('#assess_filter_text').val();
    data.batch_name = $('select[name="research_batches"]').find('option:selected').text();

//    if (!data.batch_name)
//        return;

    var assess_filter_datefrom = $('#assess_filter_datefrom').val();
    var assess_filter_dateto = $('#assess_filter_dateto').val();
    if (assess_filter_datefrom && assess_filter_dateto) {
        data.date_from = assess_filter_datefrom,
        data.date_to = assess_filter_dateto
    }

    if ($('#research_assess_price_diff').is(':checked')) {
        data.price_diff = true;
    }

    if ($('#research_assess_short_check').is(':checked')) {
        if ($('#research_assess_short_less_check').is(':checked')) {
            data.short_less = $('#research_assess_short_less').val();
        }
        if ($('#research_assess_short_more_check').is(':checked')) {
            data.short_more = $('#research_assess_short_more').val();
        }

        if ($('#research_assess_short_seo_phrases').is(':checked')) {
            data.short_seo_phrases = true;
        }
        if ($('#research_assess_short_duplicate_content').is(':checked')) {
            data.short_duplicate_content = true;
        }
    }

    if ($('#research_assess_long_check').is(':checked')) {
        if ($('#research_assess_long_less_check').is(':checked')) {
            data.long_less = $('#research_assess_long_less').val();
        }
        if ($('#research_assess_long_more_check').is(':checked')) {
            data.long_more = $('#research_assess_long_more').val();
        }

        if ($('#research_assess_long_seo_phrases').is(':checked')) {
            data.long_seo_phrases = true;
        }
        if ($('#research_assess_long_duplicate_content').is(':checked')) {
            data.long_duplicate_content = true;
        }
    }

    //display ajax loader animation
    $( '#ajaxLoadAni' ).fadeIn( 'slow' );
    $.ajax({
        url: readAssessUrl,
        dataType: 'json',
        data : data,
        success: function( response ) {

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
                        "sInfoFiltered": ""
                    },
                    "aoColumns": [
                        null, null, null, null, null, null, null, null, null
                    ]
                });
            }

//            dataTable.fnFilter(
//                $('select[name="research_batches"]').find('option:selected').text(),
//                8
//            );

            // get visible columns status
            var columns_checkboxes = $('#research_assess_choiceColumnDialog input[type=checkbox]');

            $(columns_checkboxes).each(function(i) {
                if($(this).attr('checked') != 'checked') {
                    dataTable.fnSetColumnVis( i, false, true );
                }
            });

            //hide ajax loader animation here...
            $( '#ajaxLoadAni' ).fadeOut( 'slow' );
        }
    });
}