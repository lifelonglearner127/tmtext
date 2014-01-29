<?php

if (!defined('BASEPATH'))
    exit('No direct script access allowed');

class Workflow extends MY_Controller {

    function __construct() {
        parent::__construct();
        if (!$this->ion_auth->logged_in()) {
            //redirect them to the login page
            redirect('auth/login', 'refresh');
        }
        $this->load->model('workflow_model');
        $this->load->model('operations_model');
        $this->load->model('process_model');
    }

    public function index() {
        
    }
    public function get_processes(){
        $res = $this->process_model->findAll();
        echo json_encode($res);
    }
    public function get_operations(){
        $res = $this->operations_model->findAll();
        echo json_encode((array)$res);
    }

    public function add_operation() {
        $title = $this->input->post('op_name');
        $url = $this->input->post('op_url');
        $res = $this->operations_model->add($title, $url);
        if ($res) {
            echo $res;
        }
    }

    public function update_operation() {
        
    }

    public function delete_operation() {
        $id = $this->input->post('id');
        $this->operations_model->deleteAllByAttributes(array('id' => $id));
    }

    public function add_prc() {
        $title = $this->input->post('process_name');
        $day =  $this->input->post('day');
        $oper =  $this->input->post('ops');
        $batches=  $this->input->post('batches');
        $url_import_file = $this->input->post("url_import_file");
        $param = '';
        $id = $this->process_model->add($title, $day);
        $this->workflow_model->addSteps($id, $oper, $param);
        $oper_list = $this->operations_model->getall();
        foreach($oper as $op){
            foreach($oper_list as $key=>$so){
                if($so['id']===$op){
                    $ar = array();
                    if($so['param_type']==='batch'){
                        $ar = $batches;
                    }
                    elseif($so['param_type']==='file'){
                        $ar = $url_import_file;
                    }
                    elseif($so['param_type']==='none'){
                        $oper_list[$key]['step']=$value;
                    }
                    foreach($ar as $value){
                        $oper_list[$key]['step'][]=$value;
                    }
                    break;
                }
            }
        }
        foreach ($oper_list as $op){
            if(isset($op['step'])){
                if(is_array($op['step'])){
                    foreach ($op['step'] as $value){
                        $this->workflow_model->addSteps($id,$op['id'],$value);
                    }
                }
                else{
                    $this->workflow_model->addSteps($id,$op['id']);
                }
            }
        }
        echo $id;
    }

    public function update_prc() {
        
    }

    public function delete_prc() {
        $id = $this->input->post('id');
        $this->process_model->deleteAllByAttributes(array('id' => $id));
    }

}

?>
