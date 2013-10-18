<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Category_model extends CI_Model {

    var $name = '';

    var $tables = array(
        'categories' => 'categories',
        'imported_data' => 'imported_data',
        'imported_data_parsed' => 'imported_data_parsed',
    );

    function __construct()
    {
        parent::__construct();
    }

    function getAll()
    {
        $this->db->order_by("name", "asc");
        $query = $this->db->get($this->tables['categories']);

        return $query->result();
    }

    function get($id)
    {
        $query = $this->db->where('id', $id)
            ->limit(1)
            ->get($this->tables['categories']);

        return $query->result();
    }

    function getIdByName($name)
    {
        $query = $this->db->where('name', $name)
            ->limit(1)
            ->get($this->tables['categories']);

    	if($query->num_rows() > 0) {
			return $query->row()->id;
		}
        return false;
    }

    function insert($name)
    {
        $this->name = $name;

        $this->db->insert($this->tables['categories'], $this);
        return $this->db->insert_id();
    }

    function delete($id)
    {
        return $this->db->delete($this->tables['categories'], array('id' => $id));
    }

    function getAllCategoryDescriptions($category_id = '', $limit = false, $random = false)
    {
    	$this->db->select('p.value as description, cat.id as category_id')
    		->from($this->tables['categories'].' as cat')
    		->join($this->tables['imported_data'].' as i', 'cat.id = i.category_id', 'left')
    		->join($this->tables['imported_data_parsed'].' as p', 'p.imported_data_id = i.id', 'left')
    		->where('p.key', 'Description');

    	if ($category_id > 0) {
    		$this->db->where('i.category_id', $category_id);
    	}

    	if ($limit) {
    		$this->db->limit((int)$limit);
    	}

        if ($random) {
    		$this->db->order_by('description', 'random');
    	}


    	$query = $this->db->get();

    	return $query->result();
    }

    function countAllCategoryDescriptions($category_id = '')
    {
        $this->db->select('p.value as description, cat.id as category_id')
    		->from($this->tables['categories'].' as cat')
    		->join($this->tables['imported_data'].' as i', 'cat.id = i.category_id', 'left')
    		->join($this->tables['imported_data_parsed'].' as p', 'p.imported_data_id = i.id', 'left')
    		->where('p.key', 'Description');

    	if ($category_id > 0) {
    		$this->db->where('i.category_id', $category_id);
    	}

    	return $this->db->count_all_results();
    }

/*    function getAllCategoryDescriptions($category_id = '', $limit = false)
    {
        $sql = "SELECT p.value as description, cat.id as category_id FROM `{$this->tables['categories']}` cat
                LEFT JOIN `{$this->tables['imported_data']}` i ON cat.id = i.category_id
                LEFT JOIN `{$this->tables['imported_data_parsed']}` p ON p.imported_data_id = i.id";

        if($category_id > 0) {
        	if ($limit !== false) {
        		$sql .= " WHERE i.category_id =? AND p.key = 'Description' LIMIT ?";
            	$query = $this->db->query($sql, array($category_id, (int)$limit));
        	} else {
            	$sql .= " WHERE i.category_id =? AND p.key = 'Description'";
            	$query = $this->db->query($sql, $category_id);
        	}
        } else {
        	if ($limit !== false) {
        		$sql .= " WHERE p.key = 'Description' LIMIT ?";
            	$query = $this->db->query($sql, $limit);
        	} else {
            	$sql .= " WHERE p.key = 'Description'";
            	$query = $this->db->query($sql);
        	}
        }

        return $query->result();
    }

    function countAllCategoryDescriptions($category_id = '')
    {
        $sql = "SELECT count(p.value) as quantity FROM `{$this->tables['categories']}` cat
                LEFT JOIN `{$this->tables['imported_data']}` i ON cat.id = i.category_id
                LEFT JOIN `{$this->tables['imported_data_parsed']}` p ON p.imported_data_id = i.id";

        if($category_id > 0) {
            	$sql .= " WHERE i.category_id =? AND p.key = 'Description'";
            	$query = $this->db->query($sql, $category_id);
        } else {
            	$sql .= " WHERE p.key = 'Description'";
            	$query = $this->db->query($sql);
        }
        return $query->row()->quantity;
    } */
}