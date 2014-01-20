<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Crawler_spot_requests_model extends CI_Model {
	var $request_id = '';
	var $price = '';
	var $instanceid = null;
	var $status_code = '';
	var $crawler_instances_id = null;

    var $tables = array(
        'crawler_spot_requests' => 'crawler_spot_requests'
    );

    function __construct()
    {
        parent::__construct();
    }

    function get($id)
    {
        $query = $this->db->where('id', $id)
            ->limit(1)
            ->get($this->tables['crawler_spot_requests']);

        return $query->result();
    }

    function getAll()
    {
        $query = $this->db->get($this->tables['crawler_spot_requests']);
        return $query->result();
    }

    function getNotTerminated()
    {
    	$this->db->where_not_in('state_name', array('cancelled','closed'));
        $query = $this->db->get($this->tables['crawler_spot_requests']);
        return $query->result();
    }

    function insert($request_id, $price, $instanceid, $state_name, $status_code)
    {
        $this->request_id = $request_id;
        $this->price = $price;
        $this->instanceid = $instanceid;
		$this->state_name = $state_name;
        $this->status_code = $status_code;

        $this->db->insert($this->tables['crawler_spot_requests'], $this);
        return $this->db->insert_id();
    }

    function update($request_id, $price, $instanceid, $state_name, $status_code, $crawler_instances_id = null)
    {
    	$update = array(
        	'request_id' => $request_id,
        	'price' => $price,
//        	'instanceid' => $instanceid,
        	'state_name' => $state_name,
        	'status_code' => $status_code,
		);

		if (isset($instanceid) && !empty($instanceid)) {
			$update['instanceid'] = $instanceid;
		}

		if (isset($crawler_instances_id)) {
			$update['crawler_instances_id'] = $crawler_instances_id;
		}

    	return $this->db->update($this->tables['crawler_spot_requests'],
                $update,
                array('request_id' => $request_id));
    }

    function delete($id)
    {
        return $this->db->delete($this->tables['crawler_spot_requests'], array('id' => $id));
    }

}