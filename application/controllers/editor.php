<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Editor extends MY_Controller {

	function __construct()
 	{
  		parent::__construct();

  		//$this->load->library('ion_auth');
  		$this->load->library('form_validation');
		//$this->config->set_item('item_name', 'item_value');
		$this->data['title'] = 'Editor';

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

	public function save()
	{

	}

	public function search()
	{
		$this->form_validation->set_rules('s', 'Search', 'required|alpha_dash|xss_clean');
		if ($this->form_validation->run() == true) {

			$s = $this->input->post('s');

			$this->load->library('pagination');
			$pagination_config['base_url'] = $this->config->site_url().'/editor/search';
			$pagination_config['per_page'] = 0;

			$data = array(
				's' => $s,
				'search_results' => array()
			);

			$attr_path = $this->config->item('attr_path');

			$csv_rows = array();

			if ($path = realpath($attr_path)) {
				$objects = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($path), RecursiveIteratorIterator::SELF_FIRST);
				foreach($objects as $name => $object){
					if (!$object->isDir()) {
						if (preg_match("/.*\.csv/i",$object->getFilename(),$matches)) {
							$_rows = array();
							if (($handle = fopen($name, "r")) !== FALSE) {
								while (($row = fgets($handle)) !== false) {
									if (preg_match("/$s/i",$row,$matches)) {
										$_rows[] = $row;
									}
								}
							}
							fclose($handle);

							foreach (array_keys(array_count_values($_rows)) as $row){
								$csv_rows[] = str_getcsv($row, ",", "\"");
							}
							unset($_rows);
						}
					}
				}
			}

			if (!empty($csv_rows)) {
				$current_row = 0;
				foreach($csv_rows as $row) {
					if ($current_row < (int)$this->uri->segment(3)) {
						$current_row++;
						continue;
					}
					foreach ($row as $col) {
						if (preg_match("/^http:\/\/*/i",$col,$matches)) {
							$row['url'] = $col;
						} else if ( mb_strlen($col) <= 250) {
							$row['title'] = $col;
						} else if (empty($row['description'])){
							$row['description'] = substr($col, 0, strpos(wordwrap($col, 200), "\n"));

						}
					}

					if (!empty($row['url']) && !empty($row['title'])) {
						$data['search_results'][] =  '<a href="'.$row['url'].'">'.$row['title'].'</a><br/>'.$row['description'];
					} else if (!empty($row['description'])) {
						$data['search_results'][] =  $row['description'];
					}
					if (count($data['search_results']) == $pagination_config['per_page']) break;
				}
			}

			$pagination_config['total_rows'] = count($csv_rows);
			$this->pagination->initialize($pagination_config);
			$data['pagination']= $this->pagination->create_links();

			$this->load->view('editor/search',$data);
		}
	}

	public function attributes()
	{
		$this->form_validation->set_rules('s', 'Search', 'required|alpha_dash|xss_clean');

		if ($this->form_validation->run() == true) {
			$s = $this->input->post('s');

			$data = array('search_results'=>'', 'file_id'=>'', 'product_descriptions' => '', 'product_title' => '');
			$attributes = array();

			$attr_path = $this->config->item('attr_path');

			if ($path = realpath($attr_path)) {
				$objects = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($path), RecursiveIteratorIterator::SELF_FIRST);
				foreach ($objects as $name => $object){
					if (!$object->isDir()) {
						if ($object->getFilename() == 'attributes.dat') {
							if ($content= file_get_contents($name)) {
								if (preg_match("/$s/i",$content,$matches)) {

									$part = str_ireplace($attr_path, '', $object->getPath());
									if (preg_match('/\D*(\d*)/i',$part,$matches)) {
										$data['file_id'] = $matches[1];
									}

									$content = str_replace(array_keys($this->config->item('attr_replace')), array_values($this->config->item('attr_replace')), $content);
									$data['search_results'] = $content;

									if (preg_match_all('/\s?(\S*)\s*(.*)/i', $content, $matches)) {
										foreach($matches[1] as $i=>$v) {
											if (!empty($v))
											$attributes[strtolower($v)] = $matches[2][$i];
										}
									}

									if (!empty($attributes)) {
										$title = array();
										foreach ($this->config->item('product_title') as $v) {
											if (isset($attributes[$v]))
												$title[] = $attributes[$v];
										}
										$data['product_title'] = implode(' ', $title);
									}
									break;
								}
							}
						}
					}
				}
			}

			$descCmd = str_replace($this->config->item('cmd_mask'), $data['file_id'] ,$this->config->item('descCmd'));
//			if($result = shell_exec('cd '.$this->config->item('cmd_path').'; '.$descCmd)) {
			if($result = shell_exec('cd '.$this->config->item('cmd_path').'; ./'.$descCmd)) {
				if (preg_match_all('/\(.*\)\: "(.*)"/i',$result,$matches) && isset($matches[1]) && count($matches[1])>0) {
					$data['product_descriptions'] = $matches[1];
				}
			}

			$this->load->view('editor/attributes',$data);
		}
	}
}
