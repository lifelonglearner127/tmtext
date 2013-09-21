<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class PageProcessor {

	private $url = '';
	private $html = '';
	private $hostName = '';
	private $nokogiri;
	private $allowed_meta = array(
					'name' => array('description', 'keywords')
				);

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
			$part = explode('.', str_ireplace(array('www.','www1.','shop.','-'),'', $part[0]));
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

			foreach ($result as $k => $v) {
				if (empty($result[$k])) {
					unset($result[$k]);
				}
			}

			$result['Date'] = date("Y-m-d H:i:s");

        	return $result;
        }

        return false;
	}

	public function attributes() {
		$methodName = 'attributes_'.$this->hostName;

		if	( method_exists($this, $methodName) ) {
			$result = $this->$methodName();
			foreach ($result as &$value) {
				if (!is_array($value)) {
					$value = trim($value);
				}
			}

			if (!empty($result)) {
        		return $result;
			}
        }

        return false;
	}

	public function meta($full=false) {
		$methodName = 'meta_'.$this->hostName;

		if	( method_exists($this, $methodName) ) {
        	$result = $this->$methodName();
        } else {
        	$result = $this->nokogiri->get('meta')->toArray();
        }

		if ($full) {
			return $result;
		}

        $results = array();
        foreach ($result as $e) {
        	foreach ($this->allowed_meta as $k=>$v) {
        		if (isset($e[$k]) && in_array(strtolower($e[$k]), $v)) {
					$l = trim($e['content']);
        			if (!empty($l)) {
						$results[$e[$k]] = $l;
        			}
        		}
        	}
        }

        if (!empty($results)) {
        	return $results;
        } else {
        	return false;
        }
	}

	public function process_walmart() {
		foreach($this->nokogiri->get('.ql-details-short-desc') as $item) {
			$description[] = $item['#text'][0];
		}

		foreach($this->nokogiri->get('.ql-details-short-desc p') as $item) {
			$description[] = $item['#text'][0];
		}

		foreach($this->nokogiri->get('#prodInfoSpaceBottom div') as $item) {
			if ($item['itemprop'] == 'description') {
				foreach($item['div'] as $i) {
					if (isset($i['p']) && isset($i['p'][0]) && isset($i['p'][0]['#text'])) {
						foreach ($i['p'][0]['#text'] as $j) {
							$description[] = $j;
						}
					} elseif (isset($i['#text'])) {
						foreach ($i['#text'] as $j) {
							$description[] = $j;
						}
					}
				}
			}
		}

		foreach($this->nokogiri->get('div.BodyXL div') as $item) {
			foreach ($item['#text'] as $i) {
				$description[] = trim($i);
			}
		}

		$description = implode(' ', $description);

		foreach($this->nokogiri->get('h1.productTitle') as $item) {
			$title = $item;
		}

		$price = '';
		foreach($this->nokogiri->get('.PricingInfo .camelPriceSAC span') as $item) {
			$price .= $item['#text'][0];
		}

		if (empty($price)) {
			foreach($this->nokogiri->get('.PricingInfo .camelPrice span') as $item) {
				$price .= $item['#text'][0];
			}
		}

		$price = str_replace(',','',$price);

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

		foreach ($this->meta(true) as $m) {
			if (isset($m['itemprop']) && isset($m['content']) && ($m['itemprop']=='model')){
				$result['model_meta'] =  trim($m['content']);
			}
		}

		if (isset($result['model']) || $result['model_meta']) {
			foreach($this->nokogiri->get('h1.productTitle') as $item) {
				$s = split(' ', $item['#text'][0]);
				foreach($s as $j){
					if (isset($result['model'])) {
						similar_text($j,$result['model'],$percents);
					} else {
						similar_text($j,$result['model_meta'],$percents);
					}
					if($percents>85){
						$result['model_title'] = $j;
					}
				}
			}
		}

		foreach($this->nokogiri->get('.SpecTable tr') as $item) {
			$features[] = trim($item['td'][0]['#text'][0]).trim($item['td'][1]['#text'][0]);
		}
		$result['feature_count'] = count($features);

		foreach($this->nokogiri->get('#BVRRSourceID span') as $item) {
			if (isset($item['itemprop']) && $item['itemprop']=='reviewCount' ) {
				$result['review_count'] = $item['#text'][0];
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
			$price = str_replace(',','',$price);
			if (preg_match('/\$([0-9]+[\.]*[0-9]*)/', $price, $match)) {
				$price = $match[1];
			}
		}

		foreach($this->nokogiri->get('.contentMain .prodInfo .priceFinal .salePrice') as $item) {
			$price = $item['sup'][0]['#text'][0] . $item['#text'][0]. '.' . $item['sup'][1]['#text'][0];
			$price = str_replace(',','',$price);
			if (preg_match('/\$([0-9]+[\.]*[0-9]*)/', $price, $match)) {
				$price = $match[1];
			}
		}

		foreach($this->nokogiri->get('.mainContent .prodInfo .priceBox .pricemapa del') as $item) {
			$priceOld = str_replace(',','',$item['#text'][0]);
			if (preg_match('/\$([0-9]+[\.]*[0-9]*)/', $priceOld, $match)) {
				$priceOld = $match[1];
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
			'PriceOld' => $priceOld,
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

		foreach($this->nokogiri->get('#pricingWrap .youPay .pricing') as $item) {
			if (preg_match('/\$([0-9]+[\.]*[0-9]*)/', $item['#text'][0], $match)) {
				$price = $match[1];
			}
		}

		return array(
			'Product Name' => $title,
			'Description' => $description,
			'Long_Description' => $descriptionLong['#text'][0],
			'Price' => $price
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
			$description[] = $item['#text'][0];
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

		if (empty($price)) {
			foreach($this->nokogiri->get('.skuWrapper #SkuForm .priceTotal .finalPrice') as $item) {
				if (preg_match('/\$([0-9]+[\.]*[0-9]*)/', $item['#text'][0], $match)) {
					$price = $match[1];
				}
			}
		}

		foreach($this->nokogiri->get('#subdesc_content .layoutWidth06 ul li') as $item) {
			$description[] = '<li>'.$item['#text'][0].'</li>';
		}

		foreach($this->nokogiri->get('#tabProductInfo-Content .gridWidth06 p') as $item) {
			if (isset($item['class']) && $item['class']=='skuShortDescription' ) {
				continue;
			}
			$description[] = $item['#text'][0];
		}

		$description = implode(" ",$description);

		foreach($this->nokogiri->get('#specs_content #tableSpecifications tr') as $item) {
			if (isset($item['td']) && isset($item['td'][0]) && isset($item['td'][1])) {
				$features[] = $item['td'][0]['#text'][0].": ".$item['td'][1]['#text'][0];
			}

		}
		$features = implode("\n", $features);

		return array(
			'Product Name' => $title['#text'][0],
			'Long_Description' => $description,
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
			$description_long[] = '<li>'.$item['#text'][0].'</li>';
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
			$description[] = '<li>'.$item['#text'][0].'</li>';
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
				foreach($item['#text'] as $j) {
					$line = trim($j);
					if (!empty($line)) {
						$description[] = $line;
					}
				}
			}
		}

		if (empty($description)) {
			foreach($this->nokogiri->get('#long-description p') as $item) {
				foreach($item['#text'] as $j) {
					$line = trim($j);
					if (!empty($line)) {
						$description[] = $line;
					}
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

		foreach($this->nokogiri->get('.ratings-count #ratings-count-link') as $item) {
			$p = $item['#text'][0];
			if (preg_match('/([0-9]+)/', $p, $match)) {
				$result['review_count'] =  trim($match[1]);
			}
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
			foreach($this->nokogiri->get('.content .productDescriptionWrapper span') as $item) {
				foreach($item['#text'] as $t) {
				$line = trim($t);
					if (!empty($line)) {
						$description[] = $line;
					}
				}
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

		if (empty($description)) {
			foreach($this->nokogiri->get('.content .productDescriptionWrapper') as $item) {
				$line = trim($item['#text'][0]);
				if (!empty($line)) {
					$description[] = $line;
				}
			}
		}

		$description = implode(' ',$description);

		if (empty($descriptionLong)) {
			foreach($this->nokogiri->get('.content .productDescriptionWrapper p') as $item) {
				$line = trim($item['#text'][0]);
				if (!empty($line)) {
					$descriptionLong[] = $line;
				}
			}
		}
		$descriptionLong = implode(' ',$descriptionLong);


		foreach($this->nokogiri->get('#feature-bullets-btf .bucket .content ul li') as $item) {
			$line = trim($item['#text'][0]);
			if (!empty($line)) {
				$features[] = $line;
			}
		}

		$features = implode(' ',$features);

		if (empty($description) && empty($descriptionLong) && !empty($features)) {
			$description = $features;
			unset($features);
		}

		foreach($this->nokogiri->get('#actualPriceRow #actualPriceValue .priceLarge') as $item) {
			$p = str_replace(',','',$item['#text'][0]);
			if (preg_match('/\$([0-9]+[\.]*[0-9]*)/', $p, $match)) {
				$price = $match[1];
			}
		}

		foreach($this->nokogiri->get('#priceBlock #listPriceValue.listprice') as $item) {
			$p = str_replace(',','',$item['#text'][0]);
			if (preg_match('/\$([0-9]+[\.]*[0-9]*)/', $p, $match)) {
				$price_old = $match[1];
			}
		}

		if (!isset($price)) {
			foreach($this->nokogiri->get('#priceBlock #listPriceValue') as $item) {
				$p = str_replace(',','',$item['#text'][0]);
				if (preg_match('/\$([0-9]+[\.]*[0-9]*)/', $p, $match)) {
					$price_old = $match[1];
				}
			}
		}

		$result = array(
			'Product Name' => $title,
			'Description' => $description,
			'Long_Description' => $descriptionLong,
			'Features' => $features,
			'Price' => $price,
			'PriceOld' => $price_old
		);


		foreach ($result as $key => $value) {
			if (empty($result[$key])) {
				unset($result[$key]);
			}
		}

		return $result;
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

		foreach($this->nokogiri->get('.attrG .pdTab table tr') as $item) {
			if (stripos($item['td'][0]['#text'][0], 'brand name') !==false ) {
				$result['manufacturer'] =  trim($item['td'][1]['#text'][0]);
			}
			if (stripos($item['td'][0]['#text'][0], 'item model number') !==false ) {
				$result['model'] =  trim($item['td'][1]['#text'][0]);
			}
		}

		foreach($this->nokogiri->get('.reviews #summaryContainer .acrCount a') as $item) {
			$p = $item['#text'][0];
			if (preg_match('/([0-9]+)/', $p, $match)) {
				$result['review_count'] =  trim($match[1]);
			}
		}

		foreach($this->nokogiri->get('#feature-bullets-btf .bucket .content ul li') as $item) {
			$line = trim($item['#text'][0]);
			if (!empty($line)) {
				$features[] = $line;
			}
		}
		$result['feature_count'] = count($features);

		foreach($this->nokogiri->get('#detail-bullets .bucket .content table tr td a') as $item) {
			if (isset($item['onclick'])) {
				if (preg_match("/.*\('([^']*\.pdf)',.*/", $item['onclick'], $matches)) {
					$result['pdf'][] = array(
						'name' => $item['#text'][0],
						'url' => $matches[1]
					);
				}
			}
		}

		$result['pdf_count'] = count($result['pdf']);

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

		foreach($this->nokogiri->get('#pdp_tabs #pdp_tabs_body_details ul li') as $item) {
			foreach($item['#text'] as $i) {
				$line = trim($i);
				if (!empty($line)) {
					$description[] = '<li>'.$line.'</li>';
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


	public function process_nordstrom(){
		foreach($this->nokogiri->get('.product-content h1') as $item) {
			$title = $item['#text'][0];
		}

		foreach($this->nokogiri->get('#productdetails #pdList .content') as $item) {
			foreach($item['#text'] as $i) {
				$line = trim($i);
				if (!empty($line)) {
					$description[] = $line;
				}
			}
		}

		foreach($this->nokogiri->get('#productdetails #pdList .content .style-features li') as $item) {
			foreach($item['#text'] as $i) {
				$line = trim($i);
				if (!empty($line)) {
					$description[] = $line;
				}
			}
		}

		$description = implode(' ',$description);

		foreach($this->nokogiri->get('li.price span.regular') as $item) {
			$i = str_ireplace('sale: ','',$item['#text'][0]);
			if (preg_match('/\$([0-9]+[\.]*[0-9]*)/', $i, $match)) {
				$price = $match[1];
			}
		}

		return array(
			'Product Name' => $title,
			'Description' => $description,
			'Price' => $price
		);
	}

	public function process_macys(){
		foreach($this->nokogiri->get('#productDescription h1#productTitle') as $item) {
			$title = $item['#text'][0];
		}

		foreach($this->nokogiri->get('#pdpTabs #prdDesc #longDescription') as $item) {
			foreach($item['#text'] as $i) {
				$line = trim($i);
				if (!empty($line)) {
					$description[] = $line;
				}
			}
		}

		foreach($this->nokogiri->get('#pdpTabs #prdDesc #bullets li') as $item) {
			foreach($item['#text'] as $i) {
				$line = trim($i);
				if (!empty($line)) {
					$description[] = $line;
				}
			}
		}

		foreach($this->nokogiri->get('#productDetails #longDescription') as $item) {
			foreach($item['#text'] as $i) {
				$line = trim($i);
				if (!empty($line)) {
					$description[] = $line;
				}
			}
		}

		$description = implode(' ',$description);

		foreach($this->nokogiri->get('#productDescription #priceInfo span.priceSale') as $item) {
			$i = str_ireplace(array('sale: ', 'now '),'',$item['#text'][0]);
			if (preg_match('/\$([0-9]+[\.]*[0-9]*)/', $i, $match)) {
				$price = $match[1];
			}
		}

		if(!isset($price)) {
			foreach($this->nokogiri->get('#productDescription #priceInfo span') as $item) {
				$i = str_ireplace('was ','',$item['#text'][0]);
				if (preg_match('/\$([0-9]+[\.]*[0-9]*)/', $i, $match)) {
					$price = $match[1];
				}
			}
		}


		$result = array(
			'Product Name' => $title,
			'Description' => $description,
			'Price' => $price,
		);

		foreach ($result as $key => $value) {
			if (empty($result[$key])) {
				unset($result[$key]);
			}
		}

		return $result;
	}

	public function attributes_macys() {
		$result = array();

		foreach($this->nokogiri->get('#pdpTabs #prdDesc #longDescription') as $item) {
			foreach($item['#text'] as $i) {
				$line = trim($i);
				if (!empty($line)) {
					$line = stristr($line, 'model');
					$arr = explode('.', $line);
					$line = str_ireplace(array('.', 'model'), '', $arr[0]);
					$line = trim($line);
					if (!empty($line)) {
						$result['model'] = $line;
					}
				}
			}
		}

		foreach($this->nokogiri->get('#productDescription h1#productTitle') as $item) {
			$title = $item['#text'][0];

			$arr = explode(' ',trim($title));
			$result['manufacturer'] = $arr[0];
		}

		return $result;
	}

	public function process_neimanmarcus(){
		foreach($this->nokogiri->get('#productDetails h1') as $item) {
			foreach($item['#text'] as $i) {
				$line = trim($i);
				if (!empty($line)) {
					$title = $line;
				}
			}
		}

		foreach($this->nokogiri->get('#productDetails table .productCutline') as $item) {
			foreach($item['#text'] as $i) {
				$line = trim($i);
				if (!empty($line)) {
					$description[] = $line;
				}
			}
		}

		foreach($this->nokogiri->get('#productDetails table .productCutline ul li') as $item) {
			foreach($item['#text'] as $i) {
				$line = trim($i);
				if (!empty($line)) {
					$description[] = $line;
				}
			}
		}

		foreach($this->nokogiri->get('#productDetails table .suiteTop') as $item) {
			foreach($item['#text'] as $i) {
				$line = trim($i);
				if (!empty($line)) {
					$description[] = $line;
				}
			}
		}

		foreach($this->nokogiri->get('#productDetails table .suiteProducts .suiteProductCutline ul li') as $item) {
			foreach($item['#text'] as $i) {
				$line = trim($i);
				if (!empty($line)) {
					$description[] = $line;
				}
			}
		}

		$description = implode(' ',$description);

		foreach($this->nokogiri->get('.lineItem .lineItemData .lineItemInfo') as $item) {
			if (isset($item['h2'])) {
				foreach($item['h2'] as $i){
					if($i['#text'][0] == $title ) {
						if (isset($item['span'])) {
							if (preg_match('/\$([0-9]+[\.]*[0-9]*)/', $item['span'][0]['#text'][0], $match)) {
								$price = $match[1];
							}
						}
					}
				}
			}
		}

		If (!isset($price)) {
			foreach($this->nokogiri->get('.lineItem .lineItemData .lineItemInfo .adornmentPriceElement .pos1override') as $item) {
				if ($item['class'] == 'price pos1override') {
					if (preg_match('/\$([0-9]+[\.]*[0-9]*)/', $item['#text'][0], $match)) {
						$price += (int)$match[1];
					}
				}
			}
		}

		If (!isset($price)) {
			foreach($this->nokogiri->get('.lineItem .lineItemData .lineItemInfo .adornmentPriceElement .pos2') as $item) {
				if ($item['class'] == 'price pos2') {
					if (preg_match('/\$([0-9]+[\.]*[0-9]*)/', $item['#text'][0], $match)) {
						$price += (int)$match[1];
					}
				}
			}
		}

		$result = array(
			'Product Name' => $title,
			'Description' => $description,
			'Price' => number_format($price,2, '.', ''),
		);

		return $result;
	}

	public function process_williamssonoma(){
		foreach($this->nokogiri->get('.pip-info h1') as $item) {
			$title = $item['#text'][0];
		}

		foreach($this->nokogiri->get('.pip-info .accordion-component') as $item) {
			if (isset($item['dt']) && isset($item['dd'])) {
				foreach ($item['dt'] as $k=>$i) {
					if (strpos($i['#text'][0], 'Summary') !== false && isset($item['dd'][$k]['div'][0]['p'])) {
						foreach ($item['dd'][$k]['div'][0]['p'][0]['#text'] as $d) {
							$description[] = trim($d);
						}
					}
				}
			}
		}

		$description = implode(' ',$description);

		foreach($this->nokogiri->get('.pip-info .accordion-component .accordion-body .accordion-contents ul li') as $item) {
			$descriptionLong[] = '<li>'.trim($item["#text"][0]).'</li>';
		}

		$descriptionLong = implode(' ',$descriptionLong);

		foreach($this->nokogiri->get('.pip-info .product-price .currency') as $item) {
			if(isset($item['span'][0]['class']) && isset($item['span'][1]['class']) && $item['span'][0]['class'] == 'currency-symbol' && $item['span'][1]['class']=='price-amount') {
				$p = str_replace(',','',$item['span'][0]['#text'][0].$item['span'][1]['#text'][0]);
				if (preg_match('/\$([0-9]+[\.]*[0-9]*)/', $p, $match)) {
					$price = $match[1];
				}
			}
		}

		return array(
			'Product Name' => $title,
			'Description' => $description,
			'Long_Description' => $descriptionLong,
			'Price' => number_format($price,2, '.', '')
		);
	}

	public function attributes_williamssonoma() {
		$result = array();

		foreach($this->nokogiri->get('.pip-info .accordion-component .accordion-body .accordion-contents ul li') as $item) {
			$line = trim($item["#text"][0]);

			if (!empty($line) && stristr($line, 'model')!== false) {
				$line = str_ireplace(array('#', 'model number' ,'model', '.'), '', $line);
				$line = trim($line);
				if (!empty($line)) {
					$result['model'] = $line;
				}
			}
		}

		foreach($this->nokogiri->get('.pip-info h1') as $item) {
			$title = $item['#text'][0];

			$arr = explode(' ',trim($title));
			$result['manufacturer'] = $arr[0];
		}

		return $result;
	}

	public function process_pgestore(){
		foreach($this->nokogiri->get('.productinfo h1.productname') as $item) {
			$title = $item['#text'][0];
		}

		foreach($this->nokogiri->get('.productinfo #pdpTab1 .tabContent') as $item) {
			$description[] = trim($item['#text'][0]);
		}

		foreach($this->nokogiri->get('.productinfo #pdpTab1 .tabContent ul li') as $item) {
			$description[] = '<li>'.trim($item['#text'][0]).'</li>';
		}

		$description = implode(' ',$description);

		foreach($this->nokogiri->get('.productinfo #pdpTab2 .tabContent p') as $item) {
			$descriptionLong[] = trim($item['#text'][0]);
		}

		$descriptionLong = implode(' ',$descriptionLong);

		foreach($this->nokogiri->get('.productinfo .pricing .price div') as $item) {
			if (preg_match('/\$([0-9]+[\.]*[0-9]*)/', $item['#text'][0], $match)) {
				$price = $match[1];
			}
		}

		return array(
			'Product Name' => $title,
			'Description' => $description,
			'Long_Description' => $descriptionLong,
			'Price' => number_format($price,2, '.', '')
		);
	}

	public function attributes_pgestore() {
		$result = array();

		foreach($this->nokogiri->get('.productinfo #prodSku') as $item) {
			$line = trim($item["#text"][0]);

			if (!empty($line)) {
				$result['model'] = $line;
			}
		}

		foreach($this->nokogiri->get('.productinfo h1.productname') as $item) {
			$title = $item['#text'][0];

			$arr = explode(' ',trim($title));

			if (in_array($arr[1], array('&', 'and')))
				$result['manufacturer'] = $arr[0].' '.$arr[1].' '.$arr[2] ;
			else
				$result['manufacturer'] = $arr[0];
		}

		return $result;
	}

	public function process_newegg(){
		foreach($this->nokogiri->get('.grpDesc h1 span') as $item) {
			$title = $item['#text'][0];
		}

		foreach($this->nokogiri->get('#Overview_Content .itmDesc #overview-content') as $item) {
			foreach($item['#text'] as $i) {
				$description[] = trim($i);
			}
		}
		$description = trim(implode(' ',$description));

		if (empty($description)) {
			foreach($this->nokogiri->get('#Overview_Content .itmDesc p') as $item) {
				$description[] = trim($item['#text'][0]);
			}
			$description = trim(implode(' ',$description));
		}

		foreach($this->nokogiri->get('#Details_Content #Specs dl') as $item) {
			if (isset($item['dt']) && isset($item['dd'])) {
				$features[] = trim($item['dt'][0]['#text'][0]).': '.trim($item['dd'][0]['#text'][0]);
			}
		}

		$features = implode("\n",$features);

		return array(
			'Product Name' => $title,
			'Description' => $description,
			'Long_Description' => $descriptionLong,
			'Features' => $features,
			'Price' => $price
		);
	}

	public function attributes_newegg() {
		$result = array();

		foreach($this->nokogiri->get('#Details_Content #Specs dl') as $item) {
			if (isset($item['dt']) && isset($item['dd'])) {
				$line = trim($item['dt'][0]["#text"][0]);
				if (!empty($line) && stristr($line, 'brand')!== false) {
					$result['manufacturer'] = trim($item['dd'][0]['#text'][0]);
				} else if (!empty($line) && stristr($line, 'model')!== false) {
					$result['model'] = trim($item['dd'][0]['#text'][0]);
				}
			}
		}

		foreach($this->nokogiri->get('.grpDesc  .itmRating span') as $item) {
			if (isset($item['itemprop']) && ($item['itemprop']=='reviewCount')){
				$p = $item['#text'][0];
				if (preg_match('/([0-9]+)/', $p, $match)) {
					$result['review_count'] =  trim($match[1]);
				}
			}
		}

		return $result;
	}
}

?>