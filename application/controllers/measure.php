<?php

if (!defined('BASEPATH'))
    exit('No direct script access allowed');

class Measure extends MY_Controller {

    function __construct() {
        parent::__construct();

        $this->load->library('form_validation');
        $this->load->library('helpers');
        $this->load->helper('algoritm');
        $this->data['title'] = 'Measure';


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
        $this->render();
    }

    private function upload_record_webshoot($ext_url, $url_name) {
        $file = file_get_contents($ext_url);
        $type = 'png';
        $dir = realpath(BASEPATH . "../webroot/webshoots");
        if (!file_exists($dir)) {
            mkdir($dir);
            chmod($dir, 0777);
        }
        // --- NEW STUFF (TIMESTAMP BASED IMAGES NAMES) (START)
        $url_name = $url_name . "-" . date('Y-m-d-H-i-s', time());
        // --- NEW STUFF (TIMESTAMP BASED IMAGES NAMES) (END)
        $t = file_put_contents($dir . "/$url_name.$type", $file);
        $path = base_url() . "webshoots/$url_name.$type";
        $res = array(
            'path' => $path,
            'dir' => $dir . "/$url_name.$type"
        );
        return $res;
    }

    private function urlExists($url) {
        if ($url === null || trim($url) === "")
            return false;
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_TIMEOUT, 5);
        curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        $data = curl_exec($ch);
        $httpcode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        if ($httpcode >= 200 && $httpcode <= 302) {
            return true;
        } else {
            return false;
        }
    }

    private function check_screen_crawl_status($url) {
        $this->load->model('webshoots_model');
        return $this->webshoots_model->checkScreenCrawlStatus($url);
    }

    public function webshootcrawlall() {
        $customers = $this->customers_list_new();
        $this->load->model('webshoots_model');
        $uid = $this->ion_auth->get_user_id();
        $week = date("W", time());
        $year = date("Y", time());
        $sites = array();
        foreach ($customers as $k => $v) {
            if ($this->urlExists($v['name_val']))
                $sites[] = $v['name_val'];
        }
        foreach ($sites as $url) {
            $url = urlencode(trim($url));
            // -- configs (start)
            $api_key = "dc598f9ae119a97234ea";
            $api_secret = "47c7248bc03fbd368362";
            $token = md5("$api_secret+$url");
            $size_s = "w600";
            $size_l = "w1260";
            $format = "png";
            // -- configs (end)
            $res = array(
                "s" => "http://api.webyshots.com/v1/shot/$api_key/$token/?url=$url&dimension=$size_s&format=$format",
                'l' => "http://api.webyshots.com/v1/shot/$api_key/$token/?url=$url&dimension=$size_l&format=$format"
            );
            $crawl_s = $this->upload_record_webshoot($res['s'], $url . "_small");
            $crawl_l = $this->upload_record_webshoot($res['l'], $url . "_big");
            $result = array(
                'state' => false,
                'url' => $url,
                'small_crawl' => $crawl_s['path'],
                'big_crawl' => $crawl_l['path'],
                'dir_thumb' => $crawl_s['dir'],
                'dir_img' => $crawl_l['dir'],
                'uid' => $uid,
                'year' => $year,
                'week' => $week,
                'pos' => 0
            );
            $insert_id = $this->webshoots_model->recordUpdateWebshoot($result);
        }
        $this->output->set_content_type('application/json')->set_output(true);
    }

    public function dropselectionscan() {
        $year = $this->input->post('year');
        $week = $this->input->post('week');
        $uid = $this->ion_auth->get_user_id();
        $this->load->model('webshoots_model');
        $res = array();
        for ($i = 1; $i <= 6; $i++) {
            $mid = array(
                'pos' => $i,
                'cell' => $this->webshoots_model->getScreenCellSelection($i, $uid, $year, $week)
            );
            $res[] = $mid;
        }
        $this->output->set_content_type('application/json')->set_output(json_encode($res));
    }

    public function getwebshootbyurl() {
        ini_set("max_execution_time", 0);
        $year = $this->input->post('year');
        $week = $this->input->post('week');
        $url = $this->input->post('url');
        $pos = $this->input->post('pos');
        $uid = $this->ion_auth->get_user_id();
        $this->load->model('webshoots_model');
        $res = $this->webshoots_model->getWebShootByUrl($url);
        if ($res !== false) {
            $screen_id = $res->id;
            $this->webshoots_model->recordWebShootSelectionAttempt($screen_id, $uid, $pos, $year, $week, $res->img, $res->thumb, $res->stamp, $res->url); // --- webshoot selection record attempt
            $result = $res;
        } else { // --- crawl brand new screenshot
            $url = urlencode(trim($url));
            // -- configs (start)
            $api_key = "dc598f9ae119a97234ea";
            $api_secret = "47c7248bc03fbd368362";
            $token = md5("$api_secret+$url");
            // $size_s = "200x150";
            // $size_l = "600x450";
            // $size_s = "800x600";
            // $size_l = "1200x1000";
            $size_s = "w600";
            $size_l = "w1260";
            $format = "png";
            // -- configs (end)
            // http://api.webyshots.com/v1/shot/dc598f9ae119a97234ea/04921f81ebf1786b24ff0823ba1488b2/?url=google.com&dimension=w1260&format=png
            $res = array(
                "s" => "http://api.webyshots.com/v1/shot/$api_key/$token/?url=$url&dimension=$size_s&format=$format",
                'l' => "http://api.webyshots.com/v1/shot/$api_key/$token/?url=$url&dimension=$size_l&format=$format"
            );
            $crawl_s = $this->upload_record_webshoot($res['s'], $url . "_small");
            $crawl_l = $this->upload_record_webshoot($res['l'], $url . "_big");
            $result = array(
                'state' => false,
                'url' => $url,
                'small_crawl' => $crawl_s['path'],
                'big_crawl' => $crawl_l['path'],
                'dir_thumb' => $crawl_s['dir'],
                'dir_img' => $crawl_l['dir'],
                'uid' => $uid,
                'year' => $year,
                'week' => $week,
                'pos' => $pos
            );
            $insert_id = $this->webshoots_model->recordUpdateWebshoot($result);
            $result = $this->webshoots_model->getWebshootDataById($insert_id);
            $this->webshoots_model->recordWebShootSelectionAttempt($insert_id, $uid, $pos, $year, $week, $result->img, $result->thumb, $result->stamp, $result->url); // --- webshoot selection record attempt
        }
        $this->output->set_content_type('application/json')->set_output(json_encode($result));
    }

    public function getwebshootdata() {
        $url = $this->input->post('url');
        $this->load->model('webshoots_model');
        $res = $this->webshoots_model->getWebshootData($url);
        $this->output->set_content_type('application/json')->set_output(json_encode($res));
    }

    public function getcustomerslist_crawl() {
        $cs = $this->customers_list_new();
        $res = array();
        foreach ($cs as $k => $v) {
            $mid = array(
                'id' => $v['id'],
                'name' => $v['name'],
                'crawl_st' => $this->check_screen_crawl_status($v['name'])
            );
            $res[] = $mid;
        }
        $this->output->set_content_type('application/json')->set_output(json_encode($res));
    }

    public function webshootcrawl() {
        ini_set("max_execution_time", 0);
        // $year = $this->input->post('year');
        // $week = $this->input->post('week');
        $week = date("W", time());
        $year = date("Y", time());
        $url = $this->input->post('url');
        $url = urlencode(trim($url));
        $uid = $this->ion_auth->get_user_id();
        // -- configs (start)
        $api_key = "dc598f9ae119a97234ea";
        $api_secret = "47c7248bc03fbd368362";
        $token = md5("$api_secret+$url");
        // $size_s = "200x150";
        // $size_l = "600x450";
        // $size_s = "800x600";
        // $size_l = "1200x1000";
        $size_s = "w600";
        $size_l = "w1260";
        $format = "png";
        // -- configs (end)
        $res = array(
            "s" => "http://api.webyshots.com/v1/shot/$api_key/$token/?url=$url&dimension=$size_s&format=$format",
            'l' => "http://api.webyshots.com/v1/shot/$api_key/$token/?url=$url&dimension=$size_l&format=$format"
        );
        $crawl_s = $this->upload_record_webshoot($res['s'], $url . "_small");
        $crawl_l = $this->upload_record_webshoot($res['l'], $url . "_big");
        $result = array(
            'state' => false,
            'url' => $url,
            'small_crawl' => $crawl_s['path'],
            'big_crawl' => $crawl_l['path'],
            'dir_thumb' => $crawl_s['dir'],
            'dir_img' => $crawl_l['dir'],
            'uid' => $uid,
            'year' => $year,
            'week' => $week,
            'pos' => 0
        );
        $this->load->model('webshoots_model');
        $r = $this->webshoots_model->recordUpdateWebshoot($result);
        if ($r > 0)
            $result['state'] = true;
        $this->output->set_content_type('application/json')->set_output(json_encode($result));
    }

    public function rec_emails_reports_recipient() {
        $recs_arr = $this->input->post('recs_arr');
        $rec_day = $this->input->post('rec_day');
        $this->load->model('webshoots_model');
        $this->webshoots_model->rec_emails_reports_recipient($rec_day, $recs_arr);
        $this->output->set_content_type('application/json')->set_output(true);
    }

    public function timelineblock() {
        $first_cwp = $this->input->post('first_cwp');
        $last_cwp = $this->input->post('last_cwp');
        $state = $this->input->post('state');
        $week = date("W", time());
        $data = array(
            'first_cwp' => $first_cwp,
            'last_cwp' => $last_cwp,
            'state' => $state,
            'week' => $week
        );
        $this->load->view('measure/timelineblock', $data);
    }

    public function gethomepageyeardata() {
        $this->load->model('webshoots_model');
        $year = $this->input->post('year');
        $week = $this->input->post('week');
        if ($year == date('Y', time())) {
            $c_week = date("W", time());
            $c_year = date("Y", time());
            $data = array(
                'year' => $c_year,
                'week' => $c_week,
                'ct_final' => date("m.d.Y", time()),
                'customers_list' => $this->customers_list_new(),
                'status' => 'current',
                'img_av' => $this->webshoots_model->getWeekAvailableScreens($c_week, $year)
            );
        } else {
            $week = 1;
            $year_s = "01/01/" . $this->input->post('year');
            $i = ($week - 1) * 7;
            $total = strtotime($year_s) + 60 * 60 * 24 * $i;
            $ct_final = date('m.d.Y', $total);
            $data = array(
                'year' => $year,
                'week' => $week,
                'ct_final' => $ct_final,
                'customers_list' => $this->customers_list_new(),
                'status' => 'selected',
                'img_av' => $this->webshoots_model->getWeekAvailableScreens($week, $year)
            );
        }
        $this->load->view('measure/gethomepageyeardata', $data);
    }

    public function gethomepageweekdata() {
        $this->load->model('webshoots_model');
        $year = $this->input->post('year');
        $week = $this->input->post('week');
        $year_s = "01/01/" . $this->input->post('year');
        // ---- figure out total date (start)
        $i = ($week - 1) * 7;
        $total = strtotime($year_s) + 60 * 60 * 24 * $i;
        $ct_final = date('m.d.Y', $total);
        // ---- figure out total date (end)
        $data = array(
            'year' => $year,
            'week' => $week,
            'ct_final' => $ct_final,
            'customers_list' => $this->customers_list_new(),
            'img_av' => $this->webshoots_model->getWeekAvailableScreens($week, $year)
        );
        $this->load->view('measure/gethomepageweekdata', $data);
    }

    public function measure_products() {
        $this->data['category_list'] = $this->category_full_list();
        $this->data['customers_list'] = $this->category_customers_list();
        $this->load->model('batches_model');
        $batches = $this->batches_model->getAll();
        $batches_list = array(0 => 'Choose Batch');
        //Max
        foreach ($batches as $batch) {
            $batches_list[$batch->title] = $batch->title;
        }
        //Max
        $this->data['batches_list'] = $batches_list;
        $this->render();
    }

    public function measure_departments() {
        $this->load->model('department_model');

        foreach ($this->department_model->getAll() as $row) {
            ;
            $this->data['departmens_list'][$row->id] = $row->short_name;
        }

        $this->data['customers_list'] = $this->customers_list_new();
        $this->render();
    }

    public function measure_categories() {
        $this->render();
    }

    public function measure_pricing() {
        $this->render();
    }

    public function get_product_price() {
        $this->load->model('crawler_list_prices_model');

        $price_list = $this->crawler_list_prices_model->get_products_with_price();

        if (!empty($price_list['total_rows'])) {
            $total_rows = $price_list['total_rows'];
        } else {
            $total_rows = 0;
        }

        $output = array(
            "sEcho" => intval($_GET['sEcho']),
            "iTotalRecords" => $total_rows,
            "iTotalDisplayRecords" => $total_rows,
            "iDisplayLength" => $price_list['display_length'],
            "aaData" => array()
        );

        if (!empty($price_list['result'])) {
            foreach ($price_list['result'] as $price) {
                $parsed_attributes = unserialize($price->parsed_attributes);
                $model = (!empty($parsed_attributes['model']) ? $parsed_attributes['model'] : $parsed_attributes['UPC/EAN/ISBN']);
                $output['aaData'][] = array(
                    $price->created,
                    '<a href ="' . $price->url . '">' . substr($price->url, 0, 60) . '</a>',
                    $model,
                    $price->product_name,
                    sprintf("%01.2f", $price->price),
                );
            }
        }

        $this->output->set_content_type('application/json')
                ->set_output(json_encode($output));
    }

    private function category_full_list() {
        $this->load->model('category_model');
        $categories = $this->category_model->getAll();
        return $categories;
    }

    private function customers_list_new() {
        $this->load->model('customers_model');
        $output = array();
        $customers_init_list = $this->customers_model->getAll();
        if (count($customers_init_list) > 0) {
            foreach ($customers_init_list as $key => $value) {
                $mid = array(
                    'id' => $value->id,
                    'desc' => $value->description,
                    'image_url' => $value->image_url,
                    'name' => $value->name,
                    'name_val' => strtolower($value->name)
                );
                $output[] = $mid;
            }
        }
        return $output;
    }

    public function getcustomerslist_general() {
        $output = $this->customers_list_new();
        $this->output->set_content_type('application/json')->set_output(json_encode($output));
    }

    private function category_customers_list() {
        $this->load->model('customers_model');
        $output = array();
        $customers_init_list = $this->customers_model->getAll();
        if (count($customers_init_list) > 0) {
            foreach ($customers_init_list as $key => $value) {
                $n = strtolower($value->name);
                $output[] = $n;
            }
        }
        $output = array_unique($output);
        return $output;
    }

    public function cisearchteram() {
        // $q = $this->input->get('term'); // OLD
        $q = $this->input->get('q'); // NEW
        $sl = $this->input->get('sl');
        $cat = $this->input->get('cat');
        $this->load->model('imported_data_parsed_model');
        $data = $this->imported_data_parsed_model->getData($q, $sl, $cat_id, 4);
        foreach ($data as $key => $value) {
            $response[] = array('id' => $value['imported_data_id'], 'value' => $value['product_name']);
        };
        $this->output->set_content_type('application/json')->set_output(json_encode($response));
    }

