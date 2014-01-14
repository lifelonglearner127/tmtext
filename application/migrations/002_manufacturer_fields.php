<?php

defined('BASEPATH') OR exit('No direct script access allowed');

class Migration_Manufacturer_fields extends CI_Migration
{

	public function up()
	{
		$fields = array('manufacturer_info' => array('type' => 'TEXT','null'=>TRUEc));
		$this->dbforge->add_column('statistics_new', $fields);
	}

	public function down()
	{
		$this->dbforge->drop_column('statistics_new', 'manufacturer_info');
	}

}