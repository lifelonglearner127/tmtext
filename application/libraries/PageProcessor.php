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

			// hiding useragent
        	$this->curl->option('USERAGENT', 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12');

        	// TODO: add caching
			if ($this->html = $this->curl->simple_get($this->url)) {
				$this->nokogiri = new nokogiri($this->html);
				return true;
			}
			$this->curl->debug();
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
			$part = explode('.', str_ireplace(array('www.','www1.'),'', $part[0]));
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

	public function attributes() {
		$methodName = 'attributes_'.$this->hostName;

		if	( method_exists($this, $methodName) ) {
			$result = $this->$methodName();
			foreach ($result as &$value) {
				$value = trim($value);
			}

			if (!empty($result)) {
        		return $result;
			}
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
			$description[] = $item['#text'][0];
		}

		foreach($this->nokogiri->get('#prodInfoSpaceBottom div') as $item) {
			if ($item['itemprop'] == 'description') {
				foreach($item['div'] as $i) {
					if (isset($i['p']) && isset($i['p'][0]) && isset($i['p'][0]['#text'])) {
						foreach ($i['p'][0]['#text'] as $j) {
							$description[] = $j;
						}
					}
				}
			}
		}

		$description = implode(' ', $description);

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
			'Description' => $description,
			'Price' => $price,
			'Features' => $features
		);
	}

	public function meta_walmart(){
		return $this->nokogiri->get('meta')->toArray();
	}

	public function attributes_walmart() {
		$result = array();

		foreach($this->nokogiri->get('.SpecTable tr') as $item) {
			if (stripos($item['td'][0]["#text"][0], 'model no')!==false) {
				$result['model'] =  trim($item['td'][1]["#text"][0]);
			}
		}

		foreach($this->nokogiri->get('h1.productTitle') as $item) {
			if (isset($result['model']) && !empty($result['model'])) {
				$s = split($result['model'], $item['#text'][0]);
				if (isset($s[0]) && !empty($s[0]) && $s[0]!=$item['#text'][0]) {
					$result['manufacturer'] = $s[0];
				}
			}
		}

		foreach($this->nokogiri->get('meta') as $item){
			if($item['itemprop'] == 'productID') {
				$result['UPC/EAN/ISBN'] =  trim($item['content']);
			}
		}

		return $result;
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

	public function attributes_tigerdirect() {
		$result = array();

		foreach($this->nokogiri->get('ul.pInfo li:first-child') as $item) {
			if (stripos($item["#text"][0], 'manufactured by')!==false) {
				$result['manufacturer'] =  trim($item['strong'][0]["#text"][0]);
			}
			if (stripos($item["#text"][3], 'mfg part no')!==false) {
				$result['model'] =  trim($item["b"][0]["#text"][0]);
			}
		}

		return $result;
	}

	public function process_sears() {
		foreach($this->nokogiri->get('#productDetails #desc p') as $item) {
			foreach($item['#text'] as $i) {
				$description[] = $i;
			}
		}
		$description = implode(' ',$description);

		foreach($this->nokogiri->get('#productDetails #desc .desc1more') as $item) {
			$descriptionLong = $item;
		}

		foreach($this->nokogiri->get('.productName h1') as $item) {
			$title = $item['#text'][0];
		}

		return array(
			'Product Name' => $title,
			'Description' => $description,
			'Long_Description' => $descriptionLong['#text'][0]
		);
	}

	public function attributes_sears() {
		$result = array();

		foreach($this->nokogiri->get('meta') as $item){
			if($item['name'] == 'keywords') {
				$i = split(',',$item['content']);
				$result['manufacturer'] =  trim($i[1]);
			}
		}

		foreach($this->nokogiri->get('.productName small span') as $item) {
			if (isset($item['itemprop']) && $item['itemprop']=='model') {
				$result['model'] =  trim(preg_replace("/[^A-Za-z0-9\- ]/", '',$item['#text'][0]));
			}
		}

		return $result;
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

	public function attributes_staples() {
		$result = array();

		foreach($this->nokogiri->get('.productDetails h1') as $item) {
			$s = split(' ', trim($item['#text'][0]));
			if (isset($s[0]) && !empty($s[0])) {
				$result['manufacturer'] = $s[0];
			}
		}

		foreach($this->nokogiri->get('#skuspecial .productDetails .itemModel') as $item) {
			if (stripos($item['#text'][0], 'model')!==false) {
				$s = split('Model:', trim($item['#text'][0]));
				$result['model'] =  trim($s[1]);
			}
		}

		return $result;
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

	public function attributes_overstock() {
		$result = array();

		foreach($this->nokogiri->get('#related_cats .bd ul li ') as $item) {

			if (stripos($item['#text'][0], 'brand')!==false) {
				$s = split(',',$item['a'][0]['#text'][0]);
				$result['manufacturer'] =  trim($s[0]);
			}
		}

		foreach($this->nokogiri->get('.description-extra-data #details_descMisc dl') as $item) {
			foreach($item["dt"] as $key=>$dt){
				if (stripos($dt['#text'][0], 'model no')!==false) {
					$result['model'] =  trim($item["dd"][$key]['#text'][0]);
				}
			}
		}

		return $result;
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

		foreach($this->nokogiri->get('div#skuDetails .sku_desc p') as $item) {
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

		foreach($this->nokogiri->get('div#skuHeading h1') as $item) {
			$title = $item;
		}

		foreach($this->nokogiri->get('.sku_det table tr') as $item) {
			$features[] = $item['th'][0]['#text'][0].' - '.$item['td'][0]['#text'][0];
		}
		$features = implode(' ',$features);

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

	public function attributes_officedepot(){
		$result = array();

		foreach($this->nokogiri->get('.sku_det table tr') as $item) {
			if ($item['th'][0]['#text'][0] =='manufacturer' ) {
				$result['manufacturer'] = preg_replace("/[^A-Za-z0-9\- ]/", '',$item['td'][0]['#text'][0]);
			}
			if ($item['th'][0]['#text'][0] =='model name' ) {
				$result['model'] = preg_replace("/[^A-Za-z0-9\- ]/", '',$item['td'][0]['#text'][0]);
			}
		}

		return $result;
	}

	public function process_bestbuy(){
		foreach($this->nokogiri->get('div#productsummary h1') as $item) {
			$title = $item['#text'][0];
		}

		if (empty($description)) {
			foreach($this->nokogiri->get('div#sku-title h1') as $item) {
				$title = $item['#text'][0];
			}
		}

		foreach($this->nokogiri->get('#tabbed-overview .csc-medium-column p') as $item) {
			$line = trim($item['#text'][0]);
			if (!empty($line)) {
				$description[] = $line;
			}
		}

		if (empty($description)) {
			foreach($this->nokogiri->get('#tabbed-bundle-overview p') as $item) {
				$line = trim($item['#text'][0]);
				if (!empty($line)) {
					$description[] = $line;
				}
			}
		}

		if (empty($description)) {
			foreach($this->nokogiri->get('#long-description') as $item) {
				$line = trim($item['#text'][0]);
				if (!empty($line)) {
					$description[] = $line;
				}
			}
		}

		$description = implode(' ',$description);

		foreach($this->nokogiri->get('#tabbed-overview .csc-medium-column ul li') as $item) {
			if (isset($item['b'])) {
				$features[] =  $item['b'][0]['#text'][0].' - '.$item['#text'][0];
			}
		}

		foreach($this->nokogiri->get('#tabbed-bundle-overview ul li') as $item) {
			$features[] =  trim($item['#text'][0]);
		}

		foreach($this->nokogiri->get('#features .feature') as $item) {
			$features[] = trim($item['h4'][0]['#text'][0]).' - '.trim($item['p'][0]['#text'][0]);
		}

		$features = implode("\n",$features);

		foreach($this->nokogiri->get('#priceblock #saleprice .price') as $item) {
			if (preg_match('/\$([0-9]+[\.]*[0-9]*)/', $item['#text'][0], $match)) {
				$price = $match[1];
			}
		}

		foreach($this->nokogiri->get('#price #priceblock-wrapper .priceblock .item-price') as $item) {
			$price = str_replace(',','',$item['#text'][0]);
		}


		$result = array(
			'Product Name' => $title,
			'Description' => $description,
//			'Long_Description' => $description_long,
			'Features' => $features,
			'Price' => $price
		);

		foreach ($result as $key => $value) {
			if (empty($result[$key])) {
				unset($result[$key]);
			}
		}

		return $result;
	}

	public function attributes_bestbuy() {
		$result = array();

		foreach($this->nokogiri->get('div#productsummary h1') as $item) {
			$s = split('-',$item['#text'][0]);
			$result['manufacturer'] =  trim($s[0]);
		}

		foreach($this->nokogiri->get('div#sku-title h1') as $item) {
			$s = split('-',$item['#text'][0]);
			$result['manufacturer'] =  trim($s[0]);
		}

		foreach($this->nokogiri->get('div#productsummary h2 span') as $item) {
			if (isset($item['itemprop']) && $item['itemprop']=='model') {
				$result['model'] =  trim($item['#text'][0]);
			}
		}

		foreach($this->nokogiri->get('li.model-number #model-value') as $item) {
			$result['model'] =  trim($item['#text'][0]);
		}

		return $result;
	}

	public function process_amazon(){
		foreach($this->nokogiri->get('h1.parseasinTitle span') as $item) {
			$title = $item['#text'][0];
		}

		foreach($this->nokogiri->get('.content .productDescriptionWrapper .productDescriptionWrapper') as $item) {
			$line = trim($item['#text'][0]);
			if (!empty($line)) {
				$description[] = $line;
			}
		}

		if (empty($description)) {
			foreach($this->nokogiri->get('.content .productDescriptionWrapper .aplus .aplus p') as $item) {
				$line = trim($item['#text'][0]);
				if (!empty($line)) {
					$description[] = $line;
				}
			}
		}

		$description = implode(' ',$description);

		return array(
			'Product Name' => $title,
			'Description' => $description,
		);
	}

	public function attributes_amazon() {
		$result = array();

		foreach($this->nokogiri->get('#technical-data ul li') as $item) {
			if (stripos($item['b'][0]['#text'][0], 'brand name') !==false ) {
				$result['manufacturer'] =  trim(str_replace(':','',$item['#text'][0]));
			}
			if (stripos($item['b'][0]['#text'][0], 'model') !==false ) {
				$result['model'] =  trim(str_replace(':','',$item['#text'][0]));
			}
		}

		foreach($this->nokogiri->get('#detail-bullets table td.bucket ul li') as $item) {
			if (stripos($item['b'][0]['#text'][0], 'item model number') !==false ) {
				$result['model'] =  trim($item['#text'][0]);
			}
		}

		return $result;
	}

	public function process_toysrus(){
		foreach($this->nokogiri->get('#rightSide h1') as $item) {
			$title = $item['#text'][0];
		}

		foreach($this->nokogiri->get('#infoPanel dl dd:first-child p') as $item) {
			foreach($item['#text'] as $i) {
				$line = trim($i);
				if (!empty($line)) {
					$description[] = $line;
				}
			}
		}

		$description = implode(' ',$description);


		foreach($this->nokogiri->get('#buyWrapper #price .retail span') as $item) {
			if (preg_match('/\$([0-9]+[\.]*[0-9]*)/', $item['#text'][0], $match)) {
				$price = $match[1];
			}
		}

		return array(
			'Product Name' => $title,
			'Description' => $description,
			'Price' => $price
		);
	}

	public function attributes_toysrus() {
		$result = array();

		foreach($this->nokogiri->get('#rightSide h3 label') as $item) {
			$result['manufacturer'] =  trim($item['#text'][0]);
		}

		foreach($this->nokogiri->get('#infoPanel dl dd#additionalInfo p.upc span') as $item) {
			$result['UPC/EAN/ISBN'] =  trim($item['#text'][0]);
		}

		return $result;
	}

	public function process_bloomingdales(){
		foreach($this->nokogiri->get('#productDescription h1#productTitle') as $item) {
			$title = $item['#text'][0];
		}

		foreach($this->nokogiri->get('#pdp_tabs .pdp_longDescription') as $item) {
			foreach($item['#text'] as $i) {
				$line = trim($i);
				if (!empty($line)) {
					$description[] = $line;
				}
			}
		}

		$description = implode(' ',$description);

		foreach($this->nokogiri->get('#pdp_tabs #pdp_tabs_body_left ul li') as $item) {
			$features[] = trim($item['#text'][0]);
		}

		$features = implode("\n",$features);

		foreach($this->nokogiri->get('#productDescription .priceSale .priceBig') as $item) {
			if (preg_match('/\$([0-9]+[\.]*[0-9]*)/', $item['#text'][0], $match)) {
				$price = $match[1];
			}
		}

		return array(
			'Product Name' => $title,
			'Description' => $description,
			'Price' => $price,
			'Features' => $features
		);
	}
}

?>