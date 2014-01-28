<?php

require_once(APPPATH . 'models/base_model.php');
require_once(APPPATH . 'models/ifilters.php');

class Filters_values extends Base_model implements IFilters 
{		
	public $id;
	public $value;
	public $filter_id;
	public $combination_id;	
	public $icon;	

	public $filters = array(
		self::ASSESS_REPORT_TOTAL_ITEMS => 'assess_report_total_items',
		self::ASSESS_REPORT_TOTAL_ITEMS_COMPETITOR => 'assess_report_competitor_matches_number',
		self::ASSESS_REPORT_ITEMS_PRICED_HIGHER_THAN_COMPETITORS => 'items_priced_higher_than_competitors',
		self::SKUS_SHORTER_THAN_COMPETITOR_PRODUCT_CONTENT => 'skus_shorter_than_competitor_product_content',
		self::SKUS_LONGER_THAN_COMPETITOR_PRODUCT_CONTENT => 'skus_longer_than_competitor_product_content',
		self::SKUS_SAME_COMPETITOR_PRODUCT_CONTENT => 'skus_same_competitor_product_content',
		self::SKUS_FEWER_50_PRODUCT_CONTENT => 'skus_fewer_50_product_content',
		self::SKUS_FEWER_50_PRODUCT_CONTENT_COMPETITOR => 'skus_fewer_50_product_content_competitor',
		self::SKUS_FEWER_100_PRODUCT_CONTENT => 'skus_fewer_100_product_content',
		self::SKUS_FEWER_100_PRODUCT_CONTENT_COMPETITOR => 'skus_fewer_100_product_content_competitor',
		self::SKUS_FEWER_150_PRODUCT_CONTENT => 'skus_fewer_150_product_content',
		self::SKUS_FEWER_150_PRODUCT_CONTENT_COMPETITOR => 'skus_fewer_150_product_content_competitor',
		self::SKUS_FEWER_COMPETITOR_OPTIMIZED_KEYWORDS => 'skus_fewer_competitor_optimized_keywords',
		self::SKUS_ZERO_OPTIMIZED_KEYWORDS => 'skus_zero_optimized_keywords',
		self::SKUS_ZERO_OPTIMIZED_KEYWORDS_COMPETITOR => 'skus_zero_optimized_keywords_competitor',
		self::SKUS_ONE_OPTIMIZED_KEYWORDS => 'skus_one_optimized_keywords',
		self::SKUS_ONE_OPTIMIZED_KEYWORDS_COMPETITOR => 'skus_one_optimized_keywords_competitor',
		self::SKUS_TWO_OPTIMIZED_KEYWORDS => 'skus_two_optimized_keywords',
		self::SKUS_TWO_OPTIMIZED_KEYWORDS_COMPETITOR => 'skus_two_optimized_keywords_competitor',
		self::SKUS_THREE_OPTIMIZED_KEYWORDS => 'skus_three_optimized_keywords',
		self::SKUS_THREE_OPTIMIZED_KEYWORDS_COMPETITOR => 'skus_three_optimized_keywords_competitor',
		self::SKUS_TITLE_LESS_THAN_70_CHARS => 'skus_title_less_than_70_chars',
		self::SKUS_TITLE_LESS_THAN_70_CHARS_COMPETITOR => 'skus_title_less_than_70_chars_competitor',
		self::SKUS_TITLE_MORE_THAN_70_CHARS => 'skus_title_more_than_70_chars',
		self::SKUS_TITLE_MORE_THAN_70_CHARS_COMPETITOR => 'skus_title_more_than_70_chars_competitor',
		self::SKUS_WITH_NO_PRODUCT_IMAGES => 'skus_with_no_product_images',
		self::SKUS_WITH_NO_PRODUCT_IMAGES_COMPETITOR => 'skus_with_no_product_images_competitor',
		self::SKUS_WITH_ONE_PRODUCT_IMAGE => 'skus_with_one_product_image',
		self::SKUS_WITH_ONE_PRODUCT_IMAGE_COMPETITOR => 'skus_with_one_product_image_competitor',
		self::SKUS_WITH_MORE_THAN_ONE_PRODUCT_IMAGE => 'skus_with_more_than_one_product_image',
		self::SKUS_WITH_MORE_THAN_ONE_PRODUCT_IMAGE_COMPETITOR => 'skus_with_more_than_one_product_image_competitor',
		self::SKUS_FEWER_REVIEWS_THAN_COMPETITOR => 'skus_fewer_reviews_than_competitor',
		self::SKUS_ZERO_REVIEWS => 'skus_zero_reviews',
		self::SKUS_ZERO_REVIEWS_COMPETITOR => 'skus_zero_reviews_competitor',
		self::SKUS_ONE_FOUR_REVIEWS => 'skus_one_four_reviews',
		self::SKUS_ONE_FOUR_REVIEWS_COMPETITOR => 'skus_one_four_reviews_competitor',
		self::SKUS_MORE_THAN_FIVE_REVIEWS => 'skus_more_than_five_reviews',
		self::SKUS_MORE_THAN_FIVE_REVIEWS_COMPETITOR => 'skus_more_than_five_reviews_competitor',
		self::SKUS_MORE_THAN_HUNDRED_REVIEWS => 'skus_more_than_hundred_reviews',
		self::SKUS_MORE_THAN_HUNDRED_REVIEWS_COMPETITOR => 'skus_more_than_hundred_reviews_competitor',
		self::SKUS_FEWER_FEATURES_THAN_COMPETITOR => 'skus_fewer_features_than_competitor',
		self::SKUS_FEATURES => 'skus_features',
		self::SKUS_FEATURES_COMPETITOR => 'skus_features_competitor',
		self::SKUS_75_DUPLICATE_CONTENT => 'skus_75_duplicate_content',
		self::SKUS_50_DUPLICATE_CONTENT => 'skus_50_duplicate_content',
		self::SKUS_25_DUPLICATE_CONTENT => 'skus_25_duplicate_content',
		self::SKUS_THIRD_PARTY_CONTENT => 'skus_third_party_content',
		self::SKUS_THIRD_PARTY_CONTENT_COMPETITOR => 'skus_third_party_content_competitor',
		self::SKUS_PDFS => 'skus_pdfs',
		self::SKUS_PDFS_COMPETITOR => 'skus_pdfs_competitor',
		self::SKUS_VIDEOS => 'skus_videos',
		self::SKUS_VIDEOS_COMPETITOR => 'skus_videos_competitor',
		self::SKUS_WITH_ZERO_PRODUCT_DESCRIPTION_LINKS => 'skus_with_zero_product_description_links',
		self::SKUS_WITH_ZERO_PRODUCT_DESCRIPTION_LINKS_COMPETITOR => 'skus_with_zero_product_description_links_competitor',
		self::SKUS_WITH_MORE_THAN_ONE_PRODUCT_DESCRIPTION_LINKS => 'skus_with_more_than_one_product_description_links',
		self::SKUS_WITH_MORE_THAN_ONE_PRODUCT_DESCRIPTION_LINKS_COMPETITOR => 'skus_with_more_than_one_product_description_links_competitor',
		self::SKUS_WITH_MANUFACTURER_VIDEOS => 'skus_with_manufacturer_videos',
		self::SKUS_WITH_MANUFACTURER_IMAGES => 'skus_with_manufacturer_images',
		self::SKUS_WITH_MANUFACTURER_PAGES => 'skus_with_manufacturer_pages',
		self::ASSESS_REPORT_TOTAL_ITEMS_SELECTED_BY_FILTER => 'total_items_selected_by_filter',
	);
	
	public function __construct()
	{
		parent::__construct();
		$this->load->model('filters_items', 'fi');
		$this->load->model('statistics_new_model');
		$this->load->model('batches_model');
        $this->load->model('statistics_model');
        $this->load->model('statistics_duplicate_content_model');
        $this->load->model('product_category_model');
        $this->load->model('keywords_model');
	}
	
	public static function model($className = __CLASS__)
	{
		return parent::model($className);
	}
	
	public function getRules()
	{
		return array(
			'filter_id' => array('type' => 'required'),
			'combination_id' => array('type' => 'required'),
			'value' => array('type' => 'required')
		);
	}
	
	public function getTableName()
	{
		return 'filters_values';
	}

	public function getComparisonData(array $data)
	{
		$params = new stdClass();
		$params->batch_id = $data['batch_id'];		
		$params->category_id = $data['category_id'];							
		
		$results = $this->statistics_new_model->getStatsData($params);
		
		return $results;
	}

	public function generateFiltersValues(array $data)
	{
		$data['combination_id'] = $this->db->insert_id();
		
		$comparison_data = $this->getComparisonData(array(
			'batch_id' => $data['first_batch_id'],			
			'category_id' => $data['category']
		));
		$this->buildFilters($comparison_data, $data);
		
		return true;
	}
		
