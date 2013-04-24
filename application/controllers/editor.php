<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Editor extends MY_Controller {

	function __construct()
 	{
  		parent::__construct();

		$this->load->helper('HTML');
		$this->load->helper('form');

		//$this->config->set_item('item_name', 'item_value');
 	}

	public function index()
	{
		$header = array(
        	'title' => 'Editor',
			'heading' => 'Editor'
        );

		$this->load->view('header', $header);
		$this->load->view('editor/index');
		$this->load->view('footer');
	}

	public function save()
	{

	}

	public function search()
	{

		if (empty($s)) $s = $this->input->post('s');

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
						if (($handle = fopen($name, "r")) !== FALSE) {
    						while (($row = fgetcsv($handle, null, ",", "\"")) !== FALSE) {
    							foreach ($row as $content) {
    								if (preg_match("/$s/i",$content,$matches)) {
    									$csv_rows[] = $row;
    								}
    							}
    						}
						}
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
				} else {
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

	public function attributes()
	{

		if (empty($s)) $s = $this->input->post('s');

		$data = array('search_results'=>'', 'file_id'=>'', 'product_descriptions' => '', 'product_title' => '');
		$attributes = array();

		$attr_path = $this->config->item('attr_path');

		if ($path = realpath($attr_path)) {
			$objects = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($path), RecursiveIteratorIterator::SELF_FIRST);
			foreach($objects as $name => $object){
				if (!$object->isDir()) {
					if ($object->getFilename() == 'attributes.dat') {
						if($content= file_get_contents($name)) {
							if (preg_match("/$s/i",$content,$matches)) {

								$part = str_ireplace($attr_path, '', $object->getPath());
								if (preg_match('/\D*(\d*)/i',$part,$matches)) {
									$data['file_id'] = $matches[1];
								}

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

		$descCmd = str_replace('', $data['file_id'] ,$this->config->item('descCmd'));
		if($result = shell_exec('cd '.$this->config->item('cmd_path').'; ./'.$descCmd)) {
			if (preg_match_all('/\(.*\)\: "(.*)"/i',$result,$matches) && isset($matches[1]) && count($matches[1])>0) {
				$data['product_descriptions'] = $matches[1];
			}
		}

		$this->load->view('editor/attributes',$data);

	}
}
