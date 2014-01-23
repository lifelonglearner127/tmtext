<?php

defined('BASEPATH') OR exit('No direct script access allowed');

class Migration_Batches_combinations_title extends CI_Migration
{
	public function up()
	{
		$this->dbforge->add_column('batches_combinations', array(
			'title' => array('type' => 'varchar(255)')
		));		
	}

	public function down()
	{
		$this->dbforge->drop_column('batches_combinations', 'title');
	}

}