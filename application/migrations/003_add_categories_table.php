<?php

defined('BASEPATH') OR exit('No direct script access allowed');

class Migration_Add_categories_table extends CI_Migration
{

	public function up()
	{
		$this->dbforge->add_field(array(
			'id' => array(
				'type' => 'INT',
				'constraint' => 10,
				'unsigned' => TRUE,
				'auto_increment' => TRUE
			),
			'category_name' => array(
				'type' => 'VARCHAR',
				'constraint' => 250
			),
			'category_code' => array(
				'type' => 'VARCHAR',
				'constraint' => 50
			),
		));
		$this->dbforge->add_key('id',TRUE);
		$this->dbforge->create_table('product_categories');
		$this->db->query('ALTER TABLE `product_categories` ADD UNIQUE (`category_name` ,`category_code`);');
	}

	public function down()
	{
		$this->dbforge->drop_table('product_categories');
	}

}