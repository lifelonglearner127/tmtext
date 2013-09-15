<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Department_members_model extends CI_Model {
    

    var $tables = array(
        'department_members' => 'department_members',
        'site_departments_snaps' => 'site_departments_snaps'
    );

    function __construct()
    {
        parent::__construct();
    }

    function getLatestDepartmentScreen($dep_id) {
        $res_data = array(
            'dep_id' => '',
            'snap_name' => '',
            'snap_path' => '',
            'snap_dir' => '',
            'http_status' => '',
            'stamp' => '',
            'img_av_status' => false
        );
        $check_obj = array(
            'dep_id' => $dep_id
        );
        $query = $this->db->where($check_obj)->order_by('stamp', 'desc')->limit(1)->get($this->tables['site_departments_snaps']);
        $query_res = $query->result();
        if(count($query_res) > 0) {
            $r = $query_res[0];
            $fs = filesize($r->snap_dir);
            $res_data['dep_id'] = $r->dep_id;
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

    function insertSiteDepartmentSnap($dep_id, $snap_name, $snap_path, $snap_dir, $http_status) {
        $insert_object = array(
            'dep_id' => $dep_id,
            'snap_name' => $snap_name,
            'snap_path' => $snap_path,
            'snap_dir' => $snap_dir,
            'http_status' => $http_status,
            'stamp' => date("Y-m-d H:i:s")
        );
        $this->db->insert($this->tables['site_departments_snaps'], $insert_object);
        return $this->db->insert_id();
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

    function getAllByCustomerID($customerID)
    {
        $sql = "SELECT `id`, `text` FROM `department_members` WHERE `site_id` = '".$customerID."' group by `text` ORDER BY `text` ASC";
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

    function insert($parent_id, $site_id, $department_id = '', $text = '', $url = '',$description_wc = 0, $description_text = '',
                    $keyword_count = '', $keyword_density = '', $description_title = '', $level)
    {
        $data = array(
            'text' => $text,
            'url' => $url,
            'department_id' => $department_id,
            'site_id' => $site_id,
            'parent_id' => $parent_id,
            'level' => $level,
            'description_words' => $description_wc,
            'description_text' => $description_text,
            'title_keyword_description_count' => $keyword_count,
            'title_keyword_description_density' => $keyword_density,
            'description_title' => $description_title
        );
        
        $this->db->insert($this->tables['department_members'], $data);
        return $this->db->insert_id();
    }

    function update($check_id, $department_id = '', $description_wc = 0,$description_text = '', $keyword_count = '',
                    $keyword_density = '',$description_title = '',$level)
    {
        $data = array(
            'level' => $level,
            'department_id' => $department_id,
            'description_words' => $description_wc,
            'description_text' => $description_text,
            'title_keyword_description_count' => $keyword_cout,
            'title_keyword_description_density' => $keyword_density,
            'description_title' => $description_title
        );
        
        $this->db->where('id', $check_id);
        $this->db->update($this->tables['department_members'], $data);
        return $check_id;
    }

    function delete($id)
    {
        return $this->db->delete($this->tables['department_members'], array('id' => $id));
    }

    function deleteAll($site_id)
    {
        return $this->db->delete($this->tables['department_members'], array('site_id' => $site_id));
    }

    function checkExist($site_id, $text)
    {
        $query =  $this->db->select('id')
            ->from($this->tables['department_members'])
            ->where('site_id', trim($site_id))->where('text', trim($text))->limit(1)->get();
        if($query->num_rows() > 0) {
            return $query->row()->id;
        }
        return false;
    }
}