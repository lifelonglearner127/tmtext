<?php

if (!defined('BASEPATH'))
    exit('No direct script access allowed');

class snapshot_queue_list_model extends CI_Model {

    var $tables = array(
        'snapshot_queue_list' => 'snapshot_queue_list'
    );

    function __construct() {
        parent::__construct();
    }

    public function getAll() {
        $query = $this->db->get($this->tables['snapshot_queue_list']);
        $result = $query->result_array();
        return $result;
    }

    public function insert($snapshot_arr, $type) {
        foreach ($snapshot_arr as $snapshot) {
            $query = $this->db->get_where($this->tables['snapshot_queue_list'], array(
                'snapshot_id' => $snapshot[0],
                'user_id' => $this->ion_auth->get_user_id(),
                'type' => $type
                    ));
            $result = $query->result();
            if (!$result) {
                if ($type === 'sites_view_snapshoot') {
                    $query = $this->db->query("
                            SELECT 
                                `department_members`.`text`,
                                `sites`.`name`,
                                `department_members`.`url`
                              FROM
                                `department_members` 
                                INNER JOIN `sites` 
                                  ON `sites`.`id` = `department_members`.`site_id` 
                              WHERE `department_members`.`id` = {$snapshot[0]} 
                        ");
                    $result = $query->result_array();
                    $site_name = $result[0]['name'];
                    $url = $result[0]['url'];
                    $name = $result[0]['text'];
                } else if ($type === 'site_crawl_snapshoot') {
                    $site_name = '';
                    $url = $snapshot[1];
                    $name = 'Crawl list - ' . $snapshot[2];
                }
                $data = array(
                    'snapshot_id' => $snapshot[0],
                    'user_id' => $this->ion_auth->get_user_id(),
                    'type' => $type,
                    'site_name' => $site_name,
                    'url' => $url,
                    'name' => $name,
                    'time_added' => date("Y-m-d H:i:s")
                );
                $this->db->insert($this->tables['snapshot_queue_list'], $data);
            }
        }
    }

    public function select() {
        $query = $this->db->get($this->tables['snapshot_queue_list']);
        $result = $query->result_array();
        return $result;
    }

    public function delete() {
        $this->db->empty_table($this->tables['snapshot_queue_list']);
    }

    public function deleteByDepId($snapshot_id) {
        $this->db->delete($this->tables['snapshot_queue_list'], array('snapshot_id' => $snapshot_id, 'user_id' => $this->ion_auth->get_user_id()));
    }

}
