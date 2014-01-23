<?php

defined('BASEPATH') OR exit('No direct script access allowed');

class Migration_Workflow_table extends CI_Migration
{
	public function up(){
            $sql = "create table if not exists processes(
                id int not null auto_increment
                ,process_name varchar(50) not null
                ,process_step int not null default 0
                ,week_day int not null default 0
                ,process_started timestamp
                ,process_ended timestamp
                ,primary key (id)
                ,unique key (process_name)
                )engine=InnoDB";
            $this->db->query($sql);
            $sql = "create table if not exists operations(
                id int not null auto_increment
                ,func_title varchar(50)
                ,func_url varchar(50)
                ,primary key(id)
                )engine=InnoDB";
            $this->db->query($sql);
            $sql = "create table if not exists process_steps(
                id int not null auto_increment
                ,process_id int not null
                ,operation_id int
                ,function_param int
                ,step_number int
                ,primary key (id)
                ,foreign key (process_id) references processes(id) 
                on update cascade on delete cascade
                ,foreign key (operation_id) references operations(id) 
                on update cascade on delete cascade
                )engine=InnoDB";
            $this->db->query($sql);
	}

	public function down(){
            $sql = "drop table if exists process_steps";
            $this->db->query($sql);
            $sql = "drop table if exists processes";
            $this->db->query($sql);
            $sql = "drop table if exists operations";
            $this->db->query($sql);
	}

}