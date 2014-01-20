<?php

require_once(APPPATH . 'models/base_model.php');

class User_summary_settings extends Base_model 
{
	const USER_SUMMARY_SETTING_FILTER = 1;
	const USER_SUMMARY_SETTING_FILTER_ORDER = 2;
	const USER_SUMMARY_SETTING_SELECTED_COLUMNS = 3;
	
	public $id;
	public $setting_id;
	public $setting_value;
	public $user_id;
	public $user_ip;
	public $create_time;
	public $update_time;	
	
	public $settings = array(
		self::USER_SUMMARY_SETTING_FILTER => 'Summary filter items',
		self::USER_SUMMARY_SETTING_FILTER_ORDER => 'Summary filter items order',
		self::USER_SUMMARY_SETTING_SELECTED_COLUMNS => 'Summary filter items order',
	);	
	
	public function getRules()
	{
		return array(
			'setting_id' => array('type' => 'required'),
			'setting_value' => array('type' => 'required')
		);
	}
	
	public function getTableName()
	{
		return 'user_summary_settings';
	}		
	
	public function getSettings($setting_id = null)
	{
		return is_null($setting_id) ? $this->settings : $this->settings[$setting_id];
	}			
}