<?php

defined('BASEPATH') OR exit('No direct script access allowed');

class Migration_Batches_combinations extends CI_Migration
{
	public function up()
	{
		$this->db->query("
			CREATE TABLE IF NOT EXISTS `batches_combinations` (
			  `id` int(11) NOT NULL AUTO_INCREMENT,
			  `batches_combination` varchar(255) NOT NULL,
			  `category_id` int(11) NULL,
			  PRIMARY KEY (`id`)
			) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;
		");
	}

	public function down()
	{
		$this->dbforge->drop_table('batches_combinations');
	}

}