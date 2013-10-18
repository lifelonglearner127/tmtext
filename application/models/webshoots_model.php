<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Webshoots_model extends CI_Model {

    var $tables = array(
    	'webshoots' => 'webshoots',
        'webshoots_select' => 'webshoots_select',
        'ci_home_page_recipients' => 'ci_home_page_recipients',
        'customers' => 'customers',
        'crawler_list' => 'crawler_list',
        'home_pages_config' => 'home_pages_config',
        'site_departments_snaps' => 'site_departments_snaps',
        'department_members' => 'department_members'
    );

    function __construct() {
        parent::__construct();
    } 

    private function getScreenPosition($screen_id) {
        $pos = 0;
        $query = $this->db->where('screen_id', $screen_id)->get($this->tables['webshoots_select']);
        $query_res = $query->result();
        if(count($query_res) > 0) {
            $r = $query_res[0];
            $pos = $r->pos;
        }
        return $pos;
    }

    public function changeHomePageRecipients($id, $week_day) {
        $update_object = array(
            'day' => $week_day
        );
        return $this->db->update($this->tables['ci_home_page_recipients'], $update_object, array('id' => $id));
    }

    public function scanForProductSnap($im_data_id) {
        $res_data = array(
            'snap' => '',
            'img_av_status' => false,
            'status' => '',
            'fs' => 0
        );
        $check_obj = array(
            'imported_data_id' => $im_data_id,
            'snap !=' => 'null'
        );
        // $query = $this->db->where($check_obj)->order_by('snap_date', 'desc')->limit(1)->get($this->tables['crawler_list']);
        $query = $this->db->where($check_obj)->limit(1)->get($this->tables['crawler_list']);
        $query_res = $query->result();
        if(count($query_res) > 0) {
            $r = $query_res[0];
            $snap = $r->snap;
            $url = $r->url;
            $fs = filesize(realpath(BASEPATH . "../webroot/webshoots/$snap"));
            $res_data['snap'] = $snap;
            $res_data['url'] = $url;
            if($fs !== false || $fs > 10000) {
                $res_data['img_av_status'] = true;
                $res_data['status'] = 'ok';
            } else {
                $res_data['status'] = 'low filesize or file not exists';
            }
            $res_data['fs'] = $fs;
        } else {
            $res_data['status'] = 'no snap in db';
        }
        return $res_data;
    }

    public function get_crawler_list_by_ids($ids) {
        $cr_query = $this->db->where_in('id', $ids)->get($this->tables['crawler_list']);
        return $cr_query->result();
    }

    public function webthumb_call_link($url) {
        $webthumb_user_id = $this->config->item('webthumb_user_id');
        $api_key = $this->config->item('webthumb_api_key');
        $url = "http://$url";
        $c_date = gmdate('Ymd', time()); 
        $hash = md5($c_date.$url.$api_key); 
        $e_url = urlencode(trim($url));
        $call = "http://webthumb.bluga.net/easythumb.php?user=$webthumb_user_id&url=$e_url&hash=$hash&size=large&cache=1";
        return $call;
    }

    public function urlExistsCode($url) {
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

    public function crawl_webshoot($call_url, $id, $prefix) {
        $file = file_get_contents($call_url);
        $type = 'png';
        $dir = realpath(BASEPATH . "../webroot/webshoots");
        if (!file_exists($dir)) {
            mkdir($dir);
            chmod($dir, 0777);
        }
        // --- NEW STUFF (TIMESTAMP BASED IMAGES NAMES) (START)
        $url_name = $prefix . $id . "-" . date('Y-m-d-H-i-s', time());
        // --- NEW STUFF (TIMESTAMP BASED IMAGES NAMES) (END)
        $t = file_put_contents($dir . "/$url_name.$type", $file);
        $path = base_url() . "webshoots/$url_name.$type";
        $res = array(
            'path' => $path,
            'dir' => $dir . "/$url_name.$type",
            'img' => $url_name.".".$type,
            'call' => $call_url
        );
        return $res;
    }

    public function updateHomePagesConfig($type, $value) {
        $update_object = array(
            'value' => $value
        );
        return $this->db->update($this->tables['home_pages_config'], $update_object, array('type' => $type));
    }

    public function getEmailReportConfig($type) {
        $res = '';
        $query = $this->db->where('type', $type)->get($this->tables['home_pages_config']);
        $qr_res = $query->result();
        if(count($qr_res) > 0) {
            $r = $qr_res[0];
            $res = $r->value;
        }
        return $res;
    }

    public function resetScreenDrop($uid, $pos, $year, $week) {
        $check_obj = array(
            'uid' => $uid,
            'year' => $year,
            'week' => $week,
            'pos' => $pos
        );
        $qr = $this->db->where($check_obj)->get($this->tables['webshoots_select']);
        $qr_res = $qr->result();
        if(count($qr_res) > 0) { // === TODO: just set pos value to 0 for existing selection
            $r = $qr_res[0];
            $update_object = array(
                'reset' => 1
            );
            $this->db->update($this->tables['webshoots_select'], $update_object, array('id' => $r->id));
        }
        return true;
    }

    public function getDistinctEmailScreensAnonim($c_week, $c_year) {
        $images = array();
        $check_obj = array(
            'year' => $c_year,
            'week' => $c_week,
            'reset' => 0
        );
        $sel_query = $this->db->where($check_obj)->order_by('stamp', 'desc')->limit(6)->get($this->tables['webshoots_select']);
        $sel_res = $sel_query->result();
        if(count($sel_res) > 0) {
            foreach($sel_res as $k => $v) {
                $shot_name = $v->shot_name;
                $dir_img = realpath(BASEPATH . "../webroot/webshoots/$shot_name");
                $fs = filesize($dir_img); 
                if($fs !== false && $fs > 10000) {
                    $mid = array(
                        'link' => $v->img,
                        'dir' => $dir_img,
                        'pos' => $v->pos
                    );
                    $images[] = $mid;
                }
            }
        }
        return $images;
    }

    public function getDistinctEmailScreens($c_week, $c_year, $uid) {
        $images = array();
        $check_obj = array(
            'uid' => $uid,
            'year' => $c_year,
            'week' => $c_week,
            'reset' => 0
        );
        $sel_query = $this->db->where($check_obj)->order_by('stamp', 'desc')->limit(6)->get($this->tables['webshoots_select']);
        $sel_res = $sel_query->result();
        if(count($sel_res) > 0) {
            foreach($sel_res as $k => $v) {
                $shot_name = $v->shot_name;
                $dir_img = realpath(BASEPATH . "../webroot/webshoots/$shot_name");
                $fs = filesize($dir_img); 
                if($fs !== false && $fs > 10000) {
                    $mid = array(
                        'link' => $v->img,
                        'dir' => $dir_img,
                        'pos' => $v->pos
                    );
                    $images[] = $mid;
                }
            }
        }
        return $images;
    }

    // public function getDistinctEmailScreens($c_week, $c_year, $uid) {
    //     $images = array();
    //     $check_obj = array(
    //         'uid' => $uid,
    //         'year' => $c_year,
    //         'week' => $c_week,
    //         'reset' => 0
    //     );
    //     $sel_query = $this->db->where($check_obj)->order_by('stamp', 'desc')->limit(6)->get($this->tables['webshoots_select']);
    //     $sel_res = $sel_query->result();
    //     var_dump($sel_res);
    //     if(count($sel_res) > 0) {
    //         $screen_ids = array();
    //         foreach ($sel_res as $ks => $vs) {
    //             $screen_ids[] = $vs->screen_id;
    //         }
    //         // $screen_ids = array_unique($screen_ids);
    //         $shots_query = $this->db->where_in('id', $screen_ids)->get($this->tables['webshoots']);
    //         $shots_res = $shots_query->result();
    //         if(count($shots_res) > 0) {
    //             foreach($shots_res as $k => $v) {
    //                 $fs = filesize($v->dir_img); 
    //                 if($fs !== false && $fs > 10000) {
    //                     $mid = array(
    //                         'link' => $v->img,
    //                         'dir' => $v->dir_img,
    //                         'pos' => $this->getScreenPosition($v->id) # ==== !!! CHECK IT, SOMETHING WRONG !!!
    //                     );
    //                     $images[] = $mid;
    //                 }
    //             }
    //         }
    //     }
    //     return $images;
    // }

    public function updateWebshootById($up_object, $id) {
        return $this->db->update($this->tables['webshoots'], $up_object, array('id' => $id));
    }

    public function updateCrawlListWithSnap($id, $snap, $http_status) {
        // === destroy previous snap (start)
        $check_obj = array(
            'id' => $id
        );
        $check_query = $this->db->get_where($this->tables['crawler_list'], $check_obj);
        $check_query_res = $check_query->result();
        if(count($check_query_res) > 0) {
            $prev_snap = $check_query_res[0];
            $sn = $prev_snap->snap;
            @unlink(realpath(BASEPATH . "../webroot/webshoots/$sn"));
        }
        // === destroy previous snap (end)
        $update_object = array(
            'snap' => $snap,
            'snap_date' => date("Y-m-d H:i:s"),
            'snap_state' => $http_status
        );
        return $this->db->update($this->tables['crawler_list'], $update_object, array('id' => $id));
    }

    public function screenAutoSelection($year, $week, $pos, $uid) {
        $res = false;
        $check_obj = array(
            'pos' => $pos,
            'uid' => $uid,
            'year' => $year,
            'week' => $week
        );
        $check_query = $this->db->get_where($this->tables['webshoots_select'], $check_obj);
        $check_query_res = $check_query->result();
        if(count($check_query_res) < 1) { // === no selection for this slot, so start auto-selection
            $s_pos = $pos - 1;
            $query_customer = $this->db->order_by('url', 'asc')->limit(1, $s_pos)->get($this->tables['customers']);
            $query_customer_res = $query_customer->result();
            $candidate = $query_customer_res[0];
            $candidate_url = preg_replace('#^https?://#', '', $candidate->url);
            $candidate_url = preg_replace('#^www.#', '', $candidate_url);
            // ---- check if we need to crawl url before auto-selection
            $candidate_name = $candidate->name;
            // if($candidate_url === 'sears.com') {
            //     $candidate_url = 'wayfair.com';
            //     $candidate_name = 'wayfair.com';
            // }
            // if($candidate_url == 'bloomingdales.com') {
            //     $candidate_url = 'toysrus.com';
            //     $candidate_name = 'toysrus.com';
            // }
            $query_url_check = $this->db->where('url', $candidate_url)->order_by('stamp', 'desc')->get($this->tables['webshoots']);
            $query_url_check_res = $query_url_check->result();
            if(count($query_url_check_res) > 0) { // --- just make auto-selection
                $object_as = $query_url_check_res[0];
                if($object_as->reset == 0) {
                    $insert_object = array(
                        'screen_id' => $object_as->id,
                        'uid' => $uid,
                        'pos' => $pos,
                        'year' => $year,
                        'week' => $week,
                        'img' => $object_as->img,
                        'thumb' => $object_as->thumb,
                        'stamp' => date("Y-m-d H:i:s"),
                        'screen_stamp' => $object_as->stamp,
                        'site' => $candidate_url,
                        'label' => $candidate_name,
                        'shot_name' => $object_as->shot_name
                    );
                    $this->db->insert($this->tables['webshoots_select'], $insert_object);
                }
            }
            $res = true; 
        } 
        return $res;
    }

    public function getLimitedScreens($limit) {
        $res = array();
        $query = $this->db->where(array())->order_by('stamp', 'desc')->limit($limit)->get($this->tables['webshoots']);
        $query_res = $query->result();
        if(count($query_res) > 0) {
            $res = $query_res;
        }
        return $res;
    }

    public function delete_reports_recipient($id) {
        return $this->db->delete($this->tables['ci_home_page_recipients'], array('id' => $id)); 
    }

    public function get_recipients_list() {
        $query = $this->db->where(array())->order_by('stamp', 'desc')->get($this->tables['ci_home_page_recipients']);
        return $query->result();
    }

    public function rec_emails_reports_recipient($rec_day, $recs_arr) {
        $res = false;
        if(count($recs_arr) > 0) {
            $result = array();
            foreach ($recs_arr as $email) {
                $check_query = $this->db->get_where($this->tables['ci_home_page_recipients'], array('email' => $email));
                $check_query_res = $check_query->result();
                if(count($check_query_res) > 0) { // --- update
                    $update_object = array(
                        'day' => $rec_day,
                        'stamp' => date("Y-m-d H:i:s")
                    );
                    $this->db->update($this->tables['ci_home_page_recipients'], $update_object, array('email' => $email));
                } else { // --- insert
                    $insert_object = array(
                        'email' => $email,
                        'day' => $rec_day,
                        'stamp' => date("Y-m-d H:i:s")
                    );
                    $this->db->insert($this->tables['ci_home_page_recipients'], $insert_object);
                    $query = $this->db->where('id', $this->db->insert_id())
                        ->limit(1)
                        ->get($this->tables['ci_home_page_recipients']);
                    array_push($result, $query->result());
                }
            }
            $res = $result;
        }   
        return $res;
    }

    public function getWeekAvailableScreens($week, $year) {
        $res = array();
        $query = $this->db->where(array('year' => $year, 'week' => $week))->order_by('stamp', 'desc')->limit(6)->get($this->tables['webshoots']);
        $query_res = $query->result();
        if(count($query_res) > 0) {
            $res = $query_res;
        }
        return $res;
    }

    function getScreenCellSelection($pos, $uid, $year, $week) {
        $res = false;
        $check_obj = array(
            'pos' => $pos,
            'uid' => $uid,
            'year' => $year,
            'week' => $week
        );
        $check_query = $this->db->get_where($this->tables['webshoots_select'], $check_obj);
        $check_query_res = $check_query->result();
        if(count($check_query_res) > 0) {
            $res = $check_query_res[0];
        }
        return $res;
    }

    function recordWebShootSelectionAttempt($screen_id, $uid, $pos, $year, $week, $img, $thumb, $screen_stamp, $url, $label, $shot_name) {
        $res = false;
        $check_obj = array(
            'pos' => $pos,
            'uid' => $uid,
            'year' => $year,
            'week' => $week
        );
        $check_query = $this->db->get_where($this->tables['webshoots_select'], $check_obj);
        $check_query_res = $check_query->result();
        if(count($check_query_res) > 0) { // --- update
            $update_object = array(
                'screen_id' => $screen_id,
                'stamp' => date("Y-m-d H:i:s"),
                'img' => $img,
                'thumb' => $thumb,
                'screen_stamp' => $screen_stamp, 
                'site' => $url, 
                'label' => $label,
                'reset' => 0,
                'shot_name' => $shot_name
            );
            $this->db->update($this->tables['webshoots_select'], $update_object, $check_obj);
        } else { // --- new
            $insert_object = array(
                'screen_id' => $screen_id,
                'uid' => $uid,
                'pos' => $pos,
                'year' => $year,
                'week' => $week,
                'img' => $img,
                'thumb' => $thumb,
                'stamp' => date("Y-m-d H:i:s"),
                'screen_stamp' => $screen_stamp,
                'site' => $url,
                'label' => $label,
                'shot_name' => $shot_name
            );
            $this->db->insert($this->tables['webshoots_select'], $insert_object);
        }
        return true;
    }

    function updateWebShootPosition($screen_id, $pos) {
        $update_object = array(
            'pos' => $pos
        );
        return $this->db->update($this->tables['webshoots'], $update_object, array('id' => $screen_id));
    }

    function getWebshootDataById($insert_id) {
        $res = false;
        $check_query = $this->db->get_where($this->tables['webshoots'], array('id' => $insert_id));
        $check_query_res = $check_query->result();
        if(count($check_query_res) > 0) {
            $res = $check_query_res[0];
        }
        return $res;
    }

    function selectionRefreshDecision($id) {
        $ws_query = $this->db->get_where($this->tables['webshoots'], array('id' => $id));
        $ws_query_res = $ws_query->result();
        if(count($ws_query_res) > 0) {
            $ws_item = $ws_query_res[0];
            $s_object = array(
                'uid' => $ws_item->uid,
                'site' => $ws_item->url
            );
            $check_query = $this->db->get_where($this->tables['webshoots_select'], $s_object);
            $check_query_res = $check_query->result();
            if(count($check_query_res) > 0) {
                foreach ($check_query_res as $k => $v) {
                    $u_object = array(
                        'screen_id' => $ws_item->id,
                        'img' => $ws_item->img,
                        'thumb' => $ws_item->thumb,
                        'screen_stamp' => $ws_item->stamp,
                        'shot_name' => $ws_item->shot_name
                    );
                    $this->db->update($this->tables['webshoots_select'], $u_object, array('id' => $v->id));
                }
            }
        }
    }

    function recordUpdateWebshoot($result) {
        $insert_object = array(
            'url' => $result['url'],
            'img' => $result['big_crawl'],
            'thumb' => $result['small_crawl'],
            'dir_thumb' => $result['dir_thumb'],
            'dir_img' => $result['dir_img'],
            'stamp' => date("Y-m-d H:i:s"),
            'uid' => $result['uid'],
            'year' => $result['year'],
            'week' => $result['week'],
            'pos' => $result['pos'],
            'shot_name' => $result['shot_name'] 
        );
        $this->db->insert($this->tables['webshoots'], $insert_object);
        $insert_id = $this->db->insert_id();
        return $insert_id;
    }

    function checkScreenCrawlStatus($url) {
        $res = false;
        $check_query = $this->db->get_where($this->tables['webshoots'], array('url' => $url));
        $check_query_res = $check_query->result();
        if(count($check_query_res) > 0) {
            $res = true;
        }
        return $res;
    }

    function getWebShootByUrl($url) {
        $query = $this->db->where('url', $url)->order_by('stamp', 'desc')->get($this->tables['webshoots']);
        $query_res = $query->result();
        if(count($query_res) > 0) {
            $res = $query_res[0];
        } else {
            $res = false;
        }
        return $res;
    }

    function getWebshootData($url) {
        $query = $this->db->get_where($this->tables['webshoots'], array('url' => $url));
        $query_res = $query->result();
        if(count($query_res) > 0) {
            return $query_res;
        } else {
            return array();
        }
    }

    function getWebshootDataStampDesc($url) {
        $query = $this->db->where('url', $url)->order_by('stamp', 'desc')->get($this->tables['webshoots']);
        $query_res = $query->result();
        if(count($query_res) > 0) {
            return $query_res;
        } else {
            return array();
        }
    }

    public function checkAndGenerateDepScreenshot($dep_id) {
      $this->load->model('department_members_model');
      $check_obj = array(
        'dep_id' => $dep_id
      );
      $qr = $this->db->where($check_obj)->get($this->tables['site_departments_snaps']);
      $qr_res = $qr->result();
      if(count($qr_res) > 0) { // === check image status of existed (and refresh if image is bad)
        $r = $qr_res[0];
        $snap_name = $r->snap_name;
        $dir_img = realpath(BASEPATH . "../webroot/webshoots/$snap_name");
        $fs = filesize($dir_img); 
        if($fs === false || $fs < 10000) {
          $dep_query = $this->db->where('id', $dep_id)->limit(1)->get($this->tables['department_members']);
          $dep_query_res = $dep_query->result();
          if(count($dep_query_res) > 0) {
            $dep = $dep_query_res[0];
            @unlink($dir_img);
            $url = $dep->url;
            $http_status = $this->urlExistsCode($url);
            if($http_status >= 200 && $http_status <= 302) {
              $url = preg_replace('#^https?://#', '', $url);
              $call_url = $this->webthumb_call_link($url);
              $snap_res = $this->crawl_webshoot($call_url, $dep->id, 'sites_dep_snap-');
              $this->department_members_model->updateSiteDepartmentSnap($dep->id, $snap_res['img'], $snap_res['path'], $snap_res['dir'], $http_status);
            }
          }
        }
      } else { // === create brand new snap
        $dep_query = $this->db->where('id', $dep_id)->limit(1)->get($this->tables['department_members']);
        $dep_query_res = $dep_query->result();
        if(count($dep_query_res) > 0) {
          $dep = $dep_query_res[0];
          $url = $dep->url;
          $http_status = $this->urlExistsCode($url);
          if($http_status >= 200 && $http_status <= 302) {
            $url = preg_replace('#^https?://#', '', $url);
            $call_url = $this->webthumb_call_link($url);
            $snap_res = $this->crawl_webshoot($call_url, $dep->id, 'sites_dep_snap-');
            $this->department_members_model->insertSiteDepartmentSnap($dep->id, $snap_res['img'], $snap_res['path'], $snap_res['dir'], $http_status);
          }
        }
      }
      return true;
    }

}
