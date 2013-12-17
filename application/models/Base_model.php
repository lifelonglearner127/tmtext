<?php

class Base_model extends CI_Model 
{
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
}