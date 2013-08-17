<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Admin_Customer extends MY_Controller {

	function __construct()
 	{
  		parent::__construct();

  		$this->load->library('form_validation');
		$this->data['title'] = 'Admin Customer Setting';

 	}

	public function index()
	{                       
		$this->data['message'] = $this->session->flashdata('message');
		$this->data['user_settings'] = $this->user_settings;
                $this->data['customers']= $this->getCustomersList();
                $this->render();
	}
    function getCustomersList(){
        
       $this->load->model('customers_model');
        $this->load->model('users_to_customers_model');
//        $admin = $this->ion_auth->is_admin($this->ion_auth->get_user_id());
//        $customers_init_list = $this->users_to_customers_model->getByUserId($this->ion_auth->get_user_id());
//        if (count($customers_init_list) == 0 && $admin) {
//            $customers_init_list = $this->customers_model->getAll();
//        }
        $customers_init_list = $this->customers_model->getAll();
        if (count($customers_init_list) > 0) {
            
            foreach ($customers_init_list as $key => $value) {
                $output[] = array('text' => '',
                    'value' => strtolower($value->name),
                    'image' => base_url() . 'img/' . $value->image_url,
                     'url' =>$value->url
                );
            }
        } else {
            $output[] = array('text' => 'No Customers',
                'value' => 'No Customers',
                'image' => ''
            );
        }
        return $output;
    }
    public function customer_list()
    {
        $this->render();
    }
   
   public function save() {
		$this->form_validation->set_rules('user_settings[customer_name]', 'Customer name', 'xss_clean');
		$this->form_validation->set_rules('user_settings[csv_directories]', 'CSV Directories', 'required|xss_clean');
		$this->form_validation->set_rules('user_settings[title_length]', 'Default Title', 'required|integer|xss_clean');
		$this->form_validation->set_rules('user_settings[description_length]', 'Description Length', 'required|integer|xss_clean');

		if ($this->form_validation->run() === true) {
			$settings = $this->input->post('user_settings');

			$settings['use_files'] = (isset($settings['use_files'])?true:false);
			$settings['use_database'] = (isset($settings['use_database'])?true:false);

			$this->settings_model->db->trans_start();
			foreach ($settings as $key=>$value) {
				if (!$this->settings_model->update_value($this->ion_auth->get_user_id(), $key,$value)) {
					$this->settings_model->create($this->ion_auth->get_user_id(), $key, $value, $key);
				}
			}
			$this->settings_model->db->trans_complete();
		} else {
			$this->session->set_flashdata('message', (validation_errors()) ? validation_errors() : $this->session->flashdata('message'));

		}
		redirect('admin_customer/index?ajax=true');
	}

    public function upload_csv()
    {
        $this->load->library('UploadHandler');

        $this->output->set_content_type('application/json');
        $this->uploadhandler->upload(array(
            'script_url' => site_url('admin_customer/upload_csv'),
            'upload_dir' => $this->config->item('csv_upload_dir'),
            'param_name' => 'files',
            'delete_type' => 'POST',
            'accept_file_types' => '/.+\.(jpg|gif|png)$/i',
        ));
    }

    public function upload_img()
    {
        $this->load->library('UploadHandler');
        $this->output->set_content_type('application/json');

        $this->uploadhandler->upload(array(
            'script_url' => site_url('admin_customer/upload_img'),
            'upload_dir' => 'webroot/img/',
            'param_name' => 'files',
            'delete_type' => 'POST',
            'accept_file_types' => '/.+\.(jpg|gif|png)$/i',
        ));
    }

    public function add_customer()
    {
        $this->load->model('customers_model');
        $response['message'] = '';
        if($this->input->post('customer_name') != ''){
             
            if($this->customers_model->getByName($this->input->post('customer_name'))!=''){
                $this->customers_model->update($this->input->post('customer_name'), $this->input->post('customer_url'), $this->input->post('logo'));
                $response['message'] =  'Customer was updated successfully';
                
            }else{
            $this->customers_model->insert($this->input->post('customer_name'), $this->input->post('customer_url'), $this->input->post('logo'));
            $response['message'] =  'Customer was added successfully';
            }
        }
        $this->output->set_content_type('application/json')->set_output(json_encode($response));
    }
}