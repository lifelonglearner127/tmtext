<?php

/**
 *  @file base_model.php
 *  @brief Base model class. All children models should be extended from this Base_model class.
 *  It provides basement ActiveRecord logic which is easier to use than CI query builder.
 *  @author Oleg Meleshko <qu1ze34@gmail.com>
 */
 
abstract class Base_model extends CI_Model 
{
	
	private static $_models = array();
	
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
	 *  @brief Returns the static model of the specified class.
	 *  
	 *  @param string $className active record class name.
	 *  @return active record model instance
	 */
	public static function model($className = __CLASS__)
	{
		if (!isset(self::$_models[$className]))
			self::$_models[$className] = new $className();	
					
		return self::$_models[$className];
	}
	
	/**
	 *  @brief Finds all active records satisfying the specified condition.
	 *  
	 *  @return list of active records satisfying the specified condition
	 */
	public function findAll()
	{
		return $this->findAllByAttributes(array());
	}
	
	/**
	 *  @brief Finds a single active record with the specified primary key.
	 *  
	 *  @param $pk primary key value
	 *  @return the record found	 
	 */
	public function findByPk($pk)
	{
		return $this->findByAttributes(array('id' => $pk));
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
	 *  @brief Finds all active records that have the specified attribute values
	 *  
	 *  @param $attributes query attributes
	 *  @return All records found. An empty array is returned if none is found.
	 */
	public function findAllByAttributes(array $attributes)
	{
		$query = $this->db
			->where($attributes)			
			->get($this->getTableName());
			
		return $query->result();
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
	 *  @return boolean
	 */
	public function save($runValidation = true)
	{	
		if (!$runValidation || $this->beforeValidate())
			if ($this->beforeSave()) 
			{								
				$r = $this->id ? $this->db->update($this->getTableName(), $this, array('id' => $this->id)) : $this->db->insert($this->getTableName(), $this);
				return $r || $this->db->affected_rows();
			}
		
		return false;
	}
	
	/**
	 *  @brief Deletes the row corresponding to this active record.
	 *  
	 *  @param $pk primary key value
	 *  @return boolean
	 */
	public function deleteByPk($pk)
	{
		return $this->deleteAllByAttributes(array('id' => $pk));
	}	
	
	/**
	 *  @brief Deletes rows which match the specified attribute values.
	 *  
	 *  @param $attributes list of attribute values
	 *  @return boolean
	 */
	public function deleteAllByAttributes(array $attributes)
	{
		$r = $this->db->delete($this->getTableName(), $attributes);
			
		return $r || $this->db->affected_rows();
	}
	
	/**
	 *  @brief Deletes rows with the specified condition.
	 *  
	 *  @param $truncate boolean should be truncated or no, false is by default.
	 *  @return boolean	
	 */
	public function deleteAll($truncate = false)
	{				
		$r = !$truncate ? $this->db->empty_table($this->getTableName()) : $this->db->truncate($this->getTableName());
		
		return $r || $this->db->affected_rows();
	}
	
	/**
	 *  @brief Specifies which related objects should be eagerly loaded
	 *  
	 *  @param $join join array
	 *  @return DB object	
	 */
	public function with($join)
	{
		$default_type = 'inner';
		if (is_array($join))
			$this->db
				->join($join['table'], $join['on'], isset($join['type']) ? $join['type'] : $default_type);
        else
			$this->db
				->join($join, '`' . $this->getTableName() . '`.`' . $join . '_id` = `' . $join . '`.`id`', $default_type);
			
		return $this;
	}
	
	public function multipleSave($models)
	{
		
	}
}