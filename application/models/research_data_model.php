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
        'research_data' => 'research_data',
        'batches' => 'batches',
        'users' => 'users',
        'items' => 'items'
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
                    $meta_description, $meta_keywords, $short_description, $short_description_wc, $long_description, $long_description_wc, $revision = 1)
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
        $this->short_description_wc = $short_description_wc;
        $this->long_description = $long_description;
        $this->long_description_wc = $long_description_wc;
        $this->revision = $revision;

        $this->created = date('Y-m-d h:i:s');
        $this->modified = date('Y-m-d h:i:s');
        $this->db->insert($this->tables['research_data'], $this);
        return $this->db->insert_id();
    }

   function update($id, $batch_id, $url, $product_name, $short_description, $short_description_wc, $long_description, $long_description_wc, $keyword1='', $keyword2='', $keyword3='', $meta_name='',
                    $meta_description='', $meta_keywords='', $revision='')
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
        $this->short_description_wc = $short_description_wc;
        $this->long_description = $long_description;
        $this->long_description_wc = $long_description_wc;
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

   function getInfoFromResearchData($text, $batch_id)
   {
        $batch_first_str = "";
        $batch_second_str = "";
        if($batch_id != ''){
            $batch_first_str = " `rd`.`batch_id`= ". $batch_id ." and ";
            $batch_second_str = " `i`.`batch_id`= ". $batch_id ." and ";
        }

        $query = $this->db->query("(SELECT `rd`.`id`, `rd`.`batch_id`, `rd`.`url`,`rd`.`product_name`, `rd`.`keyword1`, `rd`.`keyword2`, `rd`.`keyword3`, `rd`.`meta_name`,`rd`.`meta_description`, `rd`.`meta_keywords`, `rd`.`short_description`, `rd`.`short_description_wc`, `rd`.`long_description`, `rd`.`long_description_wc`,
        `u`.`email` as `user_id`,
        `b`.`title` as `batch_name`
     FROM ".$this->tables['research_data']." as `rd`
        left join ".$this->tables['batches']." as `b` on `rd`.`batch_id` = `b`.`id`
        left join ".$this->tables['users']." as `u` on `rd`.`user_id` = `u`.`id`
        where ". $batch_first_str." concat(`rd`.`url`, `rd`.`product_name`, `rd`.`keyword1`, `rd`.`keyword2`, `rd`.`keyword3`, `rd`.`meta_name`,
        `rd`.`meta_description`, `rd`.`meta_keywords`, `rd`.`short_description`, `rd`.`short_description_wc`,
        `rd`.`long_description`, `rd`.`long_description_wc`) like '%".$text."%')
union all
    (SELECT `i`.`id`, `i`.`batch_id`, `i`.`url`,`i`.`product_name`, `i`.`keyword1`, `i`.`keyword2`, `i`.`keyword3`, `i`.`meta_name`,`i`.`meta_description`, `i`.`meta_keywords`, `i`.`short_description`, `i`.`short_description_wc`, `i`.`long_description`, `i`.`long_description_wc`,
        `u`.`email` as `user_id`,
        `b`.`title` as `batch_name`
     FROM ".$this->tables['items']." as `i`
        left join ".$this->tables['batches']." as `b` on `i`.`batch_id` = `b`.`id`
        left join ".$this->tables['users']." as `u` on `i`.`user_id` = `u`.`id`
        where ".$batch_second_str." concat(`i`.`url`, `i`.`product_name`, `i`.`keyword1`, `i`.`keyword2`, `i`.`keyword3`, `i`.`meta_name`,
        `i`.`meta_description`, `i`.`meta_keywords`, `i`.`short_description`, `i`.`short_description_wc`,
        `i`.`long_description`, `i`.`long_description_wc`) like '%".$text."%')");

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

    public function updateItem($id, $product_name, $url, $short_description, $long_description, $short_description_wc = 0, $long_description_wc = 0) {
        $data = array(
            'product_name' => $product_name,
            'url' => $url,
            'short_description' => $short_description,
            'long_description' => $long_description,
            'short_description_wc' => $short_description_wc,
            'long_description_wc' => $long_description_wc,
        );

        $this->db->update( 'research_data', $data, array( 'id' => $id ) );
    }

    function delete($id)
    {
        return $this->db->delete($this->tables['research_data'], array('id' => $id));
    }

    public function checkItemUrl($batch_id, $url){
        $query = $this->db->where('url', $url)->where('batch_id', $batch_id)
            ->limit(1)
            ->get($this->tables['research_data']);
        
        return $query->result();
    }

}