<?php

defined('BASEPATH') OR exit('No direct script access allowed');

class Migration_Operation_order extends CI_Migration
{
	public function up()
	{
		$this->dbforge->add_column('operations', array(
			'operation_order' => array('type' => 'int',
                            'null'=>TRUE)
		));		
	}

	public function down()
	{
		$this->dbforge->drop_column('operations', 'operation_order');
	}

}