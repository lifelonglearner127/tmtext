<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class SitemapProcessor {

	public function __construct() {
	}

	public function __get($var)	{
		return get_instance()->$var;
	}

	function isCompressed($url) {
		$matches = array();
		return preg_match('/.*\.gz$/', $url, $matches);
	}

	function pre_download($url){
		if ($this->isCompressed($url)) {
			$pre_download = 'compress.zlib://';
		} else {
			$pre_download = '';
		}
		return $pre_download.$url;
	}

	public function getURLs($site_url) {
		$this->load->library('Robots');
		$url = $site_url.'/robots.txt';
		$this->robots->robots($url);

		$result = array();
		$sitemaps = $this->robots->get_directive('*', 'sitemap');
		foreach($sitemaps as $sitemap) {
			$xml = file_get_contents($this->pre_download($sitemap));

			$obj = new SimpleXMLElement($xml);
			if ($obj->getName() == 'sitemapindex') {
				foreach ($obj->sitemap as $xml_sitemap) {
					$real_xml = file_get_contents($this->pre_download($xml_sitemap->loc));
					$real_obj = new SimpleXMLElement($real_xml);
					if ($real_obj->getName() == 'urlset') {
						foreach ($real_obj->url as $url) {
							$result[] = ''.$url->loc;
						}
					}
				}
			} else if ($obj->getName() == 'urlset') {
				foreach ($obj->url as $url) {
					$result[] = ''.$url->loc;
				}
			}
		}

		return $result;
	}

}