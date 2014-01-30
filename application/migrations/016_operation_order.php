<?php

defined('BASEPATH') OR exit('No direct script access allowed');

class Migration_Operation_order extends CI_Migration
{
	public function up()
	{
            if(!$this->db->field_exists('operation_order','operations')){
		$this->dbforge->add_column('operations', array(
			'operation_order' => array('type' => 'int',
                            'null'=>TRUE)
		));		
            }
	}

	public function down()
	{
            if($this->db->field_exists('operation_order','operations')){
		$this->dbforge->drop_column('operations', 'operation_order');
            }
	}

}