	public function buildFilters($results, $data)
	{
		$batch_id = $data['first_batch_id'];
		$catId = $data['category'];
		$batch2 = $data['second_batch_id'];
		$max_similar_item_count = 1;
		$long_duplicate_content = 1;
		$short_duplicate_content = 1;
		
		if(intval($catId) > 0) {
			$catList = $this->product_category_model->get(array('id'=>$catId));
		} elseif(intval($batch_id) > 0) {
			$catList = $this->product_category_model->getCatsByBatchId($batch_id);
		} else {	
			$catList = $this->product_category_model->get();
		}
		
		$prodCats = array();
		if(is_array($catList)) {
			foreach($catList as $cl) {
				$prodCats[$cl['id']] = $cl['category_name'].' ('.$cl['category_code'].')';
			}	
		}	
        
        $duplicate_content_range = 25;
		$batch2_items_count = 0;
		$iterator = 0;		                      
		
        $success_filter_entries = array();
        $customer_name = $this->batches_model->getCustomerById($batch_id);
        $customer_url = parse_url($customer_name->url);
        $batch1_meta_percents = array();
        $batch2_meta_percents = array();
        $report = array();     
        $stored_filter_items = array();
		$tb_product_name = 'tb_product_name';
			
		//getting columns				
		$raw_columns = $columns;
		$columns = AssessHelper::addCompetitorColumns($columns);
			
		//extracting initial data varialbes for filters
		extract(AssessHelper::getInitialFilterData());
						
		$result_table_rows_count = $total_rows = count($results);		
		$iterator_limit = $displayCount ? $display_start + $displayCount : $total_rows;
		$totalRows = 0;	
        for ($row_iterator = $display_start; $row_iterator < $total_rows; $row_iterator++) 
		{	
			$row_key = $row_iterator;
			$row = $results[$row_iterator];								
				$success_filter_entries = array();
				$similar_items_data = array();
				$f_count1 = 0;
				$r_count1 = 0;            
				$meta_key_gap = 0;                     			         		
				
			if ($batch2 && $batch2 != 'all') 
			{
					$customer_name = $this->batches_model->getCustomerUrlByBatch($batch2);						
					if (stripos($row->similar_products_competitors, $customer_name) > 0) 
					{
						$similar_items = unserialize($row->similar_products_competitors);

						if (count($similar_items) > 1) 
						{
							$has_similar_items = false;
							foreach ($similar_items as $key => $item) 
							{
								$tsp = '';

								if (!empty($customer_name) && !empty($item['customer']) && $this->statistics_new_model->if_url_in_batch($item['imported_data_id'], $batch2)) 
								{
									$parsed_anchors_unserialize_val = '';
									//$parsed_meta_unserialize_val = '';
									//$parsed_meta_unserialize_val_c = '';                                    
									$parsed_meta_keywords_unserialize_val = '';
									$parsed_review_count_unserialize_val_count = '';                                                                        
									$title_seo_prases = array();
																																			  
									$parsed_column_features_unserialize_val_count = 0;
									$column_external_content = '';
									$cmpare = $this->statistics_new_model->get_compare_item($item['imported_data_id']);
									if(isset($cmpare->Anchors))
									{	
										$parsed_anchors_unserialize = unserialize($cmpare->Anchors);
									}
									if(isset($cmpare->Anchors))
									{	
										$parsed_attributes_unserialize = unserialize($cmpare->parsed_attributes);
									}	

									if (trim($cmpare->title_keywords) && $cmpare->title_keywords != 'None') {
										$title_seo_prases = unserialize($cmpare->title_keywords);
									}
									if (!empty($title_seo_prases)) {

										$str_title_long_seo = '<div class="table_keywords_long">';
										foreach ($title_seo_prases as $pras) {
											$str_title_long_seo .= '<p>' . $pras['ph'] . '<span class = "phr-density" style="display:none;">  ' . $pras['prc']
													. '%</span><span class = "phr-frequency"> - ' . $pras['frq'] . '</span></p>';
										}
										$tsp = $str_title_long_seo . '</div>';
									}
									$HTags = unserialize($cmpare->HTags);
									
									$buildedH1Field = AssessHelper::buildHField($HTags, 'h1');
									$buildedH2Field = AssessHelper::buildHField($HTags, 'h2');
																										   
									$parsed_attributes_unserialize_val = isset($parsed_attributes_unserialize['item_id']) ? $parsed_attributes_unserialize['item_id'] : '';
									$parsed_model_unserialize_val = isset($parsed_attributes_unserialize['model']) ? $parsed_attributes_unserialize['model'] : '';
									$parsed_loaded_in_seconds_unserialize_val = isset($parsed_attributes_unserialize['loaded_in_seconds']) ? $parsed_attributes_unserialize['loaded_in_seconds'] : '';
									$parsed_column_reviews_unserialize_val = isset($parsed_attributes_unserialize['review_count']) ? $parsed_attributes_unserialize['review_count']: 0;
									$parsed_average_review_unserialize_val_count = isset($parsed_attributes_unserialize['average_review']) ? $parsed_attributes_unserialize['average_review'] : '';
									$parsed_column_features_unserialize_val_count = isset($parsed_attributes_unserialize['feature_count']) ? $parsed_attributes_unserialize['feature_count'] : 0;
									$images_cmp = isset($parsed_attributes_unserialize['product_images']) ? $parsed_attributes_unserialize['product_images'] : 'none';				
									$video_count = isset($parsed_attributes_unserialize['video_count']) ? $parsed_attributes_unserialize['video_count'] : 'none';                      
									$title_pa = isset($parsed_attributes_unserialize['title']) ? $parsed_attributes_unserialize['title'] : 'none';                                    
									$links_count = isset($parsed_anchors_unserialize['quantity']) ? $parsed_anchors_unserialize['quantity'] : 'none';
										
									if (isset($parsed_attributes_unserialize['cnetcontent']) || isset($parsed_attributes_unserialize['webcollage']))
										$column_external_content = $this->column_external_content($parsed_attributes_unserialize['cnetcontent'], $parsed_attributes_unserialize['webcollage']);										                                   

									$parsed_meta_unserialize = unserialize($cmpare->parsed_meta);

									if (isset($parsed_meta_unserialize['description'])) {
										$parsed_meta_unserialize_val_c = count(explode(" ",  $parsed_meta_unserialize['description']));
										if ($parsed_meta_unserialize_val_c < 1)
											$parsed_meta_unserialize_val_count = $parsed_meta_unserialize_val_c;
									}
									else if (isset($parsed_meta_unserialize['Description'])) {
										$parsed_meta_unserialize_val_c = count(explode(" ", $parsed_meta_unserialize['Description']));
										if ($parsed_meta_unserialize_val_c < 1)
											$parsed_meta_unserialize_val_count = $parsed_meta_unserialize_val_c;
									}

									if (isset($parsed_meta_unserialize['keywords'])) {
										$Meta_Keywords_un = '<table class="table_keywords_long">';
										$cnt_meta = explode(',', $parsed_meta_unserialize['keywords']);
										$cnt_meta_count = count($cnt_meta);
										$_count_meta = 0;
										foreach ($cnt_meta as $cnt_m) {
											$cnt_m = trim($cnt_m);
											if (!$cnt_m) {
												continue;
											}
											if ($cmpare->Short_Description || $cmpare->Long_Description) {
												$_count_meta = $this->keywords_appearence($cmpare->Long_Description . $cmpare->Short_Description, $cnt_m);
												$_count_meta_num = round(($_count_meta * $cnt_meta_count / ($cmpare->long_description_wc + $cmpare->short_description_wc)) * 100, 2) . '%';
												$Meta_Keywords_un .= '<tr><td>' . $cnt_m . '</td><td style="width: 25px;padding-right: 0px;">' . $_count_meta_num . '</td></tr>';
											}
										}
										$Meta_Keywords_un .= '</table>';
										$parsed_meta_keywords_unserialize_val = $Meta_Keywords_un;
									}

									$row->snap1 = $cmpare->snap;
									$row->imp_data_id1 = $item['imported_data_id'];
									$row->product_name1 = $cmpare->product_name;
									$row->item_id1 = $parsed_attributes_unserialize_row;
									$row->model1 = $parsed_model_unserialize_row;
									$row->url1 = $cmpare->url;
									$row->Page_Load_Time1 = $parsed_loaded_in_seconds_unserialize_row;
									$row->Short_Description1 = $cmpare->Short_Description;
									$row->short_description_wc1 = $cmpare->short_description_wc;
									$row->Meta_Keywords1 = $parsed_meta_keywords_unserialize_row;
									$row->Long_Description1 = $cmpare->Long_Description;
									$row->long_description_wc1 = $cmpare->long_description_wc;
									$row->Meta_Description1 = $parsed_meta_unserialize_row;
									$row->Meta_Description_Count1 = $parsed_meta_unserialize_row_count;
									$row->column_external_content1 = $column_external_content;
									$row->H1_Tags1 = $buildedH1Field['rowue'];
									$row->H1_Tags_Count1 = $buildedH1Field['count'];
									$row->H2_Tags1 = $buildedH2Field['rowue'];
									$row->H2_Tags_Count1 = $buildedH2Field['count'];
									$row->column_reviews1 = $parsed_column_reviews_unserialize_row;
									$row->average_review1 = $parsed_average_review_unserialize_row_count;
									$row->column_features1 = $parsed_column_features_unserialize_row_count;
									$row->title_seo_phrases1 = $tsp !== '' ? $tsp : 'None';
									$row->images_cmp1 = $images_cmp;
									$row->video_count1 = $video_count;
									$row->title_pa1 = $title_pa;
									$row->links_count1 = $links_count;
									$row->total_description_wc1 = $row->short_description_wc1+$row->long_description_wc1;
									$cmpare->imported_data_id = $item['imported_data_id'];
									$batch2_items_count++;

									$similar_items_data[] = $cmpare;
									$row->similar_items = $similar_items_data;
									
									$has_similar_items = true;
									break;
								} 							
							}
							if (!$has_similar_items) {
								$result_table_rows_count--;
								continue;
							}
								
						} else {
							$result_table_rows_count--;
							continue;
						}
					} else {
						$result_table_rows_count--;
						continue;
					}	
				}
			
			// getting initial (default) result row data
			$result_row = AssessHelper::getInitialScalarRowData($row);
			
			$pars_atr = $this->imported_data_parsed_model->getByImId($row->imported_data_id);	
			         
            if ($max_similar_item_count > 0) {                
                $sim_items = $row->similar_items;
                $max_similar_item_count = (int) $max_similar_item_count;
                

                for ($it = 0, $sim_it = 1; $it < $max_similar_item_count; $it++, $sim_it++) {
                    
                    $parsed_anchors_unserialize_val = '';                   
                    $parsed_meta_unserialize_val_count = '';
                    $parsed_meta_keywords_unserialize_val = '';                                                                                              
                    $column_external_content = '';
                                                            
                    $parsed_attributes_unserialize = unserialize($sim_items[$it]->parsed_attributes);
                    $parsed_anchors_unserialize = unserialize($sim_items[$it]->Anchors);

                    if (isset($parsed_attributes_unserialize['cnetcontent']) || isset($parsed_attributes_unserialize['webcollage']))
                        $column_external_content = $this->column_external_content($parsed_attributes_unserialize['cnetcontent'], $parsed_attributes_unserialize['webcollage']);

                    $HTags = unserialize($sim_items[$it]->HTags);
					
					$buildedH1Field = AssessHelper::buildHField($HTags, 'h1');
					$buildedH2Field = AssessHelper::buildHField($HTags, 'h2');					                                      
                    
                    $parsed_attributes_unserialize_val = isset($parsed_attributes_unserialize['item_id']) ? $parsed_attributes_unserialize['item_id'] : '';
					$parsed_attributes_model_unserialize_val = isset($parsed_attributes_unserialize['model']) ? $parsed_attributes_unserialize['model'] : '';
					$parsed_loaded_in_seconds_unserialize_val = isset($parsed_attributes_unserialize['loaded_in_seconds']) ? $parsed_attributes_unserialize['loaded_in_seconds'] : '';
                    $parsed_column_reviews_unserialize_val = isset($parsed_attributes_unserialize['review_count']) ? $parsed_attributes_unserialize['review_count'] : 0;
					$parsed_average_review_unserialize_val = isset($parsed_attributes_unserialize['average_review']) ? $parsed_attributes_unserialize['average_review'] : '';
					$parsed_column_features_unserialize_val = isset($parsed_attributes_unserialize['feature_count']) ? $parsed_attributes_unserialize['feature_count'] : 0;
                    $images_cmp = isset($parsed_attributes_unserialize['product_images']) ? $parsed_attributes_unserialize['product_images'] : '';
					$video_count = isset($parsed_attributes_unserialize['video_count']) ? $parsed_attributes_unserialize['video_count'] : '';
					$title_pa = isset($parsed_attributes_unserialize['title']) ? $parsed_attributes_unserialize['title'] : '';                    
                    $links_count = isset($parsed_anchors_unserialize['quantity']) ? $parsed_anchors_unserialize['quantity'] : '';
                    
                   
                    $parsed_meta_unserialize = unserialize($sim_items[$it]->parsed_meta);
					
		    if ($parsed_meta_unserialize['description']) {
                        $parsed_meta_unserialize_val_c = count(explode(" ", $parsed_meta_unserialize['description']));
                        if ($parsed_meta_unserialize_val_c < 1)
                            $parsed_meta_unserialize_val_count = $parsed_meta_unserialize_val_c;
                    }
                    else if ($parsed_meta_unserialize['Description']) {
                        $parsed_meta_unserialize_val_c = count(explode(" ", $parsed_meta_unserialize['Description']));
                        if ($parsed_meta_unserialize_val_c != 1)
                            $parsed_meta_unserialize_val_count = $parsed_meta_unserialize_val_c;
                    }
  
                    if ($parsed_meta_unserialize['keywords']) {

                        $Meta_Keywords_un = "<table class='table_keywords_long'>";
                        $cnt_meta_un = explode(',', $parsed_meta_unserialize['keywords']);
                        $cnt_meta_count_un = count($cnt_meta_un);
                        foreach ($cnt_meta_un as $key => $cnt_m_un) {
                            $_count_meta_un = 0;
                            $cnt_m_un = trim($cnt_m_un);
                            if (!$cnt_m_un) {
                                continue;
                            }
                            if ($sim_items[$it]->Long_Description || $sim_items[$it]->Short_Description) {
                                $_count_meta_un = $this->keywords_appearence($sim_items[$it]->Long_Description . $sim_items[$it]->Short_Description, $cnt_m_un);
                                $_count_meta_num_un = (float) round(($_count_meta_un * $cnt_meta_count_un / ($sim_items[$it]->long_description_wc + $sim_items[$it]->short_description_wc)) * 100, 2);

                                $batch2_meta_percents[$row_key][$key] = $_count_meta_num_un;

                                $_count_meta_num_un_proc = $_count_meta_num_un . "%";
                                $Meta_Keywords_un .= "<tr><td>" . $cnt_m_un . "</td><td>" . $_count_meta_num_un_proc . "</td></tr>";
//                        
                                if ($i == 1 && !$meta_key_gap) {
                                    $metta_prc = round(($_count_meta_un * $cnt_meta_count_un / ($row->long_description_wc + $row->short_description_wc)) * 100, 2);
                                    if ($metta_prc >= 2) {
                                        $meta_key_gap = $metta_prc;
                                    }
                                }
                            }
                        }
                        $Meta_Keywords_un .= "</table>";
                        $parsed_meta_keywords_unserialize_val = $Meta_Keywords_un;
                    }


                    if ($i == 1) {
                        if (isset($parsed_attributes_unserialize['feature_count'])) {
                            $f_count1 = $parsed_attributes_unserialize['feature_count'];
                        } else {
                            $f_count1 = 0;
                        }
                        if (isset($parsed_attributes_unserialize['review_count'])) {
                            $r_count1 = $parsed_attributes_unserialize['review_count'];
                        } else {
                            $r_count1 = 0;
                        }

                        if (!$meta_key_gap) {

                            $result_row->gap .= "Competitor is not keyword optimized<br>";
                        }
                    }
					
										
					if (isset($parsed_attributes_unserialize['pdf_count']) && $parsed_attributes_unserialize['pdf_count']) {
						$skus_pdfs_competitor++;
						$this->filterBySummaryCriteria('skus_pdfs_competitor', array(), $success_filter_entries, $stored_filter_items, $iterator);
					}
					
					if (isset($parsed_attributes_unserialize['video_count']) && $parsed_attributes_unserialize['video_count']) {
						$skus_videos_competitor++;
						$this->filterBySummaryCriteria('skus_videos_competitor', array(), $success_filter_entries, $stored_filter_items, $iterator);
					}
					
					if (isset($parsed_attributes_unserialize['product_images']))
					{
						if (!$parsed_attributes_unserialize['product_images']) {
							$skus_with_no_product_images_competitor++;
							$this->filterBySummaryCriteria('skus_with_no_product_images_competitor', array(), $success_filter_entries, $stored_filter_items, $iterator);
						}
						
						if ($parsed_attributes_unserialize['product_images'] == 1) {
							$skus_with_one_product_image_competitor++;
							$this->filterBySummaryCriteria('skus_with_one_product_image_competitor', array(), $success_filter_entries, $stored_filter_items, $iterator);
						}
						
						if ($parsed_attributes_unserialize['product_images'] > 1) {
							$skus_with_more_than_one_product_image_competitor++;
							$this->filterBySummaryCriteria('skus_with_more_than_one_product_image_competitor', array(), $success_filter_entries, $stored_filter_items, $iterator);
						}
					}

					if (!$parsed_anchors_unserialize['quantity']) {
						$skus_with_zero_product_description_links_competitor++;
						$this->filterBySummaryCriteria('skus_with_zero_product_description_links_competitor', array(), $success_filter_entries, $stored_filter_items, $iterator);
					}elseif($parsed_anchors_unserialize['quantity'] > 0) {
						$skus_with_more_than_one_product_description_links_competitor++;
						$this->filterBySummaryCriteria('skus_with_more_than_one_product_description_links_competitor', array(), $success_filter_entries, $stored_filter_items, $iterator);
					}

					
					if (isset($parsed_attributes_unserialize['title']) && $parsed_attributes_unserialize['title'] && strlen($parsed_attributes_unserialize['title']) < 70) {
						$skus_title_less_than_70_chars_competitor++;
						$this->filterBySummaryCriteria('skus_title_less_than_70_chars_competitor', array(), $success_filter_entries, $stored_filter_items, $iterator);
					}
					
					if (isset($parsed_attributes_unserialize['title']) && $parsed_attributes_unserialize['title'] && strlen($parsed_attributes_unserialize['title']) >= 70) {
						$skus_title_more_than_70_chars_competitor++;
						$this->filterBySummaryCriteria('skus_title_more_than_70_chars_competitor', array(), $success_filter_entries, $stored_filter_items, $iterator);
					}
					if (isset($result_row->mvid) && $result_row->mvid > 0) {
						$skus_with_manufacturer_videos++;
						$this->filterBySummaryCriteria('skus_with_manufacturer_videos', array(), $success_filter_entries, $stored_filter_items, $iterator);
					}
					if (isset($result_row->mimg) && $result_row->mimg > 0) {
						$skus_with_manufacturer_images++;
						$this->filterBySummaryCriteria('skus_with_manufacturer_images', array(), $success_filter_entries, $stored_filter_items, $iterator);
					} 
					if (isset($result_row->murl) && strlen($result_row->murl) > 0) { 
						$skus_with_manufacturer_pages++;
						$this->filterBySummaryCriteria('skus_with_manufacturer_pages', array(), $success_filter_entries, $stored_filter_items, $iterator);
					}
					
                
                    $result_row = (array) $result_row;
                    $result_row['snap' . $sim_it] = $sim_items[$it]->snap !== false ? '<span style="cursor:pointer;"><img src="' . base_url() . 'webshoots/' . $sim_items[$it]->snap . '" /></snap>'  : '-';
                    $result_row['title_seo_phrases' . $sim_it] = $row->title_seo_phrases1 ? $row->title_seo_phrases1 : 'None';
                    $result_row['imp_data_id' . $sim_it] = $sim_items[$it]->imported_data_id !== false ? $sim_items[$it]->imported_data_id : '';
                    $result_row['images_cmp' . $sim_it] = $images_cmp ? $images_cmp : 'None';
                    $result_row['video_count' . $sim_it] = $video_count ? $video_count : 'None';
                    $result_row['title_pa' . $sim_it] = $title_pa ? $title_pa : 'None';
                    $result_row['product_name' . $sim_it] = $sim_items[$it]->product_name !== false ?  $sim_items[$it]->product_name  : "-";
                    $result_row['item_id' . $sim_it] = $parsed_attributes_unserialize_val;
                    $result_row['Page_Load_Time' . $sim_it] = $parsed_loaded_in_seconds_unserialize_val;
					$result_row['H1_Tags' . $sim_it] = $buildedH1Field['value'];
                    $result_row['H1_Tags_Count' . $sim_it] = $buildedH1Field['count'];
                    $result_row['H2_Tags' . $sim_it] = $buildedH2Field['value'];
                    $result_row['H2_Tags_Count' . $sim_it] = $buildedH2Field['count'];
                    $result_row['url' . $sim_it] = $sim_items[$it]->url !== false ? "<span class='res_url'><a target='_blank' href='" . $sim_items[$it]->url . "'>" . $sim_items[$it]->url . "</a></span>" : "-";
                    $result_row['model' . $sim_it] = $parsed_attributes_model_unserialize_val;
                    $result_row['short_description_wc' . $sim_it] = $sim_items[$it]->short_description_wc !== false ? $sim_items[$it]->short_description_wc : '';
                    $result_row['Short_Description' . $sim_it] = $sim_items[$it]->Short_Description !== false ? $sim_items[$it]->Short_Description : '';
                    $result_row['Long_Description' . $sim_it] = $sim_items[$it]->Long_Description !== false ? $sim_items[$it]->Long_Description : '';
                    $result_row['Meta_Keywords' . $sim_it] = $parsed_meta_keywords_unserialize_val;
                    $result_row['long_description_wc' . $sim_it] = $sim_items[$it]->long_description_wc !== false ? $sim_items[$it]->long_description_wc : '';
                    $result_row['Meta_Description' . $sim_it] = $parsed_meta_unserialize_val;
                    $result_row['Meta_Description_Count' . $sim_it] = $parsed_meta_unserialize_val_count;
                    $result_row['column_external_content' . $sim_it] = $column_external_content;                    
                    $result_row['column_reviews' . $sim_it] = $parsed_column_reviews_unserialize_val;
                    $result_row['average_review' . $sim_it] = $parsed_average_review_unserialize_val;
                    $result_row['column_features' . $sim_it] = $parsed_column_features_unserialize_val;
                    $result_row['links_count' . $sim_it] = $links_count ? $links_count : 'None';
                    $result_row['total_description_wc' . $sim_it] = $result_row['short_description_wc' . $sim_it] + $result_row['long_description_wc' . $sim_it];
                }

                $result_row = (object) $result_row;
            }	    

            if ($pars_atr['parsed_attributes']['cnetcontent'] || $pars_atr['parsed_attributes']['webcollage']) {
                $result_row->column_external_content = $this->column_external_content($pars_atr['parsed_attributes']['cnetcontent'], $pars_atr['parsed_attributes']['webcollage']);
            }
            $result_row->column_reviews = $pars_atr['parsed_attributes']['review_count'];
            $result_row->column_features = $pars_atr['parsed_attributes']['feature_count'];

            if ($pars_atr['parsed_meta']['description'] && $pars_atr['parsed_meta']['description'] != '') {
                $pars_atr_array = $pars_atr['parsed_meta']['description'];
                $result_row->Meta_Description = $pars_atr_array;
                $words_des = count(explode(" ", $pars_atr_array));
                $result_row->Meta_Description_Count = $words_des;
            } else if ($pars_atr['parsed_meta']['Description'] && $pars_atr['parsed_meta']['Description'] != '') {
                $pars_atr_array = $pars_atr['parsed_meta']['Description'];
                $result_row->Meta_Description = $pars_atr_array;
                $words_des = count(explode(" ", $pars_atr_array));
                $result_row->Meta_Description_Count = $words_des;
            }



            if ($pars_atr['parsed_meta']['keywords'] && $pars_atr['parsed_meta']['keywords'] != '') {
                $Meta_Keywords = "<table class='table_keywords_long'>";
                $cnt_meta = explode(',', $pars_atr['parsed_meta']['keywords']);
                $cnt_meta_count = count($cnt_meta);
                $_count_meta = 0;
                foreach ($cnt_meta as $key => $cnt_m) {
                    $cnt_m = trim($cnt_m);
                    if (!$cnt_m) {
                        continue;
                    }
                    if ($result_row->long_description || $result_row->short_description) {
                        $_count_meta = $this->keywords_appearence($result_row->long_description . $result_row->short_description, $cnt_m);
                        $_count_meta_num = (float) round(($_count_meta * $cnt_meta_count / ($result_row->long_description_wc + $result_row->short_description_wc)) * 100, 2);

                        $batch1_meta_percents[$row_key][$key] = $_count_meta_num;

                        $_count_meta_num_proc = $_count_meta_num . "%";
                        $Meta_Keywords .= "<tr><td>" . $cnt_m . "</td><td style='width: 25px;padding-right: 0px;'>" . $_count_meta_num . "%</td></tr>";  
                    }
                }
                $Meta_Keywords .= "</table>";
                $result_row->Meta_Keywords = $Meta_Keywords;
            }

            if (isset($pars_atr['parsed_attributes']['item_id']) && $pars_atr['parsed_attributes']['item_id'] != '') {
                $result_row->item_id = $pars_atr['parsed_attributes']['item_id'];
            }

            if (isset($pars_atr['parsed_attributes']['model']) && $pars_atr['parsed_attributes']['model'] != '') {
                $result_row->model = $pars_atr['parsed_attributes']['model'];
            }

            if (isset($pars_atr['parsed_attributes']['loaded_in_seconds']) && $pars_atr['parsed_attributes']['loaded_in_seconds'] != '') {
                $result_row->Page_Load_Time = $pars_atr['parsed_attributes']['loaded_in_seconds'];
            }
            if (isset($pars_atr['parsed_attributes']['average_review']) && $pars_atr['parsed_attributes']['average_review'] != '') {
                $result_row->average_review = $pars_atr['parsed_attributes']['average_review'];
            }
            if (isset($pars_atr['parsed_attributes']['product_images'])) {
                $result_row->images_cmp = $pars_atr['parsed_attributes']['product_images'];
            }
            if (isset($pars_atr['parsed_attributes']['video_count'])) {
                $result_row->video_count = $pars_atr['parsed_attributes']['video_count'];
            }
            if (isset($pars_atr['parsed_attributes']['title'])) {
                $result_row->title_pa = $pars_atr['parsed_attributes']['title'];
            }
            if (isset($pars_atr['Anchors']['quantity'])) {
                $result_row->links_count = $pars_atr['Anchors']['quantity'];
            }

			$buildedH1Field = AssessHelper::buildHField($pars_atr['HTags'], 'h1');
			$buildedH2Field = AssessHelper::buildHField($pars_atr['HTags'], 'h2');
			
            $result_row->H1_Tags = $buildedH1Field['value'];
            $result_row->H1_Tags_Count = $buildedH1Field['count'];
			$result_row->H2_Tags = $buildedH2Field['value'];
            $result_row->H2_Tags_Count = $buildedH2Field['count'];			          

            $custom_seo = $this->keywords_model->get_by_imp_id($row->imported_data_id);
			
			$result_row->Custom_Keywords_Long_Description = AssessHelper::getCustomDescriptionKeywords(array(
				'row' => $row,
				'custom_seo' => $custom_seo,
				'table_class' => 'table_keywords_long',
				'seo_elements' => array(
					'primary', 'secondary', 'tetriary'
				),
				'controller' => $this,
				'key' => 'long_description'
			));
			
			$result_row->Custom_Keywords_Short_Description = AssessHelper::getCustomDescriptionKeywords(array(
				'row' => $row,
				'custom_seo' => $custom_seo,
				'table_class' => 'table_keywords_short',
				'seo_elements' => array(
					'primary', 'secondary', 'tetriary'
				),
				'controller' => $this,
				'key' => 'short_description'
			));


            if ($row->snap != null && $row->snap != '') {
                $result_row->snap = $row->snap;
            }

            if (floatval($row->own_price) <> false) {
                $own_site = parse_url($row->url, PHP_URL_HOST);
                $own_site = str_replace('www.', '', $own_site);
                $own_site = str_replace('www1.', '', $own_site);
                $result_row->price_diff = "<nobr>" . $own_site . " - $" . $row->own_price . "</nobr><br />";
//                var_dump($row->own_price);
            }

            if (count($price_diff) > 1) {
                $own_price = floatval($price_diff['own_price']);
                $own_site = str_replace('www.', '', $price_diff['own_site']);
                $own_site = str_replace('www1.', '', $own_site);
                $price_diff_res = "<nobr>" . $own_site . " - $" . $price_diff['own_price'] . "</nobr><br />";
                $flag_competitor = false;
                for ($i = 0; $i < count($price_diff['competitor_customer']); $i++) {
                    if ($customer_url["host"] != $price_diff['competitor_customer'][$i]) {
                        if ($own_price > floatval($price_diff['competitor_price'][$i])) {
                            $result_row->lower_price_exist = true;
                            $competitor_site = str_replace('www.', '', $price_diff['competitor_customer'][$i]);
                            $competitor_site = str_replace('www.', '', $competitor_site);
                            $price_diff_res .= "<input type='hidden'><nobr>" . $competitor_site . " - $" . $price_diff['competitor_price'][$i] . "</nobr><br />";                            
                        }
                    }
                }

                $result_row->price_diff = $price_diff_res;
            }

            $result_row->competitors_prices = @unserialize($row->competitors_prices);

            if (property_exists($row, 'include_in_assess_report') && intval($row->include_in_assess_report) > 0) {
                $detail_comparisons_total += 1;
            }

           

                if (strpos($row->short_seo_phrases, 'a:') !== false) {
                    $short_seo = @unserialize($row->short_seo_phrases);
                } else {
                    $short_seo = false;
                }

                if ($short_seo) {
                    $str_short_seo = '<table class="table_keywords_short">';
                    foreach ($short_seo as $val) {
                        $str_short_seo .= '<tr><td>' . $val['ph'] . '</td><td>' . $val['prc'] . '%</td></tr>';
                    }
                    $result_row->short_seo_phrases = $str_short_seo . '</table>';
                }

                if (strpos($row->long_seo_phrases, 'a:') !== FALSE) {
                    $long_seo = @unserialize($row->long_seo_phrases);
                } else {
                    $long_seo = false;
                }

                if ($long_seo) {
                    $str_long_seo = '<table class="table_keywords_long">';
                    foreach ($long_seo as $val) {
                        $str_long_seo .= '<tr><td>' . $val['ph'] . '</td><td>' . $val['prc'] . '%</td></tr>';
                    }
                    $result_row->long_seo_phrases = $str_long_seo . '</table>';
                }
                //getting title_keywords from statistics_new
                $title_seo_pr = array();
                if ($row->title_keywords != '' && $row->title_keywords != 'None') {
                    $title_seo_pr = unserialize($row->title_keywords);
                }
                if (!empty($title_seo_pr)) {
                    $str_title_long_seo = '<div class="table_keywords_long 3186">';
                    foreach ($title_seo_pr as $val) {
                        $str_title_long_seo .= '<p>' . $val['ph'] . '<span class = "phr-density" style="display:none;">  ' . $val['prc']
                                . '%</span><span class = "phr-frequency"> - ' . $val['frq'] . '</span></p>';
                    }
                    $result_row->title_seo_phrases = $str_title_long_seo . '</div>';
                }
				$result_row->prodcat = 'None';
				if(isset($prodCats[$row->category_id]))
				{	
					$result_row->prodcat = $prodCats[$row->category_id];
				}
				if(!empty($row->manufacturer_info))
				{
					$mi = unserialize($row->manufacturer_info);
					$result_row->murl = '<a target="_blank" class="active_link" href="'.$mi['url'].'">'.$mi['url'].'</a>';
					$result_row->mimg = $mi['images'];
					$result_row->mvid = $mi['videos'];
					if(strlen($mi['url']) > 0)
					{	
						$skus_with_manufacturer_pages++;
						$this->filterBySummaryCriteria('skus_with_manufacturer_pages', array(), $success_filter_entries, $stored_filter_items, $iterator);
					}
					if($mi['images'] > 0)
					{	
						$skus_with_manufacturer_images++;
						$this->filterBySummaryCriteria('skus_with_manufacturer_images', array(), $success_filter_entries, $stored_filter_items, $iterator);
					}
					if($mi['videos'] > 0)
					{	
						$skus_with_manufacturer_videos++;
						$this->filterBySummaryCriteria('skus_with_manufacturer_videos', array(), $success_filter_entries, $stored_filter_items, $iterator);
					}	
				}
           
	
            if ($short_duplicate_content || $long_duplicate_content) {
                $dc = $this->statistics_duplicate_content_model->get($row->imported_data_id);
                $duplicate_customers_short = '';
                $duplicate_customers_long = '';
                $duplicate_short_percent_total = 0;
                $duplicate_long_percent_total = 0;
                if (count($dc) > 1) {

                    foreach ($dc as $vs) {
                        if ($customer_url['host'] == $vs->customer) {
                            $short_percent = 0;
                            $long_percent = 0;
                            if ($short_duplicate_content) {
                                $duplicate_short_percent_total = 100 - round($vs->short_original, 1);
                                $short_percent = 100 - round($vs->short_original, 1);
                                if ($short_percent > 0) {
                                    //$duplicate_customers_short = '<nobr>'.$vs->customer.' - '.$short_percent.'%</nobr><br />';
                                    $duplicate_customers_short = '<nobr>' . $short_percent . '%</nobr><br />';
                                }
                            }
                            if ($long_duplicate_content) {
                                $duplicate_long_percent_total = 100 - round($vs->long_original, 1);
                                $long_percent = 100 - round($vs->long_original, 1);
                                if ($long_percent > 0) {
                                    $duplicate_customers_long = '<nobr>' . $vs->customer . ' - ' . $long_percent . '%</nobr><br />';
                                }
                            }
                        }
                    }                

                    if ($duplicate_customers_short != '') {
                        $duplicate_customers = 'Duplicate short<br />' . $duplicate_customers_short;
                    }
                    if ($duplicate_customers_long != '') {
                        $duplicate_customers = $duplicate_customers . 'Duplicate long<br />' . $duplicate_customers_long;
                    }

                    if ($duplicate_short_percent_total > $duplicate_content_range || $duplicate_long_percent_total > $duplicate_content_range) {
                        $duplicate_customers = "<input type='hidden'/>" . $duplicate_customers;
                    }
                    $result_row->duplicate_content = $duplicate_customers;
                }
            }           
			
			//Dublicate Content      
			if (!$row->Short_Description2 || !$row->Long_Description2) {

				if ($row->short_description) {
					$short_desc_1 = $row->short_description;
				} else {
					$short_desc_1 = '';
				}
				if ($row->long_description) {
					$long_desc_1 = $row->long_description;
				} else {
					$long_desc_1 = '';
				}
				$desc_1 = $short_desc_1 . ' ' . $long_desc_1;

				if ($row->Short_Description1) {
					$short_desc_2 = $row->Short_Description1;
				} else {
					$short_desc_2 = '';
				}
				if ($row->Long_Description1) {
					$long_desc_2 = $row->Long_Description1;
				} else {
					$long_desc_2 = '';
				}
				$desc_2 = $short_desc_2 . ' ' . $long_desc_2;

				if (strcasecmp($desc_1, $desc_2) <= 0)
					similar_text($desc_1, $desc_2, $percent);
				else
					similar_text($desc_2, $desc_1, $percent);

				$percent = number_format($percent, 2);
				
				
				if ($percent >= 25) {
					$skus_25_duplicate_content++;
					$this->filterBySummaryCriteria('skus_25_duplicate_content', array(), $success_filter_entries, $stored_filter_items, $iterator);
				}

				if ($percent >= 50) {
					$skus_50_duplicate_content++;
					$this->filterBySummaryCriteria('skus_50_duplicate_content', array(), $success_filter_entries, $stored_filter_items, $iterator);
				}

				if ($percent >= 75) {
					$skus_75_duplicate_content++;
					$this->filterBySummaryCriteria('skus_75_duplicate_content', array(), $success_filter_entries, $stored_filter_items, $iterator);
				}
				

				$result_row->Duplicate_Content.= $percent . '%';                
			} else {
				$result_row->Duplicate_Content.='';
			}
			
												
				if (isset($pars_atr['parsed_attributes']['pdf_count']) && $pars_atr['parsed_attributes']['pdf_count']) {
					$skus_pdfs++;
					$this->filterBySummaryCriteria('skus_pdfs', array(), $success_filter_entries, $stored_filter_items, $iterator);
				}

				if (isset($pars_atr['parsed_attributes']['video_count']) && $pars_atr['parsed_attributes']['video_count']) {
					$skus_videos++;
					$this->filterBySummaryCriteria('skus_videos', array(), $success_filter_entries, $stored_filter_items, $iterator);
				}
				
				if (isset($pars_atr['parsed_attributes']['product_images']))
				{
					if (!$pars_atr['parsed_attributes']['product_images']) {
						$skus_with_no_product_images++;
						$this->filterBySummaryCriteria('skus_with_no_product_images', array(), $success_filter_entries, $stored_filter_items, $iterator);
					}
					
					if ($pars_atr['parsed_attributes']['product_images'] == 1) {
						$skus_with_one_product_image++;
						$this->filterBySummaryCriteria('skus_with_one_product_image', array(), $success_filter_entries, $stored_filter_items, $iterator);
					}
					
					if ($pars_atr['parsed_attributes']['product_images'] > 1) {
						$skus_with_more_than_one_product_image++;
						$this->filterBySummaryCriteria('skus_with_more_than_one_product_image', array(), $success_filter_entries, $stored_filter_items, $iterator);
					}
				}

				if (!$pars_atr['Anchors']['quantity']) {
						$skus_with_zero_product_description_links++;
						$this->filterBySummaryCriteria('skus_with_zero_product_description_links', array(), $success_filter_entries, $stored_filter_items, $iterator);
				}
				if($pars_atr['Anchors']['quantity'] > 0) {
						$skus_with_more_than_one_product_description_links++;
						$this->filterBySummaryCriteria('skus_with_more_than_one_product_description_links', array(), $success_filter_entries, $stored_filter_items, $iterator);
				}

				if (isset($pars_atr['parsed_attributes']['title']) && $pars_atr['parsed_attributes']['title'] && $pars_atr['parsed_attributes']['title'] < 70) {
					$skus_title_less_than_70_chars++;
					$this->filterBySummaryCriteria('skus_title_less_than_70_chars', array(), $success_filter_entries, $stored_filter_items, $iterator);
				}

				if (isset($pars_atr['parsed_attributes']['title']) && $pars_atr['parsed_attributes']['title'] && $pars_atr['parsed_attributes']['title'] >= 70) {
					$skus_title_more_than_70_chars++;
					$this->filterBySummaryCriteria('skus_title_more_than_70_chars', array(), $success_filter_entries, $stored_filter_items, $iterator);
				}	

				//gap analises
				if ($max_similar_item_count > 0) {
					$sim_items = $row->similar_items;

					if (isset($sim_items[$i - 1]) && ($sim_items[$i - 1]->long_description_wc || $sim_items[$i - 1]->short_description_wc) && ($sim_items[$i - 1]->short_description_wc + $sim_items[$i - 1]->long_description_wc) < 100) {
						$totoal = $sim_items[$i - 1]->short_description_wc + $sim_items[$i - 1]->long_description_wc;
						$result_row->gap.="Competitor total product description length only $totoal words<br>";
					}


					if ($result_row->column_features1 > $result_row->column_features) {
						$x = $result_row->column_features1 - $result_row->column_features;
						$result_row->gap.="Competitor has ".$x." features listed<br>";
					}

					if ($result_row->column_features < $result_row->column_features1) {
						$skus_fewer_features_than_competitor++;
						$this->filterBySummaryCriteria('skus_fewer_features_than_competitor', array(), $success_filter_entries, $stored_filter_items, $iterator);
					}

					if ($result_row->column_reviews < $result_row->column_reviews1) {
						$skus_fewer_reviews_than_competitor++;
						$this->filterBySummaryCriteria('skus_fewer_reviews_than_competitor', array(), $success_filter_entries, $stored_filter_items, $iterator);
					}

					

					if ($result_row->column_features1) {
						$skus_features_competitor++;
						$this->filterBySummaryCriteria('skus_features_competitor', array(), $success_filter_entries, $stored_filter_items, $iterator);
					}

				

					//Second batch								
					if (!$result_row->column_reviews1) {
						$skus_zero_reviews_competitor++;
						$this->filterBySummaryCriteria('skus_zero_reviews_competitor', array(), $success_filter_entries, $stored_filter_items, $iterator);
					}

					if ($result_row->column_reviews1 >= 1 && $result_row->column_reviews1 <= 4) {
						$skus_one_four_reviews_competitor++;
						$this->filterBySummaryCriteria('skus_one_four_reviews_competitor', array(), $success_filter_entries, $stored_filter_items, $iterator);
					}

					if ($result_row->column_reviews1 >= 5) {
						$skus_more_than_five_reviews_competitor++;
						$this->filterBySummaryCriteria('skus_more_than_five_reviews_competitor', array(), $success_filter_entries, $stored_filter_items, $iterator);
					}

					if ($result_row->column_reviews1 >= 100) {
						$skus_more_than_hundred_reviews_competitor++;
						$this->filterBySummaryCriteria('skus_more_than_hundred_reviews_competitor', array(), $success_filter_entries, $stored_filter_items, $iterator);
					}
				}
				
				if ($result_row->column_features) {
					$skus_features++;
					$this->filterBySummaryCriteria('skus_features', array(), $success_filter_entries, $stored_filter_items, $iterator);
				}
				
				/*
				 * Reviews section
				 */
				//First batch								
				if (!$result_row->column_reviews) {
					$skus_zero_reviews++;
					$this->filterBySummaryCriteria('skus_zero_reviews', array(), $success_filter_entries, $stored_filter_items, $iterator);
				}

				if ($result_row->column_reviews >= 1 && $result_row->column_reviews <= 4) {
					$skus_one_four_reviews++;
					$this->filterBySummaryCriteria('skus_one_four_reviews', array(), $success_filter_entries, $stored_filter_items, $iterator);
				}

				if ($result_row->column_reviews >= 5) {
					$skus_more_than_five_reviews++;
					$this->filterBySummaryCriteria('skus_more_than_five_reviews', array(), $success_filter_entries, $stored_filter_items, $iterator);
				}

				if ($result_row->column_reviews >= 100) {
					$skus_more_than_hundred_reviews++;
					$this->filterBySummaryCriteria('skus_more_than_hundred_reviews', array(), $success_filter_entries, $stored_filter_items, $iterator);
				}
				
				if ($result_row->lower_price_exist == true) {
					$items_priced_higher_than_competitors += $row->items_priced_higher_than_competitors;

					$this->filterBySummaryCriteria('assess_report_items_priced_higher_than_competitors', array(), $success_filter_entries, $stored_filter_items, $iterator);
				}
				
				if (trim($result_row->column_external_content)) {
					$skus_third_party_content++;
					$this->filterBySummaryCriteria('skus_third_party_content', array(), $success_filter_entries, $stored_filter_items, $iterator);
				}

				if (trim($result_row->column_external_content1)) {
					$skus_third_party_content_competitor++;
					$this->filterBySummaryCriteria('skus_third_party_content_competitor', array(), $success_filter_entries, $stored_filter_items, $iterator);
				}

				$first_general_description_size = $result_row->short_description_wc + $result_row->long_description_wc;
				$second_general_description_size = $result_row->short_description_wc1 + $result_row->long_description_wc1;

				if ($first_general_description_size < $second_general_description_size) {
					$skus_shorter_than_competitor_product_content++;
					$this->filterBySummaryCriteria('skus_shorter_than_competitor_product_content', array(), $success_filter_entries, $stored_filter_items, $iterator);
				}

				if ($first_general_description_size > $second_general_description_size) {
					$skus_longer_than_competitor_product_content++;
					$this->filterBySummaryCriteria('skus_longer_than_competitor_product_content', array(), $success_filter_entries, $stored_filter_items, $iterator);
				}

				if ($first_general_description_size == $second_general_description_size) {
					$skus_same_competitor_product_content++;
					$this->filterBySummaryCriteria('skus_same_competitor_product_content', array(), $success_filter_entries, $stored_filter_items, $iterator);
				}

				// For Batch 1
				if ($first_general_description_size < 50) {
					$skus_fewer_50_product_content++;
					$this->filterBySummaryCriteria('skus_fewer_50_product_content', array(), $success_filter_entries, $stored_filter_items, $iterator);
				}

				if ($first_general_description_size < 100) {
					$skus_fewer_100_product_content++;
					$this->filterBySummaryCriteria('skus_fewer_100_product_content', array(), $success_filter_entries, $stored_filter_items, $iterator);
				}

				if ($first_general_description_size < 150) {
					$skus_fewer_150_product_content++;
					$this->filterBySummaryCriteria('skus_fewer_150_product_content', array(), $success_filter_entries, $stored_filter_items, $iterator);
				}

				// For Competitor (Batch 2)
				if ($second_general_description_size < 50 && $batch2) {
					$skus_fewer_50_product_content_competitor++;
					$this->filterBySummaryCriteria('skus_fewer_50_product_content_competitor', array(), $success_filter_entries, $stored_filter_items, $iterator);
				}

				if ($second_general_description_size < 100 && $batch2) {
					$skus_fewer_100_product_content_competitor++;
					$this->filterBySummaryCriteria('skus_fewer_100_product_content_competitor', array(), $success_filter_entries, $stored_filter_items, $iterator);
				}

				if ($second_general_description_size < 150 && $batch2) {
					$skus_fewer_150_product_content_competitor++;
					$this->filterBySummaryCriteria('skus_fewer_150_product_content_competitor', array(), $success_filter_entries, $stored_filter_items, $iterator);
				}
				
				$batch1_filtered_title_percents = substr_count($result_row->title_seo_phrases, '%');
				$batch2_filtered_title_percents = substr_count($result_row->title_seo_phrases1, '%');
				
				if ($batch1_filtered_title_percents < $batch2_filtered_title_percents)
				{
					$skus_fewer_competitor_optimized_keywords++;
					$this->filterBySummaryCriteria('skus_fewer_competitor_optimized_keywords', array(), $success_filter_entries, $stored_filter_items, $iterator);					
				}
				
				if (!$batch1_filtered_title_percents)
				{
					$skus_zero_optimized_keywords++;
					$this->filterBySummaryCriteria('skus_zero_optimized_keywords', array(), $success_filter_entries, $stored_filter_items, $iterator);
				}
				
				if ($batch1_filtered_title_percents >= 1)
				{
					$skus_one_optimized_keywords++;
					$this->filterBySummaryCriteria('skus_one_optimized_keywords', array(), $success_filter_entries, $stored_filter_items, $iterator);		
				}
					
				if ($batch1_filtered_title_percents >= 2)
				{
					$skus_two_optimized_keywords++;
					$this->filterBySummaryCriteria('skus_two_optimized_keywords', array(), $success_filter_entries, $stored_filter_items, $iterator);			
				}
					
				if ($batch1_filtered_title_percents >= 3)
				{
					$skus_three_optimized_keywords++;			
					$this->filterBySummaryCriteria('skus_three_optimized_keywords', array(), $success_filter_entries, $stored_filter_items, $iterator);
				}
				
				
				if (!$batch2_filtered_title_percents)
				{
					$skus_zero_optimized_keywords_competitor++;
					$this->filterBySummaryCriteria('skus_zero_optimized_keywords_competitor', array(), $success_filter_entries, $stored_filter_items, $iterator);
				}
				
				if ($batch2_filtered_title_percents >= 1)
				{
					$skus_one_optimized_keywords_competitor++;
					$this->filterBySummaryCriteria('skus_one_optimized_keywords_competitor', array(), $success_filter_entries, $stored_filter_items, $iterator);		
				}
					
				if ($batch2_filtered_title_percents >= 2)
				{
					$skus_two_optimized_keywords_competitor++;
					$this->filterBySummaryCriteria('skus_two_optimized_keywords_competitor', array(), $success_filter_entries, $stored_filter_items, $iterator);			
				}
					
				if ($batch2_filtered_title_percents >= 3)
				{
					$skus_three_optimized_keywords_competitor++;			
					$this->filterBySummaryCriteria('skus_three_optimized_keywords_competitor', array(), $success_filter_entries, $stored_filter_items, $iterator);
				}
				if (isset($data_row->mvid) && $data_row->mvid > 0) {
							$skus_with_manufacturer_videos++;
							$this->filterBySummaryCriteria('skus_with_manufacturer_videos', array(), $success_filter_entries, $stored_filter_items, $iterator);
				}
			        if (isset($data_row->mimg) && $data_row->mimg > 0) {
							$skus_with_manufacturer_images++;
							$this->filterBySummaryCriteria('skus_with_manufacturer_images', array(), $success_filter_entries, $stored_filter_items, $iterator);
				} 
				if (isset($data_row->murl) && strlen($data_row->murl) > 0) { 
							$skus_with_manufacturer_pages++;
							$this->filterBySummaryCriteria('skus_with_manufacturer_pages', array(), $success_filter_entries, $stored_filter_items, $iterator);
				}
            
			
			
			if ($iterator < $iterator_limit) ++$totalRows;
			//	$result_table[$iterator] = $result_row;
	
		++$iterator;			
        }
       
        $own_batch_total_items = $this->statistics_new_model->total_items_in_batch($batch_id);
		
		$summary_fields = array(
			'assess_report_total_items' => array( 'value' => $own_batch_total_items, 'percentage' => array() ),
			'items_priced_higher_than_competitors' => array( 'value' => $items_priced_higher_than_competitors, 'percentage' => array('batch1')),			
			'skus_25_duplicate_content' => array( 'value' => $skus_25_duplicate_content, 'percentage' => array('batch1')),
			'skus_50_duplicate_content' => array( 'value' => $skus_50_duplicate_content, 'percentage' => array('batch1')),
			'skus_75_duplicate_content' => array( 'value' => $skus_75_duplicate_content, 'percentage' => array('batch1')),									
			'skus_shorter_than_competitor_product_content' => array( 'value' => $skus_shorter_than_competitor_product_content, 'percentage' => array('batch1')),
			'skus_longer_than_competitor_product_content' => array( 'value' => $skus_longer_than_competitor_product_content, 'percentage' => array('batch1')),
			'skus_same_competitor_product_content' => array( 'value' => $skus_same_competitor_product_content, 'percentage' => array('batch1')),
			'skus_fewer_features_than_competitor' => array( 'value' => $skus_fewer_features_than_competitor, 'percentage' => array('batch1'), 'icon' => $skus_fewer_features_than_competitor ? 'assess_report_seo_red.png' : 'assess_report_seo.png'),
			'skus_fewer_reviews_than_competitor' => array( 'value' => $skus_fewer_reviews_than_competitor, 'percentage' => array('batch1')),
			'skus_fewer_competitor_optimized_keywords' => array( 'value' => $skus_fewer_competitor_optimized_keywords, 'percentage' => array('batch1')),
			
			'skus_zero_optimized_keywords' => array( 'value' => $skus_zero_optimized_keywords, 'percentage' => array('batch1', 'competitor'), 'generals' => array('competitor' => $skus_zero_optimized_keywords_competitor)),
			'skus_one_optimized_keywords' => array( 'value' => $skus_one_optimized_keywords, 'percentage' => array('batch1', 'competitor'), 'generals' => array('competitor' => $skus_one_optimized_keywords_competitor)),
			'skus_two_optimized_keywords' => array( 'value' => $skus_two_optimized_keywords, 'percentage' => array('batch1', 'competitor'), 'generals' => array('competitor' => $skus_two_optimized_keywords_competitor)),
			'skus_three_optimized_keywords' => array( 'value' => $skus_three_optimized_keywords, 'percentage' => array('batch1', 'competitor'), 'generals' => array('competitor' => $skus_three_optimized_keywords_competitor)),
			
			'skus_zero_optimized_keywords_competitor' => array( 'value' => $skus_zero_optimized_keywords_competitor, 'percentage' => array('batch2', 'competitor'), 'generals' => array('competitor' => $skus_zero_optimized_keywords)),
			'skus_one_optimized_keywords_competitor' => array( 'value' => $skus_one_optimized_keywords_competitor, 'percentage' => array('batch2', 'competitor'), 'generals' => array('competitor' => $skus_one_optimized_keywords)),
			'skus_two_optimized_keywords_competitor' => array( 'value' => $skus_two_optimized_keywords_competitor, 'percentage' => array('batch2', 'competitor'), 'generals' => array('competitor' => $skus_two_optimized_keywords)),
			'skus_three_optimized_keywords_competitor' => array( 'value' => $skus_three_optimized_keywords_competitor, 'percentage' => array('batch2', 'competitor'), 'generals' => array('competitor' => $skus_three_optimized_keywords)),
			
			'skus_title_less_than_70_chars' => array( 'value' => $skus_title_less_than_70_chars, 'percentage' => array('batch1', 'competitor'), 'generals' => array('competitor' => $skus_title_less_than_70_chars_competitor)),
			'skus_title_more_than_70_chars' => array( 'value' => $skus_title_more_than_70_chars, 'percentage' => array('batch1', 'competitor'), 'icon_percentage' => function($percent) {
				if ($percent > 50)
					return 'assess_report_seo_red.png';
				else if ($percent >= 25 && $percent <= 50)
					return 'assess_report_seo_yellow.png';
				else
					return 'assess_report_seo.png';
			}, 'generals' => array('competitor' => $skus_title_more_than_70_chars_competitor)),
			
			'skus_title_less_than_70_chars_competitor' => array( 'value' => $skus_title_less_than_70_chars_competitor, 'percentage' => array('batch2', 'competitor'), 'generals' => array('competitor' => $skus_title_less_than_70_chars)),
			'skus_title_more_than_70_chars_competitor' => array( 'value' => $skus_title_more_than_70_chars_competitor, 'percentage' => array('batch2', 'competitor'), 'icon_percentage' => function($percent) {
				if ($percent > 50)
					return 'assess_report_seo_red.png';
				else if ($percent >= 25 && $percent <= 50)
					return 'assess_report_seo_yellow.png';
				else
					return 'assess_report_seo.png';
			}, 'generals' => array('competitor' => $skus_title_more_than_70_chars)),
			
			'total_items_selected_by_filter' => array( 'value' => $totalRows, 'percentage' => array()),
			'assess_report_competitor_matches_number' => array( 'value' => $batch2_items_count, 'percentage' => array()),
			'skus_third_party_content' => array( 'value' => $skus_third_party_content, 'percentage' => array('batch1', 'competitor'), 'generals' => array('competitor' => $skus_third_party_content_competitor)),
			'skus_third_party_content_competitor' => array( 'value' => $skus_third_party_content_competitor, 'percentage' => array('batch2', 'competitor'), 'generals' => array('competitor' => $skus_third_party_content)),
			'skus_fewer_50_product_content' => array( 'value' => $skus_fewer_50_product_content, 'percentage' => array('batch1', 'competitor'), 'generals' => array('competitor' => $skus_fewer_50_product_content_competitor)),
			'skus_fewer_100_product_content' => array( 'value' => $skus_fewer_100_product_content, 'percentage' => array('batch1', 'competitor'), 'generals' => array('competitor' => $skus_fewer_100_product_content_competitor)),
			'skus_fewer_150_product_content' => array( 'value' => $skus_fewer_150_product_content, 'percentage' => array('batch1', 'competitor'), 'generals' => array('competitor' => $skus_fewer_150_product_content_competitor)),		
			'skus_fewer_50_product_content_competitor' => array( 'value' => $skus_fewer_50_product_content_competitor, 'percentage' => array('batch2', 'competitor'), 'generals' => array('competitor' => $skus_fewer_50_product_content)),
			'skus_fewer_100_product_content_competitor' => array( 'value' => $skus_fewer_100_product_content_competitor, 'percentage' => array('batch2', 'competitor'), 'generals' => array('competitor' => $skus_fewer_100_product_content)),
			'skus_fewer_150_product_content_competitor' => array( 'value' => $skus_fewer_150_product_content_competitor, 'percentage' => array('batch2', 'competitor'), 'generals' => array('competitor' => $skus_fewer_150_product_content)),		
			'skus_features' => array( 'value' => $skus_features, 'percentage' => array('batch1', 'competitor'), 'generals' => array('competitor' => $skus_features_competitor)),
			'skus_features_competitor' => array( 'value' => $skus_features_competitor, 'percentage' => array('batch2', 'competitor'), 'generals' => array('competitor' => $skus_features)),
						
			'skus_zero_reviews' => array( 'value' => $skus_zero_reviews, 'percentage' => array('batch1', 'competitor'), 'generals' => array('competitor' => $skus_zero_reviews_competitor)),
			'skus_one_four_reviews' => array( 'value' => $skus_one_four_reviews, 'percentage' => array('batch1', 'competitor'), 'generals' => array('competitor' => $skus_one_four_reviews_competitor)),
			'skus_more_than_five_reviews' => array( 'value' => $skus_more_than_five_reviews, 'percentage' => array('batch1', 'competitor'), 'generals' => array('competitor' => $skus_more_than_five_reviews_competitor)),
			'skus_more_than_hundred_reviews' => array( 'value' => $skus_more_than_hundred_reviews, 'percentage' => array('batch1', 'competitor'), 'generals' => array('competitor' => $skus_more_than_hundred_reviews_competitor)),
						
			'skus_zero_reviews_competitor' => array( 'value' => $skus_zero_reviews_competitor, 'percentage' => array('batch1', 'competitor'), 'generals' => array('competitor' => $skus_zero_reviews)),
			'skus_one_four_reviews_competitor' => array( 'value' => $skus_one_four_reviews_competitor, 'percentage' => array('batch1', 'competitor'), 'generals' => array('competitor' => $skus_one_four_reviews)),
			'skus_more_than_five_reviews_competitor' => array( 'value' => $skus_more_than_five_reviews_competitor, 'percentage' => array('batch1', 'competitor'), 'generals' => array('competitor' => $skus_more_than_five_reviews)),
			'skus_more_than_hundred_reviews_competitor' => array( 'value' => $skus_more_than_hundred_reviews_competitor, 'percentage' => array('batch1', 'competitor'), 'generals' => array('competitor' => $skus_more_than_hundred_reviews)),
			
			'skus_pdfs' => array( 'value' => $skus_pdfs, 'percentage' => array('batch1', 'competitor'), 'generals' => array('competitor' => $skus_pdfs_competitor), 'icon_percentage' => function($percent) {
				return $percent < 50 ? 'assess_report_seo_red.png' : 'assess_report_seo.png';
			}),
			'skus_pdfs_competitor' => array( 'value' => $skus_pdfs_competitor, 'percentage' => array('batch2', 'competitor'), 'generals' => array('competitor' => $skus_pdfs), 'icon_percentage' => function($percent) {
				return $percent < 50 ? 'assess_report_seo_red.png' : 'assess_report_seo.png';
			}),
			
			'skus_videos' => array( 'value' => $skus_videos, 'percentage' => array('batch1', 'competitor'), 'generals' => array('competitor' => $skus_videos_competitor), 'icon_percentage' => function($percent) {
				return $percent < 50 ? 'assess_report_seo_red.png' : 'assess_report_seo.png';
			}),
			'skus_videos_competitor' => array( 'value' => $skus_videos_competitor, 'percentage' => array('batch2', 'competitor'), 'generals' => array('competitor' => $skus_videos), 'icon_percentage' => function($percent) {
				return $percent < 50 ? 'assess_report_seo_red.png' : 'assess_report_seo.png';
			}),
			
			'skus_with_no_product_images' => array( 'value' => $skus_with_no_product_images, 'percentage' => array('batch1', 'competitor'), 'generals' => array('competitor' => $skus_with_no_product_images_competitor)),
			'skus_with_one_product_image' => array( 'value' => $skus_with_one_product_image, 'percentage' => array('batch1', 'competitor'), 'generals' => array('competitor' => $skus_with_one_product_image_competitor)),
			'skus_with_more_than_one_product_image' => array( 'value' => $skus_with_more_than_one_product_image, 'percentage' => array('batch1', 'competitor'), 'generals' => array('competitor' => $skus_with_more_than_one_product_image_competitor)),
			
			'skus_with_no_product_images_competitor' => array( 'value' => $skus_with_no_product_images_competitor, 'percentage' => array('batch2', 'competitor'), 'generals' => array('competitor' => $skus_with_no_product_images)),
			'skus_with_one_product_image_competitor' => array( 'value' => $skus_with_one_product_image_competitor, 'percentage' => array('batch2', 'competitor'), 'generals' => array('competitor' => $skus_with_one_product_image)),
			'skus_with_more_than_one_product_image_competitor' => array( 'value' => $skus_with_more_than_one_product_image_competitor, 'percentage' => array('batch2', 'competitor'), 'generals' => array('competitor' => $skus_with_more_than_one_product_image)),
			
			'skus_with_zero_product_description_links' => array( 'value' => $skus_with_zero_product_description_links, 'percentage' => array('batch1', 'competitor'), 'generals' => array('competitor' => $skus_with_zero_product_description_links_competitor)),
			'skus_with_more_than_one_product_description_links' => array( 'value' => $skus_with_more_than_one_product_description_links, 'percentage' => array('batch1', 'competitor'), 'generals' => array('competitor' => $skus_with_more_than_one_product_description_links_competitor)),
			'skus_with_zero_product_description_links_competitor' => array( 'value' => $skus_with_zero_product_description_links_competitor, 'percentage' => array('batch2', 'competitor'), 'generals' => array('competitor' => $skus_with_zero_product_description_links)),
			'skus_with_more_than_one_product_description_links_competitor' => array( 'value' => $skus_with_more_than_one_product_description_links_competitor, 'percentage' => array('batch2', 'competitor'), 'generals' => array('competitor' => $skus_with_more_than_one_product_description_links)),

			'skus_with_manufacturer_videos' => array( 'value' => (isset($skus_with_manufacturer_videos)) ? $skus_with_manufacturer_videos : 0, 'percentage' => array('batch2', 'competitor'), 'generals' => array('competitor' => $skus_with_manufacturer_videos)),
			'skus_with_manufacturer_images' => array( 'value' => (isset($skus_with_manufacturer_images)) ? $skus_with_manufacturer_images : 0, 'percentage' => array('batch2', 'competitor'), 'generals' => array('competitor' => $skus_with_manufacturer_images)),
			'skus_with_manufacturer_pages' => array( 'value' => (isset($skus_with_manufacturer_pages)) ? $skus_with_manufacturer_pages : 0, 'percentage' => array('batch2', 'competitor'), 'generals' => array('competitor' => $skus_with_manufacturer_pages)),

		);		
		
		foreach ($summary_fields as $key => $summary_field)
		{						
			$my_percent = 0;
			$filter_value = new Filters_values;
			$filter_value->combination_id = $data['combination_id'];
			$filter_value->filter_id = array_search($key, $this->filters);
			
			$filter_value->value = $report['summary'][$key] = trim($summary_field['value']) . $this->calculatePercentage(array('batch1' => $own_batch_total_items, 'batch2' => $batch2_items_count), $summary_field, $my_percent);
			
			if (isset($summary_field['icon']))
				$filter_value->icon = $report['summary'][$key . '_icon'] = $summary_field['icon'];
			
			if (isset($summary_field['icon_percentage']))			
				$filter_value->icon = $report['summary'][$key . '_icon'] = $summary_field['icon_percentage']($my_percent);
				
			$filter_value->save();					
			
			Filters_items::model()->save_filtered_items($data, $stored_filter_items, $this->db->insert_id());
		}	
					
		return true;
	}
	
