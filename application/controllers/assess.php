<?php

if (!defined('BASEPATH'))
    exit('No direct script access allowed');

class Assess extends MY_Controller {

    function __construct() {
        parent::__construct();

        $this->load->library('form_validation');
        $this->load->library('helpers');
        $this->data['title'] = 'Assess';
        $this->load->model('imported_data_parsed_model');
        $this->load->model('keywords_model');
        $this->ion_auth->add_auth_rules(array(
            'compare_results' => true,
            'index' => true,
            'research_url' => true,
            'get_assess_info' => true,
            'get_board_view_snap' => true,
            'get_graph_batch_data' => true,
            'compare' => true,
            'filterCustomerByBatch' => true,
            'batches_get_all' => true,
            'customers_get_all' => true,
            'assess_save_columns_state' => true,
            'export_assess' => true,
            'remember_batches' => true,
            'getbatchvalues' => true,
			'save_summary_filters' => true,
			'get_summary_filters' => true,
			'save_summary_filters_order' => true,
            'deleteSecondaryMatch' => true,
            'getColumns' => true,
        ));
    }

//    public function delete_rows_db() {
//        $this->load->model('statistics_new_model');
//
//        $this->statistics_new_model->delete_rows_db();
//    }
//    public function delete_rows_db_imp() {
//        $this->load->model('statistics_new_model');
//
//        $this->statistics_new_model->delete_rows_db_imp();
//    }

    public function index() {

        $this->load->model('webshoots_model');
        $this->data['customers_list'] = $this->customers_list_new();
        $this->data['user_id'] = $this->ion_auth->get_user_id();
        $c_week = date("W", time());
        $c_year = date("Y", time());
        $this->data['ct_final'] = date("m.d.Y", time());
        $this->data['c_week'] = $c_week;
        $this->data['c_year'] = $c_year;
        $this->data['img_av'] = $this->webshoots_model->getWeekAvailableScreens($c_week, $c_year);
        $this->data['webshoots_model'] = $this->webshoots_model;
        // $this->data['rec'] = $this->webshoots_model->get_recipients_list();
        $this->render();
    }
    public function export_unmatches(){
        
        $this->load->model('statistics_new_model');
	$this->load->model('statistics_new_model');
        $batch_id = (int) trim($_GET['batch_id']);
        $cmp_selected = (int)trim(strtolower($_GET['cmp_selected']));
        $batch_name = $_GET['batch_name'];
        $sql = "select im.value, c.imported_data_id, c.similar_products_competitors 
                from statistics_new as c 
                left join  imported_data_parsed as im on im.imported_data_id = c.imported_data_id and im.key = 'url' 
                where batch_id =$batch_id ";
        $query = $this->db->query($sql);
        $results = $query->result_array();
        
        foreach($results as $k => $val){
            $similar_items = unserialize($val['similar_products_competitors']);

                if (count($similar_items) > 1) {
                    foreach ($similar_items as $key => $item) {
                       
                        if ($this->statistics_new_model->if_url_in_batch($item['imported_data_id'], $cmp_selected)) {
                            unset($results[$k]);
                            break;
                        }
                    }
                }else{
                    unset($results[$k]);
                }
        }
         $res_array = array();
         foreach($results as $k => $val){
            $res_array[] = array($val['imported_data_id'], $val['value']);
         }
        
        $res_array_keys = array('imported_data_id', 'URL');
        array_unshift($res_array, $res_array_keys);
        $this->load->helper('csv');
        array_to_csv($res_array, $batch_name . "(" . date("Y-m-d H:i") . ').csv');
        
    }

    public function compare_results() {

        $this->data['customer_list'] = $this->getCustomersByUserId();
        $this->data['category_list'] = $this->category_list();
        if (!empty($this->data['customer_list'])) {
            $this->data['batches_list'] = $this->batches_list();
        }
		
		$this->load->model('user_summary_settings', 'uss');
		if ($this->ion_auth->logged_in() && ($user_id = $this->ion_auth->get_user_id()))		
		{
			$user_setting_filters = $this->uss->findByAttributes(array('user_id' => $user_id, 'setting_id' => User_summary_settings::USER_SUMMARY_SETTING_FILTER));			
			$user_setting_filters_order = $this->uss->findByAttributes(array('user_id' => $user_id, 'setting_id' => User_summary_settings::USER_SUMMARY_SETTING_FILTER_ORDER));
		}
		else
		{			
			$user_setting_filters = $this->uss->findByAttributes(array('user_ip' => $_SERVER['REMOTE_ADDR'], 'setting_id' => User_summary_settings::USER_SUMMARY_SETTING_FILTER));	
			$user_setting_filters_order = $this->uss->findByAttributes(array('user_ip' => $_SERVER['REMOTE_ADDR'], 'setting_id' => User_summary_settings::USER_SUMMARY_SETTING_FILTER_ORDER));
		}
		
		$this->data['user_filters'] = $user_setting_filters && $user_setting_filters->setting_value ? json_decode($user_setting_filters->setting_value) : array();
		$this->data['user_filters_order'] = $user_setting_filters_order && $user_setting_filters_order->setting_value ? json_decode($user_setting_filters_order->setting_value) : array();

        $this->render();
    }

    private function customers_list_new() {
        $this->load->model('customers_model');
        $output = array();
        $customers_init_list = $this->customers_model->getAll();
        if (count($customers_init_list) > 0) {
            foreach ($customers_init_list as $key => $value) {
                $c_url = preg_replace('#^https?://#', '', $value->url);
                $c_url = preg_replace('#^www.#', '', $c_url);
                $mid = array(
                    'id' => $value->id,
                    'desc' => $value->description,
                    'image_url' => $value->image_url,
                    'name' => $value->name,
                    'name_val' => $value->name,
                    'c_url' => $c_url
                );
                $output[] = $mid;
            }
        }
        return $output;
    }

    private function get_keywords($title, $string) {
        $black_list = array('and', 'the', 'in', 'on', 'at', 'for');
        $title = trim(preg_replace(array('/\s+/', '/\(.*\)/'), array(' ', ''), $title));
        $string = trim(preg_replace('/\s+/', ' ', $string));
        $title_w = explode(' ', $title);
        $title_wc = count($title_w);
        $string_w = explode(' ', $string);
        $string_wc = count($string_w);
        $phrases = array();
        $i = 0;
        while ($title_wc - $i > 1) {
            for ($j = 0; $j < $i + 1; ++$j) {
                $needl = '';
                for ($k = $j; $k < $title_wc - $i + $j; ++$k) {
                    $needl .=$title_w[$k] . ' ';
                }
                $needl = trim($needl);
                $frc = substr_count(strtolower($string), strtolower($needl));
                $prc = ($frc * ($title_wc - $i)) / $string_wc * 100;
                if ($frc > 0 && $prc > 2) {//
                    $phrases[] = array(
                        'frq' => $frc,
                        'prc' => round($prc, 2),
                        'ph' => $needl
                    );
                }
            }
//            if(!empty($phrases)){
//                break;
//            }
            ++$i;
        }
        //*
        foreach ($black_list as $w) {
            foreach ($phrases as $key => $val) {
                $val['ph'] = substr($val['ph'], 0, strlen($w)) === $w ? substr($val['ph'], strlen($w)) : $val['ph'];
                $val['ph'] = substr($val['ph'], (-1) * strlen($w)) === $w ? substr($val['ph'], 0, strlen($val['ph']) - strlen($w)) : $val['ph'];
                $val['ph'] = trim($val['ph']);
                $pw = explode(' ', $val['ph']);
                if (count($pw) < 2) {
                    unset($phrases[$key]);
                }
            }
        }
        foreach ($phrases as $ar_key => $seo_pr) {
            foreach ($phrases as $ar_key1 => $seo_pr1) {
                if ($ar_key != $ar_key1 && $this->compare_str($seo_pr['ph'], $seo_pr1['ph']) && $seo_pr['frq'] >= $seo_pr1['frq']) {
                    unset($phrases[$ar_key1]);
                }
            }
        }
        foreach ($phrases as $ar_key => $seo_pr) {
            foreach ($phrases as $ar_key1 => $seo_pr1) {
                if ($ar_key != $ar_key1 && $this->compare_str($seo_pr['ph'], $seo_pr1['ph'])) {
                    if ($seo_pr['frq'] >= $seo_pr1['frq']) {
                        unset($phrases[$ar_key1]);
                    } else {
                        $phrases[$ar_key1]['frq']-=$seo_pr['frq'];
                        $akw = explode(' ', $seo_pr1['ph']);
                        $phrases[$ar_key1]['prc'] = round($phrases[$ar_key1]['frq'] * count($akw) / $string_wc * 100, 2);
                    }
                }
            }
        }
//*/
        return serialize($phrases);
    }
	
	private function buildObject(array $fields = array())
	{
		$r = new stdClass();
		
		foreach($fields as $key => $field)
		{
			if (is_array($field))
			{
				$input_field = $this->input->get($key);
			
				if (isset($field['callback']))
					$input_field = $field['callback']($input_field);
				
				$input_field = $input_field ?: $field['default'];
				
				$r->{$key} = $input_field;
			} else {
			
				//scalar value
				$r->{$key} = $field;
			}
		}
		
		return $r;
	}
	
    public function get_assess_info() {
        //Debugging
        $st_time = microtime(TRUE);
        
        $batch_id = $this->input->get('batch_id');

        if ($batch_id == 0) {
            $output = array(
                'sEcho' => 1,
                'iTotalRecords' => 0,
                'iTotalDisplayRecords' => 0,
                'iDisplayLength' => 10,
                'aaData' => array()
            );

            $this->output->set_content_type('application/json')
                    ->set_output(json_encode($output));			
        } else {			 
			$batch2_items_count = 0;
			
			if (!($txt_filter = $this->input->get('search_text'))) 
				if (!($txt_filter = $this->input->get('sSearch'))) 
					$txt_filter = '';			
			
           $build_assess_params = $this->buildObject(array(
				'date_from' => array( 'default' => '' ),
				'date_to' => array( 'default' => '' ),
				'price_diff' => array( 'default' => -1 ),
				'max_similar_item_count' => 0,
				'short_less_check' => $this->input->get('short_less_check'),
				'short_less' => array( 'default' => 20,  'callback' => function($value) {
					return (int)$value;
				}),
				'short_more_check' => $this->input->get('short_more_check'),
				'short_more' => array( 'default' => 0,  'callback' => function($value) {
					return (int)$value;
				}),
				'short_seo_phrases' => $this->input->get('short_seo_phrases'),
				'short_duplicate_content' => $this->input->get('short_duplicate_content'),
				'long_less_check' => $this->input->get('long_less_check'),
				'long_less' => array( 'default' => 50,  'callback' => function($value) {
					return (int)$value;
				}),
				'long_more_check' => $this->input->get('long_more_check'),
				'long_more' => array( 'default' => 0,  'callback' => function($value) {
					return (int)$value;
				}),
				'long_seo_phrases' => $this->input->get('long_seo_phrases'),
				'long_duplicate_content' => $this->input->get('long_duplicate_content'),
				'all_columns' => $this->input->get('sColumns'),
				'sort_columns' => $this->input->get('iSortCol_0'),
				'sort_dir' => $this->input->get('sSortDir_0'),
				'flagged' => $this->input->get('flagged'),
				'summaryFilterData' => array( 'default' => array(), 'callback' => function($value) {
					return $value ? explode(',', $value) : array();
				}),
				'compare_batch_id' => array( 'default' => null, 'callback' => function($value) {
					return (int)$value;
				}),
			));			
			
            $params = new stdClass();
            $params->batch_id = $batch_id;
            $params->txt_filter = $txt_filter;
            $params->date_from = $build_assess_params->date_from;
            $params->date_to = $build_assess_params->date_to;
            $batch2 = $this->input->get('batch2') && $this->input->get('batch2') == 'undefined' ? '' : $this->input->get('batch2');
            if ($batch2 === '') {
                $params->iDisplayLength = $this->input->get('iDisplayLength');
                $params->iDisplayStart = $this->input->get('iDisplayStart');
            }
			
            $results = $this->get_data_for_assess($params);
			
            $cmp = array();
//            //Debugging
//            $dur = microtime(true)-$st_time;
//            header('Mem-and-Time1: '.memory_get_usage().'-'.$dur);
//            $st_time=  microtime(true);

            if ($batch2 && $batch2 != 'all') {
                $this->load->model('batches_model');
                $build_assess_params->max_similar_item_count = 1;

                $customer_name = $this->batches_model->getCustomerUrlByBatch($batch2);

                foreach ($results as $val) {
                    $similar_items_data = array();
                    if (substr_count(strtolower($val->similar_products_competitors), strtolower($customer_name)) > 0) {

                        $similar_items = unserialize($val->similar_products_competitors);

                        if (count($similar_items) > 1) {
                            foreach ($similar_items as $key => $item) {
                                $tsp = '';

                                if (!empty($customer_name) && !empty($item['customer']) && $this->statistics_new_model->if_url_in_batch($item['imported_data_id'], $batch2)) {
                                    $parsed_attributes_unserialize_val = '';
                                    $parsed_anchors_unserialize_val = '';
                                    $parsed_meta_unserialize_val = '';
                                    $parsed_meta_unserialize_val_c = '';
                                    $parsed_model_unserialize_val = '';
                                    $parsed_meta_keywords_unserialize_val = '';
                                    $parsed_review_count_unserialize_val_count = '';
                                    $parsed_loaded_in_seconds_unserialize_val = '';
                                    $parsed_H1_Tags_unserialize_val = '';
                                    $parsed_H1_Tags_unserialize_val_count = '';
                                    $parsed_H2_Tags_unserialize_val = '';
                                    $parsed_column_reviews_unserialize_val = 0;
                                    $parsed_H2_Tags_unserialize_val_count = '';
                                    $parsed_average_review_unserialize_val_count = '';
                                    $title_seo_prases = array();
                                    $images_cmp = 'none';
                                    $video_count = 'none';
                                    $title_pa = 'none';
                                    $links_count = 'none';
                                    $parsed_column_features_unserialize_val_count = 0;
                                    $column_external_content = '';
                                    $cmpare = $this->statistics_new_model->get_compare_item($item['imported_data_id']);

                                    
                                    $parsed_anchors_unserialize = unserialize($cmpare->Anchors);

                                    $parsed_attributes_unserialize = unserialize($cmpare->parsed_attributes);

                                    if ($cmpare->title_keywords != '' && $cmpare->title_keywords != 'None') {
                                        $title_seo_prases = unserialize($cmpare->title_keywords);
                                    }
                                    if (!empty($title_seo_prases)) {

                                        $str_title_long_seo = '<table class="table_keywords_long">';
                                        foreach ($title_seo_prases as $pras) {
                                            $str_title_long_seo .= '<tr><td>' . $pras['ph'] . '</td><td class = "phr-density">  ' . $pras['prc']
                                                    . '%</td><td style="display:none;" class = "phr-frequency">  ' . $pras['frq'] . '</td></tr>';
                                        }
                                        $tsp = $str_title_long_seo . '</table>';
                                    }
                                    $HTags = unserialize($cmpare->HTags);

                                    if (isset($HTags['h1']) && $HTags['h1'] && $HTags['h1'] != '') {
                                        $H1 = $HTags['h1'];
                                        if (is_array($H1)) {
                                            $str_1 = '<table  class="table_keywords_long">';
                                            $str_1_Count = '<table  class="table_keywords_long">';
                                            foreach ($H1 as $h1) {
                                                $str_1.= '<tr><td>' . $h1 . '</td></tr>';
                                                $str_1_Count.='<tr><td>' . strlen($h1) . '</td></tr>';
                                            }
                                            $str_1 .= '</table>';
                                            $str_1_Count .= '</table>';
                                            $parsed_H1_Tags_unserialize_val = $str_1;
                                            $parsed_H1_Tags_unserialize_val_count = $str_1_Count;
                                        } else {
                                            $H1_Count = strlen($HTags['h1']);
                                            $parsed_H1_Tags_unserialize_val = '<table  class="table_keywords_long"><tr><td>' . $H1 . '</td></tr></table>';
                                            ;
                                            $parsed_H1_Tags_unserialize_val_count = '<table  class="table_keywords_long"><tr><td>' . $H1_Count . '</td></tr></table>';
                                            ;
                                        }
                                    }
                                    if (isset($HTags['h2']) && $HTags['h2'] && $HTags['h2'] != '') {
                                        $H2 = $HTags['h2'];
                                        if (is_array($H2)) {
                                            $str_2 = '<table  class="table_keywords_long">';
                                            $str_2_Count = '<table  class="table_keywords_long">';
                                            foreach ($H2 as $h2) {
                                                $str_2.= '<tr><td>' . $h2 . '</td></tr>';
                                                $str_2_Count.='<tr><td>' . strlen($h2) . '</td></tr>';
                                            }
                                            $str_2 .= '</table>';
                                            $str_2_Count .='</table>';
                                            $parsed_H2_Tags_unserialize_val = $str_2;
                                            $parsed_H2_Tags_unserialize_val_count = $str_2_Count;
                                        } else {
                                            $H1_Count = strlen($HTags['h2']);
                                            $parsed_H2_Tags_unserialize_val = '<table  class="table_keywords_long"><tr><td>' . $H2 . '</td></tr></table>';
                                            ;
                                            $parsed_H2_Tags_unserialize_val_count = '<table  class="table_keywords_long"><tr><td>' . $H2_Count . '</td></tr></table>';
                                            ;
                                        }
                                    }
                                    if (isset($parsed_attributes_unserialize['item_id']))
                                        $parsed_attributes_unserialize_val = $parsed_attributes_unserialize['item_id'];

                                    if (isset($parsed_attributes_unserialize['model']))
                                        $parsed_model_unserialize_val = $parsed_attributes_unserialize['model'];

                                    if (isset($parsed_attributes_unserialize['loaded_in_seconds']))
                                        $parsed_loaded_in_seconds_unserialize_val = $parsed_attributes_unserialize['loaded_in_seconds'];
//                       
                                    if (isset($parsed_attributes_unserialize['review_count']))
                                        $parsed_column_reviews_unserialize_val = $parsed_attributes_unserialize['review_count'];

                                    if (isset($parsed_attributes_unserialize['average_review']))
                                        $parsed_average_review_unserialize_val_count = $parsed_attributes_unserialize['average_review'];

                                    if (isset($parsed_attributes_unserialize['feature_count']))
                                        $parsed_column_features_unserialize_val_count = $parsed_attributes_unserialize['feature_count'];

                                    if (isset($parsed_attributes_unserialize['cnetcontent']) || isset($parsed_attributes_unserialize['webcollage']))
                                        $column_external_content = $this->column_external_content($parsed_attributes_unserialize['cnetcontent'], $parsed_attributes_unserialize['webcollage']);
                                    if (isset($parsed_attributes_unserialize['product_images']))
                                        $images_cmp = $parsed_attributes_unserialize['product_images'];
                                    if (isset($parsed_attributes_unserialize['video_count']))
                                        $video_count = $parsed_attributes_unserialize['video_count'];
                                    if (isset($parsed_attributes_unserialize['title']))
                                        $title_pa = $parsed_attributes_unserialize['title'];

                                    if (isset($parsed_anchors_unserialize['quantity']))
                                        $links_count = $parsed_anchors_unserialize['quantity'];

                                    $parsed_meta_unserialize = unserialize($cmpare->parsed_meta);

                                    if (isset($parsed_meta_unserialize['description'])) {
                                        $parsed_meta_unserialize_val = $parsed_meta_unserialize['description'];
                                        $parsed_meta_unserialize_val_c = count(explode(" ", $parsed_meta_unserialize_val));
                                        if ($parsed_meta_unserialize_val_c != 1)
                                            $parsed_meta_unserialize_val_count = $parsed_meta_unserialize_val_c;
                                    }
                                    else if (isset($parsed_meta_unserialize['Description'])) {
                                        $parsed_meta_unserialize_val = $parsed_meta_unserialize['Description'];
                                        $parsed_meta_unserialize_val_c = count(explode(" ", $parsed_meta_unserialize_val));
                                        if ($parsed_meta_unserialize_val_c != 1)
                                            $parsed_meta_unserialize_val_count = $parsed_meta_unserialize_val_c;
                                    }


//                                    if ($parsed_meta_unserialize['keywords']) {
//
//                                       $Meta_Keywords_un = "<table class='table_keywords_long'>";
//                                       $cnt_meta_un = explode(',', $parsed_meta_unserialize['keywords']);
//                                       $cnt_meta_count_un = count($cnt_meta_un);
//                                       foreach($cnt_meta_un as $cnt_m_un){
//                                           $cnt_m_un = trim($cnt_m_un);
//                                           $_count_meta_un = $this->keywords_appearence($parsed_meta_unserialize_val, $cnt_m_un);
//                                           $_count_meta_num_un = round(($_count_meta_un * $cnt_meta_count_un / $parsed_meta_unserialize_val_count) * 100, 2) . "%";
//                                           $Meta_Keywords_un .= "<tr><td>" . $cnt_m_un . "</td><td>".$_count_meta_num_un."</td></tr>";
//                                       }
//                                       $Meta_Keywords_un .= "</table>";
//                                       $parsed_meta_keywords_unserialize_val = $Meta_Keywords_un;
//
//                                   }

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
//                                                else if($cmpare->Short_Description){
//                                                    $_count_meta = $this->keywords_appearence($cmpare->Short_Description, $cnt_m);
//                                                    $_count_meta_num = round(($_count_meta * $cnt_meta_count / $cmpare->short_description_wc) * 100, 2) . "%";
//                                                    $Meta_Keywords_un .= "<tr><td>" . $cnt_m . "</td><td>".$_count_meta_num."</td></tr>";
//                                                }
//                                                else if($cmpare->Long_Description){
//                                                        $_count_meta = $this->keywords_appearence($cmpare->Short_Description, $cnt_m);
//                                                        $_count_meta_num = round(($_count_meta * $cnt_meta_count / $cmpare->short_description_wc) * 100, 2) . "%";
//                                                        $Meta_Keywords_un .= "<tr><td>" . $cnt_m . "</td><td>".$_count_meta_num."</td></tr>";
//                                                    }
                                        }
                                        $Meta_Keywords_un .= '</table>';
                                        $parsed_meta_keywords_unserialize_val = $Meta_Keywords_un;
                                    }




                                    $val->snap1 = $cmpare->snap;
                                    $val->imp_data_id1 = $item['imported_data_id'];
                                    $val->product_name1 = $cmpare->product_name;
                                    $val->item_id1 = $parsed_attributes_unserialize_val;
                                    $val->model1 = $parsed_model_unserialize_val;
                                    $val->url1 = $cmpare->url;
                                    $val->Page_Load_Time1 = $parsed_loaded_in_seconds_unserialize_val;
                                    $val->Short_Description1 = $cmpare->Short_Description;
                                    $val->short_description_wc1 = $cmpare->short_description_wc;
                                    $val->Meta_Keywords1 = $parsed_meta_keywords_unserialize_val;
                                    $val->Long_Description1 = $cmpare->Long_Description;
                                    $val->long_description_wc1 = $cmpare->long_description_wc;
                                    $val->Meta_Description1 = $parsed_meta_unserialize_val;
                                    $val->Meta_Description_Count1 = $parsed_meta_unserialize_val_count;
                                    $val->column_external_content1 = $column_external_content;
                                    $val->H1_Tags1 = $parsed_H1_Tags_unserialize_val;
                                    $val->H1_Tags_Count1 = $parsed_H1_Tags_unserialize_val_count;
                                    $val->H2_Tags1 = $parsed_H2_Tags_unserialize_val;
                                    $val->H2_Tags_Count1 = $parsed_H2_Tags_unserialize_val_count;
                                    $val->column_reviews1 = $parsed_column_reviews_unserialize_val;
                                    $val->average_review1 = $parsed_average_review_unserialize_val_count;
                                    $val->column_features1 = $parsed_column_features_unserialize_val_count;
                                    $val->title_seo_phrases1 = $tsp !== '' ? $tsp : 'None';
                                    $val->images_cmp1 = $images_cmp;
                                    $val->video_count1 = $video_count;
                                    $val->title_pa1 = $title_pa;
                                    $val->links_count1 = $title_pa;
                                    $cmpare->imported_data_id = $item['imported_data_id'];
                                    $batch2_items_count++;

                                    $similar_items_data[] = $cmpare;
                                    $val->similar_items = $similar_items_data;

                                    $cmp[] = $val;
                                    break;
                                }
                            }


                            //$cmp[] = $val;
                        }
                    }
                }
                $results = $cmp;
            }
//            //Debugging
//            $dur = microtime(true)-$st_time;
//            header('Mem-and-Time2: '.memory_get_usage().'-'.$dur);
//            $st_time=  microtime(true);

            if ($batch2 == 'all') {
                $max_similar_item_count = 1;
                $this->load->model('batches_model');
                $customer_name = $this->batches_model->getCustomerUrlByBatch($batch_id);
                $cmp = array();
                foreach ($results as $key1 => $val) {
                    $similar_items = unserialize($val->similar_products_competitors);
                    $similar_items_data = array();
                    if (count($similar_items) > 1) {
                        foreach ($similar_items as $key => $item) {
                            if (substr_count(strtolower($customer_name), strtolower($item['customer'])) == 0) {
                                $cmpare = $this->statistics_new_model->get_compare_item($similar_items[$key]['imported_data_id']);

                                $similar_items_data[] = $cmpare;
                            }
                        }
                        $sim_item_count = count($similar_items_data);
                        if ($sim_item_count > $max_similar_item_count) {
                            $max_similar_item_count = $sim_item_count;
                        }
                        $val->similar_items = $similar_items_data;
                        $results[$key1] = $val;
                    } else {
                        unset($results[$key1]);
                    }
                }
                $build_assess_params->max_similar_item_count = $max_similar_item_count;
            }

            $build_assess_params->batch2_items_count = $batch2_items_count;
            $output = $this->build_asses_table($results, $build_assess_params, $batch_id);
//            //Debugging
//            $dur = microtime(true)-$st_time;
//            header('Mem-and-Time4: '.memory_get_usage().'-'.$dur);
//            $st_time=  microtime(true);

