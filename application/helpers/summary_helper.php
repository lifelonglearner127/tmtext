<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');
if ( ! function_exists('render_filter_item'))
{
	function render_filter_item($filter_id, $icon, $label, $batch_class_number = '', $is_extended_partial = true, array $question = array(), $display = false)
	{
		// $icon_td_width = $batch_class_number ? '10%' : '7.5%';
		$icon_td_width = '45px';
		$question_td_width = $batch_class_number ? '3%' : '1.5%';		
		$question_content = isset($question['explanation']) ? $question['explanation'] : '';
		$question_title = isset($question['title']) ? $question['title'] : 'Explanation';		
		
		$question_mark = $question_content ? '
		<span data-content="' . $question_content . '" title="' . $question_title . '<a class=\'popover_close_btn\' href=\'#\' onclick=\'close_popover(this); return false;\'>x</a>" data-placement="left" data-original-title="' . $question_title . '" class="question_mark" data-popover-uniqueid="' . $filter_id . '">
			<i class="icon-large icon-question-sign" ></i>
		</span>' : '';
								
		$r = '
			<div class="mt_10 ml_15 item_line ' . ($is_extended_partial ? 'ui-widget-content' : 'non-selectable') . ' ' . ($batch_class_number) . '" data-filterid="' . $filter_id . '" style="display: ' . $display . '">
				<div class="mr_10">
					<table width="100%">
						<tr>
							<td width="' . $icon_td_width . '">
								<img src="' . base_url() . 'img/' . $icon . '" class="' . $filter_id . '_icon" />
							</td>
							<td>
								' . $label . '
								<span class="' . $filter_id . ' mr_10" ></span>
							</td>
							<td width="' . $question_td_width . '">
								' . $question_mark . '
							</td>
						</tr>
					</table>
				</div>
			</div>
		';
		
		return $r;
	}
}

