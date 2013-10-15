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
            'urls_snapshot' => true
        ));
    }

    public function urls_snapshot() {
//        $query = $this->db->query("
//                    SELECT 
//                        `department_members`.`id` ,
//                        `department_members`.`url` 
//                      FROM
//                        `department_members` 
//                        LEFT OUTER JOIN `site_departments_snaps` 
//                          ON `department_members`.`id` = `site_departments_snaps`.`dep_id` 
//                      WHERE `site_departments_snaps`.`dep_id` IS NULL AND url != ''
//                      LIMIT 3     
//            ");
//        $result = $query->result_array();
        
        $this->load->model('snapshot_queue_list_model');
        $result = $this->snapshot_queue_list_model->select();
        
        $ids = array();
        foreach ($result as $value) {
            $ids[] = $value['dep_id'];
        }
        
        
        
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
        $this->snapshot_queue_list_model->delete();
    }

}