            $this->output->set_content_type('application/json')
                    ->set_output(json_encode($output));
        }
		if (function_exists('fastcgi_finish_request '))
			fastcgi_finish_request();
    }

    public function filterBatchByCustomerName() {
        $this->load->model('batches_model');
        $this->load->model('customers_model');
        $customer_id = $this->customers_model->getIdByName($this->input->post('customer_name'));
        $batches = $this->batches_model->getAllByCustomer($customer_id);
        $batches_list = array();
        if (strtolower($this->input->post('customer_name')) == "select customer") {
            $batches = $this->batches_model->getAll();
            $batches_list[] = array('id' => 0, 'title' => 'Select batch');
        }

        if (!empty($batches)) {

            foreach ($batches as $batch) {

                $batches_list[] = array('id' => $batch->id, 'title' => $batch->title);
            }
        }
        $this->output->set_content_type('application/json')
                ->set_output(json_encode($batches_list));
    }

    public function filterCustomerByBatch() {
        $this->load->model('batches_model');
        $batch = $this->input->post('batch');
        $customer_name = $this->batches_model->getCustomerByBatch($batch);
        $this->output->set_content_type('application/json')
                ->set_output(json_encode(strtolower($customer_name)));
    }

    private function get_min_max($imported_data_id,$graphBuild) {
        $this->load->model('settings_model');
        $this->load->model('statistics_model');
        $this->load->model('statistics_new_model');
        $results = $this->statistics_new_model->getStatsData_min_max($imported_data_id,$graphBuild);
            return $results;
        }
    private function get_data_for_assess($params) {        
        $this->load->model('statistics_model');
        $this->load->model('statistics_new_model');
		
        if ($this->settings['statistics_table'] == "statistics_new") {
            $results = $this->statistics_new_model->getStatsData($params);
        } else {
            $results = $this->statistics_model->getStatsData($params);
        }
        //$results = $this->statistics_model->getStatsData($params);
        //$this->load->model('research_data_model');
        //$results = $this->research_data_model->getInfoForAssess($params);
        return $results;
    }

    private function get_report_presetted_pages($params) {
        $this->load->model('reports_model');
        $report = $this->reports_model->get_by_name($params->report_name);
        $report_pages = array();

        $report_page = new stdClass();
        $report_page->name = $report[0]->about_page_name;
        $report_page->order = intval($report[0]->about_page_order);
        $report_page->layout = $report[0]->about_page_layout;
        $report_page->body = $report[0]->about_page_body;
        $report_pages[] = $report_page;

        $report_page = new stdClass();
        $report_page->name = $report[0]->cover_page_name;
        $report_page->order = intval($report[0]->cover_page_order);
        $report_page->layout = $report[0]->cover_page_layout;
        $report_page->body = $report[0]->cover_page_body;
        $report_pages[] = $report_page;

        $report_page = new stdClass();
        $report_page->name = $report[0]->recommendations_page_name;
        $report_page->order = intval($report[0]->recommendations_page_order);
        $report_page->layout = $report[0]->recommendations_page_layout;
        $report_page->body = $report[0]->recommendations_page_body;
        $report_pages[] = $report_page;

        // sort by page order
        $this->sort_column = 'order';
        $this->sort_type = 'num';
        $this->sort_direction = 'asc';
        usort($report_pages, array("Assess", "assess_sort"));

        // replace patterns (#date#, #customer name#... etc)
        foreach ($report_pages as $page) {
            $page_body = $page->body;
            $page_body = str_replace('#date#', $params->current_date, $page_body);
            $page_body = str_replace('#customer name#', $params->customer_name, $page_body);
            $page->body = $page_body;
        }

        $report_parts = unserialize($report[0]->parts);

        $report_params = array(
            'report_pages' => $report_pages,
            'report_parts' => $report_parts,
        );
        return $report_params;
    }

    private function assess_sort($a, $b) {
        $column = $this->sort_column;
        $key1 = $a->$column;
        $key2 = $b->$column;

        if ($this->sort_type == "num") {
            $result = intval($key1) - intval($key2);
        } else {
            $result = strcmp(strval($key1), strval($key2));
        }

        if ($this->sort_direction == "asc") {
            return $result;
        } else {
            return -$result;
        }
    }

    private function assess_sort_ignore($a, $b) {
        $column = $this->sort_column;
        $key1 = $a->$column;
        $key2 = $b->$column;

        if ($this->sort_type == "num") {
            $result = intval($key1) - intval($key2);
        } else {
            $result = strcasecmp(strval($key1), strval($key2));
        }

        if ($this->sort_direction == "asc") {
            return $result;
        } else {
            return -$result;
        }
    }

    public function assess_report_download() {
        $report_name = 'Assess';

        $params = new stdClass();
        $params->batch_id = $this->input->get('batch_id');
        $params->batch_name = $this->input->get('batch_name');
        $results = $this->get_data_for_assess($params);

        $batch_id = $this->input->get('batch_id');
        $compare_batch_id = $this->input->get('compare_batch_id');
        $type_doc = $this->input->get('type_doc');

        $this->load->model('batches_model');
        $customer = $this->batches_model->getAllCustomerDataByBatch($params->batch_name);
        //$batch = $this->batches_model->getByName($batch_id);
        // Report options (layout)
        $assess_report_page_layout = 'Landscape';
        $user_id = $this->ion_auth->get_user_id();
        $key = 'research_assess_report_options';
        $existing_settings = $this->settings_model->get_value($user_id, $key);
        $batch_report_settings = $existing_settings[$batch_id];
        // if my report options pages layout is set
        if (!empty($batch_report_settings)) {
            if (!empty($batch_report_settings->assess_report_page_layout)) {
                $assess_report_page_layout = $batch_report_settings->assess_report_page_layout;
            }
        }

        $current_date = date('F j, Y'); //new DateTime(date('Y-m-d H:i:s'));
        $img_path = APPPATH . ".." . "/webroot/img/";
        $css_path = APPPATH . ".." . "/webroot/css/";

        $get_report_presetted_pages_params = new stdClass();
        $get_report_presetted_pages_params->report_name = $report_name;
        $get_report_presetted_pages_params->customer_name = $customer->name;
        $get_report_presetted_pages_params->current_date = $current_date;
        $report_params = $this->get_report_presetted_pages($get_report_presetted_pages_params);
        $report_presetted_pages = $report_params['report_pages'];
        $report_parts = $report_params['report_parts'];

        $build_assess_params = new stdClass();
        $build_assess_params->short_less = $this->input->get('short_less') == 'undefined' ? -1 : $this->input->get('short_less');
        $build_assess_params->short_more = $this->input->get('short_more') == 'undefined' ? -1 : $this->input->get('short_more');
        $build_assess_params->short_seo_phrases = $this->input->get('short_seo_phrases');
        $build_assess_params->short_duplicate_content = true;
        $build_assess_params->long_less = $this->input->get('long_less') == 'undefined' ? -1 : $this->input->get('long_less');
        $build_assess_params->long_more = $this->input->get('long_more') == 'undefined' ? -1 : $this->input->get('long_more');
        $build_assess_params->long_seo_phrases = true;
        $build_assess_params->long_duplicate_content = true;
        $build_assess_params->flagged = $this->input->get('flagged') == 'true' ? true : $this->input->get('flagged');
        $price_diff = $this->input->get('price_diff') == 'undefined' ? -1 : $this->input->get('price_diff');
        $build_assess_params->price_diff = $price_diff === 'true' ? true : false;
        if (intval($compare_batch_id) > 0) {
            $build_assess_params->compare_batch_id = $compare_batch_id;
        }

        $assess_data = $this->build_asses_table($results, $build_assess_params, $params->batch_id);

        $download_report_params = new stdClass();
        $download_report_params->img_path = $img_path;
        $download_report_params->css_path = $css_path;
        $download_report_params->own_logo = $img_path . "content-analytics.png";
        $download_report_params->customer_logo = $img_path . $customer->image_url;
        $download_report_params->batch_id = $params->batch_id;
        $download_report_params->batch_name = $params->batch_name;
        $download_report_params->current_date = $current_date;
        $download_report_params->report_presetted_pages = $report_presetted_pages;
        $download_report_params->report_parts = $report_parts;
        $download_report_params->assess_data = $assess_data;
        $download_report_params->assess_report_page_layout = $assess_report_page_layout;

        switch ($type_doc) {
            case 'pdf':
                $this->download_pdf($download_report_params);
                break;
            case 'doc':
                break;
            default:
                break;
        }
    }

    private function download_pdf($download_report_params) {
        $css_file = $download_report_params->css_path . 'assess_report.css';
        $report_data = $download_report_params->assess_data['ExtraData']['report'];
        $report_details = $download_report_params->assess_data['aaData'];
        $assess_report_page_layout = $download_report_params->assess_report_page_layout;

        $layout = 'L';
        if (!empty($assess_report_page_layout)) {
            if ($assess_report_page_layout == 'P') {
                $layout = 'P';
            }
        }


        $this->load->library('pdf');
        $pdf = $this->pdf->load();
        $pdf = new mPDF('', 'Letter', 0, '', 10, 10, 40, 10, 8, 8);
//        $pdf->showImageErrors = true;
//        $pdf->debug = true;
        $stylesheet = file_get_contents($css_file);
        $pdf->WriteHTML($stylesheet, 1);

        $header = '<table border=0 width=100%>';
        $header = $header . '<tr>';
        $header = $header . '<td style="text-align: left;">';
        $header = $header . '<img src="' . $download_report_params->own_logo . '" />';
        $header = $header . '</td>';
        $header = $header . '<td style="text-align: right;">';
        $header = $header . '<img src="' . $download_report_params->customer_logo . '" style="max-height:60px;max-width:300px;" />';
        $header = $header . '</td>';
        $header = $header . '</tr>';
        $header = $header . '</table>';
        $header = $header . '<hr color="#C31233" height="10">';
        $pdf->SetHTMLHeader($header);

        $pdf->SetHTMLFooter('<span style="font-size: 8px;">Copyright Р вЂ™Р’В© 2013 Content Solutions, Inc.</span>');

        $html = '';

        foreach ($download_report_params->report_presetted_pages as $page) {
            if ($page->order < 5000) {
                $pdf->AddPage($page->layout);
                $html = '';
                $html = $html . $page->body;
                $pdf->WriteHTML($html);
            }
        }

        if ($download_report_params->report_parts->summary == true) {
            $pdf->AddPage($layout);
            $html = '';

            $html = $html . '<table width=100% border=0>';
            $html = $html . '<tr><td style="text-align: left;font-weight: bold; font-style: italic;">Batch - ' . $download_report_params->batch_name . '</td><td style="text-align: right;font-weight: bold; font-style: italic;">' . $download_report_params->current_date . '</td></tr>';
            $html = $html . '<tr><td colspan="2"><hr height="3"></td></tr>';
            $html = $html . '</table>';

            $html = $html . '<table class="report" border="1" cellspacing="0" cellpadding="0">';

            $html = $html . '<tr><td class="tableheader">Summary</td></tr>';

            //if (!empty($report_data['summary']['total_items']) && intval($report_data['summary']['total_items'] > 0)) {
            $html = $html . '<tr><td class="report_td">';
            $html = $html . '<div><img class="icon" src="' . $download_report_params->img_path . 'assess_report_number.png">' . $report_data['summary']['total_items'] . ' total Items</div>';
            $html = $html . '</td></td></tr>';
            //}
            //if (!empty($report_data['summary']['items_priced_higher_than_competitors']) && intval($report_data['summary']['items_priced_higher_than_competitors'] > 0)) {
            $html = $html . '<tr><td class="report_td">';
            $html = $html . '<div><img class="icon" src="' . $download_report_params->img_path . 'assess_report_dollar.png">' . $report_data['summary']['items_priced_higher_than_competitors'] . ' items priced higher than competitors</div>';
            $html = $html . '</td></tr>';
            //}
            //if (!empty($report_data['summary']['items_have_more_than_20_percent_duplicate_content']) && intval($report_data['summary']['items_have_more_than_20_percent_duplicate_content'] > 0)) {
            $html = $html . '<tr><td class="report_td">';
            $html = $html . '<div><img class="icon" src="' . $download_report_params->img_path . 'assess_report_D.png">' . $report_data['summary']['items_have_more_than_20_percent_duplicate_content'] . ' items have more than 20% duplicate content</div>';
            $html = $html . '</td></tr>';
            //}
            //if (!empty($report_data['summary']['items_unoptimized_product_content']) && intval($report_data['summary']['items_unoptimized_product_content'] > 0)) {
            $html = $html . '<tr><td class="report_td">';
            $html = $html . '<div><img class="icon" src="' . $download_report_params->img_path . 'assess_report_seo.png">' . $report_data['summary']['items_unoptimized_product_content'] . ' items have non-keyword optimized product content</div>';
            $html = $html . '</td></tr>';
            //}

            if ($report_data['summary']['short_wc_total_not_0'] > 0 && $report_data['summary']['long_wc_total_not_0'] > 0) {
                $html = $html . '<tr><td class="report_td">';
                $html = $html . '<div><img class="icon" src="' . $download_report_params->img_path . 'assess_report_arrow_down.png">' . $report_data['summary']['items_short_products_content_short'] . ' items have short descriptions that are less than ' . $report_data['summary']['short_description_wc_lower_range'] . '</div>';
                $html = $html . '</td></tr>';
                $html = $html . '<tr><td class="report_td">';
                $html = $html . '<div><img class="icon" src="' . $download_report_params->img_path . 'assess_report_arrow_down.png">' . $report_data['summary']['items_long_products_content_short'] . ' items have long descriptions that are less than ' . $report_data['summary']['long_description_wc_lower_range'] . '</div>';
                $html = $html . '</td></tr>';
            } else {
                if ($report_data['summary']['short_wc_total_not_0'] == 0 && $report_data['summary']['long_wc_total_not_0'] != 0) {
                    $product_descriptions_that_are_too_short = $report_data['summary']['items_long_products_content_short'];
                    $product_descriptions_that_are_less_than = $report_data['summary']['long_description_wc_lower_range'];
                } else {
                    $product_descriptions_that_are_too_short = $report_data['summary']['items_short_products_content_short'];
                    $product_descriptions_that_are_less_than = $report_data['summary']['short_description_wc_lower_range'];
                }
                $html = $html . '<tr><td class="report_td">';
                $html = $html . '<div><img class="icon" src="' . $download_report_params->img_path . 'assess_report_arrow_down.png">' . $product_descriptions_that_are_too_short . ' items have long descriptions that are less than ' . $product_descriptions_that_are_less_than . '</div>';
                $html = $html . '</td></tr>';
            }

            if (!empty($report_data['summary']['absent_items_count']) && intval($report_data['summary']['absent_items_count'] > 0)) {
                $html = $html . '<tr><td class="report_td">';
                $html = $html . '<div><img class="icon" src="' . $download_report_params->img_path . 'assess_report_comparison.png">' . $report_data['summary']['absent_items_count'];
                $html = $html . ' items in ' . $report_data['summary']['compare_customer_name'] . ' - ' . $report_data['summary']['compare_batch_name'];
                $html = $html . ' are absent from ' . $report_data['summary']['own_batch_name'];
                $html = $html . '</div></td></tr>';
            }

            $html = $html . '</table>';

            $html = $html . '<table class="report recommendations" border="1" cellspacing="0" cellpadding="0">';

            $html = $html . '<tr><td class="tableheader">Recommendations</td></tr>';
            if ($report_data['recommendations']['items_priced_higher_than_competitors']) {
                $html = $html . '<tr><td class="report_td">';
                $html = $html . '<div><img class="icon" src="' . $download_report_params->img_path . 'assess_report_dollar.png">';
                $html = $html . $report_data['recommendations']['items_priced_higher_than_competitors'] . '</div>';
                $html = $html . '</td></tr>';
            }
            if ($report_data['recommendations']['items_have_more_than_20_percent_duplicate_content']) {
                $html = $html . '<tr><td class="report_td">';
                $html = $html . '<div><img class="icon" src="' . $download_report_params->img_path . 'assess_report_D.png">';
                $html = $html . $report_data['recommendations']['items_have_more_than_20_percent_duplicate_content'] . '</div>';
                $html = $html . '</td></tr>';
            }
            if ($report_data['recommendations']['items_short_products_content']) {
                $html = $html . '<tr><td class="report_td">';
                $html = $html . '<div><img class="icon" src="' . $download_report_params->img_path . 'assess_report_seo.png">';
                $html = $html . $report_data['recommendations']['items_short_products_content'] . '</div>';
                $html = $html . '</td></tr>';
            }
            if ($report_data['recommendations']['items_unoptimized_product_content']) {
                $html = $html . '<tr><td class="report_td">';
                $html = $html . '<div><img class="icon" src="' . $download_report_params->img_path . 'assess_report_arrow_up.png">';
                $html = $html . $report_data['recommendations']['items_unoptimized_product_content'] . '</div>';
                $html = $html . '</td></tr>';
            }

            $html = $html . '</table>';

            $html = $html . '<tr><td>';
            $html = $html . '</table>';

            $pdf->WriteHTML($html);
        }

        if ($download_report_params->report_parts->recommendations == true && count($report_details) > 0) {
            $data['report_details'] = $report_details;
            $report_recommendations_view = $this->load->view('research/product_recommendations_pdf', $data, true);
            $html = $report_recommendations_view;
            $pdf->AddPage($layout);
            $pdf->WriteHTML($html);
        }

        if ($download_report_params->report_parts->details == true && count($report_details) > 0) {
            $data['report_details'] = $report_details;
            $report_details_view = $this->load->view('research/product_details_pdf', $data, true);
            $html = $report_details_view;
            $pdf->AddPage($layout);
            $pdf->WriteHTML($html);
        }

        $comparison_data_array = $this->statistics_model->product_comparison($download_report_params->batch_id);
        if (count($comparison_data_array) > 0) {
            $html = '';
            foreach ($comparison_data_array as $comparison_data) {
                $pdf->AddPage($layout);
                $data['comparison_data'] = $comparison_data;
                $comparison_details_view = $this->load->view('research/comparison_details_pdf', $data, true);
                $html = $html . $comparison_details_view;
                $pdf->WriteHTML($html);
            }
        }

        foreach ($download_report_params->report_presetted_pages as $page) {
            if ($page->order > 5000) {
                $pdf->AddPage($page->layout);
                $html = '';
                $html = $html . $page->body;
                $pdf->WriteHTML($html);
            }
        }

        $pdf->Output('report.pdf', 'I');
    }

    public function assess_save_columns_state() {
        $this->load->model('settings_model');
        $user_id = $this->ion_auth->get_user_id();
        $key = 'research_assess';
        $value = $this->input->post('value');
        $description = 'Page settings -> columns state';
        $res = $this->settings_model->replace($user_id, $key, $value, $description);
        echo json_encode($res);
    }

    public function assess_save_urls() {
        $this->load->model('settings_model');
        $url = $this->input->post('url');
        $res = $this->settings_model->actual_url($url);
        echo $res;
    }

    public function research_url() {
        $serv = $_SERVER["REQUEST_URI"];
        $n = strpos($serv, "research_url?");
        $url = substr($serv, $n + 13);
        $this->load->model('settings_model');
        $res = $this->settings_model->friendly_url($url);

        redirect('assess/compare_results?' . $res, 'refresh');
    }

    public function comparison_detail() {
        $this->load->model('statistics_model');
        $batch_id = $this->input->post('batch_id');

        $comparison_data = $this->statistics_model->product_comparison($batch_id);

        $page = intval($this->uri->segment(3));
        $this->load->library('pagination');
        $config['base_url'] = $this->config->site_url() . '/assess/comparison_detail';
        $config['total_rows'] = count($comparison_data);
        $config['per_page'] = '1';
        $config['uri_segment'] = 3;
        $this->pagination->initialize($config);

        $data['comparison_data'] = $comparison_data[$page];
        $comparison_details_view = $this->load->view('research/comparison_details', $data, true);

        $comparison['comparison_pagination'] = $this->pagination->create_links();
        $comparison['comparison_detail'] = $comparison_details_view;

        $this->output->set_content_type('application/json')
                ->set_output(json_encode($comparison));
    }

    public function export_assess() {

        $this->load->model('statistics_new_model');
		//print_r($this->load->model('statistics_new_model'));
        $batch_id = (int) trim($_GET['batch_id']);
        $cmp_selected = trim(strtolower($_GET['cmp_selected']));
        $selected_columns = $_GET['checked_columns'];
        $selected_columns = explode(',', trim($selected_columns));
		
        $batch_name = $_GET['batch_name'];

        $summaryFilterData = $this->input->get('summaryFilterData');
        $summaryFilterData = $summaryFilterData ? explode(',', $summaryFilterData) : array();

		//print_r($selected_columns);
		//print_r($summaryFilterData);
        if (($key = array_search('snap', $selected_columns)) !== false) {
            unset($selected_columns[$key]);
        }
        $line = array('created' => 'Date', 'imp_data_id' => 'Item ID', 'product_name' => 'Product Name', 'url' => 'Url', 'Short_Description' => 'Short Description', 'short_description_wc' => 'Short Desc # Words', 'Long_Description' => 'Long Description', 'long_description_wc' => 'Long Desc # Words', 'short_seo_phrases' => ' Short Desc - Found SEO Keywords', 'long_seo_phrases' => ' Short Desc - Found SEO Keywords', 'price_diff' => 'Price', 'column_features' => 'Features', 'column_reviews' => 'Reviews', 'average_review' => 'Avg Review', 'title_seo_phrases' => 'Title Keywords');


        foreach ($line as $key => $val) {
            if (!in_array($key, $selected_columns)) {
                unset($line[$key]);
            }
        }

        if (count($line) == 0) {
            $this->load->helper('csv');
            array_to_csv(array(), date("Y-m-d H:i") . '.csv');
        }
        if (empty($batch_id) || $batch_id == 0) {
            $batch_id = '';
            $qnd = '';
        } else {
            $qnd = " WHERE `s`.`batch_id` = $batch_id";
        }

        $params = new stdClass();
        $params->batch_id = $batch_id;
        $results = $this->get_data_for_assess($params);
		
        $cmp = array();
        if ($cmp_selected != '' && $cmp_selected != 0 && $cmp_selected != 'all') {

            $this->load->model('batches_model');
            $max_similar_item_count = 1;
            $customer_name = $this->batches_model->getCustomerUrlByBatch($cmp_selected);

            foreach ($results as $val) {
                $val->Long_Description = $val->long_description;
                $val->Short_Description = $val->short_description;
                $similar_items_data = array();
                if (substr_count(strtolower($val->similar_products_competitors), strtolower($customer_name)) > 0) {
                    $similar_items = unserialize($val->similar_products_competitors);
                    if (count($similar_items) > 1) {
                        foreach ($similar_items as $key => $item) {
                            if (!empty($customer_name) && !empty($item['customer']) && $this->statistics_new_model->if_url_in_batch($item['imported_data_id'], $cmp_selected)) {
                                $den_for_gap = 0;
                                $parsed_attributes_unserialize_val = '';
                                $parsed_meta_unserialize_val = '';
                                $parsed_meta_unserialize_val_c = '';
                                $parsed_attributes_column_features_unserialize_val = 0;
                                $parsed_model_unserialize_val = '';
                                $parsed_meta_keywords_unserialize_val = '';
                                $parsed_loaded_in_seconds_unserialize_val = '';
                                $parsed_average_review_unserialize_val_count = '';
                                $column_external_content = '';
                                $parsed_review_count_unserialize_val_count = 0;
                                $cmpare = $this->statistics_new_model->get_compare_item($item['imported_data_id']);

                                $parsed_attributes_unserialize = unserialize($cmpare->parsed_attributes);
                                if (isset($parsed_attributes_unserialize['cnetcontent']) || isset($parsed_attributes_unserialize['webcollage']))
                                    $column_external_content = $this->column_external_content($parsed_attributes_unserialize['cnetcontent'], $parsed_attributes_unserialize['webcollage']);

                                if (isset($parsed_attributes_unserialize['feature_count']))
                                    $parsed_attributes_column_features_unserialize_val = $parsed_attributes_unserialize['feature_count'];
                                //if (isset($parsed_attributes_unserialize['item_id']))
                                //    $parsed_attributes_unserialize_val = $parsed_attributes_unserialize['item_id'];
                                if (isset($parsed_attributes_unserialize['model']))
                                    $parsed_model_unserialize_val = $parsed_attributes_unserialize['model'];
                                if (isset($parsed_attributes_unserialize['loaded_in_seconds']))
                                    $parsed_loaded_in_seconds_unserialize_val = $parsed_attributes_unserialize['loaded_in_seconds'];
                                if (isset($parsed_attributes_unserialize['average_review']))
                                    $parsed_average_review_unserialize_val_count = $parsed_attributes_unserialize['average_review'];
                                if (isset($parsed_attributes_unserialize['review_count']))
                                    $parsed_review_count_unserialize_val_count = $parsed_attributes_unserialize['review_count'];

                                $parsed_meta_unserialize = unserialize($cmpare->parsed_meta);

                                if (isset($parsed_meta_unserialize['description'])) {
                                    $parsed_meta_unserialize_val = $parsed_meta_unserialize['description'];
                                    $parsed_meta_unserialize_val_c = count(explode(" ", $parsed_meta_unserialize_val));
                                    if ($parsed_meta_unserialize_val_c != 1)
                                        $parsed_meta_unserialize_val_count = $parsed_meta_unserialize_val_c;
                                }
                                else if (isset($parsed_meta_unserialize['Description'])) {
                                    $parsed_meta_unserialize_val = $parsed_meta_unserialize['Description'];
                                    $parsed_meta_unserialize_val_c = count(explode(" ", $parsed_meta_unserialize_val));
                                    if ($parsed_meta_unserialize_val_c != 1)
                                        $parsed_meta_unserialize_val_count = $parsed_meta_unserialize_val_c;
                                }



                                if (isset($parsed_meta_unserialize['keywords'])) {
                                    $Meta_Keywords_un = "";
                                    $cnt_meta = explode(',', $parsed_meta_unserialize['keywords']);
                                    $cnt_meta_count = count($cnt_meta);
                                    $_count_meta = 0;
                                    foreach ($cnt_meta as $cnt_m) {
                                        $cnt_m = trim($cnt_m);
                                        if ($cmpare->Short_Description || $cmpare->Long_Description) {
                                            $_count_meta = $this->keywords_appearence($cmpare->Long_Description . $cmpare->Short_Description, $cnt_m);
                                            $_count_meta_num = round(($_count_meta * $cnt_meta_count / ($cmpare->long_description_wc + $cmpare->short_description_wc)) * 100, 2);

                                            if ($_count_meta_num >= 2) {
                                                $den_for_gap = $_count_meta_num;
                                            }

                                            $Meta_Keywords_un .= $cnt_m . "  - " . $_count_meta_num . "%, ";
                                        }
                                    }

                                    $parsed_meta_keywords_unserialize_val = $Meta_Keywords_un;
                                }
                                //export title keywords compare
                                $title_seo_prases = array();
                                 if ($cmpare->title_keywords != '' && $cmpare->title_keywords != 'None') {
                                        $title_seo_prases = unserialize($cmpare->title_keywords);
                                    }
                                if (!empty($title_seo_prases)) {
                                    $title_seo_phrases = '';
                                    foreach ($title_seo_prases as $pras) {
                                        $title_seo_phrases .= $pras['ph'] . ' - ' . $pras['prc'] . '%,  ';
                                    }
                                }


                                //$cmpare->item_id = $parsed_attributes_unserialize_val;
                                $cmpare->model = $parsed_model_unserialize_val;
                                $cmpare->den_for_gap = $den_for_gap;
                                $cmpare->Page_Load_Time = $parsed_loaded_in_seconds_unserialize_val;

                                $cmpare->Meta_Keywords = $parsed_meta_keywords_unserialize_val;
                                $cmpare->column_features = $parsed_attributes_column_features_unserialize_val;
                                $cmpare->column_external_content = $column_external_content;

                                $cmpare->Meta_Description = $parsed_meta_unserialize_val;
                                $cmpare->Meta_Description_Count = $parsed_meta_unserialize_val_count;
                                $cmpare->average_review = $parsed_average_review_unserialize_val_count;
                                $cmpare->review_count = $parsed_review_count_unserialize_val_count;
                                $cmpare->title_seo_phrases = $title_seo_phrases;

                                $similar_items_data[] = $cmpare;
                                $val->similar_items = $similar_items_data;

                                $cmp[] = $val;
                                break;
                            }
                        }
                    }
                }
            }
            $results = $cmp;
        }

        if ($cmp_selected == 'all') {
            $max_similar_item_count = 0;
            $this->load->model('batches_model');
            $customer_name = $this->batches_model->getCustomerUrlByBatch($batch_id);

            foreach ($results as $key1 => $val) {
                $similar_items = unserialize($val->similar_products_competitors);
                $similar_items_data = array();
                if (count($similar_items) > 1) {
                    foreach ($similar_items as $key => $item) {
                        if (substr_count(strtolower($customer_name), strtolower($item['customer'])) == 0) {
//                                $cmpare = $this->statistics_new_model->get_compare_item($similar_items[$key]['imported_data_id']);
//                                $data = $this->export_assess_cmp($similar_items[$key]['imported_data_id'],$selected_columns);
//                                echo '<pre>';
//                                print_r($data); exit();
//                                $similar_items_data[] = $cmpare;
//                              $similar_items_data[] = $similar_items[$key]['imported_data_id'];
//                            
                            $cmpare = $this->statistics_new_model->get_compare_item($similar_items[$key]['imported_data_id']);

                            $similar_items_data[] = $cmpare;
                        }
                    }
                    $sim_item_count = count($similar_items_data);
                    if ($sim_item_count > $max_similar_item_count) {
                        $max_similar_item_count = $sim_item_count;
                    }
                    $val->similar_items = $similar_items_data;

                    $results[$key1] = $val;
                } else {
                    unset($results[$key1]);
                }
            }
        }
        $res_array = array();
        $H1_tag_count = 0;
        $H2_tag_count = 0;
        $H1_tag_count_for_sim = 0;
        $H2_tag_count_for_sim = 0;
//            if (in_array('H2_Tags', $selected_columns)) {
        foreach ($results as $key => $row) {

            $pars_atr = $this->imported_data_parsed_model->getByImId($row->imported_data_id);


            if (in_array('H1_Tags', $selected_columns) && $pars_atr['HTags']['h1'] && $pars_atr['HTags']['h1'] != '') {
                $H1 = $pars_atr['HTags']['h1'];
                if (is_array($H1)) {

                    if (count($H1) > $H1_tag_count) {
                        $H1_tag_count = count($H1);
                    }
                } else {

                    if ($H1_tag_count == 0) {
                        $H1_tag_count = 1;
                    }
                }
            }

            if (in_array('H2_Tags', $selected_columns) && $pars_atr['HTags']['h2'] && $pars_atr['HTags']['h2'] != '') {
                $H2 = $pars_atr['HTags']['h2'];
                if (is_array($H2)) {

                    if (count($H2) > $H2_tag_count) {
                        $H2_tag_count = count($H2);
                    }
                } else {

                    if ($H2_tag_count == 0) {
                        $H2_tag_count = 1;
                    }
                }
            }

//Htag_count for similar 
            $sim_item_row = $row->similar_items;
            $imp_data_id_for_sim = $sim_item_row[0]->imported_data_id;
            $pars_atr_for_sim = $this->imported_data_parsed_model->getByImId($imp_data_id_for_sim);

            if (in_array('H1_Tags', $selected_columns) && $pars_atr_for_sim['HTags']['h1'] && $pars_atr_for_sim['HTags']['h1'] != '') {
                $H1 = $pars_atr_for_sim['HTags']['h1'];
                if (is_array($H1)) {

                    if (count($H1) > $H1_tag_count_for_sim) {
                        $H1_tag_count_for_sim = count($H1);
                    }
                } else {

                    if ($H1_tag_count_for_sim == 0) {
                        $H1_tag_count_for_sim = 1;
                    }
                }
            }

            if (in_array('H2_Tags', $selected_columns) && $pars_atr_for_sim['HTags']['h2'] && $pars_atr_for_sim['HTags']['h2'] != '') {
                $H2 = $pars_atr_for_sim['HTags']['h2'];
                if (is_array($H2)) {

                    if (count($H2) > $H2_tag_count_for_sim) {
                        $H2_tag_count_for_sim = count($H2);
                    }
                } else {

                    if ($H2_tag_count_for_sim == 0) {
                        $H2_tag_count_for_sim = 1;
                    }
                }
            }
        }
//            }

        $arr = array();
			//print_r($results);
        foreach ($results as $key => $row) {
            $sim = $row->similar_items;
            $pars = unserialize($row->parsed_attributes);
            $sim_pars = unserialize($sim[0]->parsed_attributes);

            $success_filter_entries =array();
   
                if ($row->short_description) {
                    $short_desc_1 = $row->short_description;
                }else{
                    $short_desc_1 = '';
                }
                if ($row->long_description) {
                    $long_desc_1 = $row->long_description;
                }else{
                    $long_desc_1 = '';
                }
                $desc_1 = $short_desc_1.' '.$long_desc_1 ;
                
                if ($sim[0]->Short_Description) {
                    $short_desc_2 = $sim[0]->Short_Description;
                }else{
                    $short_desc_2 = '';
                }
                if ($sim[0]->Long_Description) {
                    $long_desc_2 = $sim[0]->Long_Description;
                }else{
                    $long_desc_2 = '';
                }
                $desc_2 = $short_desc_2.' '.$long_desc_2 ;
               
                if (strcasecmp($desc_1, $desc_2) <= 0)
					similar_text($desc_1, $desc_2, $percent);
				else
					similar_text($desc_2, $desc_1, $percent);
					
                $percent = number_format($percent, 2);
			
				if ($percent >= 25)
				{
					
					$this->filterBySummaryCriteria('skus_25_duplicate_content', $summaryFilterData, $success_filter_entries);
                                }
				
				if ($percent >= 50)
				{
					
					$this->filterBySummaryCriteria('skus_50_duplicate_content', $summaryFilterData, $success_filter_entries);
				}
				
				if ($percent >= 75)
				{
					
					$this->filterBySummaryCriteria('skus_75_duplicate_content', $summaryFilterData, $success_filter_entries);
				}

                                 
                                if (isset($pars['pdf_count']) && $pars['pdf_count'])
                                {				

                                        $this->filterBySummaryCriteria('skus_pdfs', $summaryFilterData, $success_filter_entries);	
                                }
           
            
                                if (isset($sim_pars['pdf_count']) && $sim_pars['pdf_count'])
                                {				
                                        $this->filterBySummaryCriteria('skus_pdfs_competitor', $summaryFilterData, $success_filter_entries);	
                                 
                                }
            
            
                                if ($pars['feature_count'] < $sim_pars['feature_count'])
				{
					
					$this->filterBySummaryCriteria('skus_fewer_features_than_competitor', $summaryFilterData, $success_filter_entries);						
				}
				
				if ($pars['review_count'] < $sim_pars['review_count('])
				{
				
					$this->filterBySummaryCriteria('skus_fewer_reviews_than_competitor', $summaryFilterData, $success_filter_entries);	
				}
				
				if ($pars['feature_count'])
				{					
				
					$this->filterBySummaryCriteria('skus_features', $summaryFilterData, $success_filter_entries);	
				}
					
				if ($sim_pars['feature_count'])
				{					
				
					$this->filterBySummaryCriteria('skus_features_competitor', $summaryFilterData, $success_filter_entries);	
				}
								
				if (!$pars['review_count'])
				{										
					$this->filterBySummaryCriteria('skus_zero_reviews', $summaryFilterData, $success_filter_entries);	
				}
				if ($pars['review_count'] >= 1 && $pars['review_count'] <= 4)
				{										
					$this->filterBySummaryCriteria('skus_one_four_reviews', $summaryFilterData, $success_filter_entries);	
				}
				if ($pars['review_count'] >= 5)
				{										
					$this->filterBySummaryCriteria('skus_more_than_five_reviews', $summaryFilterData, $success_filter_entries);	
				}
				if ($pars['review_count'] >= 100)
				{										
					$this->filterBySummaryCriteria('skus_more_than_hundred_reviews', $summaryFilterData, $success_filter_entries);	
				}
				
				if (!$sim_pars['review_count'])
				{										
					$this->filterBySummaryCriteria('skus_zero_reviews_competitor', $summaryFilterData, $success_filter_entries);	
				}
				if ($sim_pars['review_count'] >= 1 && $sim_pars['review_count'] <= 4)
				{										
					$this->filterBySummaryCriteria('skus_one_four_reviews_competitor', $summaryFilterData, $success_filter_entries);	
				}
				if ($sim_pars['review_count'] >= 5)
				{										
					$this->filterBySummaryCriteria('skus_more_than_five_reviews_competitor', $summaryFilterData, $success_filter_entries);	
				}
				if ($sim_pars['review_count'] >= 100)
				{										
					$this->filterBySummaryCriteria('skus_more_than_hundred_reviews_competitor', $summaryFilterData, $success_filter_entries);	
				}															                        
                                
			$batch1_filtered_title_percents = substr_count($row->title_seo_phrases, '%');
			$batch2_filtered_title_percents = substr_count($sim[0]->title_seo_phrases, '%');
			
			if ($batch1_filtered_title_percents < $batch2_filtered_title_percents)
			{				
				$this->filterBySummaryCriteria('skus_fewer_competitor_optimized_keywords', $summaryFilterData, $success_filter_entries);					
			}
			
			if (!$batch1_filtered_title_percents)
			{			
				$this->filterBySummaryCriteria('skus_zero_optimized_keywords', $summaryFilterData, $success_filter_entries);
			}
			
			if ($batch1_filtered_title_percents >= 1)
			{			
				$this->filterBySummaryCriteria('skus_one_optimized_keywords', $summaryFilterData, $success_filter_entries);		
			}
				
			if ($batch1_filtered_title_percents >= 2)
			{			
				$this->filterBySummaryCriteria('skus_two_optimized_keywords', $summaryFilterData, $success_filter_entries);			
			}
				
			if ($batch1_filtered_title_percents >= 3)
			{			
				$this->filterBySummaryCriteria('skus_three_optimized_keywords', $summaryFilterData, $success_filter_entries);
			}
			
			if (!$batch2_filtered_title_percents)
			{			
				$this->filterBySummaryCriteria('skus_zero_optimized_keywords_competitor', $summaryFilterData, $success_filter_entries);
			}
			
			if ($batch2_filtered_title_percents >= 1)
			{			
				$this->filterBySummaryCriteria('skus_one_optimized_keywords_competitor', $summaryFilterData, $success_filter_entries);		
			}
				
			if ($batch2_filtered_title_percents >= 2)
			{			
				$this->filterBySummaryCriteria('skus_two_optimized_keywords_competitor', $summaryFilterData, $success_filter_entries);			
			}
				
			if ($batch2_filtered_title_percents >= 3)
			{			
				$this->filterBySummaryCriteria('skus_three_optimized_keywords_competitor', $summaryFilterData, $success_filter_entries);
			}
                                
            
                        
                        if ($row->column_external_content)
			{
			
				$this->filterBySummaryCriteria('skus_third_party_content', $summaryFilterData, $success_filter_entries);
			}
			
			if ($sim[0]->column_external_content)
			{
			
				$this->filterBySummaryCriteria('skus_third_party_content_competitor', $summaryFilterData, $success_filter_entries);
			}	
            
            
                        
                       
                        $first_general_description_size = $row->short_description_wc + $row->long_description_wc;
			$second_general_description_size =$sim[0]->long_description_wc + $sim[0]->short_description_wc;
			
			if ($first_general_description_size < $second_general_description_size) {
               
				$this->filterBySummaryCriteria('skus_shorter_than_competitor_product_content', $summaryFilterData, $success_filter_entries);
            }
			
			if ($first_general_description_size > $second_general_description_size) {
               
				$this->filterBySummaryCriteria('skus_longer_than_competitor_product_content', $summaryFilterData, $success_filter_entries);
            }
			
			if ($first_general_description_size == $second_general_description_size) {
               
				$this->filterBySummaryCriteria('skus_same_competitor_product_content', $summaryFilterData, $success_filter_entries);
            }
			
			// For Batch 1
			if ($first_general_description_size < 50) {
				
				$this->filterBySummaryCriteria('skus_fewer_50_product_content', $summaryFilterData, $success_filter_entries);
			}
			
			if ($first_general_description_size < 100) {
				
				$this->filterBySummaryCriteria('skus_fewer_100_product_content', $summaryFilterData, $success_filter_entries);
			}
			
			if ($first_general_description_size < 150) {
				
				$this->filterBySummaryCriteria('skus_fewer_150_product_content', $summaryFilterData, $success_filter_entries);
			}
			
			// For Competitor (Batch 2)
			if ($second_general_description_size < 50) {
			
				$this->filterBySummaryCriteria('skus_fewer_50_product_content_competitor', $summaryFilterData, $success_filter_entries);
			}
			
			if ($second_general_description_size < 100) {
				$this->filterBySummaryCriteria('skus_fewer_100_product_content_competitor', $summaryFilterData, $success_filter_entries);
			}
			
			if ($second_general_description_size < 150) {
				$this->filterBySummaryCriteria('skus_fewer_150_product_content_competitor', $summaryFilterData, $success_filter_entries);
			}
            
            
//                        if ($row->lower_price_exist == true) {									
//				$this->filterBySummaryCriteria('assess_report_items_priced_higher_than_competitors', $build_assess_params->summaryFilterData, $success_filter_entries);	
//			}
			

   
			if ($this->checkSuccessFilterEntries($success_filter_entries, $summaryFilterData)){
				$arr[] = $row;
                         }
            
           
        };
        
           
            foreach ($arr as $key => $row) {
                $row->Short_Description = $row->short_description; 
                $row->Long_Description = $row->long_description;
                
                $row = (array) $row;
                foreach ($line as $k => $v) {
                    $res_array[$key][$k] = $row[$k];
                }
                $row = (object) $row;
                
                $pars_atr = $this->imported_data_parsed_model->getByImId($row->imported_data_id);
                //print_r($pars_atr);die;
                //item_id
                //if(in_array('item_id', $selected_columns)){
                //    $res_array[$key]['item_id'] = $pars_atr['parsed_attributes']['item_id']?$pars_atr['parsed_attributes']['item_id']:' ';
                //}
				if(in_array('imp_data_id', $selected_columns)){
                    $res_array[$key]['imp_data_id'] = $pars_atr['parsed_attributes']['item_id']?$pars_atr['parsed_attributes']['item_id']:' ';
					
                }
                //model
                if(in_array('model', $selected_columns)){
                    $res_array[$key]['model'] = $pars_atr['parsed_attributes']['model']?$pars_atr['parsed_attributes']['model']:'';
                }
                //meta keywords
                if(in_array('Meta_Keywords', $selected_columns)){
                     $parsed_meta_keywords_unserialize_val = "";
                     if ($pars_atr['parsed_meta']['keywords']) {
                                       $Meta_Keywords_un = "";
                                       $cnt_meta = "";
                                            $cnt_meta = explode(',', $pars_atr['parsed_meta']['keywords']);
                                            $cnt_meta_count = count($cnt_meta);
                                            $_count_meta = 0;
                                            foreach($cnt_meta as $cnt_m){
                                                $cnt_m = trim($cnt_m);
                                                if($row->Short_Description || $row->Long_Description){
                                                    $_count_meta = $this->keywords_appearence($row->Long_Description.$row->Short_Description, $cnt_m);
                                                    $_count_meta_num = round(($_count_meta * $cnt_meta_count / ($row->long_description_wc + $row->short_description_wc)) * 100, 2) . "%";
                                                    $Meta_Keywords_un .=  $cnt_m . "  - ".$_count_meta_num.", ";
                                                }
                                            
                                                }
                                            
                                            $parsed_meta_keywords_unserialize_val = $Meta_Keywords_un;
                                        }
                    $res_array[$key]['meta_keywords'] = $parsed_meta_keywords_unserialize_val?$parsed_meta_keywords_unserialize_val:'';
                    
                }

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

            if ($sim[0]->Short_Description) {
                $short_desc_2 = $sim[0]->Short_Description;
            } else {
                $short_desc_2 = '';
            }
            if ($sim[0]->Long_Description) {
                $long_desc_2 = $sim[0]->Long_Description;
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

                $this->filterBySummaryCriteria('skus_25_duplicate_content', $summaryFilterData, $success_filter_entries);
            }

            if ($percent >= 50) {

                $this->filterBySummaryCriteria('skus_50_duplicate_content', $summaryFilterData, $success_filter_entries);
            }

            if ($percent >= 75) {

                $this->filterBySummaryCriteria('skus_75_duplicate_content', $summaryFilterData, $success_filter_entries);
            }


            if (isset($pars['pdf_count']) && $pars['pdf_count']) {

                $this->filterBySummaryCriteria('skus_pdfs', $summaryFilterData, $success_filter_entries);
            }


            if (isset($sim_pars['pdf_count']) && $sim_pars['pdf_count']) {
                $this->filterBySummaryCriteria('skus_pdfs_competitor', $summaryFilterData, $success_filter_entries);
            }


            if ($pars['feature_count'] < $sim_pars['feature_count']) {

                $this->filterBySummaryCriteria('skus_fewer_features_than_competitor', $summaryFilterData, $success_filter_entries);
            }

            if ($pars['review_count'] < $sim_pars['review_count(']) {

                $this->filterBySummaryCriteria('skus_fewer_reviews_than_competitor', $summaryFilterData, $success_filter_entries);
            }

            if ($pars['feature_count']) {

                $this->filterBySummaryCriteria('skus_features', $summaryFilterData, $success_filter_entries);
            }

            if ($sim_pars['feature_count']) {

                $this->filterBySummaryCriteria('skus_features_competitor', $summaryFilterData, $success_filter_entries);
            }

            if (!$pars['review_count']) {
                $this->filterBySummaryCriteria('skus_zero_reviews', $summaryFilterData, $success_filter_entries);
            }
            if ($pars['review_count'] >= 1 && $pars['review_count'] <= 4) {
                $this->filterBySummaryCriteria('skus_one_four_reviews', $summaryFilterData, $success_filter_entries);
            }
            if ($pars['review_count'] >= 5) {
                $this->filterBySummaryCriteria('skus_more_than_five_reviews', $summaryFilterData, $success_filter_entries);
            }
            if ($pars['review_count'] >= 100) {
                $this->filterBySummaryCriteria('skus_more_than_hundred_reviews', $summaryFilterData, $success_filter_entries);
            }

            if (!$sim_pars['review_count']) {
                $this->filterBySummaryCriteria('skus_zero_reviews_competitor', $summaryFilterData, $success_filter_entries);
            }
            if ($sim_pars['review_count'] >= 1 && $sim_pars['review_count'] <= 4) {
                $this->filterBySummaryCriteria('skus_one_four_reviews_competitor', $summaryFilterData, $success_filter_entries);
            }
            if ($sim_pars['review_count'] >= 5) {
                $this->filterBySummaryCriteria('skus_more_than_five_reviews_competitor', $summaryFilterData, $success_filter_entries);
            }
            if ($sim_pars['review_count'] >= 100) {
                $this->filterBySummaryCriteria('skus_more_than_hundred_reviews_competitor', $summaryFilterData, $success_filter_entries);
            }

            $batch1_filtered_title_percents = substr_count($row->title_seo_phrases, '%');
            $batch2_filtered_title_percents = substr_count($sim[0]->title_seo_phrases, '%');

            if ($batch1_filtered_title_percents < $batch2_filtered_title_percents) {

                $this->filterBySummaryCriteria('skus_fewer_competitor_optimized_keywords', $summaryFilterData, $success_filter_entries);
            }

            if (!$batch1_filtered_title_percents) {

                $this->filterBySummaryCriteria('skus_zero_optimized_keywords', $summaryFilterData, $success_filter_entries);
            }

            if ($batch1_filtered_title_percents >= 1) {

                $this->filterBySummaryCriteria('skus_one_optimized_keywords', $summaryFilterData, $success_filter_entries);
            }

            if ($batch1_filtered_title_percents >= 2) {

                $this->filterBySummaryCriteria('skus_two_optimized_keywords', $summaryFilterData, $success_filter_entries);
            }

            if ($batch1_filtered_title_percents >= 3) {

                $this->filterBySummaryCriteria('skus_three_optimized_keywords', $summaryFilterData, $success_filter_entries);
            }



            if ($row->column_external_content) {

                $this->filterBySummaryCriteria('skus_third_party_content', $summaryFilterData, $success_filter_entries);
            }

            if ($sim[0]->column_external_content) {

                $this->filterBySummaryCriteria('skus_third_party_content_competitor', $summaryFilterData, $success_filter_entries);
            }




            $first_general_description_size = $row->short_description_wc + $row->long_description_wc;
            $second_general_description_size = $sim[0]->long_description_wc + $sim[0]->short_description_wc;

            if ($first_general_description_size < $second_general_description_size) {

                $this->filterBySummaryCriteria('skus_shorter_than_competitor_product_content', $summaryFilterData, $success_filter_entries);
            }

            if ($first_general_description_size > $second_general_description_size) {

                $this->filterBySummaryCriteria('skus_longer_than_competitor_product_content', $summaryFilterData, $success_filter_entries);
            }

            if ($first_general_description_size == $second_general_description_size) {

                $this->filterBySummaryCriteria('skus_same_competitor_product_content', $summaryFilterData, $success_filter_entries);
            }

            // For Batch 1
            if ($first_general_description_size < 50) {

                $this->filterBySummaryCriteria('skus_fewer_50_product_content', $summaryFilterData, $success_filter_entries);
            }

            if ($first_general_description_size < 100) {

                $this->filterBySummaryCriteria('skus_fewer_100_product_content', $summaryFilterData, $success_filter_entries);
            }

            if ($first_general_description_size < 150) {

                $this->filterBySummaryCriteria('skus_fewer_150_product_content', $summaryFilterData, $success_filter_entries);
            }

            // For Competitor (Batch 2)
            if ($second_general_description_size < 50) {

                $this->filterBySummaryCriteria('skus_fewer_50_product_content_competitor', $summaryFilterData, $success_filter_entries);
            }

            if ($second_general_description_size < 100) {
                $this->filterBySummaryCriteria('skus_fewer_100_product_content_competitor', $summaryFilterData, $success_filter_entries);
            }

            if ($second_general_description_size < 150) {
                $this->filterBySummaryCriteria('skus_fewer_150_product_content_competitor', $summaryFilterData, $success_filter_entries);
            }


//                        if ($row->lower_price_exist == true) {									
//				$this->filterBySummaryCriteria('assess_report_items_priced_higher_than_competitors', $build_assess_params->summaryFilterData, $success_filter_entries);	
//			}



            if ($this->checkSuccessFilterEntries($success_filter_entries, $summaryFilterData)) {
                $arr[] = $row;
            }
        };


        foreach ($arr as $key => $row) {
            $row->Short_Description = $row->short_description;
            $row->Long_Description = $row->long_description;

            $row = (array) $row;
            foreach ($line as $k => $v) {
                $res_array[$key][$k] = $row[$k];
            }
            $row = (object) $row;

            $pars_atr = $this->imported_data_parsed_model->getByImId($row->imported_data_id);

            //item_id
            //if (in_array('item_id', $selected_columns)) {
            //    $res_array[$key]['item_id'] = $pars_atr['parsed_attributes']['item_id'] ? $pars_atr['parsed_attributes']['item_id'] : ' ';
            //}
			if (in_array('imp_data_id', $selected_columns)) {
                $res_array[$key]['imp_data_id'] = $pars_atr['parsed_attributes']['item_id'] ? $pars_atr['parsed_attributes']['item_id'] : ' ';
            }
            //model
            if (in_array('model', $selected_columns)) {
                $res_array[$key]['model'] = $pars_atr['parsed_attributes']['model'] ? $pars_atr['parsed_attributes']['model'] : '';
            }
            //meta keywords
            if (in_array('Meta_Keywords', $selected_columns)) {
                $parsed_meta_keywords_unserialize_val = "";
                if ($pars_atr['parsed_meta']['keywords']) {
                    $Meta_Keywords_un = "";
                    $cnt_meta = "";
                    $cnt_meta = explode(',', $pars_atr['parsed_meta']['keywords']);
                    $cnt_meta_count = count($cnt_meta);
                    $_count_meta = 0;
                    foreach ($cnt_meta as $cnt_m) {
                        $cnt_m = trim($cnt_m);
                        if ($row->Short_Description || $row->Long_Description) {
                            $_count_meta = $this->keywords_appearence($row->Long_Description . $row->Short_Description, $cnt_m);
                            $_count_meta_num = round(($_count_meta * $cnt_meta_count / ($row->long_description_wc + $row->short_description_wc)) * 100, 2) . "%";
                            $Meta_Keywords_un .= $cnt_m . "  - " . $_count_meta_num . ", ";
                        }
                    }

                    $parsed_meta_keywords_unserialize_val = $Meta_Keywords_un;
                }
                $res_array[$key]['meta_keywords'] = $parsed_meta_keywords_unserialize_val ? $parsed_meta_keywords_unserialize_val : '';
            }

            //meta description
            if (in_array('Meta_Description', $selected_columns)) {
                if ($pars_atr['parsed_meta']['description'] && $pars_atr['parsed_meta']['description'] != '') {
                    $res_array[$key]['meta_description'] = $pars_atr['parsed_meta']['description'];
                    $words_des = count(explode(" ", $pars_atr['parsed_meta']['description']));
                    $res_array[$key]['Meta_Description_Count'] = $words_des;
                } else if ($pars_atr['parsed_meta']['Description'] && $pars_atr['parsed_meta']['Description'] != '') {
                    $res_array[$key]['meta_description'] = $pars_atr['parsed_meta']['Description'];
                    $words_des = count(explode(" ", $pars_atr['parsed_meta']['Description']));
                    $res_array[$key]['Meta_Description_Count'] = $words_des;
                }
            }

            //custom keywords

            if (in_array('Custom_Keywords_Short_Description', $selected_columns) || in_array('Custom_Keywords_Long_Description', $selected_columns)) {
                $custom_keywords = $this->custom_keywords($row->imported_data_id, $row->Long_Description, $row->long_description_wc, $row->Short_Description, $row->short_description_wc);
                if (in_array('Custom_Keywords_Short_Description', $selected_columns)) {
                    $res_array[$key]['Custom_Keywords_Short_Description'] = $custom_keywords['Custom_Keywords_Short'];
                }
                if (in_array('Custom_Keywords_Long_Description', $selected_columns)) {
                    $res_array[$key]['Custom_Keywords_Long_Description'] = $custom_keywords['Custom_Keywords_Long'];
                }
            }
            //loaded_in_seconds
            if (in_array('Page_Load_Time', $selected_columns)) {
                $res_array[$key]['Page_Load_Time'] = $pars_atr['parsed_attributes']['loaded_in_seconds'] !== false ? $pars_atr['parsed_attributes']['loaded_in_seconds'] : '';
            }
            if (in_array('column_external_content', $selected_columns)) {
                $res_array[$key]['column_external_content'] = $this->column_external_content($pars_atr['parsed_attributes']['cnetcontent'], $pars_atr['parsed_attributes']['webcollage']);
            }
            if (in_array('column_features', $selected_columns)) {
                $res_array[$key]['column_features'] = $pars_atr['parsed_attributes']['feature_count'] !== false ? $pars_atr['parsed_attributes']['feature_count'] : 0;
            }
            if (in_array('column_reviews', $selected_columns)) {
                $res_array[$key]['column_reviews'] = $pars_atr['parsed_attributes']['review_count'] !== false ? $pars_atr['parsed_attributes']['review_count'] : 0;
            }
            if (in_array('average_review', $selected_columns)) {
                $res_array[$key]['average_review'] = $pars_atr['parsed_attributes']['average_review'] !== false ? $pars_atr['parsed_attributes']['average_review'] : '-';
            }
				//print_r($pars_atr);die;
            //export title keywords 
            $title_seo_prases = array();

            if ($row->title_keywords != '' && $row->title_keywords != 'None') {
                    $title_seo_prases = unserialize($row->title_keywords);
            }
            if (!empty($title_seo_prases)) {
                $str_title_long_seo = '';
                foreach ($title_seo_prases as $pras) {
                    $str_title_long_seo .= $pras['ph'] . ' - ' . $pras['prc'] . '%,  ';
                }
            }
            if (in_array('title_seo_phrases', $selected_columns)) {
                $res_array[$key]['title_seo_phrases'] = $str_title_long_seo;
            }
			
			if (in_array('title_seo_phrases_f', $selected_columns)) {
                $res_array[$key]['title_seo_phrases'] = $str_title_long_seo;
            }
            if (in_array('H1_Tags', $selected_columns) && $pars_atr['HTags']['h1'] && $pars_atr['HTags']['h1'] != '') {
                $H1 = $pars_atr['HTags']['h1'];
                if (is_array($H1)) {

                    $i = 0;
                    foreach ($H1 as $k => $h1) {
                        if ($i < 2) {
                            $res_array[$key]['H1_Tags' . $k] = $h1;
                            $res_array[$key]['H1_Tags_Count' . $k] = strlen($h1);
                            $i++;
                        }
                    }
                } else {
                    $res_array[$key]['H1_Tags0'] = $H1;
                    $res_array[$key]['H1_Tags_Count0'] = strlen($H1);
                }

                if ($H1_tag_count > 0) {
                    if ($H1_tag_count > 2) {
                        $H1_tag_count = 2;
                    }

                    for ($k = 0; $k < $H1_tag_count; $k++) {
                        if (!$res_array[$key]['H1_Tags' . $k]) {
                            $res_array[$key]['H1_Tags' . $k] = '';
                            $res_array[$key]['H1_Tags_Count' . $k] = ' ';
                        }
                    }
                }
            }
            if (in_array('H2_Tags', $selected_columns) && $pars_atr['HTags']['h2'] && $pars_atr['HTags']['h2'] != '') {
                $H2 = $pars_atr['HTags']['h2'];
                if (is_array($H2)) {

                    $i = 0;
                    foreach ($H2 as $k => $h2) {
                        if ($i < 2) {
                            $res_array[$key]['H2_Tags' . $k] = $h2;
                            $res_array[$key]['H2_Tags_Count' . $k] = strlen($h2);
                            $i++;
                        }
                    }
                } else {
                    $res_array[$key]['H2_Tags0'] = $H2;
                    $res_array[$key]['H2_Tags_Count0'] = strlen($H2);
                }

                if ($H2_tag_count > 0) {
                    if ($H2_tag_count > 2) {
                        $H2_tag_count = 2;
                    }

                    for ($k = 0; $k < $H2_tag_count; $k++) {
                        if (!$res_array[$key]['H2_Tags' . $k]) {
                            $res_array[$key]['H2_Tags' . $k] = '';
                            $res_array[$key]['H2_Tags_Count' . $k] = ' ';
                        }
                    }
                }
            } else {
                if ($H2_tag_count > 2) {
                    $H2_tag_count = 2;
                }

                for ($k = 0; $k < $H2_tag_count; $k++) {
                    if (!$res_array[$key]['H2_Tags' . $k]) {
                        $res_array[$key]['H2_Tags' . $k] = '';
                        $res_array[$key]['H2_Tags_Count' . $k] = ' ';
                    }
                }
            }


            if (trim($res_array[$key]['short_seo_phrases']) != 'None') {
                $shortArr = unserialize($res_array[$key]['short_seo_phrases']);

                if ($shortArr) {
                    $shortString = '';
                    foreach ($shortArr as $value) {
                        $shortString .= $value['ph'] . "\r\n";
                    }
                    $res_array[$key]['short_seo_phrases'] = trim($shortString);
                }
            }
            if (trim($res_array[$key]['long_seo_phrases']) != 'None') {

                $longArr = unserialize($res_array[$key]['long_seo_phrases']);

                if ($longArr) {
                    $longString = '';
                    foreach ($longArr as $value) {
                        $longString .= $value['ph'] . "\r\n";
                    }
                    $res_array[$key]['long_seo_phrases'] = trim($longString);
                }
            }
            if (in_array('price_diff', $selected_columns)) {
                $price_diff = unserialize($res_array[$key]['price_diff']);
                if ($price_diff) {
                    $own_price = floatval($price_diff['own_price']);
                    $own_site = str_replace('www.', '', $price_diff['own_site']);
                    $own_site = str_replace('www1.', '', $own_site);
                    $price_diff_res = $own_site . " - $" . number_format($price_diff['own_price'], 2);
                    $flag_competitor = false;
                    for ($i = 0; $i < count($price_diff['competitor_customer']); $i++) {
                        if ($customer_url["host"] != $price_diff['competitor_customer'][$i]) {
                            if ($own_price > floatval($price_diff['competitor_price'][$i])) {
                                $competitor_site = str_replace('www.', '', $price_diff['competitor_customer'][$i]);
                                $competitor_site = str_replace('www.', '', $competitor_site);
                                $price_diff_res .= "\r\n" . $competitor_site . " - $" . number_format($price_diff['competitor_price'][$i], 2);
                            }
                        }
                    }
                    $res_array[$key]['price_diff'] = $price_diff_res;
                } else {
                    $res_array[$key]['price_diff'] = '';
                }
            }


            $sim_items = $row->similar_items;
            $f_count1 = 0;
            for ($i = 1; $i <= $max_similar_item_count; $i++) {

//                        if($i==1 && !$meta_key_gap ){
//                            $meta_key_gap=round(($_count_meta_un * $cnt_meta_count_un / ($row->long_description_wc + $row->short_description_wc)) * 100, 2);
//                        }
                if ($i == 1) {
                    if (isset($sim_items[$i - 1]->column_features)) {
                        $f_count1 = $sim_items[$i - 1]->column_features;
                    } else {
                        $f_count1 = 0;
                    }
                }

                if (in_array('gap', $selected_columns)) {
                    $res_array[$key]['Gap analysis'] = '';

                    if (isset($sim_items[$i - 1]) && ($sim_items[$i - 1]->long_description_wc || $sim_items[$i - 1]->short_description_wc) && ($sim_items[$i - 1]->short_description_wc + $sim_items[$i - 1]->long_description_wc) < 100) {
                        $totoal = $sim_items[$i - 1]->short_description_wc + $sim_items[$i - 1]->long_description_wc;
                        $res_array[$key]['Gap analysis'].="Competitor total product description length only $totoal words, ";
                    }

                    if ($res_array[$key]['column_features'] && $f_count1 && $f_count1 > $res_array[$key]['column_features']) {
                    $x = $f_count1 - $res_array[$key]['column_features'];
                        
                        $res_array[$key]['Gap analysis'].="Competitor has ".$x." features listed, ";
                    }
                    if (!$sim_items[$i - 1]->den_for_gap) {

                        $res_array[$key]['Gap analysis'] .= "Competitor is not keyword optimized, ";
                    }
                    $res_array[$key]['Gap analysis'] = rtrim($res_array[$key]['Gap analysis'], ", ");
                }


//                        echo '<pre>';
//                        print_r($row->similar_items);
//                        echo '<br />';
//                        print_r($results[$key]); exit();
                if (in_array('Duplicate_Content', $selected_columns)) {


                    if ($results[$key]->Short_Description) {
                        $short_desc_1 = $results[$key]->Short_Description;
                    } else {
                        $short_desc_1 = '';
                    }
                    if ($results[$key]->Long_Description) {
                        $long_desc_1 = $results[$key]->Long_Description;
                    } else {
                        $long_desc_1 = '';
                    }
                    $desc_1 = $short_desc_1 . ' ' . $long_desc_1;

                    if ($results[$key]->similar_items[0]->Short_Description) {
                        $short_desc_2 = $results[$key]->similar_items[0]->Short_Description;
                    } else {
                        $short_desc_2 = '';
                    }
                    if ($results[$key]->similar_items[0]->Long_Description) {
                        $long_desc_2 = $results[$key]->similar_items[0]->Long_Description;
                    } else {
                        $long_desc_2 = '';
                    }
                    $desc_2 = $short_desc_2 . ' ' . $long_desc_2;

                    similar_text($desc_1, $desc_2, $percent);
                    $percent = number_format($percent, 2);
                    $res_array[$key]['Duplicate_Content'] = $percent . ' %';
                }



                //if (in_array('item_id', $selected_columns)) {
                 //   $res_array[$key]['Item Id (' . $i . ")"] = $sim_items[$i - 1]->item_id ? $sim_items[$i - 1]->item_id : ' - ';
                //}
				if (in_array('imp_data_id', $selected_columns)) {
					if($i = 1){
					$res_array[$key]['imp_data_id'] = $sim_items[$i - 1]->imported_data_id ? $sim_items[$i - 1]->imported_data_id : ' - ';
					}
					else{
					$res_array[$key]['imp_data_id' . $i] = $sim_items[$i - 1]->imported_data_id ? $sim_items[$i - 1]->imported_data_id : ' - ';
					}
                    //$res_array[$key]['imp_data_id' . $i] = $sim_items[$i - 1]->imported_data_id ? $sim_items[$i - 1]->imported_data_id : ' - ';
					//echo '<pre>';print_r($res_array[$key]);echo '</pre>';die;
                }
                if (in_array('model', $selected_columns)) {
                    $res_array[$key]['Model (' . $i . ")"] = $sim_items[$i - 1]->model ? $sim_items[$i - 1]->model : '';
                }
                if (in_array('product_name', $selected_columns)) {
                    $res_array[$key]['Product Name (' . $i . ")"] = $sim_items[$i - 1]->product_name ? $sim_items[$i - 1]->product_name : ' - ';
                }
                if (in_array('url', $selected_columns)) {
                    $res_array[$key]['Url (' . $i . ")"] = $sim_items[$i - 1]->url ? $sim_items[$i - 1]->url : '';
                }


                if (in_array('Short_Description', $selected_columns)) {
                    $res_array[$key]['Short Description (' . $i . ")"] = $sim_items[$i - 1]->Short_Description ? $sim_items[$i - 1]->Short_Description : '';
                }
                if (in_array('short_description_wc', $selected_columns)) {
                    $res_array[$key]['Short Desc # Words (' . $i . ")"] = $sim_items[$i - 1]->short_description_wc ? $sim_items[$i - 1]->short_description_wc : '';
                }
                if (in_array('Long_Description', $selected_columns)) {
                    $res_array[$key]['Long_Description (' . $i . ")"] = $sim_items[$i - 1]->Long_Description ? $sim_items[$i - 1]->Long_Description : '';
                }
                if (in_array('long_description_wc', $selected_columns)) {
                    $res_array[$key]['Long Desc # Words (' . $i . ")"] = $sim_items[$i - 1]->long_description_wc ? $sim_items[$i - 1]->long_description_wc : '';
                }

                if (in_array('Meta_Keywords', $selected_columns)) {
                    $res_array[$key]['Meta_Keywords(' . $i . ")"] = $sim_items[$i - 1]->Meta_Keywords ? $sim_items[$i - 1]->Meta_Keywords : '';
                }
                if (in_array('Meta_Description', $selected_columns)) {
                    $res_array[$key]['Meta_Description (' . $i . ")"] = $sim_items[$i - 1]->Meta_Description ? $sim_items[$i - 1]->Meta_Description : '';
                    $res_array[$key]['Meta Desc Words (' . $i . ")"] = $sim_items[$i - 1]->Meta_Description_Count ? $sim_items[$i - 1]->Meta_Description_Count : '';
                }
                if (in_array('Page_Load_Time', $selected_columns)) {
                    $res_array[$key]['Page Load Time (' . $i . ")"] = $sim_items[$i - 1]->Page_Load_Time ? $sim_items[$i - 1]->Page_Load_Time : ' - ';
                }

                if (in_array('column_features', $selected_columns)) {
                    $res_array[$key]['column_features(' . $i . ")"] = $sim_items[$i - 1]->column_features ? $sim_items[$i - 1]->column_features : 0;
                }
                if (in_array('column_external_content', $selected_columns)) {
                    $res_array[$key]['column_external_content(' . $i . ")"] = $sim_items[$i - 1]->column_external_content ? $sim_items[$i - 1]->column_external_content : '';
                }
                if (in_array('column_reviews', $selected_columns)) {
                    $res_array[$key]['column_reviews(' . $i . ")"] = $sim_items[$i - 1]->review_count ? $sim_items[$i - 1]->review_count : 0;
                }
                if (in_array('average_review', $selected_columns)) {
                    $res_array[$key]['average_review(' . $i . ")"] = $sim_items[$i - 1]->average_review ? $sim_items[$i - 1]->average_review : ' - ';
                }
                if (in_array('title_seo_phrases', $selected_columns)) {
                    $res_array[$key]['title_seo_phrases(' . $i . ")"] = $sim_items[$i - 1]->title_seo_phrases ? $sim_items[$i - 1]->title_seo_phrases : ' - ';
                }	
				if (in_array('title_seo_phrases_f', $selected_columns)) {
                    $res_array[$key]['title_seo_phrases_f(' . $i . ")"] = $sim_items[$i - 1]->title_seo_phrases ? $sim_items[$i - 1]->title_seo_phrases : ' - ';
                }
// HTags for similar
                $HTags_for_similar = unserialize($sim_items[$i - 1]->HTags);
//                        echo '<pre>';
//                        print_r($HTags_for_similar); exit();


                if (in_array('H1_Tags', $selected_columns) && $HTags_for_similar['h1'] && $HTags_for_similar['h1'] != '') {
                    $H1 = $HTags_for_similar['h1'];
                    if (is_array($H1)) {

                        $j = 0;
                        foreach ($H1 as $k => $h1) {
                            if ($j < 2) {
                                $res_array[$key]['H1_Tags' . $k . '(' . $i . ')'] = $h1;
                                $res_array[$key]['H1_Tags_Count' . $k . '(' . $i . ')'] = strlen($h1);
                                $j++;
                            }
                        }
                    } else {
                        $res_array[$key]['H1_Tags0 (' . $i . ')'] = $H1;
                        $res_array[$key]['H1_Tags_Count0 (' . $i . ')'] = strlen($H1);
                    }

                    if ($H1_tag_count_for_sim > 0) {
                        if ($H1_tag_count_for_sim > 2) {
                            $H1_tag_count_for_sim = 2;
                        }

                        for ($k = 0; $k < $H1_tag_count_for_sim; $k++) {
                            if (!$res_array[$key]['H1_Tags' . $k . '(' . $i . ')']) {
                                $res_array[$key]['H1_Tags' . $k . '(' . $i . ')'] = '';
                                $res_array[$key]['H1_Tags_Count' . $k . '(' . $i . ')'] = ' ';
                            }
                        }
                    }
                }
                if (in_array('H2_Tags', $selected_columns) && $HTags_for_similar['h2'] && $HTags_for_similar['h2'] != '') {
                    $H2 = $HTags_for_similar['h2'];
                    if (is_array($H2)) {

                        $j = 0;
                        foreach ($H2 as $k => $h2) {
                            if ($j < 2) {
                                $res_array[$key]['H2_Tags' . $k . '(' . $i . ')'] = $h2;
                                $res_array[$key]['H2_Tags_Count' . $k . '(' . $i . ')'] = strlen($h2);
                                $j++;
                            }
                        }
                    } else {
                        $res_array[$key]['H2_Tags0 (' . $i . ')'] = $H2;
                        $res_array[$key]['H2_Tags_Count0 (' . $i . ')'] = strlen($H2);
                    }

                    if ($H2_tag_count_for_sim > 0) {
                        if ($H2_tag_count_for_sim > 2) {
                            $H2_tag_count_for_sim = 2;
                        }

                        for ($k = 0; $k < $H2_tag_count_for_sim; $k++) {
                            if (!$res_array[$key]['H2_Tags' . $k . '(' . $i . ')']) {
                                $res_array[$key]['H2_Tags' . $k . '(' . $i . ')'] = '';
                                $res_array[$key]['H2_Tags_Count' . $k . '(' . $i . ')'] = ' ';
                            }
                        }
                    }
                } else {
                    if ($H2_tag_count_for_sim > 2) {
                        $H2_tag_count_for_sim = 2;
                    }

                    for ($k = 0; $k < $H2_tag_count_for_sim; $k++) {
                        if (!$res_array[$key]['H2_Tags' . $k . '(' . $i . ')']) {
                            $res_array[$key]['H2_Tags' . $k . '(' . $i . ')'] = '';
                            $res_array[$key]['H2_Tags_Count' . $k . '(' . $i . ')'] = ' ';
                        }
                    }
                }
            }
        }

        if (in_array('model', $selected_columns)) {
            array_unshift($line, 'Model');
        }
        //if (in_array('item_id', $selected_columns)) {
        //    array_unshift($line, 'Item ID');
        //}
		if (in_array('imp_data_id', $selected_columns)) {
            array_unshift($line, 'Item ID');
        }
        if (in_array('Meta_Keywords', $selected_columns)) {
            $line[] = 'Meta Keywords - Keyword Density';
        }

        //meta description
        if (in_array('Meta_Description', $selected_columns)) {
            $line[] = 'Meta Description';
            $line[] = 'Meta Desc Words';
        }
        if (in_array('Custom_Keywords_Short_Description', $selected_columns)) {
            $line[] = 'Custom Keywords - Short Description';
        }
        if (in_array('Custom_Keywords_Long_Description', $selected_columns)) {
            $line[] = 'Custom Keywords - Long Description';
        }
        if (in_array('Page_Load_Time', $selected_columns)) {
            $line[] = 'Page Load Time';
        }
        if (in_array('column_external_content', $selected_columns)) {
            $line[] = 'Third Party Content';
        }
//            if (in_array('column_features', $selected_columns)) {
//                $res_array[$key]['column_features'] = $pars_atr['parsed_attributes']['feature_count'] !== false ? $pars_atr['parsed_attributes']['feature_count'] : '';
//            }
//            if (in_array('column_reviews', $selected_columns)) {
//             $res_array[$key]['column_reviews'] = $pars_atr['parsed_attributes']['review_count'] !== false ? $pars_atr['parsed_attributes']['review_count'] : '';
//               }

        if (in_array('H1_Tags', $selected_columns)) {
            if ($H1_tag_count > 0) {
                for ($k = 1; $k <= $H1_tag_count; $k++) {
                    $line[] = "H1_tag ($k) ";
                    $line[] = "Chars ($k)";
                }
            }
        }
        if (in_array('H2_Tags', $selected_columns)) {
            if ($H2_tag_count > 0) {
                for ($k = 1; $k <= $H2_tag_count; $k++) {
                    $line[] = "H2_tag ($k) ";
                    $line[] = "Chars ($k)";
                }
            }
        }




        for ($i = 1; $i <= $max_similar_item_count; $i++) {
            if (in_array('gap', $selected_columns)) {
                $line[] = 'Gap Analysis';
            }
            if (in_array('Duplicate_Content', $selected_columns)) {
                $line[] = 'Duplicate Content';
            }
            //if (in_array('item_id', $selected_columns)) {
            //    $line[] = "Item Id(" . ($i + 1) . ")";
            //}
			if (in_array('imp_data_id', $selected_columns)) {
                $line[] = "Item Id(" . ($i + 1) . ")";
            }
            if (in_array('model', $selected_columns)) {
                $line[] = "Model(" . ($i + 1) . ")";
            }

            if (in_array('product_name', $selected_columns)) {
                $line[] = "Product Name(" . ($i + 1) . ")";
            }
            if (in_array('url', $selected_columns)) {
                $line[] = "Url(" . ($i + 1) . ")";
            }
            if (in_array('Short_Description', $selected_columns)) {
                $line[] = "Short Description(" . ($i + 1) . ")";
            }
            if (in_array('short_description_wc', $selected_columns)) {
                $line[] = "Short Desc # Words(" . ($i + 1) . ")";
            }
            if (in_array('Long_Description', $selected_columns)) {
                $line[] = "Long Description(" . ($i + 1) . ")";
            }
            if (in_array('long_description_wc', $selected_columns)) {
                $line[] = " Long Desc # Words(" . ($i + 1) . ")";
            }
            if (in_array('Meta_Keywords', $selected_columns)) {
                $line[] = "Meta Keywords (" . ($i + 1) . ") - Keyword Density";
            }
            if (in_array('Meta_Description', $selected_columns)) {
                $line[] = "Meta Description(" . ($i + 1) . ")";
                $line[] = " Meta Desc Words(" . ($i + 1) . ")";
            }
            if (in_array('Page_Load_Time', $selected_columns)) {
                $line[] = "Page Load Time(" . ($i + 1) . ")";
            }
            if (in_array('column_features', $selected_columns)) {
                $line[] = "Features(" . ($i + 1) . ")";
            }
            if (in_array('column_external_content', $selected_columns)) {
                $line[] = "Third Party Content(" . ($i + 1) . ")";
            }
            if (in_array('column_reviews', $selected_columns)) {
                $line[] = "Reviews(" . ($i + 1) . ")";
            }
            if (in_array('average_review', $selected_columns)) {
                $line[] = "Avg Review(" . ($i + 1) . ")";
            }
            if (in_array('title_seo_phrases', $selected_columns)) {
                $line[] = "Title Keywords(" . ($i + 1) . ")";
            }
			if (in_array('title_seo_phrases_f', $selected_columns)) {
                $line[] = "Title Keywords(" . ($i + 1) . ")";
            }
            if (in_array('H1_Tags', $selected_columns)) {
                if ($H1_tag_count_for_sim > 0) {
                    for ($k = 1; $k <= $H1_tag_count_for_sim; $k++) {
                        $line[] = "H1_tag ($k)    (" . ($i + 1) . ")";
                        $line[] = "Chars ($k)    (" . ($i + 1) . ")";
                    }
                }
            }
            if (in_array('H2_Tags', $selected_columns)) {
                if ($H2_tag_count_for_sim > 0) {
                    for ($k = 1; $k <= $H2_tag_count_for_sim; $k++) {
                        $line[] = "H2_tag ($k)    (" . ($i + 1) . ")";
                        $line[] = "Chars ($k)    (" . ($i + 1) . ")";
                    }
                }
            }
        }
//            echo '<pre>';
//            print_r($line);
//            echo '<pre>';
//            print_r($res_array);exit();
        //deleting empty Short_Description, Long_Description, short_descripition_wc, long_description_wc colomns
        //filterBySummaryCriteria
        if (in_array('Short_Description', $selected_columns)) {
            $short_description_count = 0;
            if (isset($max_similar_item_count)) {
                $short_description_count_1 = 0;
            }
        }
        if (in_array('Long_Description', $selected_columns)) {
            $long_description_count = 0;
            if (isset($max_similar_item_count)) {
                $long_description_count_1 = 0;
            }
        }
        if (in_array('short_description_wc', $selected_columns)) {
            $short_description_wc_count = 0;
            if (isset($max_similar_item_count)) {
                $short_description_wc_count_1 = 0;
            }
        }
        if (in_array('long_description_wc', $selected_columns)) {
            $long_description_wc_count = 0;
            if (isset($max_similar_item_count)) {
                $long_description_wc_count_1 = 0;
            }
        }

        foreach ($res_array as $key => $value) {

            if (in_array('Short_Description', $selected_columns)) {
                if (!$res_array[$key]['Short_Description'])
                    $short_description_count++;
                if (isset($max_similar_item_count)) {
                    if (!$res_array[$key]['Short Description (1)'])
                        $short_description_count_1++;
                }
            }
            if (in_array('Long_Description', $selected_columns)) {
                if (!$res_array[$key]['Long_Description'])
                    $long_description_count++;
                if (isset($max_similar_item_count)) {
                    if (!$res_array[$key]['Long_Description (1)'])
                        $long_description_count_1++;
                }
            }
            if (in_array('short_description_wc', $selected_columns)) {
                if ($res_array[$key]['short_description_wc'] == 0)
                    $short_description_wc_count++;
                if (isset($max_similar_item_count)) {
                    if ($res_array[$key]['Short Desc # Words (1)'] == 0)
                        $short_description_wc_count_1++;
                }
            }
            if (in_array('long_description_wc', $selected_columns)) {
                if ($res_array[$key]['long_description_wc'] == 0)
                    $long_description_wc_count++;
                if (isset($max_similar_item_count)) {
                    if ($res_array[$key]['Long Desc # Words (1)'] == 0)
                        $long_description_wc_count_1++;
                }
            }
        }

        if (in_array('Short_Description', $selected_columns)) {
            if ($short_description_count == count($res_array)) {
                foreach ($res_array as $key => $res) {
                    unset($res_array[$key]['Short_Description']);
                }
                unset($line['Short_Description']);
            }
            if (isset($max_similar_item_count)) {
                if ($short_description_count_1 == count($res_array)) {
                    foreach ($res_array as $key => $res) {
                        unset($res_array[$key]['Short Description (1)']);
                    }
                    unset($line['18']);
                }
            }
        }
        if (in_array('Long_Description', $selected_columns)) {
            if ($long_description_count == count($res_array)) {
                foreach ($res_array as $key => $res) {
                    unset($res_array[$key]['Long_Description']);
                }
                unset($line['Long_Description']);
            }
            if (isset($max_similar_item_count)) {
                if ($long_description_count_1 == count($res_array)) {
                    foreach ($res_array as $key => $res) {
                        unset($res_array[$key]['Long_Description (1)']);
                    }
                    unset($line['20']);
                }
            }
        }

        if (in_array('short_description_wc', $selected_columns)) {
            if ($short_description_wc_count == count($res_array)) {
                foreach ($res_array as $key => $res) {
                    unset($res_array[$key]['short_description_wc']);
                }
                unset($line['short_description_wc']);
            }
            if (isset($max_similar_item_count)) {
                if ($short_description_wc_count_1 == count($res_array)) {
                    foreach ($res_array as $key => $res) {
                        unset($res_array[$key]['Short Desc # Words (1)']);
                    }
                    unset($line['19']);
                }
            }
        }
        if (in_array('long_description_wc', $selected_columns)) {
            if ($long_description_wc_count == count($res_array)) {
                foreach ($res_array as $key => $res) {
                    unset($res_array[$key]['long_description_wc']);
                }
                unset($line['long_description_wc']);
            }
            if (isset($max_similar_item_count)) {
                if ($long_description_wc_count_1 == count($res_array)) {
                    foreach ($res_array as $key => $res) {
                        unset($res_array[$key]['Long Desc # Words(1)']);
                    }
                    unset($line['21']);
                }
            }
        }
		
		if($res_array[0]){		
				$res_key = array_keys($res_array[0]);
				$res_key_flip = array_flip($res_key);
				foreach($res_key_flip as $key => $value){
				if($key == "created"){
					$key = 'Created';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "product_name"){
					$key = 'Product name';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "H1_Tags1(1)"){
					$key = 'Product name';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "H1_Tags_Count1"){
					$key = 'H1 Tags Count1';
					$res_array_keys[$value] = $key;
				}
				elseif($key === "H1_Tags1"){
					$key = 'H1 Tags(1)';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "Long_Description"){
					$key = 'Long description';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "long_description_wc"){
					$key = 'Long Description - # Words';
					$res_array_keys[$value] = $key;
				}				
				elseif($key == "url"){
					$key = 'Url';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "Short_Description"){
					$key = 'Product Description';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "short_description_wc"){
					$key = 'Short Desc # Words';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "price_diff"){
					$key = 'Price difference';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "column_features"){
					$key = 'Features';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "average_review"){
					$key = 'Avg Review';
					$res_array_keys[$value] = $key;
				}
				elseif($key === "column_reviews"){
					$key = 'Reviews';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "title_seo_phrases"){
					$key = 'Title keywords';
					$res_array_keys[$value] = $key;
				}
				//elseif($key == "item_id"){
					//$key = 'Item ID';
				//	$res_array_keys[$value] = $key;
				//}
				elseif($key == "imp_data_id"){
					$key = 'Item ID';
					$res_array_keys[$value] = $key;
				}

				elseif($key == "H1_Tags0"){
					$key = 'H1 Tags';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "model"){
					$key = 'Model';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "Model (1)"){
					$key = 'Model(2)';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "Product Name (1)"){
					$key = 'Product Name (2)';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "meta_keywords"){
					$key = 'Meta keywords';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "meta_description"){
					$key = 'Meta description';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "Meta_Description_Count"){
					$key = 'Meta Desc # Words';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "Custom_Keywords_Short_Description"){
					$key = 'Custom Keywords Short Description';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "Custom_Keywords_Long_Description"){
					$key = 'Custom Keywords Long Description';
					$res_array_keys[$value] = $key;
				}
				elseif($key === "column_external_content"){
					$key = 'Third Party Content';
					$res_array_keys[$value] = $key;
				}
				elseif($key === "column_external_content(1)"){
					$key = 'Third Party Content';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "Page_Load_Time"){
					$key = 'Page Load Time';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "H1_Tags_Count0"){
					$key = 'H1 chars count(1)';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "H1_Tags_Count0(1)"){
					$key = 'H1 chars count(2)';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "H2_Tags0"){
					$key = 'H2 Tags(1)';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "H2_Tags_Count0"){
					$key = 'H2 chars count';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "H2_Tags1"){
					$key = 'H2 Tags(2)';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "H2_Tags_Count1"){
					$key = 'H2 chars count(1)';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "Gap analysis"){
					$key = 'Gap analysis';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "Duplicate_Content"){
					$key = 'Duplicate Content';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "imp_data_id2"){
					$key = 'Item Id (2)';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "average_review(1)"){
					$key = 'Average review(1)';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "Url (1)"){
					$key = 'Url(2)';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "Short Description (1)"){
					$key = 'Product Description (2)';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "Short Desc # Words (1)"){
					$key = 'Short Desc # Words (2)';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "Long Desc # Words (1)"){
					$key = 'Long Desc # Words (2)';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "Meta_Keywords(1)"){
					$key = 'Meta Keywords(2)';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "Meta_Description (1)"){
					$key = 'Meta Description (2)';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "Meta Desc Words (1)"){
					$key = 'Meta Desc Words (2)';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "Page Load Time (1)"){
					$key = 'Page Load Time (2)';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "column_features(1)"){
					$key = 'Features(2)';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "column_reviews(1)"){
					$key = 'Column reviews';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "title_seo_phrases(1)"){
					$key = 'Title keywords(2)';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "H2_Tags0(1)"){
					$key = 'H2 Tags(1)(2)';
					$res_array_keys[$value] = $key;
				}
				elseif($key === "H1_Tags0(1)"){
					$key = 'H1 Tags(2)';
					$res_array_keys[$value] = $key;
				} 
				elseif($key == "H2_Tags_Count0(1)"){
					$key = 'H2 chars count(2)';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "H2_Tags1(1)"){
					$key = 'H2 Tags(2)(2)';
					$res_array_keys[$value] = $key;
				}
				elseif($key == "H2_Tags_Count1(1)"){
					$key = 'H2 chars count(2)';
					$res_array_keys[$value] = $key;
				}
				else{
					$res_array_keys[$value] = $key;
				}
			}
		}
		/*
		echo '<div style="width:50%;height:auto;float:left;"><pre>';
		print_r($selected_columns);
		print_r($res_array_keys);
		echo '</pre></div><div style="width:50%;height:auto;float:right;"><pre>';
		print_r($res_array);
		echo '</pre></div>';
		*/
		array_unshift($res_array, $res_array_keys);
        $this->load->helper('csv');
        array_to_csv($res_array, $batch_name . "(" . date("Y-m-d H:i") . ').csv');
		
	}

    public function products() {
        $this->data['customer_list'] = $this->getCustomersByUserId();
        $this->data['category_list'] = $this->category_list();
        if (!empty($this->data['customer_list'])) {
            $this->data['batches_list'] = $this->batches_list();
        }

        $user_id = $this->ion_auth->get_user_id();
        $key = 'research_assess';
        $columns = $this->settings_model->get_value($user_id, $key);
		
		$this->load->model('user_summary_settings', 'uss');
		if ($this->ion_auth->logged_in() && ($user_id = $this->ion_auth->get_user_id()))		
		{
			$user_setting_filters = $this->uss->findByAttributes(array('user_id' => $user_id, 'setting_id' => User_summary_settings::USER_SUMMARY_SETTING_FILTER));			
			$user_setting_filters_order = $this->uss->findByAttributes(array('user_id' => $user_id, 'setting_id' => User_summary_settings::USER_SUMMARY_SETTING_FILTER_ORDER));
		}
		else
		{			
			$user_setting_filters = $this->uss->findByAttributes(array('user_ip' => $_SERVER['REMOTE_ADDR'], 'setting_id' => User_summary_settings::USER_SUMMARY_SETTING_FILTER));	
			$user_setting_filters_order = $this->uss->findByAttributes(array('user_ip' => $_SERVER['REMOTE_ADDR'], 'setting_id' => User_summary_settings::USER_SUMMARY_SETTING_FILTER_ORDER));
		}
		
		$this->data['user_filters'] = $user_setting_filters && $user_setting_filters->setting_value ? json_decode($user_setting_filters->setting_value) : array();
		$this->data['user_filters_order'] = $user_setting_filters_order && $user_setting_filters_order->setting_value ? json_decode($user_setting_filters_order->setting_value) : array();

        // if columns empty set default values for columns
        if (empty($columns)) {
            $columns = array(
                'product_name' => 'true',                               
                'url' => 'true',                                
                'short_description_wc' => 'true',			               
                'title_seo_phrases' => 'true',                                       
                'H1_Tags' => 'true',                              
                'column_reviews' => 'true',				          
                'images_cmp' => 'true',
                'video_count' => 'true', 
                'title_pa' => 'true',
                'links_count' => 'true'
            );
        }
        $this->data['columns'] = $columns;

        $this->render();
    }

    public function batches_list() {
        $this->load->model('batches_model');
        $batches = $this->batches_model->getAll();
        //$batches_list = array('0'=>'Select batch');
        $batches_list = array('0' => '0');
        foreach ($batches as $batch) {
            $batches_list[$batch->id] = $batch->title;
        }
        asort($batches_list);
        $batches_list[0] = 'Select batch';

        return $batches_list;
    }

    public function category_list() {
        $this->load->model('category_model');
        $categories = $this->category_model->getAll();
        $category_list = array();
        foreach ($categories as $category) {
            array_push($category_list, $category->name);
        }
        return $category_list;
    }

    public function getCustomersByUserId() {
        $this->load->model('batches_model');
        $this->load->model('customers_model');
        $this->load->model('users_to_customers_model');

        $customers = $this->customers_model->getAll();
        if ($this->ion_auth->logged_in() && !$this->ion_auth->is_admin($this->ion_auth->get_user_id())) {
            $customers = $this->users_to_customers_model->getByUserId($this->ion_auth->get_user_id());
            if (count($customers) == 0) {
                $customer_list = array();
            } else {
                $customer_list = array('0' => 'Select customer');
            }
            foreach ($customers as $customer) {
                $batches = $this->batches_model->getAllByCustomer($customer->customer_id);
                if (count($batches) > 0) {
                    array_push($customer_list, $customer->name);
                }
            }
        } else {
            if (count($customers) == 0) {
                $customers = $this->customers_model->getAll();
            }
            $customer_list = array('0' => 'Select customer');
            foreach ($customers as $customer) {
                $batches = $this->batches_model->getAllByCustomer($customer->id);
                if (count($batches) > 0) {
                    array_push($customer_list, $customer->name);
                }
            }
        }
        return $customer_list;
    }

    public function research_assess_report_options_get() {
        $this->load->model('sites_model');
        $all_sites = $this->sites_model->getAll();
        $user_id = $this->ion_auth->get_user_id();
        $key = 'research_assess_report_options';
        $batch_id = $this->input->get('batch_id');
        $existing_settings = $this->settings_model->get_value($user_id, $key);
        $batch_settings = $existing_settings[$batch_id];
        $competitors = array();
        foreach ($all_sites as $k => $v) {
            if (in_array($v->id, $batch_settings->assess_report_competitors)) {
                $selected = true;
            } else {
                $selected = false;
            }
            $competitors[] = array(
                'id' => $v->id,
                'name' => $v->name,
                'selected' => $selected
            );
        }
        $batch_settings->assess_report_competitors = $competitors;
        echo json_encode($batch_settings);
    }

    public function research_assess_report_options_set() {
        $this->load->model('settings_model');
        $this->load->model('batches_model');
        $user_id = $this->ion_auth->get_user_id();
        $key = 'research_assess_report_options';
        $description = 'Assess -> Report Options';
        $posted_settings = json_decode($this->input->post('data'));

        // get existing settings
        $existing_settings = $this->settings_model->get_value($user_id, $key);
        if (!$existing_settings) {
            $new_settings[$posted_settings->batch_id] = $posted_settings;
        } else {
            $existing_settings = $existing_settings;
            $existing_settings[$posted_settings->batch_id] = $posted_settings;
            $new_settings = $existing_settings;
        }

        $res = $this->settings_model->replace($user_id, $key, $new_settings, $description);
        echo json_encode($res);
    }

    public function include_in_assess_report_check() {
        $research_data_id = $this->input->get('research_data_id');
        $this->load->model('research_data_model');
        $result['checked'] = $this->research_data_model->include_in_assess_report_check($research_data_id);
        $this->output->set_content_type('application/json')->set_output(json_encode($result));
    }

    public function include_in_report() {
        $research_data_id = $this->input->post('research_data_id');
        $include_in_report = trim(strtolower($this->input->post('include_in_report'))) === 'true' ? true : false;
        $this->load->model('research_data_model');
        $this->research_data_model->include_in_assess_report($research_data_id, $include_in_report);
    }

    public function customers_get_all() {
        $output = $this->getCustomersByUserId();
        $this->output->set_content_type('application/json')->set_output(json_encode($output));
    }

    public function batches_get_all() {
        $output = $this->batches_list();
        $batches = array();
        foreach ($output as $kay => $val) {
            $batches[] = array('id' => $kay, 'value' => $val);
        }
        $this->output->set_content_type('application/json')->set_output(json_encode($batches));
    }

    public function delete_from_batch() {
        $batch_id = $this->input->post('batch_id');
        $research_data_id = $this->input->post('research_data_id');
        //$this->load->model('research_data_model');
        $this->load->model('statistics_model');
        $this->load->model('statistics_new_model');
        //$this->research_data_model->delete($research_data_id);
        $this->statistics_model->delete_by_research_data_id($batch_id, $research_data_id);
        $this->statistics_new_model->delete_by_research_data_id($batch_id, $research_data_id);
    }

    public function get_crawler_price_by_url() {
        $this->load->model('statistics_new_model');
        $url = $this->input->post('url');
        $res = $this->statistics_new_model->get_crawler_price_by_url_model($url);
        $this->output->set_content_type('application/json')->set_output(json_encode($res));
    }

    private function compare_str($str1, $str2) {
        $str1 = trim(strtolower($str1));
        $str2 = trim(strtolower($str2));
        $black_list = array('and', 'the', 'on', 'in', 'at', 'is', 'for');
        foreach ($black_list as $word) {
            $str1 = (substr($str1, 0, strlen($word)) === $word) ? substr($str1, strlen($word)) : $str1;
            $str1 = (substr($str1, (-1) * strlen($word)) === $word) ? substr($str1, 0, strlen($str1) - strlen($word)) : $str1;
            $str1 = trim($str1);
            $str2 = (substr($str2, 0, strlen($word)) === $word) ? substr($str2, strlen($word)) : $str2;
            $str2 = (substr($str2, (-1) * strlen($word)) === $word) ? substr($str2, 0, strlen($str2) - strlen($word)) : $str2;
            $str2 = trim($str2);
        }
        return strpos($str1, $str2) !== FALSE;
    }

    private function build_asses_table($results, $build_assess_params, $batch_id = '') 
	{
//        error_reporting(E_ALL);
        //Debugging
        $st_time = microtime(true);
        $this->load->model('batches_model');
        $this->load->model('statistics_model');
        $this->load->model('statistics_duplicate_content_model');

        
        $duplicate_content_range = 25;
        $success_filter_entries = array();
        $customer_name = $this->batches_model->getCustomerById($batch_id);
        $customer_url = parse_url($customer_name[0]->url);
        $result_table = array();
        $batch1_meta_percents = array();
        $batch2_meta_percents = array();
        $report = array();
        $pricing_details = array();
		
		//getting columns		
		$columns = AssessHelper::addCompetitorColumns(AssessHelper::columns(), $build_assess_params->max_similar_item_count);
		
		//extracting initial data varialbes for filters
        extract(AssessHelper::getInitialFilterData());
		
        $display_length = intval($this->input->get('iDisplayLength', TRUE));

        $display_start = intval($this->input->get('iDisplayStart', TRUE));
        if (empty($display_start)) {
            $display_start = 0;
        }

        if (empty($display_length)) {
            $display_length = $total_rows - $display_start;
        }
//            //Debugging
//            $dur = microtime(true)-$st_time;
//            header('Mem-and-Time1-BAT: '.memory_get_usage().'-'.$dur);
//            $st_time=  microtime(true);

        $qty = 1;
        $c=0;
        $total_rows = count($results);
        foreach ($results as $row_key => $row) {	
									
            $success_filter_entries = array();
            $f_count1 = 0;
            $r_count1 = 0;
            $result_row = new stdClass();
            $result_row->gap = '';
            $meta_key_gap = 0;
            $result_row->id = $row->id;
            $result_row->imported_data_id = $row->imported_data_id;
            $result_row->research_data_id = $row->research_data_id;
            $result_row->created = $row->created;
            if (!$row->product_name || $row->product_name == '') {
                $result_row->product_name = '-';
            } else {
                $result_row->product_name = $row->product_name;
            }
            if (!$row->url || $row->url == '') {
                $result_row->url = '-';
            } else {
                $result_row->url = $row->url;
            }

            $result_row->short_description_wc = intval($row->short_description_wc);
            $result_row->long_description_wc = intval($row->long_description_wc);
            $result_row->short_seo_phrases = "None";
            $result_row->title_seo_phrases = "None";
            $result_row->images_cmp = "None";
            $result_row->video_count = "None";
            $result_row->title_pa = "None";
            $result_row->links_count = "None";
            $result_row->long_seo_phrases = "None";
            $result_row->price_diff = "-";
            $result_row->imp_data_id = "";
            $result_row->column_external_content = "";
            $result_row->Custom_Keywords_Short_Description = "";
            $result_row->Custom_Keywords_Long_Description = "";
            $result_row->Meta_Description = "";
            $result_row->Meta_Description_Count = "";
            $result_row->item_id = "";
            $result_row->Meta_Keywords = "";
            $result_row->Page_Load_Time = "";
            $result_row->model = "";
            $result_row->H1_Tags = "";
            $result_row->H1_Tags_Count = "";
            $result_row->H2_Tags = "";
            $result_row->H2_Tags_Count = "";
            $result_row->column_reviews = 0;
            $result_row->average_review = "";
            $result_row->column_features = 0;
            $result_row->duplicate_content = "-";
            $result_row->own_price = floatval($row->own_price);
            $price_diff = unserialize($row->price_diff);
            $result_row->lower_price_exist = false;
            $result_row->snap = '';           
            $tb_product_name = '';

			
			
			if ($build_assess_params->short_less_check && $build_assess_params->short_more_check) {
                if ($result_row->short_description_wc > $build_assess_params->short_less && $result_row->short_description_wc < $build_assess_params->short_more) {
                    continue;
                }
            } else {
                if ($build_assess_params->short_less_check && $result_row->short_description_wc > $build_assess_params->short_less) {
                    continue;
                }
                if ($build_assess_params->short_more_check && $result_row->short_description_wc < $build_assess_params->short_more) {
                    continue;
                }
            }

            if ($build_assess_params->long_less_check && $build_assess_params->long_more_check) {
                if ($result_row->long_description_wc > $build_assess_params->long_less && $result_row->long_description_wc < $build_assess_params->long_more) {
                    continue;
                }
            } else {
                if ($build_assess_params->long_less_check && $result_row->long_description_wc > $build_assess_params->long_less) {
                    continue;
                }
                if ($build_assess_params->long_more_check && $result_row->long_description_wc < $build_assess_params->long_more) {
                    continue;
                }
            }

            if ($row->short_description) {
                $result_row->short_description = $row->short_description;
            } else {
                $result_row->short_description = '';
            }
            if ($row->long_description) {
                $result_row->long_description = $row->long_description;
            } else {
                $result_row->long_description = '';
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
                    $this->filterBySummaryCriteria('skus_25_duplicate_content', $build_assess_params->summaryFilterData, $success_filter_entries);
                }

                if ($percent >= 50) {
                    $skus_50_duplicate_content++;
                    $this->filterBySummaryCriteria('skus_50_duplicate_content', $build_assess_params->summaryFilterData, $success_filter_entries);
                }

                if ($percent >= 75) {
                    $skus_75_duplicate_content++;
                    $this->filterBySummaryCriteria('skus_75_duplicate_content', $build_assess_params->summaryFilterData, $success_filter_entries);
                }

                $result_row->Duplicate_Content.= $percent . ' %';                
            } else {
                $result_row->Duplicate_Content.='';
            }




            if ($build_assess_params->max_similar_item_count > 0) {                
                $sim_items = $row->similar_items;
                $max_similar_item_count = (int) $build_assess_params->max_similar_item_count;
                $tb_product_name = 'tb_product_name';


                for ($i = 1; $i <= $max_similar_item_count; $i++) {

                    $parsed_attributes_unserialize_val = '';
                    $parsed_anchors_unserialize_val = '';
                    $parsed_meta_unserialize_val = '';
                    $parsed_meta_unserialize_val_c = '';
                    $parsed_meta_unserialize_val_count = '';
                    $parsed_meta_keywords_unserialize_val = '';
                    $parsed_loaded_in_seconds_unserialize_val = '';
                    $parsed_H1_Tags_unserialize_val = '';
                    $parsed_H1_Tags_unserialize_val_count = '';
                    $parsed_H2_Tags_unserialize_val = '';
                    $parsed_H2_Tags_unserialize_val_count = '';
                    $parsed_column_reviews_unserialize_val = 0;
                    $parsed_average_review_unserialize_val = '';
                    $parsed_column_features_unserialize_val = 0;
                    $parsed_attributes_model_unserialize_val = '';
                    $column_external_content = '';
                    $images_cmp = '';
                    $video_count = '';
                    $title_pa = '';

                    $parsed_attributes_unserialize = unserialize($sim_items[$i - 1]->parsed_attributes);
                    $parsed_anchors_unserialize = unserialize($sim_items[$i - 1]->Anchors);

                    if (isset($parsed_attributes_unserialize['cnetcontent']) || isset($parsed_attributes_unserialize['webcollage']))
                        $column_external_content = $this->column_external_content($parsed_attributes_unserialize['cnetcontent'], $parsed_attributes_unserialize['webcollage']);

                    $HTags = unserialize($sim_items[$i - 1]->HTags);

                    if (isset($HTags['h1']) && $HTags['h1'] && $HTags['h1'] != '') {
                        $H1 = $HTags['h1'];
                        if (is_array($H1)) {
                            $str_1 = "<table  class='table_keywords_long'>";
                            $str_1_Count = "<table  class='table_keywords_long'>";
                            foreach ($H1 as $h1) {
                                $str_1.= "<tr><td>" . $h1 . "</td></tr>";
                                $str_1_Count.="<tr><td>" . strlen($h1) . "</td></tr>";
                            }
                            $str_1 .="</table>";
                            $str_1_Count .="</table>";
                            $parsed_H1_Tags_unserialize_val = $str_1;
                            $parsed_H1_Tags_unserialize_val_count = $str_1_Count;
                        } else {
                            $H1_Count = strlen($HTags['h1']);
                            $parsed_H1_Tags_unserialize_val = "<table  class='table_keywords_long'><tr><td>" . $H1 . "</td></tr></table>";
                            ;
                            $parsed_H1_Tags_unserialize_val_count = "<table  class='table_keywords_long'><tr><td>" . $H1_Count . "</td></tr></table>";
                            ;
                        }
                    }
                    if (isset($HTags['h2']) && $HTags['h2'] && $HTags['h2'] != '') {
                        $H2 = $HTags['h2'];
                        if (is_array($H2)) {
                            $str_2 = "<table  class='table_keywords_long'>";
                            $str_2_Count = "<table  class='table_keywords_long'>";
                            foreach ($H2 as $h2) {
                                $str_2.= "<tr><td>" . $h2 . "</td></tr>";
                                $str_2_Count.="<tr><td>" . strlen($h2) . "</td></tr>";
                            }
                            $str_2 .="</table>";
                            $str_2_Count .="</table>";
                            $parsed_H2_Tags_unserialize_val = $str_2;
                            $parsed_H2_Tags_unserialize_val_count = $str_2_Count;
                        } else {
                            $H1_Count = strlen($HTags['h2']);
                            $parsed_H2_Tags_unserialize_val = "<table  class='table_keywords_long'><tr><td>" . $H2 . "</td></tr></table>";
                            ;
                            $parsed_H2_Tags_unserialize_val_count = "<table  class='table_keywords_long'><tr><td>" . $H2_Count . "</td></tr></table>";
                            ;
                        }
                    }

                    if (isset($parsed_attributes_unserialize['item_id']))
                        $parsed_attributes_unserialize_val = $parsed_attributes_unserialize['item_id'];
                    if (isset($parsed_attributes_unserialize['model']))
                        $parsed_attributes_model_unserialize_val = $parsed_attributes_unserialize['model'];
                    if (isset($parsed_attributes_unserialize['loaded_in_seconds']))
                        $parsed_loaded_in_seconds_unserialize_val = $parsed_attributes_unserialize['loaded_in_seconds'];
                    if (isset($parsed_attributes_unserialize['review_count']))
                        $parsed_column_reviews_unserialize_val = $parsed_attributes_unserialize['review_count'];
                    if (isset($parsed_attributes_unserialize['average_review']))
                        $parsed_average_review_unserialize_val = $parsed_attributes_unserialize['average_review'];
                    if (isset($parsed_attributes_unserialize['feature_count']))
                        $parsed_column_features_unserialize_val = $parsed_attributes_unserialize['feature_count'];
                    if (isset($parsed_attributes_unserialize['product_images']))
                        $images_cmp = $parsed_attributes_unserialize['product_images'];
                    if (isset($parsed_attributes_unserialize['video_count']))
                        $video_count = $parsed_attributes_unserialize['video_count'];
                    if (isset($parsed_attributes_unserialize['title']))
                        $title_pa = $parsed_attributes_unserialize['title'];
                    if (isset($parsed_anchors_unserialize['quantity']))
                        $links_count = $parsed_anchors_unserialize['quantity'];
                   
                    $parsed_meta_unserialize = unserialize($sim_items[$i - 1]->parsed_meta);

                    if (isset($parsed_attributes_unserialize['pdf_count']) && $parsed_attributes_unserialize['pdf_count']) {
                        $skus_pdfs_competitor++;
                        $this->filterBySummaryCriteria('skus_pdfs_competitor', $build_assess_params->summaryFilterData, $success_filter_entries);
                    }
					
					if (isset($parsed_attributes_unserialize['video_count']) && $parsed_attributes_unserialize['video_count']) {
                        $skus_videos_competitor++;
                        $this->filterBySummaryCriteria('skus_videos_competitor', $build_assess_params->summaryFilterData, $success_filter_entries);
                    }
					
					if (isset($parsed_attributes_unserialize['product_images']))
					{
						if (!$parsed_attributes_unserialize['product_images']) {
							$skus_with_no_product_images_competitor++;
							$this->filterBySummaryCriteria('skus_with_no_product_images_competitor', $build_assess_params->summaryFilterData, $success_filter_entries);
						}
						
						if ($parsed_attributes_unserialize['product_images'] == 1) {
							$skus_with_one_product_image_competitor++;
							$this->filterBySummaryCriteria('skus_with_one_product_image_competitor', $build_assess_params->summaryFilterData, $success_filter_entries);
						}
						
						if ($parsed_attributes_unserialize['product_images'] > 1) {
							$skus_with_more_than_one_product_image_competitor++;
							$this->filterBySummaryCriteria('skus_with_more_than_one_product_image_competitor', $build_assess_params->summaryFilterData, $success_filter_entries);
						}
					}

                    if (!$parsed_anchors_unserialize['quantity']) {
                        $skus_with_zero_product_description_links_competitor++;
                        $this->filterBySummaryCriteria('skus_with_zero_product_description_links_competitor', $build_assess_params->summaryFilterData, $success_filter_entries);
                    }
                    
                    if($parsed_anchors_unserialize['quantity'] > 0) {
                        $skus_with_more_than_one_product_description_links_competitor++;
                        $this->filterBySummaryCriteria('skus_with_more_than_one_product_description_links_competitor', $build_assess_params->summaryFilterData, $success_filter_entries);
                    }

					
					if (isset($parsed_attributes_unserialize['title']) && $parsed_attributes_unserialize['title'] && strlen($parsed_attributes_unserialize['title']) < 70) {
                        $skus_title_less_than_70_chars_competitor++;
                        $this->filterBySummaryCriteria('skus_title_less_than_70_chars_competitor', $build_assess_params->summaryFilterData, $success_filter_entries);
                    }
					
					if (isset($parsed_attributes_unserialize['title']) && $parsed_attributes_unserialize['title'] && strlen($parsed_attributes_unserialize['title']) >= 70) {
                        $skus_title_more_than_70_chars_competitor++;
                        $this->filterBySummaryCriteria('skus_title_more_than_70_chars_competitor', $build_assess_params->summaryFilterData, $success_filter_entries);
                    }

                    if ($parsed_meta_unserialize['description']) {
                        $parsed_meta_unserialize_val = $parsed_meta_unserialize['description'];
                        $parsed_meta_unserialize_val_c = count(explode(" ", $parsed_meta_unserialize_val));
                        if ($parsed_meta_unserialize_val_c != 1)
                            $parsed_meta_unserialize_val_count = $parsed_meta_unserialize_val_c;
                        else
                            $parsed_meta_unserialize_val_count = '';
                    }
                    else if ($parsed_meta_unserialize['Description']) {
                        $parsed_meta_unserialize_val = $parsed_meta_unserialize['Description'];
                        $parsed_meta_unserialize_val_c = count(explode(" ", $parsed_meta_unserialize_val));
                        if ($parsed_meta_unserialize_val_c != 1)
                            $parsed_meta_unserialize_val_count = $parsed_meta_unserialize_val_c;
                        else
                            $parsed_meta_unserialize_val_count = '';
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
                            if ($sim_items[$i - 1]->Long_Description || $sim_items[$i - 1]->Short_Description) {
                                $_count_meta_un = $this->keywords_appearence($sim_items[$i - 1]->Long_Description . $sim_items[$i - 1]->Short_Description, $cnt_m_un);
                                $_count_meta_num_un = (float) round(($_count_meta_un * $cnt_meta_count_un / ($sim_items[$i - 1]->long_description_wc + $sim_items[$i - 1]->short_description_wc)) * 100, 2);

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
                    $result_row = (array) $result_row;
                    $result_row["snap$i"] = $sim_items[$i - 1]->snap !== false ? $sim_items[$i - 1]->snap : '-';
                    $result_row["imp_data_id$i"] = $sim_items[$i - 1]->imported_data_id !== false ? $sim_items[$i - 1]->imported_data_id : '';
                    $result_row['url' . $i] = $sim_items[$i - 1]->url !== false ? "<span class='res_url'><a target='_blank' href='" . $sim_items[$i - 1]->url . "'>" . $sim_items[$i - 1]->url . "</a></span>" : "-";
                    $result_row['Page_Load_Time' . $i] = $parsed_loaded_in_seconds_unserialize_val;
                    $result_row['product_name' . $i] = $sim_items[$i - 1]->product_name !== false ? "<span class='tb_product_name'>" . $sim_items[$i - 1]->product_name . "</span>" : "-";
                    $result_row['item_id' . $i] = $parsed_attributes_unserialize_val;
                    $result_row['model' . $i] = $parsed_attributes_model_unserialize_val;
                    $result_row['short_description_wc' . $i] = $sim_items[$i - 1]->short_description_wc !== false ? $sim_items[$i - 1]->short_description_wc : '';
                    $result_row['Short_Description' . $i] = $sim_items[$i - 1]->Short_Description !== false ? $sim_items[$i - 1]->Short_Description : '';
                    $result_row['Long_Description' . $i] = $sim_items[$i - 1]->Long_Description !== false ? $sim_items[$i - 1]->Long_Description : '';
                    $result_row['Meta_Keywords' . $i] = $parsed_meta_keywords_unserialize_val;
                    $result_row['long_description_wc' . $i] = $sim_items[$i - 1]->long_description_wc !== false ? $sim_items[$i - 1]->long_description_wc : '';
                    $result_row['Meta_Description' . $i] = $parsed_meta_unserialize_val;
                    $result_row['Meta_Description_Count' . $i] = $parsed_meta_unserialize_val_count;
                    $result_row['column_external_content' . $i] = $column_external_content;
                    $result_row['H1_Tags' . $i] = $parsed_H1_Tags_unserialize_val;
                    $result_row['H1_Tags_Count' . $i] = $parsed_H1_Tags_unserialize_val_count;
                    $result_row['H2_Tags' . $i] = $parsed_H2_Tags_unserialize_val;
                    $result_row['H2_Tags_Count' . $i] = $parsed_H2_Tags_unserialize_val_count;
                    $result_row['column_reviews' . $i] = $parsed_column_reviews_unserialize_val;
                    $result_row['average_review' . $i] = $parsed_average_review_unserialize_val;
                    $result_row['column_features' . $i] = $parsed_column_features_unserialize_val;
                    $result_row['title_seo_phrases' . $i] = $row->title_seo_pharses1 ? $row->title_seo_pharses1 : 'None';
                    $result_row['images_cmp' . $i] = $images_cmp ? $images_cmp : 'None';
                    $result_row['video_count' . $i] = $video_count ? $video_count : 'None';
                    $result_row['title_pa' . $i] = $title_pa ? $title_pa : 'None';
                    $result_row['links_count' . $i] = $links_count ? $links_count : 'None';
                }

                $result_row = (object) $result_row;
            }

            if ($row->snap1 && $row->snap1 != '') {
                $result_row->snap1 = "<span style='cursor:pointer;'><img src='" . base_url() . "webshoots/" . $row->snap1 . "' /></snap>";
            }
            if ($row->title_seo_phrases1) {
                $result_row->title_seo_phrases1 = $row->title_seo_phrases1;
            }
            if ($row->imp_data_id1) {
                $result_row->imp_data_id1 = $row->imp_data_id1;
            }
            if ($row->images_cmp1) {
                $result_row->images_cmp1 = $row->images_cmp1;
            }
            if ($row->video_count1) {
                $result_row->video_count1 = $row->video_count1;
            }
            if ($row->title_pa1) {
                $result_row->title_pa1 = $row->title_pa1;
            }
            if ($row->links_count1) {
                $result_row->links_count1 = $row->links_count1;
            }
            if ($row->product_name1) {
                $result_row->product_name1 = $row->product_name1;
            }
            if ($row->item_id1) {
                $result_row->item_id1 = $row->item_id1;
            }
            if ($row->Page_Load_Time1) {
                $result_row->Page_Load_Time1 = $row->Page_Load_Time1;
            }
            if ($row->H1_Tags1) {
                $result_row->H1_Tags1 = $row->H1_Tags1;
            }
            if ($row->H1_Tags_Count1) {
                $result_row->H1_Tags_Count1 = $row->H1_Tags_Count1;
            }
            if ($row->H2_Tags1) {
                $result_row->H2_Tags1 = $row->H2_Tags1;
            }
            if ($row->H2_Tags_Count1) {
                $result_row->H2_Tags_Count1 = $row->H2_Tags_Count1;
            }
            if ($row->column_reviews1) {
                $result_row->column_reviews1 = $row->column_reviews1;
            }
            if ($row->average_review1) {
                $result_row->average_review1 = $row->average_review1;
            }
            if ($row->column_features1) {
                $result_row->column_features1 = $row->column_features1;
            }
            if ($row->Short_Description1) {
                $result_row->Short_Description1 = $row->Short_Description1;
            }
            if ($row->Long_Description1) {
                $result_row->Long_Description1 = $row->Long_Description1;
            }
            if ($row->column_external_content1) {
                $result_row->column_external_content1 = $row->column_external_content1;
            }
            if ($row->Meta_Keywords1) {
                $result_row->Meta_Keywords1 = $row->Meta_Keywords1;
            }
            if ($row->model1) {
                $result_row->model1 = $row->model1;
            }
            if ($row->url1) {
                $result_row->url1 = "<span class='res_url'><a href='" . $row->url1 . "' target='_blank'>$row->url1</a><span>";
            }
            if ($row->short_description_wc1) {
                $result_row->short_description_wc1 = $row->short_description_wc1;
            }
            if ($row->long_description_wc1) {
                $result_row->long_description_wc1 = $row->long_description_wc1;
            }
            if ($row->Meta_Description1) {
                $result_row->Meta_Description1 = $row->Meta_Description1;
            }
            if ($row->Meta_Description_Count1) {
                $result_row->Meta_Description_Count1 = $row->Meta_Description_Count1;
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


            $result_row->H1_Tags = '';
            $result_row->H1_Tags_Count = '';
            if (isset($pars_atr['HTags']['h1']) && $pars_atr['HTags']['h1'] && $pars_atr['HTags']['h1'] != '') {
                $H1 = $pars_atr['HTags']['h1'];
                if (is_array($H1)) {
                    $str_1 = "<table  class='table_keywords_long'>";
                    $str_1_Count = "<table  class='table_keywords_long'>";
                    foreach ($H1 as $h1) {
                        $str_1.= "<tr><td>" . $h1 . "</td></tr>";
                        $str_1_Count.="<tr><td>" . strlen($h1) . "</td></tr>";
                    }
                    $str_1 .="</table>";
                    $str_1_Count .="</table>";
                    $result_row->H1_Tags = $str_1;
                    $result_row->H1_Tags_Count = $str_1_Count;
                } else {
                    $H1_Count = strlen($pars_atr['HTags']['h1']);
                    $result_row->H1_Tags = "<table  class='table_keywords_long'><tr><td>" . $H1 . "</td></tr></table>";
                    ;
                    $result_row->H1_Tags_Count = "<table  class='table_keywords_long'><tr><td>" . $H1_Count . "</td></tr></table>";
                    ;
                }
            }

            $result_row->H2_Tags = '';
            $result_row->H2_Tags_Count = '';
            if (isset($pars_atr['HTags']['h2']) && $pars_atr['HTags']['h2'] && $pars_atr['HTags']['h2'] != '') {
                $H2 = $pars_atr['HTags']['h2'];
                if (is_array($H2)) {
                    $str_2 = "<table  class='table_keywords_long'>";
                    $str_2_Count = "<table  class='table_keywords_long'>";
                    foreach ($H2 as $h2) {
                        $str_2.= "<tr><td>" . $h2 . "</td></tr>";
                        $str_2_Count.="<tr><td>" . strlen($h2) . "</td></tr>";
                    }
                    $str_2 .="</table>";
                    $str_2_Count .="</table>";
                    $result_row->H2_Tags = $str_2;
                    $result_row->H2_Tags_Count = $str_2_Count;
                } else {
                    $H2_Count = strlen($pars_atr['HTags']['h2']);
                    $result_row->H2_Tags = "<table  class='table_keywords_long'><tr><td>" . $H2 . "</td></tr></table>";
                    ;
                    $result_row->H2_Tags_Count = "<table  class='table_keywords_long'><tr><td>" . $H2_Count . "</td></tr></table>";
                    ;
                }
            }

            $custom_seo = $this->keywords_model->get_by_imp_id($row->imported_data_id);
            $Custom_Keywords_Long_Description = "<table class='table_keywords_long'>";
            if (isset($custom_seo['primary']) && $custom_seo['primary']) {
                if ($row->long_description) {
                    $_count = $this->keywords_appearence($row->long_description, $custom_seo['primary']);
                    $cnt = count(explode(' ', $custom_seo['primary']));
                    $_count = round(($_count * $cnt / $row->long_description_wc) * 100, 2) . "%";
                    $Custom_Keywords_Long_Description .= "<tr><td>" . $custom_seo['primary'] . "</td><td>$_count</td></tr>";
                } else {
                    $_count = ' ';
                }
            };
            if (isset($custom_seo['secondary']) && $custom_seo['secondary']) {
                if ($row->long_description) {
                    $_count = $this->keywords_appearence($row->long_description, $custom_seo['secondary']);
                    $cnt = count(explode(' ', $custom_seo['secondary']));
                    $_count = round(($_count * $cnt / $row->long_description_wc) * 100, 2) . "%";
                    $Custom_Keywords_Long_Description .= "<tr><td>" . $custom_seo['secondary'] . "</td><td>$_count</td></tr>";
                } else {
                    $_count = ' ';
                }
            };
            if (isset($custom_seo['tertiary']) && $custom_seo['tertiary']) {
                if ($row->long_description) {
                    $_count = $this->keywords_appearence($row->long_description, $custom_seo['tertiary']);
                    $cnt = count(explode(' ', $custom_seo['tertiary']));
                    $_count = round(($_count * $cnt / $row->long_description_wc) * 100, 2) . "%";
                    $Custom_Keywords_Long_Description .= "<tr><td>" . $custom_seo['tertiary'] . "</td><td> $_count</td></tr>";
                } else {
                    $_count = ' ';
                }
            };



            $result_row->Custom_Keywords_Long_Description = $Custom_Keywords_Long_Description . "</table>";

            $Custom_Keywords_Short_Description = "<table class='table_keywords_short'>";

            if (isset($custom_seo['primary'])) {
                if ($row->short_description) {
                    $_count = $this->keywords_appearence($row->short_description, $custom_seo['primary']);
                    $cnt = count(explode(' ', $custom_seo['primary']));
                    $_count = round(($_count * $cnt / $row->short_description_wc) * 100, 2) . "%";
                    $Custom_Keywords_Short_Description .= "<tr><td>" . $custom_seo['primary'] . "</td><td>$_count</td></tr>";
                } else {
                    $_count = ' ';
                }
            };
            if (isset($custom_seo['secondary'])) {
                if ($row->short_description) {
                    $_count = $this->keywords_appearence($row->short_description, $custom_seo['secondary']);
                    $cnt = count(explode(' ', $custom_seo['secondary']));
                    $_count = round(($_count * $cnt / $row->short_description_wc) * 100, 2) . "%";
                    $Custom_Keywords_Short_Description .= "<tr><td>" . $custom_seo['secondary'] . "</td><td>$_count</td></tr>";
                } else {
                    $_count = ' ';
                }
            };
            if (isset($custom_seo['tertiary'])) {
                if ($row->short_description) {
                    $_count = $this->keywords_appearence($row->short_description, $custom_seo['tertiary']);
                    $cnt = count(explode(' ', $custom_seo['tertiary']));
                    $_count = round(($_count * $cnt / $row->short_description_wc) * 100, 2) . "%";
                    $Custom_Keywords_Short_Description .= "<tr><td>" . $custom_seo['tertiary'] . "</td><td>$_count</td></tr>";
                } else {
                    $_count = ' ';
                }
            };
            $result_row->Custom_Keywords_Short_Description = $Custom_Keywords_Short_Description . "</table>";


			





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

            if ($this->settings['statistics_table'] == "statistics_new") {

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
                    $str_title_long_seo = '<table class="table_keywords_long 3186">';
                    foreach ($title_seo_pr as $val) {
                        $str_title_long_seo .= '<tr><td>' . $val['ph'] . '</td><td class = "phr-density">  ' . $val['prc']
                                . '%</td><td style="display:none;" class = "phr-frequency">  ' . $val['frq'] . '</td></tr>';
                    }
                    $result_row->title_seo_phrases = $str_title_long_seo . '</table>';
                }
            } else {
                $result_row->short_seo_phrases = $row->short_seo_phrases;
                $result_row->long_seo_phrases = $row->long_seo_phrases;
                $result_row->title_seo_phrases = '';
            }

	

            if ($build_assess_params->short_duplicate_content || $build_assess_params->long_duplicate_content) {
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
                            if ($build_assess_params->short_duplicate_content) {
                                $duplicate_short_percent_total = 100 - round($vs->short_original, 1);
                                $short_percent = 100 - round($vs->short_original, 1);
                                if ($short_percent > 0) {
                                    //$duplicate_customers_short = '<nobr>'.$vs->customer.' - '.$short_percent.'%</nobr><br />';
                                    $duplicate_customers_short = '<nobr>' . $short_percent . '%</nobr><br />';
                                }
                            }
                            if ($build_assess_params->long_duplicate_content) {
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

            if ($result_row->short_seo_phrases == 'None' && $result_row->long_seo_phrases == 'None') {
                $items_unoptimized_product_content++;
            }    

			// $recomend = false;
            // if (($result_row->short_description_wc <= $build_assess_params->short_less ||
                    // $result_row->long_description_wc <= $build_assess_params->long_less) && ($build_assess_params->long_less_check || $build_assess_params->long_more_check)
            // ) {
                // $recomend = true;
            // }
            // if ($result_row->short_seo_phrases == 'None' && $result_row->long_seo_phrases == 'None') {
                // $recomend = true;
            // }
            // if ($result_row->lower_price_exist == true && !empty($result_row->competitors_prices)) {
                // if (min($result_row->competitors_prices) < $result_row->own_price) {
                    // $recomend = true;
                // }
            // }

            // if ($build_assess_params->flagged == true && $recomend == false) {
                // continue;
            // }
            // if ($build_assess_params->price_diff == true && $result_row->lower_price_exist == false) {
                // continue;
            // }
			
			
			$pars_atr = $this->imported_data_parsed_model->getByImId($row->imported_data_id);
            if (isset($pars_atr['parsed_attributes']['pdf_count']) && $pars_atr['parsed_attributes']['pdf_count']) {
                $skus_pdfs++;
                $this->filterBySummaryCriteria('skus_pdfs', $build_assess_params->summaryFilterData, $success_filter_entries);
            }

			if (isset($pars_atr['parsed_attributes']['video_count']) && $pars_atr['parsed_attributes']['video_count']) {
                $skus_videos++;
                $this->filterBySummaryCriteria('skus_videos', $build_assess_params->summaryFilterData, $success_filter_entries);
            }
			
			if (isset($pars_atr['parsed_attributes']['product_images']))
			{
				if (!$pars_atr['parsed_attributes']['product_images']) {
					$skus_with_no_product_images++;
					$this->filterBySummaryCriteria('skus_with_no_product_images', $build_assess_params->summaryFilterData, $success_filter_entries);
				}
				
				if ($pars_atr['parsed_attributes']['product_images'] == 1) {
					$skus_with_one_product_image++;
					$this->filterBySummaryCriteria('skus_with_one_product_image', $build_assess_params->summaryFilterData, $success_filter_entries);
				}
				
				if ($pars_atr['parsed_attributes']['product_images'] > 1) {
					$skus_with_more_than_one_product_image++;
					$this->filterBySummaryCriteria('skus_with_more_than_one_product_image', $build_assess_params->summaryFilterData, $success_filter_entries);
				}
			}

            if (!$pars_atr['Anchors']['quantity']) {
                    $skus_with_zero_product_description_links++;
                    $this->filterBySummaryCriteria('skus_with_zero_product_description_links', $build_assess_params->summaryFilterData, $success_filter_entries);
            }
            if($pars_atr['Anchors']['quantity'] > 0) {
                    $skus_with_more_than_one_product_description_links++;
                    $this->filterBySummaryCriteria('skus_with_more_than_one_product_description_links', $build_assess_params->summaryFilterData, $success_filter_entries);
            }

			if (isset($pars_atr['parsed_attributes']['title']) && $pars_atr['parsed_attributes']['title'] && $pars_atr['parsed_attributes']['title'] < 70) {
                $skus_title_less_than_70_chars++;
                $this->filterBySummaryCriteria('skus_title_less_than_70_chars', $build_assess_params->summaryFilterData, $success_filter_entries);
            }

			if (isset($pars_atr['parsed_attributes']['title']) && $pars_atr['parsed_attributes']['title'] && $pars_atr['parsed_attributes']['title'] >= 70) {
                $skus_title_more_than_70_chars++;
                $this->filterBySummaryCriteria('skus_title_more_than_70_chars', $build_assess_params->summaryFilterData, $success_filter_entries);
            }	

			//gap analises
            if ($build_assess_params->max_similar_item_count > 0) {
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
                    $this->filterBySummaryCriteria('skus_fewer_features_than_competitor', $build_assess_params->summaryFilterData, $success_filter_entries);
                }

                if ($result_row->column_reviews < $result_row->column_reviews1) {
                    $skus_fewer_reviews_than_competitor++;
                    $this->filterBySummaryCriteria('skus_fewer_reviews_than_competitor', $build_assess_params->summaryFilterData, $success_filter_entries);
                }

                if ($result_row->column_features) {
                    $skus_features++;
                    $this->filterBySummaryCriteria('skus_features', $build_assess_params->summaryFilterData, $success_filter_entries);
                }

                if ($result_row->column_features1) {
                    $skus_features_competitor++;
                    $this->filterBySummaryCriteria('skus_features_competitor', $build_assess_params->summaryFilterData, $success_filter_entries);
                }

                /*
                 * Reviews section
                 */
                //First batch								
                if (!$result_row->column_reviews) {
                    $skus_zero_reviews++;
                    $this->filterBySummaryCriteria('skus_zero_reviews', $build_assess_params->summaryFilterData, $success_filter_entries);
                }

                if ($result_row->column_reviews >= 1 && $result_row->column_reviews <= 4) {
                    $skus_one_four_reviews++;
                    $this->filterBySummaryCriteria('skus_one_four_reviews', $build_assess_params->summaryFilterData, $success_filter_entries);
                }

                if ($result_row->column_reviews >= 5) {
                    $skus_more_than_five_reviews++;
                    $this->filterBySummaryCriteria('skus_more_than_five_reviews', $build_assess_params->summaryFilterData, $success_filter_entries);
                }

                if ($result_row->column_reviews >= 100) {
                    $skus_more_than_hundred_reviews++;
                    $this->filterBySummaryCriteria('skus_more_than_hundred_reviews', $build_assess_params->summaryFilterData, $success_filter_entries);
                }

                //Second batch								
                if (!$result_row->column_reviews1) {
                    $skus_zero_reviews_competitor++;
                    $this->filterBySummaryCriteria('skus_zero_reviews_competitor', $build_assess_params->summaryFilterData, $success_filter_entries);
                }

                if ($result_row->column_reviews1 >= 1 && $result_row->column_reviews1 <= 4) {
                    $skus_one_four_reviews_competitor++;
                    $this->filterBySummaryCriteria('skus_one_four_reviews_competitor', $build_assess_params->summaryFilterData, $success_filter_entries);
                }

                if ($result_row->column_reviews1 >= 5) {
                    $skus_more_than_five_reviews_competitor++;
                    $this->filterBySummaryCriteria('skus_more_than_five_reviews_competitor', $build_assess_params->summaryFilterData, $success_filter_entries);
                }

                if ($result_row->column_reviews1 >= 100) {
                    $skus_more_than_hundred_reviews_competitor++;
                    $this->filterBySummaryCriteria('skus_more_than_hundred_reviews_competitor', $build_assess_params->summaryFilterData, $success_filter_entries);
                }
            }
			
            if ($result_row->lower_price_exist == true) {
                $items_priced_higher_than_competitors += $row->items_priced_higher_than_competitors;

                $this->filterBySummaryCriteria('assess_report_items_priced_higher_than_competitors', $build_assess_params->summaryFilterData, $success_filter_entries);
            }
			
			if (trim($result_row->column_external_content)) {
                $skus_third_party_content++;
                $this->filterBySummaryCriteria('skus_third_party_content', $build_assess_params->summaryFilterData, $success_filter_entries);
            }

            if (trim($result_row->column_external_content1)) {
                $skus_third_party_content_competitor++;
                $this->filterBySummaryCriteria('skus_third_party_content_competitor', $build_assess_params->summaryFilterData, $success_filter_entries);
            }

            $first_general_description_size = $result_row->short_description_wc + $result_row->long_description_wc;
            $second_general_description_size = $result_row->short_description_wc1 + $result_row->long_description_wc1;

            if ($first_general_description_size < $second_general_description_size) {
                $skus_shorter_than_competitor_product_content++;
                $this->filterBySummaryCriteria('skus_shorter_than_competitor_product_content', $build_assess_params->summaryFilterData, $success_filter_entries);
            }

            if ($first_general_description_size > $second_general_description_size) {
                $skus_longer_than_competitor_product_content++;
                $this->filterBySummaryCriteria('skus_longer_than_competitor_product_content', $build_assess_params->summaryFilterData, $success_filter_entries);
            }

            if ($first_general_description_size == $second_general_description_size) {
                $skus_same_competitor_product_content++;
                $this->filterBySummaryCriteria('skus_same_competitor_product_content', $build_assess_params->summaryFilterData, $success_filter_entries);
            }

            // For Batch 1
            if ($first_general_description_size < 50) {
                $skus_fewer_50_product_content++;
                $this->filterBySummaryCriteria('skus_fewer_50_product_content', $build_assess_params->summaryFilterData, $success_filter_entries);
            }

            if ($first_general_description_size < 100) {
                $skus_fewer_100_product_content++;
                $this->filterBySummaryCriteria('skus_fewer_100_product_content', $build_assess_params->summaryFilterData, $success_filter_entries);
            }

            if ($first_general_description_size < 150) {
                $skus_fewer_150_product_content++;
                $this->filterBySummaryCriteria('skus_fewer_150_product_content', $build_assess_params->summaryFilterData, $success_filter_entries);
            }

            // For Competitor (Batch 2)
            if ($second_general_description_size < 50 && $build_assess_params->compare_batch_id) {
                $skus_fewer_50_product_content_competitor++;
                $this->filterBySummaryCriteria('skus_fewer_50_product_content_competitor', $build_assess_params->summaryFilterData, $success_filter_entries);
            }

            if ($second_general_description_size < 100 && $build_assess_params->compare_batch_id) {
                $skus_fewer_100_product_content_competitor++;
                $this->filterBySummaryCriteria('skus_fewer_100_product_content_competitor', $build_assess_params->summaryFilterData, $success_filter_entries);
            }

            if ($second_general_description_size < 150 && $build_assess_params->compare_batch_id) {
                $skus_fewer_150_product_content_competitor++;
                $this->filterBySummaryCriteria('skus_fewer_150_product_content_competitor', $build_assess_params->summaryFilterData, $success_filter_entries);
            }
			
					$batch1_filtered_title_percents = substr_count($result_row->title_seo_phrases, '%');
			$batch2_filtered_title_percents = substr_count($result_row->title_seo_phrases1, '%');
			
			if ($batch1_filtered_title_percents < $batch2_filtered_title_percents)
			{
				$skus_fewer_competitor_optimized_keywords++;
				$this->filterBySummaryCriteria('skus_fewer_competitor_optimized_keywords', $build_assess_params->summaryFilterData, $success_filter_entries);					
			}
			
			if (!$batch1_filtered_title_percents)
			{
				$skus_zero_optimized_keywords++;
				$this->filterBySummaryCriteria('skus_zero_optimized_keywords', $build_assess_params->summaryFilterData, $success_filter_entries);
			}
			
			if ($batch1_filtered_title_percents >= 1)
			{
				$skus_one_optimized_keywords++;
				$this->filterBySummaryCriteria('skus_one_optimized_keywords', $build_assess_params->summaryFilterData, $success_filter_entries);		
			}
				
			if ($batch1_filtered_title_percents >= 2)
			{
				$skus_two_optimized_keywords++;
				$this->filterBySummaryCriteria('skus_two_optimized_keywords', $build_assess_params->summaryFilterData, $success_filter_entries);			
			}
				
			if ($batch1_filtered_title_percents >= 3)
			{
				$skus_three_optimized_keywords++;			
				$this->filterBySummaryCriteria('skus_three_optimized_keywords', $build_assess_params->summaryFilterData, $success_filter_entries);
			}
			
			
			if (!$batch2_filtered_title_percents)
			{
				$skus_zero_optimized_keywords_competitor++;
				$this->filterBySummaryCriteria('skus_zero_optimized_keywords_competitor', $build_assess_params->summaryFilterData, $success_filter_entries);
			}
			
			if ($batch2_filtered_title_percents >= 1)
			{
				$skus_one_optimized_keywords_competitor++;
				$this->filterBySummaryCriteria('skus_one_optimized_keywords_competitor', $build_assess_params->summaryFilterData, $success_filter_entries);		
			}
				
			if ($batch2_filtered_title_percents >= 2)
			{
				$skus_two_optimized_keywords_competitor++;
				$this->filterBySummaryCriteria('skus_two_optimized_keywords_competitor', $build_assess_params->summaryFilterData, $success_filter_entries);			
			}
				
			if ($batch2_filtered_title_percents >= 3)
			{
				$skus_three_optimized_keywords_competitor++;			
				$this->filterBySummaryCriteria('skus_three_optimized_keywords_competitor', $build_assess_params->summaryFilterData, $success_filter_entries);
			}
	
		
			$are_records_on_the_page = $c >= $display_start && $c < ($display_start + $display_length);
			$are_records_filtered = $this->checkSuccessFilterEntries($success_filter_entries, $build_assess_params->summaryFilterData);
            
			if (!$build_assess_params->summaryFilterData && $are_records_on_the_page) {
                $result_table[] = $result_row;				
            } else if ($are_records_filtered) {
				
				if ($filtered_count >= $display_start && $filtered_count < ($display_start + $display_length))
				{					
					$result_table[] = $result_row;	
				}
				$filtered_count++;
				
			}
		
			$c++;							         
        }

//            //Debugging
//            $dur = microtime(true)-$st_time;
//            header('Mem-and-Time2-BAT01: '.memory_get_usage().'-'.$dur);
//            $st_time=  microtime(true);  
      
//Debugging problem part
        if ($this->settings['statistics_table'] == "statistics_new") {
            $own_batch_total_items = $this->statistics_new_model->total_items_in_batch($batch_id);
        } else {
            $own_batch_total_items = $this->statistics_model->total_items_in_batch($batch_id);
        }


		$summary_fields = array(
			'assess_report_total_items' => array( 'value' => $own_batch_total_items, 'percentage' => array() ),
			'items_priced_higher_than_competitors' => array( 'value' => $items_priced_higher_than_competitors, 'percentage' => array('batch1')),
			'items_have_more_than_20_percent_duplicate_content' => array( 'value' => $items_have_more_than_20_percent_duplicate_content, 'percentage' => array()),
			'skus_25_duplicate_content' => array( 'value' => $skus_25_duplicate_content, 'percentage' => array('batch1')),
			'skus_50_duplicate_content' => array( 'value' => $skus_50_duplicate_content, 'percentage' => array('batch1')),
			'skus_75_duplicate_content' => array( 'value' => $skus_75_duplicate_content, 'percentage' => array('batch1')),
			'items_unoptimized_product_content' => array( 'value' => $items_unoptimized_product_content, 'percentage' => array()),
			'items_short_products_content_short' => array( 'value' => $items_short_products_content_short, 'percentage' => array()),
			'items_long_products_content_short' => array( 'value' => $items_long_products_content_short, 'percentage' => array()),
			'short_wc_total_not_0' => array( 'value' => $short_wc_total_not_0, 'percentage' => array()),
			'long_wc_total_not_0' => array( 'value' => $long_wc_total_not_0, 'percentage' => array()),
			'short_description_wc_lower_range' => array( 'value' => $build_assess_params->short_less, 'percentage' => array()),
			'long_description_wc_lower_range' => array( 'value' => $build_assess_params->long_less, 'percentage' => array()),
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
			
			'total_items_selected_by_filter' => array( 'value' => count($result_table), 'percentage' => array()),
			'assess_report_competitor_matches_number' => array( 'value' => $build_assess_params->batch2_items_count, 'percentage' => array()),
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
            'skus_with_more_than_one_product_description_links' => array( 'value' => $skus_with_more_than_one_product_description_links, 'percentage' => array('batch1', 'competitor'), 'generals' => array('competitor' => $skus_with_zero_product_description_links_competitor)),

            'skus_with_zero_product_description_links_competitor' => array( 'value' => $skus_with_zero_product_description_links_competitor, 'percentage' => array('batch2', 'competitor'), 'generals' => array('competitor' => $skus_with_zero_product_description_links)),
            'skus_with_more_than_one_product_description_links_competitor' => array( 'value' => $skus_with_more_than_one_product_description_links_competitor, 'percentage' => array('batch2', 'competitor'), 'generals' => array('competitor' => $skus_with_zero_product_description_links_competitor)),

		);		
				
		foreach ($summary_fields as $key => $summary_field)
		{						
			$my_percent = 0;
			
			$report['summary'][$key] = trim($summary_field['value']) . $this->calculatePercentage(array('batch1' => $own_batch_total_items, 'batch2' => $build_assess_params->batch2_items_count), $summary_field, $my_percent);
			if (isset($summary_field['icon']))
				$report['summary'][$key . '_icon'] = $summary_field['icon'];
			
			if (isset($summary_field['icon_percentage']))
			{
				$report['summary'][$key . '_icon'] = $summary_field['icon_percentage']($my_percent);
			}			
		}		              

        if ($items_priced_higher_than_competitors > 0) {
            $report['recommendations']['items_priced_higher_than_competitors'] = 'Reduce pricing on ' . $items_priced_higher_than_competitors . ' item(s)';
        }
        if ($items_have_more_than_20_percent_duplicate_content > 0) {
            $report['recommendations']['items_have_more_than_20_percent_duplicate_content'] = 'Create original product content';
        }
        if ($items_unoptimized_product_content > 0) {
            $report['recommendations']['items_unoptimized_product_content'] = 'Optimize product content';
        }
        if ($items_short_products_content_short > 0) {
            $report['recommendations']['items_short_products_content_short'] = 'Increase short product description lengths';
        }
        if ($items_long_products_content_short > 0) {
            $report['recommendations']['items_long_products_content_short'] = 'Increase long product description lengths';
        }

        $report['detail_comparisons_total'] = $detail_comparisons_total;
        //Debugging
        $dur = microtime(true) - $st_time;
        header('Mem-and-Time2-BAT03: ' . memory_get_usage() . '-' . $dur);
        $st_time = microtime(true);

        $this->load->library('pagination');
        $config['base_url'] = $this->config->site_url() . '/assess/comparison_detail';
        $config['total_rows'] = $detail_comparisons_total;
        $config['per_page'] = '1';
        $config['uri_segment'] = 3;
        $this->pagination->initialize($config);
        $report['comparison_pagination'] = $this->pagination->create_links();


        if ($build_assess_params->all_columns) {
            $s_columns = explode(',', $build_assess_params->all_columns);
            $s_column_index_cmp = $build_assess_params->sort_columns;
            $s_column_index = intval($build_assess_params->sort_columns);
            $s_column = $s_columns[$s_column_index];
            $this->sort_column = $s_column;
            $sort_direction = strtolower($build_assess_params->sort_dir);
            if ($s_column == 'price_diff') {
                if ($sort_direction == 'asc') {
                    $this->sort_direction = 'desc';
                } else
                if ($sort_direction == 'desc') {
                    $this->sort_direction = 'asc';
                } else {
                    $this->sort_direction = 'asc';
                }
            } else {
                $this->sort_direction = $sort_direction;
            }
            $this->sort_type = is_numeric($result_table[0]->$s_column) ? "num" : "";


            if ($s_column == 'product_name') {
                usort($result_table, array("Assess", "assess_sort_ignore"));
            } else {
                usort($result_table, array("Assess", "assess_sort"));
            }
        }


        $output = array(
            "sEcho" => intval($this->input->get('sEcho')),
            "iTotalRecords" => $filtered_count ?: $total_rows,
            "iTotalDisplayRecords" => $filtered_count ?: $total_rows,
            "iDisplayLength" => $display_length,
            "aaData" => array()
        );
       

        if (!empty($result_table)) {
          
            foreach ($result_table as $data_row) {

               

                    if (isset($data_row->recommendations)) {
                        // this is for absent product in selected batch only
                        $recommendations_html = '<ul class="assess_recommendations"><li>' . $data_row->recommendations . '</li></ul>';
                    } else {
                        $img_path = base_url() . "img/";
                        $recommendations = array();

                        if ($data_row->short_description_wc == 0 && $data_row->long_description_wc == 0) {
                            $recommendations[] = array(
                                'img' => '<img class="bullet" src="' . $img_path . 'assess_report_D.png">',
                                'msg' => 'Add product descriptions',
                            );
                        }

                        if ($data_row->short_description_wc > 0 && $data_row->long_description_wc == 0) {
                            if ($data_row->short_description_wc > 100) {
                                $sd_diff = 100 - $data_row->short_description_wc;
                            } else {
                                $sd_diff = $build_assess_params->short_less - $data_row->short_description_wc;
                            }
                            if ($sd_diff > 0) {
                                $recommendations[] = array(
                                    'img' => '<img class="bullet" src="' . $img_path . 'assess_report_arrow_up.png">',
                                    'msg' => 'Increase descriptions word count by ' . $sd_diff . ' words',
                                );
                            }
                        }
                        if ($data_row->long_description_wc > 0 && $data_row->short_description_wc == 0) {
                            if ($data_row->long_description_wc > 200) {
                                $ld_diff = 200 - $data_row->long_description_wc;
                            } else {
                                $ld_diff = $build_assess_params->long_less - $data_row->long_description_wc;
                            }
                            if ($ld_diff > 0) {
                                $recommendations[] = array(
                                    'img' => '<img class="bullet" src="' . $img_path . 'assess_report_arrow_up.png">',
                                    'msg' => 'Increase descriptions word count by ' . $ld_diff . ' words',
                                );
                            }
                        }

                        if ($data_row->short_description_wc > 0 && $data_row->long_description_wc != 0) {
                            if ($data_row->short_description_wc > 100) {
                                $sd_diff = 100 - $data_row->short_description_wc;
                            } else {
                                $sd_diff = $build_assess_params->short_less - $data_row->short_description_wc;
                            }
                            if ($sd_diff > 0) {
                                $recommendations[] = array(
                                    'img' => '<img class="bullet" src="' . $img_path . 'assess_report_arrow_up.png">',
                                    'msg' => 'Increase short descriptions word count by ' . $sd_diff . ' words',
                                );
                            }
                        }
                        if ($data_row->long_description_wc > 0 && $data_row->short_description_wc != 0) {
                            if ($data_row->long_description_wc > 200) {
                                $ld_diff = 200 - $data_row->long_description_wc;
                            } else {
                                $ld_diff = $build_assess_params->long_less - $data_row->long_description_wc;
                            }
                            if ($ld_diff > 0) {
                                $recommendations[] = array(
                                    'img' => '<img class="bullet" src="' . $img_path . 'assess_report_arrow_up.png">',
                                    'msg' => 'Increase long descriptions word count by ' . $ld_diff . ' words',
                                );
                            }
                        }

                        if ($data_row->short_seo_phrases == 'None' && $data_row->long_seo_phrases == 'None') {
                            $recommendations[] = array(
                                'img' => '<img class="bullet" src="' . $img_path . 'assess_report_seo.png">',
                                'msg' => 'Keyword optimize product content',
                            );
                        }
                        if ($data_row->lower_price_exist == true && !empty($data_row->competitors_prices)) {
                            if (min($data_row->competitors_prices) < $data_row->own_price) {
                                $min_price_diff = $data_row->own_price - min($data_row->competitors_prices);
                                $recommendations[] = array(
                                    'img' => '<img class="bullet" src="' . $img_path . 'assess_report_dollar.png">',
                                    'msg' => 'Lower price by $' . $min_price_diff . ' to be competitive',
                                );
                            }
                        }

                        $data_row->recommendations = $recommendations;

                        for ($i = 0; $i < count($recommendations); $i++) {
                            $recommendations[$i] = '<li>' . $recommendations[$i]['img'] . $recommendations[$i]['msg'] . '</li>';
                        }

                        $recommendations_html = '<ul class="assess_recommendations">' . implode('', $recommendations) . '</ul>';
                    }

                    $row_created_array = explode(' ', $data_row->created);
                    $row_created = '<nobr>' . $row_created_array[0] . '</nobr><br/>';
                    $row_created = $row_created . '<nobr>' . $row_created_array[1] . '</nobr>';
                    $snap = '';

                    $row_url = '<a class="active_link" href="' . $data_row->url . '" target="_blank">' . $data_row->url . '</a>';
                    if ($data_row->snap != '') {
                        $file = realpath(BASEPATH . "../webroot/webshoots") . '/' . $data_row->snap;
                        if (file_exists($file)) {
                            if (filesize($file) > 1024) {
                                $snap = "<img src='" . base_url() . "webshoots/" . $data_row->snap . "' />";
                            }
                        }
                    }

                    $output_row = array(
                        'snap' => '<span style="cursor:pointer;">' . $snap . '</span>',
                        'created' => $row_created,
                        'imp_data_id' => $data_row->imported_data_id,
                        'product_name' => '<span class= "' . $tb_product_name . '">' . $data_row->product_name . "</span>",
                        'item_id' => $data_row->item_id,
                        'model' => $data_row->model,
                        'url' => $row_url,
                        'Page_Load_Time' => $data_row->Page_Load_Time,
                        'Short_Description' => $data_row->short_description,
                        'short_description_wc' => $data_row->short_description_wc,
                        'Meta_Keywords' => $data_row->Meta_Keywords,
                        'short_seo_phrases' => $data_row->short_seo_phrases,
                        'title_seo_phrases' => $data_row->title_seo_phrases,
                        'images_cmp' => $data_row->images_cmp,
                        'video_count' => $data_row->video_count,
                        'title_pa' => $data_row->title_pa,
                        'links_count' => $data_row->links_count,
                        'long_description' => $data_row->long_description,
                        'long_description_wc' => $data_row->long_description_wc,
                        'long_seo_phrases' => $data_row->long_seo_phrases,
                        'Custom_Keywords_Short_Description' => $data_row->Custom_Keywords_Short_Description,
                        'Custom_Keywords_Long_Description' => $data_row->Custom_Keywords_Long_Description,
                        'Meta_Description' => $data_row->Meta_Description,
                        'Meta_Description_Count' => $data_row->Meta_Description_Count,
                        'H1_Tags' => $data_row->H1_Tags,
                        'H1_Tags_Count' => $data_row->H1_Tags_Count,
                        'H2_Tags' => $data_row->H2_Tags,
                        'H2_Tags_Count' => $data_row->H2_Tags_Count,
                        'duplicate_content' => $data_row->duplicate_content,
                        'column_external_content' => $data_row->column_external_content,
                        'column_reviews' => $data_row->column_reviews,
                        'average_review' => $data_row->average_review,
                        'column_features' => $data_row->column_features,
                        'price_diff' => $data_row->price_diff,
                        'recommendations' => $recommendations_html,
                        'json_encoded_data' => json_encode($data_row)
                    );

                    if ($build_assess_params->max_similar_item_count > 0) {
                        $data_row = (array) $data_row;
                        for ($i = 1; $i <= $build_assess_params->max_similar_item_count; $i++) {
                            $output_row['snap' . $i] = $data_row['snap' . $i] != null ? $data_row['snap' . $i] : '-';
                            $output_row['imp_data_id' . $i] = $data_row['imp_data_id' . $i] != null ? $data_row['imp_data_id' . $i] : '';
                            $output_row['product_name' . $i] = $data_row['product_name' . $i] != null ? $data_row['product_name' . $i] : '-';
                            $output_row['item_id' . $i] = $data_row['item_id' . $i] != null ? $data_row['item_id' . $i] : '';
                            $output_row['model' . $i] = $data_row['model' . $i] != null ? $data_row['model' . $i] : '';
                            $output_row['url' . $i] = $data_row['url' . $i] != null ? $data_row['url' . $i] : '-';
                            $output_row['Page_Load_Time' . $i] = $data_row['Page_Load_Time' . $i] != null ? $data_row['Page_Load_Time' . $i] : '';
                            $output_row['Short_Description' . $i] = $data_row['Short_Description' . $i] != null ? $data_row['Short_Description' . $i] : '';
                            $output_row['short_description_wc' . $i] = $data_row['short_description_wc' . $i] != null ? $data_row['short_description_wc' . $i] : '';
                            $output_row['Meta_Keywords' . $i] = $data_row['Meta_Keywords' . $i] != null ? $data_row['Meta_Keywords' . $i] : '';
                            $output_row['Long_Description' . $i] = $data_row['Long_Description' . $i] != null ? $data_row['Long_Description' . $i] : '';
                            $output_row['long_description_wc' . $i] = $data_row['long_description_wc' . $i] != null ? $data_row['long_description_wc' . $i] : '';
                            $output_row['Meta_Description' . $i] = $data_row['Meta_Description' . $i] != null ? $data_row['Meta_Description' . $i] : '';
                            $output_row['Meta_Description_Count' . $i] = $data_row['Meta_Description_Count' . $i] != null ? $data_row['Meta_Description_Count' . $i] : '';
                            $output_row[] = $data_row['column_external_content' . $i] != null ? $data_row['column_external_content' . $i] : '';
                            $output_row['H1_Tags' . $i] = $data_row['H1_Tags' . $i] != null ? $data_row['H1_Tags' . $i] : '';
                            $output_row['H1_Tags_Count' . $i] = $data_row['H1_Tags_Count' . $i] != null ? $data_row['H1_Tags_Count' . $i] : '';
                            $output_row['H2_Tags' . $i] = $data_row['H2_Tags' . $i] != null ? $data_row['H2_Tags' . $i] : '';
                            $output_row['H2_Tags_Count' . $i] = $data_row['H2_Tags_Count' . $i] != null ? $data_row['H2_Tags_Count' . $i] : '';
                            $output_row['column_reviews' . $i] = $data_row['column_reviews' . $i] != null ? $data_row['column_reviews' . $i] : 0;
                            $output_row['average_review' . $i] = $data_row['average_review' . $i] != null ? $data_row['average_review' . $i] : '';
                            $output_row['column_features' . $i] = $data_row['column_features' . $i] != null ? $data_row['column_features' . $i] : '';
                            $output_row['title_seo_phrases' . $i] = $data_row['title_seo_phrases' . $i] != null ? $data_row['title_seo_phrases' . $i] : '';
                            $output_row['images_cmp' . $i] = $data_row['images_cmp' . $i] != null ? $data_row['images_cmp' . $i] : 'none';
                            $output_row['video_count' . $i] = $data_row['video_count' . $i] != null ? $data_row['video_count' . $i] : 'none';
                            $output_row['title_pa' . $i] = $data_row['title_pa' . $i] != null ? $data_row['title_pa' . $i] : '';
                            $output_row['links_count' . $i] = $data_row['links_count' . $i] != null ? $data_row['links_count' . $i] : '';
                        }

                        $output_row['gap'] = $data_row['gap'];
                        $output_row['Duplicate_Content'] = $data_row['Duplicate_Content'];                      
                    } else {
                        $output_row['snap1'] = $data_row->snap1;
                        $output_row['imp_data_id1'] = $data_row->imp_data_id1;
                        $output_row['product_name1'] = $data_row->product_name1;
                        $output_row['item_id1'] = $data_row->item_id1;
                        $output_row['model1'] = $data_row->model1;
                        $output_row['url1'] = $data_row->url1;
                        $output_row['Page_Load_Time1'] = $data_row->Page_Load_Time1;
                        $output_row['Short_Description1'] = $data_row->Short_Description1;
                        $output_row['short_description_wc1'] = $data_row->short_description_wc1;
                        $output_row['Meta_Keywords1'] = $data_row->Meta_Keywords1;
                        $output_row['Long_Description1'] = $data_row->Long_Description1;
                        $output_row['long_description_wc1'] = $data_row->long_description_wc1;
                        $output_row['Meta_Description1'] = $data_row->Meta_Description1;
                        $output_row['Meta_Description_Count1'] = $data_row->Meta_Description_Count1;
                        $output_row['column_external_content1'] = $data_row->column_external_content1;
                        $output_row['H1_Tags1'] = $data_row->H1_Tags1;
                        $output_row['H1_Tags_Count1'] = $data_row->H1_Tags_Count1;
                        $output_row['H2_Tags1'] = $data_row->H2_Tags1;
                        $output_row['H2_Tags_Count1'] = $data_row->H2_Tags_Count1;
                        $output_row['column_reviews1'] = $data_row->column_reviews1;
                        $output_row['average_review1'] = $data_row->average_review1;
                        $output_row['column_features1'] = $data_row->column_features1;
                        $output_row['title_seo_phrases1'] = $data_row->title_seo_phrases1;
                        $output_row['images_cmp1'] = $data_row->images_cmp1;
                        $output_row['video_count1'] = $data_row->video_count1;
                        $output_row['title_pa1'] = $data_row->title_pa1;
                        $output_row['links_count1'] = $data_row->links_count1;
                        $output_row['gap'] = $data_row->gap;
                        $output_row['Duplicate_Content'] = $data_row->Duplicate_Content;
                    }
                    
                    $output['aaData'][] = AssessHelper::setTableData($columns, $output_row);
            }
        }
						
        $output['aoColumns'] = $columns;
        $output['ExtraData']['report'] = $report;        
        return $output;
    }
	
	public function getColumns()
	{								
		$this->output->set_content_type('application/json')
                    ->set_output(json_encode(AssessHelper::addCompetitorColumns(AssessHelper::columns())));
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

    private function filterBySummaryCriteria($current_criteria, $filterCriterias, &$success_filter_entries) {
        $success_filter_entries[] = in_array('batch_me_' . $current_criteria, $filterCriterias) || in_array('batch_competitor_' . $current_criteria, $filterCriterias);
				
    }

    private function checkSuccessFilterEntries($success_filter_entries, $filterCriterias) {
        if (!$filterCriterias)
            return true;

        return array_filter($success_filter_entries);
    }

    public function get_board_view_snap() {

        if (isset($_POST['batch_id']) && isset($_POST['compare_batch_id'])) {
            if (trim($_POST['batch_id']) == '')
                $batch_id = -1;
            else
                $batch_id = $_POST['batch_id'];

            if (trim($_POST['compare_batch_id']) == '' || $_POST['compare_batch_id'] == 'all' || $_POST['compare_batch_id'] == 0)
                $batch_compare_id = -1;
            else {
                $batch_compare_id = $_POST['compare_batch_id'];
                $this->load->model('batches_model');
                $customer_name = $this->batches_model->getCustomerUrlByBatch($batch_compare_id);
            }

            $batch_arr = array($batch_id, $batch_compare_id);
            $snap_data = array();

            $params = new stdClass();
            $params->batch_id = $batch_id;
            $params->txt_filter = '';
            $params->date_from = '';
            $params->date_to = '';
            $results = $this->get_data_for_assess($params);
            
//            var_dump(count($results));
            if ($batch_compare_id != -1) {
                foreach ($results as $val) {
                    $similar_items_data = array();
                    if (substr_count(strtolower($val->similar_products_competitors), strtolower($customer_name)) > 0) {
                        $similar_items = unserialize($val->similar_products_competitors);
                        if (count($similar_items) > 1) {
                            foreach ($similar_items as $key => $item) {

                                if (substr_count(strtolower($customer_name), strtolower($item['customer'])) > 0) {

                                    $parsed_attributes_column_features_unserialize_val = '';
                                    $parsed_model_unserialize_val = '';
                                    $parsed_review_count_unserialize_val_count = '';
                                    $cmpare = $this->statistics_new_model->get_compare_item($item['imported_data_id']);

                                    $parsed_attributes_unserialize = unserialize($cmpare->parsed_attributes);

                                    if (isset($parsed_attributes_unserialize['feature_count']))
                                        $parsed_attributes_column_features_unserialize_val = $parsed_attributes_unserialize['feature_count'];
                                    if (isset($parsed_attributes_unserialize['model']))
                                        $parsed_model_unserialize_val = $parsed_attributes_unserialize['model'];
                                    if (isset($parsed_attributes_unserialize['review_count']))
                                        $parsed_review_count_unserialize_val_count = $parsed_attributes_unserialize['review_count'];

                                    $parsed_meta_unserialize = unserialize($cmpare->parsed_meta);

                                    $cmpare->model = $parsed_model_unserialize_val;
                                    $cmpare->column_features = $parsed_attributes_column_features_unserialize_val;
                                    $cmpare->review_count = $parsed_review_count_unserialize_val_count;

                                    $similar_items_data[] = $cmpare;
                                    $val->similar_items = $similar_items_data;
                                }
                            }
                            $cmp[] = $val;
                        }
                    }
                }
                $results = $cmp;
            }
            
            /*             * **Foreach Begin*** */
            $snap_data = array();
            foreach ($results as $data_row) {
                $sim_item_data = $data_row->similar_items;
                $output = array();
                if ($data_row->snap != '') {
                    $file = realpath(BASEPATH . "../webroot/webshoots") . '/' . $data_row->snap;
                    if (file_exists($file)) {
                        if (filesize($file) > 1024) {
                            $snap = "<img src='" . base_url() . "webshoots/" . $data_row->snap . "' />";
                            $output['snap'] = $snap;
                            $output['product_name'] = $data_row->product_name;
                            $output['url'] = $data_row->url;
                        }
                    }
                }
                if ($batch_compare_id != -1 && $sim_item_data[0]->snap != '') {
                    $file1 = realpath(BASEPATH . "../webroot/webshoots") . '/' . $sim_item_data[0]->snap;
                    if (file_exists($file1)) {
                        if (filesize($file1) > 1024) {
                            $snap1 = "<img src='" . base_url() . "webshoots/" . $sim_item_data[0]->snap . "' />";
                            $output['snap1'] = $snap1;
                            $output['product_name1'] = $sim_item_data[0]->product_name;
                            $output['url1'] = $sim_item_data[0]->url;
                        }
                    }
                }
                if(!(empty($output)))
                    $snap_data[] = $output;
            }
//            var_dump($snap_data); exit();
            /*             * **Foreach End*** */
            $this->output->set_content_type('application/json')->set_output(json_encode($snap_data));
        }
    }

    public function save_statistic_data() {
        $this->load->model('settings_model');
        $this->load->model('statistics_model');
        $this->load->model('statistics_new_model');
        if ($this->settings['statistics_table'] == "statistics_new") {
            $results = $this->statistics_new_model->updateStatsData($_POST);
        } else {
            $results = $this->statistics_model->updateStatsData($_POST);
        }
        return $results;
    }

    public function get_graph_batch_data() {

        if (isset($_POST['batch_id']) && isset($_POST['batch_compare_id']) && isset($_POST['graphBuild'])) {
            if (trim($_POST['batch_id']) == '')
                $batch_id = -1;
            else
                $batch_id = $_POST['batch_id'];
            if (trim($_POST['graphBuild']) == '')
                $graphBuild = -1;
            else
                $graphBuild = $_POST['graphBuild'];
            if (trim($_POST['batch_compare_id']) == '' || $_POST['batch_compare_id'] == 'all')
                $batch_compare_id = -1;
            else {
                $batch_compare_id = $_POST['batch_compare_id'];
                $this->load->model('batches_model');
                $customer_name = $this->batches_model->getCustomerUrlByBatch($batch_compare_id);
            }

            $batch_arr = array($batch_id, $batch_compare_id);
            $snap_data = array();
            $min_max = array();

            $params = new stdClass();
            $params->batch_id = $batch_id;
            $params->txt_filter = '';
            $params->date_from = '';
            $params->date_to = '';
            $results = $this->get_data_for_assess($params);


            if ($batch_compare_id != -1) {
                foreach ($results as $val) {
                    $similar_items_data = array();
                    if (substr_count(strtolower($val->similar_products_competitors), strtolower($customer_name)) > 0) {
                        $similar_items = unserialize($val->similar_products_competitors);
                        if (count($similar_items) > 1) {
                            foreach ($similar_items as $key => $item) {

                                if (substr_count(strtolower($customer_name), strtolower($item['customer'])) > 0) {

                                    $parsed_attributes_column_features_unserialize_val = '';
                                    $parsed_model_unserialize_val = '';
                                    $parsed_review_count_unserialize_val_count = '';
                                    $cmpare = $this->statistics_new_model->get_compare_item($item['imported_data_id']);

                                    $parsed_attributes_unserialize = unserialize($cmpare->parsed_attributes);

                                    if (isset($parsed_attributes_unserialize['feature_count']))
                                        $parsed_attributes_column_features_unserialize_val = $parsed_attributes_unserialize['feature_count'];
                                    if (isset($parsed_attributes_unserialize['model']))
                                        $parsed_model_unserialize_val = $parsed_attributes_unserialize['model'];
                                    if (isset($parsed_attributes_unserialize['review_count']))
                                        $parsed_review_count_unserialize_val_count = $parsed_attributes_unserialize['review_count'];

                                    $parsed_meta_unserialize = unserialize($cmpare->parsed_meta);

                                    $cmpare->model = $parsed_model_unserialize_val;
                                    $cmpare->column_features = $parsed_attributes_column_features_unserialize_val;
                                    $cmpare->review_count = $parsed_review_count_unserialize_val_count;

                                    $similar_items_data[] = $cmpare;
                                    $val->similar_items = $similar_items_data;
                                }
                            }
                            $cmp[] = $val;
                        }
                    }
                }
                $results = $cmp;
            }

            foreach ($results as $data_row) {
                $parsed_attributes_feature = unserialize($data_row->parsed_attributes);
                $snap_data[0]['product_name'][] = (string) $data_row->product_name;
                $snap_data[0]['url'][] = (string) $data_row->url;
                $snap_data[0]['short_description_wc'][] = (int) $data_row->short_description_wc;
                $snap_data[0]['long_description_wc'][] = (int) $data_row->long_description_wc;
                $snap_data[0]['total_description_wc'][] = (int) $data_row->short_description_wc + (int) $data_row->long_description_wc;
                $snap_data[0]['Date'][] = (string) $data_row->Date;
                 if ($parsed_attributes_feature['review_count']) {
                    $snap_data[0]['revision'][] = (int) $parsed_attributes_feature['review_count'];
                } else {
                    $snap_data[0]['revision'][] = 0;
                }
                if ($parsed_attributes_feature['feature_count']) {
                    $snap_data[0]['Features'][] = (int) $parsed_attributes_feature['feature_count'];
                } else {
                    $snap_data[0]['Features'][] = 0;
                }
                $arr = $this->get_min_max($data_row->imported_data_id,$graphBuild); 
                $updated_short_description_wc = '';
                $updated_long_description_wc = '';
                $updated_total_description_wc = '';
                $updated_revision = '';
                $updated_Features = '';
                $updated_h1_word_counts = '';
                $updated_h2_word_counts = '';
                if($graphBuild == "total_description_wc"){
                foreach($arr as $a){
                        if($a->date !=''){
                          $long_des = count(explode(' ',$a->long_description));
                          $des = count(explode(' ',$a->description));
                          if($des == 1 && $long_des == 1)
                            $updated_total_description_wc.='Total Description Word Count: '.$a->date .' - null  words<br>';  
                          else
                            $updated_total_description_wc.='Total Description Word Count: '.$a->date .' - '.(count(explode(' ',$a->long_description)) + count(explode(' ',$a->description)))."  words<br>";  
                        }
       
                    }
                 }else{
                    foreach($arr as $a){
                    $pars = unserialize($a->parsed_attributes);
                    $htags_upd = unserialize($a->HTags);
                    $updated_short_description_wc.='Short Description: '.$a->date .' - '.count(explode(' ',$a->description))."  words<br>";
                    $updated_long_description_wc.='Long Description: '.$a->date .' - '.count(explode(' ',$a->long_description))." words <br>";
                    $updated_total_description_wc.='Total Description Word Count: '.$a->date .' - '.(count(explode(' ',$a->long_description)) + count(explode(' ',$a->description)))."  words<br>";
                    $updated_revision.='Reviews: '.$a->date .' - '.$pars['review_count']."<br>";
                    $updated_Features.='Features: '.$a->date .' - '.$pars['feature_count']."<br>";
                    $updated_h1_word_counts.='H1 Characters: ' .$a->date .' - '.count($htags_upd['h1'])." words <br>";
                    $updated_h2_word_counts.='H2 Characters: ' .$a->date .' - '.count($htags_upd['h2'])." words <br>";
                }
                 }
                $snap_data[0]['updated_short_description_wc'][] =  $updated_short_description_wc;
                $snap_data[0]['updated_long_description_wc'][] =  $updated_long_description_wc;
                $snap_data[0]['updated_total_description_wc'][] =  $updated_total_description_wc;
                $snap_data[0]['updated_revision'][] =  $updated_revision;
                $snap_data[0]['updated_Features'][] =  $updated_Features;
                $snap_data[0]['updated_h1_word_counts'][] =  $updated_h1_word_counts;
                $snap_data[0]['updated_h2_word_counts'][] =  $updated_h2_word_counts;
//                $snap_data[0]['own_price'][] = (float) $data_row->own_price;
                
                $htags = unserialize($data_row->htags);
                if ($htags) {
                    if (isset($htags['h1'])) {
                        $snap_data[0]['h1_word_counts'][] = count($htags['h1']);
                    } else {
                        $snap_data[0]['h1_word_counts'][] = 0;
                    }
                    if (isset($htags['h2'])) {
                        $snap_data[0]['h2_word_counts'][] = count($htags['h2']);
                    } else {
                        $snap_data[0]['h2_word_counts'][] = 0;
                    }
                } else {
                    $snap_data[0]['h1_word_counts'][] = 0;
                    $snap_data[0]['h2_word_counts'][] = 0;
                }

                if (isset($data_row->similar_items)) {

                    $data_row_sim = $data_row->similar_items;

                    $snap_data[1]['product_name'][] = (string) $data_row_sim[0]->product_name;
                    $snap_data[1]['url'][] = (string) $data_row_sim[0]->url;
                    $snap_data[1]['short_description_wc'][] = (int) $data_row_sim[0]->short_description_wc;
                    $snap_data[1]['long_description_wc'][] = (int) $data_row_sim[0]->long_description_wc;
                    $snap_data[1]['total_description_wc'][] = (int) $data_row_sim[0]->short_description_wc + (int) $data_row_sim[0]->long_description_wc;
                    $snap_data[1]['revision'][] = (int) $data_row_sim[0]->review_count;
                    $snap_data[1]['Features'][] = (int) $data_row_sim[0]->column_features;
                    $snap_data[1]['Date'][] = (string) $data_row_sim[0]->Date;
                    
                $arr1 = $this->get_min_max($data_row_sim[0]->imported_data_id,$graphBuild);
                $updated_short_description_wc1 = '';
                $updated_long_description_wc1 = '';
                $updated_total_description_wc1 = '';
                $updated_revision1 = '';
                $updated_Features1 = '';
                $updated_h1_word_counts1 = '';
                $updated_h2_word_counts1 = '';
                 if($graphBuild == "total_description_wc"){
                    foreach($arr1 as $a1){
                      if($a1->date !=''){
                          $long_des1 = count(explode(' ',$a1->long_description));
                          $des1 = count(explode(' ',$a1->description));
                          if($des1 == 1 && $long_des1 == 1)
                            $updated_total_description_wc1.='Total Description Word Count: '.$a1->date .' - null  words<br>';  
                          else    
                            $updated_total_description_wc1.='Total Description Word Count: '.$a1->date .' - '.($long_des1 + $des1)."  words<br>";  
                      }
                    
                    }
                 }else{
                    foreach($arr1 as $a1){
                    $pars1 = unserialize($a1->parsed_attributes);
                    $htags_upd1 = unserialize($a1->HTags);
                    $updated_short_description_wc1.='Short Description: '.$a1->date .' - '.count(explode(' ',$a1->description))."  words<br>";
                    $updated_long_description_wc1.='Long Description: '.$a1->date .' - '.count(explode(' ',$a1->long_description))." words <br>";
                    $updated_total_description_wc1.='Total Description Word Count: '.$a1->date .' - '.(count(explode(' ',$a1->long_description)) + count(explode(' ',$a1->description)))."  words<br>";
                    $updated_revision1.='Reviews: '.$a1->date .' - '.$pars1['review_count']."<br>";
                    $updated_Features1.='Features: '.$a1->date .' - '.$pars1['feature_count']."<br>";
                    $updated_h1_word_counts1.='H1 Characters: ' .$a1->date .' - '.count($htags_upd1['h1'])." words <br>";
                    $updated_h2_word_counts1.='H2 Characters: ' .$a1->date .' - '.count($htags_upd1['h2'])." words <br>";
                    }
                 }   
                $snap_data[1]['updated_short_description_wc'][] =  $updated_short_description_wc1;
                $snap_data[1]['updated_long_description_wc'][] =  $updated_long_description_wc1;
                $snap_data[1]['updated_total_description_wc'][] =  $updated_total_description_wc1;
                $snap_data[1]['updated_revision'][] =  $updated_revision1;
                $snap_data[1]['updated_Features'][] =  $updated_Features1;
                $snap_data[1]['updated_h1_word_counts'][] =  $updated_h1_word_counts1;
                $snap_data[1]['updated_h2_word_counts'][] =  $updated_h2_word_counts1;  
//                      $snap_data[1]['own_price'][] = (float) $data_row_sim[0]->own_price;
                    $htags = unserialize($data_row_sim[0]->HTags);
                    if ($htags) {
                        if (isset($htags['h1'])) {
                            $snap_data[1]['h1_word_counts'][] = count($htags['h1']);
                        } else {
                            $snap_data[1]['h1_word_counts'][] = 0;
                        }
                        if (isset($htags['h2'])) {
                            $snap_data[1]['h2_word_counts'][] = count($htags['h2']);
                        } else {
                            $snap_data[1]['h2_word_counts'][] = 0;
                        }
                    } else {
                        $snap_data[1]['h1_word_counts'][] = 0;
                        $snap_data[1]['h2_word_counts'][] = 0;
                    }
                }
            }
//            echo '<pre>';
//            print_r($snap_data); die();
            $this->output->set_content_type('application/json')->set_output(json_encode($snap_data));
        }
    }

    private function keywords_appearence($desc, $phrase) {

        $desc = strip_tags($desc);
        return substr_count($desc, $phrase);
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

    private function costom_keywords_den($imported_data_id, $description, $description_wc) {
        $custom_seo = $this->keywords_model->get_by_imp_id($imported_data_id);
        $key_den = 0;
        if ($custom_seo['primary']) {
            if ($description) {
                $_count = $this->keywords_appearence($description, $custom_seo['primary']);
                $cnt = count(explode(' ', $custom_seo['primary']));
                $key_den = round(($_count * $cnt / $description_wc) * 100, 2);
            }
        };
        if ($custom_seo['secondary']) {
            if ($description) {
                $_count = $this->keywords_appearence($description, $custom_seo['secondary']);
                $cnt = count(explode(' ', $custom_seo['secondary']));
                $key_den = round(($_count * $cnt / $description_wc) * 100, 2);
            }
        };
        if ($custom_seo['tertiary']) {
            if ($description) {
                $_count = $this->keywords_appearence($description, $custom_seo['tertiary']);
                $cnt = count(explode(' ', $custom_seo['tertiary']));
                $key_den = round(($_count * $cnt / $description_wc) * 100, 2);
            }
        };

        return $key_den;
    }

    private function custom_keywords($imported_data_id, $long_description, $long_description_wc, $short_description, $short_description_wc) {

        $custom_seo = $this->keywords_model->get_by_imp_id($imported_data_id);
        $Custom_Keywords_Long_Description = '';
        if ($custom_seo['primary']) {
            if ($long_description) {
                $_count = $this->keywords_appearence($long_description, $custom_seo['primary']);
                $cnt = count(explode(' ', $custom_seo['primary']));
                $_count = round(($_count * $cnt / $long_description_wc) * 100, 2) . "%";
                $Custom_Keywords_Long_Description .= $custom_seo['primary'] . "</td><td>$_count  \r\n";
            } else {
                $_count = ' ';
            }
        };
        if ($custom_seo['secondary']) {
            if ($long_description) {
                $_count = $this->keywords_appearence($long_description, $custom_seo['secondary']);
                $cnt = count(explode(' ', $custom_seo['secondary']));
                $_count = round(($_count * $cnt / $long_description_wc) * 100, 2) . "%";
                $Custom_Keywords_Long_Description .= $custom_seo['secondary'] . " - $_count  \r\n";
            } else {
                $_count = ' ';
            }
        };
        if ($custom_seo['tertiary']) {
            if ($long_description) {
                $_count = $this->keywords_appearence($long_description, $custom_seo['tertiary']);
                $cnt = count(explode(' ', $custom_seo['tertiary']));
                $_count = round(($_count * $cnt / $long_description_wc) * 100, 2) . "%";
                $Custom_Keywords_Long_Description .= $custom_seo['tertiary'] . " - $_count  \r\n";
            } else {
                $_count = ' ';
            }
        };


        $Custom_Keywords_Short_Description = "";

        if ($custom_seo['primary']) {
            if ($short_description) {
                $_count = $this->keywords_appearence($short_description, $custom_seo['primary']);
                $cnt = count(explode(' ', $custom_seo['primary']));
                $_count = round(($_count * $cnt / $short_description_wc) * 100, 2) . "%";
                $Custom_Keywords_Short_Description .= $custom_seo['primary'] . " - $_count  \r\n";
            } else {
                $_count = ' ';
            }
        };
        if ($custom_seo['secondary']) {
            if ($short_description) {
                $_count = $this->keywords_appearence($short_description, $custom_seo['secondary']);
                $cnt = count(explode(' ', $custom_seo['secondary']));
                $_count = round(($_count * $cnt / $short_description_wc) * 100, 2) . "%";
                $Custom_Keywords_Short_Description .= $custom_seo['secondary'] . " - $_count  \r\n";
            } else {
                $_count = ' ';
            }
        };
        if ($custom_seo['tertiary']) {
            if ($short_description) {
                $_count = $this->keywords_appearence($short_description, $custom_seo['tertiary']);
                $cnt = count(explode(' ', $custom_seo['tertiary']));
                $_count = round(($_count * $cnt / $short_description_wc) * 100, 2) . "%";
                $Custom_Keywords_Short_Description .= "<tr><td>" . $custom_seo['tertiary'] . " - $_count  \r\n";
            } else {
                $_count = ' ';
            }
        };

        return array("Custom_Keywords_Long" => $Custom_Keywords_Long_Description, "Custom_Keywords_Short" => $Custom_Keywords_Short_Description);
    }

    public function remember_batches() {
        session_start();
        if (isset($_POST['batch_id'])) {
            $_SESSION['batch_id'] = $_POST['batch_id'];
        }
        if (isset($_POST['compare_batch_id'])) {
            $_SESSION['compare_batch_id'] = $_POST['compare_batch_id'];
        }
    }

    public function getbatchvalues() {
        session_start();
        $batches = array(
            'batch_id' => $_SESSION['batch_id'],
            'compare_batch_id' => $_SESSION['compare_batch_id']
        );

        $this->output->set_content_type('application/json')->set_output(json_encode($batches));
    }
	
	public function get_summary_filters()
	{
		$this->load->model('user_summary_settings', 'uss');
		$user_setting = null;
		
		if ($this->ion_auth->logged_in() && ($user_id = $this->ion_auth->get_user_id()))		
			$user_setting = $this->uss->findByAttributes(array('user_id' => $user_id, 'setting_id' => User_summary_settings::USER_SUMMARY_SETTING_FILTER));			
		else
			$user_setting = $this->uss->findByAttributes(array('user_ip' => $_SERVER['REMOTE_ADDR'], 'setting_id' => User_summary_settings::USER_SUMMARY_SETTING_FILTER));
				
		die(json_encode($user_setting));
	}
	
	public function save_summary_filters()
	{				
		$this->load->model('user_summary_settings', 'uss');					
		$this->uss->user_id = null;
		
		if ($this->ion_auth->logged_in() && ($this->uss->user_id = $this->ion_auth->get_user_id()))		
			$user_setting = $this->uss->findByAttributes(array('user_id' => $this->uss->user_id, 'setting_id' => User_summary_settings::USER_SUMMARY_SETTING_FILTER));								
		else
			$user_setting = $this->uss->findByAttributes(array('user_ip' => $_SERVER['REMOTE_ADDR'], 'setting_id' => User_summary_settings::USER_SUMMARY_SETTING_FILTER));
		
		if ($user_setting)
			$this->uss->setAttributes((array)$user_setting);
		
		$this->uss->setting_id = User_summary_settings::USER_SUMMARY_SETTING_FILTER;
		$this->uss->setting_value = json_encode($this->input->post('summary_active_items'));
		
		die(json_encode($this->uss->save()));
	}
	
	public function save_summary_filters_order()
	{
		$this->load->model('user_summary_settings', 'uss');					
		$this->uss->user_id = null;
		
		if ($this->ion_auth->logged_in() && ($this->uss->user_id = $this->ion_auth->get_user_id()))		
			$user_setting = $this->uss->findByAttributes(array('user_id' => $this->uss->user_id, 'setting_id' => User_summary_settings::USER_SUMMARY_SETTING_FILTER_ORDER));								
		else
			$user_setting = $this->uss->findByAttributes(array('user_ip' => $_SERVER['REMOTE_ADDR'], 'setting_id' => User_summary_settings::USER_SUMMARY_SETTING_FILTER_ORDER));
		
		if ($user_setting)
			$this->uss->setAttributes((array)$user_setting);
		
		$this->uss->setting_id = User_summary_settings::USER_SUMMARY_SETTING_FILTER_ORDER;
		$this->uss->setting_value = json_encode($this->input->post('summary_items_order'));
		
		die(json_encode($this->uss->save()));
	}
        
        public function deleteSecondaryMatch(){
            if(isset($_POST['impdataid'])){
                $data = array(
                                'similar_products_competitors' => null,
                             );
                $this->load->model('statistics_new_model');
                $this->db->where('imported_data_id', $_POST['impdataid']);
                $this->db->update('statistics_new', $data); 
                return true;
}
            return false;
        }
}
