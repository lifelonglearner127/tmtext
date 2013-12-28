var columns = [
        {
            "sTitle": "Snapshot",
            "sName": "snap",
            // "sWidth": "10%",
            "sClass": "Snapshot"
        },
        {
            "sTitle": "Date",
            "sName": "created",
            // "sWidth": "7%"
        },
        {
            "sTitle": "ID",
            "sName": "imp_data_id",
            // "sWidth": "10%",
            "sClass": "imp_data_id"
        },
        {
            "sTitle": "Product Name",
            "sName": "product_name",
            // "sWidth": "10%",
            "sClass": "product_name_text"
        },
        {
            "sTitle": "item ID",
            "sName": "item_id",
            // "sWidth": "10%",
            "sClass": "item_id"
        },
        {
            "sTitle": "Model",
            "sName": "model",
            // "sWidth": "10%",
            "sClass": "model"
        },
        {
            "sTitle": "URL",
            "sName": "url",
            // "sWidth": "10%",
            "sClass": "url_text"
        },
        {
            "sTitle": "Page Load Time",
            "sName": "Page_Load_Time",
            // "sWidth": "10%",
            "sClass": "Page_Load_Time"
        },
        {
            "sTitle": "<span class='subtitle_desc_short' >Short</span> Description",
            "sName": "Short_Description",
            // "sWidth": "10%",
            "sClass": "Short_Description"
        },
        {
            "sTitle": "Short Desc <span class='subtitle_word_short' ># Words</span>",
            "sName": "short_description_wc",
            // "sWidth": "7%",
            "sClass": "word_short"
        },
        {
            "sTitle": "Meta Keywords",
            "sName": "Meta_Keywords",
            // "sWidth": "7%",
            "sClass": "Meta_Keywords"
        },
        {
            "sTitle": "Keywords <span class='subtitle_keyword_short'>Short</span>",
            "sName": "short_seo_phrases",
            // "sWidth": "7%",
            "sClass": "keyword_short"
        },
        {
            "sTitle": "Title Keywords",
            "sName": "title_seo_phrases",
            // "sWidth": "7%",
            "sClass": "title_seo_phrases"
        },
        {
            "sTitle": "Images",
            "sName": "images_cmp",
            // "sWidth": "7%",
            "sClass": "images_cmp"
        },
        {
            "sTitle": "Videos",
            "sName": "video_count",
            // "sWidth": "7%",
            "sClass": "video_count"
        },/*max*/
        {
            "sTitle": "Title",
            "sName": "title_pa",
            // "sWidth": "7%",
            "sClass": "title_pa"
        },
        {
            "sTitle": "<span class='subtitle_desc_long' >Long </span>Description",
            "sName": "Long_Description",
            // "sWidth": "7%",
            "sClass": "Long_Description"
        },
        {
            "sTitle": "Long Desc <span class='subtitle_word_long' ># Words</span>",
            "sName": "long_description_wc",
            // "sWidth": "7%",
            "sClass": "word_long"
        },
        {
            "sTitle": "Keywords <span class='subtitle_keyword_long'>Long</span>",
            "sName": "long_seo_phrases",
            // "sWidth": "7%",
            "sClass": "keyword_long"
        },
        {
            "sTitle" : "Custom Keywords Short Description",
            "sName" : "Custom_Keywords_Short_Description", 
            // "sWidth" :  "7%",
            "sClass" : "Custom_Keywords_Short_Description"
            
        },
        {
            "sTitle" : "Custom Keywords Long Description",
            "sName" : "Custom_Keywords_Long_Description", 
            // "sWidth" : "7%",
            "sClass" : "Custom_Keywords_Long_Description"
            
        },
        {
            "sTitle" : "Meta Description",
            "sName" : "Meta_Description", 
            // "sWidth" : "7%",
            "sClass" : "Meta_Description"
            
        },
        {
            "sTitle" : "Meta Desc <span class='subtitle_word_long' ># Words</span>",
            "sName" : "Meta_Description_Count", 
            // "sWidth" : "7%",
            "sClass" : "Meta_Description_Count"
            
        },        
        {
            "sTitle" : "H1 Tags", 
            "sName":"H1_Tags", 
            // "sWidth": "7%",
            "sClass" :  "HTags_1"
        },
        {
            "sTitle" : "Chars", 
            "sName":"H1_Tags_Count", 
            // "sWidth": "7%",
            "sClass" :  "HTags"
        },
        {
            "sTitle" : "H2 Tags", 
            "sName":"H2_Tags", 
            // "sWidth": "7%",
            "sClass" :  "HTags_2"
        },
        {
            "sTitle" : "Chars", 
            "sName":"H2_Tags_Count", 
            // "sWidth": "7%",
            "sClass" :  "HTags"
        },
        {
            "sTitle": "Duplicate Content",
            "sName": "duplicate_content",
            // "sWidth": "7%"
        },
        {
            "sTitle": "Third Party Content",
            "sName": "column_external_content",
            // "sWidth": "7%",
            "sClass" :  "column_external_content"
        },
        {
            "sTitle": "Reviews",
            "sName": "column_reviews",
            // "sWidth": "7%",
            "sClass" :  "column_reviews"
        },
        {
            "sTitle": "Avg Review",
            "sName": "average_review",
            // "sWidth": "7%",
            "sClass" :  "average_review"
        },
        {
            "sTitle": "Features",
            "sName": "column_features",
            // "sWidth": "7%"
        },
        {
            "sTitle": "Price",
            "sName": "price_diff",
            // "sWidth": "7%",
            "sClass": "price_text"
        },
        {
            "sTitle": "Recommendations",
            "sName": "recommendations",
            // "sWidth": "17%",
            "bVisible": false,
            "bSortable": false
        },
        {
            "sName": "add_data",
            "bVisible": false
        },
        {
            "sTitle": "Snapshot",
            "sName": "snap1",
            // "sWidth": "10%",
            "sClass": "Snapshot1"
        },
        {
            "sTitle": "ID",
            "sName": "imp_data_id1",
            // "sWidth": "10%",
            "sClass": "imp_data_id1"
        },
        {
            "sTitle": "Product Name",
            "sName": "product_name1",
            // "sWidth": "10%",
			"sClass": "product_name1"
        },
        {
            "sTitle": "item ID",
            "sName": "item_id1",
            // "sWidth": "10%",
            "sClass": "item_id1"
        },
        {
            "sTitle": "Model",
            "sName": "model1",
            // "sWidth": "10%",
            "sClass": "model1"
        },
        {
            "sTitle": "URL",
            "sName": "url1",
            // "sWidth": "10%",
            "sClass": "url1"
        },
        {
            "sTitle": "Page Load Time",
            "sName": "Page_Load_Time1",
            // "sWidth": "10%",
            "sClass": "Page_Load_Time1"
        },
        {
            "sTitle": "<span class='subtitle_desc_short1' >Short </span> Description",
            "sName": "Short_Description1",
            // "sWidth": "10%",
            "sClass": "Short_Description1"
        },
        {
            "sTitle": "Short Desc <span class='subtitle_word_short' ># Words</span>",
            "sName": "short_description_wc1",
            // "sWidth": "7%",
            "sClass": "word_short1"
        },
        {
            "sTitle": "Meta Keywords",
            "sName": "Meta_Keywords1",
            // "sWidth": "7%",
            "sClass": "Meta_Keywords1"
        },
        {
            "sTitle": "<span class='subtitle_desc_long1' >Long </span>Description",
            "sName": "Long_Description1",
            // "sWidth": "7%",
            "sClass": "Long_Description1"
        },
        {
            "sTitle": "Long Desc <span class='subtitle_word_long' ># Words</span>",
            "sName": "long_description_wc1",
            // "sWidth": "7%",
            "sClass": "word_long1"
        },
        {
            "sTitle" : "Meta Description",
            "sName" : "Meta_Description1", 
            // "sWidth" : "7%",
            "sClass" : "Meta_Description1"
            
        },
        {
            "sTitle" : "Meta Desc <span class='subtitle_word_long' ># Words</span>",
            "sName" : "Meta_Description_Count1", 
            // "sWidth" : "7%",
            "sClass" : "Meta_Description_Count1"
            
        },
        {
            "sTitle": "Third Party Content",
            "sName": "column_external_content1",
            // "sWidth": "7%",
            "sClass" :  "column_external_content1"
        },
        {
            "sTitle" : "H1 Tags", 
            "sName":"H1_Tags1", 
            // "sWidth": "7%",
            "sClass" :  "HTags_11"
        },
        {
            "sTitle" : "Chars", 
            "sName":"H1_Tags_Count1", 
            // "sWidth": "7%",
            "sClass" :  "HTags1"
        },
        {
            "sTitle" : "H2 Tags", 
            "sName":"H2_Tags1", 
            // "sWidth": "7%",
            "sClass" :  "HTags_21"
        },
        {
            "sTitle" : "Chars", 
            "sName":"H2_Tags_Count1", 
            // "sWidth": "7%",
            "sClass" :  "HTags1 CharsHTags1"
        },
        {
            "sTitle": "Reviews",
            "sName": "column_reviews1",
            // "sWidth": "7%",
            "sClass": "column_reviews1"
        },
        {
            "sTitle": "Avg Review",
            "sName": "average_review1",
            // "sWidth": "7%",
            "sClass" :  "average_review1"
        },
        {
            "sTitle": "Features",
            "sName": "column_features1",
            // "sWidth": "7%",
            "sClass" :  "column_features1"
        },
        {
            "sTitle": "Title Keywords",
            "sName": "title_seo_phrases1",
            // "sWidth": "7%",
            "sClass": "title_seo_phrases1"
        },
        {
            "sTitle": "Images",
            "sName": "images_cmp1",
            // "sWidth": "7%",
            "sClass": "images_cmp1"
        },
        {
            "sTitle": "Videos",
            "sName": "video_count1",
            // "sWidth": "7%",
            "sClass": "video_count1"
        },
        {
            "sTitle": "Title",
            "sName": "title_pa1",
            // "sWidth": "7%",
            "sClass": "title_pa1"
        },
        {
            "sTitle": "Gap Analysis",
            "sName": "gap",
            // "sWidth": "7%",
            "sClass" :  ""
        },
        {
            "sTitle": "Duplicate Content",
            "sName": "Duplicate_Content",
            // "sWidth": "7%",
            "sClass" :  ""
        },

    ];
	
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
            "product_selection"

        ],
         details_compare: [
            "snap",
            "imp_data_id",
            "product_name",
            "item_id",
            "model",
            "url",
            "Page_Load_Time",
            "Short_Description",
            "short_description_wc",
            "Meta_Keywords",
            "title_seo_phrases",
            "images_cmp",
            "video_count",
            "title_pa",
            "Long_Description",
            "long_description_wc",
            "Meta_Description",
            "Meta_Description_Count",
            "column_external_content",
            "H1_Tags",
            "H1_Tags_Count",
            "H2_Tags",
            "H2_Tags_Count",
            "column_reviews",
            "average_review",
            "column_features",
            "snap1",
            "imp_data_id1",
            "product_name1",
            "item_id1",
            "model1",
            "url1",
            "Page_Load_Time1",
            "Short_Description1",
            "short_description_wc1",
            "Meta_Keywords1",
            "Long_Description1",
            "long_description_wc1",
            "Meta_Description1",
            "Meta_Description_Count1",
            "column_external_content1",
            "H1_Tags1",
            "H1_Tags_Count1",
            "H2_Tags1",
            "H2_Tags_Count1",
            "column_reviews1",
            "average_review1",
            "column_features1",
            "title_seo_phrases1",
            "images_cmp1",
            "video_count1",
            "title_pa1",
            "gap",
            "Duplicate_Content"
            
        ],
        recommendations: [
            "product_name",
            "url",
            "recommendations"
        ]
    };