<?php

defined('BASEPATH') OR exit('No direct script access allowed');

class Migration_Filters_items extends CI_Migration
{
	public function up()
	{
		$this->db->query("
			CREATE TABLE IF NOT EXISTS `filters_items` (
			  `id` int(11) NOT NULL AUTO_INCREMENT,
			  `item_key` int(11) NOT NULL,
			  `filter_id` int(11) NOT NULL,
			  `combination_id` int(11) NOT NULL,
			  PRIMARY KEY (`id`),
			  KEY `filter_id` (`filter_id`,`combination_id`)
			) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;
		");
	}

	public function down()
	{
		$this->dbforge->drop_table('filters_items');
	}

}