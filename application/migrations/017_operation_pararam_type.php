<?php

defined('BASEPATH') OR exit('No direct script access allowed');

class Migration_Operation_pararam_type extends CI_Migration
{
	public function up()
	{
            if(!$this->db->field_exists('param_type','operations')){
		$this->dbforge->add_column('operations', array(
			'param_type' => array('type' => 'ENUM (\'batch\',\'file\',\'none\')',
                            'null'=>TRUE)
		));		
            }
	}

	public function down()
	{
            if($this->db->field_exists('param_type','operations')){
		$this->dbforge->drop_column('operations', 'param_type');
            }
	}

}