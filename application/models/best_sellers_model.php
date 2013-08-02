<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Best_sellers_model extends CI_Model {

    var $site_id = 0;
    var $date = '';
    var $page_title = '';
    var $url = '';
    var $brand = '';
    var $price = '';
    var $rank = 0;
    var $department = '';
    var $list_name = '';
    var $product_name = '';
    var $listprice = '';

    var $tables = array(
        'best_sellers' => 'best_sellers'
    );

    function __construct()
    {
        parent::__construct();
    }

    function get($id)
    {
        $query = $this->db->where('id', $id)
            ->limit(1)
            ->get($this->tables['best_sellers']);

        return $query->result();
    }

    function getAll()
    {
        $sql = "SELECT `id`, `page_title` FROM `best_sellers` group by `page_title` ORDER BY `page_title` ASC";
        $query = $this->db->query($sql);
        return $query->result();
    }

    function getAllBySiteId($site_id){
        $sql = "SELECT `id`, `page_title` FROM `best_sellers` WHERE `site_id` = '".$site_id."' ORDER BY `page_title` ASC";
        $query = $this->db->query($sql);
        return $query->result();
    }

    function insert($site_id, $page_title, $url, $brand='', $rank='', $price='',
                    $list_name='', $product_name='', $listprice='')
    {
        $this->site_id = $site_id;
        $this->page_title = $page_title;
        $this->url = $url;
        $this->brand = $brand;
        $this->rank = $rank;
        $this->price = $price;
        $this->list_name = $list_name;
        $this->product_name = $product_name;
        $this->listprice = $listprice;
        $this->date = date('Y-m-d h:i:s');

        $this->db->insert($this->tables['best_sellers'], $this);
        return $this->db->insert_id();
    }

    function delete($id)
    {
        return $this->db->delete($this->tables['best_sellers'], array('id' => $id));
    }

    function deleteAll($site_id)
    {
        return $this->db->delete($this->tables['best_sellers'], array('site_id' => $site_id));
    }
}