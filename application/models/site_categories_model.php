<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Site_categories_model extends CI_Model {

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

    function getLatestCatScreen($cat_id) {
        $res_data = array(
            'cat_id' => '',
            'snap_name' => '',
            'snap_path' => '',
            'snap_dir' => '',
            'http_status' => '',
            'stamp' => '',
            'img_av_status' => false
        );
        $check_obj = array(
            'cat_id' => $cat_id
        );
        $query = $this->db->where($check_obj)->order_by('stamp', 'desc')->limit(1)->get($this->tables['site_categories_snaps']);
        $query_res = $query->result();
        if(count($query_res) > 0) {
            $r = $query_res[0];
            $fs = filesize($r->snap_dir);
            $res_data['cat_id'] = $r->cat_id;
            $res_data['snap_name'] = $r->snap_name;
            $res_data['snap_path'] = $r->snap_path;
            $res_data['snap_dir'] = $r->snap_dir;
            $res_data['http_status'] = $r->http_status;
            $res_data['stamp'] = $r->stamp;
            if($fs !== false || $fs > 10000) {
                $res_data['img_av_status'] = true;
            }
        }
        return $res_data;
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
        $query = $this->db->where('id', $id)->where('flag', 'ready')
            ->limit(1)
            ->get($this->tables['site_categories']);

        return $query->result();
    }

    function getCatsBySideId($site_id) {
        $query = $this->db->where('site_id', $site_id)->where('flag', 'ready')
            ->limit(1)
            ->get($this->tables['site_categories']);

        return $query->result();
    }

    function getAllBySiteId($site_id, $department_id=''){
        if($department_id != ''){
            $department_id = " and `department_members_id`='".$department_id."' ";
        }
        $sql = "SELECT * FROM `site_categories` WHERE `flag`='ready' and `site_id` = '".$site_id."' ".$department_id." ORDER BY `text` ASC";
        $query = $this->db->query($sql);
        return $query->result();
    }
	
	function getDataByCategory($category_id){
	$sql = "SELECT `description_text`, `description_words` FROM `site_categories` WHERE `flag`='ready' and `id` = '".$category_id."'";
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
        $sql = "SELECT `url` FROM `site_categories` WHERE `id` = '".$category_id."' and `flag`='ready'";
        $query = $this->db->query($sql);
        return $query->result();
    }

    function insert($parent_id, $site_id, $text = '', $url = '', $special = 0, $parent_text = '', $department_members_id = 0,
                    $nr_products = 0, $description_wc = 0, $title_keyword_description_count = '', $title_keyword_description_density = '', $description_title = '', $description_text = '', $level='')
    {
        $data = array(
            'parent_id' => $parent_id,
            'site_id' => $site_id,
            'text' => $text,
            'url' => $url,
            'special' => $special,
            'parent_text' => $parent_text,
            'department_members_id' => $department_members_id,
            'level' => $level,
            'nr_products' => $nr_products,
            'description_words' => $description_wc,
            'title_keyword_description_count' => $title_keyword_description_count,
            'title_keyword_description_density' => $title_keyword_description_density,
            'description_title' => $description_title,
            'description_text' => $description_text
        );
        
        $this->db->insert($this->tables['site_categories'], $data);
        return $this->db->insert_id();
    }

    function delete($id)
    {
        $data = array(
            'flag' => 'deleted'
        );

        $this->db->where('id', $id);
        $this->db->update($this->tables['site_categories'], $data);
        return $id;
    }

    function deleteAll($site_id)
    {
        $data = array(
            'flag' => 'deleted'
        );

        $this->db->where('site_id', $site_id);
        $this->db->update($this->tables['site_categories'], $data);
        return $site_id;
    }

    function checkExist($site_id, $text, $department_id='')
    {
        $str = "";
        if($department_id!=''){
            $str .= " and `department_members_id` = '".$department_id."'";
        }
        $sql = $this->db->query("SELECT `id` FROM `site_categories` WHERE `site_id` = '".$site_id."' and `flag`='ready' ".$str." and `text`='".trim($text)."' limit 1");
        if($query->num_rows() > 0) {
            return $query->row()->id;
        }
        return false;
    }

    function updateFlag($site_id, $text, $department_id)
    {
        $data = array(
            'flag' => 'ready'
        );

        $this->db->where('site_id', $site_id);
        $this->db->where('text', trim($text));
        $this->db->where('department_members_id', $department_id);
        $this->db->update($this->tables['site_categories'], $data);
    }

    function checkDepartmentId($parent_id)
    {
        $sql = "SELECT `department_members_id` FROM `site_categories` WHERE `id` = '".$parent_id."' and `flag`='ready'";
        $query = $this->db->query($sql);
        $result = $query->result();
        return $result[0];
    }

    function getDescriptionData($site_id)
    {
        $sql = $this->db->query("SELECT count(*) as total,
                (SELECT round(avg(`description_words`)) AS c  FROM `site_categories` WHERE `site_id`=".$site_id." and `description_words`>0 GROUP BY `site_id`) as res_avg,
                count(if((`description_words`>0 and `description_words`<250), id, null)) as more,
                count(if(`description_words`>0, id, null)) as more_than_0
                FROM  `site_categories` WHERE `site_id`=".$site_id." and `flag`='ready'");
        $result = $sql->result();
        return array(
            'total' => $result[0]->total,
            'res_avg' => $result[0]->res_avg,
            'res_more' => $result[0]->more,
            'res_more_than_0' => $result[0]->more_than_0
        );
    }

    function getCategoriesByWc($site_id)
    {
        $sql = "SELECT * FROM `site_categories` WHERE `site_id` = '".$site_id."' and `description_words` > 0  and `flag`='ready' group by `text` order by `text` asc";
        $query = $this->db->query($sql);
        return $query->result();
    }

    function getCatData($site_id, $condition)
    {
        $sql = "SELECT `id`, `text`, `url`, `description_words`, `title_keyword_description_density` FROM `site_categories` WHERE `site_id`=".$site_id." and `flag`='ready' and ".$condition." group by `text` order by `text` asc";
        $query = $this->db->query($sql);
        return $query->result();
    }
}