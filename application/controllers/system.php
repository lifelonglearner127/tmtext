<?php
if (!defined('BASEPATH'))
	exit('No direct script access allowed');

class System extends MY_Controller {

	function __construct() {
		parent::__construct();
		$this -> load -> library('helpers');
		$this -> load -> library('ion_auth');
		$this -> data['title'] = 'System Settings';
		$this -> data['checked_controllers'] = array('batches', 'measure', 'assess', 'research', 'brand', 'customer');
		$this -> data['admin_controllers'] = array('system', 'admin_customer', 'admin_editor', 'admin_tag_editor');

		$this -> load -> model('imported_data_parsed_model');
		$this -> load -> library('form_validation');

		$this -> ion_auth -> add_auth_rules(array('urls_snapshot' => true, 'check_urls_threading' => true, 'stopChecking'=>true));

	}

	public function index() {
		$this -> load -> model('webshoots_model');
		$this -> data['message'] = $this -> session -> flashdata('message');
		$this -> data['email_report_config_sender'] = $this -> webshoots_model -> getEmailReportConfig('sender');
		$this -> data['email_report_config_attach'] = $this -> webshoots_model -> getEmailReportConfig('attach');
		$this -> data['email_report_config_logo'] = $this -> webshoots_model -> getEmailReportConfig('logo');
		$this -> render();
	}

	public function clear_imported_data_parsed() {
		$this -> load -> model('imported_data_parsed_archived_model');
		$this -> load -> model('imported_data_parsed_model');
                $this -> load -> model('statistics_new_model');
//		$this -> imported_data_parsed_archived_model -> mark_queued_from_archive();
		$this -> imported_data_parsed_model -> delete_repeated_data();
                $results= $this -> imported_data_parsed_model ->get_items_that_havenot_batch();
                
                foreach($results as $result){
                    if ($this -> imported_data_parsed_archived_model -> saveToArchive($result['imported_data_id'])) {
                        $this -> imported_data_parsed_model -> deleteRows($result['imported_data_id']);
                        $this -> statistics_new_model -> delete($result['imported_data_id']);
                    }
                }
		echo "end";
	}

	public function new_batch_nf_list_modal() {
		$this -> load -> model('webshoots_model');
		$rec_list = $this -> webshoots_model -> getEmailToBatchNotifyList();
		$data = array('rec_list' => $rec_list);
		$this -> load -> view('system/new_batch_nf_list_modal', $data);
	}

