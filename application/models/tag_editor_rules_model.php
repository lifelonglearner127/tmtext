<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Tag_Editor_Rules_model extends CI_Model {

    var $rule = '';
    var $category_id = 0;
    var $user_id = 0;
    var $created = '';
    var $modified = '';

    var $tables = array(
        'tag_editor_rules' => 'tag_editor_rules'
    );

    function __construct()
    {
        parent::__construct();
    }

    function get($id)
    {
        $query = $this->db->where('id', $id)
            ->limit(1)
            ->get($this->tables['tag_editor_rules']);

        return $query->result();
    }

    function getAllByCategoryId($category_id)
    {
        $query = $this->db->where('category_id', $category_id)
            ->get($this->tables['tag_editor_rules']);

        return $query->result();
    }

    function insert($rule, $category_id)
    {
        $CI =& get_instance();
        $this->rule = $rule;
        $this->category_id = $category_id;

        $this->user_id = $CI->ion_auth->get_user_id();

        $this->created = date('Y-m-d h:i:s');
        $this->modified = date('Y-m-d h:i:s');

        $this->db->insert($this->tables['tag_editor_rules'], $this);
        return $this->db->insert_id();
    }

    function getByRule($name, $category_id)
    {
       $query = $this->db->where('rule', $name)->where('category_id', $category_id)->get($this->tables['tag_editor_rules']);
       if($query->num_rows() > 0) {
           return $query->row()->id;
       }
       return false;
    }

    function update($value, $id)
    {
        return $this->db->update($this->tables['tag_editor_rules'],
            array('rule' => $value, 'modified' => date('Y-m-d h:i:s')),
            array('id' => $id));
    }

    function delete($category_id)
    {
        return $this->db->delete($this->tables['tag_editor_rules'], array('category_id' => $category_id));
    }


}
