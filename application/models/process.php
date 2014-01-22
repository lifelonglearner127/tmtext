<?php

require_once(APPPATH . 'models/base_model.php');

class Process_model extends Base_model 
{	
    public function getRules()
	{
		return array(
			'process_model' => array('type' => 'required'),			
		);
	}
	
	public function getTableName()
	{
		return 'processes';
	}
}

?>