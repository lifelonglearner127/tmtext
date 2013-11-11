<?php

if (!defined('BASEPATH'))
    exit('No direct script access allowed');

class Assess extends MY_Controller {

    function __construct() {
        parent::__construct();

        $this->load->library('form_validation');
        $this->load->library('helpers');
        $this->data['title'] = 'Assess';

        if (!$this->ion_auth->logged_in()) {
            //redirect them to the login page
            redirect('auth/login', 'refresh');
        }
    }

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

    public function compare() {
        $arr = array();
        for ($i = 1; $i < 3; $i++) {

            $arr[] = array("sTitle" => "Snapshot", "sName" => 'snap' . $i);
        }

        echo json_encode($arr);
        exit;
//        $batch1 = $this->input->post('batch1');
//        $batch2 = $this->input->post('batch2');
//        $this->load->model('batches_model');
//        $customer_name = $this->batches_model->getCustomerUrlByBatch($batch2);
//        $this->load->model('statistics_new_model');
//        $data =  $this->statistics_new_model->get_for_compare($batch1);
//        $cmp= array();
//        foreach($data as $val){
//    
//            if(substr_count($val->similar_products_competitors, $customer_name)>0){
//                $similar_items= unserialize($val->similar_products_competitors);
//                
//                foreach($similar_items as $key => $item){
//                    if(substr_count($customer_name,$item['customer'])>0){
//                        $cmpare = $this->statistics_new_model->get_compare_item($similar_items[$key]['imported_data_id']);
//                        $val->snap1= $cmpare->snap;
//                        $val->product_name1= $cmpare->product_name;
//                        $val->url1= $cmpare->url;
//                        $val->short_description_wc1= $cmpare->short_description_wc;
//                        $val->long_description_wc1= $cmpare->long_description_wc;
//                    }
//                }
//                $cmp[]=$val;
//            }
//        }
//        $data['results']=$cmp;
////        echo "<pre>";
////        print_r($cmp);
////        echo "</pre>";
//        $this->load->view('assess/compare', $data);
    }

