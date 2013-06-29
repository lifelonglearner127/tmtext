<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class System extends MY_Controller {



	function __construct()
 	{
  		parent::__construct();

		$this->data['title'] = 'System Settings';
		$this->data['checked_controllers'] = array( 'measure', 'research', 'editor', 'customer');
		$this->data['admin_controllers'] = array('system', 'admin_customer', 'admin_editor', 'admin_tag_editor');


		$this->load->library('form_validation');

 	}

	public function index()
	{
		$this->data['message'] = $this->session->flashdata('message');

		$this->render();
	}

	public function testattributesext() {
		$s = $this->input->post('desc');
		$descCmd = str_replace($this->config->item('cmd_mask'), $s, $this->system_settings['python_cmd']);
		echo "SEARCH: ".$s."<br />";
		echo "MASK: ".$this->config->item('cmd_mask')."<br />";
		echo "CMD: ".$this->system_settings['python_cmd']."<br />";
		echo "EXEC RES: ".shell_exec($descCmd)."<br />";
		if($result = shell_exec($descCmd)) {
			echo "EXEC RES:"."<br />";
			echo var_dump($result);
			if (preg_match_all('/.*ELECTR_DESCRIPTION:\s*(.*)\s*-{5,}/', $result, $matches)) {
				echo "PREG MATCH RES:"."<br />";
				echo var_dump($matches);
			}
			die('NO MATCHES');
		}
		die('EXEC LAUNCH FAILED!');
	}

	public function deleteproductsvotedpair() {
		$this->load->model('imported_data_parsed_model');
		$id = $this->input->post('id');
		$res = $this->imported_data_parsed_model->deleteProductsVotedPair($id);
		$this->output->set_content_type('application/json')->set_output(json_encode($res));
	}

	public function renewcomparerightsidefromdropdown() {
		$customer_r_selected = $this->input->post('customer_r_selected');
		$customer_l = $this->input->post('customer_l');
		$id_l = $this->input->post('id_l');
		$id_r = $this->input->post('id_r');
		$this->load->model('imported_data_parsed_model');
		$get_random_r = $this->imported_data_parsed_model->getRandomRightCompareProductDrop($customer_r_selected, $customer_l, $id_l, $id_r);
		$data = array(
			'get_random_r' => $get_random_r
		);
		$this->load->view('system/renewcomparerightside', $data);
	}

	public function renewcomparerightside() {
		$customer_l = $this->input->post('customer_l');
		$id_l = $this->input->post('id_l');
		$this->load->model('imported_data_parsed_model');
		$get_random_r = $this->imported_data_parsed_model->getRandomRightCompareProduct($customer_l, $id_l);
		$data = array(
			'get_random_r' => $get_random_r
		);
		$this->load->view('system/renewcomparerightside', $data);
	}

	public function renewallcomparesides() {
		$this->load->model('imported_data_parsed_model');

		$get_random_l = $this->imported_data_parsed_model->getRandomLeftCompareProduct();
		$get_random_r = $this->imported_data_parsed_model->getRandomRightCompareProduct($get_random_l['customer'], $get_random_l['id']);

		$data = array(
			'get_random_l' => $get_random_l,
			'get_random_r' => $get_random_r
		);
		$this->load->view('system/renewallcomparesides', $data);
	}

	public function getmatchnowinterface() {
		$this->load->model('imported_data_parsed_model');
		
		$get_random_l = $this->imported_data_parsed_model->getRandomLeftCompareProduct();
		// $get_random_r = $this->imported_data_parsed_model->getRandomRightCompareProduct($get_random_l['customer'], $get_random_l['id']);
		$get_random_r = $this->imported_data_parsed_model->getRandomRightCompareProduct($get_random_l['customer'], $get_random_l['id'], $get_random_l['product_name']);

		$data = array(
			'get_random_l' => $get_random_l,
			'get_random_r' => $get_random_r
		);
		$this->load->view('system/getmatchnowinterface', $data);
	}

	public function getproductscomparevoted() {
		$page = $this->input->post('page');
		$items_per_page = 2;
		$this->load->model('imported_data_parsed_model');
        $data = array(
            'v_producs' => $this->imported_data_parsed_model->getProductsCompareVoted($page, $items_per_page),
            'v_producs_count' => $this->imported_data_parsed_model->getProductsCompareVotedTotalCount(),
            'page' => $page,
            'items_per_page' => $items_per_page
        );
        $this->load->view('system/getproductscomparevoted', $data);
	}

	public function votecompareproducts() {
		$this->load->model('imported_data_parsed_model');
		$ids = $this->input->post('ids');
		$dec = $this->input->post('dec');
		$output = $this->imported_data_parsed_model->voteCompareProducts($ids, $dec);
		$this->output->set_content_type('application/json')->set_output(json_encode($output));
	}

	public function getcompareproducts() {
		$this->load->model('imported_data_parsed_model');
		$ids = $this->input->post('ids');
        $data = array(
            'c_product' => $this->imported_data_parsed_model->getProductsByIdStack($ids)
        );
        $this->load->view('system/getcompareproducts', $data);
	}

	public function system_productsmatch() {
		$this->render();
	}

	public function system_compare() {
		$this->load->model('imported_data_parsed_model');
		$this->data['all_products'] = $this->imported_data_parsed_model->getAllProducts();
		$this->render();	
	}

	public function system_accounts()
	{
		$this->render();
	}

	public function system_roles()
	{

        $this->load->model('user_groups_model');
        $user_groups = $this->user_groups_model->getAll();
        $this->data['user_groups'] = $user_groups;
		$checked = array();
		foreach ($user_groups as $user_group) {
			$rules = unserialize($user_group->auth_rules);
			foreach ($this->data['checked_controllers'] as $checked_controller) {
				if($rules[$checked_controller]['index']){
					$checked[$user_group->id][$checked_controller] = true;
				}
			}
            $checked[$user_group->id]['default_controller'] = $user_group->default_controller;
		}
		$this->data['checked'] = $checked;
		$this->render();
	}

	public function system_users()
	{
		$this->load->model('user_groups_model');
		$this->load->model('customers_model');
		$this->data['user_groups'] = $this->user_groups_model->getAll();
		$customers = $this->customers_model->getAll();
		$customersArray = array();
		$customersArray['all'] = 'All';
		foreach ($customers as $customer) {
			if(!in_array($customer->name, $customersArray)){
				$customersArray[$customer->id] = $customer->name;
			}
		}
		asort($customersArray);
		$this->data['customers'] = $customersArray;
		$this->data['message'] = array();
		$this->render();
	}

	public function save()
	{
		$response = array();
		$this->form_validation->set_rules('settings[site_name]', 'Site name', 'required|xss_clean');
		$this->form_validation->set_rules('settings[company_name]', 'Company name', 'required|xss_clean');
		$this->form_validation->set_rules('settings[csv_directories]', 'CSV Directories', 'required|xss_clean');
		$this->form_validation->set_rules('settings[tag_rules_dir]', 'tagRules', 'required|xss_clean'); // Shulgin I.L.
		$this->form_validation->set_rules('settings[python_cmd]', 'Python script', 'required|xss_clean');
		$this->form_validation->set_rules('settings[java_cmd]', 'Java tools', 'required|xss_clean');
		$this->form_validation->set_rules('settings[python_input]', 'Python input', 'required|xss_clean');
		$this->form_validation->set_rules('settings[java_input]', 'Java input', 'required|xss_clean');

		if ($this->form_validation->run() === true) {
			$settings = $this->input->post('settings');
			// Process checkboxes
			$settings['use_files'] = (isset($settings['use_files'])?true:false);
			$settings['use_database'] = (isset($settings['use_database'])?true:false);

			$settings['java_generator'] = (isset($settings['java_generator'])?true:false);
			$settings['python_generator'] = (isset($settings['python_generator'])?true:false);

			$this->settings_model->db->trans_start();
			foreach ($settings as $key=>$value) {
				if (!$this->settings_model->update_system_value($key,$value)) {
					$this->settings_model->create_system($key, $value, $key);
				}
			}
			$this->settings_model->db->trans_complete();
			$response['success'] = 1;
			$response['message'] =  'Settings vas saved successfully';
		} else {
			$response['message'] =  (validation_errors()) ? validation_errors() : '';
		}
		$this->output->set_content_type('application/json')
		        ->set_output(json_encode($response));
	}

	public function save_account_deafults()
	{
		$response = array();
		$this->form_validation->set_rules('settings[title_length]', 'Default Title', 'required|integer|xss_clean');
		$this->form_validation->set_rules('settings[description_length]', 'Description Length', 'required|integer|xss_clean');

		$response['message'] =  'ping';
		if ($this->form_validation->run() === true) {
			$settings = $this->input->post('settings');

			$this->settings_model->db->trans_start();
			foreach ($settings as $key=>$value) {
				if (!$this->settings_model->update_system_value($key,$value)) {
					$this->settings_model->create_system($key, $value, $key);
				}
			}
			$this->settings_model->db->trans_complete();
			$response['success'] = 1;
			$response['message'] =  'Settings vas saved successfully';
		} else {
			$response['message'] =  (validation_errors()) ? validation_errors() : 'Saving error';
		}
		$this->output->set_content_type('application/json')
		        ->set_output(json_encode($response));
	}

	public function csv_import() {
		$this->load->model('imported_data_model');
		$this->load->model('imported_data_parsed_model');
		$this->load->model('category_model');

		$_rows = array(); $i = 0;

		$header_replace = $this->config->item('csv_header_replace');
		// Find all unique lines in files
		foreach(explode("\n",trim($this->system_settings['csv_directories'])) as $_path) {
			if ($path = realpath($_path)) {
				$objects = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($path), RecursiveIteratorIterator::SELF_FIRST);
				foreach ($objects as $name => $object){
					if ($object->isFile()) {
						$path_parts = pathinfo($object->getFilename());
						if ( in_array($path_parts['extension'], array('csv')) ) {

							// Parse company name
							/*
							  	categoryname.csv 								([^_\-]*)
								categoryname_20130521.csv 						([^_\-]*)_(\d*)
								sitename_xxxxxx_categoryname.csv 				([^_\-]*)_([^_\-]*)_([^_\-0-9]*)
								sitename_xxxxxx_categoryname_20130521.csv 		([^_\-]*)_([^_\-]*)_([^_\-]*)_(\d*)
								sitename_categoryname.csv						([^_\-]*)_([^_\-0-9]*)
								sitename_categoryname_20130521.csv				([^_\-]*)_([^_\-]*)_(\d*)
								sitename - categoryname -xxxxxx.csv				([^_\-\s]*)\s*-\s*([^_\-\s]*)\s*-\s*([^_\-\s]*)
								sitename - categoryname -xxxxxx-20130521.csv 	([^_\-\s]*)\s*-\s*([^_\-\s]*)\s*-\s*([^_\-\s]*)\s*-\s*(\d*)
							*/
							$category =''; $header = array();
							if ( preg_match('/^([^_\-]*)$/', $path_parts['filename'], $matches) && isset($matches[0][0]) ) {
								$category = $matches[1];
							} else
							if (preg_match('/^([^_\-]*)_(\d*)$/', $path_parts['filename'], $matches)) {
								$category = $matches[1];
							} else if (preg_match('/^([^_\-]*)_([^_\-]*)_([^_\-0-9]*)$/', $path_parts['filename'], $matches)) {
								$category = $matches[3];
							} else if (preg_match('/^([^_\-]*)_([^_\-]*)_([^_\-]*)_(\d*)$/', $path_parts['filename'], $matches)) {
								$category = $matches[3];
							} else if (preg_match('/^([^_\-]*)_([^_\-0-9]*)$/', $path_parts['filename'], $matches)) {
								$category = $matches[2];
							} else if (preg_match('/^([^_\-]*)_([^_\-]*)_(\d*)$/', $path_parts['filename'], $matches)) {
								$category = $matches[2];
							} else if (preg_match('/^([^_\-\s]*)\s*-\s*([^_\-\s]*)\s*-\s*([^_\-]*)$/', $path_parts['filename'], $matches)) {
								$category = $matches[2];
							} else if (preg_match('/^([^_\-\s]*)\s*-\s*([^_\-\s]*)\s*-\s*([^_\-\s]*)\s*-\s*(\d*)$/', $path_parts['filename'], $matches)) {
								$category = $matches[2];
							}

							if (($handle = fopen($name, "r")) !== FALSE) {
								$first_line = true;
								while (($parsed = fgetcsv($handle, 2000, ",", "\"")) !== false) {
									$continue = false;
									// first line is a header?
									if ($first_line) {
										$first_line = false;

										foreach($parsed as &$col) {
											if ( in_array(strtolower($col),array('url','product name', 'description')) ) {
												$continue = true;
											}
											if (isset($header_replace[$col])) {
												$col = $header_replace[$col];
											}
										}

									}
									if ($continue) {
										$header = $parsed;
										continue;
									}

									$parsed_tmp = $parsed;
									foreach($parsed_tmp as &$col) {
										$col = '"'.str_replace('"','\"', $col).'"';
									}
									$row = implode(',',$parsed_tmp);

									$key = $this->imported_data_model->_get_key($row); $i++;
									if (!array_key_exists($key, $_rows)) {
										$_rows[$key] = array(
											'row'=>$row,
											'category' => $category
										);
										// add parsed data
										if (!empty($header)) {
											foreach( $header as $i=>$h ){
												if (!empty($h)) {
													$_rows[$key]['parsed'][$h] = $parsed[$i];
												}
											}
										}

									}
								}
							}
							fclose($handle);
						}
					}
				}
			}
		}

		$imported_rows = 0;
		// Compare all rows with database rows
		if (!empty($_rows)) {
			$this->imported_data_model->db->trans_start();
			foreach ($_rows as $key=>$arr) {
				if (!$this->imported_data_model->findByKey($key)) {
					if (!empty($arr['category'])) {
						if ( ($category_id = $this->category_model->getIdByName($arr['category'])) == false ) {
							$category_id  = $this->category_model->insert($arr['category']);
						}
						$imported_id = $this->imported_data_model->insert($arr['row'], $category_id);
					} else {
						$imported_id = $this->imported_data_model->insert($arr['row']);
					}

					if (isset($arr['parsed'])) {
						foreach($arr['parsed'] as $key=>$value) {
							$this->imported_data_parsed_model->insert($imported_id, $key, $value);
						}
					}
					$imported_rows++;
				}
			}
			$this->imported_data_model->db->trans_complete();
		}

		echo json_encode(array(
			'message' => 'Imported '.$imported_rows.' rows. Total '.count($_rows).' rows.'
		));
	}

	public function save_new_user()
	{
		$response = array();
		//validate form input
		$this->form_validation->set_rules('user_name', 'User name', 'required|xss_clean|is_unique[users.username]');
		$this->form_validation->set_rules('user_mail', 'User mail', 'required|valid_email|is_unique[users.email]');
		$this->form_validation->set_rules('user_password', 'User password','required|min_length[' . $this->config->item('min_password_length', 'ion_auth') . ']|max_length[' . $this->config->item('max_password_length', 'ion_auth') . ']');
		$this->form_validation->set_rules('user_role', 'User role', 'required|xss_clean]');

		if ($this->form_validation->run() == true)
		{
			$username = strtolower($this->input->post('user_name'));
			$email    = $this->input->post('user_mail');
			$password = $this->input->post('user_password');
			$customers = $this->input->post('user_customers');
			$group = array($this->input->post('user_role'));
			$additional_data = array();
			$active = $this->input->post('user_active');
			$new_id = $this->ion_auth->register($username, $password, $email, $additional_data, $group);
			if ($new_id)
			{
				$this->load->model('users_to_customers_model');
				foreach ($customers as $customer) {
					$this->users_to_customers_model->set($new_id, $customer);
				}
				if((empty($active))){
					$this->ion_auth->deactivate($new_id);
				}
				$response['success'] = 1;
				$response['message'] = 'User created successfully';
				$this->output->set_content_type('application/json')
		            ->set_output(json_encode($response));
			}
		}
		else
		{
			$response['message'] = validation_errors();
			$this->output->set_content_type('application/json')
		        ->set_output(json_encode($response));
		}
	}

	public function save_roles(){
		$roles = array();
		$response = array();

		foreach ($_POST as $checkbox_name => $checkbox_value) {
			$arr = explode('_', $checkbox_name);
			$roles[$arr[1]][] = $arr[0];
		}
		foreach ($roles as $key => $value) {
            $this->ion_auth->set_default_tab_to_group($key, $this->input->post('default_'.$key));
			$deny_controllers = array_diff($this->data['checked_controllers'], $value);
			if($key !== 1){
				$deny_controllers = array_merge($deny_controllers, $this->data['admin_controllers']);
			}
			$saving_errors = $this->ion_auth->set_rules_to_group($key, $deny_controllers);
		}

		if(empty($saving_errors)){
			$response['success'] = 1;
			$response['message'] = 'Roles saved successfully';
		}else{
			$response['message'] = $saving_errors;
		}

		$this->output->set_content_type('application/json')
		            ->set_output(json_encode($response));
	}

	public function jqueryAutocomplete(){
		$userQuery = $this->input->get('term');
		$searchColumn = $this->input->get('column');
		$columns = array('username', 'email');
		if(in_array($searchColumn, $columns)){
			$answer = $this->ion_auth->getUserLike($searchColumn, $userQuery);
			$response = array();
			foreach ($answer as $row) {
				$response[] = array('id' => $row['id'], 'value' => $row[$searchColumn]);
			}
			$this->output->set_content_type('application/json')
			        ->set_output(json_encode($response));
		}
	}

	public function update_user()
	{
		$this->load->model('users_to_customers_model');
		$this->load->model('user_groups_model');
		$response = array();
		$response['success'] = 1;
		$new_data = array();
		$user_id = $this->input->post('user_id');
		$old_user_info = $this->ion_auth->user($user_id)->result_array();
		$old_user_group = $this->user_groups_model->getRoleByUserId($user_id);
		$customers = $this->users_to_customers_model->getByUserId($user_id);
		$old_customers = array();
		foreach ($customers as $customer) {
			$old_customers[] = $customer->customer_id;
		}

		if($old_user_info[0]['username'] != $this->input->post('user_name')){
			$this->form_validation->set_rules('user_name', 'User name', 'required|xss_clean|is_unique[users.username]');
			$new_data['username'] = strtolower($this->input->post('user_name'));
		}

		if($old_user_info[0]['email'] != $this->input->post('user_mail')){
			$this->form_validation->set_rules('user_mail', 'User mail', 'required|valid_email|is_unique[users.email]');
			$new_data['email'] = $this->input->post('user_mail');
		}

		$new_password = $this->input->post('user_password');
		if(!empty($new_password)){
			$this->form_validation->set_rules('user_password', 'User password','required|min_length[' . $this->config->item('min_password_length', 'ion_auth') . ']|max_length[' . $this->config->item('max_password_length', 'ion_auth') . ']');
			$new_data['password'] = $this->input->post('user_password');
		}

		$this->form_validation->set_rules('user_role', 'User role', 'required|xss_clean]');

		if ($this->form_validation->run() == true)
		{
			$new_customers = $this->input->post('user_customers');
			$new_group = $this->input->post('user_role');
			$active = $this->input->post('user_active');

			if(!empty($new_data)){
				$this->ion_auth->update($user_id, $new_data);
			}

			if($old_user_group[0]->group_id != $new_group){
				$this->ion_auth->remove_from_group($old_user_group[0]->group_id, $user_id);
				$this->ion_auth->add_to_group($new_group, $user_id);
			}

			$add_customers = array_diff($new_customers, $old_customers);
			$delete_customers = array_diff($old_customers, $new_customers);

			if(empty($new_customers)){
				foreach ($old_customers as $customer) {
					$this->users_to_customers_model->delete($user_id, $customer);
				}
			}
			if(!empty($add_customers)){
				foreach ($add_customers as $customer) {
					$this->users_to_customers_model->set($user_id, $customer);
				}
			}
			if(!empty($delete_customers)){
				foreach ($delete_customers as $customer) {
					$this->users_to_customers_model->delete($user_id, $customer);
				}
			}

			if((empty($active))){
				$this->ion_auth->deactivate($user_id);
			}else{
				$this->ion_auth->activate($user_id);
			}


			$response['message'] = 'User updated successfully';
			$this->output->set_content_type('application/json')
		        ->set_output(json_encode($response));
		}
		else
		{
			$response['success'] = false;
			$response['message'] = validation_errors();
			$this->output->set_content_type('application/json')
		        ->set_output(json_encode($response));
		}
	}

	public function upload_csv()
    {
		$this->load->library('UploadHandler');

		$this->output->set_content_type('application/json');
		$this->uploadhandler->upload(array(
            'script_url' => site_url('system/upload_csv'),
            'upload_dir' => $this->config->item('csv_upload_dir'),
            'param_name' => 'files',
            'delete_type' => 'POST',
			'accept_file_types' => '/.+\.csv$/i',
		));
	}

    public function get_batch_review()
    {
        $this->load->model('batches_model');
        $results = $this->batches_model->getAll();
        $this->output->set_content_type('application/json')
            ->set_output(json_encode($results));
    }

    public function update_batch_review()
    {
        $this->load->model('batches_model');
        if( !empty( $_POST ) ) {
            $id = $this->input->post('id');
            $title = $this->input->post('title');
            $this->batches_model->update($id, $title);
            echo 'Record updated successfully!';
        }
    }

    public function delete_batch_review()
    {
        $this->load->model('batches_model');
        $id = $this->input->post('id');
        if( is_null( $id ) ) {
            echo 'ERROR: Id not provided.';
            return;
        }
        $this->batches_model->delete( $id );
        echo 'Records deleted successfully';
    }

    public function getBatchById( $id ) {
        $this->load->model('batches_model');
        if( isset( $id ) )
            echo json_encode( $this->batches_model->get( $id ) );
    }

    public function batch_review()
    {
        $this->render();
    }
}