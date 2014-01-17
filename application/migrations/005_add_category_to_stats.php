<?php

defined('BASEPATH') OR exit('No direct script access allowed');

class Migration_Add_category_to_stats extends CI_Migration
{

	public function up()
	{
		$field = array('category_id' => array('type' => 'INT','constraint' => 11,'null'=>TRUE,'default'=>'0'));
		$this->dbforge->add_column('statistics_new', $field);
	}

	public function down()
	{
		$this->dbforge->drop_column('statistics_new', 'category_id');
	}

}