	public function add_email_to_batch_notify_list() {
		$this -> load -> model('webshoots_model');
		$rc = $this -> input -> post('rc');
		$res = $this -> webshoots_model -> addEmailToBatchNotifyList($rc);
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($res));
	}

	public function update_home_pages_config() {
		$this -> load -> model('webshoots_model');
		$type = $this -> input -> post('type');
		$value = $this -> input -> post('value');
		$res = $this -> webshoots_model -> updateHomePagesConfig($type, $value);
		$this -> output -> set_content_type('application/json') -> set_output(true);
	}

	public function recordcollection() {
		$this -> load -> model('imported_data_parsed_model');
		$crawl_stack = $this -> input -> post('crawl_stack');
		// !!! array of objects !!!
		$error_code = 1;
		$crawl = array();
		if ($crawl_stack !== null && count($crawl_stack) > 0) {
			$cid = md5(time());
			foreach ($crawl_stack as $k => $v) {
				$check = $this -> imported_data_parsed_model -> checkIfUrlIExists($v['url']);
				// ---- check if such url exists in products data
				$mid = array('cid' => $cid, 'imported_data_id' => $check, 'url' => $v['url'], 'sku' => $v['sku'], 'crawl_st' => false);
				if ($check !== false) {
					$mid['crawl_st'] = true;
				}
				array_push($crawl, $mid);
			}
			if (count($crawl) > 1) {// --- all ok, so record collection to DB
				$record = $this -> imported_data_parsed_model -> recordProductMatchCollection($crawl);
			} else {
				$error_code = 2;
				// --- not enough valid collection items (must be 2>)
			}
		} else {
			$error_code = 3;
			// --- internal server error
		}
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($error_code));
	}

	public function testattributesext() {
		$s = $this -> input -> post('desc');
		$descCmd = str_replace($this -> config -> item('cmd_mask'), $s, $this -> system_settings['python_cmd']);
		echo "SEARCH: " . $s . "<br />";
		echo "MASK: " . $this -> config -> item('cmd_mask') . "<br />";
		echo "CMD: " . $this -> system_settings['python_cmd'] . "<br />";
		echo "EXEC RES: " . shell_exec($descCmd) . "<br />";
		if ($result = shell_exec($descCmd)) {
			echo "EXEC RES:" . "<br />";
			echo var_dump($result);
			if (preg_match_all('/.*ELECTR_DESCRIPTION:\s*(.*)\s*-{5,}/', $result, $matches)) {
				echo "PREG MATCH RES:" . "<br />";
				echo var_dump($matches);
			}
			die('NO MATCHES');
		}
		die('EXEC LAUNCH FAILED!');
	}

	public function deleteproductsvotedpair() {
		$this -> load -> model('imported_data_parsed_model');
		$id = $this -> input -> post('id');
		$res = $this -> imported_data_parsed_model -> deleteProductsVotedPair($id);
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($res));
	}

	public function renewcomparerightsidefromdropdown() {
		$customer_r_selected = $this -> input -> post('customer_r_selected');
		$customer_l = $this -> input -> post('customer_l');
		$id_l = $this -> input -> post('id_l');
		$id_r = $this -> input -> post('id_r');
		$this -> load -> model('imported_data_parsed_model');
		$get_random_r = $this -> imported_data_parsed_model -> getRandomRightCompareProductDrop($customer_r_selected, $customer_l, $id_l, $id_r);
		$data = array('get_random_r' => $get_random_r);
		$this -> load -> view('system/renewcomparerightside', $data);
	}

	public function renewcomparerightside() {
		$customer_l = $this -> input -> post('customer_l');
		$id_l = $this -> input -> post('id_l');
		$this -> load -> model('imported_data_parsed_model');
		$get_random_r = $this -> imported_data_parsed_model -> getRandomRightCompareProduct($customer_l, $id_l);
		$data = array('get_random_r' => $get_random_r);
		$this -> load -> view('system/renewcomparerightside', $data);
	}

	public function renewallcomparesides() {
		$this -> load -> model('imported_data_parsed_model');

		$get_random_l = $this -> imported_data_parsed_model -> getRandomLeftCompareProduct();
		$get_random_r = $this -> imported_data_parsed_model -> getRandomRightCompareProduct($get_random_l['customer'], $get_random_l['id']);

		$data = array('get_random_l' => $get_random_l, 'get_random_r' => $get_random_r);
		$this -> load -> view('system/renewallcomparesides', $data);
	}

	public function getmatchnowinterface() {
		$this -> load -> model('imported_data_parsed_model');

		$get_random_l = $this -> imported_data_parsed_model -> getRandomLeftCompareProduct();
		// $get_random_r = $this->imported_data_parsed_model->getRandomRightCompareProduct($get_random_l['customer'], $get_random_l['id']);
		$get_random_r = $this -> imported_data_parsed_model -> getRandomRightCompareProduct($get_random_l['customer'], $get_random_l['id'], $get_random_l['product_name']);

		$data = array('get_random_l' => $get_random_l, 'get_random_r' => $get_random_r);
		$this -> load -> view('system/getmatchnowinterface', $data);
	}

	public function getproductscomparevoted() {
		$page = $this -> input -> post('page');
		$items_per_page = 2;
		$this -> load -> model('imported_data_parsed_model');
		$data = array('v_producs' => $this -> imported_data_parsed_model -> getProductsCompareVoted($page, $items_per_page), 'v_producs_count' => $this -> imported_data_parsed_model -> getProductsCompareVotedTotalCount(), 'page' => $page, 'items_per_page' => $items_per_page);
		$this -> load -> view('system/getproductscomparevoted', $data);
	}

	public function votecompareproducts() {
		$this -> load -> model('imported_data_parsed_model');
		$ids = $this -> input -> post('ids');
		$dec = $this -> input -> post('dec');
		$output = $this -> imported_data_parsed_model -> voteCompareProducts($ids, $dec);
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($output));
	}

	public function getcompareproducts() {
		$this -> load -> model('imported_data_parsed_model');
		$ids = $this -> input -> post('ids');
		$data = array('c_product' => $this -> imported_data_parsed_model -> getProductsByIdStack($ids));
		$this -> load -> view('system/getcompareproducts', $data);
	}

	public function system_productsmatch() {
		$this -> render();
	}

	public function system_compare() {
		$this -> load -> model('imported_data_parsed_model');
		$this -> data['all_products'] = $this -> imported_data_parsed_model -> getAllProducts();
		$this -> render();
	}

	public function system_accounts() {
		$this -> render();
	}

	public function system_roles() {

		$this -> load -> model('user_groups_model');
		$user_groups = $this -> user_groups_model -> getAll();
		$this -> data['user_groups'] = $user_groups;
		$checked = array();
		foreach ($user_groups as $user_group) {
			$rules = unserialize($user_group -> auth_rules);
			foreach ($this->data['checked_controllers'] as $checked_controller) {
				if ($rules[$checked_controller]['index']) {
					$checked[$user_group -> id][$checked_controller] = true;
				}
			}
			$checked[$user_group -> id]['default_controller'] = $user_group -> default_controller;
		}
		$this -> data['checked'] = $checked;
		$this -> render();
	}

	public function system_users() {
		$this -> load -> model('user_groups_model');
		$this -> load -> model('customers_model');
		$this -> data['user_groups'] = $this -> user_groups_model -> getAll();
		$customers = $this -> customers_model -> getAll();
		$customersArray = array();
		$customersArray['all'] = 'All';
		foreach ($customers as $customer) {
			if (!in_array($customer -> name, $customersArray)) {
				$customersArray[$customer -> id] = $customer -> name;
			}
		}
		asort($customersArray);
		$this -> data['customers'] = $customersArray;
		$this -> data['message'] = array();
		$this -> render();
	}

	public function save() {
		$response = array();
		$this -> form_validation -> set_rules('settings[site_name]', 'Site name', 'required|xss_clean');
		$this -> form_validation -> set_rules('settings[company_name]', 'Company name', 'required|xss_clean');
		$this -> form_validation -> set_rules('settings[csv_directories]', 'CSV Directories', 'required|xss_clean');
		$this -> form_validation -> set_rules('settings[tag_rules_dir]', 'tagRules', 'required|xss_clean');
		// Shulgin I.L.
		$this -> form_validation -> set_rules('settings[python_cmd]', 'Python script', 'required|xss_clean');
		$this -> form_validation -> set_rules('settings[java_cmd]', 'Java tools', 'required|xss_clean');
		$this -> form_validation -> set_rules('settings[python_input]', 'Python input', 'required|xss_clean');
		$this -> form_validation -> set_rules('settings[java_input]', 'Java input', 'required|xss_clean');

		if ($this -> form_validation -> run() === true) {
			$settings = $this -> input -> post('settings');
			// Process checkboxes
			$settings['use_files'] = (isset($settings['use_files']) ? true : false);
			$settings['use_database'] = (isset($settings['use_database']) ? true : false);

			$settings['java_generator'] = (isset($settings['java_generator']) ? true : false);
			$settings['python_generator'] = (isset($settings['python_generator']) ? true : false);

			$this -> settings_model -> db -> trans_start();
			foreach ($settings as $key => $value) {
				if (!$this -> settings_model -> update_system_value($key, $value)) {
					$this -> settings_model -> create_system($key, $value, $key);
				}
			}
			$this -> settings_model -> db -> trans_complete();
			$response['success'] = 1;
			$response['message'] = 'Settings vas saved successfully';
		} else {
			$response['message'] = (validation_errors()) ? validation_errors() : '';
		}
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($response));
	}

	public function save_account_deafults() {
		$response = array();
		$this -> form_validation -> set_rules('settings[title_length]', 'Default Title', 'required|integer|xss_clean');
		$this -> form_validation -> set_rules('settings[description_length]', 'Description Length', 'required|integer|xss_clean');

		$response['message'] = 'ping';
		if ($this -> form_validation -> run() === true) {
			$settings = $this -> input -> post('settings');

			$this -> settings_model -> db -> trans_start();
			foreach ($settings as $key => $value) {
				if (!$this -> settings_model -> update_system_value($key, $value)) {
					$this -> settings_model -> create_system($key, $value, $key);
				}
			}
			$this -> settings_model -> db -> trans_complete();
			$response['success'] = 1;
			$response['message'] = 'Settings vas saved successfully';
		} else {
			$response['message'] = (validation_errors()) ? validation_errors() : 'Saving error';
		}
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($response));
	}

	public function csv_import() {
		$this -> load -> model('imported_data_model');
		$this -> load -> model('imported_data_parsed_model');
		$this -> load -> model('category_model');

		$_rows = array();
		$i = 0;

		$header_replace = $this -> config -> item('csv_header_replace');
		// Find all unique lines in files
		foreach (explode("\n",trim($this->system_settings['csv_directories'])) as $_path) {
			if ($path = realpath($_path)) {
				$objects = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($path), RecursiveIteratorIterator::SELF_FIRST);
				foreach ($objects as $name => $object) {
					if ($object -> isFile()) {
						$path_parts = pathinfo($object -> getFilename());
						if (in_array($path_parts['extension'], array('csv'))) {

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
							$category = '';
							$header = array();
							if (preg_match('/^([^_\-]*)$/', $path_parts['filename'], $matches) && isset($matches[0][0])) {
								$category = $matches[1];
							} else if (preg_match('/^([^_\-]*)_(\d*)$/', $path_parts['filename'], $matches)) {
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

										foreach ($parsed as &$col) {
											if (in_array(strtolower($col), array('url', 'product name', 'description'))) {
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
									foreach ($parsed_tmp as &$col) {
										$col = '"' . str_replace('"', '\"', $col) . '"';
									}
									$row = implode(',', $parsed_tmp);

									$key = $this -> imported_data_model -> _get_key($row);
									$i++;
									if (!array_key_exists($key, $_rows)) {
										$_rows[$key] = array('row' => $row, 'category' => $category);
										// add parsed data
										if (!empty($header)) {
											foreach ($header as $i => $h) {
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
			$this -> imported_data_model -> db -> trans_start();
			foreach ($_rows as $key => $arr) {
				if (!$this -> imported_data_model -> findByKey($key)) {
					if (!empty($arr['category'])) {
						if (($category_id = $this -> category_model -> getIdByName($arr['category'])) == false) {
							$category_id = $this -> category_model -> insert($arr['category']);
						}
						$imported_id = $this -> imported_data_model -> insert($arr['row'], $category_id);
					} else {
						$imported_id = $this -> imported_data_model -> insert($arr['row']);
					}

					if (isset($arr['parsed'])) {
						foreach ($arr['parsed'] as $key => $value) {
							$this -> imported_data_parsed_model -> insert($imported_id, $key, $value);
						}
					}
					$imported_rows++;
				}
			}
			$this -> imported_data_model -> db -> trans_complete();
		}

		echo json_encode(array('message' => 'Imported ' . $imported_rows . ' rows. Total ' . count($_rows) . ' rows.'));
	}

	public function save_new_user() {
		$response = array();
		//validate form input
		//		$this->form_validation->set_rules('user_name', 'User name', 'required|xss_clean|is_unique[users.username]');
		$this -> form_validation -> set_rules('user_mail', 'User mail', 'required|valid_email|is_unique[users.email]');
		$this -> form_validation -> set_rules('user_password', 'User password', 'required|min_length[' . $this -> config -> item('min_password_length', 'ion_auth') . ']|max_length[' . $this -> config -> item('max_password_length', 'ion_auth') . ']');
		$this -> form_validation -> set_rules('user_role', 'User role', 'required|xss_clean]');

		if ($this -> form_validation -> run() == true) {
			//			$username = strtolower($this->input->post('user_name'));
			$username = $this -> input -> post('user_name');
			$email = $this -> input -> post('user_mail');
			$password = $this -> input -> post('user_password');
			$customers = $this -> input -> post('user_customers');
			$group = array($this -> input -> post('user_role'));
			$additional_data = array();
			$active = $this -> input -> post('user_active');
			$new_id = $this -> ion_auth -> register($username, $password, $email, $additional_data, $group);
			if ($new_id) {
				$this -> load -> model('users_to_customers_model');
				foreach ($customers as $customer) {
					$this -> users_to_customers_model -> set($new_id, $customer);
				}
				if ((empty($active))) {
					$this -> ion_auth -> deactivate($new_id);
				}
				$response['success'] = 1;
				$response['message'] = 'User created successfully';
				$this -> output -> set_content_type('application/json') -> set_output(json_encode($response));
			}
		} else {
			$response['message'] = validation_errors();
			$this -> output -> set_content_type('application/json') -> set_output(json_encode($response));
		}
	}

	public function save_roles() {
		$roles = array();
		$response = array();

		foreach ($_POST as $checkbox_name => $checkbox_value) {
			$arr = explode('_', $checkbox_name);
			if ($arr[0] != 'job') {
				$roles[$arr[1]][] = $arr[0];
			} else {
				$roles[$arr[2]][] = $arr[0] . '_' . $arr[1];
			}

		}
		foreach ($roles as $key => $value) {
			$this -> ion_auth -> set_default_tab_to_group($key, $this -> input -> post('default_' . $key));
			$deny_controllers = array_diff($this -> data['checked_controllers'], $value);
			if ($key !== 1) {
				$deny_controllers = array_merge($deny_controllers, $this -> data['admin_controllers']);
			}
			$saving_errors = $this -> ion_auth -> set_rules_to_group($key, $deny_controllers);
		}

		if (empty($saving_errors)) {
			$response['success'] = 1;
			$response['message'] = 'Roles saved successfully';
		} else {
			$response['message'] = $saving_errors;
		}

		$this -> output -> set_content_type('application/json') -> set_output(json_encode($response));
	}

	public function jqueryAutocomplete() {
		$userQuery = $this -> input -> get('term');
		$searchColumn = $this -> input -> get('column');
		$columns = array('username', 'email');
		if (in_array($searchColumn, $columns)) {
			$answer = $this -> ion_auth -> getUserLike($searchColumn, $userQuery);
			$response = array();
			foreach ($answer as $row) {
				$response[] = array('id' => $row['id'], 'value' => $row[$searchColumn]);
			}
			$this -> output -> set_content_type('application/json') -> set_output(json_encode($response));
		}
	}

	public function update_user() {
		$this -> load -> model('users_to_customers_model');
		$this -> load -> model('user_groups_model');
		$response = array();
		$response['success'] = 1;
		$new_data = array();
		$user_id = $this -> input -> post('user_id');
		$old_user_info = $this -> ion_auth -> user($user_id) -> result_array();
		$old_user_group = $this -> user_groups_model -> getRoleByUserId($user_id);
		$customers = $this -> users_to_customers_model -> getByUserId($user_id);
		$old_customers = array();
		foreach ($customers as $customer) {
			$old_customers[] = $customer -> customer_id;
		}

		if ($old_user_info[0]['username'] != $this -> input -> post('user_name')) {
			//			$this->form_validation->set_rules('user_name', 'User name', 'required|xss_clean|is_unique[users.username]');
			//			$new_data['username'] = strtolower($this->input->post('user_name'));
			$new_data['username'] = $this -> input -> post('user_name');
		}

		if ($old_user_info[0]['email'] != $this -> input -> post('user_mail')) {
			$this -> form_validation -> set_rules('user_mail', 'User mail', 'required|valid_email|is_unique[users.email]');
			$new_data['email'] = $this -> input -> post('user_mail');
		}

		$new_password = $this -> input -> post('user_password');
		if (!empty($new_password)) {
			$this -> form_validation -> set_rules('user_password', 'User password', 'required|min_length[' . $this -> config -> item('min_password_length', 'ion_auth') . ']|max_length[' . $this -> config -> item('max_password_length', 'ion_auth') . ']');
			$new_data['password'] = $this -> input -> post('user_password');
		}

		$this -> form_validation -> set_rules('user_role', 'User role', 'required|xss_clean]');

		if ($this -> form_validation -> run() == true) {
			$new_customers = $this -> input -> post('user_customers');
			$new_group = $this -> input -> post('user_role');
			$active = $this -> input -> post('user_active');

			if (!empty($new_data)) {
				$this -> ion_auth -> update($user_id, $new_data);
			}

			if ($old_user_group[0] -> group_id != $new_group) {
				$this -> ion_auth -> remove_from_group($old_user_group[0] -> group_id, $user_id);
				$this -> ion_auth -> add_to_group($new_group, $user_id);
			}

			$add_customers = array_diff($new_customers, $old_customers);
			$delete_customers = array_diff($old_customers, $new_customers);

			if (empty($new_customers)) {
				foreach ($old_customers as $customer) {
					$this -> users_to_customers_model -> delete($user_id, $customer);
				}
			}
			if (!empty($add_customers)) {
				foreach ($add_customers as $customer) {
					$this -> users_to_customers_model -> set($user_id, $customer);
				}
			}
			if (!empty($delete_customers)) {
				foreach ($delete_customers as $customer) {
					$this -> users_to_customers_model -> delete($user_id, $customer);
				}
			}

			if ((empty($active))) {
				$this -> ion_auth -> deactivate($user_id);
			} else {
				$this -> ion_auth -> activate($user_id);
			}

			$response['message'] = 'User updated successfully';
			$this -> output -> set_content_type('application/json') -> set_output(json_encode($response));
		} else {
			$response['success'] = false;
			$response['message'] = validation_errors();
			$this -> output -> set_content_type('application/json') -> set_output(json_encode($response));
		}
	}

	public function upload_departments_categories() {
		ini_set('post_max_size', '100M');
		$this -> load -> library('UploadHandler');
		$this -> output -> set_content_type('application/json');
		$this -> uploadhandler -> upload(array('script_url' => site_url('system/upload_departments_categories'), 'upload_dir' => $this -> config -> item('csv_upload_dir'), 'param_name' => 'files', 'delete_type' => 'POST', 'accept_file_types' => '/.+\.(txt|jl)$/i', ));
	}

	public function save_departments_categories() {
		$this -> load -> helper('file');
		$this -> load -> model('department_model');
		$this -> load -> model('department_members_model');
		$this -> load -> model('site_categories_model');
		session_start();
		$filespath = realpath(base_url()) . "jl_import_dir";
		if (!file_exists($filespath)) {
			mkdir($filespath);
		}
		if (isset($_SESSION['mpost'])) {//$this->uri->segment(n)
			$_POST['site_id'] = $_SESSION['mpost']['site_id'];
			$_POST['site_name'] = $_SESSION['mpost']['site_name'];
		} else {
			$file = $this -> config -> item('csv_upload_dir') . $this -> input -> post('choosen_file');
			$fcont = file($file);
			$i = 1;
			$fnum = 0;
			$fobj = '';
			foreach ($fcont as $line) {
				if (!file_exists($filespath . '/temp_imp_jl_' . $fnum . '.jl')) {
					file_put_contents($filespath . '/temp_imp_jl_' . $fnum . '.jl', $line);
					$fobj = fopen($filespath . '/temp_imp_jl_' . $fnum . '.jl', 'a');
				} else
					fwrite($fobj, $line);
				if ($i == 500) {
					++$fnum;
					$i = 0;
					fclose($fobj);
				}
				++$i;
			}
			/*
			 $handle = fopen($file, "rb");
			 $content = fread($handle, filesize($file));
			 $mj_obj = json_decode('['.trim($content,'"').']');
			 if(!empty($mj_obj)){
			 $num = 1;
			 $file_num=0;
			 $tarray = array();
			 foreach ($mj_obj as $oj){
			 $tarray[]=$oj;
			 if($num==500){
			 $nstr = str_replace('\\/','/',json_encode($tarray));
			 $sl = strlen($nstr);
			 $nc = substr($nstr, 1,$sl-2);
			 //$nc = trim(trim(,'['),']');
			 file_put_contents($filespath.'/temp_imp_jl_'.$file_num.'.jl', $nc);
			 ++$file_num;
			 $tarray = array();
			 $num = 0;
			 }
			 ++$num;
			 }
			 if(!empty($tarray)){
			 $nstr = str_replace('\\/','/',json_encode($tarray));
			 $sl = strlen($nstr);
			 $nc = substr($nstr, 1,$sl-2);
			 file_put_contents($filespath.'/temp_imp_jl_'.$file_num.'.jl', $nc);
			 }
			 }
			 //*/
		}
		$site_id = $this -> input -> post('site_id');
		$site_name = explode(".", strtolower($this -> input -> post('site_name')));
		$sited = implode('/', $site_name);
		$call_link = base_url() . "crons/save_departments_categories/$site_id/$sited";
		// > /dev/null 2>/dev/null &";
		//echo $call_link;
		$this -> site_categories_model -> curl_async($call_link);
		// $string = shell_exec("wget -S -O- ".$call_link);
		exit($call_link . ' ' . $string);
		//$file = $this->config->item('csv_upload_dir').$this->input->post('choosen_file');
		$flist = get_filenames($filespath);
		if (empty($flist)) {
			unset($_SESSION['mpost']);
			return;
		}
		//exit;
		$file = $filespath . '/' . $flist[0];
		$_rows = array();
		//        $handle = fopen($file, "rb");
		//        $contents = fread($handle, filesize($file));
		//        fclose($handle);

		$cfile = file($file);
		//$data = '['.trim($contents,'"').']';
		//$json_obj = json_decode($data);

		$debug_stack = array('department_members' => array(), 'site_categories' => array());

		// new change 1 line
		set_time_limit(1000);
		foreach ($cfile as $line) {
			$line = rtrim(trim($line), ',');
			$row = json_decode($line);
			// === DB table decision (start)
			$level = '';
			$work_table = "";
			if (isset($row -> level) && $row -> level !== NULL && $row -> level !== '') {
				$level = $row -> level;
				if ($level >= 1) {
					$work_table = 'department_members';
				} else {
					$work_table = 'site_categories';
				}
			}
			// === DB table decision (end)

			// === all possible values and default values (start)
			$special = 0;
			$department_text = "";
			$url = "";
			$text = "";
			$department_url = "";
			$description_title = "";
			$keyword_count = "";
			$description_wc = 0;
			$description_text = "";
			$keyword_density = "";
			$nr_products = 0;
			$parent_url = "";
			$parent_text = "";

			if (isset($row -> special) && $row -> special != '' && !is_null($row -> special)) {
				$special = $row -> special;
			}
			if (isset($row -> department_text) && is_array($row -> department_text)) {
				$department_text = $row -> department_text[0];
			} else if (isset($row -> department_text) && !is_array($row -> department_text) && !is_null($row -> department_text) && $row -> department_text != '') {
				$department_text = $row -> department_text;
			}
			if (isset($row -> url) && is_array($row -> url)) {
				$url = addslashes($row -> url[0]);
			} else if (isset($row -> url) && !is_array($row -> url) && !is_null($row -> url)) {
				$url = addslashes($row -> url);
			}
			if (isset($row -> text) && is_array($row -> text)) {
				$text = $row -> text[0];
			} else if (isset($row -> text) && !is_array($row -> text) && !is_null($row -> text)) {
				$text = $row -> text;
			}
			if (isset($row -> department_url) && !is_null($row -> department_url) && $row -> department_url != '') {
				$department_url = addslashes($row -> department_url);
			}
			if (isset($row -> description_title) && is_array($row -> description_title)) {
				$description_title = $row -> description_title[0];
			} else if (isset($row -> description_title) && !is_array($row -> description_title) && !is_null($row -> description_title) && $row -> description_title != '') {
				$description_title = $row -> description_title;
			}
			if (isset($row -> keyword_count) && is_array($row -> keyword_count)) {
				$keyword_count = $row -> keyword_count[0];
			} else if (isset($row -> keyword_count) && !is_array($row -> keyword_count) && !is_null($row -> keyword_count) && $row -> keyword_count != '') {
				$keyword_count = json_encode($row -> keyword_count);
			}
			if (isset($row -> description_wc) && is_array($row -> description_wc)) {
				$description_wc = $row -> description_wc[0];
			} else if (isset($row -> description_wc) && !is_array($row -> description_wc) && !is_null($row -> description_wc) && $row -> description_wc != '') {
				$description_wc = $row -> description_wc;
			}
			if (isset($row -> description_text) && is_array($row -> description_text)) {
				$description_text = $row -> description_text[0];
			} else if (isset($row -> description_text) && !is_array($row -> description_text) && !is_null($row -> description_text) && $row -> description_text != '') {
				$description_text = $row -> description_text;
			}
			if (isset($row -> keyword_density) && is_array($row -> keyword_density)) {
				$keyword_density = $row -> keyword_density[0];
			} else if (isset($row -> keyword_density) && !is_array($row -> keyword_density) && !is_null($row -> keyword_density) && $row -> keyword_density != '') {
				$keyword_density = json_encode($row -> keyword_density);
			}
			if (isset($row -> nr_products) && is_array($row -> nr_products)) {
				$nr_products = $row -> nr_products[0];
			} else if (isset($row -> nr_products) && !is_array($row -> nr_products) && !is_null($row -> nr_products) && $row -> nr_products != '') {
				$nr_products = $row -> nr_products;
			}
			if (isset($row -> parent_url) && is_array($row -> parent_url)) {
				$parent_url = addslashes($row -> parent_url[0]);
			} else if (isset($row -> parent_url) && !is_array($row -> parent_url) && !is_null($row -> parent_url) && $row -> parent_url != '') {
				$parent_url = addslashes($row -> parent_url);
			}
			if (isset($row -> parent_text) && is_array($row -> parent_text)) {
				$parent_text = $row -> parent_text[0];
			} else if (isset($row -> parent_text) && !is_array($row -> parent_text) && !is_null($row -> parent_text) && $row -> parent_text != '') {
				$parent_text = $row -> parent_text;
			}
			// === all possible values and default values (end)

			if ($work_table != "") {// === work table define, ok, otherwise !!! DO NOTHING !!!
				// ==== 'department_members' DB table actions stuffs (start)
				if ($work_table == 'department_members') {
					// === debuging stack (start)
					$debug_stack_mid = array('status' => 'department_members', 'department_text' => $department_text, 'url' => $url, 'text' => $text, 'department_url' => $department_url, 'description_title' => $description_title, 'keyword_count' => $keyword_count, 'description_wc' => $description_wc, 'description_text' => $description_text, 'keyword_density' => $keyword_density, 'department_id' => null, 'check_id' => null, 'department_members_model_insert_id' => null, 'department_members_model_up_flag' => null, 'department_members_model_update' => null);
					// === debuging stack (end)

					// === insert / update decisions stuffs (start)
					try {
						$check_department_id = $this -> department_model -> checkExist($department_text);
					} catch(Exception $e) {
						echo 'Error: ', $e -> getMessage(), "\n";
						$this -> statistics_model -> db -> close();
						$this -> statistics_model -> db -> initialize();
						$check_department_id = $this -> department_model -> checkExist($department_text);
					}
					if ($check_department_id == false) {
						try {
							$department_id = $this -> department_model -> insert($department_text, $department_text);
						} catch(Exception $e) {
							$this -> department_model -> db -> close();
							$this -> department_model -> db -> initialize();
							$department_id = $this -> department_model -> insert($department_text, $department_text);
						}
					} else {
						$department_id = $check_department_id;
					}
					$debug_stack_mid['department_id'] = $department_id;
					$parent_id = 0;
					try {
						$check_id = $this -> department_members_model -> checkExist($site_id, $department_text, $url);
					} catch(Exception $e) {
						$this -> department_members_model -> db -> close();
						$this -> department_members_model -> db -> initialize();
						$check_id = $this -> department_members_model -> checkExist($site_id, $department_text, $url);
					}
					$debug_stack_mid['check_id'] = $check_id;
					if ($check_id == false) {
						try {
							$department_members_model_insert_id = $this -> department_members_model -> insert($parent_id, $site_id, $department_id, $department_text, $url, $description_wc, $description_text, $keyword_count, $keyword_density, $description_title, $level);
						} catch(Exception $e) {
							$this -> department_members_model -> db -> close();
							$this -> department_members_model -> db -> initialize();
							$department_members_model_insert_id = $this -> department_members_model -> insert($parent_id, $site_id, $department_id, $department_text, $url, $description_wc, $description_text, $keyword_count, $keyword_density, $description_title, $level);
						}
						$debug_stack_mid['department_members_model_insert_id'] = $department_members_model_insert_id;
					} else {
						try {
							$department_members_model_up_flag = $this -> department_members_model -> updateFlag($site_id, $department_text);
						} catch(Exception $e) {
							$this -> department_members_model -> db -> close();
							$this -> department_members_model -> db -> initialize();
							$department_members_model_up_flag = $this -> department_members_model -> updateFlag($site_id, $department_text);
						}
						$debug_stack_mid['department_members_model_up_flag'] = $department_members_model_up_flag;
						try {
							$department_members_model_update = $this -> department_members_model -> update($check_id, $department_id, $description_wc, $description_text, $keyword_count, $keyword_density, $description_title, $level);
						} catch(Exception $e) {
							$this -> department_members_model -> db -> close();
							$this -> department_members_model -> db -> initialize();
							$department_members_model_update = $this -> department_members_model -> update($check_id, $department_id, $description_wc, $description_text, $keyword_count, $keyword_density, $description_title, $level);
						}
						$debug_stack_mid['department_members_model_update'] = $department_members_model_update;
					}
					// === insert / update decisions stuffs (end)
					$debug_stack['department_members'][] = $debug_stack_mid;
				}
				// ==== 'department_members' DB table actions stuffs (end)

				// ==== 'site_categories' DB table actions stuffs (start)
				if ($work_table == 'site_categories') {
					$department_members_id = 0;
					if ($department_text != '') {
						try {
							$check_id = $this -> department_members_model -> checkExist($site_id, $department_text);
						} catch(Exception $e) {
							$this -> department_members_model -> db -> close();
							$this -> department_members_model -> db -> initialize();
							$check_id = $this -> department_members_model -> checkExist($site_id, $department_text);
						}
						if ($check_id) {
							$department_members_id = $check_id;
						}
					}
					// === debuging stack (start)
					$debug_stack_mid = array('status' => 'site_categories', 'nr_products' => $nr_products, 'url' => $url, 'text' => $text, 'department_url' => $department_url, 'description_wc' => $description_wc, 'parent_url' => $parent_url, 'parent_text' => $parent_text, 'department_text' => $department_text, 'parent_id' => 0, 'site_categories_model_update_flag_one' => null, 'department_members_id' => $department_members_id, 'check_site' => null, 'site_categories_model_insert' => null, 'site_categories_model_update_flag_two' => null, 'description_text' => $description_text, 'keyword_count' => $keyword_count, 'keyword_density' => $keyword_density, 'description_title' => $description_title);
					// === debuging stack (end)

					// === insert / update decisions stuffs (start)
					$parent_id = 0;
					if ($parent_text != '') {
						try {
							$parent_id = $this -> site_categories_model -> checkExist($site_id, $parent_text);
						} catch(Exception $e) {
							$this -> site_categories_model -> db -> close();
							$this -> site_categories_model -> db -> initialize();
							$parent_id = $this -> site_categories_model -> checkExist($site_id, $parent_text);
						}
						if ($parent_id == false) {
							try {
								$parent_id = $this -> site_categories_model -> insert(0, $site_id, $text, $url, $special, $parent_text, $department_members_id, $nr_products, $description_wc, $keyword_count, $keyword_density, $description_title, $description_text, $level);
							} catch(Exception $e) {
								$this -> site_categories_model -> db -> close();
								$this -> site_categories_model -> db -> initialize();
								$parent_id = $this -> site_categories_model -> insert(0, $site_id, $text, $url, $special, $parent_text, $department_members_id, $nr_products, $description_wc, $keyword_count, $keyword_density, $description_title, $description_text, $level);
							}
							$debug_stack_mid['parent_id'] = $parent_id;
						} else {
							try {
								$site_categories_model_update_flag_one = $this -> site_categories_model -> updateFlag($site_id, $parent_text, $department_members_id);
							} catch(Exception $e) {
								$this -> site_categories_model -> db -> close();
								$this -> site_categories_model -> db -> initialize();
								$site_categories_model_update_flag_one = $this -> site_categories_model -> updateFlag($site_id, $parent_text, $department_members_id);
							}
							$debug_stack_mid['site_categories_model_update_flag_one'] = $site_categories_model_update_flag_one;
						}
					}

					if ($parent_id != 0 && $department_members_id == 0) {
						$res = $this -> site_categories_model -> checkDepartmentId($parent_id);
						$department_members_id = $res -> department_members_id;
						$debug_stack_mid['department_members_id'] = $department_members_id;
					}

					if ($text != '') {
						try {
							$check_site = $this -> site_categories_model -> checkExist($site_id, $text, $department_members_id);
						} catch(Exception $e) {
							$this -> site_categories_model -> db -> close();
							$this -> site_categories_model -> db -> initialize();
							$check_site = $this -> site_categories_model -> checkExist($site_id, $text, $department_members_id);
						}
						$debug_stack_mid['check_site'] = $check_site;
						if ($check_site == false) {
							try {
								$site_categories_model_insert = $this -> site_categories_model -> insert($parent_id, $site_id, $text, $url, $special, $parent_text, $department_members_id, $nr_products, $description_wc, $keyword_count, $keyword_density, $description_title, $description_text, $level);
							} catch(Exception $e) {
								$this -> site_categories_model -> db -> close();
								$this -> site_categories_model -> db -> initialize();
								$site_categories_model_insert = $this -> site_categories_model -> insert($parent_id, $site_id, $text, $url, $special, $parent_text, $department_members_id, $nr_products, $description_wc, $keyword_count, $keyword_density, $description_title, $description_text, $level);
							}
							$debug_stack_mid['site_categories_model_insert'] = $site_categories_model_insert;
						} else {
							try {
								$site_categories_model_update_flag_two = $this -> site_categories_model -> updateFlag($site_id, $text, $department_members_id);
							} catch(Exception $e) {
								$this -> site_categories_model -> db -> close();
								$this -> site_categories_model -> db -> initialize();
								$site_categories_model_update_flag_two = $this -> site_categories_model -> updateFlag($site_id, $text, $department_members_id);
							}
							$debug_stack_mid['site_categories_model_update_flag_two'] = $site_categories_model_update_flag_two;
						}
					}
					// === insert / update decisions stuffs (end)
					$debug_stack['site_categories'][] = $debug_stack_mid;
				}
				// ==== 'site_categories' DB table actions stuffs (end)

			}

		}
		unlink($file);
		if (count($flist) > 1) {
			$call_link = base_url() . "crons/save_departments_categories/$site_id/$site_name > /dev/null 2>/dev/null &";
			//echo $call_link;
			shell_exec("wget -S -O- " . $call_link);
			//          shell_exec("wget -S -O- ".  base_url()."system/save_department_categories > /dev/null 2>/dev/null &");
		}
		//        else{
		//unset($_SESSION['mpost']);
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($debug_stack));
	}

	public function save_departments_categories_old() {
		$this -> load -> model('department_model');
		$this -> load -> model('department_members_model');
		$this -> load -> model('site_categories_model');
		$site_id = $this -> input -> post('site_id');
		$site_name = explode(".", strtolower($this -> input -> post('site_name')));
		$file = $this -> config -> item('csv_upload_dir') . $this -> input -> post('choosen_file');
		$_rows = array();
		$handle = fopen($file, "rb");
		$contents = fread($handle, filesize($file));
		fclose($handle);

		$data = '[' . trim($contents, '"') . ']';
		$json_obj = json_decode($data);

		$highest_level = $json_obj[0] -> level;
		foreach ($json_obj as $key => $one) {
			if ((int)$highest_level <= (int)$one -> level)
				$highest_level = $one -> level;
		}

		foreach ($json_obj as $row) {
			$special = 0;
			$parent_text = '';
			$department_text = '';
			$text = '';
			$url = '';
			$nr_products = 0;
			$description_wc = 0;
			$description_text = '';
			$keyword_density = '';
			$keyword_count = '';
			$description_title = '';
			$level = '';

			if ($row -> level == $highest_level) {
				if (isset($row -> level) && !is_null($row -> level) && $row -> level != '') {
					$level = $row -> level;
				}
				if (isset($row -> url) && !is_null($row -> url) && $row -> url != '') {
					$url = addslashes($row -> url);
				}
				if (isset($row -> description_wc) && is_array($row -> description_wc)) {
					$description_wc = $row -> description_wc[0];
				} else if (isset($row -> description_wc) && !is_array($row -> description_wc) && !is_null($row -> description_wc) && $row -> description_wc != '') {
					$description_wc = $row -> description_wc;
				}
				if (isset($row -> department_text) && is_array($row -> department_text)) {
					$department_text = $row -> department_text[0];
				} else if (isset($row -> department_text) && !is_array($row -> department_text) && !is_null($row -> department_text) && $row -> department_text != '') {
					$department_text = $row -> department_text;
				}
				if (isset($row -> keyword_density) && is_array($row -> keyword_density)) {
					$keyword_density = $row -> keyword_density[0];
				} else if (isset($row -> keyword_density) && !is_array($row -> keyword_density) && !is_null($row -> keyword_density) && $row -> keyword_density != '') {
					$keyword_density = json_encode($row -> keyword_density);
				}
				if (isset($row -> keyword_count) && is_array($row -> keyword_count)) {
					$keyword_count = $row -> keyword_count[0];
				} else if (isset($row -> keyword_count) && !is_array($row -> keyword_count) && !is_null($row -> keyword_count) && $row -> keyword_count != '') {
					$keyword_count = json_encode($row -> keyword_count);
				}
				if (isset($row -> description_title) && is_array($row -> description_title)) {
					$description_title = $row -> description_title[0];
				} else if (isset($row -> description_title) && !is_array($row -> description_title) && !is_null($row -> description_title) && $row -> description_title != '') {
					$description_title = $row -> description_title;
				}
				if (isset($row -> description_text) && is_array($row -> description_text)) {
					$description_text = $row -> description_text[0];
				} else if (isset($row -> description_text) && !is_array($row -> description_text) && !is_null($row -> description_text) && $row -> description_text != '') {
					$description_text = $row -> description_text;
				}
				$check_department_id = $this -> department_model -> checkExist($department_text);
				if ($check_department_id == false) {
					$department_id = $this -> department_model -> insert($department_text, $department_text);
				} else {
					$department_id = $check_department_id;
				}
				$parent_id = 0;
				if ($parent_text != '') {
					$parent_id = $this -> department_members_model -> checkExist($site_id, $department_text, $url);
					if ($parent_id == false) {
						$parent_id = $this -> department_members_model -> insert(0, $site_id, $department_id, $department_text, $url, $description_wc, $description_text, $keyword_count, $keyword_density, $description_title, $level);
					} else {
						$this -> department_members_model -> updateFlag($site_id, $department_text);
					}
				}
				$check_id = $this -> department_members_model -> checkExist($site_id, $department_text, $url);
				if ($check_id == false) {
					$this -> department_members_model -> insert($parent_id, $site_id, $department_id, $department_text, $url, $description_wc, $description_text, $keyword_count, $keyword_density, $description_title, $level);
				} else {
					$this -> department_members_model -> updateFlag($site_id, $department_text);
					$this -> department_members_model -> update($check_id, $department_id, $description_wc, $description_text, $keyword_count, $keyword_density, $description_title, $level);
				}
			}
		}
		foreach ($json_obj as $row_data) {
			$special = 0;
			$parent_text = '';
			$department_text = '';
			$text = '';
			$url = '';
			$nr_products = 0;
			$description_wc = 0;
			$description_text = '';
			$keyword_count = '';
			$keyword_density = '';
			$description_title = '';
			$level = 0;

			if ($row_data -> level < $highest_level) {
				if ($row_data -> special != '' && !is_null($row_data -> special)) {
					$special = $row_data -> special;
				}
				if (isset($row_data -> parent_text) && is_array($row_data -> parent_text)) {
					$parent_text = $row_data -> parent_text[0];
				} else if (isset($row_data -> parent_text) && !is_array($row_data -> parent_text) && !is_null($row_data -> parent_text) && $row_data -> parent_text != '') {
					$parent_text = $row_data -> parent_text;
				}
				if (isset($row_data -> department_text) && is_array($row_data -> department_text)) {
					$department_text = $row_data -> department_text[0];
				} else if (isset($row_data -> department_text) && !is_array($row_data -> department_text) && !is_null($row_data -> department_text) && $row_data -> department_text != '') {
					$department_text = $row_data -> department_text;
				}
				if (isset($row_data -> text) && is_array($row_data -> text)) {
					$text = $row_data -> text[0];
				} else if (isset($row_data -> text) && !is_array($row_data -> text) && !is_null($row_data -> text)) {
					$text = $row_data -> text;
				}
				if (isset($row_data -> url) && is_array($row_data -> url)) {
					$url = $row_data -> url[0];
				} else if (isset($row_data -> url) && !is_array($row_data -> url) && !is_null($row_data -> url)) {
					$url = $row_data -> url;
				}
				if (substr_count($url, 'http://') == 0 && $this -> input -> post('site_name') != '[Choose site]') {
					$url = str_replace('..', '', $url);
					$url = 'http://' . strtolower($this -> input -> post('site_name')) . $url;
				}

				$department_members_id = 0;
				if ($department_text != '') {
					$check_id = $this -> department_members_model -> checkExist($site_id, $department_text, $url);
					if ($check_id) {
						$department_members_id = $check_id;
					}
				}

				if (isset($row_data -> level) && is_array($row_data -> level)) {
					$level = $row_data -> level[0];
				} else if (isset($row_data -> level) && !is_array($row_data -> level) && !is_null($row_data -> level) && $row_data -> level != '') {
					$level = $row_data -> level;
				}
				if (isset($row_data -> nr_products) && is_array($row_data -> nr_products)) {
					$nr_products = $row_data -> nr_products[0];
				} else if (isset($row_data -> nr_products) && !is_array($row_data -> nr_products) && !is_null($row_data -> nr_products) && $row_data -> nr_products != '') {
					$nr_products = $row_data -> nr_products;
				}
				if (isset($row_data -> description_wc) && is_array($row_data -> description_wc)) {
					$description_wc = $row_data -> description_wc[0];
				} else if (isset($row_data -> description_wc) && !is_array($row_data -> description_wc) && !is_null($row_data -> description_wc) && $row_data -> description_wc != '') {
					$description_wc = $row_data -> description_wc;
				}
				if (isset($row_data -> description_text) && is_array($row_data -> description_text)) {
					$description_text = $row_data -> description_text[0];
				} else if (isset($row_data -> description_text) && !is_array($row_data -> description_text) && !is_null($row_data -> description_text) && $row_data -> description_text != '') {
					$description_text = $row_data -> description_text;
				}
				if (isset($row_data -> keyword_count) && is_array($row_data -> keyword_count)) {
					$keyword_count = $row_data -> keyword_count[0];
				} else if (isset($row_data -> keyword_count) && !is_array($row_data -> keyword_count) && !is_null($row_data -> keyword_count) && $row_data -> keyword_count != '') {
					$keyword_count = json_encode($row_data -> keyword_count);
				}
				if (isset($row_data -> keyword_density) && is_array($row_data -> keyword_density)) {
					$keyword_density = $row_data -> keyword_density[0];
				} else if (isset($row_data -> keyword_density) && !is_array($row_data -> keyword_density) && !is_null($row_data -> keyword_density) && $row_data -> keyword_density != '') {
					$keyword_density = json_encode($row_data -> keyword_density);
				}
				if (isset($row_data -> description_title) && is_array($row_data -> description_title)) {
					$description_title = $row_data -> description_title[0];
				} else if (isset($row_data -> description_title) && !is_array($row_data -> description_title) && !is_null($row_data -> description_title) && $row_data -> description_title != '') {
					$description_title = $row_data -> description_title;
				}
				$this -> load -> database();
				$parent_id = 0;
				if ($parent_text != '') {
					$parent_id = $this -> site_categories_model -> checkExist($site_id, $parent_text);
					if ($parent_id == false) {
						$parent_id = $this -> site_categories_model -> insert(0, $site_id, $text, $url, $special, $parent_text, $department_members_id, $nr_products, $description_wc, $keyword_count, $keyword_density, $description_title, $description_text, $level);
					} else {
						$this -> site_categories_model -> updateFlag($site_id, $parent_text, $department_members_id);
					}
				}

				if ($parent_id != 0 && $department_members_id == 0) {
					$res = $this -> site_categories_model -> checkDepartmentId($parent_id);
					$department_members_id = $res -> department_members_id;
				}

				if ($text != '') {
					$check_site = $this -> site_categories_model -> checkExist($site_id, $text, $department_members_id);
					if ($check_site == false) {
						$this -> site_categories_model -> insert($parent_id, $site_id, $text, $url, $special, $parent_text, $department_members_id, $nr_products, $description_wc, $keyword_count, $keyword_density, $description_title, $description_text, $level);
					} else {
						$this -> site_categories_model -> updateFlag($site_id, $text, $department_members_id);
					}
				}
			}
		}
		$response['message'] = 'File was added successfully';
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($response));
	}

	public function delete_department() {
		$this -> load -> model('department_members_model');
		$department_id = $this -> input -> post('id');
		$this -> department_members_model -> delete($department_id);

		$response['message'] = 'Department was deleted successfully';
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($response));
	}

	public function delete_category() {
		$this -> load -> model('site_categories_model');
		$category_id = $this -> input -> post('id');
		$this -> site_categories_model -> delete($category_id);
		$response['message'] = 'Category was deleted successfully';
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($response));
	}

	public function delete_overall() {
		$this -> load -> model('best_sellers_model');
		$overall_id = $this -> input -> post('id');
		$this -> best_sellers_model -> delete($overall_id);
		$response['message'] = 'Overall was deleted successfully';
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($response));
	}

	public function delete_all() {
		$this -> load -> model('site_categories_model');
		$this -> load -> model('department_members_model');
		$this -> load -> model('best_sellers_model');
		$type = $this -> input -> post('type');
		$site_id = $this -> input -> post('site_id');
		//        $site_name = explode(".", $this->input->post('site_name'));
		if ($type == 'categories') {
			$this -> site_categories_model -> deleteAll($site_id);
			$response['message'] = 'Categories was deleted successfully';
		} elseif ($type == 'departments') {
			$this -> department_members_model -> deleteAll($site_id);
			$response['message'] = 'Departments was deleted successfully';
		} elseif ($type == 'overall') {
			$this -> best_sellers_model -> deleteAll($site_id);
			$response['message'] = 'Overall was deleted successfully';
		}

		$this -> output -> set_content_type('application/json') -> set_output(json_encode($response));
	}

	public function save_best_sellers() {
		$this -> load -> model('best_sellers_model');
		$this -> load -> model('sites_model');

		$site_id = $this -> input -> post('site_id');
		//        $site_name = explode(".", strtolower($this->input->post('site_name')));
		$file = $this -> config -> item('csv_upload_dir') . $this -> input -> post('overall_choosen_file');
		$_rows = array();
		if (($handle = fopen($file, "r")) !== FALSE) {
			while (($data = fgetcsv($handle, 1000, "\n")) !== FALSE) {
				if (!is_null($data[0]) && $data[0] != '') {
					$_rows[] = json_decode($data[0]);
				}
			}
			fclose($handle);
		}
		foreach ($_rows as $row) {
			$listprice = '';
			$brand = '';
			$department = '';
			$price = '';
			$page_title = '';
			$url = '';
			$rank = '';
			$list_name = '';
			$product_name = '';
			if (!is_null($row -> listprice)) {
				$listprice = $row -> listprice;
			}
			if (!is_null($row -> brand)) {
				$brand = $row -> brand;
			}
			if (!is_null($row -> department)) {
				$department = $row -> department;
			}
			if (!is_null($row -> price)) {
				$price = $row -> price;
			}
			if (!is_null($row -> page_title)) {
				$page_title = $row -> page_title;
			}
			if (!is_null($row -> url)) {
				$url = $row -> url;
			}
			if (!is_null($row -> rank)) {
				$rank = $row -> rank;
			}
			if (!is_null($row -> list_name)) {
				$list_name = $row -> list_name;
			}
			if (!is_null($row -> product_name)) {
				$product_name = $row -> product_name;
			}
			if ($page_title != '') {
				$this -> best_sellers_model -> insert($site_id, $page_title, $url, $brand, $rank, $department, $price, $list_name, $product_name, $listprice);
			}
		}
		$response['message'] = 'File was added successfully';
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($response));
	}

	public function upload_email_logo() {
		$this -> load -> model('webshoots_model');
		$status = "";
		$msg = "";
		$file_element_name = 'logoemail';
		$filename = "";

		if ($status != "error") {
			$up_path = realpath(BASEPATH . "../webroot/emails_logos/");
			$config['upload_path'] = $up_path;
			$config['allowed_types'] = 'gif|jpg|png|jpeg';
			$config['max_size'] = 1024 * 8;
			$config['encrypt_name'] = TRUE;

			$this -> load -> library('upload', $config);

			if (!$this -> upload -> do_upload($file_element_name)) {
				$status = 'error';
				$msg = $this -> upload -> display_errors('', '');
			} else {
				$data = $this -> upload -> data();
				$filename = $data['file_name'];
				$this -> webshoots_model -> updateHomePagesConfig('logo', $filename);
				$status = "success";
				$msg = "File successfully uploaded";
			}
			@unlink($_FILES[$file_element_name]);
		}
		$this -> output -> set_content_type('application/json') -> set_output(json_encode(array('status' => $status, 'msg' => $msg, 'filename' => $filename)));
	}

	public function upload_csv() {
		$this -> load -> library('UploadHandler');

		$this -> output -> set_content_type('application/json');
		$this -> uploadhandler -> upload(array('script_url' => site_url('system/upload_csv'), 'upload_dir' => $this -> config -> item('csv_upload_dir'), 'param_name' => 'files', 'delete_type' => 'POST', 'accept_file_types' => '/.+\.csv$/i', ));
	}

	public function upload_img() {
		$this -> load -> library('UploadHandler');
		$this -> output -> set_content_type('application/json');

		$this -> uploadhandler -> upload(array('script_url' => site_url('system/upload_img'), 'upload_dir' => 'webroot/img/', 'param_name' => 'files', 'delete_type' => 'POST', 'accept_file_types' => '/.+\.(jpg|gif|png)$/i', ));
	}

	public function get_batch_review() {
		$this -> load -> model('batches_model');
		$results = $this -> batches_model -> getBatchReview();
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($results));
	}

	public function update_batch_review() {
		$this -> load -> model('batches_model');
		if (!empty($_POST)) {
			$id = $this -> input -> post('id');
			$title = $this -> input -> post('title');
			$this -> batches_model -> update($id, $title);
			echo 'Record updated successfully!';
		}
	}

	public function delete_batch_review() {
		$this -> load -> model('batches_model');
		$id = $this -> input -> post('id');
		if (is_null($id)) {
			echo 'ERROR: Id not provided.';
			return;
		}
		$this -> batches_model -> delete($id);
		echo 'Records deleted successfully';
	}

	public function getBatchById($id) {
		$this -> load -> model('batches_model');
		if (isset($id))
			echo json_encode($this -> batches_model -> get($id));
	}

	public function batch_review() {
		$this -> render();
	}

	public function scanForCatSnap() {
		$this -> load -> model('site_categories_model');
		$cat_id = $this -> input -> post('cat_id');
		$snap_data = $this -> site_categories_model -> getLatestCatScreen($cat_id);
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($snap_data));
	}

	public function scanForDepartmentSnap() {
		$this -> load -> model('department_members_model');
		$dep_id = $this -> input -> post('dep_id');
		$snap_data = $this -> department_members_model -> getLatestDepartmentScreen($dep_id);
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($snap_data));
	}

	public function getCategoriesBySiteId() {
		$this -> load -> model('site_categories_model');
		$this -> load -> model('department_members_model');
		$department_id = '';
		$snap_data = null;
		if ($this -> input -> post('department_id') != '') {
			$department_id = $this -> input -> post('department_id');
			$snap_data = $this -> department_members_model -> getLatestDepartmentScreen($department_id);
		}
		$result = $this -> site_categories_model -> getAllBySiteId($this -> input -> post('site_id'), $department_id);
		// $this->output->set_content_type('application/json')->set_output(json_encode($result)); // === OLD STUFF
		// === NEW STUFF (START)
		$res_data = array('result' => $result, 'snap_data' => $snap_data);
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($res_data));
		// === NEW STUFF (END)
	}

	public function getBestSellersBySiteId() {
		$this -> load -> model('best_sellers_model');
		$result = $this -> best_sellers_model -> getAllBySiteId($this -> input -> post('site_id'));
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($result));
	}

	public function category_list() {
		$this -> load -> model('site_categories_model');
		$categories = $this -> site_categories_model -> getAll();
		$category_list = array();
		foreach ($categories as $category) {
			array_push($category_list, $category -> text);
		}
		return $category_list;

	}

	private function category_list_new() {
		$this -> load -> model('site_categories_model');
		$categories = $this -> site_categories_model -> getAll();
		$category_list = array();
		/*foreach($categories as $category) {
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
		 }*/
		return $category_list;
	}

	//    public function system_sites_department_snap() {
	//    	$res = array(
	//    		'status' => false,
	//    		'snap' => '',
	//    		'msg' => '',
	//    		'site' => ''
	//    	);
	//    	$id = $this->input->post('id');
	//    	$this->load->model('webshoots_model');
	//    	$this->load->model('department_members_model');
	//    	$this->load->model('sites_model');
	//    	$department = $this->department_members_model->get($id);
	//
	//    	if(count($department) > 0) {
	//    		$dep = $department[0];
	//    		if(isset($dep->url) && trim($dep->url) !== "") {
	//    			$url = $dep->url;
	//    			$http_status = $this->webshoots_model->urlExistsCode($url);
	//    			if($http_status >= 200 && $http_status <= 302) {
	//    					$url = preg_replace('#^https?://#', '', $url);
	//	            $call_url = $this->webshoots_model->webthumb_call_link($url);
	//	            $snap_res = $this->webshoots_model->crawl_webshoot($call_url, $dep->id, 'sites_dep_snap-');
	//	            // ==== check image (if we need to repeat snap craw, but using snapito.com) (start)
	//	            $fs = filesize($snap_res['dir']);
	//	            if($fs === false || $fs < 10000) { // === so re-craw it
	//	            	@unlink($snap_res['dir']);
	//	            	$api_key = $this->config->item('snapito_api_secret');
	//	            	$call_url = "http://api.snapito.com/web/$api_key/mc/$url";
	//	    					$snap_res = $this->webshoots_model->crawl_webshoot($call_url, $dep->id, 'sites_dep_snap-');
	//	            }
	//	            // ==== check image (if we need to repeat snap craw, but using snapito.com) (end)
	//	            $res_insert = $this->department_members_model->insertSiteDepartmentSnap($dep->id, $snap_res['img'], $snap_res['path'], $snap_res['dir'], $http_status);
	//			    		if($res_insert > 0) {
	//			    			$res['snap'] = $snap_res['path'];
	//			    			$res['site'] = $url;
	//			    			$res['status'] = true;
	//			    			$res['msg'] = 'Ok';
	//			    		}
	//    			} else {
	//    				$res['site'] = $url;
	//    				$res['msg'] = "Department url is unreachable. Snapshot attempt is canceled. HTTP STATUS: $http_status";
	//    			}
	//    		} else {
	//    			$res['msg'] = "Url field is empty DB. Unable to process snapshot process";
	//    		}
	//    	} else {
	//    		$res['msg'] = "Such department don't exists in DB. Snapshot attempt is canceled.";
	//    	}
	//    	$this->output->set_content_type('application/json')->set_output(json_encode($res));
	//    }

	public function system_sites_department_snaps() {
		$ids = $this -> input -> post('ids');
		$this -> load -> model('webshoots_model');
		$this -> load -> model('department_members_model');
		$this -> load -> model('sites_model');
		$this -> load -> model('snapshot_queue_model');
		$this -> load -> model('snapshot_queue_list_model');

		$this -> snapshot_queue_model -> insertCount(count($ids));

		foreach ($ids as $id) {
			$res[$id] = array('status' => false, 'snap' => '', 'msg' => '', 'site' => '');
			$department = $this -> department_members_model -> get($id);

			if (count($department) > 0) {
				$dep = $department[0];
				if (isset($dep -> url) && trim($dep -> url) !== "") {
					$url = $dep -> url;
					$http_status = $this -> webshoots_model -> urlExistsCode($url);
					if ($http_status >= 200 && $http_status <= 302 || $http_status == 400) {
						$url = preg_replace('#^https?://#', '', $url);
						$call_url = $this -> webshoots_model -> webthumb_call_link($url);
						$snap_res = $this -> webshoots_model -> crawl_webshoot($call_url, $dep -> id, 'sites_dep_snap-');
						// ==== check image (if we need to repeat snap craw, but using snapito.com) (start)
						$fs = filesize($snap_res['dir']);
						if ($fs === false || $fs < 10000) {// === so re-craw it
							@unlink($snap_res['dir']);
							$api_key = $this -> config -> item('snapito_api_secret');
							$call_url = "http://api.snapito.com/web/$api_key/mc/$url";
							$snap_res = $this -> webshoots_model -> crawl_webshoot($call_url, $dep -> id, 'sites_dep_snap-');
						}
						// ==== check image (if we need to repeat snap craw, but using snapito.com) (end)
						$res_insert = $this -> department_members_model -> insertSiteDepartmentSnap($dep -> id, $snap_res['img'], $snap_res['path'], $snap_res['dir'], $http_status);
						if ($res_insert > 0) {
							$res[$id]['snap'] = $snap_res['path'];
							$res[$id]['site'] = $url;
							$res[$id]['status'] = true;
							$res[$id]['msg'] = 'Ok';
						}
					} else {
						$res[$id]['site'] = $url;
						$res[$id]['msg'] = "Department url is unreachable. Snapshot attempt is canceled. HTTP STATUS: $http_status";
					}
					$this -> snapshot_queue_list_model -> deleteByDepId($dep -> id);
				} else {
					$res[$id]['msg'] = "Url field is empty DB. Unable to process snapshot process";
				}
			} else {
				$res[$id]['msg'] = "Such department don't exists in DB. Snapshot attempt is canceled.";
			}
			$this -> snapshot_queue_model -> updateCount();
		}
		$this -> snapshot_queue_model -> deleteCount();
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($res));
	}

	public function department_snaps_ajax() {
		if (isset($_POST['ajax'])) {
			$this -> load -> model('snapshot_queue_model');
			$result = $this -> snapshot_queue_model -> checkCount();
			echo json_encode($result);
		}
	}

	// public function system_sites_department_snap() {
	// 	$res = array(
	// 		'status' => false,
	// 		'snap' => '',
	// 		'msg' => '',
	// 		'site' => ''
	// 	);
	// 	$id = $this->input->post('id');
	// 	$this->load->model('webshoots_model');
	// 	$this->load->model('department_members_model');
	// 	$this->load->model('sites_model');
	// 	$department = $this->department_members_model->get($id);

	// 	if(count($department) > 0) {
	// 		$dep = $department[0];
	// 		$site_id = $dep->site_id;
	// 		$site = $this->sites_model->get($site_id);
	// 		if(count($site) > 0) {
	// 			$site = $site[0];
	// 			$url = $site->url;
	// 			$http_status = $this->webshoots_model->urlExistsCode($url);
	// 			if($http_status >= 200 && $http_status <= 302) {
	// 					$url = preg_replace('#^https?://#', '', $url);
	//          $call_url = $this->webshoots_model->webthumb_call_link($url);
	//          $snap_res = $this->webshoots_model->crawl_webshoot($call_url, $dep->id, 'sites_dep_snap-');
	//          // ==== check image (if we need to repeat snap craw, but using snapito.com) (start)
	//          $fs = filesize($snap_res['dir']);
	//          if($fs === false || $fs < 10000) { // === so re-craw it
	//          	@unlink($snap_res['dir']);
	//          	$api_key = $this->config->item('snapito_api_secret');
	//          	$call_url = "http://api.snapito.com/web/$api_key/mc/$url";
	//  					$snap_res = $this->webshoots_model->crawl_webshoot($call_url, $dep->id, 'sites_dep_snap-');
	//          }
	//          // ==== check image (if we need to repeat snap craw, but using snapito.com) (end)
	//          $res_insert = $this->department_members_model->insertSiteDepartmentSnap($dep->id, $snap_res['img'], $snap_res['path'], $snap_res['dir'], $http_status);
	//    		if($res_insert > 0) {
	//    			$res['snap'] = $snap_res['path'];
	//    			$res['site'] = $url;
	//    			$res['status'] = true;
	//    			$res['msg'] = 'Ok';
	//    		}
	// 			} else {
	// 				$res['site'] = $url;
	// 				$res['msg'] = "Department url is unreachable. Snapshot attempt is canceled. HTTP STATUS: $http_status";
	// 			}
	// 		} else {
	// 			$res['msg'] = "Such site don't exists in DB. Snapshot attempt is canceled.";
	// 		}
	// 	} else {
	// 		$res['msg'] = "Such department don't exists in DB. Snapshot attempt is canceled.";
	// 	}
	// 	$this->output->set_content_type('application/json')->set_output(json_encode($res));
	// }

	public function system_sites_category_snap() {
		$res = array('status' => false, 'snap' => '', 'msg' => '');
		$id = $this -> input -> post('id');
		$this -> load -> model('webshoots_model');
		$this -> load -> model('site_categories_model');
		$category = $this -> site_categories_model -> get($id);
		if (count($category) > 0) {
			$cat = $category[0];
			// === implement snapshoting (start)
			$http_status = $this -> webshoots_model -> urlExistsCode($cat -> url);
			if ($http_status == 200) {
				$url = preg_replace('#^https?://#', '', $cat -> url);
				$call_url = $this -> webshoots_model -> webthumb_call_link($url);
				$snap_res = $this -> webshoots_model -> crawl_webshoot($call_url, $cat -> id, 'sites_cat_snap-');
				// ==== check image (if we need to repeat snap craw, but using snapito.com) (start)
				$fs = filesize($snap_res['dir']);
				if ($fs === false || $fs < 10000) {// === so re-craw it
					@unlink($snap_res['dir']);
					$api_key = $this -> config -> item('snapito_api_secret');
					$call_url = "http://api.snapito.com/web/$api_key/mc/$url";
					$snap_res = $this -> webshoots_model -> crawl_webshoot($call_url, $cat -> id, 'sites_cat_snap-');
				}
				// ==== check image (if we need to repeat snap craw, but using snapito.com) (end)
				$res_insert = $this -> site_categories_model -> insertSiteCategorySnap($cat -> id, $snap_res['img'], $snap_res['path'], $snap_res['dir'], $http_status);
				if ($res_insert > 0) {
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
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($res));
	}

	public function sites_view() {
		$this -> load -> model('sites_model');
		$this -> load -> model('department_members_model');
		$this -> load -> model('best_sellers_model');

		$sites = $this -> sites_model -> getAll();
		$sitesArray = array();
		foreach ($sites as $site) {
			if (!in_array($customer -> name, sitesArray)) {
				$sitesArray[$site -> id] = $site -> name;
			}
		}
		foreach ($this->department_members_model->getAll() as $row) {
			$this -> data['departmens_list'][$row -> id] = $row -> text;
		}
		foreach ($this->best_sellers_model->getAll() as $row) {
			$this -> data['best_sellers_list'][$row -> id] = $row -> page_title;
		}

		$this -> data['sites'] = $sitesArray;
		$this -> data['category_list'] = $this -> category_list_new();
		$this -> render();
	}

	public function generate_attributes() {
		$this -> load -> model('imported_data_parsed_model');
		$this -> load -> model('imported_data_model');
		$this -> load -> model('imported_data_attributes_model');

		$lines = $this -> imported_data_model -> findNullAttributes(1000);

		foreach ($lines as $line) {
			$imported_id = $line -> id;
			$data = $this -> imported_data_parsed_model -> getByImId($imported_id);

			$res = array();
			foreach ($data as $key => $value) {
				if ($key != 'url') {
					$descCmd = str_replace($this -> config -> item('cmd_mask'), $value, $this -> config -> item('tsv_cmd'));
					if ($result = shell_exec($descCmd)) {
						$a = json_decode(json_encode(simplexml_load_string($result)), 1);
						foreach ($a['description']['attributes']['attribute'] as $attribute) {
							$res[$key][$attribute['@attributes']['tagName']] = $attribute['@attributes']['value'];
						}
					}
				}
			}

			if (!empty($res)) {
				$result = $this -> imported_data_model -> getRow($imported_id);
				if (is_null($result -> imported_data_attribute_id)) {
					$imported_data_attribute_id = $this -> imported_data_attributes_model -> insert(serialize($res));
					$this -> imported_data_model -> update_attribute_id($imported_id, $imported_data_attribute_id);
				} else {
					$imported_data_attribute_id = $result -> imported_data_attribute_id;
					$this -> imported_data_attributes_model -> update($imported_data_attribute_id, serialize($res));
				}
			}
		}
	}

	function similarity_calculation() {
		$this -> load -> model('imported_data_parsed_model');
		$this -> load -> model('imported_data_model');
		$this -> load -> model('imported_data_attributes_model');
		$this -> load -> model('similar_imported_data_model');
		$this -> load -> model('similar_groups_model');

		$imported = $this -> similar_groups_model -> getIdsForComparition();

		$merged = array();

		foreach ($imported as $imported_id) {
			$attributes = $this -> imported_data_attributes_model -> getByImportedDataId($imported_id);

			$resArr = array();
			foreach (unserialize($attributes->attributes) as $key => $value) {
				if ($key != 'features') {
					$resArr = array_merge($resArr, $value);
				}
			}
			$merged[] = $resArr;
		}

		function allKeysExist($arr, $keys) {
			foreach ($keys as $key) {
				if (!key_exists($key, $arr)) {
					return false;
				}
			}
			return true;
		}

		$similar_array = array();
		$similar_to = array();
		$similar_to2 = array();

		for ($i = 0; $i < count($merged); $i++) {
			for ($j = $i + 1; $j < count($merged); $j++) {
				$intersec = array_intersect($merged[$i], $merged[$j]);
				$diff = abs(count($merged[$i]) - count($merged[$j]));
				$max = max(count($merged[$i]), count($merged[$j]));
				$similarity = count($intersec) / max(count($merged[$i]), count($merged[$j]));

				$inserted = false;
				if (allKeysExist($intersec, $this -> config -> item('important_attributes'))) {
					foreach ($similar_to as &$arr) {
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
				} else if (allKeysExist($intersec, $this -> config -> item('important_attributes_min')) && ($similarity > 0.7)) {
					foreach ($similar_to2 as &$arr) {
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

		function saveSimilar($similar_to, $percent = 0) {
			$CI = &get_instance();

			$similarity = 1;
			foreach ($similar_to as &$similar_group) {
				$group_id = false;

				$j = count($similar_group);
				for ($i = 0; $i < $j; $i++) {
					if ($group_id = $CI -> similar_imported_data_model -> findByImportedDataId($similar_group[$i])) {
						unset($similar_group[$i]);
					}
				}

				if ($group_id === false) {
					if ($percent !== 0) {
						$similarity = 0;
					}
					$group_id = $CI -> similar_groups_model -> insert($similarity, $percent);
				}
				foreach ($similar_group as $imported_id) {
					$CI -> similar_imported_data_model -> insert($imported_id, $group_id);
				}
			}
		}

		saveSimilar($similar_to);
		saveSimilar($similar_to2, 70);
	}

	public function get_site_info() {
		$this -> load -> model('sites_model');
		$site_id = $this -> input -> post('site');
		$site_info = $this -> sites_model -> get($site_id);
		/* foreach($site_info as $site){
		 $site->image_url = $this->config->item('tmp_upload_dir').$site->image_url;
		 }*/
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($site_info));
	}

	public function add_new_site() {
		$this -> load -> model('sites_model');
		$response['id'] = $this -> sites_model -> insertSiteByName($this -> input -> post('site'));
		$response['message'] = 'Site was added successfully';
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($response));
	}

	public function delete_site() {
		$this -> load -> model('sites_model');
		$this -> sites_model -> delete($this -> input -> post('site'));
		$response['message'] = 'Site was deleted successfully';
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($response));
	}

	public function update_site_logo() {
		$this -> load -> model('sites_model');
		$this -> sites_model -> updateSite($this -> input -> post('id'), $this -> input -> post('logo'));
		$response['message'] = 'Site was updated successfully';
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($response));
	}

	public function update_site_info() {
		$this -> load -> model('sites_model');
		$this -> sites_model -> update($this -> input -> post('id'), $this -> input -> post('site_name'), $this -> input -> post('site_url'), $this -> input -> post('logo'));
		$response['message'] = 'Site was updated successfully';
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($response));
	}

	public function delete_sitelogo() {
		$this -> load -> model('sites_model');
		$this -> sites_model -> updateSite($this -> input -> post('id'), $this -> input -> post('logo'));
		$response['message'] = 'Site was deleted successfully';
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($response));
	}

	private function customers_list_new() {
		$this -> load -> model('customers_model');
		$output = array();
		$customers_init_list = $this -> customers_model -> getAll();
		if (count($customers_init_list) > 0) {
			foreach ($customers_init_list as $key => $value) {
				$mid = array('id' => $value -> id, 'desc' => $value -> description, 'image_url' => $value -> image_url, 'name' => $value -> name, 'name_val' => strtolower($value -> name));
				$output[] = $mid;
			}
		}
		return $output;
	}

	public function system_rankings() {
		$api_username = $this -> config -> item('ranking_api_username');
		$api_key = $this -> config -> item('ranking_api_key');
		// === get keyword data to http://www.serpranktracker.com (start)
		$data = array("data" => json_encode(array("action" => "getAccountRankings", "id" => "$api_username", "apikey" => "$api_key")));
		$ch = curl_init('https://www.serpranktracker.com/tracker/webservice');
		curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");
		curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
		$track_data = curl_exec($ch);
		$this -> data['track_data'] = json_decode($track_data);
		// === get keyword data to http://www.serpranktracker.com (end)
		$this -> render();
	}

	public function getrankingdata() {
		$api_username = $this -> config -> item('ranking_api_username');
		$api_key = $this -> config -> item('ranking_api_key');
		// === get keyword data to http://www.serpranktracker.com (start)
		$data = array("data" => json_encode(array("action" => "getAccountRankings", "id" => "$api_username", "apikey" => "$api_key")));
		$ch = curl_init('https://www.serpranktracker.com/tracker/webservice');
		curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");
		curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
		$track_data = curl_exec($ch);
		$data = array('track_data' => json_decode($track_data));
		$this -> load -> view('system/getrankingdata', $data);
	}

	public function system_reports() {
		$this -> render();
	}

	public function system_reports_get_all() {
		$this -> load -> model('reports_model');
		$response['data'] = $this -> reports_model -> get_all_report_names();
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($response));
	}

	public function system_reports_get_options() {
		$this -> load -> model('reports_model');
		$id = $this -> input -> get('id');
		$page = $this -> input -> get('page');
		$report = $this -> reports_model -> get_by_id($id);
		switch ($page) {
			case 'cover' :
				$response = array('page_name' => $report[0] -> cover_page_name, 'page_order' => $report[0] -> cover_page_order, 'page_layout' => $report[0] -> cover_page_layout, 'page_body' => $report[0] -> cover_page_body, );
				break;
			case 'recommendations' :
				$response = array('page_name' => $report[0] -> recommendations_page_name, 'page_order' => $report[0] -> recommendations_page_order, 'page_layout' => $report[0] -> recommendations_page_layout, 'page_body' => $report[0] -> recommendations_page_body, );
				break;
			case 'about' :
				$response = array('page_name' => $report[0] -> about_page_name, 'page_order' => $report[0] -> about_page_order, 'page_layout' => $report[0] -> about_page_layout, 'page_body' => $report[0] -> about_page_body, );
				break;
			case 'parts' :
				$report_parts = unserialize($report[0] -> parts);
				if ($report_parts == false) {
					$response = array('summary' => true, 'recommendations' => false, 'details' => false, );
				} else {
					$response = $report_parts;
				}
				break;
			default :
				$response = array('page_name' => $report[0] -> cover_page_name, 'page_order' => $report[0] -> cover_page_order, 'page_layout' => $report[0] -> cover_page_layout, 'page_body' => $report[0] -> cover_page_body, );
				break;
		}
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($response));
	}

	public function system_reports_create() {
		$this -> load -> model('reports_model');
		$name = $this -> input -> post('name');
		$id = $this -> reports_model -> insert($name);
		$response['id'] = $id;
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($response));
	}

	public function system_reports_delete() {
		$this -> load -> model('reports_model');
		$id = $this -> input -> post('id');
		$this -> reports_model -> delete($id);
	}

	public function system_reports_update() {
		$this -> load -> model('reports_model');
		$id = $this -> input -> post('id');
		$params = json_decode($this -> input -> post('params'));
		$type = $this -> input -> post('type');
		if ($type != false) {
			switch ($type) {
				case 'parts' :
					$params -> parts = serialize($params -> parts);
					break;
				default :
					$params = new stdClass();
					break;
			}
		}
		$response['success'] = $this -> reports_model -> update($id, $params);
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($response));
	}

	public function system_logins() {
		$this -> render();
	}

	public function system_batches_list() {
		$this -> load -> model('batches_model');
		$batches = $this -> batches_model -> getAll();
		//$batches_list = array('0'=>'Select batch');
		$batches_list = array('0' => '0');
		foreach ($batches as $batch) {
			$batches_list[$batch -> id] = $batch -> title;
		}
		asort($batches_list);
		$batches_list[0] = 'Select batch';

		return $batches_list;
	}

	public function sync_meta_personal() {
		$this -> load -> model('rankapi_model');
		$id = $this -> input -> post('id');
		$res = $this -> rankapi_model -> sync_meta_personal_keyword($id);
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($res));
	}

	public function delete_keyword_from_kw_source() {
		$this -> load -> model('statistics_new_model');
		$id = $this -> input -> post('id');
		$res = $this -> statistics_new_model -> delete_keyword_kw_source($id);
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($res));
	}

	public function add_keyword_to_kw_source() {
		$this -> load -> model('statistics_new_model');
		$statistics_new_id = $this -> input -> post('id');
		$batch_id = $this -> input -> post('batch_id');
		$kw = $this -> input -> post('kw');
		$kw_prc = $this -> input -> post('kw_prc');
		$kw_count = $this -> input -> post('kw_count');
		$url = $this -> input -> post('url');
		$imported_data_id = $this -> input -> post('imported_data_id');
		$res = $this -> statistics_new_model -> add_keyword_kw_source($statistics_new_id, $batch_id, $kw, $kw_prc, $kw_count, $url, $imported_data_id);
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($res));
	}

	private function keywords_appearence_count($desc, $phrase) {
		return substr_count($desc, ' ' . $phrase . ' ');
	}

	private function prepare_kw_proceed_data($bid, $mode, $cpage) {
		$this -> load -> model('statistics_new_model');
		$this -> load -> model('keywords_model');
		$this -> load -> model('kwsync_queue_list_model');
		$results_stack = array('status' => false, 'msg' => '', 'overall_count' => 0, 'after_filter_count' => 0, 'data' => array(), 'data_pager' => array(), 'pages' => 1, 'cpage' => $cpage);
		if ($bid == 0) {
			$results_stack['msg'] = 'Batch id not specified';
		} else {
			$results = $this -> statistics_new_model -> getStatsDataPure($bid);
			if (count($results) > 0) {
				$results_stack['status'] = true;
				$results_stack['msg'] = 'OK';
				$results_stack['overall_count'] = count($results);
				foreach ($results as $val) {
					if (($val -> url !== null && trim($val -> url) !== "") && ($val -> product_name !== null && trim($val -> product_name) !== "") && (unserialize($val -> long_seo_phrases) !== false || unserialize($val -> short_seo_phrases) !== false)) {
						$mid = array('batch_id' => $val -> batch_id, 'competitors_prices' => unserialize($val -> competitors_prices), 'created' => $val -> created, 'htags' => unserialize($val -> htags), 'id' => $val -> id, 'imported_data_id' => $val -> imported_data_id, 'items_priced_higher_than_competitors' => $val -> items_priced_higher_than_competitors, 'long_description' => $val -> long_description, 'long_description_wc' => $val -> long_description_wc, 'long_seo_phrases' => unserialize($val -> long_seo_phrases), 'own_price' => $val -> own_price, 'parsed_attributes' => unserialize($val -> parsed_attributes), 'price_diff' => unserialize($val -> price_diff), 'product_name' => $val -> product_name, 'research_data_id' => $val -> research_data_id, 'revision' => $val -> revision, 'short_description' => $val -> short_description, 'short_description_wc' => $val -> short_description_wc, 'short_seo_phrases' => unserialize($val -> short_seo_phrases), 'similar_products_competitors' => unserialize($val -> similar_products_competitors), 'snap' => $val -> snap, 'snap_date' => $val -> snap_date, 'snap_state' => $val -> snap_state, 'url' => $val -> url, 'meta' => array('short_meta' => array(), 'long_meta' => array()), 'sync_status' => null);
						// ==== prepare meta keywords data (start) $val->parsed_meta
						$meta_object = unserialize($val -> parsed_meta);
						$meta = array();
						if ((isset($meta_object['Keywords']) && $meta_object['Keywords'] != '')) {
							$meta = explode(',', $meta_object['Keywords']);
						}
						if ((isset($meta_object['keywords']) && $meta_object['keywords'] != '')) {
							$meta = explode(',', $meta_object['keywords']);
						}
						if (count($meta) > 0 && isset($val -> short_description) && $val -> short_description != '') {
							foreach ($meta as $key => $val) {
								$volume = '';
								$from_keyword_data = $this -> keywords_model -> get_by_keyword($val['ph']);
								if (count($from_keyword_data) > 0) {
									$volume = $from_keyword_data['volume'];
								}
								$words = count(explode(' ', trim($val)));
								$count = $this -> keywords_appearence_count(strtolower($val -> short_description), strtolower($val));
								$desc_words_count = count(explode(' ', $val -> short_description));

								$prc = round($count * $words / $desc_words_count * 100, 2);
								$val = preg_replace("/'/", '', $val);
								$mid['meta']['short_meta'][] = array('ph' => $val, 'count' => $count, 'prc' => $prc, 'volume' => $volume);
							}
						}
						if (count($meta) > 0 && isset($val -> long_description) && $val -> long_description != '') {
							foreach ($meta as $key => $val) {
								$volume = '';
								$from_keyword_data = $this -> keywords_model -> get_by_keyword($val);
								if (count($from_keyword_data) > 0) {
									$volume = $from_keyword_data['volume'];
								}
								$words = count(explode(' ', trim($val)));
								$count = $this -> keywords_appearence_count(strtolower($val -> long_description), strtolower($val));
								$desc_words_count = count(explode(' ', $val -> long_description));

								$prc = round($count * $words / $desc_words_count * 100, 2);
								$val = preg_replace("/'/", '', $val);
								$mid['meta']['long_meta'][] = array('ph' => $val, 'count' => $count, 'prc' => $prc, 'volume' => $volume);
							}
						}
						// ==== prepare meta keywords data (end)
						$results_stack['data'][] = $mid;
					}
				}
				$results_stack['after_filter_count'] = count($results_stack['data']);
				// ==== pagination stuffs fitering (start)
				if ($mode == 'page') {
					$items_per_page = 20;
					$skip = ($cpage - 1) * $items_per_page;
					$limit = $items_per_page;
					$kw_data = array_slice($results_stack['data'], $skip, $limit);
				} else {
					$kw_data = $results_stack['data'];
				}
				// ==== pagination stuffs fitering (end)
			} else {
				$kw_data = array();
			}
		}
		return $kw_data;
	}

	public function kw_common_add_to_queu() {
		$this -> load -> model('statistics_new_model');
		$this -> load -> model('keywords_model');
		$this -> load -> model('kwsync_queue_list_model');
		$bid = $this -> input -> post('bid');
		$cpage = $this -> input -> post('cpage');
		$q_mode = $this -> input -> post('q_mode');
		$kw_data = $this -> prepare_kw_proceed_data($bid, $q_mode, $cpage);
		// ===== prepare keywords data for syns processess (start)
		$kw_words_data = array();
		if (count($kw_data) > 0) {
			foreach ($kw_data as $kw => $vw) {
				if ($vw['long_seo_phrases']) {
					foreach ($vw['long_seo_phrases'] as $ki => $vi) {
						$check = $this -> statistics_new_model -> check_keyword_kw_source($vw['id'], $vw['batch_id'], trim($vi['ph']));
						if ($check['status']) {
							$mid_kw = array('status' => 'sync', 'kw_id' => $check['last_id'], 'imported_data_id' => $vw['imported_data_id'], 'url' => $vw['url'], 'batch_id' => $vw['batch_id'], 'statistics_new_id' => $vw['id'], 'kw' => trim($vi['ph']), 'kw_prc' => $vi['prc'], 'kw_count' => $vi['count']);
						} else {
							$mid_kw = array('status' => 'add_sync', 'kw_id' => null, 'imported_data_id' => $vw['imported_data_id'], 'url' => $vw['url'], 'batch_id' => $vw['batch_id'], 'statistics_new_id' => $vw['id'], 'kw' => trim($vi['ph']), 'kw_prc' => $vi['prc'], 'kw_count' => $vi['count']);
						}
						$kw_words_data[] = $mid_kw;
					}
				}
				if ($vw['short_seo_phrases']) {
					foreach ($vw['short_seo_phrases'] as $ki => $vi) {
						$check = $this -> statistics_new_model -> check_keyword_kw_source($vw['id'], $vw['batch_id'], trim($vi['ph']));
						if ($check['status']) {
							$mid_kw = array('status' => 'sync', 'kw_id' => $check['last_id'], 'imported_data_id' => $vw['imported_data_id'], 'url' => $vw['url'], 'batch_id' => $vw['batch_id'], 'statistics_new_id' => $vw['id'], 'kw' => trim($vi['ph']), 'kw_prc' => $vi['prc'], 'kw_count' => $vi['count']);
						} else {
							$mid_kw = array('status' => 'add_sync', 'kw_id' => null, 'imported_data_id' => $vw['imported_data_id'], 'url' => $vw['url'], 'batch_id' => $vw['batch_id'], 'statistics_new_id' => $vw['id'], 'kw' => trim($vi['ph']), 'kw_prc' => $vi['prc'], 'kw_count' => $vi['count']);
						}
						$kw_words_data[] = $mid_kw;
					}
				}
				if ($vw['meta']['short_meta']) {
					foreach ($vw['meta']['short_meta'] as $ki => $vi) {
						$check = $this -> statistics_new_model -> check_keyword_kw_source($vw['id'], $vw['batch_id'], trim($vi['ph']));
						if ($check['status']) {
							$mid_kw = array('status' => 'sync', 'kw_id' => $check['last_id'], 'imported_data_id' => $vw['imported_data_id'], 'url' => $vw['url'], 'batch_id' => $vw['batch_id'], 'statistics_new_id' => $vw['id'], 'kw' => trim($vi['ph']), 'kw_prc' => $vi['prc'], 'kw_count' => $vi['count']);
						} else {
							$mid_kw = array('status' => 'add_sync', 'kw_id' => null, 'imported_data_id' => $vw['imported_data_id'], 'url' => $vw['url'], 'batch_id' => $vw['batch_id'], 'statistics_new_id' => $vw['id'], 'kw' => trim($vi['ph']), 'kw_prc' => $vi['prc'], 'kw_count' => $vi['count']);
						}
						$kw_words_data[] = $mid_kw;
					}
				}
				if ($vw['meta']['long_meta']) {
					foreach ($vw['meta']['long_meta'] as $ki => $vi) {
						$check = $this -> statistics_new_model -> check_keyword_kw_source($vw['id'], $vw['batch_id'], trim($vi['ph']));
						if ($check['status']) {
							$mid_kw = array('status' => 'sync', 'kw_id' => $check['last_id'], 'imported_data_id' => $vw['imported_data_id'], 'url' => $vw['url'], 'batch_id' => $vw['batch_id'], 'statistics_new_id' => $vw['id'], 'kw' => trim($vi['ph']), 'kw_prc' => $vi['prc'], 'kw_count' => $vi['count']);
						} else {
							$mid_kw = array('status' => 'add_sync', 'kw_id' => null, 'imported_data_id' => $vw['imported_data_id'], 'url' => $vw['url'], 'batch_id' => $vw['batch_id'], 'statistics_new_id' => $vw['id'], 'kw' => trim($vi['ph']), 'kw_prc' => $vi['prc'], 'kw_count' => $vi['count']);
						}
						$kw_words_data[] = $mid_kw;
					}
				}
			}
		}
		// ===== prepare keywords data for syns processess (end)

		// ===== starting syncing/adding processes (start)
		if (count($kw_words_data) > 0) {
			foreach ($kw_words_data as $ka => $va) {
				$this -> kwsync_queue_list_model -> insert($va['kw_id'], $va['kw'], $va['url']);
				// === add to queue
			}
			if (isset($_POST['shell_queue']))
				shell_exec('php index.php crawl crawl_sync_meta_personal');
		}
		// ===== starting syncing/adding processes (end)

		$this -> output -> set_content_type('application/json') -> set_output(json_encode($kw_words_data));
	}

	public function kw_sync_current_page() {
		$this -> load -> model('statistics_new_model');
		$this -> load -> model('keywords_model');
		$this -> load -> model('kwsync_queue_list_model');
		$this -> load -> model('rankapi_model');
		$bid = $this -> input -> post('bid');
		$cpage = $this -> input -> post('cpage');
		$sync_mode = $this -> input -> post('sync_mode');
		$kw_data = $this -> prepare_kw_proceed_data($bid, $sync_mode, $cpage);

		// ===== prepare keywords data for syns processess (start)
		$kw_words_data = array();
		if (count($kw_data) > 0) {
			foreach ($kw_data as $kw => $vw) {
				if ($vw['long_seo_phrases']) {
					foreach ($vw['long_seo_phrases'] as $ki => $vi) {
						$check = $this -> statistics_new_model -> check_keyword_kw_source($vw['id'], $vw['batch_id'], trim($vi['ph']));
						if ($check['status']) {
							$mid_kw = array('status' => 'sync', 'kw_id' => $check['last_id'], 'imported_data_id' => $vw['imported_data_id'], 'url' => $vw['url'], 'batch_id' => $vw['batch_id'], 'statistics_new_id' => $vw['id'], 'kw' => trim($vi['ph']), 'kw_prc' => $vi['prc'], 'kw_count' => $vi['count']);
						} else {
							$mid_kw = array('status' => 'add_sync', 'kw_id' => null, 'imported_data_id' => $vw['imported_data_id'], 'url' => $vw['url'], 'batch_id' => $vw['batch_id'], 'statistics_new_id' => $vw['id'], 'kw' => trim($vi['ph']), 'kw_prc' => $vi['prc'], 'kw_count' => $vi['count']);
						}
						$kw_words_data[] = $mid_kw;
					}
				}
				if ($vw['short_seo_phrases']) {
					foreach ($vw['short_seo_phrases'] as $ki => $vi) {
						$check = $this -> statistics_new_model -> check_keyword_kw_source($vw['id'], $vw['batch_id'], trim($vi['ph']));
						if ($check['status']) {
							$mid_kw = array('status' => 'sync', 'kw_id' => $check['last_id'], 'imported_data_id' => $vw['imported_data_id'], 'url' => $vw['url'], 'batch_id' => $vw['batch_id'], 'statistics_new_id' => $vw['id'], 'kw' => trim($vi['ph']), 'kw_prc' => $vi['prc'], 'kw_count' => $vi['count']);
						} else {
							$mid_kw = array('status' => 'add_sync', 'kw_id' => null, 'imported_data_id' => $vw['imported_data_id'], 'url' => $vw['url'], 'batch_id' => $vw['batch_id'], 'statistics_new_id' => $vw['id'], 'kw' => trim($vi['ph']), 'kw_prc' => $vi['prc'], 'kw_count' => $vi['count']);
						}
						$kw_words_data[] = $mid_kw;
					}
				}
				if ($vw['meta']['short_meta']) {
					foreach ($vw['meta']['short_meta'] as $ki => $vi) {
						$check = $this -> statistics_new_model -> check_keyword_kw_source($vw['id'], $vw['batch_id'], trim($vi['ph']));
						if ($check['status']) {
							$mid_kw = array('status' => 'sync', 'kw_id' => $check['last_id'], 'imported_data_id' => $vw['imported_data_id'], 'url' => $vw['url'], 'batch_id' => $vw['batch_id'], 'statistics_new_id' => $vw['id'], 'kw' => trim($vi['ph']), 'kw_prc' => $vi['prc'], 'kw_count' => $vi['count']);
						} else {
							$mid_kw = array('status' => 'add_sync', 'kw_id' => null, 'imported_data_id' => $vw['imported_data_id'], 'url' => $vw['url'], 'batch_id' => $vw['batch_id'], 'statistics_new_id' => $vw['id'], 'kw' => trim($vi['ph']), 'kw_prc' => $vi['prc'], 'kw_count' => $vi['count']);
						}
						$kw_words_data[] = $mid_kw;
					}
				}
				if ($vw['meta']['long_meta']) {
					foreach ($vw['meta']['long_meta'] as $ki => $vi) {
						$check = $this -> statistics_new_model -> check_keyword_kw_source($vw['id'], $vw['batch_id'], trim($vi['ph']));
						if ($check['status']) {
							$mid_kw = array('status' => 'sync', 'kw_id' => $check['last_id'], 'imported_data_id' => $vw['imported_data_id'], 'url' => $vw['url'], 'batch_id' => $vw['batch_id'], 'statistics_new_id' => $vw['id'], 'kw' => trim($vi['ph']), 'kw_prc' => $vi['prc'], 'kw_count' => $vi['count']);
						} else {
							$mid_kw = array('status' => 'add_sync', 'kw_id' => null, 'imported_data_id' => $vw['imported_data_id'], 'url' => $vw['url'], 'batch_id' => $vw['batch_id'], 'statistics_new_id' => $vw['id'], 'kw' => trim($vi['ph']), 'kw_prc' => $vi['prc'], 'kw_count' => $vi['count']);
						}
						$kw_words_data[] = $mid_kw;
					}
				}
			}
		}
		// ===== prepare keywords data for syns processess (end)

		// ===== starting syncing/adding processes (start)
		if (count($kw_words_data) > 0) {
			foreach ($kw_words_data as $ka => $va) {
				if ($va['status'] === 'sync') {// ===== just syncing (plus adding to TWCrawler queue)
					$this -> rankapi_model -> sync_meta_personal_keyword($va['kw_id']);
					// === sync (!!! PROBBALY NO NEED FOR THIS HERE, CAUSE OVERLOAD AND TAKES A LOT TIME TO PROCEED !!!)
					$this -> kwsync_queue_list_model -> insert($va['kw_id'], $va['kw'], $va['url']);
					// === add to queue
				} else {// ===== add and sync (plus adding to TWCrawler queue)
					$add_res = $this -> statistics_new_model -> add_keyword_kw_source($va['statistics_new_id'], $va['batch_id'], $va['kw'], $va['kw_prc'], $va['kw_count'], $va['url'], $va['imported_data_id']);
					// === add
					if ($add_res['status']) {
						$this -> rankapi_model -> sync_meta_personal_keyword($add_res['last_id']);
						// === sync (!!! PROBBALY NO NEED FOR THIS HERE, CAUSE OVERLOAD AND TAKES A LOT TIME TO PROCEED !!!)
						$this -> kwsync_queue_list_model -> insert($add_res['last_id'], $va['kw'], $va['url']);
						// === add to queue
					}
				}
			}
		}
		// ===== starting syncing/adding processes (end)

		$this -> output -> set_content_type('application/json') -> set_output(json_encode($kw_data));
	}

	public function system_get_mkw_info() {
		$this -> load -> model('statistics_new_model');
		$this -> load -> model('keywords_model');
		$bid = $this -> input -> post('bid');
		$cpage = $this -> input -> post('cpage');
		$v_mode_option = $this -> input -> post('v_mode_option');
		$results_stack = array('status' => false, 'msg' => '', 'overall_count' => 0, 'after_filter_count' => 0, 'data' => array(), 'data_pager' => array(), 'pages' => 1, 'cpage' => $cpage);
		if ($bid == 0) {
			$results_stack['msg'] = 'Batch id not specified';
		} else {
			// $results = $this->statistics_new_model->getStatsDataPure($bid, $limit, $skip);
			$results = $this -> statistics_new_model -> getStatsDataPure($bid);
			if (count($results) > 0) {
				$results_stack['status'] = true;
				$results_stack['msg'] = 'OK';
				$results_stack['overall_count'] = count($results);
				foreach ($results as $val) {
					if (($val -> url !== null && trim($val -> url) !== "") && ($val -> product_name !== null && trim($val -> product_name) !== "") && (unserialize($val -> long_seo_phrases) !== false || unserialize($val -> short_seo_phrases) !== false)) {
						$mid = array('batch_id' => $val -> batch_id, 'competitors_prices' => unserialize($val -> competitors_prices), 'created' => $val -> created, 'htags' => unserialize($val -> htags), 'id' => $val -> id, 'imported_data_id' => $val -> imported_data_id, 'items_priced_higher_than_competitors' => $val -> items_priced_higher_than_competitors, 'long_description' => $val -> long_description, 'long_description_wc' => $val -> long_description_wc, 'long_seo_phrases' => unserialize($val -> long_seo_phrases), 'own_price' => $val -> own_price, 'parsed_attributes' => unserialize($val -> parsed_attributes), 'price_diff' => unserialize($val -> price_diff), 'product_name' => $val -> product_name, 'research_data_id' => $val -> research_data_id, 'revision' => $val -> revision, 'short_description' => $val -> short_description, 'short_description_wc' => $val -> short_description_wc, 'short_seo_phrases' => unserialize($val -> short_seo_phrases), 'similar_products_competitors' => unserialize($val -> similar_products_competitors), 'snap' => $val -> snap, 'snap_date' => $val -> snap_date, 'snap_state' => $val -> snap_state, 'url' => $val -> url, 'meta' => array('short_meta' => array(), 'long_meta' => array())
						// 'fixed_seo_short' => $this->helpers->measure_analyzer_start_v2_product_name($val->product_name, preg_replace('/\s+/', ' ', $val->short_description)),
						// 'fixed_seo_long' => $this->helpers->measure_analyzer_start_v2_product_name($val->product_name, preg_replace('/\s+/', ' ', $val->long_description))
						);
						// ==== prepare meta keywords data (start) $val->parsed_meta
						$meta_object = unserialize($val -> parsed_meta);
						$meta = array();
						if ((isset($meta_object['Keywords']) && $meta_object['Keywords'] != '')) {
							$meta = explode(',', $meta_object['Keywords']);
						}
						if ((isset($meta_object['keywords']) && $meta_object['keywords'] != '')) {
							$meta = explode(',', $meta_object['keywords']);
						}
						if (count($meta) > 0 && isset($val -> short_description) && $val -> short_description != '') {
							foreach ($meta as $key => $val) {
								$volume = '';
								$from_keyword_data = $this -> keywords_model -> get_by_keyword($val['ph']);
								if (count($from_keyword_data) > 0) {
									$volume = $from_keyword_data['volume'];
								}
								$words = count(explode(' ', trim($val)));
								$count = $this -> keywords_appearence_count(strtolower($val -> short_description), strtolower($val));
								$desc_words_count = count(explode(' ', $val -> short_description));

								$prc = round($count * $words / $desc_words_count * 100, 2);
								$val = preg_replace("/'/", '', $val);
								$mid['meta']['short_meta'][] = array('ph' => $val, 'count' => $count, 'prc' => $prc, 'volume' => $volume);
							}
						}
						if (count($meta) > 0 && isset($val -> long_description) && $val -> long_description != '') {
							foreach ($meta as $key => $val) {
								$volume = '';
								$from_keyword_data = $this -> keywords_model -> get_by_keyword($val);
								if (count($from_keyword_data) > 0) {
									$volume = $from_keyword_data['volume'];
								}
								$words = count(explode(' ', trim($val)));
								$count = $this -> keywords_appearence_count(strtolower($val -> long_description), strtolower($val));
								$desc_words_count = count(explode(' ', $val -> long_description));

								$prc = round($count * $words / $desc_words_count * 100, 2);
								$val = preg_replace("/'/", '', $val);
								$mid['meta']['long_meta'][] = array('ph' => $val, 'count' => $count, 'prc' => $prc, 'volume' => $volume);
							}
						}
						// ==== prepare meta keywords data (end)
						$results_stack['data'][] = $mid;
					}
				}
				$results_stack['after_filter_count'] = count($results_stack['data']);
				// ==== pagination stuffs fitering (start)
				$items_per_page = 20;
				$skip = ($cpage - 1) * $items_per_page;
				$limit = $items_per_page;
				$results_stack['data_pager'] = array_slice($results_stack['data'], $skip, $limit);
				$results_stack['pages'] = ceil($results_stack['after_filter_count'] / $items_per_page);
				// ==== pagination stuffs fitering (end)
			} else {
				$results_stack['msg'] = 'No any data finded';
			}
		}

		$data['results_stack'] = $results_stack;
		$data['statistics_new_model'] = $this -> statistics_new_model;
		$data['v_mode_option'] = $v_mode_option;
		$data['bid'] = $bid;
		$this -> load -> view('system/system_get_mkw_info', $data);
		// $this->output->set_content_type('application/json')->set_output(json_encode($results_stack));
	}

	public function explore_meta_personal() {
		$this -> load -> model('statistics_new_model');
		$id = $this -> input -> post('id');
		$response = $this -> statistics_new_model -> get_keyword_source_by_id($id);
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($response));
	}

	public function keywords() {
		$this -> load -> model('keyword_model_system');
		$regions = $this -> keyword_model_system -> get_regions();
		$keyword_data_sources = $this -> keyword_model_system -> get_keyword_data_sources();
		$search_engines = $this -> keyword_model_system -> get_serach_engine();
		foreach ($regions as $region) {
			$regions_list[$region -> id] = $region -> region;
		}
		foreach ($search_engines as $search_engine) {
			$search_engine_list[$search_engine -> id] = $search_engine -> search_engine;
		}
		foreach ($keyword_data_sources as $keyword_data_source) {
			$keyword_data_sources_list[$keyword_data_source -> id] = $keyword_data_source -> data_source_name;
		}
		$this -> data['regions'] = $regions_list;
		$this -> data['keyword_data_sources'] = $keyword_data_sources_list;
		$this -> data['search_engine'] = $search_engine_list;
		// ===== meta keywords ranking stuffs (start)
		$this -> load -> model('batches_model');
		$this -> data['batches_list'] = $this -> system_batches_list();
		// ===== meta keywords ranking stuffs (end)
		$this -> render();
	}

	public function system_last_logins() {
		$this -> load -> model('logins_model');
		$response['data'] = $this -> logins_model -> get_last_logins();
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($response));
	}

	public function system_keywords() {
		$this -> load -> model('keyword_model_system');
		$response['data'] = $this -> keyword_model_system -> get_keywords();
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($response));
	}

	public function add_new_keywords() {
		$this -> load -> model('keyword_model_system');
		$new_keyword = $this -> input -> post('new_keyword');
		$new_data_source_name = $this -> input -> post('new_data_source_name');
		$new_volume = $this -> input -> post('new_volume');
		$new_search_engine = $this -> input -> post('new_search_engine');
		$new_region = $this -> input -> post('new_region');
		$response['data'] = $this -> keyword_model_system -> insertKeywords($new_keyword, $new_volume, $new_search_engine, $new_region, $new_data_source_name);
		$response['message'] = 'keyword was added successfully';
		$this -> output -> set_content_type('application/json') -> set_output(json_encode($response));
	}

	public function save_category() {
		$this -> load -> model('site_categories_model');
		$site_id = $this -> input -> post('site_id');
		$category_text = $this -> input -> post('category');
		$description_text = $this -> input -> post('text');
		$url = $this -> input -> post('url');
		$wc = $this -> input -> post('wc');
		$department_members_id = $this -> input -> post('department_id');
		if ($category_text != '') {
			$parent_id = $this -> site_categories_model -> checkExist($site_id, $category_text, $department_members_id);
			if ($parent_id == false) {
				$response['data'] = $this -> site_categories_model -> insert(0, $site_id, $category_text, $url, 0, '', $department_members_id, 0, $wc, '', '', '', $description_text, 0);
			} else {
				$response['data'] = $this -> site_categories_model -> insert($parent_id, $site_id, $category_text, $url, 0, '', $department_members_id, 0, $wc, '', '', '', $description_text, 0);
			}
			$response['message'] = 'category was added successfully';
			$this -> output -> set_content_type('application/json') -> set_output(json_encode($response));
		}
	}

	public function save_department() {
		$this -> load -> model('department_model');
		$this -> load -> model('department_members_model');
		$site_id = $this -> input -> post('site_id');
		$url = $this -> input -> post('url');
		$department_text = $this -> input -> post('department');
		$description_text = $this -> input -> post('text');
		$wc = $this -> input -> post('wc');
		$department_id = 0;

		$check_department_id = $this -> department_model -> checkExist($department_text);
		if ($check_department_id == false) {
			$department_id = $this -> department_model -> insert($department_text, $department_text);
		} else {
			$department_id = $check_department_id;
		}
		$parent_id = 0;
		if ($department_text != '') {
			$parent_id = $this -> department_members_model -> checkExist($site_id, $department_text);
			if ($parent_id == false) {
				$response['data'] = $this -> department_members_model -> insert(0, $site_id, $department_id, $department_text, $url, $wc, $description_text, '', '', '', 0);
			} else {
				$response['data'] = $this -> department_members_model -> insert($parent_id, $site_id, $department_id, $department_text, $url, $wc, $description_text, '', '', '', 0);
			}
			$response['message'] = 'department was added successfully';
			$this -> output -> set_content_type('application/json') -> set_output(json_encode($response));
		}
	}

	public function edit_department() {
		if (isset($_POST['id']) && isset($_POST['text']) && isset($_POST['url']) && isset($_POST['description_text']) && isset($_POST['description_words'])) {
			$id = $_POST['id'];
			$data['text'] = $_POST['text'];
			$data['url'] = $_POST['url'];
			$data['description_text'] = $_POST['description_text'];
			$data['description_words'] = $_POST['description_words'];
			$this -> load -> model('department_members_model');
			$this -> department_members_model -> updateDepartment($id, $data);
		}
	}

	public function get_department() {
		if ($_POST['id']) {
			$this -> load -> model('department_members_model');
			$result = $this -> department_members_model -> get($_POST['id']);
			echo json_encode($result);
		}
	}

	public function get_custom_models() {
            $search = NULL;
            $iDisplayStart = 1;
            $iDisplayLength = null;
            if ( isset( $_GET['iDisplayStart'] ) && $_GET['iDisplayLength'] != '-1' )
            {
                $iDisplayStart = $_GET['iDisplayStart'];
                $iDisplayLength = $_GET['iDisplayLength'];
                
            }
            if ( $_GET['sSearch'] != "" ){
                $search = $_GET['sSearch'];
            }
                $sEcho = $_GET['sEcho'];
        
            $results = $this -> imported_data_parsed_model -> get_custom_models($search, $iDisplayStart , $iDisplayLength,$sEcho);
            $this -> output -> set_content_type('application/json') -> set_output(json_encode($results));
	}

	public function update_custom_model() {
		$model = $this -> input -> post('model');
		$imported_data_id = $this -> input -> post('imported_data_id');
		$results = $this -> imported_data_parsed_model -> give_model($imported_data_id, $model);
		echo 'ok';
	}

	public function delete_custom_model() {
		$imported_data_id = $this -> input -> post('imported_data_id');
		$this -> imported_data_parsed_model -> delete_model($imported_data_id);
	}

	public function add_snapshot_queue() {
		if (isset($_POST['snapshot_arr']) && isset($_POST['type'])) {
			$this -> load -> model('snapshot_queue_list_model');
			$this -> snapshot_queue_list_model -> insert($_POST['snapshot_arr'], $_POST['type']);
		} else if (isset($_POST['batch_id']) && isset($_POST['type']) && isset($_POST['unsnapshoted_items'])) {
			$this -> load -> model('crawler_list_model');
			$result = $this -> crawler_list_model -> getByBatchOverall($_POST['batch_id'], $_POST['unsnapshoted_items']);
			foreach ($result as $key => $value) {
				$snapshot_arr[$key][0] = $value -> id;
				$snapshot_arr[$key][1] = $value -> url;
				$snapshot_arr[$key][2] = $value -> imported_data_id;
			}
			$this -> load -> model('snapshot_queue_list_model');
			$this -> snapshot_queue_list_model -> insert($snapshot_arr, $_POST['type']);
		}
	}

	public function snapshot_queue() {
		$this -> load -> model('snapshot_queue_list_model');
		$result = $this -> snapshot_queue_list_model -> getAll();
		$this -> data['rows'] = $result;
		$this -> render();
	}

	public function system_uploadmatchurls() {
		$this -> render();
	}

	public function system_dostatsmonitor() {
            $this -> load -> model('batches_model');
            $this->data['batches'] = $this -> batches_model -> getAll();
		$this -> render();
	}
        public function get_size_of_batch(){
            $this -> load -> model('statistics_new_model');
            $batch = $this -> input -> post('batch_id');
            if($batch){
                echo $this -> statistics_new_model -> get_size_of_batch($batch);
            }
            else{
                redirect('system');
            }
        }

	public function upload_match_urls() {
		ini_set('post_max_size', '100M');
		$this -> load -> library('UploadHandler');
		$this -> output -> set_content_type('application/json');
		$this -> uploadhandler -> upload(array('script_url' => site_url('system/upload_match_urls'), 'upload_dir' => $this -> config -> item('csv_upload_dir'), 'param_name' => 'files', 'delete_type' => 'POST', 'accept_file_types' => '/.+\.(txt|jl|csv)$/i', ));
	}

