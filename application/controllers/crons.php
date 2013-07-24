<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Crons extends MY_Controller {

	function __construct() {
  		parent::__construct();
  		$this->load->library('ion_auth');
		$this->ion_auth->add_auth_rules(array(
  			'index' => true,
  			'screenscron' => true
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
     * Cron Job for CI home tab screenshots  
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

}