<?php

class AssessHelper
{
	public static function getInitialFilterData()
	{
		$data_for_extract = array (
			'skus_third_party_content' => 0,
			'skus_third_party_content_competitor' => 0,
			'skus_features' => 0,
			'skus_features_competitor' => 0,
			'skus_zero_reviews' => 0,
			'skus_one_four_reviews' => 0,
			'skus_more_than_five_reviews' => 0,
			'skus_more_than_hundred_reviews' => 0,
			'skus_zero_reviews_competitor' => 0,
			'skus_one_four_reviews_competitor' => 0,
			'skus_more_than_five_reviews_competitor' => 0,
			'skus_more_than_hundred_reviews_competitor' => 0,
			'skus_pdfs' => 0,
			'skus_videos' => 0,
			'skus_videos_competitor' => 0,
			'skus_pdfs_competitor' => 0,
			'items_priced_higher_than_competitors' => 0,
			'items_have_more_than_20_percent_duplicate_content' => 0,
			'skus_25_duplicate_content' => 0,
			'skus_50_duplicate_content' => 0,
			'skus_75_duplicate_content' => 0,
			'skus_fewer_50_product_content' => 0,
			'skus_fewer_100_product_content' => 0,
			'skus_fewer_150_product_content' => 0,
			'items_unoptimized_product_content' => 0,
			'short_wc_total_not_0' => 0,
			'long_wc_total_not_0' => 0,
			'items_short_products_content_short' => 0,
			'items_long_products_content_short' => 0,
			'skus_shorter_than_competitor_product_content' => 0,
			'skus_longer_than_competitor_product_content' => 0,
			'skus_same_competitor_product_content' => 0,
			'detail_comparisons_total' => 0,
			'skus_fewer_features_than_competitor' => 0,
			'skus_fewer_reviews_than_competitor' => 0,
			'skus_fewer_competitor_optimized_keywords' => 0,
			'skus_title_less_than_70_chars' => 0,
			'skus_title_more_than_70_chars' => 0,
			'skus_title_less_than_70_chars_competitor' => 0,
			'skus_title_more_than_70_chars_competitor' => 0,		
			'skus_zero_optimized_keywords' => 0,
			'skus_one_optimized_keywords' => 0,
			'skus_two_optimized_keywords' => 0,
			'skus_three_optimized_keywords' => 0,		
			'skus_zero_optimized_keywords_competitor' => 0,
			'skus_one_optimized_keywords_competitor' => 0,
			'skus_two_optimized_keywords_competitor' => 0,
			'skus_three_optimized_keywords_competitor' => 0,		
			'skus_fewer_50_product_content_competitor' => 0,
			'skus_fewer_100_product_content_competitor' => 0,
			'skus_fewer_150_product_content_competitor' => 0,		
			'skus_with_no_product_images' => 0,
			'skus_with_one_product_image' => 0,
			'skus_with_more_than_one_product_image' => 0,		
			'skus_with_no_product_images_competitor' => 0,
			'skus_with_one_product_image_competitor' => 0,
			'skus_with_more_than_one_product_image_competitor' => 0,
		);
		
		return $data_for_extract;
	}
	
	public static function addCompetitorColumns($columns, $max_similar_item_count = 1)
	{
		if (!$max_similar_item_count) return array();
		
		// for now it should be 1 (no more)
		$max_similar_item_count /= $max_similar_item_count;
		$r = array();
		
		for ($i = 1; $i <= $max_similar_item_count; $i++)
		{
			$column = $columns[$i];
			if ($column['nonCompared'])
				continue;
			
			$new_class = isset($column['newClass']) ? str_replace('?', $i, $column['newClass']) : '';
			
			$columns[] = array(
				'sTitle' => $column['sTitle'],
				'sName' => $column['sName'] . $i,
				'sClass' => $new_class
			);
		}
		
		return $columns;
	}
	
