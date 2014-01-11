<?php if (!defined('BASEPATH')) exit('No direct script access allowed');
/**
* Name:  MY_Controller
*
* Author:  Ben Edmunds
* Created:  7.21.2009
*
* Description:  Class to extend the CodeIgniter Controller Class.  All controllers should extend this class.
*
*/

class MY_Controller extends CI_Controller {

    protected $data = Array();
    protected $controller_name;
    protected $action_name;
    protected $previous_controller_name;
    protected $previous_action_name;
    protected $save_previous_url = false;
    protected $page_title;
    protected $system_settings;
    protected $user_settings;
    protected $settings;

    public function __construct() {
        parent::__construct();
	$this->load->library('migration');
	if (!$this->migration->current())
	{
		show_error($this->migration->error_string());
	}
        $this->load->library(array('session','ion_auth'));

        $this->load->helper(array('HTML','form','url'));

        //save the previous controller and action name from session
        $this->previous_controller_name = $this->session->flashdata('previous_controller_name');
        $this->previous_action_name     = $this->session->flashdata('previous_action_name');

        //set the current controller and action name
        $this->controller_name = $this->router->fetch_directory() . $this->router->fetch_class();
        $this->action_name     = $this->router->fetch_method();

        $this->data['content'] = '';
        $this->data['css']     = '';

        $this->load->model('settings_model');
		$this->system_settings = $this->settings_model->get_system_settings();
		$this->data['settings'] = $this->system_settings;

		$this->settings	= $this->system_settings;

		if ($this->ion_auth->get_user_id()) {
			$this->user_settings = $this->settings_model->get_settings($this->ion_auth->get_user_id());

			// Replace settings with user settings
			foreach ($this->user_settings as $key => $value) {
				$this->settings[$key] = $this->user_settings[$key];
			}

		}
    }

    protected function render($template='main') {
        //save the controller and action names in session
        if ($this->save_previous_url) {
        	$this->session->set_flashdata('previous_controller_name', $this->previous_controller_name);
        	$this->session->set_flashdata('previous_action_name', $this->previous_action_name);
        }
        else {
        	$this->session->set_flashdata('previous_controller_name', $this->controller_name);
        	$this->session->set_flashdata('previous_action_name', $this->action_name);
        }

        $view_path = $this->controller_name . '/' . $this->action_name . '.php'; //set the path off the view
        if (file_exists(APPPATH . 'views/' . $view_path)) {
            $this->data['content'] .= $this->load->view($view_path, $this->data, true);  //load the view
        }
        if($this->input->get("ajax", false)==true){
            $this->load->view("layouts/ajax.tpl.php", $this->data);  //load the template
        }else{
            $this->load->view("layouts/$template.tpl.php", $this->data);  //load the template
        }
    }

    protected function add_title() {
    	$this->load->model('page_model');

    	//the default page title will be whats set in the controller
    	//but if there is an entry in the db override the controller's title with the title from the db
    	$page_title = $this->page_model->get_title($this->controller_name,$this->action_name);
    	if ($page_title) {
    		$this->data['title'] = $page_title;
    	}
    }

    protected function save_url() {
    	$this->save_previous_url = true;
    }
}