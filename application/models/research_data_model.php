<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Research_data_model extends CI_Model {

    var $batch_id  = 0;
    var $user_id = 0;
    var $url = '';
    var $product_name = '';
    var $keyword1 = '';
    var $keyword2 = '';
    var $keyword3 = '';
    var $meta_name = '';
    var $meta_description = '';
    var $meta_keywords = '';
    var $short_description = '';
    var $long_description = '';
    var $created = '';
    var $modified = '';


    var $tables = array(
        'research_data' => 'research_data'
    );

    function __construct()
    {
        parent::__construct();
    }

    function get($id)
    {
        $query = $this->db->where('id', $id)
            ->limit(1)
            ->get($this->tables['research_data']);

        return $query->result();
    }

    function insert($batch_id, $url, $product_name, $keyword1, $keyword2, $keyword3, $meta_name,
                    $meta_description, $meta_keywords, $short_description, $long_description, $revision = 1)
    {
        $CI =& get_instance();
        $this->batch_id = $batch_id;
        $this->user_id = $CI->ion_auth->get_user_id();
        $this->url = $url;
        $this->product_name = $product_name;
        $this->keyword1 = $keyword1;
        $this->keyword2 = $keyword2;
        $this->keyword3 = $keyword3;
        $this->meta_name = $meta_name;
        $this->meta_description = $meta_description ;
        $this->meta_keywords = $meta_keywords;
        $this->short_description = $short_description;
        $this->long_description = $long_description;
        $this->revision = $revision;

        $this->created = date('Y-m-d h:i:s');
        $this->modified = date('Y-m-d h:i:s');
        $this->db->insert($this->tables['research_data'], $this);
        return $this->db->insert_id();
    }

   function update($id, $batch_id, $url, $product_name, $keyword1, $keyword2, $keyword3, $meta_name,
                    $meta_description, $meta_keywords, $short_description, $long_description, $revision)
    {
        $CI =& get_instance();
        $this->batch_id = $batch_id;
        $this->user_id = $CI->ion_auth->get_user_id();
        $this->url = $url;
        $this->product_name = $product_name;
        $this->keyword1 = $keyword1;
        $this->keyword2 = $keyword2;
        $this->keyword3 = $keyword3;
        $this->meta_name = $meta_name;
        $this->meta_description = $meta_description;
        $this->meta_keywords = $meta_keywords;
        $this->short_description = $short_description;
        $this->long_description = $long_description;
        $this->revision = $revision;
        $this->modified = date('Y-m-d h:i:s');

        return $this->db->update($this->tables['research_data'],
            $this,
            array('id' => $id));
    }

    function getAllByProductName( $product_name, $batch_id='')
    {
        if($batch_id == '') {
            $query = $this->db->where('product_name', $product_name)->limit(1)->get($this->tables['research_data']);
        } else {
            $query = $this->db->where('product_name', $product_name)->where('batch_id', $batch_id)
                ->limit(1)
                ->get($this->tables['research_data']);
        }

        return $query->result();
    }

    function getDataByBatchId($text, $batch_id)
    {
        $query = $this->db->query("select *, DATE_FORMAT(`created`,'%d-%m-%Y') as created from ".$this->tables['research_data']." where concat(url, product_name,
            keyword1, keyword2, keyword3, meta_name, meta_description, meta_keywords, short_description, long_description ) like '%".$text."%'
             and batch_id=".$batch_id);
        return $query->result();
    }

    function getLastRevision(){
        $query = $this->db->select('revision')->limit(1)->order_by("id", "desc")->get($this->tables['research_data']);
        return $query->result();
    }

    function getAllByBatchId($batch_id){
        $query = $this->db->where('batch_id', $batch_id)->get($this->tables['research_data']);
        return $query->result();
    }

    function delete($id)
    {
        return $this->db->delete($this->tables['research_data'], array('id' => $id));
    }

}