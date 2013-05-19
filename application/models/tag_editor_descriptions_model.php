<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Tag_Editor_Descriptions_model extends CI_Model {

    var $user_id = 0;
    var $description = '';
    var $created = '';
    var $modified = '';

    var $tables = array(
        'tag_editor_descriptions' => 'tag_editor_descriptions'
    );

    function __construct()
    {
        parent::__construct();
    }

    function get($id)
    {
        $query = $this->db->where('user_id', $id)
            ->limit(1)
            ->get($this->tables['tag_editor_descriptions']);

        return $query->result();
    }

    function insert($description)
    {
        $CI =& get_instance();

        $this->description = $description;

        $this->user_id = $CI->ion_auth->get_user_id();

        $this->created = date('Y-m-d h:i:s');
        $this->modified = date('Y-m-d h:i:s');

        $this->db->insert($this->tables['tag_editor_descriptions'], $this);
        return $this->db->insert_id();
    }

    function update($user_id, $value)
    {
          return $this->db->update($this->tables['tag_editor_descriptions'],
                array('description' => $value, 'modified' => date('Y-m-d h:i:s')),
                array('user_id' => $user_id));
    }

    function delete($user_id)
    {
        return $this->db->delete($this->tables['tag_editor_descriptions'], array('user_id' => $user_id));
    }


}
