<?php

defined('BASEPATH') OR exit('No direct script access allowed');

class Migration_Assess_results_table extends CI_Migration
{

	public function up()
	{
		$this->dbforge->add_field(array(
			'id' => array(
				'type' => 'INT',
				'constraint' => 11,
				'unsigned' => TRUE,
				'auto_increment' => TRUE
			),
			'row_data' => array(
				'type' => 'TEXT'
			)
		));
		$this->dbforge->add_key('id',TRUE);
		$this->dbforge->create_table('assess_results');
	}

	public function down()
	{
		$this->dbforge->drop_table('assess_results');
	}

}