<?php

defined('BASEPATH') OR exit('No direct script access allowed');

class Migration_Statistics_trendline_dates_table extends CI_Migration
{

	public function up()
	{
            $this->db->query("
                    CREATE TABLE IF NOT EXISTS `statistics_trendline_dates` (
                      `id` int(11) NOT NULL AUTO_INCREMENT,
                      `batch_id` int(11) NOT NULL,
                      `batch_compare_id` int(11) NOT NULL,
                      `graph_build` varchar(255) NOT NULL,
                      `trendline_dates_items` varchar(3000) NOT NULL,
                      PRIMARY KEY (`id`)
                    );
            ");
	}

	public function down()
	{
		$this->dbforge->drop_table('statistics_trendline_dates');
		
		
	}

}