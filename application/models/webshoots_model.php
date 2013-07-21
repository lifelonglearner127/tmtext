<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Webshoots_model extends CI_Model {

    var $tables = array(
    	'webshoots' => 'webshoots'
    );

    function __construct() {
        parent::__construct();
    }

    // function recordUpdateWebshoot($result) {
    //     $st = 1; // 1 - insert, 2 - update
    //     $check_query = $this->db->get_where($this->tables['webshoots'], array('url' => $result['url']));
    //     $check_query_res = $check_query->result();
    //     if(count($check_query_res) > 0) {
    //         $st = 2;
    //     }
    //     $change_status = false;
    //     if($st === 1) { // insert
    //         $insert_object = array(
    //             'url' => $result['url'],
    //             'img' => $result['big_crawl'],
    //             'thumb' => $result['small_crawl'],
    //             'dir_thumb' => $result['dir_thumb'],
    //             'dir_img' => $result['dir_img'],
    //             'stamp' => date("Y-m-d H:i:s")
    //         );
    //         $this->db->insert($this->tables['webshoots'], $insert_object);
    //         $insert_id = $this->db->insert_id();
    //         if($insert_id > 0) $change_status = true;
    //     } else if($st === 2) { // update (update only date cause file_put_contents will update image by itself)
    //         $update_object = array(
    //             'stamp' => date("Y-m-d H:i:s")
    //         );
    //         $res = $this->db->update($this->tables['webshoots'], $update_object, array('url' => $result['url']));
    //         if($res) $change_status = true;
    //     }
    //     return $change_status;
    // }

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
