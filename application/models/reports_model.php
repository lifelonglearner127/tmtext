<?php  if (!defined('BASEPATH')) exit('No direct script access allowed');

class Reports_model extends CI_Model {
    var $id = 0;
    var $name = '';
    var $body = '';

    var $tables = array(
        'reports' => 'reports',
    );

    function __construct() {
        parent::__construct();
    }

    function insert($name) {
        $this->name = $name;
        $this->db->insert($this->tables['reports'], $this);
        return $this->db->insert_id();
    }

    function update($id, $body) {
        $data = array(
            'body' => $body,
        );
        return $this->db->update($this->tables['reports'],
            $data,
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