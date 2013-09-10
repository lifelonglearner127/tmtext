<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class System extends MY_Controller {



	function __construct()
 	{
  		parent::__construct();

		$this->data['title'] = 'System Settings';
		$this->data['checked_controllers'] = array( 'batches','measure', 'assess', 'research', 'customer');
		$this->data['admin_controllers'] = array('system', 'admin_customer', 'admin_editor', 'admin_tag_editor');


		$this->load->library('form_validation');

 	}

	public function index() {
		$this->load->model('webshoots_model');
		$this->data['message'] = $this->session->flashdata('message');
		$this->data['email_report_config_sender'] = $this->webshoots_model->getEmailReportConfig('sender');
		$this->data['email_report_config_attach'] = $this->webshoots_model->getEmailReportConfig('attach');
		$this->render();
	}

	public function update_home_pages_config() {
		$this->load->model('webshoots_model');
		$type = $this->input->post('type');
		$value = $this->input->post('value');
		$res = $this->webshoots_model->updateHomePagesConfig($type, $value);
		$this->output->set_content_type('application/json')->set_output(true);
	}

	public function recordcollection() {
		$this->load->model('imported_data_parsed_model');
		$crawl_stack = $this->input->post('crawl_stack'); // !!! array of objects !!!
		$error_code = 1;
		$crawl = array();
		if($crawl_stack !== null && count($crawl_stack) > 0) {
			$cid = md5(time());
			foreach ($crawl_stack as $k => $v) {
				$check = $this->imported_data_parsed_model->checkIfUrlIExists($v['url']); // ---- check if such url exists in products data
				$mid = array(
					'cid' => $cid,
					'imported_data_id' => $check,
					'url' => $v['url'],
					'sku' => $v['sku'],
					'crawl_st' => false
				);
				if($check !== false) {
					$mid['crawl_st'] = true;
				}
				array_push($crawl, $mid);
			}
			if(count($crawl) > 1) { // --- all ok, so record collection to DB
				$record = $this->imported_data_parsed_model->recordProductMatchCollection($crawl);
			} else {
				$error_code = 2; // --- not enough valid collection items (must be 2>)
			}
		} else {
			$error_code = 3; // --- internal server error
		}
		$this->output->set_content_type('application/json')->set_output(json_encode($error_code));
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
            if($arr[0] != 'job'){
                $roles[$arr[1]][] = $arr[0];
            } else {
                $roles[$arr[2]][] = $arr[0].'_'.$arr[1];
            }

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

    public function upload_departments_categories()
    {
        $this->load->library('UploadHandler');

        $this->output->set_content_type('application/json');
        $this->uploadhandler->upload(array(
            'script_url' => site_url('system/upload_departments_categories'),
            'upload_dir' => $this->config->item('csv_upload_dir'),
            'param_name' => 'files',
            'delete_type' => 'POST',
            'accept_file_types' => '/.+\.(txt|jl)$/i',
        ));
    }

    public function save_departments_categories()
    {
        $this->load->model('department_members_model');
        $this->load->model('site_categories_model');
        $site_id = $this->input->post('site_id');
        $site_name = explode(".", strtolower($this->input->post('site_name')));
        $file = $this->config->item('csv_upload_dir').$this->input->post('choosen_file');
        $_rows = array();
        if (($handle = fopen($file, "r")) !== FALSE) {
            while (($data = fgetcsv($handle, 5000, "\n")) !== FALSE) {
                if(!is_null($data[0]) && $data[0]!=''){
                    $_rows[] = json_decode($data[0]);
                }
            }
            fclose($handle);
        }
        foreach($_rows as $row){
            if($row->level <= 0){
                $special = 0;
                $parent_text = '';
                $text = '';
                $url = '';
                if($row->special!='' && !is_null($row->special)){
                    $special = $row->special;
                }
                if(is_array($row->parent_text)){
                    $parent_text = $row->parent_text[0];
                } else if(!is_array($row->parent_text) && !is_null($row->parent_text) && $row->parent_text!=''){
                    $parent_text = $row->parent_text;
                }
                if(is_array($row->text)){
                    $text = $row->text[0];
                } else if(!is_array($row->text) && !is_null($row->text)){
                    $text = $row->text;
                }
                if(is_array($row->url)){
                    $url = $row->url[0];
                } else if(!is_array($row->url) && !is_null($row->url)){
                    $url = $row->url;
                }
                if(substr_count($url, 'http://') == 0 && $this->input->post('site_name')!='[Choose site]'){
                    $url = str_replace('..', '', $url);
                    $url = 'http://'.strtolower($this->input->post('site_name')).$url;
                }	
                $department_members_id = 0;
                if($parent_text!=''){
                    $check_id = $this->department_members_model->checkExist($site_name[0], $site_id, $parent_text);
                    if($check_id == false){
                        $department_members_id = $this->department_members_model->insert($site_name[0], $site_id, $parent_text);
                    } else {
                        $department_members_id = $check_id;
                    }
                }
				/*new columns*/
				if(isset($row->nr_products) && is_array($row->nr_products)){
                    $nr_products = $row->nr_products[0];
                } else if(isset($row->nr_products) && !is_array($row->nr_products) && !is_null($row->nr_products) && $row->nr_products!=''){
                    $nr_products = $row->nr_products;
                }
				
				if(isset($row->description_wc) && is_array($row->description_wc)){
                    $description_wc = $row->description_wc[0];
                } else if(isset($row->description_wc) && !is_array($row->description_wc) && !is_null($row->description_wc) && $row->description_wc!=''){
                    $description_wc = $row->description_wc;
                }
				if(isset($row->description_text) && is_array($row->description_text)){
                    $description_text = $row->description_text[0];
                } else if(isset($row->description_text) && !is_array($row->description_text) && !is_null($row->description_text) && $row->description_text!=''){
                    $description_text = $row->description_text;
                }
				
				
				if(isset($row->keyword_density) && is_array($row->keyword_density)){
				
                    $keyword_density = $row->keyword_density[0];
                } else if(isset($row->keyword_density) && !is_array($row->keyword_density) && !is_null($row->keyword_density) && $row->keyword_density!=''){
				
                    $keyword_density = json_encode($row->keyword_density);
                }
				
				if(isset($row->description_title) && is_array($row->description_title)){
				
                    $description_title = $row->description_title[0];
                } else if(isset($row->description_title) && !is_array($row->description_title) && !is_null($row->description_title) && $row->description_title!=''){
				
                    $description_title = json_encode($row->description_title);
                }
				if(isset($row->description_text) && is_array($row->description_text)){
				
                    $description_text = $row->description_text[0];
                } 
				else if(isset($row->description_text) && !is_array($row->description_text) && !is_null($row->description_text) && $row->description_text!=''){
				
                    $description_text = json_encode($row->description_text);
                }
				
				/*end new columns*/
                if($text != ''){
                    $check_site = $this->site_categories_model->checkExist($site_id, $text);
                    if($check_site == false){
                        $this->site_categories_model->insert($site_id, $text, $url, $special, $parent_text, $department_members_id, $nr_products, $description_wc,$keyword_density,$description_title,$description_text);
                    }
                }
			}
            if($row->level == 1){
           
                $check_id = $this->department_members_model->checkExist($site_name[0], $site_id, $row->text);
                
                if(isset($row->description_wc) && is_array($row->description_wc)){
                    $description_wc = $row->description_wc[0];
                } else if(isset($row->description_wc) && !is_array($row->description_wc) && !is_null($row->description_wc) && $row->description_wc!=''){
                    $description_wc = $row->description_wc;
                }
                
     	
		if(isset($row->keyword_density) && is_array($row->keyword_density)){
				
                    $keyword_density = $row->keyword_density[0];
                } else if(isset($row->keyword_density) && !is_array($row->keyword_density) && !is_null($row->keyword_density) && $row->keyword_density!=''){
				
                    $keyword_density = json_encode($row->keyword_density);
                }
				
		if(isset($row->description_title) && is_array($row->description_title)){
				
                    $description_title = $row->description_title[0];
                } else if(isset($row->description_title) && !is_array($row->description_title) && !is_null($row->description_title) && $row->description_title!=''){
				
                    $description_title = json_encode($row->description_title);
                }
		if(isset($row->description_text) && is_array($row->description_text)){
				
                    $description_text = $row->description_text[0];
                } 
				else if(isset($row->description_text) && !is_array($row->description_text) && !is_null($row->description_text) && $row->description_text!=''){
				
                    $description_text = json_encode($row->description_text);
                }
                
                if($check_id == false){
                    $this->department_members_model->insert($site_name[0], $site_id, $row->text, $description_wc, $description_text, $keyword_density, $description_title );
                }
            }
        }
		
        $response['message'] =  'File was added successfully';
        $this->output->set_content_type('application/json')->set_output(json_encode($response));
    }

    public function delete_department()
    {
        $this->load->model('department_members_model');
        $department_id = $this->input->post('id');
        $this->department_members_model->delete($department_id);

        $response['message'] =  'Department was deleted successfully';
        $this->output->set_content_type('application/json')->set_output(json_encode($response));
    }

    public function delete_category()
    {
        $this->load->model('site_categories_model');
        $category_id = $this->input->post('id');
        $this->site_categories_model->delete($category_id);
        $response['message'] =  'Category was deleted successfully';
        $this->output->set_content_type('application/json')->set_output(json_encode($response));
    }

    public function delete_overall()
    {
        $this->load->model('best_sellers_model');
        $overall_id = $this->input->post('id');
        $this->best_sellers_model->delete($overall_id);
        $response['message'] =  'Overall was deleted successfully';
        $this->output->set_content_type('application/json')->set_output(json_encode($response));
    }

    public function delete_all(){
        $this->load->model('site_categories_model');
        $this->load->model('department_members_model');
        $this->load->model('best_sellers_model');
        $type = $this->input->post('type');
        $site_id = $this->input->post('site_id');
        $site_name = explode(".", $this->input->post('site_name'));
        if($type == 'categories'){
            $this->site_categories_model->deleteAll($site_id);
            $response['message'] =  'Categories was deleted successfully';
        } elseif($type == 'departments'){
            $this->department_members_model->deleteAll(strtolower($site_name[0]));
            $response['message'] =  'Departments was deleted successfully';
        } elseif($type == 'overall'){
            $this->best_sellers_model->deleteAll($site_id);
            $response['message'] =  'Overall was deleted successfully';
        }

        $this->output->set_content_type('application/json')->set_output(json_encode($response));
    }

    public function save_best_sellers(){
        $this->load->model('best_sellers_model');
        $this->load->model('sites_model');

        $site_id = $this->input->post('site_id');
        $site_name = explode(".", strtolower($this->input->post('site_name')));
        $file = $this->config->item('csv_upload_dir').$this->input->post('overall_choosen_file');
        $_rows = array();
        if (($handle = fopen($file, "r")) !== FALSE) {
            while (($data = fgetcsv($handle, 1000, "\n")) !== FALSE) {
                if(!is_null($data[0]) && $data[0]!=''){
                    $_rows[] = json_decode($data[0]);
                }
            }
            fclose($handle);
        }
        foreach($_rows as $row){
            $listprice ='';
            $brand = '';
            $department = '';
            $price = '';
            $page_title = '';
            $url = '';
            $rank = '';
            $list_name = '';
            $product_name = '';
            if(!is_null($row->listprice)){
                $listprice = $row->listprice;
            }
            if(!is_null( $row->brand)){
                $brand = $row->brand;
            }
            if(!is_null( $row->department)){
                $department = $row->department;
            }
            if(!is_null( $row->price)){
                $price = $row->price;
            }
            if(!is_null( $row->page_title)){
                $page_title = $row->page_title;
            }
            if(!is_null( $row->url)){
                $url = $row->url;
            }
            if(!is_null( $row->rank)){
                $rank = $row->rank;
            }
            if(!is_null( $row->list_name)){
                $list_name = $row->list_name;
            }
            if(!is_null( $row->product_name)){
                $product_name = $row->product_name;
            }
            if($page_title!=''){
                $this->best_sellers_model->insert($site_id, $page_title, $url, $brand,
                    $rank, $department, $price, $list_name, $product_name, $listprice);
            }
        }
        $response['message'] =  'File was added successfully';
        $this->output->set_content_type('application/json')->set_output(json_encode($response));
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

    public function upload_img()
    {
        $this->load->library('UploadHandler');
        $this->output->set_content_type('application/json');

        $this->uploadhandler->upload(array(
            'script_url' => site_url('system/upload_img'),
            'upload_dir' => 'webroot/img/',
            'param_name' => 'files',
            'delete_type' => 'POST',
            'accept_file_types' => '/.+\.(jpg|gif|png)$/i',
        ));
    }

    public function get_batch_review()
    {
        $this->load->model('batches_model');
        $results = $this->batches_model->getBatchReview();
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

    public function getCategoriesBySiteId()
    {
        $this->load->model('site_categories_model');
        $department_id = '';
        if($this->input->post('department_id') != ''){
            $department_id = $this->input->post('department_id');
        }
        $result = $this->site_categories_model->getAllBySiteId($this->input->post('site_id'), $department_id);
        $this->output->set_content_type('application/json')->set_output(json_encode($result));
    }

    public function getBestSellersBySiteId(){
        $this->load->model('best_sellers_model');
        $result = $this->best_sellers_model->getAllBySiteId($this->input->post('site_id'));
        $this->output->set_content_type('application/json')->set_output(json_encode($result));
    }

    public function category_list()
    {
        $this->load->model('site_categories_model');
        $categories = $this->site_categories_model->getAll();
        $category_list = array();
        foreach($categories as $category){
            array_push($category_list, $category->text);
        }
        return $category_list;

    }

    private function category_list_new() {
        $this->load->model('site_categories_model');
        $categories = $this->site_categories_model->getAll();
        $category_list = array();
        foreach($categories as $category) {
        	$mid = array(
        		'id' => $category->id,
        		'site_id' => $category->site_id,
        		'text' => $category->text,
        		'url' => $category->url,
        		'special' => $category->special,
        		'parent_text' => $category->parent_text,
        		'department_members_id' => $category->department_members_id
        	);
        	$category_list[] = $mid;
        }
        return $category_list;
    }

    public function system_sites_category_snap() {
    	$res = array(
    		'status' => false,
    		'snap' => '',
    		'msg' => ''
    	);
    	$id = $this->input->post('id');
    	$this->load->model('webshoots_model');
    	$this->load->model('site_categories_model');
    	$category = $this->site_categories_model->get($id);
    	if(count($category) > 0) {
    		$cat = $category[0];
    		// === implement snapshoting (start)
    		$http_status = $this->webshoots_model->urlExistsCode($cat->url);
    		if($http_status == 200) {
	            $url = preg_replace('#^https?://#', '', $cat->url);
	            $call_url = $this->webshoots_model->webthumb_call_link($url);
	            $snap_res = $this->webshoots_model->crawl_webshoot($call_url, $cat->id, 'sites_cat_snap-');
	            // ==== check image (if we need to repeat snap craw, but using snapito.com) (start)
				$fs = filesize($snap_res['dir']);
				if($fs === false || $fs < 10000) { // === so re-craw it
					@unlink($snap_res['dir']);
					$api_key = $this->config->item('snapito_api_secret');
	    			$call_url = "http://api.snapito.com/web/$api_key/mc/$url";
	    			$snap_res = $this->webshoots_model->crawl_webshoot($call_url, $cat->id, 'sites_cat_snap-');
				}
				// ==== check image (if we need to repeat snap craw, but using snapito.com) (end)
	            $res_insert = $this->site_categories_model->insertSiteCategorySnap($cat->id, $snap_res['img'], $snap_res['path'], $snap_res['dir'], $http_status);
	    		if($res_insert > 0) {
	    			$res['snap'] = $snap_res['path'];
	    			$res['status'] = true;
	    			$res['msg'] = 'Ok';
	    		}
	    		// === implement snapshoting (end)
    		} else {
    			$res['msg'] = "Category url is unreachable (400) or redirected (302). Snapshot attempt is canceled. HTTP STATUS: $http_status";
    		}
    	} else {
    		$res['msg'] = "Such category don't exists in DB. Snapshot attempt is canceled.";
    	}
    	$this->output->set_content_type('application/json')->set_output(json_encode($res));
    }

    public function sites_view()
    {
        $this->load->model('sites_model');
        $this->load->model('department_members_model');
        $this->load->model('best_sellers_model');

        $sites = $this->sites_model->getAll();
        $sitesArray = array();
        foreach ($sites as $site) {
            if(!in_array($customer->name, sitesArray)){
                $sitesArray[$site->id] = $site->name;
            }
        }
        foreach ($this->department_members_model->getAll() as $row) {
            $this->data['departmens_list'][$row->id] = $row->text;
        }
        foreach ($this->best_sellers_model->getAll() as $row) {
            $this->data['best_sellers_list'][$row->id] = $row->page_title;
        }

        $this->data['sites'] = $sitesArray;
        $this->data['category_list'] = $this->category_list_new();
        $this->render();
    }

 	public function generate_attributes() {
 		$this->load->model('imported_data_parsed_model');
		$this->load->model('imported_data_model');
		$this->load->model('imported_data_attributes_model');

		$lines = $this->imported_data_model->findNullAttributes(1000);

		foreach ( $lines as $line) {
			$imported_id = $line->id;
			$data = $this->imported_data_parsed_model->getByImId($imported_id);

			$res = array();
			foreach($data as $key => $value) {
				if ($key != 'url') {
					$descCmd = str_replace($this->config->item('cmd_mask'), $value ,$this->config->item('tsv_cmd'));
					if ($result = shell_exec($descCmd)) {
						$a = json_decode(json_encode(simplexml_load_string($result)),1);
						foreach ($a['description']['attributes']['attribute'] as $attribute) {
							$res[$key][$attribute['@attributes']['tagName']] = $attribute['@attributes']['value'];
						}
					}
				}
			}

			if (!empty($res)) {
				$result = $this->imported_data_model->getRow($imported_id);
				if (is_null($result->imported_data_attribute_id)) {
					$imported_data_attribute_id = $this->imported_data_attributes_model->insert(serialize($res));
					$this->imported_data_model->update_attribute_id($imported_id, $imported_data_attribute_id);
				} else {
					$imported_data_attribute_id = $result->imported_data_attribute_id;
					$this->imported_data_attributes_model->update($imported_data_attribute_id ,serialize($res));
				}
			}
		}
 	}

 	function similarity_calculation(){
		$this->load->model('imported_data_parsed_model');
		$this->load->model('imported_data_model');
		$this->load->model('imported_data_attributes_model');
		$this->load->model('similar_imported_data_model');
		$this->load->model('similar_groups_model');

		$imported = $this->similar_groups_model->getIdsForComparition();

		$merged = array();

		foreach($imported as $imported_id) {
			$attributes = $this->imported_data_attributes_model->getByImportedDataId($imported_id);

			$resArr = array();
			foreach( unserialize($attributes->attributes) as $key=>$value ) {
				if ($key != 'features') {
					$resArr = array_merge($resArr, $value);
				}
			}
			$merged[] = $resArr;
		}


		function allKeysExist($arr, $keys) {
			foreach($keys as $key) {
				if (!key_exists($key, $arr)) {
					return false;
				}
			}
			return true;
		}

		$similar_array = array(); $similar_to = array(); $similar_to2 = array();

		for($i=0; $i<count($merged); $i++) {
			for($j=$i+1; $j<count($merged); $j++) {
				$intersec = array_intersect($merged[$i],$merged[$j]);
				$diff = abs(count($merged[$i])-count($merged[$j]));
				$max = max(count($merged[$i]),count($merged[$j]));
				$similarity = count($intersec)/max(count($merged[$i]),count($merged[$j]));

				$inserted = false;
				if (allKeysExist($intersec, $this->config->item('important_attributes'))) {
					foreach ( $similar_to as &$arr) {
						if (in_array($imported[$i], $arr) && !in_array($imported[$j], $arr)) {
							$arr[] = $imported[$j];
							$inserted = true;
						} else if (in_array($imported[$j], $arr) && !in_array($imported[$i], $arr)) {
							$arr[] = $imported[$i];
							$inserted = true;
						}
					}

					if (!$inserted) {
						$similar_to[] = array($imported[$i], $imported[$j]);
					}
				} else if (allKeysExist($intersec, $this->config->item('important_attributes_min')) && ($similarity > 0.7)) {
					foreach ( $similar_to2 as &$arr) {
						if (in_array($imported[$i], $arr) && !in_array($imported[$j], $arr)) {
							$arr[] = $imported[$j];
							$inserted = true;
						} else if (in_array($imported[$j], $arr) && !in_array($imported[$i], $arr)) {
							$arr[] = $imported[$i];
							$inserted = true;
						}
					}

					if (!$inserted) {
						$similar_to2[] = array($imported[$i], $imported[$j]);
					}
				}
			}
		}


		function saveSimilar( $similar_to, $percent = 0) {
			$CI =& get_instance();

			$similarity = 1;
			foreach($similar_to as &$similar_group) {
				$group_id = false;

				$j = count($similar_group);
				for($i=0; $i<$j ; $i++) {
					if($group_id = $CI->similar_imported_data_model->findByImportedDataId($similar_group[$i])) {
						 unset($similar_group[$i]);
					}
				}

				if($group_id === false) {
					if ($percent !==0) {
						$similarity = 0;
					}
					$group_id = $CI->similar_groups_model->insert($similarity, $percent);
				}
				foreach($similar_group as $imported_id) {
					$CI->similar_imported_data_model->insert($imported_id, $group_id);
				}
			}
		}

		saveSimilar($similar_to);
		saveSimilar($similar_to2, 70);
 	}

    public function get_site_info()
    {
        $this->load->model('sites_model');
        $site_id = $this->input->post('site');
        $site_info = $this->sites_model->get($site_id);
        /* foreach($site_info as $site){
             $site->image_url = $this->config->item('tmp_upload_dir').$site->image_url;
         }*/
        $this->output->set_content_type('application/json')->set_output(json_encode($site_info));
    }

    public function add_new_site()
    {
        $this->load->model('sites_model');
        $response['id'] = $this->sites_model->insertSiteByName($this->input->post('site'));
        $response['message'] =  'Site was added successfully';
        $this->output->set_content_type('application/json')->set_output(json_encode($response));
    }

    public function delete_site()
    {
        $this->load->model('sites_model');
        $this->sites_model->delete($this->input->post('site'));
        $response['message'] =  'Site was deleted successfully';
        $this->output->set_content_type('application/json')->set_output(json_encode($response));
    }

    public function update_site_logo()
    {
        $this->load->model('sites_model');
        $this->sites_model->updateSite($this->input->post('id'), $this->input->post('logo'));
        $response['message'] =  'Site was updated successfully';
        $this->output->set_content_type('application/json')->set_output(json_encode($response));
    }

    public function update_site_info()
    {
        $this->load->model('sites_model');
        $this->sites_model->update($this->input->post('id'), $this->input->post('site_name'),
            $this->input->post('site_url'), $this->input->post('logo'));
        $response['message'] =  'Site was updated successfully';
        $this->output->set_content_type('application/json')->set_output(json_encode($response));
    }

    public function delete_sitelogo()
    {
        $this->load->model('sites_model');
        $this->sites_model->updateSite($this->input->post('id'), $this->input->post('logo'));
        $response['message'] =  'Site was deleted successfully';
        $this->output->set_content_type('application/json')->set_output(json_encode($response));
    }

    private function customers_list_new() {
        $this->load->model('customers_model');
        $output = array();
        $customers_init_list = $this->customers_model->getAll();
        if (count($customers_init_list) > 0) {
            foreach ($customers_init_list as $key => $value) {
                $mid = array(
                    'id' => $value->id,
                    'desc' => $value->description,
                    'image_url' => $value->image_url,
                    'name' => $value->name,
                    'name_val' => strtolower($value->name)
                );
                $output[] = $mid;
            }
        }
        return $output;
    }

    public function system_reports() {
        $this->render();
    }

    public function system_reports_get_all() {
        $this->load->model('reports_model');
        $response['data'] = $this->reports_model->get_all_report_names();
        $this->output->set_content_type('application/json')->set_output(json_encode($response));
    }

    public function system_reports_get_options() {
        $this->load->model('reports_model');
        $id = $this->input->get('id');
        $page = $this->input->get('page');
        $report = $this->reports_model->get_by_id($id);
        switch ($page) {
            case 'cover':
                $response = array(
                    'page_name' => $report[0]->cover_page_name,
                    'page_order' => $report[0]->cover_page_order,
                    'page_layout' => $report[0]->cover_page_layout,
                    'page_body' => $report[0]->cover_page_body,
                );
                break;
            case 'recommendations':
                $response = array(
                    'page_name' => $report[0]->recommendations_page_name,
                    'page_order' => $report[0]->recommendations_page_order,
                    'page_layout' => $report[0]->recommendations_page_layout,
                    'page_body' => $report[0]->recommendations_page_body,
                );
                break;
            case 'about':
                $response = array(
                    'page_name' => $report[0]->about_page_name,
                    'page_order' => $report[0]->about_page_order,
                    'page_layout' => $report[0]->about_page_layout,
                    'page_body' => $report[0]->about_page_body,
                );
                break;
            default:
                $response = array(
                    'page_name' => $report[0]->cover_page_name,
                    'page_order' => $report[0]->cover_page_order,
                    'page_layout' => $report[0]->cover_page_layout,
                    'page_body' => $report[0]->cover_page_body,
                );
                break;
        }
        $this->output->set_content_type('application/json')->set_output(json_encode($response));
    }

    public function system_reports_create() {
        $this->load->model('reports_model');
        $name = $this->input->post('name');
        $id = $this->reports_model->insert($name);
        $response['id'] = $id;
        $this->output->set_content_type('application/json')->set_output(json_encode($response));
    }

    public function system_reports_delete() {
        $this->load->model('reports_model');
        $id = $this->input->post('id');
        $this->reports_model->delete($id);
    }

    public function system_reports_update() {
        $this->load->model('reports_model');
        $id = $this->input->post('id');
        $params = json_decode($this->input->post('params'));
        $response['success'] = $this->reports_model->update($id, $params);
        $this->output->set_content_type('application/json')->set_output(json_encode($response));
    }
    
    public function system_logins() {
        $this->render();
	}
	
	public function system_last_logins() {
		$this->load->model('logins_model');
		$response['data'] = $this->logins_model->get_last_logins();
        $this->output->set_content_type('application/json')->set_output(json_encode($response));
	}
}
