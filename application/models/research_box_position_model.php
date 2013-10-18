<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Research_box_position_model extends CI_Model {

    var $user_id  = 0;
    var $position = '';
    var $box_id = '';
    var $width = 0;
    var $height = 0;
    var $created = '';
    var $modified = '';


    var $tables = array(
        'research_box_position' => 'research_box_position'
    );

    function __construct()
    {
        parent::__construct();
    }

    function get($id)
    {
        $query = $this->db->where('id', $id)
            ->limit(1)
            ->get($this->tables['research_box_position']);

        return $query->result();
    }

    function insert($position, $box_id, $width, $height)
    {
        $CI =& get_instance();
        $this->user_id = $CI->ion_auth->get_user_id();
        $this->position = $position;
        $this->box_id = $box_id;
        $this->width = $width;
        $this->height = $height;
        $this->created = date('Y-m-d h:i:s');
        $this->modified = date('Y-m-d h:i:s');
        $this->db->insert($this->tables['research_box_position'], $this);
        return $this->db->insert_id();
    }

    function delete()
    {
        $CI =& get_instance();
        $this->user_id = $CI->ion_auth->get_user_id();
        return $this->db->delete($this->tables['research_box_position'], array('user_id' => $this->user_id));
    }

    function getDataByUserId()
    {
        $CI =& get_instance();
        $query = $this->db->where('user_id', $CI->ion_auth->get_user_id())->get($this->tables['research_box_position']);
        return $query->result();
    }


}