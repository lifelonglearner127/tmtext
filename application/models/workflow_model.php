<?php

/**
 *  @file workflow_model.php
 *  @brief Workflow model class. 
 *  It access to workflow process control table
 *  @author Fjodor Adamenko
 */
 
class Workflow_model extends CI_model {
    /**
	 *  @return This method should return database table name.	 	
	 */
	public function getRules()
	{
		return array(
			'process_name' => array('type' => 'required')			
		);
	}
	
	/**
	 *  @brief This method is used for setting up model validation rules.
	 *  
	 *  @return array of validation rules	 
	 */
	public function getTableName()
	{
		return 'processes';
	}		
	
	/**
	 *  @brief This method returns tasks.
	 *  
	 *  @return process name and task	 
	 */
        public function getCurrentTask(){
            $sql = "select p.process_name
                , COALESCE(f.function_url,0) as function_url
                , COALESCE(ps.function_param,'none') as function_param
                from processes as p
                left join process_steps as ps 
                on p.id = ps.process_id and ps.step_number=(p.process_step+1)
                inner join functions as f on f.id=ps.function_id
                where p.week_day = weekday(current_timestamp)
                and (p.process_ended is null or dayofyear(p.process_ended)<dayofyear(current_timestamp))";
            $query = $this->db->query($sql);
            if($query->num_rows==0){
                return false;
            }
            return $query->first_row();
        }
        public function addOperation($title,$url){
            $this->db->select('id');
            $this->db->from('operations');
            $this->db->where('func_url', $url);
            $query = $this->db->get();
            if($query->num_rows>0){
                return FALSE;
            }
            $data = array(
                'func_title'=>$title,
                'func_url'=>$url
            );
            $this->db->insert('operations',$data);
            return $this->db->insert_id();
        }
        public function addProcess($title,$day){
            $day = intval($day);
            if($day>6 || $day<0){
                return FALSE;
            }
            $data = array(
                'process_name'=>$title,
                'week_day'=>$day
            );
            $this->db->insert('process',$data);
            return $this->db->insert_id();
        }
        public function nextStep(){
            $sql = "select p.id, p.process_name, p.process_step, p.process_started
                from processes as p
                where p.week_day = weekday(current_timestamp)";
            $query = $this->db->query($sql);
            if($query->num_rows==0){
                return false;
            }
            $row = $query->firs_row();
            $data = array(
                'process_step'=>$row->process_step+1
            );
            if($row->process_started===null){
                $pst = ', process_started=current_timestamp';
            }
            $sql = 'UPDATE processes SET process_step='.($row->process_step+1)
                    .', process_ended=current_timestamp'
                    .$pst
                    .' WHERE id='.$row->id;
            $this->db->query($sql);
        }
        public function lastStep(){
            $sql = "select p.id, p.process_name, p.process_step
                from processes as p
                where p.week_day = weekday(current_timestamp)";
            $query = $this->db->query($sql);
            if($query->num_rows==0){
                return false;
            }
            $row = $query->firs_row();
            $sql = "UPDATE processes SET process_step=0, process_ended=current_timestamp
                WHERE id=".$row->id;
            $this->db->query($sql);
        }
        private function checkProcess($proc_id){
            $this->db->select('id');
            $this->db->from('process');
            $this->db->where('id',$proc_id);
            $query = $this->db->get();
            return $query->num_rows===1;
        }
        private function checkOperation($op_id){
            $this->db->select('id');
            $this->db->from('process');
            $this->db->where('id',$op_id);
            $query = $this->db->get();
            return $query->num_rows===1;
        }
        public function addSteps($process,$oper,$param){
            if($this->checkProcess($process)||$this->checkOperation($oper)){
                return FALSE;
            }
            $this->db->select('Max(step_number) as step');
            $this->db->from('process_steps');
            $this->db->where('process_id',$process);
            $this->db->group_by('step_number');
            $query = $this->db->get();
            $step=0;
            if($query->num_rows==1){
                $row = $query->first_row();
                $step=$row->step+1;
            }
            $data = array(
                'process_id'=>$process,
                'operation_id'=>$oper,
                'function_param'=>$param,
                'step_number'=>$step
            );
            $this->db->insert('process_steps',$data);
            return $this->db->insert_id();
        }
        
}