	public static function columns() 
	{
        $columns = array(
            array(
                'sTitle' => 'Snapshot',
                'sName' => 'snap',
                'sClass' => 'Snapshot'
            ),
            array(
                'sTitle' => 'Date',
                'sName' => 'created',
				'sClass' => 'created',
            ),
            array(
                'sTitle' => 'ID',
                'sName' => 'imp_data_id',            
                'sClass' => 'imp_data_id'
            ),
            array(
                'sTitle' => "Product Name",
                'sName' => 'product_name',                
                'sClass' => 'product_name_text'
            ),
            array(
                'sTitle' => "item ID",
                'sName' => 'item_id',
                'sClass' => 'item_id'
            ),
            array(
                'sTitle' => 'Model',
                'sName' => 'model',
                'sClass' => 'model'
            ),
            array(
                'sTitle' => 'URL',
                'sName' => 'url',                
                'sClass' => 'url_text'
            ),
            array(
                'sTitle' => "Page Load Time",
                'sName' => 'Page_Load_Time',               
                'sClass' => 'Page_Load_Time'
            ),
            array(
                'sTitle' => '<span class="subtitle_desc_short" >Short</span> Description',
                'sName' => 'Short_Description',                
                'sClass' => 'Short_Description',
				'newClass' => '<span class="subtitle_desc_short?" >Short</span> Description'
            ),
            array(
                'sTitle' => 'Short Desc <span class="subtitle_word_short" ># Words</span>',
                'sName' => 'short_description_wc',                
                'sClass' => 'word_short',
				'newClass' => 'Short Desc <span class="subtitle_word_short?" ># Words</span>',
            ),
            array(
                'sTitle' => "Meta Keywords",
                'sName' => 'Meta_Keywords',
                'sClass' => 'Meta_Keywords'
            ),
			array(
                'sTitle' => '<span class="subtitle_desc_long" >Long </span>Description',
                'sName' => 'Long_Description',                
                'sClass' => 'Long_Description',
				'newClass' => '<span class="subtitle_desc_long?" >Long </span>Description'
            ),
			array(
                'sTitle' => 'Long Desc <span class="subtitle_word_long" ># Words</span>',
                'sName' => 'long_description_wc',                
                'sClass' => 'word_long',
				'newClass' => 'Long Desc <span class="subtitle_word_long?" ># Words</span>'
            ),
			array(
                'sTitle' => "Meta Description",
                'sName' => 'Meta_Description',               
                'sClass' => 'Meta_Description'
            ),
			array(
                'sTitle' => 'Meta Desc <span class="subtitle_word_long" ># Words</span>',
                'sName' => 'Meta_Description_Count',                
                'sClass' => 'Meta_Description_Count',
				'newClass' => 'Meta Desc <span class="subtitle_word_long?" ># Words</span>'
            ),
			array(
                'sTitle' => "Third Party Content",
                'sName' => 'column_external_content',
                'sClass' => 'column_external_content'            
            ),
			array(
                'sTitle' => "H1 Tags",
                'sName' => 'H1_Tags',                
                'sClass' => 'HTags_1'
            ),
			array(
                'sTitle' => 'Chars',
                'sName' => 'H1_Tags_Count',                
                'sClass' => 'HTags'
            ),
            array(
                'sTitle' => "H2 Tags",
                'sName' => 'H2_Tags',                
                'sClass' => 'HTags_2'
            ),
            array(
                'sTitle' => 'Chars',
                'sName' => 'H2_Tags_Count',                
                'sClass' => 'HTags'
            ),
			array(
                'sTitle' => "Avg Review",
                'sName' => 'average_review',               
                'sClass' => 'average_review'
            ),
			array(
                'sTitle' => 'Reviews',
                'sName' => 'column_reviews',                
                'sClass' => 'column_reviews'
            ),            
            array(
                'sTitle' => 'Features',
                'sName' => 'column_features',               
                'sClass' => 'column_features'
            ),
			array(
                'sTitle' => "Title Keywords", 
                'sName' => 'title_seo_phrases',                
                'sClass' => 'title_seo_phrases'
            ),
			array(
                'sTitle' => 'Images',
                'sName' => 'images_cmp',              
                'sClass' => 'images_cmp'
            ),
            array(
                'sTitle' => 'Video', 
                'sName' => 'video_count',             
                'sClass' => 'video_count'
            ),
            array(
                'sTitle' => 'Title', 
                'sName' => 'title_pa',               
                'sClass' => 'title_pa'
            ),		
			array(
				'sTitle' => 'Gap Analysis',
				'sClass' => 'gap',
				'sName' => 'gap'
			),
            array(
                'sTitle' => "Duplicate Content",
                'sName' => 'duplicate_content',
				'sClass' => 'Duplicate_Content',			
            ),    
            array(
                'sTitle' => "Keywords <span class='subtitle_keyword_short'>Short</span>",
                'sName' => 'short_seo_phrases',                
                'sClass' => 'keyword_short',
				'nonCompared' => true
            ),                                            
            array(
                'sTitle' => "Keywords <span class='subtitle_keyword_long'>Long</span>",
                'sName' => 'long_seo_phrases',               
                'sClass' => 'keyword_long',
				'nonCompared' => true
            ),
            array(
                'sTitle' => "Custom Keywords Short Description",
                'sName' => 'Custom_Keywords_Short_Description',     
                'sClass' => 'Custom_Keywords_Short_Description',
				'nonCompared' => true
            ),
            array(
                'sTitle' => "Custom Keywords Long Description",
                'sName' => 'Custom_Keywords_Long_Description',      
                'sClass' => 'Custom_Keywords_Long_Description',
				'nonCompared' => true
            ),  			                 
            array(
                'sTitle' => 'Price',
                'sName' => 'price_diff',               
                'sClass' => 'price_text',
				'nonCompared' => true
            ),
            array(
                'sTitle' => 'Recommendations',
                'sName' => 'recommendations',               
                'bVisible' => false,
                'bSortable' => false,
				'nonCompared' => true
            ),
            array(
                'sName' => 'add_data',
                'bVisible' => false,
				'nonCompared' => true
            )
        );
        return $columns;
    }
}