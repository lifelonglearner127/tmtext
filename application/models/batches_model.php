<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Batches_model extends CI_Model {

    var $title = '';
    var $user_id = 0;
    var $created = '';
    var $modified = '';

    var $tables = array(
        'batches' => 'batches'
    );

    function __construct()
    {
        parent::__construct();
    }

    function get($id)
    {
        $query = $this->db->where('id', $id)
            ->limit(1)
            ->get($this->tables['batches']);

        return $query->result();
    }

    function getAll()
    {
        $this->db->order_by("title", "asc");
        $query = $this->db->get($this->tables['batches']);

        return $query->result();
    }


    function insert($title)
    {
        $CI =& get_instance();
        $this->title = $title;
        $this->user_id = $CI->ion_auth->get_user_id();
        $this->created = date('Y-m-d h:i:s');
        $this->modified = date('Y-m-d h:i:s');

        $this->db->insert($this->tables['batches'], $this);
        return $this->db->insert_id();
    }

    function getIdByName($title)
    {
        $query = $this->db->where('title', $title)
            ->limit(1)
            ->get($this->tables['batches']);

        if($query->num_rows() > 0) {
            return $query->row()->id;
        }
        return false;
    }

    function update($id, $title)
    {
        $CI =& get_instance();
        $this->user_id = $CI->ion_auth->get_user_id();
        $this->title = $title;
        $this->modified = date('Y-m-d h:i:s');

        return $this->db->update($this->tables['batches'],
            $this,
            array('id' => $id));
    }

    function delete($id)
    {
        return $this->db->delete($this->tables['batches'], array('id' => $id));
    }


}