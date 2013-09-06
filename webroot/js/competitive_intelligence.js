    var readUrl = base_url + 'index.php/measure/get_product_price';
    var rankingUrl = base_url + 'index.php/brand/rankings';
    var brand_most_type_flag = true;

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
        "sAjaxSource": rankingUrl, //rankingUrl, readUrl
        "oLanguage": {
            "sInfo": "Showing _START_ to _END_ of _TOTAL_ records",
            "sInfoEmpty": "Showing 0 to 0 of 0 records",
            "sInfoFiltered": ""
        },
        "aoColumns": [
            {"sName" : "social_rank"},
            {"sName" : "IR500Rank"},
            {"sName" : "name"},
            {"sName" : "tweets"},
            {"sName" : "total_tweets"},
            {"sName" : "followers"},
            {"sName" : "following"},
            {"sName" : "videos"},
            {"sName" : "views"},
            {"sName" : "total_youtube_views"},
            {"sName" : "average"},
            {"sName" : "total_youtube_videos"}
        ],
        "fnServerData": function (sSource, aoData, fnCallback) {
            if (brand_most_type_flag == true){
                brand_most_type_flag = false;
                var brand_most_type = $("#brand_most_type").val();
                replace_value(aoData, 'iSortCol_0', brand_most_type);
                if (brand_most_type == 0){
                    replace_value(aoData, 'sSortDir_0', 'asc');
                }else{
                    replace_value(aoData, 'sSortDir_0', 'desc');
                }
            }
            $.getJSON(sSource, aoData, function (json) {
                fnCallback(json);
            });
        }
    });

    $('#brand_filters select').change(function(){
        if ($(this).attr('id') == 'brand_most_type'){
            brand_most_type_flag = true;
        }
        dataTable.fnFilter(
            $("#brand_types").val()
                +','+$("#month").val()
                +','+$("#year").val()
            ,1
        );
    });

  //hide ajax loader animation here...
  //  $( '#ajaxLoadAni' ).fadeOut( 'slow' );
}

    function replace_value(aoData, name, value){
        $.each(aoData, function(){
            if (this.name == name){
                this.value = value;
                return;
            }
        });
        //aoData.push({name: name, value: value});
    }