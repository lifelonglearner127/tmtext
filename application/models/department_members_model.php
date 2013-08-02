<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Department_members_model extends CI_Model {

    var $department_id = 0;
    var $site = '';
    var $site_id = 0;
    var $customer_id = 0;
    var $text = '';
    var $url = '';
    var $level = 0;
    var $parent_id = null;

    var $tables = array(
        'department_members' => 'department_members'
    );

    function __construct()
    {
        parent::__construct();
    }

    function get($id)
    {
        $query = $this->db->where('id', $id)
            ->limit(1)
            ->get($this->tables['department_members']);

        return $query->result();
    }

    function getAll()
    {
        $sql = "SELECT `id`, `text` FROM `department_members` group by `text` ORDER BY `text` ASC";
        $query = $this->db->query($sql);
        return $query->result();
    }

    function getAllByCustomer($customer)
    {
        $sql = "SELECT `id`, `text` FROM `department_members` WHERE `site` = '".$customer."' group by `text` ORDER BY `text` ASC";
        $query = $this->db->query($sql);
        return $query->result();
    }

    function getUrlByDepartment($id){
        $sql = "SELECT `url` FROM `department_members` WHERE id=".$id;
        $query = $this->db->query($sql);
        return $query->result();
    }

    function insert($site_name, $site_id, $text)
    {
        $this->text = $text;
        $this->site = $site_name;
        $this->site_id = $site_id;
        $this->db->insert($this->tables['department_members'], $this);
        return $this->db->insert_id();
    }

    function delete($id)
    {
        return $this->db->delete($this->tables['department_members'], array('id' => $id));
    }

    function deleteAll($site)
    {
        return $this->db->delete($this->tables['department_members'], array('site' => $site));
    }
}