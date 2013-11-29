<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Rankapi_model extends CI_Model {

    var $tables = array(
    	'ranking_api_data' => 'ranking_api_data',
        'meta_kw_rank_source' => 'meta_kw_rank_source'
    );

    function __construct() {
        parent::__construct();
    }

    function sync_meta_personal_keyword($id) {
        $api_username = $this->config->item('ranking_api_username');
        $api_key = $this->config->item('ranking_api_key');
        $res_source = null;
        $res_object = array(
            'status' => false,
            'msg' => '',
            'debug_rank' => null,
            'mode' => 'get',
            'find_track' => array()
        );
        $sql_source = $this->db->where('id', $id)->get($this->tables['meta_kw_rank_source']);
        $sql_source_res = $sql_source->result();
        if(count($sql_source_res) > 0) {
            $res_source = $sql_source_res[0];  
            $key_word = $res_source->kw;
            $url = $res_source->url;

            $data = array("data" => json_encode(array("action" => "getAccountRankings", "id" => "$api_username", "apikey" => "$api_key")));
            $ch = curl_init('https://www.serpranktracker.com/tracker/webservice');
            curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");
            curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
            $track_data = curl_exec($ch);
            $rank_data = json_decode($track_data);
            // === find needed data and procced syns process (start)
            $find_object = array(
                'status' => false,
                'site' => '',
                'keyword' => '',
                'location' => '',
                'engine' => '',
                'rank_json_encode' => '',
                'rank' => 0,
                'highest_rank' => array(),
                'add_api_curl' => null
            );
            if($rank_data->status == 'success') {
                if(count($rank_data->data) > 0) {
                    foreach($rank_data->data as $key => $value) {
                        if($value->site == $url) {
                            if(count($value->keywords) > 0) {
                                foreach ($value->keywords as $k => $v) {
                                    if($v->keyword == $key_word) { // !!! finded !!!
                                        // ===== sort out ranking stack (start)
                                        $r_object = null;
                                        $rank_int = null;
                                        $ranking_stack = array();
                                        foreach ($v->rankings as $ks => $vs) {
                                            $mid = array(
                                                'ranking' => $vs->ranking,
                                                'rankedurl' => $vs->rankedurl,
                                                'datetime' => $vs->datetime
                                            );
                                            array_push($ranking_stack, $mid);
                                        }
                                        $sort = array();
                                        foreach ($ranking_stack as $k => $vd) {
                                            $sort['datetime'][$k] = $vd['datetime'];
                                        }
                                        array_multisort($sort['datetime'], SORT_DESC, $ranking_stack);
                                        if (count($ranking_stack) > 0) {
                                            $r_object = $ranking_stack[0];
                                        }
                                        if ($r_object !== null) $rank_int = $r_object['ranking'];
                                        // ===== sort out ranking stack (end)
                                        // ===== figure out highest rank (start)
                                        $ranking_stack_mh = $ranking_stack;
                                        $sort_h = array();
                                        foreach ($ranking_stack_mh as $k => $vr) {
                                            if($vr['ranking'] !== null) $sort_h['ranking'][$k] = $vr['ranking'];
                                        }
                                        array_multisort($sort_h['ranking'], SORT_ASC, $ranking_stack_mh);
                                        if (count($ranking_stack_mh) > 0) {
                                            $h_object = $ranking_stack_mh[0];
                                        }
                                        // ===== figure out highest rank (end)
                                        $find_object['status'] = true;
                                        $find_object['site'] = $value->site;
                                        $find_object['keyword'] = $v->keyword;
                                        $find_object['location'] = $v->location;
                                        $find_object['engine'] = $v->searchengine;
                                        $find_object['rank_json_encode'] = json_encode($ranking_stack);
                                        $find_object['rank'] = $rank_int;
                                        $find_object['highest_rank'] = json_encode($h_object);
                                        // ===== finish sync (update db record) (start)
                                        $update_object = array(
                                            'rank_json_encode' => $find_object['rank_json_encode'],
                                            'highest_rank' => $find_object['highest_rank'],
                                            'rank' => $find_object['rank']
                                        );
                                        $this->db->update($this->tables['meta_kw_rank_source'], $update_object, array('id' => $id));
                                        // ===== finish sync (update db record) (end)
                                    }
                                }
                            }
                        }
                    }
                }
            }
            // === find needed data and procced syns process (end)

            // === check if need to insert new keyword to api (start)
            if($find_object['status'] !== true) { // ===== so insert to api
                $res_object['mode'] = 'insert';
                $key_url = array(
                    "site" => "$url",
                    "keyword" => "$key_word",
                    "location" => "US",
                    "searchengine" => "G"
                );
                $data_ins = array("data" => json_encode(array("action" => "addAccountKeywords", "id" => "$api_username", "apikey" => "$api_key", "keywords" => array($key_url))));
                $ch = curl_init('https://www.serpranktracker.com/tracker/webservice');
                curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");
                curl_setopt($ch, CURLOPT_POSTFIELDS, $data_ins);
                curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
                $res_object['add_api_curl'] = curl_exec($ch);
            }
            // === check if need to insert new keyword to api (end)

            $res_object['status'] = true;
            $res_object['msg'] = 'OK';
            $res_object['debug_rank'] = $rank_data;
            $res_object['find_track'] = $find_object;

        } else {
            $res_object['msg'] = 'Source object not finded';
        }
        return $res_object;
    }

    public function addGridItemRankingApi($url, $key_word) {
        $api_username = $this->config->item('ranking_api_username');
        $api_key = $this->config->item('ranking_api_key');
        $res = array(
            'status' => false,
            'msg' => "",
            'add_api_curl' => "",
            'rank' => null
        );
        $check_obj = array(
            'site' => $url,
            'keyword' => $key_word
        );
        $c_query = $this->db->where($check_obj)->order_by('stamp', 'desc')->get($this->tables['ranking_api_data']);
        $c_res = $c_query->result();
        if(count($c_res) < 1) {
            // ===== insert to api (start)
            $key_url = array(
                "site" => "$url",
                "keyword" => "$key_word",
                "location" => "US",
                "searchengine" => "G"
            );
            $data = array("data" => json_encode(array("action" => "addAccountKeywords", "id" => "$api_username", "apikey" => "$api_key", "keywords" => array($key_url))));
            $ch = curl_init('https://www.serpranktracker.com/tracker/webservice');
            curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");
            curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
            $res['add_api_curl'] = curl_exec($ch);
            // ===== insert to api (end)

            // ===== start sync process (start)
            $data = array("data" => json_encode(array("action" => "getAccountRankings", "id" => "$api_username", "apikey" => "$api_key")));
            $ch = curl_init('https://www.serpranktracker.com/tracker/webservice');
            curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");
            curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
            $track_data = curl_exec($ch);
            $data = json_decode($track_data);
            if (isset($data) && $data->status == 'success') {
                foreach ($data->data as $k => $v) {
                    $site = $v->site;
                    $keywords = $v->keywords;
                    if ((isset($site) && trim($site) !== "") && (isset($keywords) && count($keywords) > 0)) {
                        foreach ($keywords as $ks => $kv) {
                            // === extract not null and latest (according to date) rank object (start)
                            $r_object = null;
                            $rank_int = null;
                            $ranking_stack = array();
                            foreach ($kv->rankings as $ks => $vs) {
                                if (isset($vs->ranking) && $vs->ranking !== null && $vs->ranking !== "") {
                                    $mid = array(
                                        'ranking' => $vs->ranking,
                                        'rankedurl' => $vs->rankedurl,
                                        'datetime' => $vs->datetime
                                    );
                                    array_push($ranking_stack, $mid);
                                }
                            }
                            $sort = array();
                            foreach ($ranking_stack as $k => $v) {
                                $sort['datetime'][$k] = $v['datetime'];
                            }
                            array_multisort($sort['datetime'], SORT_DESC, $ranking_stack);
                            if (count($ranking_stack) > 0) {
                                $r_object = $ranking_stack[0];
                            }
                            if ($r_object !== null)
                                $rank_int = $r_object['ranking'];
                            // === extract not null and latest (according to date) rank object (end)
                            $sync_data = array(
                                'site' => $site,
                                'keyword' => $kv->keyword,
                                'location' => $kv->location,
                                'engine' => $kv->searchengine,
                                'rank_json_encode' => json_encode($kv->rankings),
                                'rank' => $rank_int
                            );
                            if($v->site == $url && $vs->keyword == $key_word) $res['rank'] = $vs->ranking;
                            $this->start_db_sync($sync_data);
                        }
                    }
                }
                $res['status'] = true;
                $res['msg'] = 'sync finished';
            } else {
                $res['msg'] = 'API call failed';
            }
            // ===== start sync process (end)
        } else {
            $res['msg'] = 'Already in DB (and ready for sync). No need to do anything in that case.';
        }
        return $res;
    }

    public function checkRankApiData($url, $keyword) {
        $rank = 0;
        $check_obj = array(
            'site' => $url,
            'keyword' => $keyword
        );
        $c_query = $this->db->where($check_obj)->order_by('stamp', 'desc')->get($this->tables['ranking_api_data']);
        $c_res = $c_query->result();
        if(count($c_res) > 0) {
            $rank_data = $c_res[0];
            $rank = $rank_data->rank; 
        }
        return $rank;
    }

    public function start_db_sync($sync_data) {
        $check_obj = array(
            'site' => $sync_data['site'],
            'keyword' => $sync_data['keyword']
        );
        $c_query = $this->db->where($check_obj)->order_by('stamp', 'desc')->get($this->tables['ranking_api_data']);
        $c_res = $c_query->result();
        if(count($c_res) > 0) { // === update
            $r = $c_res[0];
            $update_object = array(
                'location' => $sync_data['location'],
                'engine' => $sync_data['engine'],
                'rank_json_encode' => $sync_data['rank_json_encode'],
                'rank' => $sync_data['rank'],
                'stamp' => date("Y-m-d H:i:s")
            );
            $c_object = array(
                'site' => $r->site,
                'keyword' => $r->keyword
            );
            $this->db->update($this->tables['ranking_api_data'], $update_object, $c_object);
        } else { // === insert
            $insert_object = array(
                'site' => $sync_data['site'],
                'keyword' => $sync_data['keyword'],
                'location' => $sync_data['location'],
                'engine' => $sync_data['engine'],
                'rank_json_encode' => $sync_data['rank_json_encode'],
                'rank' => $sync_data['rank'],
                'stamp' => date("Y-m-d H:i:s")
            );
            $this->db->insert($this->tables['ranking_api_data'], $insert_object);
        }
        return true;   
    }

}
