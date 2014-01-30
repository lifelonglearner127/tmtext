<?php

defined('BASEPATH') OR exit('No direct script access allowed');

class Migration_Combination_status extends CI_Migration
{
	public function up()
	{
		if(!$this->db->field_exists('status','batches_combinations'))
		{
			$field = array('status' => array('type' => 'TINYINT','constraint' => 4,'unsigned' => TRUE,'default'=>0));
			$this->dbforge->add_column('batches_combinations', $field);
		}
	}

	public function down()
	{
		if($this->db->field_exists('status','batches_combinations'))
		{
			$this->dbforge->drop_column('batches_combinations', 'status');
		}	
	}
}