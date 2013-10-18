<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Job_Board extends MY_Controller {

    function __construct()
    {
        parent::__construct();

        $this->load->library('form_validation');
        $this->load->library('helpers');
        $this->data['title'] = 'Research & Edit';

        if (!$this->ion_auth->logged_in())
        {
            //redirect them to the login page
            redirect('auth/login', 'refresh');
        }
    }

    public function index()
    {
        $this->render();
    }


    public function individual_jobs(){
        $this->render();
    }

    public function my_jobs(){
        $this->render();
    }
}