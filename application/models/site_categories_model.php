<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Site_categories_model extends CI_Model {

    var $site_id = 0;
    var $text = '';
    var $url = '';
    var $special = 0;
    var $parent_text = '';

    var $tables = array(
        'site_categories' => 'site_categories',
        'site_categories_snaps' => 'site_categories_snaps'
    );

    function __construct()
    {
        parent::__construct();
    }

    function getAll()
    {
        $this->db->order_by("text", "asc");
        $query = $this->db->get($this->tables['site_categories']);

        return $query->result();
    }

    function insertSiteCategorySnap($cat_id, $snap_name, $snap_path, $snap_dir, $http_status) {
        $insert_object = array(
            'cat_id' => $cat_id,
            'snap_name' => $snap_name,
            'snap_path' => $snap_path,
            'snap_dir' => $snap_dir,
            'http_status' => $http_status,
            'stamp' => date("Y-m-d H:i:s")
        );
        $this->db->insert($this->tables['site_categories_snaps'], $insert_object);
        return $this->db->insert_id();
    }

    function get($id)
    {
        $query = $this->db->where('id', $id)
            ->limit(1)
            ->get($this->tables['site_categories']);

        return $query->result();
    }

    function getAllBySiteId($site_id, $department_id=''){
        if($department_id != ''){
            $department_id = " and `department_members_id`='".$department_id."' ";
        }
        $sql = "SELECT `id`, `text`, `nr_products`, `description_words`, `description_title`, `title_keyword_description_density` ,`user_keyword_description_density`, `user_seo_keywords` FROM `site_categories` WHERE `site_id` = '".$site_id."' ".$department_id." ORDER BY `text` ASC";
        $query = $this->db->query($sql);
        return $query->result();
    }
	
	function getDataByCategory($category_id){
	$sql = "SELECT `description_text`, `description_words` FROM `site_categories` WHERE `id` = '".$category_id."'";
    $query = $this->db->query($sql);
	$result = $query->result();
    return $result[0];
	}
	
	 function UpdateKeywordsData($category_id, $user_seo_keywords = "",$user_keyword_description_count = 0,$user_keyword_description_density = 0){
	 $sql="UPDATE `site_categories` SET `user_seo_keywords` = '".$user_seo_keywords."',`user_keyword_description_count` = $user_keyword_description_count,`user_keyword_description_density` = $user_keyword_description_density WHERE `id` = $category_id";
	 $query = $this->db->query($sql);
	 return $query;
	 }


    function getUrlByCategory($category_id){
        $sql = "SELECT `url` FROM `site_categories` WHERE `id` = '".$category_id."'";
        $query = $this->db->query($sql);
        return $query->result();
    }

    function insert($site_id, $text, $url, $special=0, $parent_text='', $department_members_id = 0, $nr_products = 0 , $description_wc = 0,$title_keyword_description_density,$description_title,$description_text )
    {
        $this->site_id = $site_id;
        $this->text = $text;
        $this->url = $url;
        $this->special = $special;
        $this->parent_text = $parent_text;
        $this->department_members_id = $department_members_id;
		
		if($nr_products != NULL)
			$this->nr_products = $nr_products;
		if($description_wc != NULL)
			$this->description_words = $description_wc;
		if(isset($title_keyword_description_density))
			$this->title_keyword_description_density = $title_keyword_description_density;
		if(isset($description_title))
			$this->description_title = $description_title;
		if(isset($description_text))
			$this->description_text = $description_text;
			
			
        $this->db->insert($this->tables['site_categories'], $this);
        return $this->db->insert_id();
    }

    function delete($id)
    {
        return $this->db->delete($this->tables['site_categories'], array('id' => $id));
    }

    function deleteAll($site_id)
    {
        return $this->db->delete($this->tables['site_categories'], array('site_id' => $site_id));
    }

    function checkExist($site_id, $text)
    {
        $query =  $this->db->select('id')
            ->from($this->tables['site_categories'])
            ->where('site_id', $site_id)->where('text', trim($text))->limit(1)->get();
        if($query->num_rows() > 0) {
            return $query->row()->id;
        }
        return false;
    }
}