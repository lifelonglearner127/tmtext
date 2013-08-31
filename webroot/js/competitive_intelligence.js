    var readUrl = base_url + 'index.php/measure/get_product_price';
    var rankingUrl = base_url + 'index.php/brand/rankings';

$( function() {
    
    if($('#brand_ranking').length) {
        readGridDataBrandRanking(); //for Brand Rankings
    } else {
        /* Pricing */
        readGridData1(); // for pricing
    }
    
});

// for pricing
function readGridData() {
    //display ajax loader animation
    $( '#ajaxLoadAni' ).fadeIn( 'slow' );

    $.ajax({
        url: readUrl,
        dataType: 'json',
        data:{
            'search_text': $('input[name="research_batches_text"]').val()
        },
        success: function( response ) {
            //clear old rows
            $( '#records > tbody' ).html( '' );

            //append new rows
            $( '#readTemplate' ).render( response ).appendTo( "#records > tbody" );

            //apply dataTable to #records table and save its object in dataTable variable
            dataTable = $( '#records' ).dataTable({
                "bJQueryUI": true,
                "bDestroy": true,
                "sPaginationType": "full_numbers",
                "bProcessing": true,
                "bServerSide": true,
                "sAjaxSource": readUrl,
                "oLanguage": {
                    "sInfo": "Showing _START_ to _END_ of _TOTAL_ records",
                    "sInfoEmpty": "Showing 0 to 0 of 0 records",
                    "sInfoFiltered": ""
                },
                "aoColumns": [
                    {"sName" : "created"},
                    {"sName" : "url"},
                    {"sName" : "model"},
                    {"sName" : "product_name"},
                    {"sName" : "price"}
                ]

            });
            dataTable.fnSort([[0, 'desc']]);

            //hide ajax loader animation here...
            $( '#ajaxLoadAni' ).fadeOut( 'slow' );
        }
    });
}

function readGridData1() {
    //display ajax loader animation
//    $( '#ajaxLoadAni' ).fadeIn( 'slow' );

    $( '#records > tbody' ).html( '' );

    //append new rows
//    $( '#readTemplate' ).render( response ).appendTo( "#records > tbody" );

    //apply dataTable to #records table and save its object in dataTable variable
    dataTable = $( '#records' ).dataTable({
        "bJQueryUI": true,
        "bDestroy": true,
        "sPaginationType": "full_numbers",
        "bProcessing": true,
        "bServerSide": true,
        "sAjaxSource": readUrl,
        "oLanguage": {
            "sInfo": "Showing _START_ to _END_ of _TOTAL_ records",
            "sInfoEmpty": "Showing 0 to 0 of 0 records",
            "sInfoFiltered": ""
        },
        "aoColumns": [
            {"sName" : "created"},
            {"sName" : "url"},
            {"sName" : "model"},
            {"sName" : "product_name"},
            {"sName" : "price"}
        ]

    });
    dataTable.fnSort([[0, 'desc']]);

    //hide ajax loader animation here...
  //  $( '#ajaxLoadAni' ).fadeOut( 'slow' );
}

function readGridDataBrandRanking() {
    //display ajax loader animation
//    $( '#ajaxLoadAni' ).fadeIn( 'slow' );

    $( '#records > tbody' ).html( '' );

    //apply dataTable to #brand_ranking table and save its object in dataTable variable
    dataTable = $( '#brand_ranking' ).dataTable({
        "bJQueryUI": true,
        "bDestroy": true,
        "sPaginationType": "full_numbers",
        "bProcessing": true,
        "bServerSide": true,
        "bSort": false,
        "sAjaxSource": rankingUrl, //rankingUrl, readUrl
        "oLanguage": {
            "sInfo": "Showing _START_ to _END_ of _TOTAL_ records",
            "sInfoEmpty": "Showing 0 to 0 of 0 records",
            "sInfoFiltered": ""
        },
        "aoColumns": [
            {"sName" : "social_rank"},
            {"sName" : "IR500rank"},
            {"sName" : "brand"},
            {"sName" : "tweet_count"},
            {"sName" : "total_tweets"},
            {"sName" : "twitter_followers"},
            {"sName" : "youtube_video_count"},
            {"sName" : "youtube_view_count"},
            {"sName" : "total_youtube_views"},
            {"sName" : "average"},
            {"sName" : "total_youtube_videos"}
        ]

    });
//    dataTable.fnSort([[0, 'desc']]);
    
    dataTable.fnFilter( $("#brand_types").val()+','+$("#month").val()+','+$("#year").val(), 1 );
//    dataTable.fnFilter( $("#month").val(), 2 );
//    dataTable.fnFilter( $("#year").val(), 3 );
    
//    $("#brand_types").change( function() { dataTable.fnFilter( $("#brand_types").val(), 1 ); } );
//    $("#month").change( function() { dataTable.fnFilter( $("#month").val(), 2 ); } );
//    $("#year").change( function() { dataTable.fnFilter( $("#year").val(), 3 ); } );

    //hide ajax loader animation here...
  //  $( '#ajaxLoadAni' ).fadeOut( 'slow' );
}