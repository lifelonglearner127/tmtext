<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Webshoots_model extends CI_Model {

    var $tables = array(
    	'webshoots' => 'webshoots',
        'webshoots_select' => 'webshoots_select',
        'ci_home_page_recipients' => 'ci_home_page_recipients',
        'customers' => 'customers',
        'crawler_list' => 'crawler_list',
        'home_pages_config' => 'home_pages_config'
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

    public function getDistinctEmailScreens($c_week, $c_year, $uid) {
        $images = array();
        $check_obj = array(
            'uid' => $uid,
            'year' => $c_year,
            'week' => $c_week,
            'reset' => 0
        );
        $sel_query = $this->db->where($check_obj)->order_by('stamp', 'desc')->get($this->tables['webshoots_select']);
        $sel_res = $sel_query->result();
        if(count($sel_res) > 0) {
            $screen_ids = array();
            foreach ($sel_res as $ks => $vs) {
                $screen_ids[] = $vs->screen_id;
            }
            // $screen_ids = array_unique($screen_ids);
            $shots_query = $this->db->where_in('id', $screen_ids)->get($this->tables['webshoots']);
            $shots_res = $shots_query->result();
            if(count($shots_res) > 0) {
                foreach($shots_res as $k => $v) {
                    $fs = filesize($v->dir_img); 
                    if($fs !== false && $fs > 10000) {
                        $mid = array(
                            'link' => $v->img,
                            'dir' => $v->dir_img,
                            'pos' => $this->getScreenPosition($v->id) # ==== !!! CHECK IT, SOMETHING WRONG !!!
                        );
                        $images[] = $mid;
                    }
                }
            }
        }
        return $images;
    }

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
                        'label' => $candidate_name
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

    function recordWebShootSelectionAttempt($screen_id, $uid, $pos, $year, $week, $img, $thumb, $screen_stamp, $url, $label) {
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
                'reset' => 0
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
                'label' => $label
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
                        'screen_stamp' => $ws_item->stamp
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
            'pos' => $result['pos']
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

}
