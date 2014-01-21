<?php

defined('BASEPATH') OR exit('No direct script access allowed');

class Migration_Secondary_batches extends CI_Migration
{
	public function up()
	{
		$this->dbforge->add_field(array(
			'primary_batch_id' => array(
				'type' => 'INT',
				'constraint' => 11,
				'unsigned' => TRUE
			),
			'secondary_batch_id' => array(
				'type' => 'INT',
				'constraint' => 11,
				'unsigned' => TRUE
			),
			'secondary_customer_id' => array(
				'type' => 'INT',
				'constraint' => 11,
				'unsigned' => TRUE
			)
		));
		$this->dbforge->add_key('primary_batch_id',TRUE);
		$this->dbforge->add_key('secondary_customer_id');
		$this->dbforge->create_table('secondary_batches');
	}

	public function down()
	{
		$this->dbforge->drop_table('secondary_batches');
	}

}