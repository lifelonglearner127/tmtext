<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Crawler_instances_model extends CI_Model {
	var $instance_id = '';
	var $instance_type = '';
	var $state_name = '';
	var $public_dns_name = '';

    var $tables = array(
        'crawler_instances' => 'crawler_instances'
    );

    function __construct()
    {
        parent::__construct();
    }

    function get($id)
    {
        $query = $this->db->where('id', $id)
            ->limit(1)
            ->get($this->tables['crawler_instances']);

        return $query->result();
    }

    function getAll()
    {
        $query = $this->db->get($this->tables['crawler_instances']);
        return $query->result();
    }


    function insert($instance_id, $instance_type, $state_name, $public_dns_name)
    {
        $this->instance_id = $instance_id;
        $this->instance_type = $instance_type;
        $this->state_name = $state_name;
        $this->public_dns_name = $public_dns_name;

        $this->db->insert($this->tables['crawler_instances'], $this);
        return $this->db->insert_id();
    }




    function delete($id)
    {
        return $this->db->delete($this->tables['crawler_instances'], array('id' => $id));
    }

}