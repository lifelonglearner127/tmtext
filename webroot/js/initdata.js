var readAssessUrl = base_url + 'index.php/assess/get_assess_info';
var readBoardSnapUrl = base_url + 'index.php/assess/get_board_view_snap';
var readGraphDataUrl = base_url + 'index.php/assess/get_graph_batch_data';
var readAssessUrlCompare = base_url + 'index.php/assess/compare';
var rememberBatchValue = base_url + 'index.php/assess/remember_batches';
var getbatchesvalue = base_url + 'index.php/assess/getbatchvalues';
var get_summary_filters = base_url + 'index.php/assess/get_summary_filters';
var save_summary_filters = base_url + 'index.php/assess/save_summary_filters';
var save_summary_filters_order = base_url + 'index.php/assess/save_summary_filters_order';
var get_columns = base_url + 'index.php/assess/getColumns';
var serevr_side = true;
var serverside_table;
var tblAllColumns = [];
var summaryInfoSelectedElements = [];
var tblAssess;
var last_batch_id;
var last_compare_batch_id;
var summary_active_items = [];
var arrow_css_top;
var summary_filters_order;
var tblAssess_need_to_be_reinit = false;
var scrollYesOrNot = true;
var zeroTableDraw = true;
var options = { path: '/', expires: 30 };
var table_loaded=false;
var curentSibil = 0;
var isFromLocalStorage = false;
var testIsFromLocalStorage = 0;
var dataTableLastPageNumber = 0;
var isReloaded = false;
var outputedFilterIndexes = [];

var FIRST_DISPLAY_LIMIT_COUNT = 200;
var NEXT_DISPLAY_LIMIT_COUNT = 1000;

var short_wc_total_not_0 = 0;
var long_wc_total_not_0 = 0;

var customLocalStorage = {};

var items_short_products_content_short = 0;
var items_long_products_content_short = 0;
	
var summaryFieldNames = [
		'assess_report_total_items',
		'assess_report_competitor_matches_number',
		'skus_shorter_than_competitor_product_content',
		'skus_longer_than_competitor_product_content',
		'skus_same_competitor_product_content',
		'skus_fewer_features_than_competitor',
		'skus_fewer_reviews_than_competitor',
		'skus_fewer_competitor_optimized_keywords',
		
		'skus_zero_optimized_keywords',
		'skus_one_optimized_keywords',
		'skus_two_optimized_keywords',
		'skus_three_optimized_keywords',
		
		'skus_zero_optimized_keywords_competitor',
		'skus_one_optimized_keywords_competitor',
		'skus_two_optimized_keywords_competitor',
		'skus_three_optimized_keywords_competitor',
		
		'skus_title_less_than_70_chars',
		'skus_title_more_than_70_chars',
		'skus_title_less_than_70_chars_competitor',
		'skus_title_more_than_70_chars_competitor',		
		'skus_75_duplicate_content',
		'skus_25_duplicate_content',
		'skus_50_duplicate_content',
		'total_items_selected_by_filter',
		'skus_third_party_content',
		'skus_third_party_content_competitor',
		'skus_fewer_50_product_content',
		'skus_fewer_100_product_content',
		'skus_fewer_150_product_content',
		'skus_fewer_50_product_content_competitor',
		'skus_fewer_100_product_content_competitor',
		'skus_fewer_150_product_content_competitor',
		'skus_features',
		'skus_features_competitor',
		
		'skus_zero_reviews',
		'skus_one_four_reviews',
		'skus_more_than_five_reviews',
		'skus_more_than_hundred_reviews',
		
		'skus_zero_reviews_competitor',
        'skus_one_four_reviews_competitor',
        'skus_more_than_five_reviews_competitor',
        'skus_more_than_hundred_reviews_competitor',
		
		'skus_pdfs',
		'skus_videos',
		'skus_videos_competitor',
		'skus_pdfs_competitor',
		
		'skus_with_no_product_images',
		'skus_with_one_product_image',
		'skus_with_more_than_one_product_image',
		'skus_with_no_product_images_competitor',
		'skus_with_one_product_image_competitor',
		'skus_with_more_than_one_product_image_competitor',
		
		'skus_with_zero_product_description_links',
		'skus_with_zero_product_description_links_competitor',
		'skus_with_more_than_one_product_description_links',
		'skus_with_more_than_one_product_description_links_competitor',
		
		'assess_report_items_priced_higher_than_competitors'
	];
	
	var batch_sets = {
		me : {
			batch_batch : 'research_assess_batches',
			batch_compare : '#research_assess_compare_batches_batch',
			batch_items_prefix : 'batch_me_',
		},
		competitor : {
			batch_batch : 'research_assess_batches_competitor',
			batch_compare : '#research_assess_compare_batches_batch_competitor',
			batch_items_prefix : 'batch_competitor_'
		}
	};
	
    var tableCase = {
        details: [
            // "price", // I.L.
            "snap",
            "created",
            "imp_data_id",
            "product_name",
            "item_id",
            "model",
            "url",
            "Page_Load_Time",
            "Short_Description",
            "short_description_wc",
            "Meta_Keywords",
            "short_seo_phrases",
            "title_seo_phrases",
            "images_cmp",
            "video_count",
            "title_pa",
            "Long_Description",
            "long_description_wc",
            "long_seo_phrases",
            "duplicate_content",
            "Custom_Keywords_Short_Description",
            "Custom_Keywords_Long_Description",
            "Meta_Description",
            "Meta_Description_Count",
            "H1_Tags",
            "H1_Tags_Count",
            "H2_Tags",
            "H2_Tags_Count",
            "column_external_content",
            "column_reviews",
            "average_review",
            "column_features",
            "price_diff",
            "product_selection",
            "links_count"

        ],
         details_compare: [
            // "price", // I.L.
           
            "product_name",
          
            "url",
           
            "short_description_wc",
           
            "title_seo_phrases",
          
            "long_description_wc",
			
        ],
        recommendations: [
            "product_name",
            "url",
            "recommendations"
        ]
    };
