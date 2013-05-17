<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Settings extends MY_Controller {

	function __construct()
 	{
  		parent::__construct();

		$this->data['title'] = 'Settings';

 	}

	public function index()	{

	}

	public function examples(){
		$this->load->model('settings_model');

		$settings = array();
		$settings[] = $this->settings_model->get_value($this->ion_auth->get_user_id(), 'java_cmd');
		$settings[] = $this->settings_model->get_settings($this->ion_auth->get_user_id());
		$settings[] = $this->settings_model->get_value($this->ion_auth->get_user_id(), 'tmp_attr');
		$this->settings_model->load_user_settings($this->ion_auth->get_user_id());

//		$this->settings_model->update_value($this->ion_auth->get_user_id(), 'java_cmd', 'nlg.sh {1} {1} user');
//		$this->settings_model->create($this->ion_auth->get_user_id(), 'tmp_attr2', array(1=>2, 2=>3), 'tmp_attr2');

		$settings[] = $this->settings_model->get_value(5, 'java_cmd');
//		$this->settings_model->create_system('tmtmt', array(1=>222,3=>444), 'asdaasdsa as as a');

		$settings[] = $this->settings_model->get_system_settings();

		die(var_dump($settings));
//		var_dump($this->config);

	}
}
?>