	private function keywords_appearence($desc, $phrase) {

        $desc = strip_tags($desc);
        return substr_count($desc, $phrase);
    }
	
	private function filterBySummaryCriteria($current_criteria, $filterCriterias, &$success_filter_entries, &$stored_filter_items, $index) {
	    $is_batch = in_array('batch_me_' . $current_criteria, $filterCriterias);
            $is_competitor = in_array('batch_competitor_' . $current_criteria, $filterCriterias);
	    
            $is_competitor = in_array('batch_competitor_' . $current_criteria, $filterCriterias);
	    $success_filter_entries[] = $is_batch || $is_competitor;
		
		$prefix = $is_batch ? 'batch_me_' : $is_competitor ? 'batch_competitor_' : '';
		
		$stored_filter_items[$prefix . $current_criteria][] = $index;		
    }

    private function checkSuccessFilterEntries($success_filter_entries, $filterCriterias) {  
        if (!$filterCriterias)
            return true;
	
        return array_filter($success_filter_entries);
    }
	
	private function column_external_content($cnetcontent = false, $webcollage = false) {
        $column_external_content = ' ';
        if ($cnetcontent == 1 && $webcollage == 1)
            $column_external_content = 'CNET, Webcollage';
        elseif ($cnetcontent == 1 && $webcollage != 1)
            $column_external_content = 'CNET';
        elseif ($cnetcontent != 1 && $webcollage == 1)
            $column_external_content = 'Webcollage';
        return $column_external_content;
    }
	