    public function get_assess_info() {
        $txt_filter = '';
        if ($this->input->get('search_text') != '') {
            $txt_filter = $this->input->get('search_text');
        }
        if ($this->input->get('sSearch') != '') {
            $txt_filter = $this->input->get('sSearch');
        }
        $batch_id = $this->input->get('batch_id');


        $compare_batch_id = $this->input->get('compare_batch_id');

        if ($batch_id == 0) {
            $output = array(
                "sEcho" => 1,
                "iTotalRecords" => 0,
                "iTotalDisplayRecords" => 0,
                "iDisplayLength" => 10,
                "aaData" => array()
            );

            $this->output->set_content_type('application/json')
                    ->set_output(json_encode($output));
        } else {
            $build_assess_params = new stdClass();
            $build_assess_params->date_from = $this->input->get('date_from') == 'undefined' ? '' : $this->input->get('date_from');
            $build_assess_params->date_to = $this->input->get('date_to') == 'undefined' ? '' : $this->input->get('date_to');
            $build_assess_params->price_diff = $this->input->get('price_diff') == 'undefined' ? -1 : $this->input->get('price_diff');
            $build_assess_params->max_similar_item_count = 0;
            $build_assess_params->short_less_check = $this->input->get('short_less_check') == 'true' ? true : false;
            if ($this->input->get('short_less')) {
                $build_assess_params->short_less = $this->input->get('short_less') == 'undefined' ? -1 : intval($this->input->get('short_less'));
            } else {
                $build_assess_params->short_less = 20;
            }
            $build_assess_params->short_more_check = $this->input->get('short_more_check') == 'true' ? true : false;
            if ($this->input->get('short_more')) {
                $build_assess_params->short_more = $this->input->get('short_more') == 'undefined' ? -1 : intval($this->input->get('short_more'));
            } else {
                $build_assess_params->short_more = 0;
            }

            $build_assess_params->short_seo_phrases = $this->input->get('short_seo_phrases');
            $build_assess_params->short_duplicate_content = $this->input->get('short_duplicate_content');

            $build_assess_params->long_less_check = $this->input->get('long_less_check') == 'true' ? true : false;
            if ($this->input->get('long_less')) {
                $build_assess_params->long_less = $this->input->get('long_less') == 'undefined' ? -1 : intval($this->input->get('long_less'));
            } else {
                $build_assess_params->long_less = 50;
            }
            $build_assess_params->long_more_check = $this->input->get('long_more_check') == 'true' ? true : false;
            if ($this->input->get('long_more')) {
                $build_assess_params->long_more = $this->input->get('long_more') == 'undefined' ? -1 : intval($this->input->get('long_more'));
            } else {
                $build_assess_params->long_more = 0;
            }

            $build_assess_params->long_seo_phrases = $this->input->get('long_seo_phrases');
            $build_assess_params->long_duplicate_content = $this->input->get('long_duplicate_content');
            $build_assess_params->all_columns = $this->input->get('sColumns');
            $build_assess_params->sort_columns = $this->input->get('iSortCol_0');
            $build_assess_params->sort_dir = $this->input->get('sSortDir_0');
            $build_assess_params->flagged = $this->input->get('flagged') == 'true' ? true : $this->input->get('flagged');
            if (intval($compare_batch_id) > 0) {
                $build_assess_params->compare_batch_id = intval($compare_batch_id);
            }
            
            $params = new stdClass();
            $params->batch_id = $batch_id;
            $params->txt_filter = $txt_filter;
            $params->date_from = $build_assess_params->date_from;
            $params->date_to = $build_assess_params->date_to;
            $batch2 = $this->input->get('batch2')&&$this->input->get('batch2') == 'undefined' ? '' : $this->input->get('batch2');
            if($batch2===''){
                $params->iDisplayLength = $this->input->get('iDisplayLength');
                $params->iDisplayStart = $this->input->get('iDisplayStart');
            }
            
            $results = $this->get_data_for_assess($params);
            $cmp = array();
                               
            if ($batch2 != '' && $batch2 != 0 && $batch2 != 'all') {
                $this->load->model('batches_model');
                $build_assess_params->max_similar_item_count =1;

                $customer_name = $this->batches_model->getCustomerUrlByBatch($batch2);

                foreach ($results as $val) {
                    $similar_items_data = array();
                    if (substr_count(strtolower($val->similar_products_competitors), strtolower($customer_name)) > 0) {

                        $similar_items = unserialize($val->similar_products_competitors);
                       
                        if(count($similar_items)>1){
                        foreach ($similar_items as $key => $item) {
                            if (substr_count(strtolower($customer_name), strtolower($item['customer'])) > 0) {
                               $parsed_attributes_unserialize_val ='';                                                           
                               $parsed_meta_unserialize_val = ''; 
                               $parsed_meta_unserialize_val_c = '';
                               $cmpare = $this->statistics_new_model->get_compare_item($item['imported_data_id']);
                               
                               $parsed_attributes_unserialize = unserialize($cmpare->parsed_attributes);
                               if($parsed_attributes_unserialize['item_id'])
                                  $parsed_attributes_unserialize_val = $parsed_attributes_unserialize['item_id'];
                               if($parsed_attributes_unserialize['model'])
                                  $parsed_attributes_unserialize_val = $parsed_attributes_unserialize['model'];

                                $parsed_meta_unserialize = unserialize($cmpare->parsed_meta);
                               if($parsed_meta_unserialize['description']){
                                $parsed_meta_unserialize_val = $parsed_meta_unserialize['description'];
                                $parsed_meta_unserialize_val_c = count(explode(" ",$parsed_meta_unserialize_val));
                                if($parsed_meta_unserialize_val_c !=1)
                                    $parsed_meta_unserialize_val_count = $parsed_meta_unserialize_val_c;
                               } 
                               else if($parsed_meta_unserialize['Description']){
                                $parsed_meta_unserialize_val = $parsed_meta_unserialize['Description'];
                                $parsed_meta_unserialize_val_c = count(explode(" ",$parsed_meta_unserialize_val));
                                if($parsed_meta_unserialize_val_c !=1)
                                    $parsed_meta_unserialize_val_count = $parsed_meta_unserialize_val_c;
                               }
                               $val->snap1 = $cmpare->snap;
                               $val->product_name1 = $cmpare->product_name;
                               $val->item_id1 = $parsed_attributes_unserialize_val;
                               $val->model1 = '#';
                               $val->url1 = $cmpare->url;
                               $val->short_description_wc1 = $cmpare->short_description_wc;
                               $val->long_description_wc1 = $cmpare->long_description_wc;
                               $val->Meta_Description1 = $parsed_meta_unserialize_val;
                               $val->Meta_Description_Count1 = $parsed_meta_unserialize_val_count;
                               $similar_items_data[]=$cmpare;
                               $val->similar_items =  $similar_items_data; 
                                
                                
                            }
                        }
                        
                        
                        $cmp[] = $val;
                        }
                    }
                }
                $results = $cmp;

            }

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
                 
         $output = $this->build_asses_table($results, $build_assess_params, $batch_id);
         
         $this->output->set_content_type('application/json')
         ->set_output(json_encode($output));
        }
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

    private function get_data_for_assess($params) {
        $this->load->model('settings_model');
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

        $pdf->SetHTMLFooter('<span style="font-size: 8px;">Copyright © 2013 Content Solutions, Inc.</span>');

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
        $batch_id = (int) trim($_GET['batch_id']);
        $cmp_selected = trim(strtolower($_GET['cmp_selected']));
        
        if (($cmp_selected=='all') || ($cmp_selected >0)) {

            $query = $this->db->query('select `s`.*,
            (select `value` from imported_data_parsed where `key`="Product Name" and `imported_data_id` = `s`.`imported_data_id` limit 1) as `product_name`,
            (select `value` from imported_data_parsed where `key`="Description" and `imported_data_id` = `s`.`imported_data_id` limit 1) as `short_description`,
            (select `value` from imported_data_parsed where `key`="Long_Description" and `imported_data_id` = `s`.`imported_data_id` limit 1) as `long_description`,
            (select `value` from imported_data_parsed where `key`="Url" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `url`
            from `statistics_new` as `s`  where `s`.`batch_id`=' . $batch_id);
            $results = $query->result();
            $this->load->model('batches_model');

            if ($cmp_selected != 'all' && $cmp_selected != null && $cmp_selected != 0) {


                $max_similar_item_count = 1;

                $customer_name = $this->batches_model->getCustomerUrlByBatch($cmp_selected);

                foreach ($results as $val) {
                    $similar_items_data = array();
                    if (substr_count(strtolower($val->similar_products_competitors), strtolower($customer_name)) > 0) {

                        $similar_items = unserialize($val->similar_products_competitors);

                        if (count($similar_items) > 1) {
                            foreach ($similar_items as $key => $item) {
                                if (substr_count(strtolower($customer_name), strtolower($item['customer'])) > 0) {


                                    $cmpare = $this->statistics_new_model->get_compare_item($item['imported_data_id']);
                                    $val->snap1 = $cmpare->snap;
                                    $val->product_name1 = $cmpare->product_name;
                                    $val->url1 = $cmpare->url;
                                    $val->short_description_wc1 = $cmpare->short_description_wc;
                                    $val->long_description_wc1 = $cmpare->long_description_wc;
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
                    }else{
                        unset($results[$key1]);
                    }
                }
            }
            
            

            $res_array = array();
            $line = array('Product Name' => 'Product Name', 'Url' => 'Url', 'Word Count (S)' => 'Word Count (S)', 'Word Count (L)' => 'Word Count (L)', 'SEO Phrases (S)' => 'SEO Phrases (S)', 'SEO Phrases (L)' => 'SEO Phrases (L)', 'Price' => 'Price');
            foreach ($results as $key => $row) {
                $res_array[$key]['Product Name'] = $row->product_name;
                $res_array[$key]['Url'] = $row->url;
                $res_array[$key]['Word Count (S)'] = $row->short_description_wc;
                $res_array[$key]['Word Count (L)'] = $row->long_description_wc;
                $res_array[$key]['SEO Phrases (S)'] = $row->short_seo_phrases;
                $res_array[$key]['SEO Phrases (L)'] = $row->long_seo_phrases;
                $res_array[$key]['Price'] = $row->price_diff;



                if (trim($res_array[$key]['SEO Phrases (S)']) != 'None') {
                    $shortArr = unserialize($res_array[$key]['SEO Phrases (S)']);

                    if ($shortArr) {
                        $shortString = '';
                        foreach ($shortArr as $value) {
                            $shortString .= $value['ph'] . "\r\n";
                        }
                        $res_array[$key]['SEO Phrases (S)'] = trim($shortString);
                    }
                }
                if (trim($res_array[$key]['SEO Phrases (L)']) != 'None') {

                    $longArr = unserialize($res_array[$key]['SEO Phrases (L)']);

                    if ($longArr) {
                        $longString = '';
                        foreach ($longArr as $value) {
                            $longString .= $value['ph'] . "\r\n";
                        }
                        $res_array[$key]['SEO Phrases (L)'] = trim($longString);
                    }
                }


                $price_diff = unserialize($res_array[$key]['Price']);
                if ($price_diff) {
                    $own_price = floatval($price_diff['own_price']);
                    $own_site = str_replace('www.', '', $price_diff['own_site']);
                    $own_site = str_replace('www1.', '', $own_site);
                    $price_diff_res = $own_site . " - $" . $price_diff['own_price'];
                    $flag_competitor = false;
                    for ($i = 0; $i < count($price_diff['competitor_customer']); $i++) {
                        if ($customer_url["host"] != $price_diff['competitor_customer'][$i]) {
                            if ($own_price > floatval($price_diff['competitor_price'][$i])) {
                                $competitor_site = str_replace('www.', '', $price_diff['competitor_customer'][$i]);
                                $competitor_site = str_replace('www.', '', $competitor_site);
                                $price_diff_res .= "\r\n" . $competitor_site . " - $" . $price_diff['competitor_price'][$i];
                            }
                        }
                    }
                    $res_array[$key]['Price'] = $price_diff_res;
                } else {
                    $res_array[$key]['Price'] = '';
                }
           

            if ($max_similar_item_count > 0) {
                $sim_items = $row->similar_items;

                for ($i = 1; $i <= $max_similar_item_count; $i++) {
                    $res_array[$key]['Product Name (' . $i . ")"] = $sim_items[$i - 1]->product_name ? $sim_items[$i - 1]->product_name : '';
                    $res_array[$key]['Url (' . $i . ")"] = $sim_items[$i - 1]->url ? $sim_items[$i - 1]->url : '';
                    $res_array[$key]['Word Count (S) (' . $i . ")"] = $sim_items[$i - 1]->short_description_wc ? $sim_items[$i - 1]->short_description_wc : '';
                    $res_array[$key]['Word Count (L) (' . $i . ")"] = $sim_items[$i - 1]->long_description_wc ? $sim_items[$i - 1]->long_description_wc : '';
                }
            }

 }
            for ($i = 1; $i <= $max_similar_item_count; $i++) {
                $line[] = 'Product Name (' . $i . ")";
                $line[] = 'Url (' . $i . ")";
                $line[] = 'Word Count (S) (' . $i . ")";
                $line[] = 'Word Count (L) (' . $i . ")";
            }
        } else {
            
            $this->load->model('batches_model');
            //$batch_id = $this->input->get('batch');
            $customer_name = $this->batches_model->getCustomerById($batch_id);
            if (empty($batch_id) || $batch_id == 0){
                $batch_id = '';
                $qnd= '';
            }else{
                $qnd= " WHERE `s`.`batch_id` = $batch_id";
            }
            $this->load->database();
            $query = $this->db->query('
            SELECT 
                `s`.`created` AS `Date`, 
                (SELECT `value` FROM imported_data_parsed WHERE `key`="Product Name" AND `imported_data_id` = `s`.`imported_data_id` LIMIT 1) AS `Product Name`, 
                (SELECT `value` FROM imported_data_parsed WHERE `key`="Url" AND `imported_data_id` = `s`.`imported_data_id` LIMIT 1) AS `URL`, 
                `s`.`short_description_wc` AS `Word Count (S)`, 
                `s`.`short_seo_phrases` AS `SEO Phrases (S)`, 
                `s`.`long_description_wc` AS `Word Count (L)`, 
                `s`.`long_seo_phrases` AS `SEO Phrases (L)`, 
                "-" as `Duplicate Content`,
                `s`.`price_diff` AS `Price`
            FROM 
                (`statistics_new` AS s) 
            LEFT JOIN 
                `crawler_list` AS cl ON `cl`.`imported_data_id` = `s`.`imported_data_id`
            '.$qnd
            );
            $line = array();
            foreach ($query->list_fields() as $name) {
                $line[] = $name;
            }
            $result = $query->result_array();
            foreach ($result as $key => $row) {
                if (trim($row['SEO Phrases (S)']) != 'None') {
                    $shortArr = unserialize($row['SEO Phrases (S)']);
                    if ($shortArr) {
                        $shortString = '';
                        foreach ($shortArr as $value) {
                            $shortString .= $value['ph'] . "\r\n";
                        }
                        $result[$key]['SEO Phrases (S)'] = trim($shortString);
                    }
                }
                if (trim($row['SEO Phrases (L)']) != 'None') {
                    $longArr = unserialize($row['SEO Phrases (L)']);
                    if ($longArr) {
                        $longString = '';
                        foreach ($longArr as $value) {
                            $longString .= $value['ph'] . "\r\n";
                        }
                        $result[$key]['SEO Phrases (L)'] = trim($longString);
                    }
                }
                $price_diff = unserialize($row['Price']);
                if ($price_diff) {
                    $own_price = floatval($price_diff['own_price']);
                    $own_site = str_replace('www.', '', $price_diff['own_site']);
                    $own_site = str_replace('www1.', '', $own_site);
                    $price_diff_res = $own_site . " - $" . $price_diff['own_price'];
                    $flag_competitor = false;
                    for ($i = 0; $i < count($price_diff['competitor_customer']); $i++) {
                        if ($customer_url["host"] != $price_diff['competitor_customer'][$i]) {
                            if ($own_price > floatval($price_diff['competitor_price'][$i])) {
                                $competitor_site = str_replace('www.', '', $price_diff['competitor_customer'][$i]);
                                $competitor_site = str_replace('www.', '', $competitor_site);
                                $price_diff_res .= "\r\n" . $competitor_site . " - $" . $price_diff['competitor_price'][$i];
                            }
                        }
                    }
                    $result[$key]['Price'] = $price_diff_res;
                } else {
                    $result[$key]['Price'] = '';
                }
            }
            array_unshift($result, $line);
            $res_array = $result;
        }
        array_unshift($res_array, $line);
        $this->load->helper('csv');
        array_to_csv($res_array, date("Y-m-d H:i") . '.csv');
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

        // if columns empty set default values for columns
        if (empty($columns)) {
            $columns = array(
                'created' => 'true',
                'product_name' => 'true',
                'item_id' => 'true',
                'model' => 'true',
                'url' => 'true',
                'short_description_wc' => 'true',
                'short_seo_phrases' => 'true',
                'long_description_wc' => 'true',
                'long_seo_phrases' => 'true',
                'duplicate_context' => 'true',
                'Custom_Keywords_Short_Description' => 'true',
                'Custom_Keywords_Long_Description' => 'true',
                'Meta_Description' => 'true',
                'Meta_Description_Count' => 'true',
                'H1_Tags' => 'true',
                'H1_Tags_Count' => 'true',
                'H2_Tags' => 'true',
                'H2_Tags_Count' => 'true',
                'column_external_content' => 'true',
                'column_reviews' => 'true',
                'column_features' => 'true',
                'price_diff' => 'true',
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

        $customers = $this->users_to_customers_model->getByUserId($this->ion_auth->get_user_id());
        if (!$this->ion_auth->is_admin($this->ion_auth->get_user_id())) {
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
    function columns(){
       $columns=array(
            
            array(
                "sTitle" => "Snapshot",
                "sName" => "snap",
                //"sWidth" =>  "10%"
            ),
            array(
                "sTitle" => "Date",
                "sName" => "created",
                //"sWidth" =>"3%"
            ),
            array(
                "sTitle" => "Product Name", 
                "sName" =>"product_name", 
                //"sWidth" => "15%",
                "sClass" => "product_name_text"
            ),
            array(
                "sTitle" => "item ID", 
                "sName" =>"item_id", 
                "sClass" => "item_id"
            ),
           array(
               "sTitle" => "Model",
               "sName" =>"model",
               "sClass" => "model"
           ),
            array(
                "sTitle" => "URL", 
                "sName" => "url", 
                //"sWidth" =>"15%",
                "sClass" =>"url_text"
            ),
            array(
                 "sTitle" => "Short Desc <span class='subtitle_word_short' ># Words</span>",
                "sName" => "short_description_wc", 
               // "sWidth" => "1%",
                "sClass" => "word_short"
            ),
            array(
                 "sTitle" => "Keywords <span class='subtitle_keyword_short'>Short</span>",
                "sName" => "short_seo_phrases", 
                //"sWidth" => "2%",
                "sClass" => "keyword_short"
            ),
            array(
                "sTitle" => "Long Desc <span class='subtitle_word_long' ># Words</span>",
                "sName" =>"long_description_wc", 
                "sWidth" => "1%",
                "sClass" =>"word_long"
            ),
            array(
                 "sTitle" => "Keywords <span class='subtitle_keyword_long'>Long</span>",
                "sName" => "long_seo_phrases", 
                //"sWidth" => "2%",
                "sClass" => "keyword_long"
            ),
              
           array (
            "sTitle" => "Custom Keywords Short Description",
            "sName" => "Custom_Keywords_Short_Description", 
            "sWidth" =>  "4%",
            "sClass" => "Custom_Keywords_Short_Description"
        ),
        array(
            "sTitle" => "Custom Keywords Long Description",
            "sName" => "Custom_Keywords_Long_Description", 
            "sWidth" => "4%",
            "sClass" =>  "Custom_Keywords_Long_Description"
        ),
        array(
            "sTitle" => "Meta Description",
            "sName" => "Meta_Description", 
            "sWidth" => "4%",
            "sClass" =>  "Meta_Description"
        ),
        array(
            "sTitle" => "Prod Desc <span class='subtitle_word_long' ># Words</span>",
            "sName" => "Meta_Description_Count", 
            "sWidth" => "4%",
            "sClass" =>  "Meta_Description_Count"
        ),
              array(
            "sTitle" =>"H1 Tags", 
            "sName" =>"H1_Tags", 
            "sWidth" =>"1%",
            "sClass" =>  "HTags_1"
         ),
              array(
            "sTitle" =>"Words", 
            "sName" =>"H1_Tags_Count", 
            "sWidth" =>"1%",
            "sClass" =>  "HTags"
         ),
              array(
            "sTitle" =>"H2 Tags", 
            "sName" =>"H2_Tags", 
            "sWidth" =>"1%",
            "sClass" =>  "HTags_2"
         ),
              array(
            "sTitle" =>"Words", 
            "sName" =>"H2_Tags_Count", 
            "sWidth" =>"1%",
            "sClass" =>  "HTags"
         ),
        array(
            "sTitle" =>"Duplicate Content", 
            "sName" =>"duplicate_content", 
            //"sWidth" =>"1%"
         ),
         array(
            "sTitle" =>"Content", 
            "sName" =>"column_external_content", 
            //"sWidth" =>"2%"
        ),
         array(
            "sTitle" =>"Reviews", 
            "sName" =>"column_reviews", 
            //"sWidth" =>"3%"
       ),
         array(
            "sTitle" =>"Features", 
            "sName" =>"column_features", 
            //"sWidth" => "4%"
        ),        
         array(
            "sTitle"  =>"Price", 
            "sName" =>"price_diff", 
            //"sWidth" =>"2%",
            "sClass" =>"price_text"
       ),
         array(
            "sTitle"  =>"Recommendations", 
            "sName" =>"recommendations", 
           // "sWidth" =>"15%",
           "bVisible" =>false, 
            "bSortable" =>false
       ),

        array(
            "sName" =>"add_data", 
            "bVisible" => false
        )
        
            
            
        );
        return $columns;         
    }
    private function build_asses_table($results, $build_assess_params, $batch_id = '') {
        
        $columns = $this->columns();
        $duplicate_content_range = 25;
        $this->load->model('batches_model');
        $this->load->model('imported_data_parsed_model');
        $this->load->model('keywords_model');
        $this->load->model('statistics_model');
        $this->load->model('statistics_duplicate_content_model');

        $customer_name = $this->batches_model->getCustomerById($batch_id);
        $customer_url = parse_url($customer_name[0]->url);
        $result_table = array();
        $report = array();
        $pricing_details = array();
        $items_priced_higher_than_competitors = 0;
        $items_have_more_than_20_percent_duplicate_content = 0;
        $items_unoptimized_product_content = 0;
        $short_wc_total_not_0 = 0;
        $long_wc_total_not_0 = 0;
        $items_short_products_content_short = 0;
        $items_long_products_content_short = 0;
        $detail_comparisons_total = 0;
        if ($build_assess_params->max_similar_item_count > 0) {
                
              
            $max_similar_item_count = (int) $build_assess_params->max_similar_item_count;

            for ($i = 1; $i <= $max_similar_item_count; $i++) {

              $columns[] = array("sTitle" => "Snapshot", "sName" => 'snap' . $i);
              $columns[] = array("sTitle" => "Product Name", "sName" => 'product_name' . $i);
              $columns[] = array("sTitle" => "item ID","sClass" => "item_id".$i, "sName" => 'item_id' . $i);
              $columns[] = array("sTitle" => "Model","sClass" => "model".$i, "sName" => 'model' . $i);
              $columns[] = array("sTitle" => "URL", "sName" => 'url' . $i);
              $columns[] = array("sTitle" => "Words <span class='subtitle_word_short' >Short</span>", "sName" => 'short_description_wc' . $i);
              $columns[] = array("sTitle" => "Words <span class='subtitle_word_long' >Long</span>", "sName" => 'long_description_wc' . $i);
              $columns[] = array("sTitle" => "Meta Description","sClass" => "Meta_Description".$i, "sName" => 'Meta_Description' . $i);
              $columns[] = array("sTitle" => "Prod Desc <span class='subtitle_word_long' ># Words</span>","sClass" => "Meta_Description_Count".$i, "sName" => 'Meta_Description_Count' . $i);
            }

        }
        $display_length = intval($this->input->get('iDisplayLength', TRUE));

        $display_start = intval($this->input->get('iDisplayStart', TRUE));
        if (empty($display_start)) {
            $display_start = 0;
        }

        if (empty($display_length)) {
            $display_length = $total_rows - $display_start;
        }
        $qty = 1;
        foreach ($results as $row) {
//            $long_description_wc = $row->long_description_wc;
//            $short_description_wc = $row->short_description_wc;
                
            $result_row = new stdClass();
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

            $result_row->short_description = $row->short_description;
            $result_row->long_description = $row->long_description;
            $result_row->short_description_wc = intval($row->short_description_wc);
            $result_row->long_description_wc = intval($row->long_description_wc);
            $result_row->short_seo_phrases = "None";
            $result_row->long_seo_phrases = "None";
            $result_row->price_diff = "-";
            $result_row->column_external_content = " ";
            $result_row->Custom_Keywords_Short_Description = "";
            $result_row->Custom_Keywords_Long_Description = "";
            $result_row->Meta_Description = "";
            $result_row->Meta_Description_Count = "";
            $result_row->item_id = "";
            $result_row->model = "#";
            $result_row->H1_Tags = "";
            $result_row->H1_Tags_Count = "";
            $result_row->H2_Tags = "";
            $result_row->H2_Tags_Count = "";
            $result_row->column_reviews = " ";
            $result_row->column_features = " ";
            $result_row->duplicate_content = "-";
            $result_row->own_price = floatval($row->own_price);
            $price_diff = unserialize($row->price_diff);
            $result_row->lower_price_exist = false;
            $result_row->snap = '';
            //$class_for_all_case = '';
            $tb_product_name='';
            
            
            if ($build_assess_params->max_similar_item_count > 0) {
                //$class_for_all_case = "class_for_all_case";
                $sim_items = $row->similar_items;
                $max_similar_item_count = (int) $build_assess_params->max_similar_item_count;
                $tb_product_name = 'tb_product_name';
               

                for ($i = 1; $i <= $max_similar_item_count; $i++) {
                    
                    
                    $parsed_attributes_unserialize_val ='';                                                           
                    $parsed_meta_unserialize_val = ''; 
                    $parsed_meta_unserialize_val_c = '';
                    $parsed_meta_unserialize_val_count='';

                    $parsed_attributes_unserialize = unserialize($sim_items[$i - 1]->parsed_attributes);
                    if($parsed_attributes_unserialize['item_id'])
                       $parsed_attributes_unserialize_val = $parsed_attributes_unserialize['item_id'];
                    if($parsed_attributes_unserialize['model'])
                        $parsed_attributes_unserialize_val = $parsed_attributes_unserialize['model'];

                    $parsed_meta_unserialize = unserialize($sim_items[$i - 1]->parsed_meta);
                    if($parsed_meta_unserialize['description']){
                     $parsed_meta_unserialize_val = $parsed_meta_unserialize['description'];
                     $parsed_meta_unserialize_val_c = count(explode(" ",$parsed_meta_unserialize_val));
                     if($parsed_meta_unserialize_val_c !=1)
                         $parsed_meta_unserialize_val_count = $parsed_meta_unserialize_val_c;
                     else
                         $parsed_meta_unserialize_val_count = '';
                    } 
                    else if($parsed_meta_unserialize['Description']){
                     $parsed_meta_unserialize_val = $parsed_meta_unserialize['Description'];
                     $parsed_meta_unserialize_val_c = count(explode(" ",$parsed_meta_unserialize_val));
                     if($parsed_meta_unserialize_val_c !=1)
                         $parsed_meta_unserialize_val_count = $parsed_meta_unserialize_val_c;
                     else
                         $parsed_meta_unserialize_val_count = '';
                    }
                    
                    
                    
                    $result_row = (array) $result_row;
                    $result_row["snap$i"] = $sim_items[$i - 1]->snap !== false ? $sim_items["$i-1"]->snap : '-';
                    $result_row['url' . $i] = $sim_items[$i - 1]->url !== false ? "<span class='res_url'><a target='_blank' href='".$sim_items[$i - 1]->url."'>".$sim_items[$i - 1]->url."</a></span>" : "-";
                    $result_row['product_name' . $i] = $sim_items[$i - 1]->product_name !== false ? "<span class='tb_product_name'>".$sim_items[$i - 1]->product_name."</span>" : "-";
                    $result_row['item_id' . $i] = $parsed_attributes_unserialize_val;
                    $result_row['model' . $i] = '#';
                    $result_row['short_description_wc' . $i] = $sim_items[$i - 1]->short_description_wc !== false ? $sim_items[$i - 1]->short_description_wc : '-';
                    $result_row['long_description_wc' . $i] = $sim_items[$i - 1]->long_description_wc !== false ? $sim_items[$i - 1]->long_description_wc : '-';
                    $result_row['Meta_Description' . $i] = $parsed_meta_unserialize_val;
                    $result_row['Meta_Description_Count' . $i] = $parsed_meta_unserialize_val_count;
                }
                $result_row = (object)$result_row;
            } else {
//                $result_row->snap1 = '';
//                $result_row->product_name1 = '';
//                $result_row->url1 = '';
//                $result_row->short_description_wc1 = '-';
//                $result_row->long_description_wc1 = '-';
            }

            if ($row->snap1 && $row->snap1 != '') {
                $result_row->snap1 = "<img src='" . base_url() . "webshoots/" . $row->snap1 . "' />";
            }
            if ($row->product_name1) {
                $result_row->product_name1 = $row->product_name1;
            }
            if ($row->item_id1) {
                $result_row->item_id1 = $row->item_id1;
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


            $pars_atr = $this->imported_data_parsed_model->getByImId($row->imported_data_id);

            if ($pars_atr['parsed_attributes']['cnetcontent'] == 1 && $pars_atr['parsed_attributes']['webcollage'] == 1)
                $result_row->column_external_content = 'CNET, WC';
            elseif ($pars_atr['parsed_attributes']['cnetcontent'] == 1 && $pars_atr['parsed_attributes']['webcollage'] != 1)
                $result_row->column_external_content = 'CNET';
            elseif ($pars_atr['parsed_attributes']['cnetcontent'] != 1 && $pars_atr['parsed_attributes']['webcollage'] == 1)
                $result_row->column_external_content = 'WC';
            else
                $result_row->column_external_content = ' ';
            $result_row->column_reviews = $pars_atr['parsed_attributes']['review_count'];
            $result_row->column_features = $pars_atr['parsed_attributes']['feature_count'];
            
            if($pars_atr['parsed_meta']['description'] && $pars_atr['parsed_meta']['description'] !=''){
                $pars_atr_array = $pars_atr['parsed_meta']['description'];
                $result_row->Meta_Description = $pars_atr_array;
                $words_des = count(explode(" ", $pars_atr_array));
                $result_row->Meta_Description_Count = $words_des;
            }else if($pars_atr['parsed_meta']['Description'] && $pars_atr['parsed_meta']['Description'] !=''){
                $pars_atr_array = $pars_atr['parsed_meta']['Description'];
                $result_row->Meta_Description = $pars_atr_array;
                $words_des = count(explode(" ", $pars_atr_array));
                $result_row->Meta_Description_Count = $words_des;
            }
            if($pars_atr['parsed_attributes']['item_id'] && $pars_atr['parsed_attributes']['item_id'] !=''){
                $result_row->item_id = $pars_atr['parsed_attributes']['item_id'];
            }
            if($pars_atr['parsed_attributes']['model'] && $pars_atr['parsed_attributes']['model'] !=''){
                $result_row->model = $pars_atr['parsed_attributes']['model'];
            }
            
            $result_row->H1_Tags= '';
            $result_row->H1_Tags_Count= '';
            if($pars_atr['HTags']['h1'] && $pars_atr['HTags']['h1'] !=''){
                $H1 = $pars_atr['HTags']['h1'];
                if(is_array($H1)){
                    $str_1 =  "<table  class='table_keywords_long'>";
                    $str_1_Count =  "<table  class='table_keywords_long'>";
                    foreach($H1 as $h1){
                       $str_1.= "<tr><td>".$h1."</td></tr>" ;
                       $str_1_Count.="<tr><td>".strlen($h1)."</td></tr>" ;
                    }
                    $str_1 .="</table>";
                    $str_1_Count .="</table>";
                $result_row->H1_Tags = $str_1;
                $result_row->H1_Tags_Count= $str_1_Count;
                }else{
                   $H1_Count = strlen($pars_atr['HTags']['h1']);
                   $result_row->H1_Tags = "<table  class='table_keywords_long'><tr><td>".$H1."</td></tr></table>";;
                   $result_row->H1_Tags_Count = "<table  class='table_keywords_long'><tr><td>".$H1_Count."</td></tr></table>";;
                }
                
            }
            
            $result_row->H2_Tags= '';
            $result_row->H2_Tags_Count= '';
            if($pars_atr['HTags']['h2'] && $pars_atr['HTags']['h2'] !=''){
                $H2 = $pars_atr['HTags']['h2'];
                if(is_array($H2)){
                    $str_2 =  "<table  class='table_keywords_long'>";
                    $str_2_Count =  "<table  class='table_keywords_long'>";
                    foreach($H2 as $h2){
                       $str_2.= "<tr><td>".$h2."</td></tr>" ;
                       $str_2_Count.="<tr><td>".strlen($h2)."</td></tr>" ;
                    }
                    $str_2 .="</table>";
                    $str_2_Count .="</table>";
                $result_row->H2_Tags = $str_2;
                $result_row->H2_Tags_Count= $str_2_Count;
                }else{
                   $H2_Count = strlen($pars_atr['HTags']['h2']);
                   $result_row->H2_Tags = "<table  class='table_keywords_long'><tr><td>".$H2."</td></tr></table>";;
                   $result_row->H2_Tags_Count = "<table  class='table_keywords_long'><tr><td>".$H2_Count."</td></tr></table>";;
                }
                
            }
            
             $custom_seo = $this->keywords_model->get_by_imp_id($row->imported_data_id);
             $Custom_Keywords_Long_Description = "<table class='table_keywords_long'>";
             if($custom_seo['primary']){
                 if($row->long_description){
                     $_count = $this->keywords_appearence($row->long_description, $custom_seo['primary']);
                     $cnt = count(explode(' ',$custom_seo['primary'] ));
                     $_count = round(($_count*$cnt/$row->long_description_wc)*100, 2)."%";
                     $Custom_Keywords_Long_Description .= "<tr><td>".$custom_seo['primary']."</td><td>$_count</td></tr>";
                 }else{
                     $_count = ' ';
                 }
                 
             };
             if($custom_seo['secondary']){
                  if($row->long_description){
                     $_count = $this->keywords_appearence($row->long_description, $custom_seo['secondary']);
                     $cnt = count(explode(' ',$custom_seo['secondary'] ));
                     $_count = round(($_count*$cnt/$row->long_description_wc)*100, 2)."%";
                     $Custom_Keywords_Long_Description .= "<tr><td>".$custom_seo['secondary']."</td><td>$_count</td></tr>";
                 }else{
                     $_count = ' ';
                 }
                 
             };
             if($custom_seo['tertiary']){
                 if($row->long_description){
                     $_count = $this->keywords_appearence($row->long_description, $custom_seo['tertiary']);
                     $cnt = count(explode(' ',$custom_seo['tertiary'] ));
                     $_count = round(($_count*$cnt/$row->long_description_wc)*100, 2)."%";
                     $Custom_Keywords_Long_Description .= "<tr><td>".$custom_seo['tertiary']."</td><td> $_count</td></tr>";
                 }else{
                     $_count = ' ';
                 }
                
             };
             
             
             
             $result_row->Custom_Keywords_Long_Description =  $Custom_Keywords_Long_Description."</table>";
                
             $Custom_Keywords_Short_Description = "<table class='table_keywords_short'>";
             
             if($custom_seo['primary']){
                 if($row->short_description){
                    $_count = $this->keywords_appearence($row->short_description, $custom_seo['primary']);
                    $cnt = count(explode(' ',$custom_seo['primary'] ));
                    $_count = round(($_count*$cnt/$row->short_description_wc)*100, 2)."%";
                    $Custom_Keywords_Short_Description .= "<tr><td>".$custom_seo['primary']."</td><td>$_count</td></tr>";
                 }else{
                     $_count = ' ';
                 }
                 
             };
             if($custom_seo['secondary']){
                 if($row->short_description){
                     $_count = $this->keywords_appearence($row->short_description, $custom_seo['secondary']);
                     $cnt = count(explode(' ',$custom_seo['secondary'] ));
                     $_count = round(($_count*$cnt/$row->short_description_wc)*100, 2)."%";
                     $Custom_Keywords_Short_Description .= "<tr><td>".$custom_seo['secondary']."</td><td>$_count</td></tr>";
                 }else{
                     $_count = ' ';
                 }
                 
             };
             if($custom_seo['tertiary']){
                 if($row->short_description){
                     $_count = $this->keywords_appearence($row->short_description, $custom_seo['tertiary']);
                     $cnt = count(explode(' ',$custom_seo['tertiary'] ));
                     $_count = round(($_count*$cnt/$row->short_description_wc)*100, 2)."%";
                     $Custom_Keywords_Short_Description .= "<tr><td>".$custom_seo['tertiary']."</td><td>$_count</td></tr>";
                 }else{
                     $_count = ' ';
                 }
                
             };
                $result_row->Custom_Keywords_Short_Description =  $Custom_Keywords_Short_Description."</table>";
             
            
            
            if ($row->snap != null && $row->snap != '') {
                $result_row->snap = $row->snap;
            }

            if (floatval($row->own_price) <> false) {
                $own_site = parse_url($row->url, PHP_URL_HOST);
                $own_site = str_replace('www.', '', $own_site);
                $own_site = str_replace('www1.', '', $own_site);
                $result_row->price_diff = "<nobr>" . $own_site . " - $" . $row->own_price . "</nobr><br />";
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
                if ($result_row->lower_price_exist == true) {
                    $items_priced_higher_than_competitors += $row->items_priced_higher_than_competitors;
                }
                $result_row->price_diff = $price_diff_res;
            }

            $result_row->competitors_prices = unserialize($row->competitors_prices);

            if (intval($row->include_in_assess_report) > 0) {
                $detail_comparisons_total += 1;
            }

            if ($this->settings['statistics_table'] == "statistics_new") {
                $short_seo = unserialize($row->short_seo_phrases);
                if ($short_seo) {
                    $str_short_seo = '<table class="table_keywords_short">';
                    foreach ($short_seo as $val) {
                        $str_short_seo .= '<tr><td>'.$val['ph'] . '</td><td>' . $val['prc'] . '%</td></tr>';
                    }
                    $result_row->short_seo_phrases = $str_short_seo.'</table>';
                }
                $long_seo = unserialize($row->long_seo_phrases);
                if ($long_seo) {
                    $str_long_seo = '<table class="table_keywords_long">';
                    foreach ($long_seo as $val) {
                        $str_long_seo .= '<tr><td>'.$val['ph'] . '</td><td>' . $val['prc'] . '%</td></tr>';
                    }
                    $result_row->long_seo_phrases = $str_long_seo.'</table>';
                }
            } else {
                $result_row->short_seo_phrases = $row->short_seo_phrases;
                $result_row->long_seo_phrases = $row->long_seo_phrases;
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
                    if ($duplicate_short_percent_total >= 20 || $duplicate_long_percent_total >= 20) {
                        $items_have_more_than_20_percent_duplicate_content += 1;
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

            //$items_priced_higher_than_competitors = $this->statistics_model->countAllItemsHigher($batch_id);

            if ($result_row->short_seo_phrases == 'None' && $result_row->long_seo_phrases == 'None') {
                $items_unoptimized_product_content++;
            }

//            if (($result_row->short_description_wc < 20 && $build_assess_params->short_less == 20) &&
//                ($result_row->long_description_wc < 100 && $build_assess_params->long_less==100)) {
//                $items_short_products_content++;
//            }
//
//            if (($result_row->short_description_wc <= 20 && $build_assess_params->long_less == false ) ||
//                ($result_row->long_description_wc <= 100 && $build_assess_params->short_less == false)){
//                $items_short_products_content++;
//            }
//
//            if (($result_row->short_description_wc <= 20 && $build_assess_params->long_less == -1 ) ||
//                ($result_row->long_description_wc <= 100 && $build_assess_params->short_less == -1)){
//                $items_short_products_content++;
//            }

            if ($result_row->short_description_wc > 0) {
                $short_wc_total_not_0++;
            }

            if ($result_row->long_description_wc > 0) {
                $long_wc_total_not_0++;
            }

            if ($result_row->short_description_wc <= $build_assess_params->short_less) {
                $items_short_products_content_short++;
            }

            if ($result_row->long_description_wc <= $build_assess_params->long_less) {
                $items_long_products_content_short++;
            }


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

            $recomend = false;
//            if ($items_priced_higher_than_competitors > 0) {
//                $recomend = true;
//            }
//            if ($items_have_more_than_20_percent_duplicate_content == 0) {
//                $recomend = true;
//            }
//            if ($items_unoptimized_product_content > 0) {
//                $recomend = true;
//            }
//            if ($items_short_products_content_short > 0 || $items_long_products_content_short > 0) {
//                $recomend = true;
//            }
            if (($result_row->short_description_wc <= $build_assess_params->short_less ||
                    $result_row->long_description_wc <= $build_assess_params->long_less) && ($build_assess_params->long_less_check || $build_assess_params->long_more_check)
            ) {
                $recomend = true;
            }
            if ($result_row->short_seo_phrases == 'None' && $result_row->long_seo_phrases == 'None') {
                $recomend = true;
            }
            if ($result_row->lower_price_exist == true && !empty($result_row->competitors_prices)) {
                if (min($result_row->competitors_prices) < $result_row->own_price) {
                    $recomend = true;
                }
            }

            if ($build_assess_params->flagged == true && $recomend == false) {
                continue;
            }
            if ($build_assess_params->price_diff == true && $result_row->lower_price_exist == false) {
                continue;
            }

            $result_table[] = $result_row;
//            ++$qty;
//            if($qty>$display_length+$display_start)break;
        }

        if ($this->settings['statistics_table'] == "statistics_new") {
            $own_batch_total_items = $this->statistics_new_model->total_items_in_batch($batch_id);
        } else {
            $own_batch_total_items = $this->statistics_model->total_items_in_batch($batch_id);
        }

        $report['summary']['total_items'] = $own_batch_total_items;
        $report['summary']['items_priced_higher_than_competitors'] = $items_priced_higher_than_competitors;
        $report['summary']['items_have_more_than_20_percent_duplicate_content'] = $items_have_more_than_20_percent_duplicate_content;
        $report['summary']['items_unoptimized_product_content'] = $items_unoptimized_product_content;
        $report['summary']['items_short_products_content_short'] = $items_short_products_content_short;
        $report['summary']['items_long_products_content_short'] = $items_long_products_content_short;
        $report['summary']['short_wc_total_not_0'] = $short_wc_total_not_0;
        $report['summary']['long_wc_total_not_0'] = $long_wc_total_not_0;
        $report['summary']['short_description_wc_lower_range'] = $build_assess_params->short_less;
        $report['summary']['long_description_wc_lower_range'] = $build_assess_params->long_less;


        // only if second batch select - get absent products, merge it with result_table
//        if (isset($build_assess_params->compare_batch_id) && $build_assess_params->compare_batch_id > 0) {
//            $absent_items = $this->statistics_model->batches_compare($batch_id, $build_assess_params->compare_batch_id);
//
//            foreach ($absent_items as $absent_item) {
//                $result_row = new stdClass();
//                $result_row->product_name = $absent_item['product_name'];
//                $result_row->url = $absent_item['url'];
//                $result_row->recommendations = $absent_item['recommendations'];
//                $result_table[] = $result_row;
//            }
//
//            $own_batch = $this->batches_model->get($batch_id);
//            $compare_customer = $this->batches_model->getCustomerById($build_assess_params->compare_batch_id);
//            $compare_batch = $this->batches_model->get($build_assess_params->compare_batch_id);
//
//            $compare_batch_total_items = $this->statistics_model->total_items_in_batch($build_assess_params->compare_batch_id);
//            $report['summary']['own_batch_total_items'] = $own_batch_total_items;
//            $report['summary']['compare_batch_total_items'] = $compare_batch_total_items;
//        }

//        $report['recommendations']['absent_items'] = $absent_items;
//        $report['summary']['absent_items_count'] = count($absent_items);
//        $report['summary']['own_batch_name'] = $own_batch[0]->title;
//        $report['summary']['compare_customer_name'] = $compare_customer[0]->name;
//        $report['summary']['compare_batch_name'] = $compare_batch[0]->title;

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

        $total_rows = count($results);

        $echo = intval($this->input->get('sEcho'));

        $output = array(
            "sEcho" => $echo,
            "iTotalRecords" => $total_rows,
            "iTotalDisplayRecords" => $total_rows,
            "iDisplayLength" => $display_length,
            "aaData" => array()
        );
       
        if (!empty($result_table)) {
            $c = 0;
                       
            foreach ($result_table as $data_row) {
                              
                if ($c >=$display_start) {
                                       
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

                        /* if ($data_row->short_description_wc <= $build_assess_params->short_less ||
                          $data_row->long_description_wc <= $build_assess_params->long_less) {
                          $sd_diff = $build_assess_params->short_less - $data_row->short_description_wc;
                          $ld_diff = $build_assess_params->long_less - $data_row->long_description_wc;
                          $increase_wc = max($sd_diff, $ld_diff);
                          $recommendations[] = '<li>Increase descriptions word count by'.$increase_wc.' words</li>';
                          } */

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
                        '<span style="cursor:pointer;">'.$snap.'</span>',
                        $row_created,
                        '<span class= "'. $tb_product_name.'">'.$data_row->product_name."</span>",
                        $data_row->item_id,
                        $data_row->model,
                        $row_url,
                        $data_row->short_description_wc,
                        $data_row->short_seo_phrases,
                        $data_row->long_description_wc,
                        $data_row->long_seo_phrases,
                        $data_row->Custom_Keywords_Short_Description,
                        $data_row->Custom_Keywords_Long_Description,
                        $data_row->Meta_Description,
                        $data_row->Meta_Description_Count,
                        $data_row->H1_Tags,
                        $data_row->H1_Tags_Count,
                        $data_row->H2_Tags,
                        $data_row->H2_Tags_Count,
                        $data_row->duplicate_content,
                        $data_row->column_external_content,
                        $data_row->column_reviews,
                        $data_row->column_features,
                        $data_row->price_diff,
                        $recommendations_html,
                        json_encode($data_row)
                    );

                    if ($build_assess_params->max_similar_item_count > 0) {
                    $data_row = (array)$data_row;
                    for ($i = 1; $i <= $build_assess_params->max_similar_item_count; $i++) {
                            $output_row[] = $data_row['snap' . $i]!=null?$data_row['snap' . $i]:'-';
                            $output_row[] = $data_row['product_name' . $i]!=null?$data_row['product_name' . $i]:'-';
                            $output_row[] = $data_row['item_id' . $i]!=null?$data_row['item_id' . $i]:'';
                            $output_row[] = $data_row['model' . $i]!=null?$data_row['model' . $i]:'';
                            $output_row[] = $data_row['url' . $i]!=null?$data_row['url' . $i]:'-';
                            $output_row[] = $data_row['short_description_wc' . $i]!=null?$data_row['short_description_wc' . $i]:'-';
                            $output_row[] = $data_row['long_description_wc' . $i]!=null?$data_row['long_description_wc' . $i]:'-';
                            $output_row[] = $data_row['Meta_Description' . $i]!=null?$data_row['Meta_Description' . $i]:'';
                            $output_row[] = $data_row['Meta_Description_Count' . $i]!=null?$data_row['Meta_Description_Count' . $i]:'';
                        }
                        $data_row = (object)$data_row;
                    } else {

                        $output_row[] = $data_row->snap1;
                        $output_row[] = $data_row->product_name1;
                        $output_row[] = $data_row->item_id1;
                        $output_row[] = $data_row->model1;
                        $output_row[] = $data_row->url1;
                        $output_row[] = $data_row->short_description_wc1;
                        $output_row[] = $data_row->long_description_wc1;
                        $output_row[] = $data_row->Meta_Description1;
                        $output_row[] = $data_row->Meta_Description_Count1;
                       
                    }
                    $output['aaData'][] = $output_row;
                }
                  
                 
                if ($display_length > 0) {
                    if ($c >= ($display_start + $display_length - 1)) {
                        break;
                    }
                }
              $c++;
            }
        }
        
//       echo  "<pre>";
//       print_r($columns);
//       print_r($output['aaData']);exit;
        $output['columns']= $columns;
        $output['ExtraData']['report'] = $report;
            
        return $output;
    }

    public function get_board_view_snap(){
        if(isset($_POST['batch_id']) && $_POST['batch_id'] != 0){
            $batch_id = $_POST['batch_id'];
            $params = new stdClass();
            $params->batch_id = $batch_id;
            $params->txt_filter = '';
            $params->date_from = '';
            $params->date_to = '';
            if(isset($_POST['next_id']))
                $params->id = $_POST['next_id'];
            else
                $params->snap_count = 12;
            $results = $this->get_data_for_assess($params);
            /****Foreach Begin****/
            $snap_data = array();
            foreach($results as $data_row){
                if ($data_row->snap != '') {
                    $file = realpath(BASEPATH . "../webroot/webshoots") . '/' . $data_row->snap;
                    if (file_exists($file)) {
                        if (filesize($file) > 1024) {
                            $snap = "<img src='" . base_url() . "webshoots/" . $data_row->snap . "' rel='" . $data_row->id . "' />";
                        $output = array(
                            $snap,
                            $data_row->product_name,
                            json_encode($data_row),
                        );
                        $snap_data[] = $output;
}
                    }
                }
            }
            /****Foreach End****/
            $this->output->set_content_type('application/json')->set_output(json_encode($snap_data));
        }
    }

    public function get_graph_batch_data(){
        
        if(isset($_POST['batch_id']) && isset($_POST['batch_compare_id'])){
            
            if(trim($_POST['batch_id']) == '')
                $batch_id = -1;
            else
                $batch_id = $_POST['batch_id'];
            
            if(trim($_POST['batch_compare_id']) == '' || $_POST['batch_compare_id'] == 'All' )
                $batch_compare_id = -1;
            else
                $batch_compare_id = $_POST['batch_compare_id'];
            
            $batch_arr = array($batch_id, $batch_compare_id);
            $snap_data = array();
            foreach($batch_arr as $key => $batchID){
                $params = new stdClass();
                $params->batch_id = $batchID;
                $params->txt_filter = '';
                $params->date_from = '';
                $params->date_to = '';
                $results = $this->get_data_for_assess($params);

                foreach($results as $data_row){
                    $snap_data[$key]['product_name'][] = (string)$data_row->product_name;
                    $snap_data[$key]['url'][] = (string)$data_row->url;
                    $snap_data[$key]['short_description_wc'][] = (int)$data_row->short_description_wc;
                    $snap_data[$key]['long_description_wc'][] = (int)$data_row->long_description_wc;
                    $snap_data[$key]['revision'][] = (int)$data_row->revision;
                    $snap_data[$key]['own_price'][] = (float)$data_row->own_price;
                    $htags = unserialize($data_row->htags);
                    if($htags){
                        $snap_data[$key]['h1_word_counts'][] = count($htags['h1']);
                        $snap_data[$key]['h2_word_counts'][] = count($htags['h2']);
                    } else {
                        $snap_data[$key]['h1_word_counts'][] = 0;
                        $snap_data[$key]['h2_word_counts'][] = 0;
                }
                }
                
            }
            
            $this->output->set_content_type('application/json')->set_output(json_encode($snap_data));
        }
    }
     private function keywords_appearence($desc, $phrase) {
        
        $desc= strip_tags($desc);
        return substr_count($desc, $phrase);
    }
    
}
