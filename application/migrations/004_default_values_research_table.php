<?php

defined('BASEPATH') OR exit('No direct script access allowed');

class Migration_Default_values_research_table extends CI_Migration
{

	public function up()
	{
		$field = array('category_id' => array('type' => 'INT','constraint' => 11,'null'=>TRUE,'default'=>'0'));
		$this->dbforge->add_column('research_data', $field);
		$fields = array(
		    'product_name' => array(
			'type' =>'VARCHAR',
			'constraint' => '255',
			'null' => TRUE,
			'default' => ''
		    ),
		    'keyword1' => array(
			'type' =>'VARCHAR',
			'constraint' => '255',
			'null' => TRUE,
			'default' => ''
		    ),
		    'keyword2' => array(
			'type' =>'VARCHAR',
			'constraint' => '255',
			'null' => TRUE,
			'default' => ''
		    ),
		    'keyword3' => array(
			'type' =>'VARCHAR',
			'constraint' => '255',
			'null' => TRUE,
			'default' => ''
		    ),
		    'meta_name' => array(
			'type' =>'VARCHAR',
			'constraint' => '255',
			'null' => TRUE,
			'default' => ''
		    ),
		    'meta_description' => array(
			'type' =>'TEXT',
			'null' => TRUE,
			'default' => ''
		    ),
		    'meta_keywords' => array(
			'type' =>'VARCHAR',
			'constraint' => '255',
			'null' => TRUE,
			'default' => ''
		    ),
		    'short_description' => array(
			'type' =>'TEXT',
			'null' => TRUE,
			'default' => ''
		    ),
		    'short_description_wc' => array(
			'type' =>'INT',
			'constraint' => '11',
			'null' => TRUE,
			'default' => '0'
		    ),
		    'long_description' => array(
			'type' =>'TEXT',
			'null' => TRUE,
			'default' => ''
		    ),
		    'long_description_wc' => array(
			'type' =>'INT',
			'constraint' => '11',
			'null' => TRUE,
			'default' => '0'
		    ),
		    'include_in_assess_report' => array(
			'type' =>'TINYINT',
			'constraint' => '4',
			'null' => TRUE,
		    )
		);
		$this->dbforge->modify_column('research_data', $fields);
	}

	public function down()
	{
		$this->dbforge->drop_column('research_data', 'category_id');
		$fields = array(
		    'product_name' => array(
			'type' =>'VARCHAR',
			'constraint' => '255',
			'null' => FALSE,
		    ),
		    'keyword1' => array(
			'type' =>'VARCHAR',
			'constraint' => '255',
			'null' => FALSE,
		    ),
		    'keyword2' => array(
			'type' =>'VARCHAR',
			'constraint' => '255',
			'null' => FALSE,
		    ),
		    'keyword3' => array(
			'type' =>'VARCHAR',
			'constraint' => '255',
			'null' => FALSE,
		    ),
		    'meta_name' => array(
			'type' =>'VARCHAR',
			'constraint' => '255',
			'null' => FALSE,
		    ),
		    'meta_description' => array(
			'type' =>'TEXT',
			'null' => FALSE,
		    ),
		    'meta_keywords' => array(
			'type' =>'VARCHAR',
			'constraint' => '255',
			'null' => FALSE,
		    ),
		    'short_description' => array(
			'type' =>'TEXT',
			'null' => FALSE,
		    ),
		    'short_description_wc' => array(
			'type' =>'INT',
			'constraint' => '11',
			'null' => FALSE,
		    ),
		    'long_description' => array(
			'type' =>'TEXT',
			'null' => FALSE,
		    ),
		    'long_description_wc' => array(
			'type' =>'INT',
			'constraint' => '11',
			'null' => FALSE,
		    ),
		    'include_in_assess_report' => array(
			'type' =>'TINYINT',
			'constraint' => '4',
			'null' => FALSE,
		    )
		);
		$this->dbforge->modify_column('research_data', $fields);
	}

}