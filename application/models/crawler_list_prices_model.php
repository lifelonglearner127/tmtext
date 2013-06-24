<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Crawler_List_Prices_model extends CI_Model {

    var $tables = array(
    	'crawler_list_prices' => 'crawler_list_prices'
    );

    var $price = 0;
    var $crawler_list_id = 0;
    var $created = '';

    function __construct()
    {
        parent::__construct();
    }

    function get($id)
    {
    	$query = $this->db->where('id', $id)
                    ->limit(1)
                    ->get($this->tables['crawler_list_prices']);

        return $query->result();
    }

    function getByCrawlerListId($id)
    {
    	$query = $this->db->where('crawler_list_id', $id)
                    ->get($this->tables['crawler_list_prices']);

        return $query->result();
    }

    function getAll()
    {
        $query = $this->db->order_by('created', 'asc')->get($this->tables['crawler_list_prices']);

        return $query->result();
    }

    function insert($crawler_list_id, $price) {

    	$this->crawler_list_id = $crawler_list_id;
    	$this->price = $price;
        $this->created = date('Y-m-d h:i:s');

        $this->db->insert($this->tables['crawler_list_prices'], $this);
        return $this->db->insert_id();
    }
}
