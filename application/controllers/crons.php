<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Crons extends MY_Controller {

	function __construct() {
  		parent::__construct();
  		$this->load->library('ion_auth');
		$this->ion_auth->add_auth_rules(array(
  			'index' => true,
  			'screenscron' => true,
            'do_stats' => true,
            'hello'=>true
  		));
 	}

 	public function index() {

	}
	
	private function urlExists($url) {
        if($url === null || trim($url) === "") return false;  
        $ch = curl_init($url);  
        curl_setopt($ch, CURLOPT_TIMEOUT, 5);  
        curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);  
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);  
        $data = curl_exec($ch);  
        $httpcode = curl_getinfo($ch, CURLINFO_HTTP_CODE);  
        curl_close($ch);  
        if($httpcode>=200 && $httpcode<=302){  
            return true;  
        } else {  
            return false;  
        }  
    }

    private function customers_list() {
        $this->load->model('customers_model');
        $output = array();
        $customers_init_list = $this->customers_model->getAll();
        if(count($customers_init_list) > 0) {
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

    private function upload_record_webshoot($ext_url, $url_name) {
        $file = file_get_contents($ext_url);
        $type = 'png';
        $dir = realpath(BASEPATH."../webroot/webshoots");
        if(!file_exists($dir)) {
            mkdir($dir);
            chmod($dir, 0777);
        }
        // --- NEW STUFF (TIMESTAMP BASED IMAGES NAMES) (START)
        $url_name = $url_name."-".date('Y-m-d-H-i-s', time());
        // --- NEW STUFF (TIMESTAMP BASED IMAGES NAMES) (END)
        $t = file_put_contents($dir."/$url_name.$type", $file);
        $path = base_url()."webshoots/$url_name.$type";
        $res = array(
            'path' => $path,
            'dir' => $dir."/$url_name.$type"
        );
        return $res;
    }

	/**
     * Cron Job for CI home tab screenshots generating 
     */
	public function screenscron() {
		$customers = $this->customers_list();
        $this->load->model('webshoots_model');
        $week = date("W", time());
        $year = date("Y", time());
        $sites = array();
        foreach ($customers as $k => $v) {
            if($this->urlExists($v['name_val'])) $sites[] = $v['name_val'];
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
            );brary(array('session','ion_auth'));
            $crawl_s = $this->upload_record_webshoot($res['s'], $url."_small");
            $crawl_l = $this->upload_record_webshoot($res['l'], $url."_big");
            $result = array(
                'state' => false,
                'url' => $url,
                'small_crawl' => $crawl_s['path'],
                'big_crawl' => $crawl_l['path'],
                'dir_thumb' => $crawl_s['dir'],
                'dir_img' => $crawl_l['dir'],
                'uid' => 0,
                'year' => $year,
                'week' => $week,
                'pos' => 0
            );
            $insert_id = $this->webshoots_model->recordUpdateWebshoot($result);
        }
		echo "Cron Job Finished";
	}

    /**
     * Cron Job for CI home tab screenshots reports mailer   
     */
    public function emailreports() {
        $this->load->model('webshoots_model');
        $current_day = lcfirst(date('l', time()));
        $recs = $this->webshoots_model->get_recipients_list();
        if(count($recs) > 0) {
            // --- mailer config (start)
            $this->load->library('email');
            $config['protocol'] = 'sendmail';
            $config['mailpath'] = '/usr/sbin/sendmail';
            $config['charset'] = 'UTF-8';
            $config['wordwrap'] = TRUE;
            $this->email->initialize($config);
            // --- mailer config (end)
            foreach ($recs as $k => $v) {
                if($v->day == $current_day) {
                    $day = $v->day;
                    $email = $v->email;
                    $id = $v->id;
                    $this->email->from('ishulgin8@gmail.com', "Content Solutions");
                    $this->email->to("$email");
                    $this->email->subject('Content Solutions Screenshots Report');
                    $this->email->message("Report screenshots in attachment. Preference day: $day.");
                    // --- test (debug) attachments (start)
                    $debug_screens = $this->webshoots_model->getLimitedScreens(3);
                    if(count($debug_screens) > 0) {
                        foreach ($debug_screens as $key => $value) {
                            $path = $value->dir_thumb;
                            $this->email->attach("$path");
                        }
                    }
                    // --- test (debug) attachments (end)
                    $this->email->send();
                    echo "Report sended to $v->email"."<br>";
                }
            }
        }
        echo "Cron Job Finished";
    }

    public function do_stats(){

        $tmp_dir = sys_get_temp_dir().'/';
        unlink($tmp_dir.".locked");
        if ( file_exists($tmp_dir.".locked") )
        { exit;}

        touch($tmp_dir.".locked");
        try {
            $this->load->model('batches_model');
            $this->load->model('research_data_model');
            $this->load->model('statistics_model');
            $this->load->model('statistics_duplicate_content_model');
            $this->statistics_model->truncate();
            $this->statistics_duplicate_content_model->truncate();
            $batches = $this->batches_model->getAll();
            foreach($batches as $batch){
                    $data = $this->research_data_model->do_stats($batch->title);
                    if(count($data) > 0){
                        foreach($data as $obj){
                            $this->statistics_model->insert($obj->rid, $obj->imported_data_id, $obj->batch_name,
                                $obj->product_name, $obj->url, $obj->short_description, $obj->long_description,
                                $obj->short_description_wc, $obj->long_description_wc,
                                $obj->short_seo_phrases, $obj->long_seo_phrases);
                            $res = $this->check_duplicate_content($obj->imported_data_id);
                            foreach($res as $val){
                                $this->statistics_duplicate_content_model->insert($obj->imported_data_id, $val['product_name'],
                                    $val['description'], $val['long_description'], $val['url'],
                                    $val['features'], $val['customer'], $val['long_original'], $val['short_original']);
                            }
                            echo $batch->title."----".$obj->imported_data_id."=Done";
                        }
                    }
            }
            echo "Cron Job Finished";
        } catch (Exception $e) {
            echo 'Ошибка',  $e->getMessage(), "\n";
            unlink($tmp_dir.".locked");
        }
        unlink($tmp_dir.".locked");
    }

    private function check_duplicate_content($imported_data_id) {
        $this->load->model('imported_data_parsed_model');
        $this->load->model('similar_product_groups_model');
        $this->load->model('similar_data_model');
        $data_import = $this->imported_data_parsed_model->getByImId($imported_data_id);

        if ($data_import['description'] !== null && trim($data_import['description']) !== "") {
            $data_import['description'] = preg_replace('/\s+/', ' ', $data_import['description']);
            $data['s_product_short_desc_count'] = count(explode(" ", $data_import['description']));
        }
        if ($data_import['long_description'] !== null && trim($data_import['long_description']) !== "") {
            $data_import['long_description'] = preg_replace('/\s+/', ' ', $data_import['long_description']);
            $data['s_product_long_desc_count'] = count(explode(" ", $data_import['long_description']));
        }
        $data['s_product'] = $data_import;
        $same_pr = $this->imported_data_parsed_model->getSameProductsHuman($imported_data_id);

        if (empty($same_pr) && isset($data_import['parsed_attributes']) && isset($data_import['parsed_attributes']['model'])) {
            $strict = $this->input->post('strict');
            $same_pr = $this->imported_data_parsed_model->getByParsedAttributes($data_import['parsed_attributes']['model'], $strict);
        }

        if (empty($same_pr) && isset($data_import['parsed_attributes']) && isset($data_import['parsed_attributes']['UPC/EAN/ISBN'])) {
            $same_pr = $this->imported_data_parsed_model->getByParsedAttributes($data_import['parsed_attributes']['UPC/EAN/ISBN']);
        }
        if(empty($same_pr) && !isset($data_import['parsed_attributes']['model'])){
            $data['mismatch_button']=true;
            if (!$this->similar_product_groups_model->checkIfgroupExists($imported_data_id)) {

                if (!isset($data_import['parsed_attributes'])) {

                    $same_pr = $this->imported_data_parsed_model->getByProductName($imported_data_id, $data_import['product_name'], '', $strict);
                }
                if (isset($data_import['parsed_attributes']) ) {

                    $same_pr = $this->imported_data_parsed_model->getByProductName($imported_data_id, $data_import['product_name'], $data_import['parsed_attributes']['manufacturer'], $strict);
                }
            } else {
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
                $rows = $this->similar_data_model->getByGroupId($imported_data_id);
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

                $vs['short_original'] = 100 - round($maxshort, 2);
                $vs['long_original'] = 100 - round($maxlong, 2);


                if ($k_lng == 0) {
                    $vs['long_original'] = 100;
                }
                if ($k_sh == 0) {
                    $vs['short_original'] = 100;
                }

                $same_pr[$ks] = $vs;
            }
        } else {
            $same_pr[0]['long_original'] = 100;
            $same_pr[0]['short_original'] = 100;
        }

        return $same_pr;
    }

    private function compare_text($first_text, $second_text) {
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
}