//Max

    public function compare_text($first_text, $second_text) {

        $a = array_unique(explode(' ', $first_text));
        $b = array_unique(explode(' ', $second_text));
        $count = 0;
        foreach ($a as $val) {
            if (in_array($val, $b)) {
                $count++;
            }
        }

        $prc = $count / count($a) * 100;
        return $prc;
    }

    public function gridview() {
        $im_data_id = $this->input->post('im_data_id');

        $data = array(
            'im_data_id' => $im_data_id,
            's_product' => array(),
            's_product_short_desc_count' => 0,
            's_product_long_desc_count' => 0,
            'seo' => array('short' => array(), 'long' => array()),
            'same_pr' => array()
        );
        if ($im_data_id !== null && is_numeric($im_data_id)) {

            // --- GET SELECTED RPODUCT DATA (START)
            $this->load->model('imported_data_parsed_model');
            $data_import = $this->imported_data_parsed_model->getByImId($im_data_id);

            if ($data_import['description'] !== null && trim($data_import['description']) !== "") {
                $data_import['description'] = preg_replace('/\s+/', ' ', $data_import['description']);
                // $data_import['description'] = preg_replace('/[^A-Za-z0-9\. -!]/', ' ', $data_import['description']);
                $data['s_product_short_desc_count'] = count(explode(" ", $data_import['description']));
            }
            if ($data_import['long_description'] !== null && trim($data_import['long_description']) !== "") {
                $data_import['long_description'] = preg_replace('/\s+/', ' ', $data_import['long_description']);
                // $data_import['long_description'] = preg_replace('/[^A-Za-z0-9\. -!]/', ' ', $data_import['long_description']);
                $data['s_product_long_desc_count'] = count(explode(" ", $data_import['long_description']));
            }
            $data['s_product'] = $data_import;
            // --- GET SELECTED RPODUCT DATA (END)
            // --- ATTEMPT TO GET 'SAME' FROM 'HUMAN INTERFACE' (products_compare table) (START)
            $same_pr = $this->imported_data_parsed_model->getSameProductsHuman($im_data_id);

            // get similar by parsed_attributes
            if (empty($same_pr) && isset($data_import['parsed_attributes']) && isset($data_import['parsed_attributes']['model'])) {
                $strict = $this->input->post('strict');
                $same_pr = $this->imported_data_parsed_model->getByParsedAttributes($data_import['parsed_attributes']['model'], $strict);
            }

            if (empty($same_pr) && isset($data_import['parsed_attributes']) && isset($data_import['parsed_attributes']['UPC/EAN/ISBN'])) {
                $same_pr = $this->imported_data_parsed_model->getByParsedAttributes($data_import['parsed_attributes']['UPC/EAN/ISBN']);
            }

            // get similar for first row
            $this->load->model('similar_imported_data_model');

            $customers_list = array();
            $query_cus = $this->similar_imported_data_model->db->order_by('name', 'asc')->get('customers');
            $query_cus_res = $query_cus->result();
            if (count($query_cus_res) > 0) {
                foreach ($query_cus_res as $key => $value) {
                    $n = strtolower($value->name);
                    $customers_list[] = $n;
                }
            }
            $customers_list = array_unique($customers_list);

            if (empty($same_pr) && ($group_id = $this->similar_imported_data_model->findByImportedDataId($im_data_id))) {
                if ($rows = $this->similar_imported_data_model->getImportedDataByGroupId($group_id)) {
                    $data_similar = array();

                    foreach ($rows as $key => $row) {
                        $data_similar[$key] = $this->imported_data_parsed_model->getByImId($row->imported_data_id);
                        $data_similar[$key]['imported_data_id'] = $row->imported_data_id;

                        $cus_val = "";
                        foreach ($customers_list as $ki => $vi) {
                            if (strpos($data_similar[$key]['url'], "$vi") !== false) {
                                $cus_val = $vi;
                            }
                        }
                        if ($cus_val !== "")
                            $data_similar[$key]['customer'] = $cus_val;
                    }

                    if (!empty($data_similar)) {
                        $same_pr = $data_similar;
                    }
                }
            }
//            print "<pre>";
//            print_r($same_pr);
//            print "</pre>";
//            die();
            $compare_description = array();
            foreach ($same_pr as $key => $value) {
                if (!empty($value['description'])) {
                    $compare_description[$key] = $value['description'];
                } 
            }
            foreach ($compare_description as $key => $value) {
                $result = round(total_matches($key, $compare_description), 2);
                if ($result > 90) {
                    $same_pr[$key]['short_original'] = $result . '%';//'No'; //round($result, 2) . '%';
                } elseif (!$result) {
                    $same_pr[$key]['short_original'] = $result . '%';//'Yes';
                } else {
                    $same_pr[$key]['short_original'] = $result . '%';//'Yes';
                }
//                $same_pr[$key]= $vs;
            }

            $compare_description = array();
            foreach ($same_pr as $key => $value) {
                if (!empty($value['long_description'])) {
                    $compare_description[$key] = $value['long_description'];
                }
            }
            foreach ($compare_description as $key => $value) {
                $result = total_matches($key, $compare_description);
                if ($result > 90) {
                    $same_pr[$key]['long_original'] = round($result, 2) . '%';
                } elseif (!$result) {
                    $same_pr[$key]['long_original'] = round($result, 2) . '%';//'Yes';
                } else {
                    $same_pr[$key]['long_original'] = round($result, 2) . '%';//'Yes';
                }
//                $same_pr[$key]= $vs;
            }



//			if(count($same_pr) === 3) {
            foreach ($same_pr as $ks => $vs) {
                $same_pr[$ks]['seo']['short'] = $this->helpers->measure_analyzer_start_v2(preg_replace('/\s+/', ' ', $vs['description']));
                $same_pr[$ks]['seo']['long'] = $this->helpers->measure_analyzer_start_v2(preg_replace('/\s+/', ' ', $vs['long_description']));

                // three last prices
                $imported_data_id = $same_pr[$ks]['imported_data_id'];
                $three_last_prices = $this->imported_data_parsed_model->getLastPrices($imported_data_id);
                $same_pr[$ks]['three_last_prices'] = $three_last_prices;
            }



            //Max          
//      foreach($same_pr as $ks => $vs) {
//         $maxshort=0;
//         $maxlong=0;
//         
//         foreach($same_pr as $ks1 => $vs1 ){
//             
//           if($ks!=$ks1){
//           if($vs['description']!=''){
//                if($vs1['description']!=''){
//                     $percent=$this->compare_text($vs['description'],$vs1['description']);
//                     if($percent>$maxshort){
//                     $maxshort=$percent;}
//                }
//            
//                if($vs1['long_description']!=''){
//                     $percent=$this->compare_text($vs['description'],$vs1['long_description']);
//                     if($percent>$maxshort){
//                     $maxshort=$percent;}
//                }
//                }
//            
//            if($vs['long_description']!=''){
//                if($vs1['description']!=''){
//                 $percent=$this->compare_text($vs['long_description'],$vs1['description']);
//                 if($percent>$maxlong){
//                 $maxlong=$percent;}
//                 }
//            
//                if($vs1['long_description']!=''){
//                     $percent=$this->compare_text($vs['long_description'],$vs1['long_description']);
//                     if($percent>$maxlong){
//                     $maxlong=$percent;}
//                }
//            }
//           }    
//            }
//            if($maxshort>90){
//                $vs['short_original']=round($maxshort,2).'%';
//                //$vs['short_original']="No";
//            }else{
//                $vs['short_original']=round($maxshort,2).'%'; 
//               //$vs['short_original']="Yes";
//            }
//            
//            if($maxlong>90){
//                $vs['long_original']=round($maxlong,2).'%';
//            }else{
//               $vs['long_original']=round($maxlong,2).'%'; 
//                 }
//              $same_pr[$ks]= $vs; 
//              
//            }
            //Max                                              

            $data['same_pr'] = $same_pr;
//            }
            // --- ATTEMPT TO GET 'SAME' FROM 'HUMAN INTERFACE' (products_compare table) (END)
            // --- GET SELECTED RPODUCT SEO DATA (TMP) (START)
            if ($data_import['description'] !== null && trim($data_import['description']) !== "") {
                $data['seo']['short'] = $this->helpers->measure_analyzer_start_v2($data_import['description']);
            }
            if ($data_import['long_description'] !== null && trim($data_import['long_description']) !== "") {
                $data['seo']['long'] = $this->helpers->measure_analyzer_start_v2($data_import['long_description']);
            }
            // --- GET SELECTED RPODUCT SEO DATA (TMP) (END)
        }

        // -------- COMPARING V1 (START)
        $s_term = $this->input->post('s_term');

        // -------- COMPARING V1 (END)

        $this->load->view('measure/gridview', $data);
    }

    public function getcustomerslist_new() {
        $this->load->model('customers_model');
        $this->load->model('users_to_customers_model');
        $admin = $this->ion_auth->is_admin($this->ion_auth->get_user_id());
        $customers_init_list = $this->users_to_customers_model->getByUserId($this->ion_auth->get_user_id());
        if (count($customers_init_list) == 0 && $admin) {
            $customers_init_list = $this->customers_model->getAll();
        }

        if (count($customers_init_list) > 0) {
            if (count($customers_init_list) != 1) {
                $output[] = array('text' => 'All Customers',
                    'value' => 'All Customers',
                    'image' => ''
                );
            }
            foreach ($customers_init_list as $key => $value) {
                $output[] = array('text' => '',
                    'value' => strtolower($value->name),
                    'image' => base_url() . 'img/' . $value->image_url
                );
            }
        } else {
            $output[] = array('text' => 'No Customers',
                'value' => 'No Customers',
                'image' => ''
            );
        }
        $this->output->set_content_type('application/json')->set_output(json_encode($output));
    }

    public function getsiteslist_new() {
        $this->load->model('sites_model');
        $customers_init_list = $this->sites_model->getAll();
        if (count($customers_init_list) > 0) {
            $output[] = array('text' => 'All sites',
                'value' => 'All sites',
                'image' => ''
            );
            foreach ($customers_init_list as $key => $value) {
                $output[] = array('text' => '',
                    'value' => strtolower($value->name),
                    'image' => base_url() . 'img/' . $value->image_url
                );
            }
        }
        $this->output->set_content_type('application/json')->set_output(json_encode($output));
    }

    public function getcustomerslist() {
        $this->load->model('customers_model');
        $output = array();
        $customers_init_list = $this->customers_model->getAll();
        if (count($customers_init_list) > 0) {
            foreach ($customers_init_list as $key => $value) {
                $n = strtolower($value->name);
                $output[] = $n;
            }
        }
        $output = array_unique($output);
        $this->output->set_content_type('application/json')->set_output(json_encode($output));
    }

    public function analyzestring() {
        $clean_t = $this->input->post('clean_t');
        $output = $this->helpers->measure_analyzer_start_v2($clean_t);
        $this->output->set_content_type('application/json')->set_output(json_encode($output));
    }

    public function analyzekeywords() {
        $primary_ph = $this->input->post('primary_ph');
        $secondary_ph = $this->input->post('secondary_ph');
        $tertiary_ph = $this->input->post('tertiary_ph');
        $short_desc = $this->input->post('short_desc');
        $long_desc = $this->input->post('long_desc');
        $output = $this->helpers->measure_analyzer_keywords($primary_ph, $secondary_ph, $tertiary_ph, $short_desc, $long_desc);
        $this->output->set_content_type('application/json')->set_output(json_encode($output));
    }

    public function searchmeasuredball() {
        $batch_id = $this->input->post('batch_id');
        if (!$batch_id) {
            $s = $this->input->post('s');
            $sl = $this->input->post('sl');
            $cat_id = $this->input->post('cat');
            $limit = $this->input->post('limit');
            $this->load->model('imported_data_parsed_model');
            $data = array(
                'search_results' => array()
            );

            if ($limit !== 0) {
                $data_import = $this->imported_data_parsed_model->getData($s, $sl, $cat_id, $limit);
            } else {
                $data_import = $this->imported_data_parsed_model->getData($s, $sl, $cat_id);
            }

            if (empty($data_import)) {
                $this->load->library('PageProcessor');
                if ($this->pageprocessor->isURL($this->input->post('s'))) {
                    $parsed_data = $this->pageprocessor->get_data($this->input->post('s'));
                    $data_import[0] = $parsed_data;
                    $data_import[0]['url'] = $this->input->post('s');
                    $data_import[0]['imported_data_id'] = 0;
                }
            }

            $data['search_results'] = $data_import;
            $this->load->view('measure/searchmeasuredball', $data);
        } else {
            $this->load->model('research_data_model');

            $result = $this->research_data_model->get_by_batch_id($batch_id);


            $data['search_results'] = $result;

            $this->load->view('measure/searchmeasuredball', $data);
        }
    }

    public function attributesmeasure() {

        $s = $this->input->post('s');

        $data = array('search_results' => '', 'file_id' => '', 'product_descriptions' => '', 'product_title' => '');
        $attributes = array();

        $attr_path = $this->config->item('attr_path');

        if ($path = realpath($attr_path)) {
            $objects = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($path), RecursiveIteratorIterator::SELF_FIRST);
            foreach ($objects as $name => $object) {
                if (!$object->isDir()) {
                    if ($object->getFilename() == 'attributes.dat') {
                        if ($content = file_get_contents($name)) {
                            if (preg_match("/$s/i", $content, $matches)) {

                                $part = str_ireplace($attr_path, '', $object->getPath());
                                if (preg_match('/\D*(\d*)/i', $part, $matches)) {
                                    $data['file_id'] = $matches[1];
                                }

                                foreach ($this->config->item('attr_replace') as $replacement) {
                                    $content = str_replace(array_keys($replacement), array_values($replacement), $content);
                                }

                                $data['search_results'] = nl2br($content);

                                if (preg_match_all('/\s?(\S*)\s*(.*)/i', $content, $matches)) {
                                    foreach ($matches[1] as $i => $v) {
                                        if (!empty($v))
                                            $attributes[strtoupper($v)] = $matches[2][$i];
                                    }
                                }

                                if (!empty($attributes)) {
                                    $title = array();
                                    foreach ($this->settings['product_title'] as $v) {
                                        if (isset($attributes[strtoupper($v)]))
                                            $title[] = $attributes[strtoupper($v)];
                                    }
                                    $data['product_title'] = implode(' ', $title);
                                    $data['attributes'] = $attributes;
                                }
                                break;
                            }
                        }
                    }
                }
            }
        }

        if ($this->system_settings['java_generator']) {
            $descCmd = str_replace($this->config->item('cmd_mask'), $data['file_id'], $this->system_settings['java_cmd']);
            if ($result = shell_exec($descCmd)) {
                if (preg_match_all('/\(.*\)\: "(.*)"/i', $result, $matches) && isset($matches[1]) && count($matches[1]) > 0) {
                    if (is_array($data['product_descriptions']))
                        $data['product_descriptions'] = array_merge($data['product_descriptions'], $matches[1]);
                    else
                        $data['product_descriptions'] = $matches[1];
                }
            }
        }
        if ($this->system_settings['python_generator']) {
            $descCmd = str_replace($this->config->item('cmd_mask'), $s, $this->system_settings['python_cmd']);
            if ($result = shell_exec($descCmd)) {
                if (preg_match_all('/.*ELECTR_DESCRIPTION:\s*(.*)\s*-{5,}/', $result, $matches)) {
                    if (is_array($data['product_descriptions']))
                        $data['product_descriptions'] = array_merge($data['product_descriptions'], $matches[1]);
                    else
                        $data['product_descriptions'] = $matches[1];
                }
            }
        }

        if (!empty($this->exceptions) && !empty($data['attributes'])) {
            foreach ($data['attributes'] as $key => $value) {
                foreach ($this->exceptions as $exception) {
                    if ($exception['attribute_name'] == $key AND $exception['attribute_value'] == $value) {
                        foreach ($data['product_descriptions'] as $pd_key => $product_description) {
                            foreach ($exception['exception_values'] as $exception_value) {
                                if (stristr($product_description, $exception_value)) {
                                    unset($data['product_descriptions'][$pd_key]);
                                }
                            }
                        }
                        sort($data['product_descriptions']);
                    }
                }
            }
        }

        $this->output->set_content_type('application/json')
                ->set_output(json_encode($data));
    }

}