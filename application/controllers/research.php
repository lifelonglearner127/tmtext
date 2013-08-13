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
        $batch_id = $this->batches_model->getIdByName($this->input->post('batch'));
        if($batch_id != false){
            $batch_info = $this->batches_model->get($batch_id);
            $last_date = $this->research_data_model->getLastAddedDateItem($batch_id);
            $result = array();
            $result['created'] = mdate('%m/%d/%Y',strtotime($batch_info[0]->created));
            $result['modified'] = mdate('%m/%d/%Y',strtotime($last_date[0]->modified));
            $result['count_items'] = $this->research_data_model->countAll($batch_id);

            $this->output->set_content_type('application/json')
                ->set_output(json_encode($result));
        }
    }

    public function addToBatch(){
        $this->load->model('batches_model');
        $batch_id = $this->batches_model->getIdByName($this->input->post('batch'));
        if($batch_id != false){
            $lines = explode("\n", $this->input->post('urls'));
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

        $batch_name = $this->input->get('batch_name');

        if($batch_name == '' || $batch_name == 'Select batch'){
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
            $build_assess_params->price_diff = $this->input->get('price_diff');
            $build_assess_params->short_less = $this->input->get('short_less') == 'undefined' ? -1 : $this->input->get('short_less');
            $build_assess_params->short_more = $this->input->get('short_more') == 'undefined' ? -1 : $this->input->get('short_more');
            $build_assess_params->short_seo_phrases = $this->input->get('short_seo_phrases');
            $build_assess_params->short_duplicate_content = $this->input->get('short_duplicate_content');
            $build_assess_params->long_less = $this->input->get('long_less') == 'undefined' ? -1 : $this->input->get('long_less');
            $build_assess_params->long_more = $this->input->get('long_more') == 'undefined' ? -1 : $this->input->get('long_more');
            $build_assess_params->long_seo_phrases = $this->input->get('long_seo_phrases');
            $build_assess_params->long_duplicate_content = $this->input->get('long_duplicate_content');
            $build_assess_params->all_columns = $this->input->get('sColumns');
            $build_assess_params->sort_columns = $this->input->get('iSortCol_0');
            $build_assess_params->sort_dir = $this->input->get('sSortDir_0');

            $params = new stdClass();
            $params->batch_name = $batch_name;
            $params->txt_filter = $txt_filter;
            $params->date_from = $build_assess_params->date_from;
            $params->date_to = $build_assess_params->date_to;

            $results = $this->get_data_for_assess($params);

            $output = $this->build_asses_table($results, $build_assess_params, $batch_name);

            $this->output->set_content_type('application/json')
                ->set_output(json_encode($output));
        }
    }

    private function get_data_for_assess($params) {
        $this->load->model('statistics_model');
        $results = $this->statistics_model->getStatsData($params);
        return $results;
    }

    private function build_asses_table($results, $build_assess_params, $batch_name='') {
        $duplicate_content_range = 25;
        $this->load->model('batches_model');
        $this->load->model('imported_data_parsed_model');
        $this->load->model('statistics_duplicate_content_model');

        $customer_name = $this->batches_model->getCustomerByName($batch_name);
        $enable_exec = true;
        $result_table = array();
        $report = array();
        $pricing_details = array();
        $items_priced_higher_than_competitors = 0;
        $items_have_more_than_20_percent_duplicate_content = 0;
        $items_unoptimized_product_content = 0;
        $items_short_products_content = 0;
        foreach($results as $row) {
            //$short_description_wc = preg_match_all('/\b/', $row->short_description) / 2; // bug in PHP 5.3.10
            $short_description_wc = (count(preg_split('/\b/', $row->short_description)) - 1) / 2;
            if (is_null($row->short_description_wc)) {
                $this->imported_data_parsed_model->insert($row->imported_data_id, "Description_WC", $short_description_wc);
            } else {
                if (intval($row->short_description_wc) <> $short_description_wc) {
                    $this->imported_data_parsed_model->updateValueByKey($row->imported_data_id, "Description_WC", $short_description_wc);
                }
            }

            //$long_description_wc = preg_match_all('/\b/', $row->long_description) / 2; // bug in PHP 5.3.10
            $long_description_wc = (count(preg_split('/\b/', $row->long_description)) - 1) / 2;

            if (is_null($row->long_description_wc)) {
                $this->imported_data_parsed_model->insert($row->imported_data_id, "Long_Description_WC", $long_description_wc);
            } else {
                if (intval($row->long_description_wc) <> $long_description_wc) {
                    $this->imported_data_parsed_model->updateValueByKey($row->imported_data_id, "Long_Description_WC", $long_description_wc);
                }
            }

            $result_row = new stdClass();
            $result_row->id = $row->id;
            $result_row->imported_data_id = $row->imported_data_id;
            $result_row->created = $row->created;
            $result_row->product_name = $row->product_name;
            $result_row->url = $row->url;
            $result_row->short_description = $row->short_description;
            $result_row->long_description = $row->long_description;
            $result_row->short_description_wc = $short_description_wc;
            $result_row->long_description_wc = $long_description_wc;
            $result_row->short_seo_phrases = "None";
            $result_row->long_seo_phrases = "None";
            $result_row->price_diff = "-";
            $result_row->duplicate_content = "-";
            $result_row->own_price = "-";
            $result_row->competitors_prices = array();

            $own_site = parse_url($result_row->url,  PHP_URL_HOST);
            if (!$own_site)
                $own_site = "own site";
            $own_site = str_replace("www.", "", $own_site);

            if ($build_assess_params->price_diff) {
                $data_import = $this->imported_data_parsed_model->getByImId($row->imported_data_id);
                if (isset($data_import['parsed_attributes']) && isset($data_import['parsed_attributes']['model'])) {
                    $own_prices = $this->imported_data_parsed_model->getLastPrices($row->imported_data_id);
                    if (!empty($own_prices)) {
                        $own_price = floatval($own_prices[0]->price);
                        $result_row->own_price = $own_price;
                        $price_diff_exists = "<input type='hidden'/>";
                        $price_diff_exists = $price_diff_exists."<nobr>".$own_site." - $".$own_price."</nobr><br />";
                        $similar_items = $this->imported_data_parsed_model->getByParsedAttributes($data_import['parsed_attributes']['model']);
                        if (!empty($similar_items)) {
                            foreach ($similar_items as $ks => $vs) {
                                $similar_item_imported_data_id = $similar_items[$ks]['imported_data_id'];
                                if ($row->imported_data_id == $similar_item_imported_data_id) {
                                    continue;
                                }
                                $three_last_prices = $this->imported_data_parsed_model->getLastPrices($similar_item_imported_data_id);
                                if (!empty($three_last_prices)) {
                                    $price_scatter = $own_price * 0.03;
                                    $price_upper_range = $own_price + $price_scatter;
                                    $price_lower_range = $own_price - $price_scatter;
                                    $competitor_price = floatval($three_last_prices[0]->price);
                                    if ($competitor_price < $own_price) {
                                        $items_priced_higher_than_competitors++;
                                    }
                                    if ($competitor_price > $price_upper_range || $competitor_price < $price_lower_range) {
                                        $price_diff_exists = $price_diff_exists."<nobr>".$similar_items[$ks]['customer']." - $".$competitor_price."</nobr><br />";
                                        $result_row->price_diff = $price_diff_exists;
                                        $result_row->competitors_prices[] = $competitor_price;
                                    }
                                }
                            }
                        }
                    }
                }
            }

            if ($build_assess_params->short_seo_phrases) {
                if ($short_description_wc == $row->short_description_wc && !is_null($row->short_seo_phrases)) {
                    $result_row->short_seo_phrases = $row->short_seo_phrases;
                } else {
                    if ($enable_exec) {
                        $cmd = $this->prepare_extract_phrases_cmd($row->short_description);
                        $output = array();
                        exec($cmd, $output, $error);

                        if ($error > 0) {
                            $enable_exec = false;
                        } else {
                            $result_row->short_seo_phrases = $this->prepare_seo_phrases($output);
                            if (is_null($row->short_seo_phrases)) {
                                $this->imported_data_parsed_model->insert($row->imported_data_id, "short_seo_phrases", $result_row->short_seo_phrases);
                            } else {
                                $this->imported_data_parsed_model->updateValueByKey($row->imported_data_id, "short_seo_phrases", $result_row->short_seo_phrases);
                            }
                        }
                    }
                }
            }

            if ($build_assess_params->long_seo_phrases) {
                if ($long_description_wc == $row->long_description_wc && !is_null($row->long_seo_phrases)) {
                    $result_row->long_seo_phrases = $row->long_seo_phrases;
                } else {
                    if ($enable_exec) {
                        $cmd = $this->prepare_extract_phrases_cmd($row->long_description);
                        $output = array();
                        exec($cmd, $output, $error);

                        if ($error > 0) {
                            $enable_exec = false;
                        } else {
                            $result_row->long_seo_phrases = $this->prepare_seo_phrases($output);
                            if (is_null($row->long_seo_phrases)) {
                                $this->imported_data_parsed_model->insert($row->imported_data_id, "long_seo_phrases", $result_row->long_seo_phrases);
                            } else {
                                $this->imported_data_parsed_model->updateValueByKey($row->imported_data_id, "long_seo_phrases", $result_row->long_seo_phrases);
                            }
                        }
                    }
                }
            }

            if ($build_assess_params->short_duplicate_content || $build_assess_params->long_duplicate_content) {
                $dc = $this->statistics_duplicate_content_model->get($result_row->imported_data_id);
                $duplicate_customers_short = '';
                $duplicate_customers_long = '';
                $duplicate_short_percent_total = 0;
                $duplicate_long_percent_total = 0;
                if (count($dc) > 1) {

                    foreach ($dc as $vs) {
                        if(strtolower($customer_name[0]->name) == $vs->customer){
                            $short_percent = 0;
                            $long_percent = 0;
                            if ($build_assess_params->short_duplicate_content) {
                                $duplicate_short_percent_total += 100 - $vs->short_original;
                                $short_percent = 100 - round($vs->short_original, 1);
                                if($short_percent > 0){
                                    $duplicate_customers_short = $duplicate_customers_short.'<nobr>'.$vs->customer.' - '.$short_percent.'%</nobr><br />';
                                }
                            }
                            if ($build_assess_params->long_duplicate_content) {
                                $duplicate_long_percent_total += 100 - $vs->long_original;
                                $long_percent = 100 - round($vs->long_original, 1);
                                if($long_percent > 0){
                                    $duplicate_customers_long = $duplicate_customers_long.'<nobr>'.$vs->customer.' - '.$long_percent.'%</nobr><br />';
                                }
                            }
                            if($short_percent >= 20 || $long_percent >= 20){
                                $items_have_more_than_20_percent_duplicate_content += 1;
                            }
                        }
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

            if ($result_row->short_seo_phrases == 'None' && $result_row->long_seo_phrases == 'None') {
                $items_unoptimized_product_content++;
            }

            if (($result_row->short_description_wc < 20 && $build_assess_params->short_less == 20) &&
                ($result_row->long_description_wc < 100 && $build_assess_params->long_less==100)) {
                $items_short_products_content++;
            }

            if (($result_row->short_description_wc <= 20 && $build_assess_params->long_less == false ) ||
                ($result_row->long_description_wc <= 100 && $build_assess_params->short_less == false)){
                $items_short_products_content++;
            }

            if (($result_row->short_description_wc <= 20 && $build_assess_params->long_less == -1 ) ||
                ($result_row->long_description_wc <= 100 && $build_assess_params->short_less == -1)){
                $items_short_products_content++;
            }

            if ($build_assess_params->short_more > -1) {
                if ($short_description_wc < $build_assess_params->short_more) {
                    continue;
                }
            }
            if ($build_assess_params->short_less > -1) {
                if ($short_description_wc > $build_assess_params->short_less) {
                    continue;
                }
            }
            if ($build_assess_params->long_more > -1) {
                if ($long_description_wc < $build_assess_params->long_more) {
                    continue;
                }
            }
            if ($build_assess_params->long_less > -1) {
                if ($long_description_wc > $build_assess_params->long_less) {
                    continue;
                }
            }

            $result_table[] = $result_row;
        }

        $report['summary']['total_items'] = count($result_table);
        $report['summary']['items_priced_higher_than_competitors'] = $items_priced_higher_than_competitors;
        $report['summary']['items_have_more_than_20_percent_duplicate_content'] = $items_have_more_than_20_percent_duplicate_content;
        $report['summary']['items_unoptimized_product_content'] = $items_unoptimized_product_content;
        $report['summary']['items_short_products_content'] = $items_short_products_content;

        if ($items_priced_higher_than_competitors > 0) {
            $report['recommendations']['items_priced_higher_than_competitors'] = 'Reduce pricing on '.$items_priced_higher_than_competitors.' item(s)';
        }
        if ($items_have_more_than_20_percent_duplicate_content == 0) {
            $report['recommendations']['items_have_more_than_20_percent_duplicate_content'] = 'Create original product content';
        }
        if ($items_unoptimized_product_content > 0) {
            $report['recommendations']['items_unoptimized_product_content'] = 'Optimize product content';
        }
        if ($items_short_products_content > 0) {
            $report['recommendations']['items_short_products_content'] = 'Increase product description lengths';
        }

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
                    $recommendations = array();
                    if ($data_row->short_description_wc < 50 || $data_row->long_description_wc < 100) {
                        $recommendations[] = '<li>Increase descriptions word count</li>';
                    }
                    /*if ($data_row->short_seo_phrases != 'None' || $data_row->long_seo_phrases != 'None') {
                           $recommendations[] = '<li>SEO optimize product content</li>';
                       }*/
                    if ($data_row->short_seo_phrases == 'None' && $data_row->long_seo_phrases == 'None') {
                        $recommendations[] = '<li>SEO optimize product content</li>';
                    }
                    //$recommendations[] = '<li>Add unique content</li>';
                    if ($build_assess_params->price_diff && !empty($data_row->competitors_prices)) {
                        if (min($data_row->competitors_prices) < $data_row->own_price) {
                            $recommendations[] = '<li>Lower price to be competitive</li>';
                        }
                    }
                    //$recommendations[] = '<li>Add product to inventory</li>';

                    $recommendations_html = '<ul class="assess_recommendations">'.implode('', $recommendations).'</ul>';

                    $output['aaData'][] = array(
                        $data_row->created,
                        $data_row->product_name,
                        $data_row->url,
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
            $output['ExtraData']['report'] = $report;
        }

        return $output;
    }

    public function assess_report_download() {
        $params = new stdClass();
        $params->batch_name = $this->input->get('batch_name');
        $results = $this->get_data_for_assess($params);

        $batch_id = $this->input->get('batch_id');
        $type_doc = $this->input->get('type_doc');

        $this->load->model('batches_model');
        $customer = $this->batches_model->getAllCustomerDataByBatch($params->batch_name);
        //$batch = $this->batches_model->getByName($batch_id);
        $user_id = $this->ion_auth->get_user_id();
        $key = 'research_assess_report_options';
        $existing_settings = $this->settings_model->get_value($user_id, $key);
        $batch_report_settings = $existing_settings[$batch_id];
        if (empty($batch_report_settings)) {
            $assess_report_page_layout = 1;
        } else {
            if (!empty($batch_report_settings->assess_report_page_layout)) {
                $assess_report_page_layout = $batch_report_settings->assess_report_page_layout;
            }
        }

        $current_date = new DateTime(date('Y-m-d H:i:s'));

        $css_path = APPPATH.".."."/webroot/css/";
        $img_path = APPPATH.".."."/webroot/img/";
        $own_logo = $img_path."content-analytics.png";
        $customer_logo = $img_path.$customer->image_url;

        $this->load->model('reports_model');
        $report = $this->reports_model->get_by_name('Assess');
        $report_cover = $report[0]->body;
        $report_cover = str_replace('#date#', date('F j, Y'), $report_cover);
        $report_cover = str_replace('#customer name#', $customer->name, $report_cover);

        $html = '';

        $build_assess_params = new stdClass();
        $build_assess_params->price_diff = true;
        $build_assess_params->short_less = -1;
        $build_assess_params->short_more = -1;
        $build_assess_params->short_seo_phrases = true;
        $build_assess_params->short_duplicate_content = true;
        $build_assess_params->long_less = -1;
        $build_assess_params->long_more = -1;
        $build_assess_params->long_seo_phrases = true;
        $build_assess_params->long_duplicate_content = true;

        $output = $this->build_asses_table($results, $build_assess_params, $params->batch_name);
        $report = $output['ExtraData']['report'];

        $header = '<table border=0 width=100%>';
        $header = $header.'<tr>';
        $header = $header.'<td style="text-align: left;">';
        $header = $header.'<img src="'.$own_logo.'" />';
        $header = $header.'</td>';
        $header = $header.'<td style="text-align: right;">';
        $header = $header.'<img src="'.$customer_logo.'" />';
        $header = $header.'</td>';
        $header = $header.'</tr>';
        $header = $header.'</table>';
        $header = $header.'<hr color="#C31233" height="10">';

        $html = $html.$header;
        $html = $html.$report_cover;
        $html = $html.'<pagebreak />';


        $html = $html.$header;

        $html = $html.'<table width=100% border=0>';
        $html = $html.'<tr><td style="text-align: left;font-weight: bold; font-style: italic;">Batch - '.$params->batch_name.'</td><td style="text-align: right;font-weight: bold; font-style: italic;">'.$current_date->format('F j, Y').'</td></tr>';
        $html = $html.'<tr><td colspan="2"><hr height="3"></td></tr>';
        $html = $html.'</table>';

        $html = $html.'<table class="report" border="1" cellspacing="0" cellpadding="0">';

        $html = $html.'<tr><td style="background-color: #dddddd;text-align: center;font-weight: bold;">Summary</td></tr>';

        $html = $html.'<tr><td>';
        $html = $html.'<div class=""><img class="icon" src="'.$img_path.'assess_report_number.png">'.$report['summary']['total_items'].' total Items</div>';
        $html = $html.'</td></tr>';

        $html = $html.'<tr><td>';
        $html = $html.'<div class=""><img class="icon" src="'.$img_path.'assess_report_dollar.png">'.$report['summary']['items_priced_higher_than_competitors'].' items priced higher than competitors</div>';
        $html = $html.'</td></tr>';

        $html = $html.'<tr><td>';
        $html = $html.'<div class=""><img class="icon" src="'.$img_path.'assess_report_D.png">'.$report['summary']['items_have_more_than_20_percent_duplicate_content'].' items have more than 20% duplicate content</div>';
        $html = $html.'</td></tr>';

        $html = $html.'<tr><td>';
        $html = $html.'<div class=""><img class="icon" src="'.$img_path.'assess_report_seo.png">'.$report['summary']['items_unoptimized_product_content'].' items have unoptimized product content</div>';
        $html = $html.'</td></tr>';

        $html = $html.'<tr><td>';
        $html = $html.'<div class=""><img class="icon" src="'.$img_path.'assess_report_arrow_down.png">'.$report['summary']['items_short_products_content'].' items have product content that is too short</div>';
        $html = $html.'</td></tr>';

        $html = $html.'</table>';

        $html = $html.'<table class="report recommendations" border="1" cellspacing="0" cellpadding="0" style="border-collapse: collapse;border-spacing: 0;">';

        $html = $html.'<tr><td style="background-color: #dddddd;text-align: center;font-weight: bold;">Recommendations</td></tr>';
        if ($report['recommendations']['items_priced_higher_than_competitors']) {
            $html = $html.'<tr><td>';
            $html = $html.'<div class=""><img class="icon" src="'.$img_path.'assess_report_dollar.png">';
            $html = $html.$report['recommendations']['items_priced_higher_than_competitors'].'</div>';
            $html = $html.'</td></tr>';
        }
        if ($report['recommendations']['items_have_more_than_20_percent_duplicate_content']) {
            $html = $html.'<tr><td>';
            $html = $html.'<div class=""><img class="icon" src="'.$img_path.'assess_report_D.png">';
            $html = $html.$report['recommendations']['items_have_more_than_20_percent_duplicate_content'].'</div>';
            $html = $html.'</td></tr>';
        }
        if ($report['recommendations']['items_short_products_content']) {
            $html = $html.'<tr><td>';
            $html = $html.'<div class=""><img class="icon" src="'.$img_path.'assess_report_seo.png">';
            $html = $html.$report['recommendations']['items_short_products_content'].'</div>';
            $html = $html.'</td></tr>';
        }
        if ($report['recommendations']['items_unoptimized_product_content']) {
            $html = $html.'<tr><td>';
            $html = $html.'<div class=""><img class="icon" src="'.$img_path.'assess_report_arrow_up.png">';
            $html = $html.$report['recommendations']['items_unoptimized_product_content'].'</div>';
            $html = $html.'</td></tr>';
        }

        $html = $html.'</table>';

        $html = $html.'<tr><td>';
        $html = $html.'</table>';

        $layout = 'Letter-L';
        if (!empty($assess_report_page_layout)) {
            if ($assess_report_page_layout == 2) {
                $layout = 'Letter';
            }
        }

        $this->load->library('pdf');
        $pdf = $this->pdf->load();
        $pdf = new mPDF('', $layout, 0, '', 10, 10, 10, 10, 8, 8);
        $stylesheet = file_get_contents($css_path.'assess_report.css');

//        $pdf->showImageErrors = true;

        $pdf->WriteHTML($stylesheet, 1);

        $pdf->WriteHTML($html, 2);

        $pdf->SetHTMLFooter('<div style="font-size: 10px;">Copyright © 2013 Content Solutions, Inc.</div>');

        $pdf->Output();
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

    private function prepare_seo_phrases($seo_lines) {
        if (empty($seo_lines)) {
            return "None";
        }
        $seo_phrases = array();
        $result_phrases = array();
        foreach ($seo_lines as $line) {
            $line_array = explode(",", $line);
            $number_repetitions = intval(str_replace("\"", "", $line_array[1]));
            if ($number_repetitions < 2) {
                continue;
            }
            $phrase = str_replace("\"", "", $line_array[0]);
            $seo_phrases[] = array($number_repetitions, $phrase);
        }
        if (empty($seo_phrases)) {
            return "None";
        }
        $lines_count = 0;
        foreach ($seo_phrases as $seo_phrase) {
            if ($lines_count > 2) {
                break;
            }
            $result_phrases[] = $seo_phrase[1]." (".$seo_phrase[0].")";
            $lines_count++;
        }
        return implode(" ", $result_phrases);
    }

    private function prepare_extract_phrases_cmd($text) {
        $text = str_replace("'", "\'", $text);
        $text = str_replace("`", "\`", $text);
        $text = str_replace('"', '\"', $text);
        $text = "\"".$text."\"";
        $cmd = str_replace($this->config->item('cmd_mask'), $text ,$this->config->item('extract_phrases'));
        $cmd = $cmd." 2>&1";
        return $cmd;
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
        $data = '';
        if($this->input->get('search_text') != ''){
            $data = $this->input->get('search_text');
        }
        $batch = $this->input->get('batch_name');

        $batch_id = $this->batches_model->getIdByName($batch);
        if($batch_id == false || $data != '') {
            $batch_id = '';
        }
        $results = $this->research_data_model->getInfoFromResearchData($data, $batch_id);

        // change '0' value to '-'
        foreach($results as $result) {
            if($result->short_description_wc == '0') {
                $result->short_description_wc = '-';
            }
            if($result->long_description_wc == '0') {
                $result->long_description_wc = '-';
            }
        }

        $this->output->set_content_type('application/json')
            ->set_output(json_encode($results));
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
        $id = $this->input->post('id');
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

    public function filterCustomerByBatch(){
        $this->load->model('batches_model');
        $batch = $this->input->post('batch');
        $customer_name = $this->batches_model->getCustomerByBatch($batch);
        $this->output->set_content_type('application/json')
            ->set_output(json_encode(strtolower($customer_name)));
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
