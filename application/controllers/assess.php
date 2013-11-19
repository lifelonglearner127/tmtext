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
        if (!$this->ion_auth->logged_in()) {
            //redirect them to the login page
            redirect('auth/login', 'refresh');
        }
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
            $batch2 = $this->input->get('batch2') && $this->input->get('batch2') == 'undefined' ? '' : $this->input->get('batch2');
            if ($batch2 === '') {
                $params->iDisplayLength = $this->input->get('iDisplayLength');
                $params->iDisplayStart = $this->input->get('iDisplayStart');
            }

            $results = $this->get_data_for_assess($params);
            $cmp = array();

            if ($batch2 != '' && $batch2 != 0 && $batch2 != 'all') {
                $this->load->model('batches_model');
                $build_assess_params->max_similar_item_count = 1;

                $customer_name = $this->batches_model->getCustomerUrlByBatch($batch2);

                foreach ($results as $val) {
                    $similar_items_data = array();
                    if (substr_count(strtolower($val->similar_products_competitors), strtolower($customer_name)) > 0) {

                        $similar_items = unserialize($val->similar_products_competitors);

                        if (count($similar_items) >1) {
                            foreach ($similar_items as $key => $item) {

                                if ( !empty($customer_name) && !empty($item['customer']) && substr_count(strtolower($customer_name), strtolower($item['customer'])) > 0) {
                                    $parsed_attributes_unserialize_val = '';
                                    $parsed_meta_unserialize_val = '';
                                    $parsed_meta_unserialize_val_c = '';
                                    $parsed_model_unserialize_val = '';
                                    $parsed_meta_keywords_unserialize_val = '';
                                    $parsed_loaded_in_seconds_unserialize_val = '';
                                    $parsed_average_review_unserialize_val_count = '';
                                    $cmpare = $this->statistics_new_model->get_compare_item($item['imported_data_id']);

                                    $parsed_attributes_unserialize = unserialize($cmpare->parsed_attributes);

                                    if (isset($parsed_attributes_unserialize['item_id']))
                                        $parsed_attributes_unserialize_val = $parsed_attributes_unserialize['item_id'];
                                    if (isset($parsed_attributes_unserialize['model']))
                                        $parsed_model_unserialize_val = $parsed_attributes_unserialize['model'];
                                    if (isset($parsed_attributes_unserialize['loaded_in_seconds']))
                                        $parsed_loaded_in_seconds_unserialize_val = $parsed_attributes_unserialize['loaded_in_seconds'];
                                    if (isset($parsed_attributes_unserialize['average_review']))
                                        $parsed_average_review_unserialize_val_count = $parsed_attributes_unserialize['average_review'];

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
                                        $Meta_Keywords_un = "<table class='table_keywords_long'>";
                                            $cnt_meta = explode(',', $parsed_meta_unserialize['keywords']);
                                            $cnt_meta_count = count($cnt_meta);
                                            $_count_meta = 0;
                                            foreach($cnt_meta as $cnt_m){
                                                $cnt_m = trim($cnt_m);
                                                if($cmpare->Short_Description || $cmpare->Long_Description){
                                                    $_count_meta = $this->keywords_appearence($cmpare->Long_Description.$cmpare->Short_Description, $cnt_m);
                                                    $_count_meta_num = round(($_count_meta * $cnt_meta_count / ($cmpare->long_description_wc + $cmpare->short_description_wc)) * 100, 2) . "%";
                                                    $Meta_Keywords_un .= "<tr><td>" . $cnt_m . "</td><td>".$_count_meta_num."</td></tr>";
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
                                            $Meta_Keywords_un .= "</table>";
                                            $parsed_meta_keywords_unserialize_val = $Meta_Keywords_un;
                                        }




                                    $val->snap1 = $cmpare->snap;
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
                                    $val->average_review1 = $parsed_average_review_unserialize_val_count;
                                    $cmpare->imported_data_id = $item['imported_data_id'];

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

        $pdf->SetHTMLFooter('<span style="font-size: 8px;">Copyright В© 2013 Content Solutions, Inc.</span>');

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
        $selected_columns = $_GET['checked_columns'];
        $selected_columns = explode(',', trim($selected_columns));
        $batch_name = $_GET['batch_name'];
//        echo  '<pre>';
//        print_r($selected_columns);exit;
        if (($key = array_search('snap', $selected_columns)) !== false) {
            unset($selected_columns[$key]);
        }
        $line = array('created' => 'Date', 'product_name' => 'Product Name', 'url' => 'Url','Short_Description' =>'Short Description', 'short_description_wc' => 'Short Desc # Words','Long_Description' =>'Long Description', 'long_description_wc' => 'Long Desc # Words', 'short_seo_phrases' => ' Short Desc - Found SEO Keywords', 'long_seo_phrases' => ' Short Desc - Found SEO Keywords', 'price_diff' => 'Price', 'column_features' => 'Features', 'column_reviews' => 'Reviews');


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

        $query = $this->db->query('select `s`.*,
            (select `value` from imported_data_parsed where `key`="Product Name" and `imported_data_id` = `s`.`imported_data_id` limit 1) as `product_name`,
            (select `value` from imported_data_parsed where `key`="Description" and `imported_data_id` = `s`.`imported_data_id` limit 1) as `Short_Description`,
            (select `value` from imported_data_parsed where `key`="Long_Description" and `imported_data_id` = `s`.`imported_data_id` limit 1) as `Long_Description`,
            (select `value` from imported_data_parsed where `key`="Url" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `url`
            from `statistics_new` as `s` ' . $qnd);
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
                                    $den_for_gap = 0;
                                     $parsed_attributes_unserialize_val = '';
                                    $parsed_meta_unserialize_val = '';
                                    $parsed_meta_unserialize_val_c = '';
                                    $parsed_attributes_column_features_unserialize_val = '';
                                    $parsed_model_unserialize_val = '';
                                    $parsed_meta_keywords_unserialize_val = '';
                                    $parsed_loaded_in_seconds_unserialize_val = '';
                                    $parsed_average_review_unserialize_val_count = '';
                                    $cmpare = $this->statistics_new_model->get_compare_item($item['imported_data_id']);

                                    $parsed_attributes_unserialize = unserialize($cmpare->parsed_attributes);

                                    if (isset($parsed_attributes_unserialize['column_features']))
                                        $parsed_attributes_column_features_unserialize_val = $parsed_attributes_unserialize['column_features'];
                                    if (isset($parsed_attributes_unserialize['item_id']))
                                        $parsed_attributes_unserialize_val = $parsed_attributes_unserialize['item_id'];
                                    if (isset($parsed_attributes_unserialize['model']))
                                        $parsed_model_unserialize_val = $parsed_attributes_unserialize['model'];
                                    if (isset($parsed_attributes_unserialize['loaded_in_seconds']))
                                        $parsed_loaded_in_seconds_unserialize_val = $parsed_attributes_unserialize['loaded_in_seconds'];
                                    if (isset($parsed_attributes_unserialize['average_review']))
                                        $parsed_average_review_unserialize_val_count = $parsed_attributes_unserialize['average_review'];

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
                                            foreach($cnt_meta as $cnt_m){
                                                $cnt_m = trim($cnt_m);
                                                if($cmpare->Short_Description || $cmpare->Long_Description){
                                                    $_count_meta = $this->keywords_appearence($cmpare->Long_Description.$cmpare->Short_Description, $cnt_m);
                                                    $_count_meta_num = round(($_count_meta * $cnt_meta_count / ($cmpare->long_description_wc + $cmpare->short_description_wc)) * 100, 2);
                                                   
                                                    if($_count_meta_num >= 2){
                                                         $den_for_gap = $_count_meta_num;
                                                    }
                                                    
                                                    $Meta_Keywords_un .=  $cnt_m . "  - ".$_count_meta_num."%, ";
                                                }
                                            
                                                }
                                            
                                            $parsed_meta_keywords_unserialize_val = $Meta_Keywords_un;
                                        }




                                    $cmpare->item_id = $parsed_attributes_unserialize_val;
                                    $cmpare->model = $parsed_model_unserialize_val;
                                    $cmpare->den_for_gap = $den_for_gap;
                                    $cmpare->Page_Load_Time = $parsed_loaded_in_seconds_unserialize_val;

                                    $cmpare->Meta_Keywords = $parsed_meta_keywords_unserialize_val;
                                    $cmpare->column_features = $parsed_attributes_column_features_unserialize_val;
                                
                                    $cmpare->Meta_Description = $parsed_meta_unserialize_val;
                                    $cmpare->Meta_Description_Count = $parsed_meta_unserialize_val_count;
                                    $cmpare->average_review = $parsed_average_review_unserialize_val_count;
                                
                                    $similar_items_data[] = $cmpare;
                                    $val->similar_items = $similar_items_data;  
                                //$similar_items_data[] = $item['imported_data_id'];
                                }
                            }
                     //$val->similar_items = $similar_items_data;
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
            if (in_array('H2_Tags', $selected_columns)) {
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
                }
            }
          
            foreach ($results as $key => $row) {

                //item_id
                if(in_array('item_id', $selected_columns)){
                    $res_array[$key]['item_id'] = $pars_atr['parsed_attributes']['item_id']?$pars_atr['parsed_attributes']['item_id']:' ';
                }
                //model
                if(in_array('model', $selected_columns)){
                    $res_array[$key]['model'] = $pars_atr['parsed_attributes']['model']?$pars_atr['parsed_attributes']['model']:'';
                }
                
                $row = (array) $row;
                foreach ($line as $k => $v) {
                    $res_array[$key][$k] = $row[$k];
                }
                $row = (object) $row;

                $pars_atr = $this->imported_data_parsed_model->getByImId($row->imported_data_id);

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

                //meta description
                if(in_array('Meta_Description', $selected_columns)){
                    if ($pars_atr['parsed_meta']['description'] && $pars_atr['parsed_meta']['description'] != '') {
                        $res_array[$key]['meta_description']=$pars_atr['parsed_meta']['description'];
                        $words_des = count(explode(" ", $pars_atr['parsed_meta']['description']));
                        $res_array[$key]['Meta_Description_Count'] = $words_des;
                    } else if ($pars_atr['parsed_meta']['Description'] && $pars_atr['parsed_meta']['Description'] != '') {
                        $res_array[$key]['meta_description']=$pars_atr['parsed_meta']['Description'];
                        $words_des = count(explode(" ", $pars_atr['parsed_meta']['Description']));
                        $res_array[$key]['Meta_Description_Count'] = $words_des;
                    }
                }

                //custom keywords

                if(in_array('Custom_Keywords_Short_Description',$selected_columns) || in_array('Custom_Keywords_Long_Description',$selected_columns)){
                    $custom_keywords= $this->custom_keywords($row->imported_data_id, $row->Long_Description,$row->long_description_wc, $row->Short_Description,$row->short_description_wc);
                     if(in_array('Custom_Keywords_Short_Description',$selected_columns)){
                         $res_array[$key]['Custom_Keywords_Short_Description']= $custom_keywords['Custom_Keywords_Short'];
                     }
                     if(in_array('Custom_Keywords_Long_Description',$selected_columns)){
                         $res_array[$key]['Custom_Keywords_Long_Description']= $custom_keywords['Custom_Keywords_Long'];
                     }
                }
                //loaded_in_seconds
                if(in_array('Page_Load_Time', $selected_columns)){
                    $res_array[$key]['Page_Load_Time'] = $pars_atr['parsed_attributes']['loaded_in_seconds']!==false?$pars_atr['parsed_attributes']['loaded_in_seconds']:'';
                }
                if(in_array('column_external_content', $selected_columns)){
                   $res_array[$key]['column_external_content']= $this->column_external_content($pars_atr['parsed_attributes']['cnetcontent'],$pars_atr['parsed_attributes']['webcollage']);
                }
                if (in_array('column_features', $selected_columns)) {
                    $res_array[$key]['column_features'] = $pars_atr['parsed_attributes']['feature_count'] !== false ? $pars_atr['parsed_attributes']['feature_count'] : '';
                }
                if (in_array('column_reviews', $selected_columns)) {
                    $res_array[$key]['column_reviews'] = $row->revision !== false ? $row->revision : '';
                }
                if (in_array('H1_Tags', $selected_columns) && $pars_atr['HTags']['h1'] && $pars_atr['HTags']['h1'] != '') {
                    $H1 = $pars_atr['HTags']['h1'];
                    if (is_array($H1)) {

                        $i=0;
                        foreach ($H1 as $k => $h1) {
                            if($i<2){
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
                        if ($H1_tag_count > 2){
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

                        $i=0;
                        foreach ($H2 as $k => $h2) {
                            if($i<2){
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
                        if ($H2_tag_count > 2){
                           $H2_tag_count = 2;
                        }

                        for ($k = 0; $k < $H2_tag_count; $k++) {
                            if (!$res_array[$key]['H2_Tags' . $k]) {
                                $res_array[$key]['H2_Tags' . $k] = '';
                                $res_array[$key]['H2_Tags_Count' . $k] = ' ';
                            }
                        }
                    }
                }
                else{
                     if ($H2_tag_count > 2){
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
                        if($i == 1){
                     	if (isset($sim_items[$i -1]->column_features)) {
                        	$f_count1 =  $sim_items[$i -1]->column_features;
                     	} else {
                     		$f_count1 = 0;
                     	}
                        
                       

                    }
                       
                        if (in_array('gap', $selected_columns)) {
                        $res_array[$key]['Gap analysis'] = '';
                            
                            if(isset($sim_items[$i -1]) && $sim_items[$i -1]->long_description_wc &&  $sim_items[$i -1]->short_description_wc && ($sim_items[$i -1]->short_description_wc+$sim_items[$i -1]->long_description_wc)<100){
                                $totoal = $sim_items[$i -1]->short_description_wc+$sim_items[$i -1]->long_description_wc;
                                $res_array[$key]['Gap analysis'].="Competitor total product description length only $totoal words, ";
                            }

                            if($res_array[$key]['column_features'] && $f_count1 && $f_count1 < $res_array[$key]['column_features']){
                                 $res_array[$key]['Gap analysis'].="Competitor has fewer features listed, ";
                            }
                            if(!$sim_items[$i -1]->den_for_gap){

                            $res_array[$key]['Gap analysis'] .= "Competitor is not keyword optimized,  ";


                        }
                        }  
                        
                        
                        if (in_array('item_id', $selected_columns)) {
                            $res_array[$key]['Item Id (' . $i . ")"] = $sim_items[$i - 1]->item_id ? $sim_items[$i - 1]->item_id : ' - ';
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
                        
                        if(in_array('Meta_Keywords', $selected_columns)){
                        $res_array[$key]['Meta_Keywords(' . $i . ")"] = $sim_items[$i - 1]->Meta_Keywords ? $sim_items[$i - 1]->Meta_Keywords : '';
                        }
                        if (in_array('Meta_Description', $selected_columns)) {
                            $res_array[$key]['Meta_Description (' . $i . ")"] = $sim_items[$i - 1]->Meta_Description ? $sim_items[$i - 1]->Meta_Description : '';
                            $res_array[$key]['Meta Desc Words (' . $i . ")"] = $sim_items[$i - 1]->Meta_Description_Count ? $sim_items[$i - 1]->Meta_Description_Count : '';
                        }
                        if (in_array('Page_Load_Time', $selected_columns)) {
                            $res_array[$key]['Page Load Time (' . $i . ")"] =$sim_items[$i - 1]->Page_Load_Time ? $sim_items[$i - 1]->Page_Load_Time : ' - ';
                         }
                       
                    }                    


             }


            if(in_array('model', $selected_columns)){
            array_unshift( $line, 'Model');
            }
            if(in_array('item_id', $selected_columns)){
                 array_unshift( $line, 'item ID');
            }
            if(in_array('Meta_Keywords', $selected_columns)){
                 $line[]=  'Meta Keywords';
            }

            //meta description
            if(in_array('Meta_Description', $selected_columns)){
                $line[]=  'Meta Description';
                $line[]=  'Meta Desc Words';
            }
            if(in_array('Custom_Keywords_Short_Description',$selected_columns)){
                $line[]= 'Custom Keywords - Short Description';
            }
            if(in_array('Custom_Keywords_Long_Description',$selected_columns)){
                $line[]= 'Custom Keywords - Long Description';
            }
            if(in_array('Page_Load_Time', $selected_columns)){
                $line[]=  'Page Load Time';
            }
            if(in_array('column_external_content', $selected_columns)){
               $line[]= 'External Content';
            }
            if (in_array('column_features', $selected_columns)) {
                $res_array[$key]['column_features'] = $pars_atr['parsed_attributes']['feature_count'] !== false ? $pars_atr['parsed_attributes']['feature_count'] : '';
            }
            if (in_array('column_reviews', $selected_columns)) {
                $res_array[$key]['column_reviews'] = $row->revision !== false ? $row->revision : '';
           }

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
                    $line[] = 'Gap analysis';
                }
                if (in_array('item_id', $selected_columns)) {
                    $line[] = "Item Id(" . ($i+1) . ")";
                }
                if (in_array('model', $selected_columns)) {
                    $line[] = "Model(" . ($i+1) . ")";
                }
               
                if (in_array('product_name', $selected_columns)) {
                    $line[] = "Product Name(" . ($i+1) . ")";
                }
                 if (in_array('url', $selected_columns)) {
                    $line[] = "Url(" . ($i+1) . ")";
                }
                if (in_array('Short_Description', $selected_columns)) {
                    $line[] = "Short Description(" . ($i+1) . ")";
                }
                if (in_array('short_description_wc', $selected_columns)) {
                    $line[] = "Short Desc # Words(" . ($i+1) . ")";
                }
                if (in_array('Long_Description', $selected_columns)) {
                    $line[] = "Long Description(" . ($i+1) . ")";
                }
                if (in_array('long_description_wc', $selected_columns)) {
                    $line[] = " Long Desc # Words(" . ($i+1) . ")";
                }
                if (in_array('Meta_Keywords', $selected_columns)) {
                    $line[] = "Meta Keywords (" . ($i+1) . ")";
                }
                if (in_array('Meta_Description', $selected_columns)) {
                    $line[] = "Meta Description(" . ($i+1) . ")";
                    $line[] = " Meta Desc Words(" . ($i+1) . ")";
                }
                if (in_array('Page_Load_Time', $selected_columns)) {
                    $line[] = "Page Load Time(" . ($i+1) . ")";
                }
               
                
                
          
              
            }

        array_unshift($res_array, $line);
        $this->load->helper('csv');
//        echo  '<pre>';
//        print_r($res_array);exit;
        array_to_csv($res_array, $batch_name."(".date("Y-m-d H:i") . ').csv');
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
                'Page_Load_Time' => 'true',
                'Short_Description' => 'true',
                'short_description_wc' => 'true',
                'Meta_Keywords' => 'true',
                'short_seo_phrases' => 'true',
                'Long_Description' => 'true',
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
                'average_review' => 'true',
                'column_features' => 'true',
                'price_diff' => 'true',
                'gap' => 'true'
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

    function columns() {
        $columns = array(
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
                "sName" => "product_name",
                //"sWidth" => "15%",
                "sClass" => "product_name_text"
            ),
            array(
                "sTitle" => "item ID",
                "sName" => "item_id",
                "sClass" => "item_id"
            ),
            array(
                "sTitle" => "Model",
                "sName" => "model",
                "sClass" => "model"
            ),
            array(
                "sTitle" => "URL",
                "sName" => "url",
                //"sWidth" =>"15%",
                "sClass" => "url_text"
            ),
            array(
                "sTitle" => "Page Load Time",
                "sName" => "Page_Load_Time",
                //"sWidth" =>"15%",
                "sClass" => "Page_Load_Time"
            ),
            array(
                "sTitle" => "<span class='subtitle_desc_short' >Short</span> Description",
                "sName" => "Short_Description",
                "sWidth" =>"25%",
                "sClass" => "Short_Description"
            ),
            array(
                "sTitle" => "Short Desc <span class='subtitle_word_short' ># Words</span>",
                "sName" => "short_description_wc",
                // "sWidth" => "1%",
                "sClass" => "word_short"
            ),
            array(
                "sTitle" => "Meta Keywords",
                "sName" => "Meta_Keywords",
                "sClass" => "Meta_Keywords"
            ),
            array(
                "sTitle" => "Keywords <span class='subtitle_keyword_short'>Short</span>",
                "sName" => "short_seo_phrases",
                //"sWidth" => "2%",
                "sClass" => "keyword_short"
            ),
            array(
                "sTitle" => "<span class='subtitle_desc_long' >Long </span>Description",
                "sName" => "Long_Description",
                //"sWidth" => "2%",
                "sClass" => "Long_Description"
            ),
            array(
                "sTitle" => "Long Desc <span class='subtitle_word_long' ># Words</span>",
                "sName" => "long_description_wc",
                "sWidth" => "1%",
                "sClass" => "word_long"
            ),
            array(
                "sTitle" => "Keywords <span class='subtitle_keyword_long'>Long</span>",
                "sName" => "long_seo_phrases",
                //"sWidth" => "2%",
                "sClass" => "keyword_long"
            ),
            array(
                "sTitle" => "Custom Keywords Short Description",
                "sName" => "Custom_Keywords_Short_Description",
                "sWidth" => "4%",
                "sClass" => "Custom_Keywords_Short_Description"
            ),
            array(
                "sTitle" => "Custom Keywords Long Description",
                "sName" => "Custom_Keywords_Long_Description",
                "sWidth" => "4%",
                "sClass" => "Custom_Keywords_Long_Description"
            ),
            array(
                "sTitle" => "Meta Description",
                "sName" => "Meta_Description",
                "sWidth" => "4%",
                "sClass" => "Meta_Description"
            ),
            array(
                "sTitle" => "Meta Desc <span class='subtitle_word_long' ># Words</span>",
                "sName" => "Meta_Description_Count",
                "sWidth" => "4%",
                "sClass" => "Meta_Description_Count"
            ),
            array(
                "sTitle" => "H1 Tags",
                "sName" => "H1_Tags",
                "sWidth" => "1%",
                "sClass" => "HTags_1"
            ),
            array(
                "sTitle" => "Chars",
                "sName" => "H1_Tags_Count",
                "sWidth" => "1%",
                "sClass" => "HTags"
            ),
            array(
                "sTitle" => "H2 Tags",
                "sName" => "H2_Tags",
                "sWidth" => "1%",
                "sClass" => "HTags_2"
            ),
            array(
                "sTitle" => "Chars",
                "sName" => "H2_Tags_Count",
                "sWidth" => "1%",
                "sClass" => "HTags"
            ),
            array(
                "sTitle" => "Duplicate Content",
                "sName" => "duplicate_content",
            //"sWidth" =>"1%"
            ),
            array(
                "sTitle" => "Content",
                "sName" => "column_external_content",
            //"sWidth" =>"2%"
            ),
            array(
                "sTitle" => "Reviews",
                "sName" => "column_reviews",
            //"sWidth" =>"3%"
            ),
            array(
                "sTitle" => "Avg Review",
                "sName" => "average_review",
            //"sWidth" =>"3%"
                "sClass" => "average_review"
            ),
            array(
                "sTitle" => "Features",
                "sName" => "column_features",
            //"sWidth" => "4%"
            ),
            array(
                "sTitle" => "Price",
                "sName" => "price_diff",
                //"sWidth" =>"2%",
                "sClass" => "price_text"
            ),
            array(
                "sTitle" => "Recommendations",
                "sName" => "recommendations",
                // "sWidth" =>"15%",
                "bVisible" => false,
                "bSortable" => false
            ),
            array(
                "sName" => "add_data",
                "bVisible" => false
            )
        );
        return $columns;
    }

    private function build_asses_table($results, $build_assess_params, $batch_id = '') {

        $columns = $this->columns();
        $duplicate_content_range = 25;
        $this->load->model('batches_model');

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
                $columns[] = array("sTitle" => "item ID", "sClass" => "item_id" . $i, "sName" => 'item_id' . $i);
                $columns[] = array("sTitle" => "Model", "sClass" => "model" . $i, "sName" => 'model' . $i);
                $columns[] = array("sTitle" => "URL", "sName" => 'url' . $i);
                $columns[] = array("sTitle" => "Page Load Time", "sClass" => "Page_Load_Time" . $i, "sName" => 'Page_Load_Time' . $i);
                $columns[] = array("sTitle" => "<span class='subtitle_desc_short{$i}' >Short</span> Description", "sClass" => "Short_Description" . $i, "sName" => 'Short_Description' . $i);
                $columns[] = array("sTitle" => "Words <span class='subtitle_word_short' >Short</span>", "sName" => 'short_description_wc' . $i);
                $columns[] = array("sTitle" => "Meta Keywords", "sClass" => "Meta_Keywords" . $i, "sName" => 'Meta_Keywords' . $i);
                $columns[] = array("sTitle" => "<span class='subtitle_desc_long{$i}' >Long </span>Description", "sClass" => "Long_Description" . $i, "sName" => 'Long_Description' . $i);
                $columns[] = array("sTitle" => "Words <span class='subtitle_word_long' >Long</span>", "sName" => 'long_description_wc' . $i);
                $columns[] = array("sTitle" => "Meta Description", "sClass" => "Meta_Description" . $i, "sName" => 'Meta_Description' . $i);
                $columns[] = array("sTitle" => "Meta Desc <span class='subtitle_word_long' ># Words</span>", "sClass" => "Meta_Description_Count" . $i, "sName" => 'Meta_Description_Count' . $i);
                $columns[] = array("sTitle" => "Avg Review", "sClass" => "average_review" . $i, "sName" => 'average_review' . $i);
                 if($i == 1){
                                $columns[] = array("sTitle" => "Gap Analysis", "sClass" => "gap" . $i, "sName" => 'gap');
                            }
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

            $f_count1 = 0;
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
            $result_row->Meta_Keywords = "";
            $result_row->Page_Load_Time = "";
            $result_row->Short_Description = "";
            $result_row->Long_Description = "";
            $result_row->model = "#";
            $result_row->H1_Tags = "";
            $result_row->H1_Tags_Count = "";
            $result_row->H2_Tags = "";
            $result_row->H2_Tags_Count = "";
            $result_row->column_reviews = " ";
            $result_row->average_review = "";
            $result_row->column_features = " ";
            $result_row->duplicate_content = "-";
            $result_row->own_price = floatval($row->own_price);
            $price_diff = unserialize($row->price_diff);
            $result_row->lower_price_exist = false;
            $result_row->snap = '';
            //$class_for_all_case = '';
            $tb_product_name = '';


            if ($build_assess_params->max_similar_item_count > 0) {
                //$class_for_all_case = "class_for_all_case";
                $sim_items = $row->similar_items;
                $max_similar_item_count = (int) $build_assess_params->max_similar_item_count;
                $tb_product_name = 'tb_product_name';


               for ($i = 1; $i <= $max_similar_item_count; $i++) {


                    $parsed_attributes_unserialize_val = '';
                    $parsed_meta_unserialize_val = '';
                    $parsed_meta_unserialize_val_c = '';
                    $parsed_meta_unserialize_val_count = '';
                    $parsed_meta_keywords_unserialize_val = '';
                    $parsed_loaded_in_seconds_unserialize_val ='';
                    $parsed_average_review_unserialize_val ='';

                    $parsed_attributes_unserialize = unserialize($sim_items[$i - 1]->parsed_attributes);


                    if (isset($parsed_attributes_unserialize['item_id']))
                        $parsed_attributes_unserialize_val = $parsed_attributes_unserialize['item_id'];
                    if (isset($parsed_attributes_unserialize['model']))
                        $parsed_attributes_unserialize_val = $parsed_attributes_unserialize['model'];
                    if (isset($parsed_attributes_unserialize['loaded_in_seconds']))
                        $parsed_loaded_in_seconds_unserialize_val = $parsed_attributes_unserialize['loaded_in_seconds'];
                    if (isset($parsed_attributes_unserialize['average_review']))
                        $parsed_average_review_unserialize_val = $parsed_attributes_unserialize['average_review'];
                    $parsed_meta_unserialize = unserialize($sim_items[$i - 1]->parsed_meta);

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


//                     if ($parsed_meta_unserialize['keywords']) {
//
//                    $Meta_Keywords_un = "<table class='table_keywords_long'>";
//                    $cnt_meta_un = explode(',', $parsed_meta_unserialize['keywords']);
//                    $cnt_meta_count_un = count($cnt_meta_un);
//                    foreach($cnt_meta_un as $cnt_m_un){
//                        $cnt_m_un = trim($cnt_m_un);
//                        $_count_meta_un = $this->keywords_appearence($parsed_meta_unserialize_val, $cnt_m_un);
//                        $_count_meta_num_un = round(($_count_meta_un * $cnt_meta_count_un / $parsed_meta_unserialize_val_count) * 100, 2) . "%";
//                        $Meta_Keywords_un .= "<tr><td>" . $cnt_m_un . "</td><td>".$_count_meta_num_un."</td></tr>";
//                    }
//                    $Meta_Keywords_un .= "</table>";
//                    $parsed_meta_keywords_unserialize_val = $Meta_Keywords_un;
//
//                    }
                     if ($parsed_meta_unserialize['keywords']) {

                    $Meta_Keywords_un = "<table class='table_keywords_long'>";
                    $cnt_meta_un = explode(',', $parsed_meta_unserialize['keywords']);
                    $cnt_meta_count_un = count($cnt_meta_un);
                    foreach($cnt_meta_un as $cnt_m_un){
                        $_count_meta_un = 0;
                        $cnt_m_un = trim($cnt_m_un);
                        if($sim_items[$i - 1]->Long_Description || $sim_items[$i - 1]->Short_Description){
                            $_count_meta_un = $this->keywords_appearence($sim_items[$i - 1]->Long_Description.$sim_items[$i - 1]->Short_Description, $cnt_m_un);
                            $_count_meta_num_un = round(($_count_meta_un * $cnt_meta_count_un / ($sim_items[$i - 1]->long_description_wc + $sim_items[$i - 1]->short_description_wc)) * 100, 2) . "%";
                            $Meta_Keywords_un .= "<tr><td>" . $cnt_m_un . "</td><td>".$_count_meta_num_un."</td></tr>";
//                        }else if($sim_items[$i - 1]->Short_Description){
//                            $_count_meta_un = $this->keywords_appearence($sim_items[$i - 1]->Short_Description, $cnt_m_un);
//                            $_count_meta_num_un = round(($_count_meta_un * $cnt_meta_count_un / $sim_items[$i - 1]->short_description_wc) * 100, 2) . "%";
//                            $Meta_Keywords_un .= "<tr><td>" . $cnt_m_un . "</td><td>".$_count_meta_num_un."</td></tr>";
                         if($i==1 && !$meta_key_gap ){
                            $metta_prc= round(($_count_meta_un * $cnt_meta_count_un / ($row->long_description_wc + $row->short_description_wc)) * 100, 2);
                            if($metta_prc >= 2){
                                $meta_key_gap=$metta_prc;
                            }
                        }
                        }


                    }
                    $Meta_Keywords_un .= "</table>";
                    $parsed_meta_keywords_unserialize_val = $Meta_Keywords_un;

                    }


                     if($i == 1){
                     	if (isset($parsed_attributes_unserialize['feature_count'])) {
                        	$f_count1 =  $parsed_attributes_unserialize['feature_count'];
                     	} else {
                     		$f_count1 = 0;
                     	}

                        if(!$meta_key_gap){

                            $result_row->gap .= "Competitor is not keyword optimized<br>";


                        }

                    }
                    $result_row = (array) $result_row;
                    $result_row["snap$i"] = $sim_items[$i - 1]->snap !== false ? $sim_items[$i-1]->snap : '-';
                    $result_row['url' . $i] = $sim_items[$i - 1]->url !== false ? "<span class='res_url'><a target='_blank' href='" . $sim_items[$i - 1]->url . "'>" . $sim_items[$i - 1]->url . "</a></span>" : "-";
                    $result_row['Page_Load_Time' . $i] = $parsed_loaded_in_seconds_unserialize_val;
                    $result_row['product_name' . $i] = $sim_items[$i - 1]->product_name !== false ? "<span class='tb_product_name'>" . $sim_items[$i - 1]->product_name . "</span>" : "-";
                    $result_row['item_id' . $i] = $parsed_attributes_unserialize_val;
                    $result_row['model' . $i] = '#';
                    $result_row['short_description_wc' . $i] = $sim_items[$i - 1]->short_description_wc !== false ? $sim_items[$i - 1]->short_description_wc : '-';
                    $result_row['Short_Description' . $i] = $sim_items[$i - 1]->Short_Description !== false ? $sim_items[$i - 1]->Short_Description : '';
                    $result_row['Long_Description' . $i] = $sim_items[$i - 1]->Long_Description !== false ? $sim_items[$i - 1]->Long_Description : '';
                    $result_row['Meta_Keywords' . $i] = $parsed_meta_keywords_unserialize_val;
                    $result_row['long_description_wc' . $i] = $sim_items[$i - 1]->long_description_wc !== false ? $sim_items[$i - 1]->long_description_wc : '-';
                    $result_row['Meta_Description' . $i] = $parsed_meta_unserialize_val;
                    $result_row['Meta_Description_Count' . $i] = $parsed_meta_unserialize_val_count;
                    $result_row['average_review' . $i] = $parsed_average_review_unserialize_val;


                }

                 $result_row = (object) $result_row;

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
            if ($row->Page_Load_Time1) {
                $result_row->Page_Load_Time1 = $row->Page_Load_Time1;
            }
            if ($row->average_review1) {
                $result_row->average_review1 = $row->average_review1;
            }
            if ($row->Short_Description1) {
                $result_row->Short_Description1 = $row->Short_Description1;
            }
            if ($row->Long_Description1) {
                $result_row->Long_Description1 = $row->Long_Description1;
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



            $pars_atr = $this->imported_data_parsed_model->getByImId($row->imported_data_id);

            if (isset($pars_atr['parsed_attributes']['cnetcontent']) && (isset($pars_atr['parsed_attributes']['webcollage'])) && $pars_atr['parsed_attributes']['cnetcontent'] == 1 && $pars_atr['parsed_attributes']['webcollage'] == 1)
                $result_row->column_external_content = 'CNET, WC';
            elseif (isset($pars_atr['parsed_attributes']['cnetcontent']) && (isset($pars_atr['parsed_attributes']['webcollage'])) && $pars_atr['parsed_attributes']['cnetcontent'] == 1 && $pars_atr['parsed_attributes']['webcollage'] != 1)
                $result_row->column_external_content = 'CNET';
            elseif (isset($pars_atr['parsed_attributes']['cnetcontent']) && (isset($pars_atr['parsed_attributes']['webcollage'])) && $pars_atr['parsed_attributes']['cnetcontent'] != 1 && $pars_atr['parsed_attributes']['webcollage'] == 1)
                $result_row->column_external_content = 'WC';
            else
                $result_row->column_external_content = ' ';
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

            if ($row->short_description) {
                 $result_row->Short_Description = $row->short_description;
             }else{
                 $result_row->Long_Description = '';
             }
             if ($row->long_description) {
                 $result_row->Long_Description = $row->long_description;
             }else{
                 $result_row->Long_Description = '';
             }

            if ($pars_atr['parsed_meta']['keywords'] && $pars_atr['parsed_meta']['keywords'] != '') {
                $Meta_Keywords = "<table class='table_keywords_long'>";
                    $cnt_meta = explode(',', $pars_atr['parsed_meta']['keywords']);
                    $cnt_meta_count = count($cnt_meta);
                    $_count_meta = 0;
                    foreach($cnt_meta as $cnt_m){
                        $cnt_m = trim($cnt_m);
                        if($result_row->Long_Description || $result_row->Short_Description){
                            $_count_meta = $this->keywords_appearence($result_row->Long_Description.$result_row->Short_Description, $cnt_m);
                            $_count_meta_num = round(($_count_meta * $cnt_meta_count / ($result_row->long_description_wc + $result_row->short_description_wc)) * 100, 2) . "%";
                            $Meta_Keywords .= "<tr><td>" . $cnt_m . "</td><td>".$_count_meta_num."</td></tr>";
//                        }else if($result_row->Short_Description){
//                            $_count_meta = $this->keywords_appearence($result_row->Short_Description, $cnt_m);
//                            $_count_meta_num = round(($_count_meta * $cnt_meta_count / $result_row->short_description_wc) * 100, 2) . "%";
//                            $Meta_Keywords .= "<tr><td>" . $cnt_m . "</td><td>".$_count_meta_num."</td></tr>";
//
                        }
                    }
                $Meta_Keywords .= "</table>";
                $result_row->Meta_Keywords = $Meta_Keywords;
            }




//            if ($pars_atr['parsed_meta']['keywords'] && $pars_atr['parsed_meta']['keywords'] != '') {
//                $Meta_Keywords = "<table class='table_keywords_long'>";
//                    $cnt_meta = explode(',', $pars_atr['parsed_meta']['keywords']);
//                    $cnt_meta_count = count($cnt_meta);
//                    foreach($cnt_meta as $cnt_m){
//                        $cnt_m = trim($cnt_m);
//                        $_count_meta = $this->keywords_appearence($result_row->Meta_Description, $cnt_m);
//                        $_count_meta_num = round(($_count_meta * $cnt_meta_count / $result_row->Meta_Description_Count) * 100, 2) . "%";
//                        $Meta_Keywords .= "<tr><td>" . $cnt_m . "</td><td>".$_count_meta_num."</td></tr>";
//                    }
//                $Meta_Keywords .= "</table>";
//                $result_row->Meta_Keywords = $Meta_Keywords;
//            }



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
            if (isset($custom_seo['primary'])) {
                if ($row->long_description) {
                    $_count = $this->keywords_appearence($row->long_description, $custom_seo['primary']);
                    $cnt = count(explode(' ', $custom_seo['primary']));
                    $_count = round(($_count * $cnt / $row->long_description_wc) * 100, 2) . "%";
                    $Custom_Keywords_Long_Description .= "<tr><td>" . $custom_seo['primary'] . "</td><td>$_count</td></tr>";
                } else {
                    $_count = ' ';
                }
            };
            if (isset($custom_seo['secondary'])) {
                if ($row->long_description) {
                    $_count = $this->keywords_appearence($row->long_description, $custom_seo['secondary']);
                    $cnt = count(explode(' ', $custom_seo['secondary']));
                    $_count = round(($_count * $cnt / $row->long_description_wc) * 100, 2) . "%";
                    $Custom_Keywords_Long_Description .= "<tr><td>" . $custom_seo['secondary'] . "</td><td>$_count</td></tr>";
                } else {
                    $_count = ' ';
                }
            };
            if (isset($custom_seo['tertiary'])) {
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

//gap analises
          if ($build_assess_params->max_similar_item_count > 0) {
                //$class_for_all_case = "class_for_all_case";
                $sim_items = $row->similar_items;
//                if($result_row->short_description_wc && isset($sim_items[1]) && $sim_items[1]->short_description_wc && $result_row->short_description_wc <$sim_items[1]->short_description_wc){
//                        $result_row->gap.="Lower words count in short description<br>";
//                }
//                if($result_row->long_description_wc && isset($sim_items[1]) && $sim_items[1]->long_description_wc && $result_row->long_description_wc <$sim_items[1]->long_description_wc){
//                    $result_row->gap.="Lower words count in long description<br>";
//                }

                if(isset($sim_items[$i -1]) && $sim_items[$i -1]->long_description_wc &&  $sim_items[$i -1]->short_description_wc && ($sim_items[$i -1]->short_description_wc+$sim_items[$i -1]->long_description_wc)<100){
                                $totoal = $sim_items[$i -1]->short_description_wc+$sim_items[$i -1]->long_description_wc;
                                $result_row->gap.="Competitor total product description length only $totoal words<br>";
                }
                
                
                if($result_row->column_features && $f_count1 && $f_count1 < $result_row->column_features){
                    $result_row->gap.="Competitor has fewer features listed<br>";
                }
          }





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

            $result_row->competitors_prices = @unserialize($row->competitors_prices);

            if (property_exists($row, 'include_in_assess_report') && intval($row->include_in_assess_report) > 0) {
                $detail_comparisons_total += 1;
            }

            if ($this->settings['statistics_table'] == "statistics_new") {

            	if (strpos($row->short_seo_phrases, 'a:')) {
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

                if (strpos($row->long_seo_phrases, 'a:')) {
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

                if ($c >= $display_start) {

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
                        '<span style="cursor:pointer;">' . $snap . '</span>',
                        $row_created,
                        '<span class= "' . $tb_product_name . '">' . $data_row->product_name . "</span>",
                        $data_row->item_id,
                        $data_row->model,
                        $row_url,
                        $data_row->Page_Load_Time,
                        $data_row->Short_Description,
                        $data_row->short_description_wc,
                        $data_row->Meta_Keywords,
                        $data_row->short_seo_phrases,
                        $data_row->Long_Description,
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
                        $data_row->average_review,
                        $data_row->column_features,
                        $data_row->price_diff,
                        $recommendations_html,
                        json_encode($data_row)
                    );

                    if ($build_assess_params->max_similar_item_count > 0) {
                        $data_row = (array) $data_row;
                        for ($i = 1; $i <= $build_assess_params->max_similar_item_count; $i++) {
                            $output_row[] = $data_row['snap' . $i] != null ? $data_row['snap' . $i] : '-';
                            $output_row[] = $data_row['product_name' . $i] != null ? $data_row['product_name' . $i] : '-';
                            $output_row[] = $data_row['item_id' . $i] != null ? $data_row['item_id' . $i] : '';
                            $output_row[] = $data_row['model' . $i] != null ? $data_row['model' . $i] : '';
                            $output_row[] = $data_row['url' . $i] != null ? $data_row['url' . $i] : '-';
                            $output_row[] = $data_row['Page_Load_Time' . $i] != null ? $data_row['Page_Load_Time' . $i] : '';
                            $output_row[] = $data_row['Short_Description' . $i] != null ? $data_row['Short_Description' . $i] : '';
                            $output_row[] = $data_row['short_description_wc' . $i] != null ? $data_row['short_description_wc' . $i] : '-';
                            $output_row[] = $data_row['Meta_Keywords' . $i] != null ? $data_row['Meta_Keywords' . $i] : '';
                            $output_row[] = $data_row['Long_Description' . $i] != null ? $data_row['Long_Description' . $i] : '';
                            $output_row[] = $data_row['long_description_wc' . $i] != null ? $data_row['long_description_wc' . $i] : '-';
                            $output_row[] = $data_row['Meta_Description' . $i] != null ? $data_row['Meta_Description' . $i] : '';
                            $output_row[] = $data_row['Meta_Description_Count' . $i] != null ? $data_row['Meta_Description_Count' . $i] : '';
                            $output_row[] = $data_row['average_review' . $i] != null ? $data_row['average_review' . $i] : '';


                        }

                       $output_row[] = $data_row['gap'];

                        $data_row = (object) $data_row;
                    } else {
                        $output_row[] = $data_row->gap;
                        $output_row[] = $data_row->snap1;
                        $output_row[] = $data_row->product_name1;
                        $output_row[] = $data_row->item_id1;
                        $output_row[] = $data_row->model1;
                        $output_row[] = $data_row->url1;
                        $output_row[] = $data_row->Page_Load_Time1;
                        $output_row[] = $data_row->Short_Description1;
                        $output_row[] = $data_row->short_description_wc1;
                        $output_row[] = $data_row->Meta_Keywords1;
                        $output_row[] = $data_row->Long_Description1;
                        $output_row[] = $data_row->long_description_wc1;
                        $output_row[] = $data_row->Meta_Description1;
                        $output_row[] = $data_row->Meta_Description_Count1;
                        $output_row[] = $data_row->average_review1;
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
        $output['columns'] = $columns;
        $output['ExtraData']['report'] = $report;

        return $output;
    }

    public function get_board_view_snap() {
        if (isset($_POST['batch_id']) && $_POST['batch_id'] != 0) {
            $batch_id = $_POST['batch_id'];
            $params = new stdClass();
            $params->batch_id = $batch_id;
            $params->txt_filter = '';
            $params->date_from = '';
            $params->date_to = '';
            if (isset($_POST['next_id']))
                $params->id = $_POST['next_id'];
            else
                $params->snap_count = 12;
            $results = $this->get_data_for_assess($params);
            /*             * **Foreach Begin*** */
            $snap_data = array();
            foreach ($results as $data_row) {
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

        if (isset($_POST['batch_id']) && isset($_POST['batch_compare_id'])) {
            if (trim($_POST['batch_id']) == '')
                $batch_id = -1;
            else
                $batch_id = $_POST['batch_id'];

            if (trim($_POST['batch_compare_id']) == '' || $_POST['batch_compare_id'] == 'All')
                $batch_compare_id = -1;
            else
                $batch_compare_id = $_POST['batch_compare_id'];

            $batch_arr = array($batch_id, $batch_compare_id);
            $snap_data = array();
            foreach ($batch_arr as $key => $batchID) {
                $params = new stdClass();
                $params->batch_id = $batchID;
                $params->txt_filter = '';
                $params->date_from = '';
                $params->date_to = '';
                $results = $this->get_data_for_assess($params);


                foreach ($results as $data_row) {
                    $snap_data[$key]['product_name'][] = (string) $data_row->product_name;
                    $snap_data[$key]['url'][] = (string) $data_row->url;
                    $snap_data[$key]['short_description_wc'][] = (int) $data_row->short_description_wc;
                    $snap_data[$key]['long_description_wc'][] = (int) $data_row->long_description_wc;
                    $snap_data[$key]['revision'][] = (int) $data_row->revision;
                    $snap_data[$key]['own_price'][] = (float) $data_row->own_price;
                    $parsed_attributes_feature = unserialize($data_row->parsed_attributes);
                    if($parsed_attributes_feature['feature_count']){
                        $snap_data[$key]['Features'][] = (int) $parsed_attributes_feature['feature_count'];
                    }else{
                        $snap_data[$key]['Features'][] = 0;
                    }
                    $htags = unserialize($data_row->htags);
                    if ($htags) {
                    	if (isset($htags['h1'])) {
                        	$snap_data[$key]['h1_word_counts'][] = count($htags['h1']);
                    	} else {
                    		$snap_data[$key]['h1_word_counts'][] = 0;
                    	}
                    	if (isset($htags['h2'])) {
                        	$snap_data[$key]['h2_word_counts'][] = count($htags['h2']);
                    	} else {
                    		$snap_data[$key]['h2_word_counts'][] = 0;
                    	}
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

        $desc = strip_tags($desc);
        return substr_count($desc, $phrase);
    }

    private function column_external_content($cnetcontent = false, $webcollage = false) {
        $column_external_content = ' ';
        if ($cnetcontent == 1 && $webcollage == 1)
            $column_external_content = 'CNET, WC';
        elseif ($cnetcontent == 1 && $webcollage != 1)
            $column_external_content = 'CNET';
        elseif ($cnetcontent != 1 && $webcollage == 1)
            $column_external_content = 'WC';
        return $column_external_content;
    }

    private function costom_keywords_den($imported_data_id, $description, $description_wc){
        $custom_seo = $this->keywords_model->get_by_imp_id($imported_data_id);
            $key_den= 0;
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
                     $key_den  = round(($_count * $cnt / $description_wc) * 100, 2);

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

    private function custom_keywords($imported_data_id, $long_description, $long_description_wc, $short_description, $short_description_wc){

            $custom_seo = $this->keywords_model->get_by_imp_id($imported_data_id);
            $Custom_Keywords_Long_Description = '';
            if ($custom_seo['primary']) {
                if ($long_description) {
                    $_count = $this->keywords_appearence($long_description, $custom_seo['primary']);
                    $cnt = count(explode(' ', $custom_seo['primary']));
                    $_count = round(($_count * $cnt / $long_description_wc) * 100, 2) . "%";
                    $Custom_Keywords_Long_Description .=  $custom_seo['primary'] . "</td><td>$_count  \r\n";
                } else {
                    $_count = ' ';
                }
            };
            if ($custom_seo['secondary']) {
                if ($long_description) {
                    $_count = $this->keywords_appearence($long_description, $custom_seo['secondary']);
                    $cnt = count(explode(' ', $custom_seo['secondary']));
                    $_count = round(($_count * $cnt / $long_description_wc) * 100, 2) . "%";
                    $Custom_Keywords_Long_Description .=  $custom_seo['secondary'] . " - $_count  \r\n";
                } else {
                    $_count = ' ';
                }
            };
            if ($custom_seo['tertiary']) {
                if ($long_description) {
                    $_count = $this->keywords_appearence($long_description, $custom_seo['tertiary']);
                    $cnt = count(explode(' ', $custom_seo['tertiary']));
                    $_count = round(($_count * $cnt / $long_description_wc) * 100, 2) . "%";
                    $Custom_Keywords_Long_Description .=  $custom_seo['tertiary'] . " - $_count  \r\n";
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

            return array("Custom_Keywords_Long" =>$Custom_Keywords_Long_Description, "Custom_Keywords_Short" =>$Custom_Keywords_Short_Description);
    }

//}










private function export_assess_data_for_sim($imported_data_id, $selected_columns, $i_of_cmp) {


        $this->load->model('statistics_new_model');
        if (($key = array_search('snap', $selected_columns)) !== false) {
            unset($selected_columns[$key]);
        }
       
        $qnid = " WHERE `s`.`imported_data_id` = ".$imported_data_id;
        $query = $this->db->query('select `s`.*,
            (select `value` from imported_data_parsed where `key`="Product Name" and `imported_data_id` = `s`.`imported_data_id` limit 1) as `product_name`,
            (select `value` from imported_data_parsed where `key`="Description" and `imported_data_id` = `s`.`imported_data_id` limit 1) as `Short_Description`,
            (select `value` from imported_data_parsed where `key`="Long_Description" and `imported_data_id` = `s`.`imported_data_id` limit 1) as `Long_Description`,
            (select `value` from imported_data_parsed where `key`="Url" and `imported_data_id` = `s`.`imported_data_id`  limit 1) as `url`
            from `statistics_new` as `s` ' . $qnid);
       $results = $query->result();
       
        $this->load->model('batches_model');
        $res_array = array();
        $H1_tag_count = 0;
        $H2_tag_count = 0;
 
        foreach ($results as $key => $row) {
            //item_id
            if(in_array('item_id', $selected_columns)){
                $res_array[$key]['item_id'] = $pars_atr['parsed_attributes']['item_id']?$pars_atr['parsed_attributes']['item_id']:'';
            }
            //model
            if(in_array('model', $selected_columns)){
                $res_array[$key]['model'] = $pars_atr['parsed_attributes']['model']?$pars_atr['parsed_attributes']['model']:'';
            }
            $row = (array) $row;
            foreach ($line as $k => $v) {
                $res_array[$key][$k] = $row[$k];
            }
            $row = (object) $row;

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
            //meta keywords
                
            if(in_array('Meta_Keywords', $selected_columns)){
                if ($pars_atr['parsed_meta']['keywords']) {

                    $cnt_meta_un = explode(',', $pars_atr['parsed_meta']['keywords']);
                    $cnt_meta_count_un = count($cnt_meta_un);
                    foreach($cnt_meta_un as $cnt_m_un){
                        $_count_meta_un = 0;
                        $cnt_m_un = trim($cnt_m_un);
                        if($row->Long_Description || $row->Short_Description){
                            $_count_meta_un = $this->keywords_appearence($row->Long_Description.$row->Short_Description, $cnt_m_un);
                            $_count_meta_num_un = round(($_count_meta_un * $cnt_meta_count_un / ($sim_items[$i - 1]->long_description_wc + $sim_items[$i - 1]->short_description_wc)) * 100, 2) . "%";
                            $Meta_Keywords_un .=  $cnt_m_un.  " ".$_count_meta_num_un.", ";
                        if($i==1 && !$meta_key_gap ){
                            $metta_prc= round(($_count_meta_un * $cnt_meta_count_un / ($row->long_description_wc + $row->short_description_wc)) * 100, 2);
                            if($metta_prc >= 2)
                            $meta_key_gap=$metta_prc;
                        }
                        }


                    } 
                    $parsed_meta_keywords_unserialize_val = $Meta_Keywords_un;

                    }
                
                
                $res_array[$key]['meta_keywords'] = $parsed_meta_keywords_unserialize_val ? $parsed_meta_keywords_unserialize_val:'';
            }

            //meta description
            if(in_array('Meta_Description', $selected_columns)){
                if ($pars_atr['parsed_meta']['description'] && $pars_atr['parsed_meta']['description'] != '') {
                    $res_array[$key]['meta_description']=$pars_atr['parsed_meta']['description'];
                    $words_des = count(explode(" ", $pars_atr['parsed_meta']['description']));
                    $res_array[$key]['Meta_Description_Count'] = $words_des;
                } else if ($pars_atr['parsed_meta']['Description'] && $pars_atr['parsed_meta']['Description'] != '') {
                    $res_array[$key]['meta_description']=$pars_atr['parsed_meta']['Description'];
                    $words_des = count(explode(" ", $pars_atr['parsed_meta']['Description']));
                    $res_array[$key]['Meta_Description_Count'] = $words_des;
                }
            }

            //custom keywords

            if(in_array('Custom_Keywords_Short_Description',$selected_columns) || in_array('Custom_Keywords_Long_Description',$selected_columns)){
                $custom_keywords= $this->custom_keywords($row->imported_data_id, $row->Long_Description,$row->long_description_wc, $row->Short_Description,$row->short_description_wc);
                 if(in_array('Custom_Keywords_Short_Description',$selected_columns)){
                     $res_array[$key]['Custom_Keywords_Short_Description']= $custom_keywords['Custom_Keywords_Short'];
                 }
                 if(in_array('Custom_Keywords_Long_Description',$selected_columns)){
                     $res_array[$key]['Custom_Keywords_Long_Description']= $custom_keywords['Custom_Keywords_Long'];
                 }
            }
            //loaded_in_seconds
            if(in_array('Page_Load_Time', $selected_columns)){
                $res_array[$key]['Page_Load_Time'] = $pars_atr['parsed_attributes']['loaded_in_seconds']!==false?$pars_atr['parsed_attributes']['loaded_in_seconds']:'';
            }
            if(in_array('column_external_content', $selected_columns)){
               $res_array[$key]['column_external_content']= $this->column_external_content($pars_atr['parsed_attributes']['cnetcontent'],$pars_atr['parsed_attributes']['webcollage']);
            }
            if (in_array('column_features', $selected_columns)) {
                $res_array[$key]['column_features'] = $pars_atr['parsed_attributes']['feature_count'] !== false ? $pars_atr['parsed_attributes']['feature_count'] : '';
            }
            if (in_array('column_reviews', $selected_columns)) {
                $res_array[$key]['column_reviews'] = $row->revision !== false ? $row->revision : '';
            }
            if (in_array('H1_Tags', $selected_columns) && $pars_atr['HTags']['h1'] && $pars_atr['HTags']['h1'] != '') {
                $H1 = $pars_atr['HTags']['h1'];
                if (is_array($H1)) {

                    $i=0;
                    foreach ($H1 as $k => $h1) {
                        if($i<2){
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
                    if ($H1_tag_count > 2){
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

                    if (count($H2) > $H2_tag_count) {
                        $H2_tag_count = count($H2);
                    }
                    $i=0;
                    foreach ($H2 as $k => $h2) {
                        if($i<2){
                            $res_array[$key]['H2_Tags' . $k] = $h2;
                            $res_array[$key]['H2_Tags_Count' . $k] = strlen($h2);
                            $i++;
                        }
                    }
                } else {
                    $res_array[$key]['H2_Tags0'] = $H2;
                    $res_array[$key]['H2_Tags_Count0'] = strlen($H2);
                    if ($H2_tag_count == 0) {
                        $H2_tag_count = 1;
                    }
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


            $price_diff = unserialize($res_array[$key]['price_diff']);
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
                $res_array[$key]['price_diff'] = $price_diff_res;
            } else {
                $res_array[$key]['price_diff'] = '';
            }
        }


            if(in_array('model', $selected_columns)){
            array_unshift( $line, 'Model');
            }
            if(in_array('item_id', $selected_columns)){
                 array_unshift( $line, 'item ID');
            }
            if(in_array('Meta_Keywords', $selected_columns)){
                 $line[]=  'Meta Keywords';
            }

            //meta description
            if(in_array('Meta_Description', $selected_columns)){
                $line[]=  'Meta Description';
                $line[]=  'Meta Desc Words';
            }
            if(in_array('Custom_Keywords_Short_Description',$selected_columns)){
                $line[]= 'Custom Keywords - Short Description';
            }
            if(in_array('Custom_Keywords_Long_Description',$selected_columns)){
                $line[]= 'Custom Keywords - Long Description';
            }
            if(in_array('Page_Load_Time', $selected_columns)){
                $line[]=  'Page Load Time';
            }
            if(in_array('column_external_content', $selected_columns)){
               $line[]= 'External Content';
            }
            if (in_array('column_features', $selected_columns)) {
                $res_array[$key]['column_features'] = $pars_atr['parsed_attributes']['feature_count'] !== false ? $pars_atr['parsed_attributes']['feature_count'] : '';
            }
            if (in_array('column_reviews', $selected_columns)) {
                $res_array[$key]['column_reviews'] = $row->revision !== false ? $row->revision : '';
           }

            if (in_array('H2_Tags', $selected_columns)) {
                if ($H1_tag_count > 0) {
                    for ($k = 1; $k <= $H1_tag_count; $k++) {
                        $line[] = "H1_tag ($k) ";
                        $line[] = "Chars ($k)";
                    }
                }
                if ($H2_tag_count > 0) {
                    for ($k = 1; $k <= $H2_tag_count; $k++) {
                        $line[] = "H2_tag ($k) ";
                        $line[] = "Chars ($k)";
                    }
                }
            }

        array_unshift($res_array, $line);
        $this->load->helper('csv');
        foreach ($res_array as $key1 => $value1) {
            foreach ($value1 as $k1 => $v1){
                $res_array[$key1][$k1.''.$i_of_cmp] = $res_array[$key1][$k1];
                unset($res_array[$key1][$k1]);
            }
        }
        return $res_array;
//        array_to_csv($res_array, $batch_name."(".date("Y-m-d H:i") . ').csv');

    }

}
