<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Settings_model extends CI_Model {

    var $tables = array(
    	'settings' => 'settings',
    	'setting_values' => 'setting_values'
    );

    var $system_user = -1;

    function __construct() {
        parent::__construct();
    }

    function get_general_setting($key) {
        $res = false;
        $query_s = $this->db->where('key', $key)->get($this->tables['settings']);
        $query_s_res = $query_s->result();
        if(count($query_s_res) > 0) {
            $settings = $query_s_res[0];
            $set_id = $settings->id;
            $query_s_value = $this->db->where('setting_id', $set_id)->get($this->tables['setting_values']);
            $query_s_value_res = $query_s_value->result();
            if(count($query_s_value_res) > 0) {
                $settings_val = $query_s_value_res[0];
                $res = $settings_val->value;
            }
        }
        return $res;
    }

    function get_system_value($key) {
		return $this->get_value($this->system_user, $key);
    }

    function get_value($user_id,$key){
    	$sql = "SELECT v.value FROM `{$this->tables['settings']}` s
				JOIN `{$this->tables['setting_values']}` v ON (v.setting_id = s.id)
				WHERE v.user_id = ? AND s.key=? LIMIT 1";

		$query = $this->db->query($sql, array($user_id, $key));

    	if ($query->num_rows() === 1)
		{
			$setting = $query->row();
			if($value = @unserialize($setting->value))
				return $value;
			else
				return $setting->value;
		}
		return false;
    }

	function get_system_settings(){
		return $this->get_settings($this->system_user);
	}

    function get_settings($user_id){
    	$results = array();
    	$sql = "SELECT s.key, v.value FROM `{$this->tables['settings']}` s
				JOIN `{$this->tables['setting_values']}` v ON (v.setting_id = s.id)
				WHERE v.user_id = ?";

		$query = $this->db->query($sql, array($user_id));
		foreach ($query->result() as $row)
		{
			if( strpos($row->value, 'a:')!==false && ($value = @unserialize($row->value)))
				$results[$row->key] = $value;
			else
				$results[$row->key] = $row->value;
		}

		return $results;
    }

    function load_system_settings() {
    	$this->load_user_settings($this->system_user);
    }

    function load_user_settings($user_id) {
    	$CI =& get_instance();

    	foreach ($this->get_settings($user_id) as $k => $v) {
    		$CI->config->set_item($k, $v);
    	}
    }

    function update_system_value($key, $value) {
    	return $this->update_value($this->system_user, $key, $value);
    }

    function update_value($user_id, $key, $value) {
    	$sql = "SELECT s.id FROM `{$this->tables['settings']}` s WHERE s.key=? LIMIT 1";
		$query = $this->db->query($sql, array($key));
    	if ($query->num_rows() === 1)
		{
			$row = $query->row();

			if (is_array($value)) {
				$value = serialize($value);
			}

			if ($this->get_value($user_id, $key) === false) {
				return $this->db->insert($this->tables['setting_values'], array('value' => $value, 'user_id' => $user_id, 'setting_id' => $row->id));
			} else {
				return $this->db->update($this->tables['setting_values'], array('value' => $value), array('user_id' => $user_id, 'setting_id' => $row->id));
			}
		}
		return false;
    }

    function create_system($key, $value, $description = '') {
    	return $this->create($this->system_user, $key, $value, $description);
    }

    function create($user_id, $key, $value, $description = '') {
    	$sql = "SELECT s.id FROM `{$this->tables['settings']}` s WHERE s.key=? LIMIT 1";
		$query = $this->db->query($sql, array($key));
    	if ($query->num_rows() === 1)
		{
			$row = $query->row();
			$setting_id = $row->id;
		} else {
			$this->db->insert($this->tables['settings'], array(
				'key' => $key,
				'description' => $description,
				'created' => date('Y-m-d h:i:s'),
				'modified' => date('Y-m-d h:i:s')
			));
			$setting_id = $this->db->insert_id();
		}

		if (is_array($value)) {
			$value = serialize($value);
		}

		if ($this->get_value($user_id, $key) === false) {
			return $this->db->insert($this->tables['setting_values'], array(
					'setting_id' => $setting_id,
					'user_id' => $user_id,
					'value' => $value
			));
		}
		return false;
    }

    function replace($user_id, $key, $value, $description = '') {
        if(empty($user_id) || empty($key) || empty($value)) {
            return false;
        }
        $sql = "SELECT s.id FROM `{$this->tables['settings']}` s WHERE s.key=? LIMIT 1";
        $query = $this->db->query($sql, array($key));
        if ($query->num_rows() === 1)
        {
            $row = $query->row();
            $setting_id = $row->id;
        } else {
            $this->db->insert($this->tables['settings'], array(
                'key' => $key,
                'description' => $description,
                'created' => date('Y-m-d h:i:s'),
                'modified' => date('Y-m-d h:i:s')
            ));
            $setting_id = $this->db->insert_id();
        }

        if (is_array($value)) {
            $value = serialize($value);
        }

        if ($this->get_value($user_id, $key) === false) {
            return $this->db->insert($this->tables['setting_values'], array(
                'setting_id' => $setting_id,
                'user_id' => $user_id,
                'value' => $value
            ));
        } else {
            $this->db->update($this->tables['setting_values'], array('value' => $value), array('user_id' => $user_id, 'setting_id' => $row->id));
            $afftectedRows = $this->db->affected_rows();
            if($afftectedRows > 0) {
                return true;
            } else {
                return false;
            }
        }
        return false;
    }
    function addMatchingUrls($pr,$lines){
        $data = array(
            'key'=>'matching_urls',
            'description'=>$pr.'|'.$lines.'|'.'0',
            'created'=>date('Y-m-d H:i:s',time()),
            'modified'=>date('Y-m-d H:i:s',time())
        );
        $this->db->insert('settings',$data);
    }
    function procUpdMatchingUrls($pr,$lines,$umi){
        $this->db->where('key','matching_urls');
        $data = array(
            'description'=>$pr.'|'.$lines.'|'.$umi,
            'modified'=>date('Y-m-d H:i:s',time())
        );
        $this->db->update('settings',$data);
    }
    function updateMatchingUrls($pr,$str){
        $data = array('description'=>$str,'modified'=>date('Y-m-d H:i:s',time()));
        $this->db->where('key','matching_urls');
//        $this->db->where('description',$pr);
        $this->db->update('settings',$data);
    }
    function getMatching(){
        $this->db->select('*');
        $this->db->from('settings');
        $this->db->where('key','matching_urls');
        $this->db->order_by('created', "desc");
        $query = $this->db->get();
        if($query->num_rows===0)return FALSE;
        return $query;
    }
    function deledtMatching(){
        $this->db->where('key','matching_urls');
        $this->db->delete('settings');
    }

}
