<?php
if (!defined('BASEPATH'))
	exit('No direct script access allowed');

class Crawler_List_model extends CI_Model {
	var $url = '';
	var $user_id = 0;
	var $status = 'new';
	// new, reserved, finished
	var $created = '';
	var $category_id = 0;

	var $tables = array('crawler_list' => 'crawler_list', 'categories' => 'categories');

	function __construct() {
		parent::__construct();
	}

	function get($id) {
		$query = $this -> db -> where('id', $id) -> limit(1) -> get($this -> tables['crawler_list']);

		return $query -> result();
	}

	function getIds($ids) {
		$query = $this -> db -> where_in('id', $ids) -> get($this -> tables['crawler_list']);

		return $query -> result();
	}

	function insert($url, $category_id) {
		$CI = &get_instance();

		$this -> url = $url;
		$this -> user_id = $CI -> ion_auth -> get_user_id();
		$this -> category_id = $category_id;
		$this -> created = date('Y-m-d h:i:s');

		$this -> db -> insert($this -> tables['crawler_list'], $this);
		return $this -> db -> insert_id();
	}

	function updateUrl($id, $url) {
		$CI = &get_instance();
		return $this -> db -> update($this -> tables['crawler_list'], array('url' => $url), array('id' => $id, 'user_id' => $CI -> ion_auth -> get_user_id()));
	}

	function updateStatus($id, $status) {
		return $this -> db -> update($this -> tables['crawler_list'], array('status' => $status), array('id' => $id));
	}
	
	function updateStatusEx($ids, $status) {
		$this -> db -> where_in('id', $ids);
		return $this -> db -> update($this -> tables['crawler_list'], array('status' => $status));
	}

	function updated($id) {
		//return $this->db->update($this->tables['crawler_list'], array('updated' => date('Y-m-d h:i:s')), array('id' => $id));

		$this -> db -> set('updated', 'NOW()', FALSE);
		$this -> db -> where('id', $id);
		return $this -> db -> update($this -> tables['crawler_list']);
	}

	function updateImportedDataId($id, $imported_id) {
		return $this -> db -> update($this -> tables['crawler_list'], array('imported_data_id' => $imported_id), array('id' => $id));
	}

	function delete($id) {
		$CI = &get_instance();

		return $this -> db -> delete($this -> tables['crawler_list'], array('id' => $id, 'user_id' => $CI -> ion_auth -> get_user_id()));
	}

	function getByUrl($url) {
		$query = $this -> db -> where('url', $url) -> limit(1) -> get($this -> tables['crawler_list']);
		if ($query -> num_rows() > 0) {
			return $query -> row() -> id;
		}
		return false;
	}

	function getAllNew($limit, $only_my = true) {
		$CI = &get_instance();

		$this -> db -> select('id, url, category_id, imported_data_id') -> where('status', 'new');

		if ($only_my) {
			$this -> db -> where('user_id', $CI -> ion_auth -> get_user_id());
		}

		if (isset($limit) && $limit > 0) {
			$this -> db -> limit($limit);
		}

		$query = $this -> db -> get($this -> tables['crawler_list']);

		return $query -> result();
	}

	function getAllQueued($limit, $only_my = true) {
		$CI = &get_instance();

		$this -> db -> select('id, url, category_id, imported_data_id') -> where('status', 'queued');

		if ($only_my) {
			$this -> db -> where('user_id', $CI -> ion_auth -> get_user_id());
		}

		if (isset($limit) && $limit > 0) {
			$this -> db -> limit($limit);
		}

		$query = $this -> db -> get($this -> tables['crawler_list']);

		return $query -> result();
	}

	function getAll($limit = null, $only_my = true) {
		$CI = &get_instance();

		$this -> db -> select('id, url, category_id, imported_data_id, status') -> where('user_id', $CI -> ion_auth -> get_user_id());

		if ($only_my) {
			$this -> db -> where('user_id', $CI -> ion_auth -> get_user_id());
		}

		if (isset($limit) && $limit > 0) {
			$this -> db -> limit($limit);
		}

		$query = $this -> db -> get($this -> tables['crawler_list']);

		return $query -> result();
	}

