<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Editor extends MY_Controller {

	function __construct()
 	{
  		parent::__construct();

		$this->load->helper('HTML');
		$this->load->helper('form');

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

	public function search($s=null)
	{
		$s = 'UN40ES6500';
		//$s = '47G2';

		$data = array(
			'search_results' => array(
		            '<a href="#">LG 43" Edge-Lit LED HDTV 1080p 60Hz</a><br/>
					This 42" full HD 1080p HDTV oﬀers a superior 1,000,000:1 contrast ratio and a 60Hz refresh rate for
					impressive picture quality. Color and black levels come through like you\'ve never seen before on...',
		            '<a href="#">LG 42" Edge-Lit LED HDTV 1080p 60Hz</a><br/>
					This 42" full HD 1080p HDTV oﬀers a superior 1,000,000:1 contrast ratio and a 60Hz refresh rate for
					impressive picture quality. Color and black levels come through like you\'ve never seen before on...',
		            '<a href="#">LG 42" Edge-Lit LED HDTV 1080p 60Hz</a><br/>
					This 42" full HD 1080p HDTV oﬀers a superior 1,000,000:1 contrast ratio and a 60Hz refresh rate for
					impressive picture quality. Color and black levels come through like you\'ve never seen before on...',
	            )
		);

		$data = array(
			'search_results' => array()
		);

		$attr_path = $this->config->item('attr_path');

		$csv_rows = array();

		if ($path = realpath($attr_path)) {
			$objects = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($path), RecursiveIteratorIterator::SELF_FIRST);
			foreach($objects as $name => $object){
				if (!$object->isDir()) {
					if (preg_match("/.*\.csv/",$object->getFilename(),$matches)) {
						if (($handle = fopen($name, "r")) !== FALSE) {
    						while (($row = fgetcsv($handle, null, ",", "\"")) !== FALSE) {
    							foreach ($row as $content) {
    								if (preg_match("/$s/",$content,$matches)) {
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
			foreach($csv_rows as $row) {
				foreach ($row as $col) {
					if (preg_match("/^http:\/\/*/",$col,$matches)) {
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
			}
		}

		$this->load->library('pagination');

		$ci=& get_instance();
		echo $ci->config->site_url();
		$query = $_SERVER['QUERY_STRING'] ? '?'.$_SERVER['QUERY_STRING'] : '';
		echo $ci->config->site_url().'/'.$ci->uri->uri_string(). $query;

		//$config['base_url'] = 'http://example.com/index.php/test/page/';
		$pagination_config['total_rows'] = count($data['search_results']);
		$pagination_config['per_page'] = 3;
		$pagination_config['use_page_numbers'] = true;
		//$pagination_config['page_query_string'] = TRUE;

		$this->pagination->initialize($pagination_config);

		echo $this->pagination->create_links();


		$this->load->view('editor/search',$data);
	}

	public function attributes($s=null)
	{
		$s = 'UN40ES6500';

		$data = array('search_results'=>'');

		//$this->config->set_item('item_name', 'item_value');

		$attr_path = $this->config->item('attr_path');

		if ($path = realpath($attr_path)) {
			$objects = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($path), RecursiveIteratorIterator::SELF_FIRST);
			foreach($objects as $name => $object){
				//var_dump($name); continue;
				if (!$object->isDir()) {
					if ($object->getFilename() == 'attributes.dat') {
						if($content= file_get_contents($name)) {
							if (preg_match("/$s/",$content,$matches)) {
								$data['search_results'] = $content;
								break;
							}
						}
					}
				}
			}
		}
		$this->load->view('editor/attributes',$data);

	}
}
