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
	 *  @return affected rows count
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
				
				return $this->db->affected_rows();
			}
		
		return false;
	}
	
	/**
	 *  @brief Deletes the row corresponding to this active record.
	 *  
	 *  @param $pk primary key value
	 *  @return affected rows count	
	 */
	public function deleteByPk($pk)
	{
		return $this->deleteByAttributes(array('id' => $pk));
	}	
	
	/**
	 *  @brief Deletes rows which match the specified attribute values.
	 *  
	 *  @param $attributes list of attribute values
	 *  @return affected rows count
	 */
	public function deleteAllByAttributes(array $attributes)
	{
		$this->db->delete($this->getTableName(), $attributes);
			
		return $this->db->affected_rows();
	}
	
	/**
	 *  @brief Deletes rows with the specified condition.
	 *  
	 *  @param $truncate boolean should be truncated or no, false is by default.
	 *  @return affected rows count	
	 */
	public function deleteAll($truncate = false)
	{		
		if (!$truncate)
			$this->db->empty_table($this->getTableName());
		else
			$this->db->truncate($this->getTableName());
		
		return $this->db->affected_rows();
	}
}