	function getAllLimit($limit, $start, $only_my = true, $search_crawl_data = '', $failed = 0) {
		$CI = &get_instance();

		$this -> db -> select('cl.id, cl.imported_data_id, cl.url, cl.snap, cl.snap_date, c.name as name, cl.status, DATE(cl.updated) as updated') -> from($this -> tables['crawler_list'] . ' as cl') -> join($this -> tables['categories'] . ' as c', 'cl.category_id = c.id', 'left');

		if ($only_my) {
			$this -> db -> where('user_id', $CI -> ion_auth -> get_user_id());
		}
		if ($search_crawl_data != '') {
			$this -> db -> like('cl.url', $search_crawl_data) -> or_like('c.name', $search_crawl_data) -> or_like('cl.status', $search_crawl_data) -> or_like('DATE(cl.updated)', $search_crawl_data);
		}

		if ($failed == 1) {
			$this -> db -> where('cl.status', 'failed');
		}

		$query = $this -> db -> order_by("cl.created", "desc") -> limit($limit, $start) -> get();

		return $query -> result();
	}

	function countAll($only_my = true, $search_crawl_data = '', $failed = 0) {
		$CI = &get_instance();

		$this -> db -> select('cl.id') -> from($this -> tables['crawler_list'] . ' as cl') -> join($this -> tables['categories'] . ' as c', 'cl.category_id = c.id', 'left');

		if ($only_my) {
			$this -> db -> where('user_id', $CI -> ion_auth -> get_user_id());
		}
		if ($search_crawl_data != '') {
			$this -> db -> like('cl.url', $search_crawl_data) -> or_like('c.name', $search_crawl_data) -> or_like('cl.status', $search_crawl_data) -> or_like('DATE(cl.updated)', $search_crawl_data);
		}

		if ($failed == 1) {
			$this -> db -> where('cl.status', 'failed');
		}
		return $this -> db -> count_all_results();
	}

	function countAllWithStatus($only_my = true, $search_crawl_data = '', $status) {
		$CI = &get_instance();

		$this -> db -> select('cl.id') -> from($this -> tables['crawler_list'] . ' as cl') -> join($this -> tables['categories'] . ' as c', 'cl.category_id = c.id', 'left');

		if ($only_my) {
			$this -> db -> where('user_id', $CI -> ion_auth -> get_user_id());
		}
		if ($search_crawl_data != '') {
			$this -> db -> like('cl.url', $search_crawl_data) -> or_like('c.name', $search_crawl_data) -> or_like('cl.status', $search_crawl_data) -> or_like('DATE(cl.updated)', $search_crawl_data);
		}

		$this -> db -> where('cl.status', $status);

		return $this -> db -> count_all_results();
	}

	function countNew($only_my = true) {
		$CI = &get_instance();

		$this -> db -> select('cl.id') -> from($this -> tables['crawler_list'] . ' as cl') -> join($this -> tables['categories'] . ' as c', 'cl.category_id = c.id', 'left') -> where('status', 'new');

		if ($only_my) {
			$this -> db -> where('user_id', $CI -> ion_auth -> get_user_id());
		}
		if ($search_crawl_data != '') {
			$this -> db -> like('cl.url', $search_crawl_data) -> or_like('c.name', $search_crawl_data) -> or_like('cl.status', $search_crawl_data) -> or_like('DATE(cl.updated)', $search_crawl_data);
		}

		return $this -> db -> count_all_results();
	}

	function getNew() {
		$this -> db -> select('id, url') -> limit(1) -> where('status', 'new') -> order_by('created', 'asc');
		$query = $this -> db -> get($this -> tables['crawler_list']);

		return $query -> row();
	}

	function selectSnap($imp_d_i) {
		$this -> db -> select('snap,snap_date,snap_state') -> limit(1) -> where('imported_data_id', $imp_d_i);
		$query = $this -> db -> get($this -> tables['crawler_list']);

		return $query -> result();
	}

	function getByBatchUrls($batch_id) {
		$this -> db -> select('cl.id, cl.imported_data_id, cl.url, cl.snap, cl.snap_date, c.name as name, cl.status, DATE(cl.updated) as updated') -> from($this -> tables['crawler_list'] . ' as cl') -> join($this -> tables['categories'] . ' as c', 'cl.category_id = c.id', 'left') -> join('research_data_to_crawler_list as rc', 'cl.id = rc.crawler_list_id') -> join('research_data as rd', 'rd.id = rc.research_data_id') -> where('rd.batch_id', $batch_id);
		$query = $this -> db -> order_by("cl.created", "desc") -> get();
		return $query -> result();
	}

	function getUrlsWithoutBatch() {
		$this -> db -> select('cl.id, cl.imported_data_id, cl.url, cl.snap, cl.snap_date, c.name as name, cl.status, DATE(cl.updated) as updated') -> from($this -> tables['crawler_list'] . ' as cl') -> join($this -> tables['categories'] . ' as c', 'cl.category_id = c.id', 'left') -> join('research_data_to_crawler_list as rc', 'cl.id = rc.crawler_list_id') -> join('research_data as rd', 'rd.id = rc.research_data_id');
		$query = $this -> db -> order_by("cl.created", "desc") -> get();
		return $query -> result();
	}

