<?php

defined('BASEPATH') OR exit('No direct script access allowed');

class Migration_Filters_combos extends CI_Migration
{
	public function up()
	{
		
		
		$this->db->query("
			CREATE TABLE IF NOT EXISTS `filters_combos` (
			  `id` int(11) NOT NULL AUTO_INCREMENT,
			  `title` varchar(255) NOT NULL,
			  `filters_ids` varchar(255) NOT NULL,
			  PRIMARY KEY (`id`)
			) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=13 ;
		");
	}

	public function down()
	{
		$this->dbforge->drop_table('filters_combos');
		
		
	}

}