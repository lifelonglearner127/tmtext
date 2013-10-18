<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Rankapi_model extends CI_Model {

    var $tables = array(
    	'ranking_api_data' => 'ranking_api_data'
    );

    function __construct() {
        parent::__construct();
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