	private function calculatePercentage(array $summary_items_counts, $summary_field, &$my_percent) {
        $wrapper_begin = '<span class="filter_item_percentage">';
        $wrapper_end = '</span>';
        $r = '';

        if (isset($summary_field['generals']))
            $summary_items_counts = array_merge($summary_items_counts, $summary_field['generals']);

        foreach ($summary_field['percentage'] as $general) {
			
			// David asked to disable batch-to-batch percentages
			if ($general == 'competitor')
				continue;
				
            if (isset($summary_items_counts[$general])) {
                $percent_number = round($summary_field['value'] * 100 / $summary_items_counts[$general]);
				$my_percent = $percent_number;
                $percent = $percent_number . '%';
                $r .=!$r ? ', ' . $percent : ', ' . $percent . ' ';
            }
        }

        return $wrapper_begin . rtrim($r, ', ') . $wrapper_end;
    }
	
	public function getFilters($filter_id = null)
	{
		return is_null($filter_id) ? $this->filters : $this->filters[$filter_id];
	}
	
	function getFiltersValuesByCombination($combination_id = 0)
	{
		$result = array();
		$combination_id = (int) $combination_id;
		if($combination_id > 0)
		{	
			$filters = $this->findAllByAttributes(array('combination_id'=>$combination_id));
			if(is_array($filters))
			{	
				foreach($filters as $row)
				{
					$result[$this->filters[$row->filter_id]] = $row->value;
				}
			}
		}
		return $result; 
	}
			
}