	function lockedToQue($ids) {
		return $this -> db -> update($this -> tables['crawler_list'], array('status' => 'queued'), array('id' => $ids));
	}

	function getByBatchLimit($limit, $start, $batch_id, $failed = 0) {
		$this -> db -> select('cl.id, cl.imported_data_id, cl.url, cl.snap, cl.snap_date, c.name as name, cl.status, DATE(cl.updated) as updated') -> from($this -> tables['crawler_list'] . ' as cl') -> join($this -> tables['categories'] . ' as c', 'cl.category_id = c.id', 'left') -> join('research_data_to_crawler_list as rc', 'cl.id = rc.crawler_list_id') -> join('research_data as rd', 'rd.id = rc.research_data_id') -> where('rd.batch_id', $batch_id);

		if ($failed == 1) {
			$this -> db -> where('cl.status', 'failed');
		}

		$query = $this -> db -> order_by("cl.created", "desc") -> limit($limit, $start) -> get();

		return $query -> result();
	}

	function getByBatchOverall($batch_id, $failed = 0) {
		$this -> db -> select('cl.id, cl.imported_data_id, cl.url, cl.snap, cl.snap_date, c.name as name, cl.status, DATE(cl.updated) as updated') -> from($this -> tables['crawler_list'] . ' as cl') -> join($this -> tables['categories'] . ' as c', 'cl.category_id = c.id', 'left') -> join('research_data_to_crawler_list as rc', 'cl.id = rc.crawler_list_id') -> join('research_data as rd', 'rd.id = rc.research_data_id') -> where('rd.batch_id', $batch_id);

		if ($failed == 1) {
			$this -> db -> where('cl.snap IS NULL');
		}
		$query = $this -> db -> get();

		return $query -> result();
	}

	function countByBatchWithStatus($batch_id, $status) {
		$this -> db -> select('cl.id') -> from($this -> tables['crawler_list'] . ' as cl') -> join($this -> tables['categories'] . ' as c', 'cl.category_id = c.id', 'left') -> join('research_data_to_crawler_list as rc', 'cl.id = rc.crawler_list_id') -> join('research_data as rd', 'rd.id = rc.research_data_id') -> where('rd.batch_id', $batch_id);

		$this -> db -> where('cl.status', $status);

		return $this -> db -> count_all_results();
	}

	function countByBatch($batch_id, $failed = 0) {

		$this -> db -> select('cl.id') -> from($this -> tables['crawler_list'] . ' as cl') -> join($this -> tables['categories'] . ' as c', 'cl.category_id = c.id', 'left') -> join('research_data_to_crawler_list as rc', 'cl.id = rc.crawler_list_id') -> join('research_data as rd', 'rd.id = rc.research_data_id') -> where('rd.batch_id', $batch_id);

		if ($failed == 1) {
			$this -> db -> where('cl.status', 'failed');
		}

		return $this -> db -> count_all_results();
	}

	function getByBatchId($batch_id) {
		$this -> db -> select('cl.*') -> from($this -> tables['crawler_list'] . ' as cl') -> join('research_data_to_crawler_list as rc', 'cl.id = rc.crawler_list_id') -> join('research_data as rd', 'rd.id = rc.research_data_id') -> where('rd.batch_id', $batch_id);

		$query = $this -> db -> get();

		return $query -> result();
	}

	function getOldByBatchId($batch_id) {
		$this -> db -> select('cl.*') -> from($this -> tables['crawler_list'] . ' as cl') -> join('research_data_to_crawler_list as rc', 'cl.id = rc.crawler_list_id') -> join('research_data as rd', 'rd.id = rc.research_data_id') -> where('rd.batch_id', $batch_id) -> where("cl.updated <= DATE_SUB(NOW(),INTERVAL 3 HOUR)", NULL, FALSE);

		$query = $this -> db -> get();

		return $query -> result();
	}

	function getNewByBatchId($batch_id) {$array = array('rd.batch_id' => $batch_id, 'cl.status' => 'new');
		$this -> db -> select('cl.*') -> from($this -> tables['crawler_list'] . ' as cl') -> join('research_data_to_crawler_list as rc', 'cl.id = rc.crawler_list_id') -> join('research_data as rd', 'rd.id = rc.research_data_id') -> where($array);
		$query = $this -> db -> get();

		return $query -> result();
	}

	function queue_locked() {
		return $this -> db -> update($this -> tables['crawler_list'], array('status' => 'queued'), array('status' => 'lock'));
	}

}
