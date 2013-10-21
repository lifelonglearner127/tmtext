<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Department_members_model extends CI_Model {
    

    var $tables = array(
        'department_members' => 'department_members',
        'site_departments_snaps' => 'site_departments_snaps',
        'site_departments_reports' => 'site_departments_reports',
        'users' => 'users'
    );

    function __construct()
    {
        parent::__construct();
    }

    function deleteDepRecSet($id) {
        return $this->db->delete($this->tables['site_departments_reports'], array('id' => $id));
    }

    function getUserObjectByEmail($email) {
        $res = null;
        $check_obj = array(
            'email' => $email
        );
        $query = $this->db->where($check_obj)->get($this->tables['users']);
        $res_query = $query->result();
        if(count($res_query) > 0) {
            $res = $res_query[0];
        }
        return $res;
    }

    function getUserObjectById($uid) {
        $res = null;
        $check_obj = array(
            'id' => $uid
        );
        $query = $this->db->where($check_obj)->get($this->tables['users']);
        $res_query = $query->result();
        if(count($res_query) > 0) {
            $res = $res_query[0];
        }
        return $res;
    }

    function getDepReportsByUserId($uid) {
        $check_obj = array(
            'uid' => $uid
        );
        $query = $this->db->where($check_obj)->order_by('stamp desc')->get($this->tables['site_departments_reports']);
        return $query->result();
    }

    function getDepReportsByIds($rep_ids) {
        $query = $this->db->where_in('id', $rep_ids)->order_by('stamp desc')->get($this->tables['site_departments_reports']);
        return $query->result();
    }

    function getUserDepRepSets($uid) {
        $check_obj = array(
            'uid' => $uid
        );
        $query = $this->db->where($check_obj)->order_by('stamp desc')->get($this->tables['site_departments_reports']);
        return $query->result();
    }

    function recordUpdateDepReportSet($db_row) {
        $check_obj = array(
            'uid' => (int)$db_row['uid'],
            'set_id' => $db_row['set_id'],
            'main_choose_dep' => (int)$db_row['main_choose_dep'],
            'main_choose_site' => (int)$db_row['main_choose_site']
        );
        $query = $this->db->where($check_obj)->get($this->tables['site_departments_reports']);
        $q_res = $query->result();
        if(count($q_res) > 0) {
            $r = $q_res[0];
            $data = array(
                'stamp' => date("Y-m-d H:i:s")
            );
            $this->db->where('id', $r->id);
            $this->db->update($this->tables['site_departments_reports'], $data);
        } else {
            $insert_object = array(
                'uid' => (int)$db_row['uid'],
                'set_id' => $db_row['set_id'],
                'main_choose_dep' => (int)$db_row['main_choose_dep'],
                'main_choose_site' => (int)$db_row['main_choose_site'],
                'json_encode_com' => $db_row['json_encode_com'],
                'stamp' => date("Y-m-d H:i:s")
            );
            $this->db->insert($this->tables['site_departments_reports'], $insert_object);
        }
        return true;
    }

    // function recordUpdateDepReportSet($db_row) {
    //     $check_obj = array(
    //         'uid' => (int)$db_row['uid'],
    //         'set_id' => $db_row['set_id'],
    //         'main_choose_dep' => (int)$db_row['main_choose_dep'],
    //         'main_choose_site' => (int)$db_row['main_choose_site'],
    //         'sec_site_chooser' => (int)$db_row['sec_site_chooser'],
    //         'sec_dep_chooser' => (int)$db_row['sec_dep_chooser']
    //     );
    //     $query = $this->db->where($check_obj)->get($this->tables['site_departments_reports']);
    //     $q_res = $query->result();
    //     if(count($q_res) > 0) {
    //         $r = $q_res[0];
    //         $data = array(
    //             'stamp' => date("Y-m-d H:i:s")
    //         );
    //         $this->db->where('id', $r->id);
    //         $this->db->update($this->tables['site_departments_reports'], $data);
    //     } else {
    //         $insert_object = array(
    //             'uid' => (int)$db_row['uid'],
    //             'set_id' => $db_row['set_id'],
    //             'main_choose_dep' => (int)$db_row['main_choose_dep'],
    //             'main_choose_site' => (int)$db_row['main_choose_site'],
    //             'sec_site_chooser' => (int)$db_row['sec_site_chooser'],
    //             'sec_dep_chooser' => (int)$db_row['sec_dep_chooser'],
    //             'stamp' => date("Y-m-d H:i:s")
    //         );
    //         $this->db->insert($this->tables['site_departments_reports'], $insert_object);
    //     }
    //     return true;
    // }

    function getDepartmentsBySiteId($site_id) {
        $check_obj = array(
            'site_id' => $site_id,
            'url !=' => ''
        );
        $query = $this->db->where($check_obj)->get($this->tables['department_members']);
        return $query->result();
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
            $fs = file_get_contents($r->snap_path);
            $res_data['dep_id'] = $r->dep_id;
            $res_data['snap_name'] = $r->snap_name;
            $res_data['snap_path'] = $r->snap_path;
            $res_data['snap_dir'] = $r->snap_dir;
            $res_data['http_status'] = $r->http_status;
            $res_data['stamp'] = $r->stamp;
            if($fs !== false) {
                $res_data['img_av_status'] = true;
            }
        }
        return $res_data;
    }

    function updateSiteDepartmentSnap($dep_id, $snap_name, $snap_path, $snap_dir, $http_status)  {
        $data = array(
            'snap_name' => $snap_name,
            'snap_path' => $snap_path,
            'snap_dir' => $snap_dir,
            'http_status' => $http_status,
            'stamp' => date("Y-m-d H:i:s")
        );
        $this->db->where('dep_id', $dep_id);
        $this->db->update($this->tables['site_departments_snaps'], $data);
        return true;
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
        $sql = "SELECT `id`, `text`, `url` FROM `department_members` WHERE `site_id` = '".$customerID."' and flag='ready' group by `text` ORDER BY `text` ASC";
        $query = $this->db->query($sql);
        return $query->result();
    }

    function getDataByDepMemberId($dm_id) {
        $sql = "SELECT `d`.`id`, `d`.`text`, `d`.`description_text`, `d`.`description_words`, `d`.`title_keyword_description_density`, `d`.`title_keyword_description_count`,
        `d`.`url`, `s`.`snap_path` FROM `department_members` as `d`
        left join `site_departments_snaps` as `s` on `d`.`id` = `s`.`dep_id`
            WHERE `d`.`id` = '".$dm_id."' and `d`.`flag`='ready' and `s`.`dep_id` is not null";
        $query = $this->db->query($sql);
        $res = $query->result();
        if(count($res) > 0) {
            return $res[0];
        } else {
            return array();
        }
    }
    
    function getAllSnapsByCustomerID($customerID)
    {
        // $sql = "SELECT `d`.`id`, `d`.`text`, `d`.`description_text`, `d`.`description_words`, `d`.`title_keyword_description_density`,
        // `d`.`url`, `s`.`snap_path` FROM `department_members` as `d`
        // left join `site_departments_snaps` as `s` on `d`.`id` = `s`.`dep_id`
        //     WHERE `d`.`site_id` = '".$customerID."' and `d`.`flag`='ready' and `s`.`dep_id` is not null";

        // $sql = "SELECT `d`.`id`, `d`.`text`, `d`.`description_text`, `d`.`description_words`, `d`.`title_keyword_description_density`,
        // `d`.`url`, `s`.`snap_path` FROM `department_members` as `d`
        // left join `site_departments_snaps` as `s` on `d`.`id` = `s`.`dep_id`
        //     WHERE `d`.`site_id` = '".$customerID."' and `d`.`flag`='ready' and `s`.`dep_id` is not null ORDER BY `d`.`text` ASC";
        // $query = $this->db->query($sql);

        $sql = "SELECT `d`.`id`, `d`.`text`, `d`.`description_text`, `d`.`description_words`, `d`.`title_keyword_description_density`,
        `d`.`url`, `s`.`snap_path` FROM `department_members` as `d`
        left join `site_departments_snaps` as `s` on `d`.`id` = `s`.`dep_id`
            WHERE `d`.`site_id` = '".$customerID."' and `s`.`snap_path` != '' and `d`.`flag`='ready' and `s`.`dep_id` is not null ORDER BY `d`.`text` ASC";
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
        $sql = "SELECT  `id`, `description_title`, `title_keyword_description_density` ,`user_keyword_description_density`, `user_seo_keywords` FROM `department_members` WHERE `site_id` = '".$site_id."' ".$department_id." and `flag`='ready' ORDER BY `text` ASC";
        $query = $this->db->query($sql);
        return $query->result();
    }
    
    function getDataByDepartment($department_id){
        $sql = "SELECT `description_text`, `description_words` FROM `department_members` WHERE `id` = '".$department_id."' and `flag`='ready'";
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
            'title_keyword_description_count' => $keyword_count,
            'title_keyword_description_density' => $keyword_density,
            'description_title' => $description_title
        );
        
        $this->db->where('id', $check_id);
        $this->db->update($this->tables['department_members'], $data);
        return $check_id;
    }

    function delete($id)
    {
        $data = array(
            'flag' => 'deleted'
        );

        $this->db->where('id', $id);
        $this->db->update($this->tables['department_members'], $data);
        return $id;
    }

    function deleteAll($site_id)
    {
        $data = array(
            'flag' => 'deleted'
        );

        $this->db->where('site_id', $site_id);
        $this->db->update($this->tables['department_members'], $data);
        return $site_id;
    }

    function checkExist($site_id, $text, $url='')
    {
        $str = '';
        if($url != ''){
            $str .= " and `url`='".addslashes($url)."'";
        }
        $query = $this->db->query("SELECT `id` FROM `department_members` WHERE `site_id`= '".$site_id."' ".$str." and  `text` = '".$text."' limit 1");
        if($query->num_rows() > 0) {
            return $query->row()->id;
        }
        return false;
    }

    function updateFlag($site_id, $text)
    {
        $data = array(
            'flag' => 'ready'
        );

        $this->db->where('site_id', $site_id);
        $this->db->where('text', trim($text));
        return $this->db->update($this->tables['department_members'], $data);
    }


    function getDescriptionData($site_id)
    {
        $sql = $this->db->query("SELECT count(*) as total,
            (SELECT round(avg(`description_words`)) AS c  FROM `department_members` WHERE `site_id`=".$site_id." and `description_words`>0 GROUP BY `site_id`) as res_avg,
            count(if((`description_words`>0 and `description_words`<250), id, null)) as more,
            count(if(`description_words`>0, id, null)) as more_than_0
            FROM `department_members` WHERE `site_id`=".$site_id."");
        $result = $sql->result();
        $sql_more_data = $this->db->query("SELECT `id`, `text`, `url`, `description_words`, `title_keyword_description_density` FROM `department_members` WHERE `site_id`=".$site_id." and (`description_words`>0 and `description_words`<250) and `flag`='ready' order by `text` asc");
        $result_more_data = $sql_more_data->result();
        $sql_data_more_than_0 = $this->db->query("SELECT `id`, `text`,`url`, `description_words`, `title_keyword_description_density` FROM `department_members` WHERE `site_id`=".$site_id." and `description_words` > 0 and `flag`='ready' order by `text` asc");
        $res_data_more_than_0 = $sql_data_more_than_0->result();
        $sql0 = $this->db->query("SELECT `id`, `text`, `url`, `description_words`, `title_keyword_description_density` FROM `department_members` WHERE `site_id`=".$site_id." and `description_words`=0 and `flag`='ready' order by `text` asc");
        $result0 = $sql0->result();
        return array('total' => $result[0]->total, 'result0'=> $result0,
            'res_avg' => $result[0]->res_avg, 'res_more' => $result[0]->more, 'res_more_data' => $result_more_data,
            'res_more_than_0' => $result[0]->more_than_0, 'res_data_more_than_0' => $res_data_more_than_0 );
    }

    function getDepartmentsByWc($site_id)
    {
        $sql = "SELECT * FROM `department_members` WHERE `site_id` = '".$site_id."' and `description_words` > 0 and `flag`='ready' order by `text` asc";
        $query = $this->db->query($sql);
        return $query->result();
    }
    
    function updateDepartment($id,$data){
        $this->db->where('id', $id);
        $this->db->update($this->tables['department_members'], $data);
    }
}