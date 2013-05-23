<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Measure extends MY_Controller {

    function __construct()
    {
        parent::__construct();

        $this->load->library('form_validation');
        $this->load->library('helpers');
        $this->data['title'] = 'Measure';

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

    public function analyzestring() {
        $clean_t = $this->input->post('clean_t');
        $output = $this->helpers->measure_analyzer_start($clean_t);
        // $output = $clean_t;
        $this->output->set_content_type('application/json')->set_output(json_encode($output));
    }
}