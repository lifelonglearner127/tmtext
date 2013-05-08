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
			if($value = @unserialize($row->value))
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
			return $this->db->update($this->tables['setting_values'], array('value' => $value), array('user_id' => $user_id, 'setting_id' => $row->id));
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
}
