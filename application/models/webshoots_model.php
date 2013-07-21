<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Webshoots_model extends CI_Model {

    var $tables = array(
    	'webshoots' => 'webshoots',
        'webshoots_select' => 'webshoots_select'
    );

    function __construct() {
        parent::__construct();
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

    function recordWebShootSelectionAttempt($screen_id, $uid, $pos, $year, $week, $img, $thumb, $screen_stamp) {
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
                'screen_stamp' => $screen_stamp  
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
                'screen_stamp' => $screen_stamp
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
        $query = $this->db->where('url', $url)->order_by('stamp', 'asc')->get($this->tables['webshoots']);
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

}
