<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Research extends MY_Controller {

    function __construct()
    {
        parent::__construct();

        $this->load->library('form_validation');
        $this->load->library('helpers');
        $this->data['title'] = 'Research & Edit';

        if (!$this->ion_auth->logged_in())
        {
            //redirect them to the login page
            redirect('auth/login', 'refresh');
        }
    }

    public function index()
    {
        // test comment - testing out pull
        $this->data['customer_list'] = $this->getCustomersByUserId();
        $this->data['category_list'] = $this->category_list();
        if(!empty($this->data['customer_list'])){
             $this->data['batches_list'] = $this->batches_list();
        }

        $this->render();
    }

    public function category_list()
    {
        $this->load->model('category_model');
        $categories = $this->category_model->getAll();
        $category_list = array();
        foreach($categories as $category){
            array_push($category_list, $category->name);
        }
        return $category_list;
    }

    public function batches_list()
    {
        $this->load->model('batches_model');
        $batches = $this->batches_model->getAll();
        $batches_list = array();
        foreach($batches as $batch){
            array_push($batches_list, $batch->title);
        }
        return $batches_list;
    }

    public function search_results()
    {
        $this->load->model('imported_data_parsed_model');
        $this->load->model('category_model');

        if($this->input->post('search_data') != '') {

            $category_id = '';
            $limit = '';
            if($this->input->post('category') != '' && $this->input->post('category') != 'All categories'){
                $category_id = $this->category_model->getIdByName($this->input->post('category'));
            }
            if($this->input->post('limit')!=''){
                $limit = $this->input->post('limit');
            }

            $imported_data_parsed = $this->imported_data_parsed_model->getData($this->input->post('search_data'), $this->input->post('website'), $category_id, $limit);
            if (empty($imported_data_parsed)) {
            	$this->load->library('PageProcessor');
				if ($this->pageprocessor->isURL($this->input->post('search_data'))) {
					$parsed_data = $this->pageprocessor->get_data($this->input->post('search_data'));
					$imported_data_parsed[0] = $parsed_data;
					$imported_data_parsed[0]['url'] = $this->input->post('search_data');
					$imported_data_parsed[0]['imported_data_id'] = 0;
				}
            }
            $this->output->set_content_type('application/json')
                ->set_output(json_encode($imported_data_parsed));
        }
    }

    public function search_results_bathes()
    {
        $this->load->model('imported_data_parsed_model');
        $this->load->model('category_model');

        //$search_data = $this->input->post('search_data');

        $category_id = '';
        $website = $this->input->post('website');
        $category = $this->input->post('category');
        if(!empty($category) && $category != 'All categories'){
            $category_id = $this->category_model->getIdByName($category);
        }

        //$imported_data_parsed = $this->imported_data_parsed_model->getDataWithPaging($search_data, $website, $category_id);
        $research_data = $this->imported_data_parsed_model->getResearchDataWithPaging();

        if(!empty($research_data['total_rows'])) {
            $total_rows = $research_data['total_rows'];
        } else {
            $total_rows = 0;
        }

        $echo = intval($this->input->get('sEcho'));
        $output = array(
            "sEcho"                     => $echo,
            "iTotalRecords"             => $total_rows,
            "iTotalDisplayRecords"      => $total_rows,
            "iDisplayLength"            => $research_data['display_length'],
            "aaData"                    => array()
        );

        if(!empty($research_data)) {
            $count = $research_data['display_start'];
            foreach($research_data['result'] as $research_data_row) {
                $count++;
                $output['aaData'][] = array(
                    $count,
                    $research_data_row->product_name,
                    $research_data_row->url,
                    $research_data_row->batch_id,
                );
            }
        }

        $this->output->set_content_type('application/json')
            ->set_output(json_encode($output));
    }

    public function getResearchDataByURLandBatchId() {
        $params = new stdClass();
        $params->batch_id = intval($this->input->get('batch_id'));
        $params->url = $this->input->get('url');

        $this->load->model('imported_data_parsed_model');
        $research_data = $this->imported_data_parsed_model->getResearchDataByURLandBatchId($params);
        $this->output->set_content_type('application/json')
            ->set_output(json_encode($research_data));
    }

    public function getBatchInfo(){
        $this->load->model('batches_model');
        $this->load->model('research_data_model');
        $this->load->model('statistics_model');
        $batch_id = $this->input->post('batch_id');
        if($batch_id != false){
            $batch_info = $this->batches_model->get($batch_id);
            $last_date = $this->research_data_model->getLastAddedDateItem($batch_id);
            $result = array();
            $result['created'] = mdate('%m/%d/%Y',strtotime($batch_info[0]->created));
            $result['modified'] = mdate('%m/%d/%Y',strtotime($last_date[0]->modified));

            $params = new stdClass();
            $params->batch_id = $batch_id;
            $params->txt_filter = '';
            $res = $this->statistics_model->getStatsData($params);
            $num_rows = count($res);
            if($num_rows == 0){
                $num_rows = $this->research_data_model->countAll($batch_id);
            }
            $result['count_items'] =  $num_rows;

            $this->output->set_content_type('application/json')
                ->set_output(json_encode($result));
        }
    }

    public function addToBatch(){
        $this->load->model('batches_model');
        $batch_id = $this->batches_model->getIdByName($this->input->post('batch'));
        if($batch_id != false){
            $lines = explode("\n", $this->input->post('urls'));
            $response['batch_id'] = $batch_id;
            if($this->insert_rows($batch_id, $lines)){
                $response['message'] = 'Items were added successfully';
            } else {
                $response['message'] = 'error';
            }
            $this->output->set_content_type('application/json')
                ->set_output(json_encode($response));
        }
    }

    public function research_batches(){
        $this->load->model('settings_model');
        $this->data['customer_list'] = $this->getCustomersByUserId();
        if(!empty($this->data['customer_list'])){
            $this->data['batches_list'] = $this->batches_list();
        }
		$user_id = $this->ion_auth->get_user_id();
        $key = 'research_review';

        $columns = $this->settings_model->get_value($user_id, $key);

        // if columns empty set default values for columns
        if(empty($columns)) {
            $columns = array (
                'editor'                        => 'true',
                'product_name'                  => 'true',
                'url'                           => 'true',
                'short_description'             => 'true',
                'short_description_wc'          => 'false',
                'long_description'              => 'true',
                'long_description_wc'           => 'false',
                'actions'                       => 'true',
            );
        }
        $this->data['columns'] = $columns;
        $this->render();
    }

    public function research_reports(){
        $this->render();
    }

    public function new_batch()
    {
        $this->load->model('customers_model');
        $this->load->model('batches_model');
        if($this->input->post('batch')!=''){
            $batch = $this->input->post('batch');
            $customer_id = '';
            if($this->input->post('customer_name') != 'Customer'){
                $customer_id = $this->customers_model->getIdByName($this->input->post('customer_name'));
            }
            $batch_id = $this->batches_model->getIdByName($batch);
            if($batch_id == false) {
                $batch_id = $this->batches_model->insert($batch, $customer_id);
            }
        }
        $response['batch_id'] = $batch_id;
        $this->output->set_content_type('application/json')
            ->set_output(json_encode($response));
    }

    public function research_assess(){
        $this->data['customer_list'] = $this->getCustomersByUserId();
        $this->data['category_list'] = $this->category_list();
        if(!empty($this->data['customer_list'])){
            $this->data['batches_list'] = $this->batches_list();
        }

        $user_id = $this->ion_auth->get_user_id();
        $key = 'research_assess';
        $columns = $this->settings_model->get_value($user_id, $key);

        // if columns empty set default values for columns
        if(empty($columns)) {
            $columns = array (
                'created'                       => 'true',
                'product_name'                  => 'true',
                'url'                           => 'true',
                'short_description_wc'          => 'true',
                'short_seo_phrases'             => 'true',
                'long_description_wc'           => 'true',
                'long_seo_phrases'              => 'true',
                'duplicate_content'             => 'true',
                'price_diff'                    => 'true',
            );
        }
        $this->data['columns'] = $columns;

        $this->render();
    }

    public function get_assess_info(){
        $txt_filter = '';
        if($this->input->get('search_text') != ''){
            $txt_filter = $this->input->get('search_text');
        }

        $batch_id = $this->input->get('batch_id');
        $compare_batch_id = $this->input->get('compare_batch_id');

        if($batch_id == ''){
            $output = array(
                "sEcho"                     => 1,
                "iTotalRecords"             => 0,
                "iTotalDisplayRecords"      => 0,
                "iDisplayLength"            => 10,
                "aaData"                    => array()
            );

            $this->output->set_content_type('application/json')
                ->set_output(json_encode($output));
        } else {
            $build_assess_params = new stdClass();
            $build_assess_params->date_from = $this->input->get('date_from') == 'undefined' ? '' : $this->input->get('date_from');
            $build_assess_params->date_to = $this->input->get('date_to') == 'undefined' ? '' : $this->input->get('date_to');
            $build_assess_params->price_diff = $this->input->get('price_diff') == 'undefined' ? -1 :$this->input->get('price_diff');

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

            $results = $this->get_data_for_assess($params);

            $output = $this->build_asses_table($results, $build_assess_params, $batch_id);

            $this->output->set_content_type('application/json')
                ->set_output(json_encode($output));
        }
    }

    private function get_data_for_assess($params) {
        $this->load->model('settings_model');
        $this->load->model('statistics_model');
        $this->load->model('statistics_new_model');

        if($this->settings['statistics_table'] == "statistics_new"){
            $results = $this->statistics_new_model->getStatsData($params);
        } else {
            $results = $this->statistics_model->getStatsData($params);
        }
        //$results = $this->statistics_model->getStatsData($params);
        //$this->load->model('research_data_model');
        //$results = $this->research_data_model->getInfoForAssess($params);
        return $results;
    }

    private function build_asses_table($results, $build_assess_params, $batch_id='') {
        $duplicate_content_range = 25;
        $this->load->model('batches_model');
        $this->load->model('imported_data_parsed_model');
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

        foreach($results as $row) {
//            $long_description_wc = $row->long_description_wc;
//            $short_description_wc = $row->short_description_wc;

            $result_row = new stdClass();
            $result_row->id = $row->id;
            $result_row->imported_data_id = $row->imported_data_id;
            $result_row->research_data_id = $row->research_data_id;
            $result_row->created = $row->created;
            $result_row->product_name = $row->product_name;
            $result_row->url = $row->url;
            $result_row->short_description = $row->short_description;
            $result_row->long_description = $row->long_description;
            $result_row->short_description_wc = intval($row->short_description_wc);
            $result_row->long_description_wc = intval($row->long_description_wc);
            $result_row->short_seo_phrases = "None";
            $result_row->long_seo_phrases = "None";
            $result_row->price_diff = "-";
            $result_row->duplicate_content = "-";
            $result_row->own_price = floatval($row->own_price);
            $price_diff = unserialize($row->price_diff);
            $result_row->lower_price_exist = false;
            $result_row->snap = '';
            if ($row->snap != null && $row->snap != ''){
                $result_row->snap = $row->snap;
            }

            if (floatval($row->own_price) <> false) {
                $own_site = parse_url($row->url, PHP_URL_HOST);
                $own_site = str_replace('www.', '', $own_site);
                $own_site = str_replace('www1.', '', $own_site);
                $result_row->price_diff = "<nobr>".$own_site." - $".$row->own_price."</nobr><br />";
            }

            if(count($price_diff) > 1){
                $own_price = floatval($price_diff['own_price']);
                $own_site = str_replace('www.', '', $price_diff['own_site']);
                $own_site = str_replace('www1.', '', $own_site);
                $price_diff_res = "<nobr>".$own_site." - $".$price_diff['own_price']."</nobr><br />";
                $flag_competitor = false;
                for($i=0; $i<count($price_diff['competitor_customer']); $i++){
                    if($customer_url["host"] != $price_diff['competitor_customer'][$i]){
                        if ($own_price > floatval($price_diff['competitor_price'][$i])) {
                            $result_row->lower_price_exist = true;
                            if ($build_assess_params->price_diff == true) {
                                $competitor_site = str_replace('www.', '', $price_diff['competitor_customer'][$i]);
                                $competitor_site = str_replace('www.', '', $competitor_site);
                                $price_diff_res .= "<input type='hidden'><nobr>".$competitor_site." - $".$price_diff['competitor_price'][$i]."</nobr><br />";
                            }
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

            if($this->settings['statistics_table'] == "statistics_new"){
                $short_seo = unserialize($row->short_seo_phrases);
                if($short_seo){
                    $str_short_seo = '';
                    foreach($short_seo as $val){
                        $str_short_seo .= $val['ph'].', ';
                    }
                    $str_short_seo = substr($str_short_seo, 0, -2);
                    $result_row->short_seo_phrases = $str_short_seo;
                }
                $long_seo = unserialize($row->long_seo_phrases);
                if($long_seo){
                    $str_long_seo = '';
                    foreach($long_seo as $val){
                        $str_long_seo .= $val['ph'].', ';
                    }
                    $str_long_seo = substr($str_long_seo, 0, -2);
                    $result_row->long_seo_phrases = $str_long_seo;
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
                       if($customer_url['host'] == $vs->customer){
                           $short_percent = 0;
                           $long_percent = 0;
                           if ($build_assess_params->short_duplicate_content) {
                               $duplicate_short_percent_total = 100 - round($vs->short_original, 1);
                               $short_percent = 100 - round($vs->short_original, 1);
                               if($short_percent > 0){
                                   //$duplicate_customers_short = '<nobr>'.$vs->customer.' - '.$short_percent.'%</nobr><br />';
                                   $duplicate_customers_short = '<nobr>'.$short_percent.'%</nobr><br />';
                               }
                           }
                           if ($build_assess_params->long_duplicate_content) {
                               $duplicate_long_percent_total = 100 - round($vs->long_original, 1);
                               $long_percent = 100 - round($vs->long_original, 1);
                               if($long_percent > 0){
                                   $duplicate_customers_long = '<nobr>'.$vs->customer.' - '.$long_percent.'%</nobr><br />';
                               }
                           }
                       }
                   }
                   if($duplicate_short_percent_total >= 20 || $duplicate_long_percent_total >= 20){
                       $items_have_more_than_20_percent_duplicate_content += 1;
                   }
                   if($duplicate_customers_short !=''){
                       $duplicate_customers = 'Duplicate short<br />'.$duplicate_customers_short;
                   }
                   if($duplicate_customers_long!=''){
                       $duplicate_customers = $duplicate_customers.'Duplicate long<br />'.$duplicate_customers_long;
                   }

                   if ($duplicate_short_percent_total > $duplicate_content_range || $duplicate_long_percent_total > $duplicate_content_range) {
                       $duplicate_customers = "<input type='hidden'/>".$duplicate_customers;
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
                $result_row->long_description_wc <= $build_assess_params->long_less)
                && ($build_assess_params->long_less_check || $build_assess_params->long_more_check)
            ){
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
        }

        if($this->settings['statistics_table'] == "statistics_new"){
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
        if (isset($build_assess_params->compare_batch_id) && $build_assess_params->compare_batch_id > 0) {
            $absent_items = $this->statistics_model->batches_compare($batch_id, $build_assess_params->compare_batch_id);

            foreach ($absent_items as $absent_item) {
                $result_row = new stdClass();
                $result_row->product_name = $absent_item['product_name'];
                $result_row->url = $absent_item['url'];
                $result_row->recommendations = $absent_item['recommendations'];
                $result_table[] = $result_row;
            }

            $own_batch = $this->batches_model->get($batch_id);
            $compare_customer = $this->batches_model->getCustomerById($build_assess_params->compare_batch_id);
            $compare_batch = $this->batches_model->get($build_assess_params->compare_batch_id);

            $compare_batch_total_items = $this->statistics_model->total_items_in_batch($build_assess_params->compare_batch_id);
            $report['summary']['own_batch_total_items'] = $own_batch_total_items;
            $report['summary']['compare_batch_total_items'] = $compare_batch_total_items;
        }

        $report['recommendations']['absent_items'] = $absent_items;
        $report['summary']['absent_items_count'] = count($absent_items);
        $report['summary']['own_batch_name'] = $own_batch[0]->title;
        $report['summary']['compare_customer_name'] = $compare_customer[0]->name;
        $report['summary']['compare_batch_name'] = $compare_batch[0]->title;

        if ($items_priced_higher_than_competitors > 0) {
            $report['recommendations']['items_priced_higher_than_competitors'] = 'Reduce pricing on '.$items_priced_higher_than_competitors.' item(s)';
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
        $config['base_url'] = $this->config->site_url().'/research/comparison_detail';
        $config['total_rows'] = $detail_comparisons_total;
        $config['per_page'] = '1';
        $config['uri_segment'] = 3;
        $this->pagination->initialize($config);
        $report['comparison_pagination'] = $this->pagination->create_links();

        if ($build_assess_params->all_columns) {
            $s_columns = explode(',', $build_assess_params->all_columns);
            $s_column_index = intval($build_assess_params->sort_columns);
            $s_column = $s_columns[$s_column_index];
            $this->sort_column = $s_column;
            $sort_direction = strtolower($build_assess_params->sort_dir);
            if ($s_column == 'price_diff') {
                if ($sort_direction == 'asc') {
                    $this->sort_direction = 'desc';
                }
                else
                    if ($sort_direction == 'desc') {
                        $this->sort_direction = 'asc';
                    }
                    else {
                        $this->sort_direction = 'asc';
                    }
            } else {
                $this->sort_direction = $sort_direction;
            }
            $this->sort_type = is_numeric($result_table[0]->$s_column) ? "num" : "";
            usort($result_table, array("Research", "assess_sort"));
        }

        $total_rows = count($result_table);
        $display_length = intval($this->input->get('iDisplayLength', TRUE));

        $display_start = intval($this->input->get('iDisplayStart', TRUE));
        if (empty($display_start)) {
            $display_start = 0;
        }

        if (empty($display_length)) {
            $display_length = $total_rows - $display_start;
        }

        $echo = intval($this->input->get('sEcho'));

        $output = array(
            "sEcho"                     => $echo,
            "iTotalRecords"             => $total_rows,
            "iTotalDisplayRecords"      => $total_rows,
            "iDisplayLength"            => $display_length,
            "aaData"                    => array()
        );

        if(!empty($result_table)) {
            $c = 0;
            foreach($result_table as $data_row) {
                if ($c >= $display_start) {
                    if (isset($data_row->recommendations)) {
                        // this is for absent product in selected batch only
                        $recommendations_html = '<ul class="assess_recommendations"><li>'.$data_row->recommendations.'</li></ul>';
                    } else {
                        $recommendations = array();

                        if($data_row->short_description_wc == 0 && $data_row->long_description_wc == 0){
                            $recommendations[] = '<li>Add product descriptions</li>';
                        }

                        if($data_row->short_description_wc > 0 && $data_row->long_description_wc == 0){
                            if($data_row->short_description_wc > 100){
                                $sd_diff = 100 - $data_row->short_description_wc;
                            } else {
                                $sd_diff = $build_assess_params->short_less - $data_row->short_description_wc;
                            }
                            if($sd_diff > 0){
                                $recommendations[] = '<li>Increase descriptions word count by '.$sd_diff.' words</li>';
                            }

                        }
                        if($data_row->long_description_wc > 0 && $data_row->short_description_wc == 0){
                            if($data_row->long_description_wc > 200){
                                $ld_diff = 200 - $data_row->long_description_wc;
                            } else {
                                $ld_diff = $build_assess_params->long_less - $data_row->long_description_wc;
                            }
                            if($ld_diff > 0){
                                $recommendations[] = '<li>Increase descriptions word count by '.$ld_diff.' words</li>';
                            }
                        }

                        if($data_row->short_description_wc > 0 && $data_row->long_description_wc != 0){
                            if($data_row->short_description_wc > 100){
                                $sd_diff = 100 - $data_row->short_description_wc;
                            } else {
                                $sd_diff = $build_assess_params->short_less - $data_row->short_description_wc;
                            }
                            if($sd_diff > 0){
                                $recommendations[] = '<li>Increase short descriptions word count by '.$sd_diff.' words</li>';
                            }
                        }
                        if($data_row->long_description_wc > 0 && $data_row->short_description_wc != 0){
                            if($data_row->long_description_wc > 200){
                                $ld_diff = 200 - $data_row->long_description_wc;
                            } else {
                                $ld_diff = $build_assess_params->long_less - $data_row->long_description_wc;
                            }
                            if($ld_diff > 0){
                                $recommendations[] = '<li>Increase long descriptions word count by '.$ld_diff.' words</li>';
                            }
                        }

                        /*if ($data_row->short_description_wc <= $build_assess_params->short_less ||
                            $data_row->long_description_wc <= $build_assess_params->long_less) {
                            $sd_diff = $build_assess_params->short_less - $data_row->short_description_wc;
                            $ld_diff = $build_assess_params->long_less - $data_row->long_description_wc;
                            $increase_wc = max($sd_diff, $ld_diff);
                            $recommendations[] = '<li>Increase descriptions word count by'.$increase_wc.' words</li>';
                        }*/

                        if ($data_row->short_seo_phrases == 'None' && $data_row->long_seo_phrases == 'None') {
                            $recommendations[] = '<li>Keyword optimize product content</li>';
                        }
                        if ($data_row->lower_price_exist == true && !empty($data_row->competitors_prices)) {
                            if (min($data_row->competitors_prices) < $data_row->own_price) {
                                $min_price_diff = $data_row->own_price - min($data_row->competitors_prices);
                                $recommendations[] = '<li>Lower price by $'.$min_price_diff.' to be competitive</li>';
                            }
                        }

                        $recommendations_html = '<ul class="assess_recommendations">'.implode('', $recommendations).'</ul>';
                    }

                    $row_created_array = explode(' ', $data_row->created);
                    $row_created = '<nobr>'.$row_created_array[0].'</nobr><br/>';
                    $row_created = $row_created.'<nobr>'.$row_created_array[1].'</nobr>';

                    $row_url = '<table class="url_table"><tr><td style="padding:5px;"><a class="active_link" href="'.$data_row->url.'" target="_blank">'.$data_row->url.'</a></td></tr>';
                    if ($data_row->snap != ''){
                        $file = realpath(BASEPATH . "../webroot/webshoots").'/'.$data_row->snap;
                        if (file_exists($file)){
                            if (filesize($file) > 1024){
                                $row_url = $row_url.'<tr style="height:1px;"><td style="text-align:right; padding: 0px;"><i class="snap_ico icon-picture" snap="'.$data_row->snap.'"></i></tr></td>';
                            }
                        }
                    }
                    $row_url = $row_url.'</table>';

                    $output['aaData'][] = array(
                        $row_created,
                        $data_row->product_name,
                        $row_url,
                        $data_row->short_description_wc,
                        $data_row->short_seo_phrases,
                        $data_row->long_description_wc,
                        $data_row->long_seo_phrases,
                        $data_row->duplicate_content,
                        $data_row->price_diff,
                        $recommendations_html,
                        json_encode($data_row),
                    );
                }
                if ($display_length > 0) {
                    if ($c >= ($display_start + $display_length - 1)) {
                        break;
                    }
                }
                $c++;
            }
        }

        $output['ExtraData']['report'] = $report;

        return $output;
    }

    private function get_report_presetted_pages($params){
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
        usort($report_pages, array("Research", "assess_sort"));

        // replace patterns (#date#, #customer name#... etc)
        foreach($report_pages as $page){
            $page_body = $page->body;
            $page_body = str_replace('#date#', $params->current_date, $page_body);
            $page_body = str_replace('#customer name#', $params->customer_name, $page_body);
            $page->body = $page_body;
        }

        $report_parts = unserialize($report[0]->parts);

        $report_params = array(
            'report_pages'=>$report_pages,
            'report_parts'=>$report_parts,
        );
        return $report_params;
    }

    public function comparison_detail(){
        $this->load->model('statistics_model');
        $batch_id = $this->input->post('batch_id');

        $comparison_data = $this->statistics_model->product_comparison($batch_id);

        $page = intval($this->uri->segment(3));
        $this->load->library('pagination');
        $config['base_url'] = $this->config->site_url().'/research/comparison_detail';
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

        $current_date = date('F j, Y');//new DateTime(date('Y-m-d H:i:s'));
        $img_path = APPPATH.".."."/webroot/img/";
        $css_path = APPPATH.".."."/webroot/css/";

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
        $price_diff = $this->input->get('price_diff') == 'undefined' ? -1 :$this->input->get('price_diff');
        $build_assess_params->price_diff = $price_diff === 'true' ? true : false;
        if (intval($compare_batch_id) > 0) {
            $build_assess_params->compare_batch_id = $compare_batch_id;
        }

        $assess_table = $this->build_asses_table($results, $build_assess_params, $params->batch_id);

        $download_report_params = new stdClass();
        $download_report_params->img_path = $img_path;
        $download_report_params->css_path = $css_path;
        $download_report_params->own_logo = $img_path."content-analytics.png";
        $download_report_params->customer_logo = $img_path.$customer->image_url;
        $download_report_params->batch_id = $params->batch_id;
        $download_report_params->batch_name = $params->batch_name;
        $download_report_params->current_date = $current_date;
        $download_report_params->report_presetted_pages = $report_presetted_pages;
        $download_report_params->report_parts = $report_parts;
        $download_report_params->assess_table = $assess_table['ExtraData']['report'];
        $download_report_params->assess_report_page_layout = $assess_report_page_layout;

        switch($type_doc) {
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
        $css_file = $download_report_params->css_path.'assess_report.css';
        $report_data = $download_report_params->assess_table;
        $assess_report_page_layout = $download_report_params->assess_report_page_layout;

        $layout = 'L';
        if (!empty($assess_report_page_layout)) {
            if ($assess_report_page_layout == 'P') {
                $layout = 'P';
            }
        }


        $this->load->library('pdf');
        $pdf = $this->pdf->load();
        $pdf = new mPDF('', 'Letter', 0, '', 10, 10, 10, 10, 8, 8);
//        $pdf->showImageErrors = true;
//        $pdf->debug = true;
        $stylesheet = file_get_contents($css_file);
        $pdf->WriteHTML($stylesheet, 1);
        $pdf->SetHTMLFooter('<span style="font-size: 8px;">Copyright © 2013 Content Solutions, Inc.</span>');

        $html = '';

        $header = '<table border=0 width=100%>';
        $header = $header.'<tr>';
        $header = $header.'<td style="text-align: left;">';
        $header = $header.'<img src="'.$download_report_params->own_logo.'" />';
        $header = $header.'</td>';
        $header = $header.'<td style="text-align: right;">';
        $header = $header.'<img src="'.$download_report_params->customer_logo.'" />';
        $header = $header.'</td>';
        $header = $header.'</tr>';
        $header = $header.'</table>';
        $header = $header.'<hr color="#C31233" height="10">';

        foreach($download_report_params->report_presetted_pages as $page){
            if ($page->order < 5000) {
                $pdf->AddPage($page->layout);
                $html = '';
                $html = $html.$header;
                $html = $html.$page->body;
                $pdf->WriteHTML($html);
            }
        }

        $pdf->AddPage($layout);
        $html = '';

        $html = $html.$header;

        $html = $html.'<table width=100% border=0>';
        $html = $html.'<tr><td style="text-align: left;font-weight: bold; font-style: italic;">Batch - '.$download_report_params->batch_name.'</td><td style="text-align: right;font-weight: bold; font-style: italic;">'.$download_report_params->current_date.'</td></tr>';
        $html = $html.'<tr><td colspan="2"><hr height="3"></td></tr>';
        $html = $html.'</table>';

        $html = $html.'<table class="report" border="1" cellspacing="0" cellpadding="0">';

        $html = $html.'<tr><td class="tableheader">Summary</td></tr>';

        //if (!empty($report_data['summary']['total_items']) && intval($report_data['summary']['total_items'] > 0)) {
            $html = $html.'<tr><td class="report_td">';
            $html = $html.'<div><img class="icon" src="'.$download_report_params->img_path.'assess_report_number.png">'.$report_data['summary']['total_items'].' total Items</div>';
            $html = $html.'</td></td></tr>';
        //}

        //if (!empty($report_data['summary']['items_priced_higher_than_competitors']) && intval($report_data['summary']['items_priced_higher_than_competitors'] > 0)) {
            $html = $html.'<tr><td class="report_td">';
            $html = $html.'<div><img class="icon" src="'.$download_report_params->img_path.'assess_report_dollar.png">'.$report_data['summary']['items_priced_higher_than_competitors'].' items priced higher than competitors</div>';
            $html = $html.'</td></tr>';
        //}

        //if (!empty($report_data['summary']['items_have_more_than_20_percent_duplicate_content']) && intval($report_data['summary']['items_have_more_than_20_percent_duplicate_content'] > 0)) {
            $html = $html.'<tr><td class="report_td">';
            $html = $html.'<div><img class="icon" src="'.$download_report_params->img_path.'assess_report_D.png">'.$report_data['summary']['items_have_more_than_20_percent_duplicate_content'].' items have more than 20% duplicate content</div>';
            $html = $html.'</td></tr>';
        //}

        //if (!empty($report_data['summary']['items_unoptimized_product_content']) && intval($report_data['summary']['items_unoptimized_product_content'] > 0)) {
            $html = $html.'<tr><td class="report_td">';
            $html = $html.'<div><img class="icon" src="'.$download_report_params->img_path.'assess_report_seo.png">'.$report_data['summary']['items_unoptimized_product_content'].' items have non-keyword optimized product content</div>';
            $html = $html.'</td></tr>';
        //}

        if ($report_data['summary']['short_wc_total_not_0'] > 0 && $report_data['summary']['long_wc_total_not_0'] > 0) {
            $html = $html.'<tr><td class="report_td">';
            $html = $html.'<div><img class="icon" src="'.$download_report_params->img_path.'assess_report_arrow_down.png">'.$report_data['summary']['items_short_products_content_short'].' items have short descriptions that are too short</div>';
            $html = $html.'</td></tr>';
            $html = $html.'<tr><td class="report_td">';
            $html = $html.'<div><img class="icon" src="'.$download_report_params->img_path.'assess_report_arrow_down.png">'.$report_data['summary']['items_long_products_content_short'].' items have long descriptions that are too short</div>';
            $html = $html.'</td></tr>';
        } else {
            $html = $html.'<tr><td class="report_td">';
            $html = $html.'<div><img class="icon" src="'.$download_report_params->img_path.'assess_report_arrow_down.png">items have descriptions that are too short</div>';
            $html = $html.'</td></tr>';
        }

        if (!empty($report_data['summary']['absent_items_count']) && intval($report_data['summary']['absent_items_count'] > 0)) {
            $html = $html.'<tr><td class="report_td">';
            $html = $html.'<div><img class="icon" src="'.$download_report_params->img_path.'assess_report_comparison.png">'.$report_data['summary']['absent_items_count'];
            $html = $html.' items in '.$report_data['summary']['compare_customer_name'].' - '.$report_data['summary']['compare_batch_name'];
            $html = $html.' are absent from '.$report_data['summary']['own_batch_name'];
            $html = $html.'</div></td></tr>';
        }

        $html = $html.'</table>';

        $html = $html.'<table class="report recommendations" border="1" cellspacing="0" cellpadding="0">';

        $html = $html.'<tr><td class="tableheader">Recommendations</td></tr>';
        if ($report_data['recommendations']['items_priced_higher_than_competitors']) {
            $html = $html.'<tr><td class="report_td">';
            $html = $html.'<div><img class="icon" src="'.$download_report_params->img_path.'assess_report_dollar.png">';
            $html = $html.$report_data['recommendations']['items_priced_higher_than_competitors'].'</div>';
            $html = $html.'</td></tr>';
        }
        if ($report_data['recommendations']['items_have_more_than_20_percent_duplicate_content']) {
            $html = $html.'<tr><td class="report_td">';
            $html = $html.'<div><img class="icon" src="'.$download_report_params->img_path.'assess_report_D.png">';
            $html = $html.$report_data['recommendations']['items_have_more_than_20_percent_duplicate_content'].'</div>';
            $html = $html.'</td></tr>';
        }
        if ($report_data['recommendations']['items_short_products_content']) {
            $html = $html.'<tr><td class="report_td">';
            $html = $html.'<div><img class="icon" src="'.$download_report_params->img_path.'assess_report_seo.png">';
            $html = $html.$report_data['recommendations']['items_short_products_content'].'</div>';
            $html = $html.'</td></tr>';
        }
        if ($report_data['recommendations']['items_unoptimized_product_content']) {
            $html = $html.'<tr><td class="report_td">';
            $html = $html.'<div><img class="icon" src="'.$download_report_params->img_path.'assess_report_arrow_up.png">';
            $html = $html.$report_data['recommendations']['items_unoptimized_product_content'].'</div>';
            $html = $html.'</td></tr>';
        }

        $html = $html.'</table>';

        $html = $html.'<tr><td>';
        $html = $html.'</table>';

        $pdf->WriteHTML($html);

        $comparison_data_array = $this->statistics_model->product_comparison($download_report_params->batch_id);
        if (count($comparison_data_array) > 0) {
            foreach ($comparison_data_array as $comparison_data) {
                $pdf->AddPage($layout);
                $data['comparison_data'] = $comparison_data;
                $comparison_details_view = $this->load->view('research/comparison_details_pdf', $data, true);
                $html = $header;
                $html = $html.'<span class="pdv_header">Product Detail View</span><br /><br />';
                $html = $html.$comparison_details_view;
                $pdf->WriteHTML($html);
            }


        }

        foreach($download_report_params->report_presetted_pages as $page){
            if ($page->order > 5000) {
                $pdf->AddPage($page->layout);
                $html = '';
                $html = $html.$header;
                $html = $html.$page->body;
                $pdf->WriteHTML($html);
            }
        }

        $pdf->Output('report.pdf', 'I');
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

    public function assess_save_columns_state() {
        $this->load->model('settings_model');
        $user_id = $this->ion_auth->get_user_id();
        $key = 'research_assess';
        $value = $this->input->post('value');
        $description = 'Page settings -> columns state';
        $res = $this->settings_model->replace($user_id, $key, $value, $description);
        echo json_encode($res);
    }

    public function change_batch_name(){
        $this->load->model('research_data_model');
        $this->load->model('batches_model');
        $batch = $this->input->post('old_batch_name');
        $batch_id = $this->batches_model->getIdByName($batch);
        if($this->batches_model->update($batch_id, $this->input->post('new_batch_name'))){
            $response['message'] = 'success';
        } else {
            $response['message'] = 'error';
        }
        $this->output->set_content_type('application/json')
            ->set_output(json_encode($response));
    }

    public function get_research_data()
    {
        $this->load->model('research_data_model');
        $this->load->model('batches_model');
        $batch = $this->input->post('batch');
        $batch_id = $this->batches_model->getIdByName($batch);
        if($batch_id == false && $batch != '') {
            $batch_id = $this->batches_model->insert($batch);
        }
        $results = $this->research_data_model->getAllByProductName($this->input->post('product_name'), $batch_id);
        $this->output->set_content_type('application/json')
            ->set_output(json_encode($results));
    }

    public function get_research_info()
    {
        $this->load->model('research_data_model');
        $this->load->model('batches_model');

        $params = new stdClass();
        $batch_name = $this->input->get('batch_name');
        $params->batch_id = $this->batches_model->getIdByName($batch_name);
        $params->filter = trim($this->input->get('search_text')).'%'.trim($this->input->get('sSearch'));
        $params->display_length = intval($this->input->get('iDisplayLength', TRUE));
        $params->display_start = intval($this->input->get('iDisplayStart', TRUE));
        if (empty($params->display_start)) {
            $params->display_start = 0;
        }
        if (empty($params->display_length)) {
            $params->display_length = 10;
        }

        $all_columns = $this->input->get('sColumns');
        $sort_columns = $this->input->get('iSortCol_0');
        $s_columns = explode(',', $all_columns);
        $s_column_index = intval($sort_columns);
        $params->sort_column = $s_columns[$s_column_index];
        $params->sort_order = $this->input->get('sSortDir_0');

        $result = $this->research_data_model->getInfoFromResearchData($params);

        $echo = intval($this->input->get('sEcho'));

        $output = array(
            "sEcho"                     => $echo,
            "iTotalRecords"             => $result->total_rows,
            "iTotalDisplayRecords"      => $result->total_rows,
            "iDisplayLength"            => $params->display_length,
            "aaData"                    => array()
        );

        // change '0' value to '-'
        foreach($result->rows as $data_row) {
            if($data_row->short_description_wc == '0') {
                $data_row->short_description_wc = '-';
            }
            if($data_row->long_description_wc == '0') {
                $data_row->long_description_wc = '-';
            }

            $add_data = new stdClass();
            $add_data->id = $data_row->id;
            $add_data->status = $data_row->status;

            $output['aaData'][] = array(
                $data_row->user_id,
                $data_row->product_name,
                $data_row->url,
                $data_row->short_description,
                $data_row->short_description_wc,
                $data_row->long_description,
                $data_row->long_description_wc,
                $data_row->bach_name,
                'actions',
                $add_data
            );
        }

        $this->output->set_content_type('application/json')
            ->set_output(json_encode($output));
    }

    public function update_research_info()
    {
        $this->load->model('research_data_model');
        if( !empty( $_POST ) ) {

            $id = $this->input->post('id');
            $url = $this->input->post('url');
            $product_name = $this->input->post('product_name');
            $short_description = $this->input->post('short_description');
            $long_description = $this->input->post('long_description');
            // count words
            $short_description_wc = $this->input->post('short_description_wc');
            $long_description_wc = $this->input->post('long_description_wc');
            $this->research_data_model->updateItem($id, $product_name, $url, $short_description, $long_description, $short_description_wc, $long_description_wc);
            echo 'Record updated successfully!';
        }
    }

    public function delete_research_info()
    {
        $this->load->model('research_data_model');
        $id = $this->input->get('id');
        if( is_null( $id ) ) {
            echo 'ERROR: Id not provided.';
            return;
        }
        $this->research_data_model->delete( $id );
        echo 'Records deleted successfully';
    }

    public function save_in_batch()
    {
        $this->load->model('research_data_model');
        $this->load->model('batches_model');

        $this->form_validation->set_rules('product_name', 'Product Name', 'required|xss_clean');
        /*$this->form_validation->set_rules('keyword1', 'Keyword1', 'required|xss_clean');
        $this->form_validation->set_rules('keyword2', 'Keyword2', 'required|xss_clean');
        $this->form_validation->set_rules('keyword3', 'Keyword3', 'required|xss_clean');
        $this->form_validation->set_rules('meta_title', 'Meta title', 'required|xss_clean');
        $this->form_validation->set_rules('meta_description', 'Meta description', 'required|xss_clean');
        $this->form_validation->set_rules('meta_keywords', 'Meta keywords', 'required|xss_clean');
        $this->form_validation->set_rules('short_description', 'Short Description', 'required|xss_clean');
        $this->form_validation->set_rules('long_description', 'Long Description', 'required|xss_clean');
        $this->form_validation->set_rules('revision', 'Revision', 'integer');*/

        if ($this->form_validation->run() === true) {
            $batch = $this->input->post('batch');
            $batch_id = $this->batches_model->getIdByName($batch);
            if($batch_id == false) {
                $batch_id = $this->batches_model->insert($batch);
            }
            $url = $this->input->post('url');
            $product_name = $this->input->post('product_name');
            $keyword1 = $this->input->post('keyword1');
            $keyword2 = $this->input->post('keyword2');
            $keyword3 = $this->input->post('keyword3');
            $meta_title = $this->input->post('meta_title');
            $meta_description = $this->input->post('meta_description');
            $meta_keywords = $this->input->post('meta_keywords');
            $short_description = $this->input->post('short_description');
            $short_description_wc = $this->input->post('short_description_wc');
            $long_description = $this->input->post('long_description');
            $long_description_wc = $this->input->post('long_description_wc');
            if ($this->input->post('revision')=='') {
                $last_revision = $this->research_data_model->getLastRevision();
                if(!empty($last_revision)){
                    $revision = $last_revision[0]->revision + 1;
                } else {
                    $revision = 1;
                }
            } else {
                $revision = $this->input->post('revision');
            }
            //$results = $this->research_data_model->getAllByProductName($product_name, $batch_id);
            $results = $this->research_data_model->getProductByURL($url, $batch_id);

            if(empty($results)){
                $data['research_data_id'] = $this->research_data_model->insert($batch_id, $url, $product_name, $keyword1, $keyword2,
                    $keyword3, $meta_title, $meta_description, $meta_keywords, $short_description, $short_description_wc, $long_description, $long_description_wc, $revision);
            } else {
                $data['research_data_id'] = $this->research_data_model->update($results[0]->id, $batch_id, $url, $product_name, $short_description, $short_description_wc, $long_description, $long_description_wc, $keyword1, $keyword2,
                    $keyword3, $meta_title, $meta_description, $meta_keywords, $revision);
            }

            $data['revision'] = $revision;
        } else {
            $data['message'] = (validation_errors() ? validation_errors() : $this->session->flashdata('message'));
        }

        $this->output->set_content_type('application/json')
            ->set_output(json_encode($data));
    }

    public function getById( $id ) {
        $this->load->model('research_data_model');
        if( isset( $id ) )
            echo json_encode( $this->research_data_model->get( $id ) );
    }

    public function export()
    {
        $this->load->model('batches_model');
        $batch_id = $this->batches_model->getIdByName($this->input->get('batch'));
        $this->load->database();
        $query = $this->db->where('batch_id', $batch_id)->get('research_data');
        $this->load->helper('csv');
        query_to_csv($query, TRUE, $this->input->get('batch').'.csv');
    }

    public function getBoxData()
    {
        $this->load->model('research_box_position_model');
        $data = $this->research_box_position_model->getDataByUserId();
        $this->output->set_content_type('application/json')
            ->set_output(json_encode($data));
    }

    public function delete_research_data()
    {
        $this->research_data_model->delete($this->input->post('id'));
    }

    public function getCustomersByUserId(){
        $this->load->model('customers_model');
        $this->load->model('users_to_customers_model');

        $customers = $this->users_to_customers_model->getByUserId($this->ion_auth->get_user_id());
        if(!$this->ion_auth->is_admin($this->ion_auth->get_user_id())){
            if(count($customers) == 0){
                $customer_list = array();
            }else{
                $customer_list = array(''=>'All Customers');
            }
            foreach($customers as $customer){
                array_push($customer_list, $customer->name);
            }
        }else{
            if(count($customers) == 0){
            $customers = $this->customers_model->getAll();
            }
            $customer_list = array(''=>'All Customers');
            foreach($customers as $customer){
                array_push($customer_list, $customer->name);
            }
        }
        return $customer_list;

    }

    public function generateDesc(){
        $s = $this->input->post('product_name');

        $this->load->library('pagination');
        $pagination_config['base_url'] = $this->config->site_url().'/research/generateDesc';
        $pagination_config['per_page'] = 0;

        $data = array(
            's' => $s,
            'search_results' => array()
        );

        $attr_path = $this->config->item('attr_path');

        $csv_rows = array();

        // Search in files
        if ( isset($this->settings['use_files']) && $this->settings['use_files']) {
            if ($path = realpath($attr_path)) {
                $objects = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($path), RecursiveIteratorIterator::SELF_FIRST);
                foreach($objects as $name => $object){
                    if (!$object->isDir()) {
                        if (preg_match("/.*\.csv/i",$object->getFilename(),$matches)) {
                            $_rows = array();
                            if (($handle = fopen($name, "r")) !== FALSE) {
                                while (($row = fgets($handle, 1000)) !== false) {
                                    if (preg_match("/$s/i",$row,$matches)) {
                                        $_rows[] = $row;
                                    }
                                }
                            }
                            fclose($handle);

                            foreach (array_keys(array_count_values($_rows)) as $row){
                                $csv_rows[] = str_getcsv($row, ",", "\"");
                            }
                            unset($_rows);
                        }
                    }
                }
            }
        }

        // Search in database
        if ( isset($this->settings['use_database']) && $this->settings['use_database']) {
            $this->load->model('imported_data_model');
            if (( $_rows = $this->imported_data_model->findByData($s))!== false) {
                foreach($_rows as $row) {
                    $csv_rows[] = str_getcsv($row['data'], ",", "\"");
                }
            }
        }

        if (!empty($csv_rows)) {
            $current_row = 0;
            foreach($csv_rows as $row) {
                if ($current_row < (int)$this->uri->segment(3)) {
                    $current_row++;
                    continue;
                }
                foreach ($row as $col) {
                    if (preg_match("/^http:\/\/*/i",$col,$matches)) {
                        $row['url'] = $col;
                    } else if ( mb_strlen($col) <= 250) {
                        $row['title'] = $col;
                    } else if (empty($row['description'])){
                        $row['description'] = substr($col, 0, strpos(wordwrap($col, 200), "\n"));

                    }
                }

                if (!empty($row['url']) && !empty($row['title'])) {
                    $data['search_results'][] =  '<a href="'.$row['url'].'">'.$row['title'].'</a><br/>'.$row['description'];
                } else if (!empty($row['description'])) {
                    $data['search_results'][] =  $row['description'];
                }
                if (count($data['search_results']) == $pagination_config['per_page']) break;
            }
        }

        $pagination_config['total_rows'] = count($csv_rows);
        $this->pagination->initialize($pagination_config);
        $data['pagination']= $this->pagination->create_links();

        $this->output->set_content_type('application/json')
            ->set_output(json_encode($data));
    }

    public function countAllItemsInBatch(){
        $this->load->model('batches_model');
        $this->load->model('statistics_model');
        $this->load->model('research_data_model');
        $batch = $this->input->post('batch');
        $batch_id = $this->batches_model->getIdByName($batch);
        $params = new stdClass();
        $params->batch_id = $batch_id;
        $params->txt_filter = '';
        $res = $this->statistics_model->getStatsData($params);
        $num_rows = count($res);
        if($num_rows == 0){
            $num_rows = $this->research_data_model->countAll($batch_id);
        }
        $this->output->set_content_type('application/json')
            ->set_output(json_encode($num_rows));
    }

    public function filterCustomerByBatch(){
        $this->load->model('batches_model');
        $batch = $this->input->post('batch');
        $customer_name = $this->batches_model->getCustomerByBatch($batch);
        $this->output->set_content_type('application/json')
            ->set_output(json_encode(strtolower($customer_name)));
    }

    public function filterBatchByCustomerName(){
        $this->load->model('batches_model');
        $this->load->model('customers_model');
        $customer_id = $this->customers_model->getIdByName($this->input->post('customer_name'));
        $batches = $this->batches_model->getAllByCustomer($customer_id);
        if(strtolower($this->input->post('customer_name')) ==  "all customers"){
            $batches = $this->batches_model->getAll();
        }
        $batches_list = array();
        if(!empty($batches)){
            foreach($batches as $batch){
                $batches_list[] = array('id' => $batch->id, 'title' => $batch->title);
            }
        }
        $this->output->set_content_type('application/json')
            ->set_output(json_encode($batches_list));
    }

    public function filterBatchByCustomer(){
        $this->load->model('batches_model');
        $this->load->model('customers_model');
        $customer_id = $this->customers_model->getIdByName($this->input->post('customer_name'));
        $batches = $this->batches_model->getAllByCustomer($customer_id);
        if(strtolower($this->input->post('customer_name')) ==  "all customers"){
            $batches = $this->batches_model->getAll();
        }
        $batches_list = array();
        if(!empty($batches)){
            foreach($batches as $batch){
                array_push($batches_list, $batch->title);
            }
        }
        $this->output->set_content_type('application/json')
            ->set_output(json_encode($batches_list));
    }

    public function filterStyleByCustomer(){
        $this->load->model('customers_model');
        $this->load->model('style_guide_model');
        if(strtolower($this->input->post('customer_name')) ==  "all customers"){
            $customer_id = $this->customers_model->getIdByName($this->input->post('customer_name'));
            $style = $this->style_guide_model->getStyleByCustomerId($customer_id);
            $this->output->set_content_type('application/json')
               ->set_output(json_encode($style[0]->style));
        }
    }

    public function upload_csv(){
        $this->load->library('UploadHandler');

        $this->output->set_content_type('application/json');
        $this->uploadhandler->upload(array(
            'script_url' => site_url('research/upload_csv'),
            'upload_dir' => $this->config->item('csv_upload_dir'),
            'param_name' => 'files',
            'delete_type' => 'POST',
            'accept_file_types' => '/.+\.(csv|txt)$/i',
        ));
    }

    public function csv_import() {
        $this->load->model('batches_model');
        $this->load->model('customers_model');

        $file = $this->config->item('csv_upload_dir').$this->input->post('choosen_file');
        $_rows = array();
        if (($handle = fopen($file, "r")) !== FALSE) {
            while (($data = fgetcsv($handle, 1000, ",")) !== FALSE) {
                if(!is_null($data[0]) && $data[0]!='URL' && $data[0]!=''){
                    $_rows[] = $data[0];
                }
            }
            fclose($handle);
        }
        $batch_id = $this->batches_model->getIdByName($this->input->post('batch_name'));

        $added = $this->insert_rows($batch_id, $_rows);

        $str = $added;
        if($added==1){
            $str .= ' record';
        } else if($added>1){
            $str .= ' records';
        }
        $response['batch_id'] = $batch_id;
        $response['message'] = $str .' added to batch';
         $this->output->set_content_type('application/json')
                ->set_output(json_encode($response));
    }

    private function insert_rows($batch_id, $_rows) {
        $this->load->model('research_data_model');
        $this->load->model('research_data_to_crawler_list_model');
        $this->load->model('crawler_list_model');
		$this->load->library('PageProcessor');

    	$last_revision = $this->research_data_model->getLastRevision();
        $added = 0;

        $this->research_data_model->db->trans_start();
        foreach($_rows as $_row){
            $res = $this->research_data_model->checkItemUrl($batch_id, $_row);
            if(empty($res)){
              $research_data_id = $this->research_data_model->insert($batch_id, $_row, '', '', '',
                    '', '', '', '', '', 0, '', 0,  $last_revision);
                $added += 1;

                // Insert to crawler list
	            if ($research_data_id && $this->pageprocessor->isURL($_row)) {
                    $crawler_list_id = $this->crawler_list_model->getByUrl($_row);
                    if (!$crawler_list_id) {
						$crawler_list_id = $this->crawler_list_model->insert($_row, 0);
					}
                    $this->research_data_to_crawler_list_model->insert($research_data_id, $crawler_list_id);
					// add part if url already in crawler_list
				}
            }
        }
        $this->research_data_model->db->trans_complete();

        return $added;
    }

   private function insert_rows_batch($batch_id, $_rows) {
        $this->load->model('research_data_model');
        $this->load->model('research_data_to_crawler_list_model');
        $this->load->model('crawler_list_model');
		$this->load->library('PageProcessor');

    	$last_revision = $this->research_data_model->getLastRevision();
        $added = 0;

        $this->research_data_model->db->trans_start();
        foreach($_rows as $_row){
            // Insert to crawler list
            if ($this->pageprocessor->isURL($_row)) {
				$research_data_id = $this->research_data_model->insert($batch_id, $_row, '', '', '','', '', '', '', '', 0, '', 0,  $last_revision);
                $added += 1;

				$crawler_list_id = $this->crawler_list_model->insert($_row, 0);
				$this->research_data_to_crawler_list_model->insert($research_data_id, $crawler_list_id);
			}

			if ( $added % 100 == 0 ) {
				$this->research_data_model->db->trans_complete();
				$this->research_data_model->db->trans_start();
			}
        }
        $this->research_data_model->db->trans_complete();

        return $added;
    }


    public function sitemap_import() {
    	$this->load->model('batches_model');
        $this->load->model('customers_model');
		$this->load->library('SitemapProcessor');

    	$batch_id =  $this->batches_model->getIdByName($this->input->post('batch_name'));
    	$customer =  $this->customers_model->getByName($this->input->post('customer_name'));
		if (!empty($customer['url']) && !empty($batch_id)) {
			$urls = $this->sitemapprocessor->getURLs($customer['url']);
		}

		if (count($urls)>0) {
			$added = $this->insert_rows_batch($batch_id, $urls);
			$response['message'] = $added .' added to batch';
		} else {
			$response['message'] = 'Can\'t find sitemap, robots.txt or urls';
		}

        $this->output->set_content_type('application/json')
                ->set_output(json_encode($response));
    }

    public function delete_batch(){
        $this->load->model('batches_model');
        $batch_id =  $this->batches_model->getIdByName($this->input->post('batch_name'));
        $this->batches_model->delete($batch_id);
    }

    public function getREProducts() {
        $this->load->model('crawler_list_prices_model');

        $price_list = $this->crawler_list_prices_model->get_products_with_price();

        if(!empty($price_list['total_rows'])) {
            $total_rows = $price_list['total_rows'];
        } else {
            $total_rows = 0;
        }

        $output = array(
            "sEcho"                     => intval($_GET['sEcho']),
            "iTotalRecords"             => $total_rows,
            "iTotalDisplayRecords"      => $total_rows,
            "iDisplayLength"            => $price_list['display_length'],
            "aaData"                    => array()
        );

        if(!empty($price_list['result'])) {
            foreach($price_list['result'] as $price) {
                $output['aaData'][] = array(
                    $price->number,
                    $price->product_name,
                    $price->url,
                );
            }
        }

        $this->output->set_content_type('application/json')
            ->set_output(json_encode($output));
    }

    public function getAttributes() {
        $this->load->model('imported_data_parsed_model');
        $this->load->model('imported_data_model');
        $this->load->model('imported_data_attributes_model');
        $imported_data_id = $this->input->post('imported_data_id');
        $data = $this->imported_data_parsed_model->getByImId($imported_data_id);
        $res = array();
        foreach($data as $key => $value) {
            if ($key != 'url') {
                $descCmd = str_replace($this->config->item('cmd_mask'), $value ,$this->config->item('tsv_cmd'));
                if ($result = shell_exec($descCmd)) {
                    $a = json_decode(json_encode(simplexml_load_string($result)),1);
                    foreach ($a['description']['attributes']['attribute'] as $attribute) {
                        $res[$key][$attribute['@attributes']['tagName']] = $attribute['@attributes']['value'];
                    }
                }
            }
        }
        $this->output->set_content_type('application/json')
            ->set_output(json_encode($res));
    }
}
