<?php

return array(
		// array( // --- I.L.
		// 	'sTitle' => 'Price',
		// 	'sName' => 'price',               
		// 	'sClass' => 'own_price_text'
		// ),
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
			'sTitle' => 'Title', 
			'sName' => 'title_pa',               
			'sClass' => 'title_pa'
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
			'sTitle' => 'Price',
			'sName' => 'price_diff',               
			'sClass' => 'price_text',
			'nonCompared' => true
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
			'newTitle' => '<span class="subtitle_desc_short?" >Short</span> Description'
		),
		array(
			'sTitle' => 'Short Desc <span class="subtitle_word_short" ># Words</span>',
			'sName' => 'short_description_wc',                
			'sClass' => 'word_short',
			'newTitle' => 'Short Desc <span class="subtitle_word_short?" ># Words</span>',
		),
		array(
			'sTitle' => "Meta Keywords",
			'sName' => 'Meta_Keywords',
			'sClass' => 'Meta_Keywords'
		),
		array(
			'sTitle' => "Keywords <span class='subtitle_keyword_short'>Short</span>",
			'sName' => 'short_seo_phrases',                
			'sClass' => 'keyword_short',
			'nonCompared' => true
		),
		array(
			'sTitle' => "Title Keywords", 
			'sName' => 'title_seo_phrases',                
			'sClass' => 'title_seo_phrases',
			'moreHtml' => '<input id="tk-denisty" type="radio" name="title_keywords" value="density" checked /><label for="tk-denisty">Density</label>
								<input id="tk-frequency" type="radio" name="title_keywords" value="Frequency"/><label for="tk-frequency">Frequency</label>'
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
			'sTitle' => '<span class="subtitle_desc_long" >Long </span>Description',
			'sName' => 'Long_Description',                
			'sClass' => 'Long_Description',
			'newTitle' => '<span class="subtitle_desc_long?" >Long </span>Description'
		),
		array(
			'sTitle' => 'Long Desc <span class="subtitle_word_long" ># Words</span>',
			'sName' => 'long_description_wc',                
			'sClass' => 'word_long',
			'newTitle' => 'Long Desc <span class="subtitle_word_long?" ># Words</span>'
		),
		array(
			'sTitle' => 'Links', 
			'sName' => 'links_count',               
			'sClass' => 'links_count'
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
			'sTitle' => "Meta Description",
			'sName' => 'Meta_Description',               
			'sClass' => 'Meta_Description'
		),
		array(
			'sTitle' => 'Meta Desc <span class="subtitle_word_long" ># Words</span>',
			'sName' => 'Meta_Description_Count',                
			'sClass' => 'Meta_Description_Count',
			'newTitle' => 'Meta Desc <span class="subtitle_word_long?" ># Words</span>'
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
			'sTitle' => "Duplicate Content",
			'sName' => 'duplicate_content',
			'sClass' => 'Duplicate_Content',			
			'nonCompared' => true
		),
		array(
			'sTitle' => "Third Party Content",
			'sName' => 'column_external_content',
			'sClass' => 'column_external_content'            
		),
		array(
			'sTitle' => 'Reviews',
			'sName' => 'column_reviews',                
			'sClass' => 'column_reviews'
		), 
		array(
			'sTitle' => "Avg Review",
			'sName' => 'average_review',               
			'sClass' => 'average_review'
		),
		array(
			'sTitle' => 'Features',
			'sName' => 'column_features',               
			'sClass' => 'column_features'
		),
		array(
			'sTitle' => 'Recommendations',
			'sName' => 'recommendations',               
			'bVisible' => false,
			'bSortable' => false,
			'nonCompared' => true,
			'nonSelected' => true
		),
		array(
			'sName' => 'add_data',
			'bVisible' => false,
			'nonCompared' => true,
			'nonSelected' => true
		),
		array(
			'sTitle' => 'Gap Analysis',
			'sClass' => 'gap',
			'sName' => 'gap',
			'nonCompared' => true
		)
	);	