//    public function check_urls_test(){
//        $this->load->model('site_categories_model');
//        $this->load->model('settings_model');
//        $this->load->model('thread_model');
//        $this->load->model('imported_data_parsed_model');
//        $this->load->model('temp_data_model');
//        $manu_file_upload_opts = $this->input->post('manu_file_upload_opts');
//        $file = $this->config->item('csv_upload_dir') . $this->input->post('choosen_file');
//        $f_name = end(explode('/', $file));
//        $this->temp_data_model->emptyTable('notfoundurls');
//        $this->temp_data_model->emptyTable('urlstomatch');
//        $this->temp_data_model->emptyTable('updated_items');
//        $this->settings_model->deledtMatching();
//        $fcont = file($file);
//        $linesTotal = 0;
//        $itemsUpdated = 0;
//        $itemsUnchanged = 0;
//        $linesAdded = 0;
//        $linesScaned = 0;
//        $notFoundUrls = 0;
//        $notFoundUrlsArr = array();
//        $process = time();
//        $this->temp_data_model->createMatchUrlsTable();
//        foreach ($fcont as $line) {
//            ++$linesTotal;
//            //*for big files
//            $res = '';
//            $urls = explode(',', trim(trim($line), ','));
//            if (count($urls) == 2) {
//                ++$linesAdded;
//                $this->temp_data_model->addUrlToMatch($urls[0], $urls[1]);
//            }
//            //*/
//        }
//        $this->temp_data_model->createNonFoundTable();
//        $this->temp_data_model->cUpdDataTable();
//        $this->settings_model->addMatchingUrls($f_name, $process, $linesAdded);
//        $this->thread_model->clear($this->session->userdata('user_id'));
//        $start = microtime(true);
//        $timing = 0;
//
//        $thread = 1; // count thread
//        $thread_name = array(); // name threads
//        $time_now = time();
//        $total_strings = $linesAdded;
//        $per_process = ceil($total_strings/$thread);
//
//        /* Init name thread and parametrs */
//        for($i = 1; $i <= $thread; $i++){
//            $thread_name[$time_now.'_'.$i]['name_process'] = $time_now.'_'.$i;
//            $thread_name[$time_now.'_'.$i]['start_limit'] = ($i-1)*$per_process;
//            $thread_name[$time_now.'_'.$i]['end_limit'] = $i*$per_process-1;
//            $thread_name[$time_now.'_'.$i]['uid'] = $this->session->userdata('user_id');
//            if($i == $thread){
//                $thread_name[$time_now.'_'.$i]['end_limit'] = $total_strings;
//            }
//            $this->thread_model->add_process($thread_name[$time_now.'_'.$i]);
//        }
//
//        foreach($thread_name as $key=>$value){
//            sleep(1);
//            // var_dump(exec('curl http://tmeditor/index.php/crons/match_urls_thread/'.$key.' >/dev/null &'));
//            exec('curl http://dev.contentanalyticsinc.com/producteditor/index.php/crons/match_urls_thread/'.$key.' >/dev/null &');
//        }
//        echo "Total lines: " . $linesTotal . "<br/>";
//        echo "Lines scaned" . $linesScaned . "<br/>";
//        echo "Added lines: " . $linesAdded . "<br/>";
//        echo "Non existing urls found: " . $notFoundUrls . "<br>";
//        echo "Items updated: " . $itemsUpdated . "<br>";
//        echo "Manufacturer option status: " . $manu_file_upload_opts;
//    }

    public function check_urls() {
            $manu_file_upload_opts = $this -> input -> post('manu_file_upload_opts');
        $start_run = microtime(true);        
        log_message('ERROR', 'Start ' .  $this -> input -> post('choosen_file'));    
	    $file = $this -> config -> item('csv_upload_dir') . $this -> input -> post('choosen_file');
            // This part always working if uploading finished successfully
            // If you need this script, please, write more specific checking
            // Currently I need url import without this part 
//	    if($manu_file_upload_opts)
//	    {
//		    $this->importManufacturerStatistic($file);
//		    return;
//	    }			
            $this -> load -> model('site_categories_model');
            $this -> load -> model('settings_model');
            $this -> load -> model('imported_data_parsed_model');
            $this -> load -> model('temp_data_model');
            $f_name = end(explode('/', $file));//getting name of file
            $this -> temp_data_model -> emptyTable('notfoundurls');//remove data from 'notfoundurls' table
            $this -> temp_data_model -> emptyTable('urlstomatch');//remove data from 'urlstomatch' table
            $this -> temp_data_model -> emptyTable('updated_items');//remove data from 'updated_items' table
            $this -> settings_model -> deledtMatching();//Delete data of previous matching
            $fcont = file($file);//getting content of file
            $linesTotal = 0;
            $itemsUpdated = 0;
            $itemsUnchanged = 0;
            $linesAdded = 0;
            $linesScaned = 0;
            $notFoundUrls = 0;
            $notFoundUrlsArr = array();
            $process = time();
            //Restored script===================================
            $this->temp_data_model->createMatchUrlsTable();//Creates the table for keeping twins of URLs
            //All tables are created only if they not exists in database
            foreach ($fcont as $line) {//reading file line by line
                ++$linesTotal;
                //*for big files
                $res = '';
                $urls = explode(',', trim(trim($line), ','));//Getting URLs from line
                if (count($urls) == 2) {//If second url is missing line will be ignored
                    ++$linesAdded;
                    $this->temp_data_model->addUrlToMatch($urls[0], $urls[1]);//Add urls to table
                }
                //*/
            }
            //You can Restore this part of script, if it will necessary, 
            //but please check is it working for all cases
//            foreach ($fcont as $line) {
//                ++$linesTotal;
//                // === new I.L (start)
//                $urls = explode(',', trim(trim($line), ','));
//                $this -> temp_data_model -> createMatchUrlsTable($manu_file_upload_opts);
//                $res = '';
//                if (count($urls) == 2) {
//                  ++$linesAdded;
//                  $this -> temp_data_model -> addUrlToMatch($urls[0], $urls[1]);
//                } else if($manu_file_upload_opts && count($urls) >= 2) {
//                	++$linesAdded;
//                	$this -> temp_data_model -> addUrlToMatch($urls[0], $urls[1]);
//                }
//                // === new I.L (end)
//                // ===== previous before I.L (start)
//                // $this -> temp_data_model -> createMatchUrlsTable();
//                // $res = '';
//                // $urls = explode(',', trim(trim($line), ','));
//                // if (count($urls) == 2) {
//                //   ++$linesAdded;
//                //   $this -> temp_data_model -> addUrlToMatch($urls[0], $urls[1]);
//                // }
//                // ===== previous before I.L (end)
//            }
            $this -> temp_data_model -> createNonFoundTable();//Creating table for non found urls
            $this -> temp_data_model -> cUpdDataTable();//Create table for updated items
            $this -> settings_model -> addMatchingUrls($f_name, $process, $linesAdded);//Add matching info to settings table
            $start = microtime(true);
            $timing = 0;
    $exec_time = microtime(true) - $start_run;
    log_message('ERROR', "{$exec_time}sec - {$linesAdded} lines Phase 1");            
    log_message('ERROR', "Start while");            
    //Process of importing URLs can take long time, and makes problem with script executing time limit
    //That's why I had to add dependance from timing for importing process.
    //The following part can be written only in Crons controller, but Crons works in background 
    //and it hard for testing therefore I still keep it here with small time limit
            while ( $timing < 20 && 
                    $urls = $this -> temp_data_model -> getLineFromTable('urlstomatch')
                    ) {
                    $atuc = 2;
                    $nfurls = 0;
                    ++$linesScaned;
                    //$ms = microtime(TRUE);
                    $url1 = $this -> imported_data_parsed_model -> getModelByUrl($urls['url1']);
                    $url2 = $this -> imported_data_parsed_model -> getModelByUrl($urls['url2']);
                    //$dur = microtime(true)-$ms;
                    //exit("select data from db ".$dur);
                    $model1 = '';
                    $model2 = '';
                    if ($url1 === FALSE) {
                            ++$nfurls;
                            $this -> temp_data_model -> addUrlToNonFound($urls['url1'], $process);
                            $atuc -= 1;
                            //$notFoundUrlsArr[]=$urls[0];
                    } else {
                            $tm = false;
                            if ($url1['ph_attr']) {
                                    $tm = unserialize($url1['ph_attr']);
                            }
                            $model1 = $tm['model'] && strlen($tm['model']) > 3 ? $tm['model'] : FALSE;
                    }
                    if ($url2 === FALSE) {
                            ++$nfurls;
                            $this -> temp_data_model -> addUrlToNonFound($urls['url2'], $process);
                            $atuc -= 1;
                            //$notFoundUrlsArr[]=$urls[1];
                    } else {
                            $tm = false;
                            if ($url2['ph_attr']) {
                                    $tm = unserialize($url2['ph_attr']);
                            }
                            $model2 = isset($tm['model']) && strlen($tm['model']) > 3 ? $tm['model'] : false;
                    }
                    if ($nfurls > 0) {
                            $notFoundUrls += $nfurls;
                    } else {
                            $this -> imported_data_parsed_model -> addItem($url1['data_id'], $url2['data_id']);
                            if ($model1) {
                                    if ($model2 && $model1 != $model2) {
                                            if (!($url2['model'] && strlen($url2['model']) > 3) || ($url2['model'] != $model1)) {
                                                    $this -> temp_data_model -> addUpdData($url2['data_id'], $url2['model'], $model1);
                                                    $this -> imported_data_parsed_model -> updateModelOfItem($url2['data_id'], $model1, $url1['rev'] + 1, $url1['data_id']);
                                                    ++$itemsUpdated;
                                                    $atuc -= 1;
                                            }
                                    } elseif (!$model2 && (!($url2['model'] && strlen($url2['model']) > 3) || $model1 != $url2['model'])) {
                                            $this -> temp_data_model -> addUpdData($url2['data_id'], $url2['model'], $model1);
                                            $this -> imported_data_parsed_model -> updateModelOfItem($url2['data_id'], $model1, $url1['rev'] + 1, $url1['data_id']);
                                            ++$itemsUpdated;
                                            $atuc -= 1;
                                    }
                            } elseif ($model2) {
                                    if (!($url1['model'] && strlen($url1['model']) > 3) || $model2 != $url1['model']) {
                                            $this -> temp_data_model -> addUpdData($url1['data_id'], $url1['model'], $model2);
                                            $this -> imported_data_parsed_model -> updateModelOfItem($url1['data_id'], $model2, $url2['rev'] + 1, $url2['data_id']);
                                            ++$itemsUpdated;
                                            $atuc -= 1;
                                    }
                            } elseif (($url1['model'] && strlen($url1['model']) > 3)) {
                                    if (!($url2['model'] && strlen($url2['model']) > 3) || ($url1['model'] != $url2['model'])) {
                                            $this -> temp_data_model -> addUpdData($url2['data_id'], $url2['model'], $url1['model']);
                                            $this -> imported_data_parsed_model -> updateModelOfItem($url2['data_id'], $url1['model'], $url1['rev'] + 1, $url1['data_id']);
                                            ++$itemsUpdated;
                                            $atuc -= 1;
                                    }
                            } elseif (($url2['model'] && strlen($url2['model']) > 3)) {
                                    $this -> temp_data_model -> addUpdData($url1['data_id'], $url1['model'], $url2['model']);
                                    $this -> imported_data_parsed_model -> updateModelOfItem($url1['data_id'], $url2['model'], $url2['rev'] + 1, $url2['data_id']);
                                    ++$itemsUpdated;
                                    $atuc -= 1;
                            } else {
                                    $model = time();
                                    $this -> temp_data_model -> addUpdData($url1['data_id'], $url1['model'], $model);
                                    $this -> temp_data_model -> addUpdData($url2['data_id'], $url2['model'], $model);
                                    $this -> imported_data_parsed_model -> updateModelOfItem($url1['data_id'], $model, $url2['rev'] + 1, $url2['data_id']);
                                    $this -> imported_data_parsed_model -> updateModelOfItem($url2['data_id'], $model, $url1['rev'] + 1, $url1['data_id']);
                                    $itemsUpdated += 2;
                                    $atuc -= 1;
                            }
                    }
                    if ($atuc < 0) {exit('incrorrect ATUC');
                    }
                    $itemsUnchanged += $atuc;
                    $timing = microtime(true) - $start;
            }//*/
            if ($timing < 20) {
                    $val = "$process|$linesScaned|$notFoundUrls|$itemsUpdated|$itemsUnchanged";
                    $this -> settings_model -> updateMatchingUrls($process, $val);
            } else {
                    $lts = $this -> temp_data_model -> getTableSize('urlstomatch');
                    $this -> settings_model -> procUpdMatchingUrls($process, $lts, $itemsUnchanged);
                    if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
                            $call_link = base_url() . "crons/match_urls/$process/$linesScaned/$itemsUpdated/$notFoundUrls/$itemsUnchanged";
                            //            exit($call_link);
                            $this -> site_categories_model -> curl_async($call_link);
                    } else {
                            shell_exec("wget -S -O- http://dev.contentanalyticsinc.com/producteditor/index.php/crons/match_urls/$process/$linesScaned/$itemsUpdated/$notFoundUrls/$itemsUnchanged > /dev/null 2>/dev/null &");
                    }
            }
                    
    $start_run2 = microtime(true);        
    $exec_time = $start_run2 - $start_run1;
    log_message('ERROR', "{$exec_time}sec - {$linesAdded} lines Phase 2");  
    log_message('ERROR', 'End all sec: ' . ($start_run2 - $start_run));
    log_message('ERROR', 'memory usage (peak) : (' . memory_get_peak_usage(). ')' . memory_get_usage()) ;
            echo "Total lines: " . $linesTotal . "<br/>";
            echo "Lines scaned" . $linesScaned . "<br/>";
            echo "Added lines: " . $linesAdded . "<br/>";
            echo "Non existing urls found: " . $notFoundUrls . "<br>";
            echo "Items updated: " . $itemsUpdated . "<br>";
        }
	
	private function importManufacturerStatistic($file = '')
	{
		if(strlen($file) > 0)
		{
			$handle = fopen($file, 'rt');
			if (!$handle)
			{
			    echo('File not opened!');
			    return FALSE;
			}
			$this->load->model('settings_model');
			$this->settings_model->deledtMatching();
			$this->load->model('imported_data_parsed_model');
			$all = 0;
			$changed = 0;
			$unchanged = 0;
			while (($d = fgetcsv($handle, 0, ',')) !== FALSE)
			{
				$all++;
				if(isset($d[3]) && $all > 1)
				{
					$c = $this->imported_data_parsed_model->updateManufacturerInfoByURL($d[0],$d[1],$d[2],$d[3]);
					if($c) $changed++; else $unchanged++;
				}
			}
			$all = $all -1;
			$time = time();
			$name = end(explode('/', $file));
			$notFoundUrls = $all - ($changed + $unchanged);
                        $this->settings_model->createManufacturerMatching("$name|$time|$all|$notFoundUrls|$changed|$unchanged|1");
		}
	}
	
	
	public function stopChecking()
	{
	     $this->load->model('settings_model');
             $this->load->model('temp_data_model');
	     $this->temp_data_model->emptyTable('notfoundurls');
             $this->temp_data_model->emptyTable('urlstomatch');
             $this->temp_data_model->emptyTable('updated_items');
             $this->settings_model->deledtMatching();
	     echo 'ok';
	}

        public function check_urls_threading($choosen_file = null) {
            if(!$choosen_file)
            {
                if(defined('CMD') && CMD )
                {
                    log_message('ERROR', __METHOD__ .' : File not defined ' );                
                    return;
                }
                $choosen_file = $this -> input -> post('choosen_file');
            }
            
            $command = 'cd ' . FCPATH . ' 
php cli.php crons match_urls_thread "' . $choosen_file . '" &';
            echo shell_exec($command), PHP_EOL;
        }
        

	function get_matching_urls() {
		$this -> load -> model('settings_model');
		$this -> load -> model('temp_data_model');
		$lines = $this -> settings_model -> getMatching();
		$json['response'] = "";
                $json['active'] = FALSE;
		if ($lines == FALSE) {
			$json['response'] = "There is no process.";
		} else {
			$json['response'] .= "<div>";
			foreach ($lines->result() as $row) {
				header("Last-Change: " . strtotime($row -> modified));
				$line = "<p>";
				if ($_SERVER['REQUEST_METHOD'] == 'HEAD')
					exit ;
				$ar = explode('|', $row -> description);
				$updated = $this -> temp_data_model -> getTableSize('updated_items');
				if (strtotime($row -> created) == strtotime($row -> modified) || count($ar) == 4) {
					//$ar = explode('|', $row->modified);
					//                    $line .= 'Created-'.strtotime($row->created).'; Modified-'.strtotime($row->modified)
					//                            .'; Count of ar-'.count($ar);
					$line .= "Matching started at: " . date('Y-m-d H:i:s', $ar[1]) . " currently in process.";
					$line .= '<br>Uploaded filename: ' . $ar[0];
					$line .= '<br># Matches Updated: ' . $updated;
					$line .= '<br># Matches Unchanged: ' . $ar[3];
                                        $json['active'] = TRUE;
				} elseif(isset($ar[5])){
					$line .= 'Total matching URLs imported: ' . $ar[2] . '</p>';
					$line .= '<p>'.'Uploaded filename: ' . $ar[0];
					$line .= '<br>URLs not found in imported_data_parsed: ' . $ar[3];
					$line .= '<br># Matches Updated: ' . $updated;
					$line .= '<br># Matches Unchanged: ' . $ar[5];
					$json['manufacturer'] = TRUE;
				} else {
					//                    $line .= 'Created-'.strtotime($row->created).'; Modified-'.strtotime($row->modified)
					//                            .'; Count of ar-'.count($ar);
					$line .= 'Total matching URLs imported: ' . $ar[2] . '</p><p>' . 'Uploaded filename: ' . $ar[0] . '<br>URLs not found in imported_data_parsed: ' . $ar[3] . '  ' . (intval($ar[3]) > 0 ? '<a id="download_not_founds"
                                href="' . base_url() . 'index.php/system/get_url_list">Download</a>' : '');
					$line .= '<br># Matches Updated: ' . $updated;
					$line .= '<br># Matches Unchanged: ' . $ar[5];
					$urls = $this -> temp_data_model -> getNotFount();
					$table = '';
					if ($urls) {
						$table = '<table><thead><tr><th>URLs</th></tr></thead><tbody>';
						foreach ($urls->result() as $url) {
							$table .= '<tr><td><a href="' . $url -> url . '">' . $url -> url . '</a></td></tr>';
						}
						$table .= '</tbody></table>';
					}
				}
				$line .= "</p>";
			}
			$json['response'] .= $line
			// . $table
			."</div>";
		}
		echo json_encode($json);
	}

	public function get_url_list() {
		$this -> load -> model('temp_data_model');
		$res = $this -> temp_data_model -> getNotFount();
		$array = array();
		$this -> temp_data_model -> download_send_headers("url_list.txt");
		$strTxt = '';
		if ($res) {
			foreach ($res->result() as $row) {
				//$array[]=$row->url;
				$strTxt .= $row -> url . "\r\n";
			}
		} else {
			$array[] = '';
		}
		echo $strTxt;
		//echo $this->temp_data_model->array2file($array);
	}

	public function set_kwsync_queue() {
		$id = $_POST['id'];
		$kw = $_POST['kw'];
		$url = $_POST['url'];
		$this -> load -> model('kwsync_queue_list_model');
		echo $id . ' - ' . $kw . ' - ' . $url;
		$this -> kwsync_queue_list_model -> insert($id, $kw, $url);
	}

	public function sync_keyword_status() {
		$this -> data['batches_list'] = $this -> system_batches_list();
		$this -> render();
	}

	public function stopQueue() {
		$file = realpath(BASEPATH . "../webroot/temp/sync_keyword_status.txt");
		file_put_contents($file, 0);
	}

	public function check_queue_count() {
		$file = realpath(BASEPATH . "../webroot/temp/sync_keyword_status.txt");
		$items = file_get_contents($file);
		echo 'Remaining ' . $items . ' items.';
	}
        
}