if ( ! function_exists('get_filters') )
{
	function get_filters()
	{
		return array(
			array(
				'data_filter_id' => 'skus_shorter_than_competitor_product_content',
				'icon' => 'assess_report_seo_red.png',
				'label' => 'SKUs that have shorter product content than competitor:',
				'is_default' => true,
				'question' => array(				
					'explanation' => 'The number of your SKUs that have shorter product descriptions than the corresponding SKUs on your competitor’s site. These are good candidates for optimization.',
				)
			),
			array(
				'data_filter_id' => 'skus_longer_than_competitor_product_content',
				'icon' => 'assess_report_seo.png',
				'label' => 'SKUs that have longer product content than competitor:',
				'question' => array(				
					'explanation' => 'The number of your SKUs that have longer product descriptions than the corresponding SKUs on your competitor’s web site.',
				)
			),
			array(
				'data_filter_id' => 'skus_same_competitor_product_content',
				'icon' => 'assess_report_seo.png',
				'label' => 'SKUs that have same length product content as competitor:',
				'question' => array(				
					'explanation' => 'The number of your SKUs that have the same length product descriptions than the corresponding SKUs on your competitor’s web site.',
				)
			),
			array(
				'data_filter_id' => 'skus_fewer_50_product_content',
				'icon' => 'assess_report_seo_red.png',
				'label' => 'SKUs with product content < 50 words:',
				'has_competitor' => true,
				'is_default' => true,
				'question' => array(				
					'batch1' => array(
						'explanation' => 'The number your SKUs in the analyzed batch that have product descriptions that are less than 50 words long. These are good candidates for optimization.',
					),
					'batch2' => array(
						'explanation' => 'Competitor SKUs with product content < 50 words'
					)
				)
			),		
			array(
				'data_filter_id' => 'skus_fewer_100_product_content',
				'icon' => 'assess_report_seo_red.png',
				'label' => 'SKUs with product content < 100 words:',				
				'has_competitor' => true,
				'is_default' => true,
				'question' => array(				
					'batch1' => array(
						'explanation' => 'The number of your SKUs in the analyzed batch that have product descriptions that are less than 100 words long. These are good candidates for optimization.',
					),
					'batch2' => array(
						'explanation' => 'Competitor SKUs with product content < 100 words'
					)
				)
			),		
			array(
				'data_filter_id' => 'skus_fewer_150_product_content',
				'icon' => 'assess_report_seo_red.png',
				'label' => 'SKUs with product content < 150 words:',
				'has_competitor' => true,
				'question' => array(				
					'batch1' => array(
						'explanation' => 'The number of your SKUs in the analyzed batch that have product descriptions that are less than 150 words long.',
					),
					'batch2' => array(
						'explanation' => 'Competitor SKUs with product content < 150 words'
					)
				)
			),		
			array(
				'data_filter_id' => 'skus_fewer_competitor_optimized_keywords',
				'icon' => 'assess_report_seo_red.png',
				'is_default' => true,
				'label' => 'SKUs that have product content with fewer keywords from the title than competitor:','question' => array(				
					'explanation' => 'The number of SKUs that have product descriptions that have fewer keywords from the product title appearing in the product description than the competitor. These are good candidates for optimization. ',
				)			
			),
			array(
				'data_filter_id' => 'skus_zero_optimized_keywords',
				'icon' => 'assess_report_seo_red.png',
				'label' => 'SKUs that contain no keywords from the product title in the product description:',
				'has_competitor' => true,
				'is_default' => true,
				'question' => array(				
					'batch1' => array(
						'explanation' => 'The number of SKUs that have no keywords from the product title that appear in the product description text. These product descriptions should be re-written to include at least one keyword from the product title.',
					),
					'batch2' => array(
						'explanation' => 'Competitor SKUs that contain no keywords from the product title in the product description'
					)
				)
			),
			array(
				'data_filter_id' => 'skus_one_optimized_keywords',
				'icon' => 'assess_report_seo_red.png',
				'label' => 'SKUs that contain only 1 keyword from the product title in the product description:',
				'has_competitor' => true,
				'is_default' => true,
				'question' => array(				
					'batch1' => array(
						'explanation' => 'The number of SKUs for which only 1 keyword from the product title appears in the product description text. These product descriptions are good candidates to be re-written to include at least one more keyword.',
					),
					'batch2' => array(
						'explanation' => 'Competitor SKUs that contain 1 keyword from the product title in the product description'
					)
				)
			),
			array(
				'data_filter_id' => 'skus_two_optimized_keywords',
				'icon' => 'assess_report_seo_yellow.png',
				'label' => 'SKUs that contain 2 keywords from the product title in the product description:',
				'has_competitor' => true,
				'question' => array(				
					'batch1' => array(
						'explanation' => 'The number of SKUs for which 2 keywords from the product title appear in the product description text. These product descriptions are in good condition in terms of keyword optimization.',
					),
					'batch2' => array(
						'explanation' => 'Competitor SKUs that contain 2 keywords from the product title in the product description'
					)
				)
			),
			array(
				'data_filter_id' => 'skus_three_optimized_keywords',
				'icon' => 'assess_report_seo.png',
				'label' => 'SKUs that contain 3 or more keywords from the product title in the product description:',
				'has_competitor' => true,
				'question' => array(				
					'batch1' => array(
						'explanation' => 'The number of SKUs for which 3 keywords from the product title appear in the product description text. These product descriptions are in good condition in terms of keyword optimization.',
					),
					'batch2' => array(
						'explanation' => 'Competitor SKUs that contain 3 or more keywords from the product title in the product description'
					)
				)
			),
			array(
				'data_filter_id' => 'skus_title_less_than_70_chars',
				'icon' => 'assess_report_seo.png',
				'label' => 'SKUs with title < 70 characters:',
				'has_competitor' => true,
				'question' => array(				
					'batch1' => array(
						
					),
					'batch2' => array(
						
					)
				)
			),
			array(
				'data_filter_id' => 'skus_title_more_than_70_chars',
				'icon' => 'assess_report_seo.png',
				'label' => 'SKUs that have title of 70 characters or more:',
				'has_competitor' => true,
				'question' => array(				
					'batch1' => array(
						
					),
					'batch2' => array(
						
					)
				)
			),
			array(
				'data_filter_id' => 'skus_with_no_product_images',
				'icon' => 'assess_report_seo.png',
				'label' => 'SKUs with no product images:',
				'has_competitor' => true,
				'question' => array(				
					'batch1' => array(
						
					),
					'batch2' => array(
						
					)
				)
			),
			array(
				'data_filter_id' => 'skus_with_one_product_image',
				'icon' => 'assess_report_seo.png',
				'label' => 'SKUs with one product image:',
				'has_competitor' => true,
				'question' => array(				
					'batch1' => array(
						
					),
					'batch2' => array(
						
					)
				)
			),
			array(
				'data_filter_id' => 'skus_with_more_than_one_product_image',
				'icon' => 'assess_report_seo.png',
				'label' => 'SKUs with more than one product image:',
				'has_competitor' => true,
				'question' => array(				
					'batch1' => array(
						
					),
					'batch2' => array(
						
					)
				)
			),
			array(
				'data_filter_id' => 'skus_fewer_reviews_than_competitor',
				'icon' => 'assess_report_seo_red.png',
				'label' => 'SKUs that have fewer reviews than competitor:',	
				'question' => array(				
					'explanation' => 'The number of SKUs that have fewer reviews than the corresponding SKUs on the competitor’s site.'
				)
			),		
			array(
				'data_filter_id' => 'skus_zero_reviews',
				'icon' => 'assess_report_seo_red.png',
				'label' => 'SKUs that have 0 reviews:',	
				'has_competitor' => true,
				'question' => array(				
					'batch1' => array(
						
					),
					'batch2' => array(
						
					)
				)
			),
			array(
				'data_filter_id' => 'skus_one_four_reviews',
				'icon' => 'assess_report_seo_red.png',
				'label' => 'SKUs that have 1 - 4 reviews:',	
				'has_competitor' => true,
				'question' => array(				
					'batch1' => array(
						
					),
					'batch2' => array(
						
					)
				)
			),
			array(
				'data_filter_id' => 'skus_more_than_five_reviews',
				'icon' => 'assess_report_seo.png',
				'label' => 'SKUs that have 5 or more reviews:',	
				'has_competitor' => true,
				'question' => array(				
					'batch1' => array(
						
					),
					'batch2' => array(
						
					)
				)
			),
			array(
				'data_filter_id' => 'skus_more_than_hundred_reviews',
				'icon' => 'assess_report_seo.png',
				'label' => 'SKUs that have 100 or more reviews:',	
				'has_competitor' => true,
				'question' => array(				
					'batch1' => array(
						
					),
					'batch2' => array(
						
					)
				)
			),
			array(
				'data_filter_id' => 'skus_fewer_features_than_competitor',
				'icon' => 'assess_report_seo.png',
				'label' => 'SKUs that have fewer product specifications listed than competitor:',
				'question' => array(				
					'explanation' => ''
				)
			),
			array(
				'data_filter_id' => 'skus_features',
				'icon' => 'assess_report_seo.png',
				'label' => 'SKUs that have at least 1 product specification:',
				'has_competitor' => true,
				'question' => array(				
					'batch1' => array(
						'explanation' => 'SKUs that have at least 1 product specification. Examples of  specifications are a television’s resolution and number of HDMI ports. Each of these items is considered 1 specification.'
					),
					'batch2' => array(
						'explanation' => 'Competitor SKUs that have at least 1 feature'
					)
				)
			),		
			array(
				'data_filter_id' => 'skus_75_duplicate_content',
				'icon' => 'assess_report_seo_red.png',
				'label' => 'SKUs that have 75% or more duplicate content:',		
				'is_default' => true,
				'question' => array(					
					'explanation' => 'The number of SKUs that have 75% or more content that duplicates content for the same SKU on the competitor’s site. These SKUs are good candidates for optimization. They frequently indicate product content that contains manufacturer stock descriptions.'							
				)
			),
			array(
				'data_filter_id' => 'skus_50_duplicate_content',
				'icon' => 'assess_report_seo_red.png',
				'label' => 'SKUs that have 50% or more duplicate content:',			
				'question' => array(					
					'explanation' => 'The number of SKUs that have 50% or more content that duplicates content for the same SKU on the competitor’s site. These SKUs are good candidates for optimization. They frequently indicate product content that contains manufacturer stock descriptions.'				
				)
			),
			array(
				'data_filter_id' => 'skus_25_duplicate_content',
				'icon' => 'assess_report_seo_yellow.png',
				'label' => 'SKUs that have 25% or more duplicate content:',			
				'question' => array(					
					'explanation' => 'The number of SKUs that have 25% or more content that duplicates content for the same SKU on the competitor’s site.'				
				)
			),
			array(
				'data_filter_id' => 'skus_third_party_content',
				'icon' => 'assess_report_seo.png',
				'label' => 'SKUs that have third party content:',
				'has_competitor' => true,
				'question' => array(				
					'batch1' => array(
						'explanation' => 'The number of SKUs that contain third party content, such as from Webcollage or CNET. The name of the third party provider will be indicated in the results.',
					),
					'batch2' => array(
						'explanation' => 'Competitor SKUs that have third party content'
					)
				)
			),		
			array(
				'data_filter_id' => 'skus_pdfs',
				'icon' => 'assess_report_seo.png',
				'label' => 'SKUs that have PDFs:',
				'has_competitor' => true,
				'question' => array(				
					'batch1' => array(
						'explanation' => 'The number of SKUs that have PDFs. The number of PDFs for each SKU will be shown in the results table.',
					),
					'batch2' => array(
						'explanation' => 'Competitor SKUs that have PDFs'
					)
				)
			),
			array(
				'data_filter_id' => 'skus_videos',
				'icon' => 'assess_report_seo.png',
				'label' => 'SKUs that have videos:',
				'has_competitor' => true,
				'question' => array(				
					'batch1' => array(
						'explanation' => 'The number of SKUs that have product videos. The number of videos for each SKU will be shown in the results table.',
					),
					'batch2' => array(
						'explanation' => 'Competitor SKUs that have videos'
					)
				)
			)		
		);
	}
}
