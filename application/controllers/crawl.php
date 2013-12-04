<?php

if (!defined('BASEPATH'))
    exit('No direct script access allowed');

class Crawl extends MY_Controller {

    function __construct() {
        parent::__construct();

        $this->load->library('ion_auth');
        $this->data['title'] = 'System Settings';
        $this->data['checked_controllers'] = array('batches', 'measure', 'assess', 'research', 'brand', 'customer');
        $this->data['admin_controllers'] = array('system', 'admin_customer', 'admin_editor', 'admin_tag_editor');

        $this->load->model('imported_data_parsed_model');
        $this->load->library('form_validation');

        $this->ion_auth->add_auth_rules(array(
            'urls_snapshot' => true,
            'sync_meta_personal' => true,
        ));
    }

    public function urls_snapshot() {
        
        $this->load->model('snapshot_queue_list_model');
        $result = $this->snapshot_queue_list_model->select();
        
        $siteViewIds = array();
        $siteCrawlIds = array();
        foreach ($result as $value) {
            switch ($value['type']) {
                case 'sites_view_snapshoot':{
                    $siteViewIds[] = $value['snapshot_id'];
                }
                    break;
                case 'site_crawl_snapshoot':{
                    $siteCrawlIds[] = $value['snapshot_id'];
                }
                    break;
            }
        }
        if(!empty($siteViewIds))
            $this->sites_view_snapshoot($siteViewIds);
        if(!empty($siteCrawlIds))
            $this->site_crawl_snapshoot($siteCrawlIds);
        $this->snapshot_queue_list_model->delete();
    }
    
    
    public function sites_view_snapshoot($ids){
        
        $this->load->model('webshoots_model');
        $this->load->model('department_members_model');
        $this->load->model('sites_model');
        $this->load->model('snapshot_queue_model');

        $this->snapshot_queue_model->insertCount(count($ids));
        foreach ($ids as $id) {
            $res[$id] = array(
                'status' => false,
                'snap' => '',
                'msg' => '',
                'site' => ''
            );
            $department = $this->department_members_model->get($id);
            if (count($department) > 0) {
                $dep = $department[0];
                if (isset($dep->url) && trim($dep->url) !== "") {
                    $url = $dep->url;
                    $http_status = $this->webshoots_model->urlExistsCode($url);
                    if ($http_status >= 200 && $http_status <= 302 || $http_status == 400) {
                        $url = preg_replace('#^https?://#', '', $url);
                        $call_url = $this->webshoots_model->webthumb_call_link($url);
                        $snap_res = $this->webshoots_model->crawl_webshoot($call_url, $dep->id, 'sites_dep_snap-');
                        // ==== check image (if we need to repeat snap craw, but using snapito.com) (start)
                        $fs = filesize($snap_res['dir']);
                        if ($fs === false || $fs < 10000) { // === so re-craw it
                            @unlink($snap_res['dir']);
                            $api_key = $this->config->item('snapito_api_secret');
                            $call_url = "http://api.snapito.com/web/$api_key/mc/$url";
                            $snap_res = $this->webshoots_model->crawl_webshoot($call_url, $dep->id, 'sites_dep_snap-');
                        }
                        // ==== check image (if we need to repeat snap craw, but using snapito.com) (end)
                        $res_insert = $this->department_members_model->insertSiteDepartmentSnap($dep->id, $snap_res['img'], $snap_res['path'], $snap_res['dir'], $http_status);
                        if ($res_insert > 0) {
                            $res[$id]['snap'] = $snap_res['path'];
                            $res[$id]['site'] = $url;
                            $res[$id]['status'] = true;
                            $res[$id]['msg'] = 'Ok';
                        }
                    } else {
                        $res[$id]['site'] = $url;
                        $res[$id]['msg'] = "Department url is unreachable. Snapshot attempt is canceled. HTTP STATUS: $http_status";
                    }
                } else {
                    $res[$id]['msg'] = "Url field is empty DB. Unable to process snapshot process";
                }
                echo "\n Snapshot created:  " . $dep->text . " - " . $dep->url . "\n";
            } else {
                $res[$id]['msg'] = "Such department don't exists in DB. Snapshot attempt is canceled.";
                echo "Such department don't exists in DB. Snapshot attempt is canceled.";
            }
            $this->snapshot_queue_model->updateCount();
        }
        $this->snapshot_queue_model->deleteCount();
    }

    

    public function site_crawl_snapshoot($ids) {
        $this->load->model('webshoots_model');
        $this->load->model('crawler_list_model');
        foreach ($ids as $id) {
            $result = $this->crawler_list_model->get($id);
            $v['url'] = $result[0]->url;
            $v['id'] = $result[0]->id;
            $v['imported_data_id'] = $result[0]->imported_data_id;
            if (!empty($v)) {
                    $http_status = $this->urlExistsCode($v['url']);
                    $orig_url = $v['url'];
                    $url = preg_replace('#^https?://#', '', $v['url']);
                    $r_url = urlencode(trim($url));
                    $call_url = $this->webthumb_call_link($url);
                    $snap_res = $this->crawl_webshoot($call_url, $v['id']);
                    $this->webshoots_model->updateCrawlListWithSnap($v['id'], $snap_res['img'], $http_status);
            }
            echo "\n Snapshot created:  " . $v['imported_data_id'] . " - " . $v['url'] . "\n";
        }
    }
    
    private function urlExistsCode($url) {
        if ($url === null || trim($url) === "")
            return false;
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_TIMEOUT, 5);
        curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        $data = curl_exec($ch);
        $httpcode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        return $httpcode;
    }
    
    private function webthumb_call_link($url) {
        $webthumb_user_id = $this->config->item('webthumb_user_id');
        $api_key = $this->config->item('webthumb_api_key');
        $url = "http://$url";
        $c_date = gmdate('Ymd', time());
        $hash = md5($c_date . $url . $api_key);
        $e_url = urlencode(trim($url));
        $call = "http://webthumb.bluga.net/easythumb.php?user=$webthumb_user_id&url=$e_url&hash=$hash&size=large&cache=1";
        return $call;
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
            'img' => $url_name . "." . $type,
            'call' => $call_url
        );
        return $res;
    }
    
    
  public function sync_meta_personal() {
        $this->load->model('rankapi_model');
        $ids = array();
        if(!empty($ids)){
            foreach($ids as $id){
                $res = $this->rankapi_model->sync_meta_personal_keyword($id);
            }
        }
        for($i = 0;$i < 10;$i++){
            sleep(1);
            echo "dedwedwedwd\n";
        }
  }

}