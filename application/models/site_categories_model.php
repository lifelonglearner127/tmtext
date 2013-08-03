<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Site_categories_model extends CI_Model {

    var $site_id = 0;
    var $text = '';
    var $url = '';
    var $special = 0;
    var $parent_text = '';

    var $tables = array(
        'site_categories' => 'site_categories',
    );

    function __construct()
    {
        parent::__construct();
    }

    function getAll()
    {
        $this->db->order_by("text", "asc");
        $query = $this->db->get($this->tables['site_categories']);

        return $query->result();
    }

    function get($id)
    {
        $query = $this->db->where('id', $id)
            ->limit(1)
            ->get($this->tables['site_categories']);

        return $query->result();
    }

    function getAllBySiteId($site_id, $department_id=''){
        if($department_id != ''){
            $department_id = " and `department_members_id`='".$department_id."' ";
        }
        $sql = "SELECT `id`, `text` FROM `site_categories` WHERE `site_id` = '".$site_id."' ".$department_id." ORDER BY `text` ASC";
        $query = $this->db->query($sql);
        return $query->result();
    }

    function getUrlByCategory($category_id){
        $sql = "SELECT `url` FROM `site_categories` WHERE `id` = '".$category_id."'";
        $query = $this->db->query($sql);
        return $query->result();
    }

    function insert($site_id, $text, $url, $special=0, $parent_text='', $department_members_id = 0)
    {
        $this->text = $text;
        $this->url = $url;
        $this->site_id = $site_id;
        $this->special = $special;
        $this->parent_text = $parent_text;
        $this->department_members_id = $department_members_id;

        $this->db->insert($this->tables['site_categories'], $this);
        return $this->db->insert_id();
    }

    function delete($id)
    {
        return $this->db->delete($this->tables['site_categories'], array('id' => $id));
    }

    function deleteAll($site_id)
    {
        return $this->db->delete($this->tables['site_categories'], array('site_id' => $site_id));
    }

    function checkExist($site_id, $text)
    {
        $query =  $this->db->select('id')
            ->from($this->tables['site_categories'])
            ->where('site_id', $site_id)->where('text', trim($text))->limit(1)->get();
        if($query->num_rows() > 0) {
            return $query->row()->id;
        }
        return false;
    }
}