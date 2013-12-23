<?php

class User_summary_settings extends Base_model 
{
	const USER_SUMMARY_SETTING_FILTER = 1;
	const USER_SUMMARY_SETTING_FILTER_ORDER = 2;
	
	public $id;
	public $setting_id;
	public $setting_value;
	public $user_id;
	public $user_ip;
	public $create_time;
	public $update_time;	
	
	public $settings = array(
		self::USER_SUMMARY_SETTING_FILTER => 'Summary filter items',
		self::USER_SUMMARY_SETTING_FILTER_ORDER => 'Summary filter items order'
	);
	
	public function __construct()
	{		
		parent::__construct();			
	}
	
	private function getRules()
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
	
	public function beforeSave()
	{
		if (!$this->create_time)
			$this->create_time = time();
		
		$this->update_time = time();
		
		$this->user_ip = $_SERVER['REMOTE_ADDR'];
		
		return true;
	}	
	
	public function beforeValidate()
	{
		$rules = $this->getRules();
		$r = $this->validateRules($rules);
		
		return $r;
	}
	
	public function save()
	{
		if (!$this->beforeValidate() || !$this->beforeSave())
			return false;
		
		if ($this->id) 
		{
			$this->db->update($this->getTableName(), $this, array('id' => $this->id));
		} else {
			$this->db->insert($this->getTableName(), $this);
		}
		
		return true;
	}
	
	public function getSettings($setting_id = null)
	{
		return is_null($setting_id) ? $this->settings : $this->settings[$setting_id];
	}

	public function find($id)
	{
		$query = $this->db
			->where(array('id' => $id))
			->get($this->getTableName());
			
		return $query->row();
	}
	
	public function findByAttributes(array $attributes)
	{
		$query = $this->db
			->where($attributes)
			->limit(1)
			->get($this->getTableName());
			
		return $query->row();
	}
	
	public function setAttributes(array $data = array())
	{
		foreach ($data as $field_name => $field_value)
			$this->{$field_name} = $field_value;
	}
}