<?php

defined('BASEPATH') OR exit('No direct script access allowed');

class Migration_Filters_values extends CI_Migration
{
	public function up()
	{
		$this->db->query("
			CREATE TABLE IF NOT EXISTS `filters_values` (
			  `id` int(11) NOT NULL AUTO_INCREMENT,
			  `filter_id` int(11) NOT NULL,
			  `value` varchar(255) NOT NULL,
			  `combination_id` int(11) NOT NULL,
			  `icon` tinyint(4) NULL,
			  PRIMARY KEY (`id`),
			  KEY `combination_id` (`combination_id`)
			) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;
		");
	}

	public function down()
	{
		$this->dbforge->drop_table('filters_values');
	}

}