<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Department_members_model extends CI_Model {

    var $department_id = 0;
    var $site = '';
    var $site_id = 0;
    var $customer_id = 0;
    var $text = '';
    var $url = '';
    var $level = 0;
    var $parent_id = null;

    var $tables = array(
        'department_members' => 'department_members'
    );

    function __construct()
    {
        parent::__construct();
    }

    function get($id)
    {
        $query = $this->db->where('id', $id)
            ->limit(1)
            ->get($this->tables['department_members']);

        return $query->result();
    }

    function getAll()
    {
        $sql = "SELECT `id`, `text` FROM `department_members` group by `text` ORDER BY `text` ASC";
        $query = $this->db->query($sql);
        return $query->result();
    }

    function getAllByCustomer($customer)
    {
        $sql = "SELECT `id`, `text` FROM `department_members` WHERE `site` = '".$customer."' group by `text` ORDER BY `text` ASC";
        $query = $this->db->query($sql);
        return $query->result();
    }

    function getUrlByDepartment($id){
        $sql = "SELECT `url` FROM `department_members` WHERE id=".$id;
        $query = $this->db->query($sql);
        return $query->result();
    }
    
    function getDataByDepartmentId($site_id, $department_id=''){
        
        if($department_id != ''){
            $department_id = " and `id`='".$department_id."' ";
        }
        $sql = "SELECT  `id`, `description_title`, `title_keyword_description_density` ,`user_keyword_description_density`, `user_seo_keywords` FROM `department_members` WHERE `site_id` = '".$site_id."' ".$department_id." ORDER BY `text` ASC";
        $query = $this->db->query($sql);
        return $query->result();
    }
    
    function getDataByDepartment($department_id){
	$sql = "SELECT `description_text`, `description_words` FROM `department_members` WHERE `id` = '".$department_id."'";
    $query = $this->db->query($sql);
	$result = $query->result();
    return $result[0];
    }
    
     
    function UpdateKeywordsDepartmentData($department_id, $user_seo_keywords = "",$user_keyword_description_count = 0,$user_keyword_description_density = 0){
	 $sql="UPDATE `department_members` SET `user_seo_keywords` = '".$user_seo_keywords."',`user_keyword_description_count` = $user_keyword_description_count,`user_keyword_description_density` = $user_keyword_description_density WHERE `id` = $department_id";
	 $query = $this->db->query($sql);
	 return $query;
    }

    function insert($site_name, $site_id, $text, $description_wc,$description_text,$keyword_density,$description_title)
    {
        $this->text = $text;
        $this->site = $site_name;
        $this->site_id = $site_id;
        if($description_wc != NULL)
            $this->description_words = $description_wc;
        if($description_text !=NULL)
            $this->description_text=$description_text;
        if($keyword_density !=NULL)
            $this->title_keyword_description_density=$keyword_density;
        if($description_title !=NULL)
            $this->description_title=$description_title;
        
        $this->db->insert($this->tables['department_members'], $this);
        return $this->db->insert_id();
    }

    function delete($id)
    {
        return $this->db->delete($this->tables['department_members'], array('id' => $id));
    }

    function deleteAll($site)
    {
        return $this->db->delete($this->tables['department_members'], array('site' => $site));
    }

    function checkExist($site_name, $site_id, $text)
    {
        $query =  $this->db->select('id')
            ->from($this->tables['department_members'])
            ->where('site', trim($site_name))->where('site_id', trim($site_id))->where('text', trim($text))->limit(1)->get();
        if($query->num_rows() > 0) {
            return $query->row()->id;
        }
        return false;
    }
}