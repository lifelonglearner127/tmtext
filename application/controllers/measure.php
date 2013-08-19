<?php

if (!defined('BASEPATH'))
    exit('No direct script access allowed');

class Measure extends MY_Controller {

    function __construct() {
        parent::__construct();

        $this->load->library('form_validation');
        $this->load->library('helpers');
        $this->load->helper('algoritm');
        $this->load->helper('comparebysimilarwordscount');
        $this->load->helper('baseurl');
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
        $this->data['webshoots_model'] = $this->webshoots_model;
        // $this->data['rec'] = $this->webshoots_model->get_recipients_list();
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

    public function get_emails_reports_recipient() {
        $this->load->model('webshoots_model');
        $data['rec'] = $this->webshoots_model->get_recipients_list();
        $this->load->view('measure/get_emails_reports_recipient', $data);
    }

    public function send_recipient_report_selected() {
        $this->load->model('webshoots_model');
        $selected_data = $this->input->post('selected_data');
        // -- email config (dev configurations) (start) --
        $this->load->library('email');
        $config['protocol'] = 'sendmail';
        $config['mailpath'] = '/usr/sbin/sendmail';
        $config['charset'] = 'UTF-8';
        $config['wordwrap'] = TRUE;
        $this->email->initialize($config);
        // -- email config (dev configurations) (end) --
        foreach ($selected_data as $k => $v) {
            $day = $v['day'];
            $email = $v['email'];
            $id = $v['id'];
            $this->email->from('ishulgin8@gmail.com', "Content Solutions");
            $this->email->to("$email");
            $this->email->subject('Content Solutions Screenshots Report');
            $this->email->message("Report screenshots in attachment. Preference day: $day.");
            // --- attachments (start)
            $debug_screens = $this->webshoots_model->getLimitedScreens(3);
            if(count($debug_screens) > 0) {
                foreach ($debug_screens as $key => $value) {
                    $path = $value->dir_thumb;
                    $this->email->attach("$path");
                }
            }
            // --- attachments (end)
            $this->email->send();
        }
        $this->output->set_content_type('application/json')->set_output(json_encode($this->email->print_debugger()));
    }

    public function send_recipient_report() {
        $this->load->model('webshoots_model');
        $id = $this->input->post('id');
        $email = $this->input->post('email');
        $day = $this->input->post('day');
        // --------------- email sender (start) ---------------
        // -- email config (dev configurations) (start) --
        $this->load->library('email');
        $config['protocol'] = 'sendmail';
        $config['mailpath'] = '/usr/sbin/sendmail';
        $config['charset'] = 'UTF-8';
        $config['wordwrap'] = TRUE;
        $this->email->initialize($config);
        // -- email config (dev configurations) (end) --
        $this->email->from('ishulgin8@gmail.com', "Content Solutions");
        $this->email->to("$email");
        $this->email->subject('Content Solutions Screenshots Report');
        $this->email->message("Report screenshots in attachment. Preference day: $day.");
        // --- attachments (start)
        $debug_screens = $this->webshoots_model->getLimitedScreens(3);
        if(count($debug_screens) > 0) {
            foreach ($debug_screens as $key => $value) {
                $path = $value->dir_thumb;
                $this->email->attach("$path");
            }
        }
        // --- attachments (end)
        $this->email->send();
        $this->output->set_content_type('application/json')->set_output(json_encode($this->email->print_debugger()));
        // --------------- email sender (end) -----------------
    }

    public function delete_recipient() {
        $this->load->model('webshoots_model');
        $id = $this->input->post('id');
        $res = $this->webshoots_model->delete_reports_recipient($id);
        $this->output->set_content_type('application/json')->set_output(json_encode($res));
    }

    private function crawl_webshoot($call_url, $id) {
        $file = file_get_contents($call_url);
        $type = 'png';
        $dir = realpath(BASEPATH . "../webroot/webshoots");
        if (!file_exists($dir)) {
            mkdir($dir);
            chmod($dir, 0777);
        }
        // --- NEW STUFF (TIMESTAMP BASED IMAGES NAMES) (START)
        $url_name = "crawl_snap-" . $id . "-" . date('Y-m-d-H-i-s', time());
        // --- NEW STUFF (TIMESTAMP BASED IMAGES NAMES) (END)
        $t = file_put_contents($dir . "/$url_name.$type", $file);
        $path = base_url() . "webshoots/$url_name.$type";
        $res = array(
            'path' => $path,
            'dir' => $dir . "/$url_name.$type",
            'img' => $url_name.".".$type
        );
        return $res;
    }

    public function crawlsnapshoot() {
        $this->load->model('webshoots_model');
        $urls = $this->input->post('urls');
        if(count($urls) > 0) {
            // -- snaps configs (start)
            $api_key = $this->config->item('webyshots_api_key');
            $api_secret = $this->config->item('webyshots_api_secret');
            $size = "w800";
            $format = "png";
            // -- snaps configs (end)
            foreach ($urls as $k => $v) {
                // ---- snap it and update crawler_list table (start)
                $url = preg_replace('#^https?://#', '', $v['url']);
                $r_url = urlencode(trim($url));
                $token = md5("$api_secret+$url");
                $call_url = "http://api.webyshots.com/v1/shot/$api_key/$token/?url=$r_url&dimension=$size&format=$format";
                $snap_res = $this->crawl_webshoot($call_url, $v['id']);
                $this->webshoots_model->updateCrawlListWithSnap($v['id'], $snap_res['img']);
                // ---- snap it and update crawler_list table (end)
            }
        }
        $this->output->set_content_type('application/json')->set_output(true);
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
            $api_key = $this->config->item('webyshots_api_key');
            $api_secret = $this->config->item('webyshots_api_secret');
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
        $label = $this->input->post('label');
        $uid = $this->ion_auth->get_user_id();
        $this->load->model('webshoots_model');
        $res = $this->webshoots_model->getWebShootByUrl($url);
        if ($res !== false) {
            $screen_id = $res->id;
            $this->webshoots_model->recordWebShootSelectionAttempt($screen_id, $uid, $pos, $year, $week, $res->img, $res->thumb, $res->stamp, $res->url, $label); // --- webshoot selection record attempt
            $result = $res;
        } else { // --- crawl brand new screenshot
            $url = urlencode(trim($url));
            // -- configs (start)
            $api_key = $this->config->item('webyshots_api_key');
            $api_secret = $this->config->item('webyshots_api_secret');
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
                'pos' => $pos
            );
            $insert_id = $this->webshoots_model->recordUpdateWebshoot($result);
            $result = $this->webshoots_model->getWebshootDataById($insert_id);
            $this->webshoots_model->recordWebShootSelectionAttempt($insert_id, $uid, $pos, $year, $week, $result->img, $result->thumb, $result->stamp, $result->url, $label); // --- webshoot selection record attempt
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
                'url' => $v['c_url'],
                // 'crawl_st' => $this->check_screen_crawl_status($v['name'])
                'crawl_st' => $this->check_screen_crawl_status($v['c_url'])
            );
            $res[] = $mid;
        }
        $this->output->set_content_type('application/json')->set_output(json_encode($res));
    }

    public function webshootcrawl() {
        ini_set("max_execution_time", 0);
        $week = date("W", time());
        $year = date("Y", time());
        $url = $this->input->post('url');
        $url = urlencode(trim($url));
        $uid = $this->ion_auth->get_user_id();
        // -- configs (start)
        $api_key = $this->config->item('webyshots_api_key');
        $api_secret = $this->config->item('webyshots_api_secret');
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
        $result = $this->webshoots_model->rec_emails_reports_recipient($rec_day, $recs_arr);
        $this->output->set_content_type('application/json')->set_output(json_encode($result));
    }

    public function get_screenshots_slider_data() {
        $this->load->model('webshoots_model');
        $week = $this->input->post('week');
        $year = $this->input->post('year');
        $data['img_av'] = $this->webshoots_model->getWeekAvailableScreens($week, $year);
        $this->load->view('measure/get_screenshots_slider_data', $data);
    }

    public function timelineblock() {
        $this->load->model('webshoots_model');
        $first_cwp = $this->input->post('first_cwp');
        $last_cwp = $this->input->post('last_cwp');
        $state = $this->input->post('state');
        $year = $this->input->post('year');
        $week = date("W", time());
        $data = array(
            'first_cwp' => $first_cwp,
            'last_cwp' => $last_cwp,
            'state' => $state,
            'week' => $week,
            'year' => $year,
            'webshoots_model' => $this->webshoots_model
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
                'img_av' => $this->webshoots_model->getWeekAvailableScreens($c_week, $year),
                'webshoots_model' => $this->webshoots_model,
                'user_id' => $this->ion_auth->get_user_id()
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
                'img_av' => $this->webshoots_model->getWeekAvailableScreens($week, $year),
                'webshoots_model' => $this->webshoots_model,
                'user_id' => $this->ion_auth->get_user_id()
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
            'img_av' => $this->webshoots_model->getWeekAvailableScreens($week, $year),
            'webshoots_model' => $this->webshoots_model,
            'user_id' => $this->ion_auth->get_user_id()
        );
        $this->load->view('measure/gethomepageweekdata', $data);
    }

    public function measure_products() {
        $this->load->model('sites_model');
        $sites = $this->sites_model->getAll();
        $this->data['sites'] = $sites;
        $this->data['customers_list'] = $this->category_customers_list();
        $this->load->model('department_members_model');
        $this->data['departmens_list'][] = 'All';
        foreach ($this->department_members_model->getAll() as $row) {
            $this->data['departmens_list'][$row->id] = $row->text;
        }
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
        $this->load->model('department_members_model');
        $this->load->model('site_categories_model');

        $this->data['departmens_list'][] = 'All';
        foreach ($this->department_members_model->getAllByCustomer('amazon') as $row) {
            $this->data['departmens_list'][$row->id] = $row->text;
        }
        $this->data['category_list'][] = 'All';
        foreach ($this->site_categories_model->getAll() as $row) {
            $this->data['category_list'][$row->id] = $row->text;
        }

        $this->data['customers_list'] = $this->customers_list_new();
        $this->render();
    }

    public function getDepartmentsByCustomer(){
        $this->load->model('department_members_model');
        $customer = explode(".", $this->input->post('customer_name'));
        $result = $this->department_members_model->getAllByCustomer(strtolower($customer[0]));
        $this->output->set_content_type('application/json')->set_output(json_encode($result));
    }

    public function getCategoriesByCustomer(){
        $this->load->model('sites_model');
        $this->load->model('site_categories_model');
        $site_id = $this->sites_model->getIdByName($this->input->post('customer_name'));
        $result = $this->site_categories_model->getAllBySiteId($site_id);
        $this->output->set_content_type('application/json')->set_output(json_encode($result));
    }

    public function getCategoriesByDepartment(){
        $this->load->model('site_categories_model');
        $this->load->model('sites_model');
        $department_id = $this->input->post('department_id');
        $site_id = $this->sites_model->getIdByName($this->input->post('site_name'));
        $result = $this->site_categories_model->getAllBySiteId($site_id, $department_id);
        $this->output->set_content_type('application/json')->set_output(json_encode($result));
    }

    public function getUrlByDepartment(){
        $this->load->model('department_members_model');
        $result = $this->department_members_model->getUrlByDepartment($this->input->post('department_id'));
        $this->output->set_content_type('application/json')->set_output(json_encode($result));
    }

    public function getUrlByCategory(){
        $this->load->model('site_categories_model');
        $result = $this->site_categories_model->getUrlByCategory($this->input->post('category_id'));
        $this->output->set_content_type('application/json')->set_output(json_encode($result));
    }

    public function measure_categories() {
        $this->render();
    }

    public function measure_social() {
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
        if($first_text===$second_text){
            return 100;
        }else{
        $a = explode(' ', $first_text);
        $b = explode(' ', $second_text);
        $count = 0;
        foreach ($a as $val) {
            if (in_array($val, $b)) {
                $count++;
            }
        }

        $prc = $count / count($a) * 100;
        return $prc;
        }
    }
    public function similar_groups(){
        $this->load->model('imported_data_parsed_model');
        $this->imported_data_parsed_model->similiarity_cron();
    }
    public function report_mismatch(){

        $group_id=$this->input->post('group_id');
        $im_data_id=$this->input->post('im_data_id');
        $this->load->model('similar_data_model');
        $this->similar_data_model->update($group_id,$im_data_id,1);
        $this->output->set_content_type('application/json')->set_output(json_encode("aaaaaaaa"));

    }

    function get_base_url($url)
    {
    $chars = preg_split('//', $url, -1, PREG_SPLIT_NO_EMPTY);

    $slash = 3; // 3rd slash

    $i = 0;

    foreach($chars as $key => $char)
    {
        if($char == '/')
        {
           $j = $i++;
        }

        if($i == 3)
        {
           $pos = $key; break;
        }
    }
if(preg_match('/www/',$url)){
$main_base = substr($url, 11, $pos-11);
}else{
   $main_base = substr($url, 7, $pos-7); 
}

return $main_base;
}
function matches_count($im_data_id){
     
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
            $this->load->model('similar_product_groups_model');
            $this->load->model('similar_data_model');
            $data_import = $this->imported_data_parsed_model->getByImId($im_data_id);

            $same_pr = $this->imported_data_parsed_model->getSameProductsHuman($im_data_id);

            // get similar by parsed_attributes
            if (empty($same_pr) && isset($data_import['parsed_attributes']) && isset($data_import['parsed_attributes']['model'])) {

                $strict = $this->input->post('strict');
                $same_pr = $this->imported_data_parsed_model->getByParsedAttributes($data_import['parsed_attributes']['model'], $strict);
            }

            if (empty($same_pr) && isset($data_import['parsed_attributes']) && isset($data_import['parsed_attributes']['UPC/EAN/ISBN'])) {

                $same_pr = $this->imported_data_parsed_model->getByParsedAttributes($data_import['parsed_attributes']['UPC/EAN/ISBN']);
            }
            if(empty($same_pr) && !isset($data_import['parsed_attributes']['model'])){
            $data['mismatch_button']=true;
            if (!$this->similar_product_groups_model->checkIfgroupExists($im_data_id)) {

                if (!isset($data_import['parsed_attributes'])) {

                    $same_pr = $this->imported_data_parsed_model->getByProductName($im_data_id, $data_import['product_name'], '', $strict);
                }
                if (isset($data_import['parsed_attributes']) ) {

                    $same_pr = $this->imported_data_parsed_model->getByProductName($im_data_id, $data_import['product_name'], $data_import['parsed_attributes']['manufacturer'], $strict);
                }
            } else {
                $this->load->model('similar_imported_data_model');
                $customers_list = array();
                $query_cus = $this->similar_imported_data_model->db->order_by('name', 'asc')->get('customers');
                $query_cus_res = $query_cus->result();
                if (count($query_cus_res) > 0) {
                    foreach ($query_cus_res as $key => $value) {
                        $n = parse_url($value->url);
                        $customers_list[] = $n['host'];
                    }
                }
                $customers_list = array_unique($customers_list);
                $rows = $this->similar_data_model->getByGroupId($im_data_id);
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
            // get similar for first row
            $this->load->model('similar_imported_data_model');

            $customers_list = array();
            $query_cus = $this->similar_imported_data_model->db->order_by('name', 'asc')->get('customers');
            $query_cus_res = $query_cus->result();
            if (count($query_cus_res) > 0) {
                foreach ($query_cus_res as $key => $value) {
                    $n = parse_url($value->url);
                    $customers_list[] = $n['host'];
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

            foreach ($same_pr as $ks => $vs) {

                if ($this->get_base_url($vs['url']) == $this->get_base_url($selectedUrl)) {
                    if ($ks != 0) {
                        $same_pr[] = $same_pr[0];
                        $same_pr[0] = $vs;
                        unset($same_pr[$ks]);
                    }
                }
            }
            foreach ($same_pr as $ks => $vs) {
                if($vs['customer']==''){
                $this->load->model('sites_model');
                   if($this->get_base_url($vs['url'])=='shop.nordstrom.com'){
                      $same_pr[$ks]['customer']='nordstrom' ;
                   }else{
                       //echo $this->get_base_url($vs['url']);
                       //echo 'bbb'.strtolower($this->sites_model->get_name_by_url($this->get_base_url($vs['url']))).'aaaaaaaaa';
                   $same_pr[$ks]['customer']=  strtolower($this->sites_model->get_name_by_url($this->get_base_url($vs['url'])));
                   }
                }
            }
           
        $matched_sites=array();
        foreach($same_pr as $ks => $vs){
           $matched_sites[]=strtolower($vs['customer']);
        }
        
        // -------- COMPARING V1 (START)
        return $matched_sites;
        }
        
}
public function gridview() {
       $data['mismatch_button']=false;
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
            $this->load->model('similar_product_groups_model');
            $this->load->model('similar_data_model');
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
            if(empty($same_pr) && !isset($data_import['parsed_attributes']['model'])){
            $data['mismatch_button']=true;
            if (!$this->similar_product_groups_model->checkIfgroupExists($im_data_id)) {

                if (!isset($data_import['parsed_attributes'])) {

                    $same_pr = $this->imported_data_parsed_model->getByProductName($im_data_id, $data_import['product_name'], '', $strict);
                }
                if (isset($data_import['parsed_attributes']) ) {

                    $same_pr = $this->imported_data_parsed_model->getByProductName($im_data_id, $data_import['product_name'], $data_import['parsed_attributes']['manufacturer'], $strict);
                }
            } else {
                $this->load->model('similar_imported_data_model');
                $customers_list = array();
                $query_cus = $this->similar_imported_data_model->db->order_by('name', 'asc')->get('sites');
                $query_cus_res = $query_cus->result();
                if (count($query_cus_res) > 0) {
                    foreach ($query_cus_res as $key => $value) {
                        $n = parse_url($value->url);
                        $customers_list[] = $n['host'];
                    }
                }
                $customers_list = array_unique($customers_list);
                $rows = $this->similar_data_model->getByGroupId($im_data_id);
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
            // get similar for first row
            $this->load->model('similar_imported_data_model');

            $customers_list = array();
            $query_cus = $this->similar_imported_data_model->db->order_by('name', 'asc')->get('sites');
            $query_cus_res = $query_cus->result();
            if (count($query_cus_res) > 0) {
                foreach ($query_cus_res as $key => $value) {
                    $n = parse_url($value->url);
                    $customers_list[] = $n['host'];
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
//            $compare_description = array();
//            foreach ($same_pr as $key => $value) {
//                if (!empty($value['description'])) {
//                    $compare_description[$key]['short'] = $value['description'];
//                }
//                if (!empty($value['long_description'])) {
//                    $compare_description[$key]['long'] = $value['long_description'];
//                }
//            }
//            $compare_description_short = array();
//            foreach ($same_pr as $key => $value) {
//                if (!empty($value['description'])) {
//                    $compare_description_short[$key] = $value['description'];
//                }
//            }
//            foreach ($compare_description_short as $key => $value) {
//                $result = round(total_matches($key, $compare_description, "short"), 2);
//                if ($result > 90) {
//                    $same_pr[$key]['short_original'] = $result . '%';//'No'; //round($result, 2) . '%';
//                } elseif (!$result) {
//                    $same_pr[$key]['short_original'] = $result . '%';//'Yes';
//                } else {
//                    $same_pr[$key]['short_original'] = $result . '%';//'Yes';
//                }
////                $same_pr[$key]= $vs;
//            }
//
//            $compare_description_long = array();
//            foreach ($same_pr as $key => $value) {
//                if (!empty($value['long_description'])) {
//                    $compare_description_long[$key] = $value['long_description'];
//                }
//            }
//            foreach ($compare_description_long as $key => $value) {
//                $result = total_matches($key, $compare_description,'long');
//                if ($result > 90) {
//                    $same_pr[$key]['long_original'] = round($result, 2) . '%';
//                } elseif (!$result) {
//                    $same_pr[$key]['long_original'] = round($result, 2) . '%';//'Yes';
//                } else {
//                    $same_pr[$key]['long_original'] = round($result, 2) . '%';//'Yes';
//                }
////                $same_pr[$key]= $vs;
//            }
//			if(count($same_pr) === 3) {
            foreach ($same_pr as $ks => $vs) {
                
                $this->load->model('sites_model');
                //echo $this->get_base_url($vs['url']);
                 //echo 'bbb'.strtolower($this->sites_model->get_name_by_url($this->get_base_url($vs['url']))).'aaaaaaaaa';
                
                $same_pr[$ks]['customer']=  strtolower($this->sites_model->get_name_by_url($same_pr[$ks]['customer']));
                $same_pr[$ks]['seo']['short'] = $this->helpers-> measure_analyzer_start_v2_product_name($vs['product_name'],preg_replace('/\s+/', ' ', $vs['description']));
                $same_pr[$ks]['seo']['long'] = $this->helpers->measure_analyzer_start_v2_product_name($vs['product_name'],preg_replace('/\s+/', ' ', $vs['long_description']));

                // three last prices
                $imported_data_id = $same_pr[$ks]['imported_data_id'];
                $three_last_prices = $this->imported_data_parsed_model->getLastPrices($imported_data_id);
                $same_pr[$ks]['three_last_prices'] = $three_last_prices;
                if(!empty($three_last_prices)){
                    $same_pr[$ks]['three_last_prices'] = $three_last_prices;
                }elseif($this->imported_data_parsed_model->PriceOld($imported_data_id)){
                     $same_pr[$ks]['three_last_prices']=array((object) array('price'=>$this->imported_data_parsed_model->PriceOld($imported_data_id), 'created'=>''));
                }else{
                    $same_pr[$ks]['three_last_prices'] = array();
                }

            }



            //     Max
            if (count($same_pr) != 1) {
                foreach ($same_pr as $ks => $vs) {
                    $maxshort = 0;
                    $maxlong = 0;
                    $k_sh = 0;
                    $k_lng = 0;
                    foreach ($same_pr as $ks1 => $vs1) {

                        if ($ks != $ks1) {
                            if ($vs['description'] != '') {
                                if ($vs1['description'] != '') {
                                    $k_sh++;
                                    $percent = $this->compare_text($vs['description'], $vs1['description']);
                                    if ($percent > $maxshort) {
                                        $maxshort = $percent;
                                    }
                                }

                                if ($vs1['long_description'] != '') {
                                    $k_sh++;
                                    $percent = $this->compare_text($vs['description'], $vs1['long_description']);
                                    if ($percent > $maxshort) {
                                        $maxshort = $percent;
                                    }
                                }
                            }

                            if ($vs['long_description'] != '') {

                                if ($vs1['description'] != '') {
                                    $k_lng++;
                                    $percent = $this->compare_text($vs['long_description'], $vs1['description']);
                                    if ($percent > $maxlong) {
                                        $maxlong = $percent;
                                    }
                                }

                                if ($vs1['long_description'] != '') {
                                    $k_lng++;
                                    $percent = $this->compare_text($vs['long_description'], $vs1['long_description']);
                                    if ($percent > $maxlong) {
                                        $maxlong = $percent;
                                    }
                                }
                            }
                        }
                    }
                    if($maxshort!=0){
                        $vs['short_original'] =  round($maxshort, 2) . '%';
                    }else{
                        $vs['short_original']= "Insufficient data";
                    }

                    if($maxlong!=0){
                        $vs['long_original'] =  round($maxlong, 2) . '%';
                    }else{
                        $vs['long_original']= "Insufficient data";
                    }

                    if ($k_lng == 0) {
                        $vs['long_original'] = "Insufficient data";
                    }
                    if ($k_sh == 0) {
                        $vs['short_original'] = "Insufficient data";
                    }

                    $same_pr[$ks] = $vs;
                }
            } else {
                $same_pr[0]['long_original'] = 'Insufficient data';
                $same_pr[0]['short_original'] = 'Insufficient data';
            }
            //   Max
//Max
            $selectedUrl = $this->input->post('selectedUrl');
            foreach ($same_pr as $ks => $vs) {

                if ($this->get_base_url($vs['url']) == $this->get_base_url($selectedUrl)) {
                    if ($ks != 0) {
                        $same_pr[] = $same_pr[0];
                        $same_pr[0] = $vs;
                        unset($same_pr[$ks]);
                    }
                }
            }

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
    
   
    function tableview(){
        if($same_pr=$this->input->post('result_data')){
          $data['ind0']=$this->input->post('ind0');
          $data['ind1']=$this->input->post('ind1');
          $data['same_pr'] =$same_pr;
          $this->load->view('measure/tableview', $data);  
        }else{
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
            $this->load->model('similar_product_groups_model');
            $this->load->model('similar_data_model');
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
            if(empty($same_pr) && !isset($data_import['parsed_attributes']['model'])){
            $data['mismatch_button']=true;
            if (!$this->similar_product_groups_model->checkIfgroupExists($im_data_id)) {

                if (!isset($data_import['parsed_attributes'])) {

                    $same_pr = $this->imported_data_parsed_model->getByProductName($im_data_id, $data_import['product_name'], '', $strict);
                }
                if (isset($data_import['parsed_attributes']) ) {

                    $same_pr = $this->imported_data_parsed_model->getByProductName($im_data_id, $data_import['product_name'], $data_import['parsed_attributes']['manufacturer'], $strict);
                }
            } else {
                $this->load->model('similar_imported_data_model');
                $customers_list = array();
                $query_cus = $this->similar_imported_data_model->db->order_by('name', 'asc')->get('customers');
                $query_cus_res = $query_cus->result();
                if (count($query_cus_res) > 0) {
                    foreach ($query_cus_res as $key => $value) {
                        $n = parse_url($value->url);
                        $customers_list[] = $n['host'];
                    }
                }
                $customers_list = array_unique($customers_list);
                $rows = $this->similar_data_model->getByGroupId($im_data_id);
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
            // get similar for first row
            $this->load->model('similar_imported_data_model');

            $customers_list = array();
            $query_cus = $this->similar_imported_data_model->db->order_by('name', 'asc')->get('customers');
            $query_cus_res = $query_cus->result();
            if (count($query_cus_res) > 0) {
                foreach ($query_cus_res as $key => $value) {
                    $n = parse_url($value->url);
                    $customers_list[] = $n['host'];
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

            foreach ($same_pr as $ks => $vs) {
                if($vs['customer']==''){
                $this->load->model('sites_model');
                   if($this->get_base_url($vs['url'])=='shop.nordstrom.com'){
                      $same_pr[$ks]['customer']='nordstrom' ;
                   }else{
                       //echo $this->get_base_url($vs['url']);
                       //echo 'bbb'.strtolower($this->sites_model->get_name_by_url($this->get_base_url($vs['url']))).'aaaaaaaaa';
                   $same_pr[$ks]['customer']=  strtolower($this->sites_model->get_name_by_url($this->get_base_url($vs['url'])));
                   }

                   }
                $same_pr[$ks]['seo']['short'] = $this->helpers-> measure_analyzer_start_v2_product_name($vs['product_name'],preg_replace('/\s+/', ' ', $vs['description']));
                $same_pr[$ks]['seo']['long'] = $this->helpers->measure_analyzer_start_v2_product_name($vs['product_name'],preg_replace('/\s+/', ' ', $vs['long_description']));

                // three last prices
                $imported_data_id = $same_pr[$ks]['imported_data_id'];
                $three_last_prices = $this->imported_data_parsed_model->getLastPrices($imported_data_id);
                $same_pr[$ks]['three_last_prices'] = $three_last_prices;
                if(!empty($three_last_prices)){
                    $same_pr[$ks]['three_last_prices'] = $three_last_prices;
                }elseif($this->imported_data_parsed_model->PriceOld($imported_data_id)){
                     $same_pr[$ks]['three_last_prices']=array((object) array('price'=>$this->imported_data_parsed_model->PriceOld($imported_data_id), 'created'=>''));
                }else{
                    $same_pr[$ks]['three_last_prices'] = array();
                }

            }



            //     Max
            if (count($same_pr) != 1) {
                foreach ($same_pr as $ks => $vs) {
                    $maxshort = 0;
                    $maxlong = 0;
                    $k_sh = 0;
                    $k_lng = 0;
                    foreach ($same_pr as $ks1 => $vs1) {

                        if ($ks != $ks1) {
                            if ($vs['description'] != '') {
                                if ($vs1['description'] != '') {
                                    $k_sh++;
                                    $percent = $this->compare_text($vs['description'], $vs1['description']);
                                    if ($percent > $maxshort) {
                                        $maxshort = $percent;
                                    }
                                }

                                if ($vs1['long_description'] != '') {
                                    $k_sh++;
                                    $percent = $this->compare_text($vs['description'], $vs1['long_description']);
                                    if ($percent > $maxshort) {
                                        $maxshort = $percent;
                                    }
                                }
                            }

                            if ($vs['long_description'] != '') {

                                if ($vs1['description'] != '') {
                                    $k_lng++;
                                    $percent = $this->compare_text($vs['long_description'], $vs1['description']);
                                    if ($percent > $maxlong) {
                                        $maxlong = $percent;
                                    }
                                }

                                if ($vs1['long_description'] != '') {
                                    $k_lng++;
                                    $percent = $this->compare_text($vs['long_description'], $vs1['long_description']);
                                    if ($percent > $maxlong) {
                                        $maxlong = $percent;
                                    }
                                }
                            }
                        }
                    }
                    if($maxshort!=0){
                        $vs['short_original'] =  round($maxshort, 2) . '%';
                    }else{
                        $vs['short_original']= "Insufficient data";
                    }

                    if($maxlong!=0){
                        $vs['long_original'] =  round($maxlong, 2) . '%';
                    }else{
                        $vs['long_original']= "Insufficient data";
                    }

                    if ($k_lng == 0) {
                        $vs['long_original'] = "Insufficient data";
                    }
                    if ($k_sh == 0) {
                        $vs['short_original'] = "Insufficient data";
                    }

                    $same_pr[$ks] = $vs;
                }
            } else {
                $same_pr[0]['long_original'] = 'Insufficient data';
                $same_pr[0]['short_original'] = 'Insufficient data';
            }
            //   Max
//Max
            $selectedUrl = $this->input->post('selectedUrl');
            foreach ($same_pr as $ks => $vs) {

                if ($this->get_base_url($vs['url']) == $this->get_base_url($selectedUrl)) {
                    if ($ks != 0) {
                        $same_pr[] = $same_pr[0];
                        $same_pr[0] = $vs;
                        unset($same_pr[$ks]);
                    }
                }
            }

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

        $this->load->view('measure/tableview', $data);
        }

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
        $selected_cites=$this->input->post('selected_cites');
        foreach($selected_cites as $key => $val){
            $selected_cites[$key]=  strtolower( $val);
        }
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
           
            if($selected_cites!=NULL){
                
                foreach($result as $kay => $val){
                     $matches_sites=$this->matches_count($val['imported_data_id']);
                     if(count(array_intersect($matches_sites,$selected_cites))==0){
                    
                        unset($result[$kay]);
                    }
                }
            }
            
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

    public function get_best_sellers()
    {
        $this->load->model('best_sellers_model');
        $this->load->model('sites_model');
        $department = '';
        if($this->input->post('site') != ''){
            $site_id = $this->sites_model->getIdByName($this->input->post('site'));
            if($this->input->post('department') != '' && $this->input->post('department') != 'All'){
                $department = $this->input->post('department');
            }
            $output = $this->best_sellers_model->getAllBySiteId($site_id, $department);
        } else{
            $output = $this->best_sellers_model->getAll();
        }
        $this->output->set_content_type('application/json')
            ->set_output(json_encode($output));
    }

}