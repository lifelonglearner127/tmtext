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
                'duplicate_context'             => 'true',
                'price_diff'                    => 'true',
            );
        }
        $this->data['columns'] = $columns;

        $this->render();
    }

    public function get_assess_info(){
        $this->load->model('research_data_model');
        $this->load->model('batches_model');

        $txt_filter = '';
        if($this->input->get('search_text') != ''){
            $txt_filter = $this->input->get('search_text');
        }

        $batch_name = $this->input->get('batch_name');
//        if (empty($batch_name)) {
//            $this->output->set_content_type('application/json')
//                ->set_output("{}");
//            return;
//        }
//        $batch_id = $this->batches_model->getIdByName($batch);
//        if($batch_id == false || $txt_filter != '') {
//            $batch_id = '';
//        }

        $date_from = $this->input->get('date_from') == 'undefined' ? '' : $this->input->get('date_from');
        $date_to = $this->input->get('date_to') == 'undefined' ? '' : $this->input->get('date_to');
        $price_diff = $this->input->get('price_diff');
        $short_less = $this->input->get('short_less') == 'undefined' ? -1 : $this->input->get('short_less');
        $short_more = $this->input->get('short_more') == 'undefined' ? -1 : $this->input->get('short_more');
        $short_seo_phrases = $this->input->get('short_seo_phrases');
        $short_duplicate_context = $this->input->get('short_duplicate_context');
        $long_less = $this->input->get('long_less') == 'undefined' ? -1 : $this->input->get('long_less');
        $long_more = $this->input->get('long_more') == 'undefined' ? -1 : $this->input->get('long_more');
        $long_seo_phrases = $this->input->get('long_seo_phrases');
        $long_duplicate_context = $this->input->get('long_duplicate_context');

        $params = new stdClass();
        $params->batch_name = $batch_name;
        $params->txt_filter = $txt_filter;
        $params->date_from = $date_from;
        $params->date_to = $date_to;
//        $params->short_duplicate_context = $short_duplicate_context;
//        $params->short_misspelling = $short_misspelling;
//        $params->long_duplicate_context = $long_duplicate_context;
//        $params->long_misspelling = $long_misspelling;

        $results = $this->research_data_model->getInfoForAssess($params);

        $this->load->model('imported_data_parsed_model');
        if ($price_diff) {
            //$prices = $this->research_data_model->getPricesForBatch($batch_name);
        }

        $enable_exec = true;
        $result_table = array();
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
            if ($short_more > -1) {
                if ($short_description_wc < $short_more) {
                    continue;
                }
            }
            if ($short_less > -1) {
                if ($short_description_wc > $short_less) {
                    continue;
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
            if ($long_more > -1) {
                if ($long_description_wc < $long_more) {
                    continue;
                }
            }
            if ($long_less > -1) {
                if ($long_description_wc > $long_less) {
                    continue;
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
            $result_row->seo_s = "None";
            $result_row->seo_l = "None";
            $result_row->price_diff = "-";
            $result_row->duplicate_context = "-";
            $result_row->own_price = "-";

            if ($price_diff) {
                $data_import = $this->imported_data_parsed_model->getByImId($row->imported_data_id);
                if (isset($data_import['parsed_attributes']) && isset($data_import['parsed_attributes']['model'])) {
                    $own_prices = $this->imported_data_parsed_model->getLastPrices($row->imported_data_id);
                    if (!empty($own_prices)) {
                        $own_price = floatval($own_prices[0]->price);
                        $result_row->own_price = $own_price;
                        $price_diff = "<nobr>Own price - ".$own_price."</nobr><br />";
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
                                    $his_price = floatval($three_last_prices[0]->price);
                                    if ($his_price > $price_upper_range || $his_price < $price_lower_range) {
                                        $price_diff = $price_diff."<nobr>".$similar_items[$ks]['customer']." - ".$his_price."</nobr><br />";
                                        $result_row->price_diff = $price_diff;
                                    }
                                }
                            }
                        }
                    }
                }
            }

            if ($short_seo_phrases) {
                if ($short_description_wc == $row->short_description_wc && !is_null($row->seo_s)) {
                    $result_row->seo_s = $row->seo_s;
                } else {
                    if ($enable_exec) {
                        $cmd = $this->prepare_extract_phrases_cmd($row->short_description);
                        $output = array();
                        exec($cmd, $output, $error);

                        if ($error > 0) {
                            $enable_exec = false;
                        } else {
                            $result_row->seo_s = $this->prepare_seo_phrases($output);
                            if (is_null($row->seo_s)) {
                                $this->imported_data_parsed_model->insert($row->imported_data_id, "seo_s", $result_row->seo_s);
                            } else {
                                $this->imported_data_parsed_model->updateValueByKey($row->imported_data_id, "seo_s", $result_row->seo_s);
                            }
                        }
                    }
                }
            }

            if ($long_seo_phrases) {
                if ($long_description_wc == $row->long_description_wc && !is_null($row->seo_l)) {
                    $result_row->seo_l = $row->seo_l;
                } else {
                    if ($enable_exec) {
                        $cmd = $this->prepare_extract_phrases_cmd($row->long_description);
                        $output = array();
                        exec($cmd, $output, $error);

                        if ($error > 0) {
                            $enable_exec = false;
                        } else {
                            $result_row->seo_l = $this->prepare_seo_phrases($output);
                            if (is_null($row->seo_l)) {
                                $this->imported_data_parsed_model->insert($row->imported_data_id, "seo_l", $result_row->seo_l);
                            } else {
                                $this->imported_data_parsed_model->updateValueByKey($row->imported_data_id, "seo_l", $result_row->seo_l);
                            }
                        }
                    }
                }
            }

            $result_table[] = $result_row;
        }

        $s_columns = explode(',', $this->input->get('sColumns'));
        if (!empty($s_columns)) {
            $s_column_index = intval($this->input->get('iSortCol_0'));
            $s_column = $s_columns[$s_column_index];
            $this->sort_column = $s_column;
            $this->sort_direction = strtolower($this->input->get('sSortDir_0'));
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
                    $output['aaData'][] = array(
                        $data_row->created,
                        $data_row->product_name,
                        $data_row->url,
                        $data_row->short_description_wc,
                        $data_row->seo_s,
                        $data_row->long_description_wc,
                        $data_row->seo_l,
                        $data_row->duplicate_context,
                        $data_row->price_diff,
                        "Some Recommendations",
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

        $this->output->set_content_type('application/json')
            ->set_output(json_encode($output));
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
					if (!$this->crawler_list_model->getByUrl($_row)) {
						$crawler_list_id = $this->crawler_list_model->insert($_row, 0);
						$this->research_data_to_crawler_list_model->insert($research_data_id, $crawler_list_id);
					}
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
