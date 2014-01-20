<?php

/**
 *  @file base_model.php
 *  @brief Base model class. All children models should be extended from this Base_model class.
 *  It provides basement ActiveRecord logic which is easier to use than CI query builder.
 *  @author Oleg Meleshko <qu1ze34@gmail.com>
 */
 
abstract class Base_model extends CI_Model 
{
	/**
	 *  @return This method should return database table name.	 	
	 */
	abstract protected function getTableName();
	
	/**
	 *  @brief This method is used for setting up model validation rules.
	 *  
	 *  @return array of validation rules	 
	 */
	abstract protected function getRules();
	
	/**
	 *  @brief This method can be used for finding records in any database table depends on model.
	 *  
	 *  @param $id Primary Key id to be find by
	 *  @return database object	 
	 */
	public function find($id)
	{
		$query = $this->db
			->where(array('id' => $id))
			->get($this->getTableName());
			
		return $query->row();
	}
	
	/**
	 *  @brief This method can be used for finding only one record in any database table depends on model.
	 *  
	 *  @param $attributes query attributes
	 *  @return database object	 
	 */
	public function findByAttributes(array $attributes)
	{
		$query = $this->db
			->where($attributes)
			->limit(1)
			->get($this->getTableName());
			
		return $query->row();
	}
	
	/**
	 *  @brief This method can be used for setting up model attributes.	 	 
	 */
	public function setAttributes(array $data = array())
	{
		foreach ($data as $field_name => $field_value)
			$this->{$field_name} = $field_value;
	}

	/**
	 *  @brief This method validates model rules. 
	 *  It works as an internal method but can be overrided (not recommended).
	 *  Warning: This method will be rewrited soon bc it doesn't work properly for all possible cases, but for current purposes it will work well.
	 *  
	 *  @param $rules array of input model rules
	 *  @return true - model data was validated successfully, false - model data validation was failed.	 
	 */
	public function validateRules(array $rules)
	{
		$r = true;
		
		foreach ($rules as $field_name => $rule)
		{
			switch($rule['type'])
			{
				case 'required':
					if ($this->{$field_name} === '')
						$r = false;
				break;
			}
		}
		
		return $r;
	}
	
	/**
	 *  @brief This method is invoked before saving a record (after validation, if any).
	 *  
	 *  @return boolean whether the saving should be executed	 
	 */
	public function beforeSave()
	{
		if (!$this->create_time)
			$this->create_time = time();
		
		$this->update_time = time();
		
		$this->user_ip = $_SERVER['REMOTE_ADDR'];
		
		return true;
	}	
	
	/**
	 *  @brief This method is invoked before validation starts.
	 *  
	 *  @return boolean whether validation should be executed.
     * 	If false is returned, the validation will stop and the model is considered invalid.
	 *  
	 *  @details Details
	 */
	public function beforeValidate()
	{
		$rules = $this->getRules();
		$r = $this->validateRules($rules);
		
		return $r;
	}
	
	/**
	 *  @brief Saves the current record
	 *  
	 *  @param $runValidation boolean $runValidation whether to perform validation before saving the record.
	 *  @return boolean whether the saving succeeds
	 */
	public function save($runValidation = true)
	{	
		if (!$runValidation || $this->beforeValidate())
			if ($this->beforeSave()) 
			{				
				if ($this->id) 				
					$this->db->update($this->getTableName(), $this, array('id' => $this->id));
				else 
					$this->db->insert($this->getTableName(), $this);				
				
				return true;
			}
		
		return false;
	}
}