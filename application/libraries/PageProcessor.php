<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class PageProcessor {

	private $url = '';
	private $html = '';
	private $hostName = '';
	private $nokogiri;

	public function __construct() {
		$this->load->library('nokogiri', null, 'noko');
	}

	public function __get($var)
	{
		return get_instance()->$var;
	}

	public function loadHtml($html) {
		$this->html = $html;
		$this->nokogiri = new nokogiri($this->html);
	}

	public function loadUrl($url) {
		if ($this->isURL($url)) {
			if (stripos($url, 'http://') === false) {
				$url = 'http://'.$url;
			}
			$this->url = $url;
			$this->hostName = $this->getDomainPart($url);

			$this->load->library('curl');

			// Load cookies, etc.
			$methodName = 'pre_'.$this->hostName;
			if	( method_exists($this, $methodName) ) {
        		$this->$methodName();
        	}

        	// TODO: add caching
			if ($this->html = $this->curl->simple_get($this->url)) {
				$this->nokogiri = new nokogiri($this->html);
				return true;
			}
		}
		return false;
	}

	public function get_data($url) {
		if ($this->loadURL($url)) {
			return $this->process();
		}
		return false;
	}

	public function get_html() {
		return $this->html;
	}

	public function getDomainPart($url) {
		$part = explode('/', str_ireplace(array('http://','https://'),'', $url));
		if (!empty($part[0]) && strpos($part[0], '.') !== false) {
			$part = explode('.', str_ireplace(array('www.'),'', $part[0]));
		} else {
			return false;
		}
		return (!empty($part[0]) ? $part[0] : false);
	}

	public function isURL($url) {
		$regex = "(?i)\b((?:[a-z][\w-]+:(?:\/{1,3}|[a-z0-9%])|www\d{0,3}[.]|([a-z0-9.\-]+)[.][a-z]{2,4}\/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))";
		return preg_match_all("/".$regex."/i", $url, $matches);
	}

	public function process() {
		$methodName = 'process_'.$this->hostName;

		if	( method_exists($this, $methodName) ) {
			$result = $this->$methodName();
			foreach ($result as &$value) {
				$value = trim($value);
			}
        	return $result;
        }

        return false;
	}

	public function meta() {
		$methodName = 'meta_'.$this->hostName;

		if	( method_exists($this, $methodName) ) {
        	return $this->$methodName();
        }

        return $this->nokogiri->get('meta')->toArray();
	}

	public function process_walmart() {
		foreach($this->nokogiri->get('.ql-details-short-desc') as $item) {
			$description = $item;
		}

		foreach($this->nokogiri->get('h1.productTitle') as $item) {
			$title = $item;
		}

		$price = '';
		foreach($this->nokogiri->get('.PricingInfo .camelPrice span') as $item) {
			$price .= $item['#text'][0];
		}

		if (preg_match('/\$([0-9]+[\.]*[0-9]*)/', $price, $match)) {
				$price = $match[1];
		}

		foreach($this->nokogiri->get('.SpecTable tr') as $item) {
			$features[] = trim($item['td'][0]['#text'][0]).trim($item['td'][1]['#text'][0]);
		}
		$features = implode("\n",$features);

		return array(
			'Product Name' => $title['#text'][0],
			'Description' => $description['#text'][0],
			'Price' => $price,
			'Features' => $features
		);
	}

	public function meta_walmart(){
		return $this->nokogiri->get('meta')->toArray();
	}

	public function process_tigerdirect() {
		foreach($this->nokogiri->get('.shortDesc p') as $item) {
			if (isset($item['#text'])) {
				foreach($item['#text'] as $text) {
					$description[] = $text;
				}
			}
		}
		$description = implode(' ',$description);

		foreach($this->nokogiri->get('.prodName h1') as $item) {
			$title = $item;
		}

		foreach($this->nokogiri->get('.contentMain .prodInfo .priceToday .salePrice') as $item) {
			$price = $item['sup'][0]['#text'][0] . $item['#text'][0]. '.' . $item['sup'][1]['#text'][0];
			if (preg_match('/\$([0-9]+[\.]*[0-9]*)/', $price, $match)) {
				$price = $match[1];
			}
		}

		foreach($this->nokogiri->get('#DetailedSpecs table.prodSpec tr') as $item) {
			$i = trim($item['th'][0]['#text'][0]);
			$j = trim($item['td'][0]['#text'][0]);
			if (!empty($i) && !empty($j)) {
				$features[] = $i.": ".$j;
			} else if (!empty($j)) {
				$features[] = $j;
			}
		}
		$features = implode("\n",$features);

		return array(
			'Product Name' => $title['#text'][0],
			'Description' => $description,
			'Price' => $price,
			'Features' => $features
		);
	}

	public function process_sears() {
		foreach($this->nokogiri->get('#productDetails #desc p') as $item) {
				$description[] = $item['#text'][0];
		}
		$description = implode(' ',$description);

		foreach($this->nokogiri->get('#productDetails #desc .desc1more') as $item) {
			$descriptionLong = $item;
		}

		foreach($this->nokogiri->get('.productName h1') as $item) {
			$title = $item;
		}

		return array(
			'Product Name' => $title['#text'][0],
			'Description' => $description['#text'][0],
			'Long_Description' => $descriptionLong['#text'][0]
		);
	}

	public function pre_staples(){
		$vars = array('zipcode'=>'94129');
		$this->curl->set_cookies($vars);
	}

	public function process_staples(){
		foreach($this->nokogiri->get('.skuShortDescription') as $item) {
			$description = $item;
		}

		foreach($this->nokogiri->get('.skuHeadline') as $item) {
			$descriptionShort = $item;
		}

		foreach($this->nokogiri->get('.productDetails h1') as $item) {
			$title = $item;
		}

		foreach($this->nokogiri->get('.skuWrapper #SkuForm .priceTotal .finalPrice b i') as $item) {
			if (preg_match('/\$([0-9]+[\.]*[0-9]*)/', $item['#text'][0], $match)) {
				$price = $match[1];
			}
		}

		foreach($this->nokogiri->get('#subdesc_content .layoutWidth06 ul li') as $item) {
			$features[] = $item['#text'][0];
		}
		$features = implode("\n",$features);

		return array(
			'Product Name' => $title['#text'][0],
			'Long_Description' => $description['#text'][0],
			'Description' => $descriptionShort['#text'][0],
			'Price' => $price,
			'Features' => $features
		);
	}

	public function process_audible(){
		foreach($this->nokogiri->get('.disc-summary .adbl-content p') as $item) {
			$description[] = $item['#text'][0];
		}
		$description = implode(' ',$description);

		foreach($this->nokogiri->get('h1.adbl-prod-h1-title') as $item) {
			$title = $item;
		}
		foreach($this->nokogiri->get('.adbl-prod-detail-main .adbl-price-content .adbl-reg-price') as $item) {
			if (preg_match('/\$([0-9]+[\.]*[0-9]*)/', $item['#text'][0], $match)) {
				$price = $match[1];
			}
		}

		return array(
			'Product Name' => $title['#text'][0],
			'Description' => $description,
			'Price' => $price
		);
	}

	public function process_parties(){
		foreach($this->nokogiri->get('div.panel div.section-container div.readMore') as $item) {
			$description[] = $item['#text'][0];
		}
		$description = implode(' ',$description);

		foreach($this->nokogiri->get('h1.mainHeading') as $item) {
			$title = $item;
		}

		foreach($this->nokogiri->get('.mainProduct .mainPrice strong') as $item) {
			if (preg_match('/\$([0-9]+[\.]*[0-9]*)/', $item['#text'][0], $match)) {
				$price = $match[1];
			}
		}

		return array(
			'Product Name' => $title['#text'][0],
			'Description' => $description,
			'Price' => $price
		);
	}

	public function process_overstock(){
		foreach($this->nokogiri->get('#mainCenter_priceDescWrap ul') as $item) {
			$description[] = $item['#text'][0];
		}
		$description = implode(' ',$description);

		foreach($this->nokogiri->get('#prod_tabs #tab-Wrapper #description-text #details_descFull') as $item) {
			$description_long[] = $item['#text'][0];
		}
		foreach($this->nokogiri->get('#prod_tabs #tab-Wrapper #description-text #details_descFull ul li') as $item) {
			$description_long[] = $item['#text'][0];
		}

		$description_long = implode(' ',$description_long);

		foreach($this->nokogiri->get('#prod_mainCenter div h1') as $item) {
			$title = $item;
		}

		foreach($this->nokogiri->get('#prod_mainCenter .main-price-red') as $item) {
			if (preg_match('/\$([0-9]+[\.]*[0-9]*)/', $item['#text'][0], $match)) {
				$price = $match[1];
			}
		}

		foreach($this->nokogiri->get('#productAttributes .bd ul li') as $item) {
			$features[] = trim($item['div'][0]['#text'][0]).': '.trim($item['div'][1]['#text'][0]);
		}

		$features = implode("\n",$features);

		return array(
			'Product Name' => $title['#text'][0],
			'Description' => $description,
			'Long_Description' => $description_long,
			'Price' => $price,
			'Features' => $features
		);
	}

	public function process_officemax(){
		foreach($this->nokogiri->get('#productTabs .tabContentWrapper .details') as $item) {
			$description[] = $item['#text'][0];
		}
		$description = implode(' ',$description);

//		foreach($this->nokogiri->get('#productTabs .tabContentWrapper .details ul.featuressku li span') as $item) {
//			$description_long[] = $item['#text'][0];
//		}
//		$description_long = implode(' ',$description_long);

		foreach($this->nokogiri->get('#productTabs .tabContentWrapper .details ul.featuressku li span') as $item) {
			$features[] = $item['#text'][0];
		}
		$features = implode(' ',$features);

		foreach($this->nokogiri->get('#main_sku_wrap .skuHeading') as $item) {
			$title = $item;
		}

		foreach($this->nokogiri->get('#main_sku_wrap .skuPrice') as $item) {
			if (preg_match('/\$([0-9]+[\.]*[0-9]*)/', $item['#text'][0], $match)) {
				$price = $match[1];
			}
		}

		return array(
			'Product Name' => $title['#text'][0],
			'Description' => $description,
//			'Long_Description' => $description_long,
			'Features' => $features,
			'Price' => $price
		);
	}

	public function process_officedepot(){
		foreach($this->nokogiri->get('div.skuHeading longBulletTop i') as $item) {
			$description[] = $item['#text'][0];
		}
		foreach($this->nokogiri->get('div.skuHeading longBulletTop ul li') as $item) {
			$description[] = $item['#text'][0];
		}
		$description = implode(' ',$description);

		foreach($this->nokogiri->get('#productTabs .sku_desc b') as $item) {
			$description_long[] = $item['#text'][0];
		}
		foreach($this->nokogiri->get('#productTabs .sku_desc ul li b') as $item) {
			$description_long[] = $item['#text'][0];
		}
		$description_long = implode(' ',$description_long);

		foreach($this->nokogiri->get('div.skuHeading h1') as $item) {
			$title = $item;
		}

		foreach($this->nokogiri->get('#skuTop #purchaseBlock .your_price .price .price_amount') as $item) {
			if (preg_match('/\$([0-9]+[\.]*[0-9]*)/', $item['#text'][0], $match)) {
				$price = $match[1];
			}
		}

		return array(
			'Product Name' => $title['#text'][0],
			'Description' => $description,
			'Long_Description' => $description_long,
			'Price' => $price
		);
	}
}

?>