var filter_expand_btn_imgs = [
	'filter_expand_btn.jpg',
	'filter_unexpand_btn.jpg',
];
var filter_toggler_flag = 0
	, current_filter_list_wrapper_height = 200;
	
	
	var columns = [
        // { // I.L.
        //     "sTitle": "Price",
        //     "sName": "price",            
        //     "sClass": "own_price_text"
        // },
        {
            "sTitle": "Snapshot",
            "sName": "snap",            
            "sClass": "Snapshot"
        },       
        {
            "sTitle": "ID",
            "sName": "imp_data_id",            
            "sClass": "imp_data_id"
        },
        {
            "sTitle": "Product Name",
            "sName": "product_name",            
            "sClass": "product_name_text"
        },
		{
            "sTitle": "Title",
            "sName": "title_pa",            
            "sClass": "title_pa"
        },
        {
            "sTitle": "item ID",
            "sName": "item_id",            
            "sClass": "item_id"
        },
        {
            "sTitle": "Model",
            "sName": "model",            
            "sClass": "model"
        },
		{
            "sTitle": "Price",
            "sName": "price_diff",            
            "sClass": "price_text"
        },
        {
            "sTitle": "URL",
            "sName": "url",            
            "sClass": "url_text"
        },
        {
            "sTitle": "Page Load Time",
            "sName": "Page_Load_Time",            
            "sClass": "Page_Load_Time"
        },
        {
            "sTitle": "<span class='subtitle_desc_short' >Short</span> Description",
            "sName": "Short_Description",            
            "sClass": "Short_Description"
        },
        {
            "sTitle": "Short Desc <span class='subtitle_word_short' ># Words</span>",
            "sName": "short_description_wc",            
            "sClass": "word_short"
        },
        {
            "sTitle": "Meta Keywords",
            "sName": "Meta_Keywords",            
            "sClass": "Meta_Keywords"
        },
        {
            "sTitle": "Keywords <span class='subtitle_keyword_short'>Short</span>",
            "sName": "short_seo_phrases",            
            "sClass": "keyword_short"
        },
        {
            "sTitle": "Title Keywords",
            "sName": "title_seo_phrases",            
            "sClass": "title_seo_phrases"
        },
        {
            "sTitle": "Images",
            "sName": "images_cmp",            
            "sClass": "images_cmp"
        },
        {
            "sTitle": "Videos",
            "sName": "video_count",            
            "sClass": "video_count"
        },/*max*/
        {
            "sTitle": "<span class='subtitle_desc_long' >Long </span>Description",
            "sName": "Long_Description",            
            "sClass": "Long_Description"
        },
        {
            "sTitle": "Long Desc <span class='subtitle_word_long' ># Words</span>",
            "sName": "long_description_wc",            
            "sClass": "word_long"
        },
		{
            "sTitle": "Links",
            "sName": "links_count",            
            "sClass": "links_count"
        },
        {
            "sTitle": "Keywords <span class='subtitle_keyword_long'>Long</span>",
            "sName": "long_seo_phrases",            
            "sClass": "keyword_long"
        },
        {
            "sTitle" : "Custom Keywords Short Description",
            "sName" : "Custom_Keywords_Short_Description",             
            "sClass" : "Custom_Keywords_Short_Description"            
        },
        {
            "sTitle" : "Custom Keywords Long Description",
            "sName" : "Custom_Keywords_Long_Description",             
            "sClass" : "Custom_Keywords_Long_Description"            
        },
        {
            "sTitle" : "Meta Description",
            "sName" : "Meta_Description",             
            "sClass" : "Meta_Description"            
        },
        {
            "sTitle" : "Meta Desc <span class='subtitle_word_long' ># Words</span>",
            "sName" : "Meta_Description_Count",             
            "sClass" : "Meta_Description_Count"            
        },        
        {
            "sTitle" : "H1 Tags", 
            "sName":"H1_Tags",             
            "sClass" :  "HTags_1"
        },
        {
            "sTitle" : "Chars", 
            "sName":"H1_Tags_Count",             
            "sClass" :  "HTags"
        },
        {
            "sTitle" : "H2 Tags", 
            "sName":"H2_Tags",             
            "sClass" :  "HTags_2"
        },
        {
            "sTitle" : "Chars", 
            "sName":"H2_Tags_Count",             
            "sClass" :  "HTags"
        },
        {
            "sTitle": "Duplicate Content",
            "sName": "duplicate_content",            
        },
        {
            "sTitle": "Third Party Content",
            "sName": "column_external_content",            
            "sClass" :  "column_external_content"
        },
        {
            "sTitle": "Reviews",
            "sName": "column_reviews",            
            "sClass" :  "column_reviews"
        },
        {
            "sTitle": "Avg Review",
            "sName": "average_review",            
            "sClass" :  "average_review"
        },
        {
            "sTitle": "Features",
            "sName": "column_features",            
        },
        {
            "sTitle": "Recommendations",
            "sName": "recommendations",            
            "bVisible": false,
            "bSortable": false
        },
        {
            "sName": "add_data",
            "bVisible": false
        },
		//batch2
        {
            "sTitle": "Snapshot",
            "sName": "snap1",            
            "sClass": "Snapshot1"
        },
        {
            "sTitle": "ID",
            "sName": "imp_data_id1",            
            "sClass": "imp_data_id1"
        },
        {
            "sTitle": "Product Name",
            "sName": "product_name1",            
			"sClass": "product_name1"
        },
        {
            "sTitle": "item ID",
            "sName": "item_id1",            
            "sClass": "item_id1"
        },
        {
            "sTitle": "Model",
            "sName": "model1",            
            "sClass": "model1"
        },
        {
            "sTitle": "URL",
            "sName": "url1",            
            "sClass": "url1"
        },
        {
            "sTitle": "Page Load Time",
            "sName": "Page_Load_Time1",            
            "sClass": "Page_Load_Time1"
        },
        {
            "sTitle": "<span class='subtitle_desc_short1' >Short </span> Description",
            "sName": "Short_Description1",            
            "sClass": "Short_Description1"
        },
        {
            "sTitle": "Short Desc <span class='subtitle_word_short' ># Words</span>",
            "sName": "short_description_wc1",            
            "sClass": "word_short1"
        },
        {
            "sTitle": "Meta Keywords",
            "sName": "Meta_Keywords1",            
            "sClass": "Meta_Keywords1"
        },
		{
            "sTitle": "Title Keywords",
            "sName": "title_seo_phrases1",            
            "sClass": "title_seo_phrases1"
        },
		 {
            "sTitle": "Images",
            "sName": "images_cmp1",            
            "sClass": "images_cmp1"
        },
        {
            "sTitle": "Videos",
            "sName": "video_count1",            
            "sClass": "video_count1"
        },
        {
            "sTitle": "Title",
            "sName": "title_pa1",            
            "sClass": "title_pa1"
        },
        {
            "sTitle": "Links",
            "sName": "links_count1",            
            "sClass": "links_count1"
        },
        {
            "sTitle": "<span class='subtitle_desc_long1' >Long </span>Description",
            "sName": "Long_Description1",            
            "sClass": "Long_Description1"
        },
        {
            "sTitle": "Long Desc <span class='subtitle_word_long' ># Words</span>",
            "sName": "long_description_wc1",            
            "sClass": "word_long1"
        },
        {
            "sTitle" : "Meta Description",
            "sName" : "Meta_Description1",             
            "sClass" : "Meta_Description1"
            
        },
        {
            "sTitle" : "Meta Desc <span class='subtitle_word_long' ># Words</span>",
            "sName" : "Meta_Description_Count1",             
            "sClass" : "Meta_Description_Count1"            
        },
        
        {
            "sTitle" : "H1 Tags", 
            "sName":"H1_Tags1",             
            "sClass" :  "HTags_11"
        },
        {
            "sTitle" : "Chars", 
            "sName":"H1_Tags_Count1",             
            "sClass" :  "HTags1"
        },
        {
            "sTitle" : "H2 Tags", 
            "sName":"H2_Tags1",             
            "sClass" :  "HTags_21"
        },
        {
            "sTitle" : "Chars", 
            "sName":"H2_Tags_Count1",             
            "sClass" :  "HTags1 CharsHTags1"
        }, 
		{
            "sTitle": "Third Party Content",
            "sName": "column_external_content1",            
            "sClass" :  "column_external_content1"
        },
        {
            "sTitle": "Reviews",
            "sName": "column_reviews1",            
            "sClass": "column_reviews1"
        },
        {
            "sTitle": "Avg Review",
            "sName": "average_review1",            
            "sClass" :  "average_review1"
        },
        {
            "sTitle": "Features",
            "sName": "column_features1",            
            "sClass" :  "column_features1"
        },
        {
            "sTitle": "Gap Analysis",
            "sName": "gap",            
            "sClass" :  "gap"
        },
        {
            "sTitle": "Duplicate Content",
            "sName": "Duplicate_Content",            
            "sClass" :  "Duplicate_Content"
        },

    ];

var chart1 = null;
	