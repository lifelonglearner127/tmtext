<?php  if (!defined('BASEPATH')) exit('No direct script access allowed');

class Reports_model extends CI_Model {
    var $tables = array(
        'reports' => 'reports',
    );

    function __construct() {
        parent::__construct();
    }

    function insert($name) {
        $params = array(
            'name' => $name
        );
        $this->db->insert($this->tables['reports'], $params);
        return $this->db->insert_id();
    }

    function update($id, $params) {
        return $this->db->update($this->tables['reports'],
            $params,
            array('id' => $id)
        );
    }

    function delete($id) {
        return $this->db->delete($this->tables['reports'], array('id' => $id));
    }

    function get_all_report_names() {
        $query = $this->db
            ->select('id, name')
            ->order_by("name", "asc")
            ->get($this->tables['reports']);

        return $query->result();
    }

    function get_by_id($id) {
        $query = $this->db
            ->where('id', $id)
            ->limit(1)
            ->get($this->tables['reports']);

        return $query->result();
    }

    function get_by_name($name) {
        $query = $this->db
            ->where('name', $name)
            ->limit(1)
            ->get($this->tables['reports']);

        return $query->result();
    }
}