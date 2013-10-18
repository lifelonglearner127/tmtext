<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Research_data_to_crawler_list_model extends CI_Model {

    var $research_data_id  = 0;
    var $crawler_list_id = 0;


    var $tables = array(
        'research_data_to_crawler_list' => 'research_data_to_crawler_list',
    );

    function __construct()
    {
        parent::__construct();
    }

    function get($id)
    {
        $query = $this->db->where('id', $id)
            ->limit(1)
            ->get($this->tables['research_data_to_crawler_list']);

        return $query->result();
    }

    function insert($research_data_id, $crawler_list_id)
    {
        $this->research_data_id = $research_data_id;
        $this->crawler_list_id = $crawler_list_id;

        $this->db->insert($this->tables['research_data_to_crawler_list'], $this);
        return $this->db->insert_id();
    }

}