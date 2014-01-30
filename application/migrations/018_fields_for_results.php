<?php

defined('BASEPATH') OR exit('No direct script access allowed');

class Migration_Fields_for_results extends CI_Migration
{

	public function up()
	{
		$field = array('combination' => array('type' => 'INT','constraint' => 11,'unsigned' => TRUE,'default'=>0));
		$this->dbforge->add_column('assess_results', $field);
		$this->dbforge->modify_column('assess_results', array('id' => array(
				'type' => 'INT',
				'constraint' => 11,
				'unsigned' => TRUE,
				'auto_increment' => FALSE
			)));
	       $this->db->query('ALTER TABLE `assess_results` DROP PRIMARY KEY');
	       $this->db->query('ALTER TABLE `assess_results` ADD PRIMARY KEY (`id` ,`combination`);');
	       $this->db->truncate('assess_results');
	}

	public function down()
	{
		$this->db->query('ALTER TABLE `assess_results` DROP PRIMARY KEY');
		$this->dbforge->drop_column('assess_results', 'combination');
		$this->db->query('ALTER TABLE `assess_results` ADD PRIMARY KEY (`id`);');
		$this->dbforge->modify_column('assess_results', array('id' => array(
				'type' => 'INT',
				'constraint' => 11,
				'unsigned' => TRUE,
				'auto_increment' => TRUE
			)));
	}

}