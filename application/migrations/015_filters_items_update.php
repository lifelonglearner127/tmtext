<?php

defined('BASEPATH') OR exit('No direct script access allowed');

class Migration_Filters_items_update extends CI_Migration
{

	public function up()
	{
		$this->db->query("
			ALTER TABLE  `filters_items` CHANGE  `filters_values_id`  `filter_id` INT( 11 ) NOT NULL;
		");
	}

	public function down()
	{
		$this->db->query("
			ALTER TABLE  `filters_items` CHANGE  `filter_id`  `filters_values_id` INT( 11 ) NOT NULL;
		");
	}

}