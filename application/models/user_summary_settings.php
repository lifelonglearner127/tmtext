<?php

class User_summary_settings extends CI_Model 
{
	const USER_SUMMARY_SETTING_FILTER = 1;
	
	public $setting_id;
	public $setting_value;
	public $user_id;
	public $user_ip;
	public $create_time;
	public $update_time;
	
	public $settings = array(
		self::USER_SUMMARY_SETTING_FILTER => 'Summary filter items'
	);
	
	public function __construct()
	{
		parent::__construct();
		
		
	}
	
	public function beforeSave()
	{
		if (!$this->create_time)
			$this->create_time = time();
		
		$this->update_time = time();
		
		return true;
	}	
	
	public function beforeValidate()
	{
		return true;
	}
	
	public function save()
	{
		if (!$this->beforeValidate() || !$this->beforeSave())
			return false;
				
		return true;
	}
	
	public function getSettings($setting_id = null)
	{
		return is_null($setting_id) ? $this->settings : $this->settings[$setting_id];
	}
}