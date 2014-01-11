<?php

defined('BASEPATH') OR exit('No direct script access allowed');

class Migration_First_dump extends CI_Migration
{

	public function up()
	{
		/*$filename = './sql/fulldump.sql';
		$dump = file_get_contents($filename);
		$dump = explode(';', $dump);
		foreach ($dump as $query)
		{
			if (!empty($query))
			{
				$this->db->query($query);
			}
		}*/
	}

	public function down()
	{
		
	}

}