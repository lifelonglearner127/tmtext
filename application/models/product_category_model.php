<?php

if (!defined('BASEPATH'))
	exit('No direct script access allowed');

class Product_category_model extends CI_Model
{

	var $table = 'product_categories';
	var $tableResearch = 'research_data';

	function __construct()
	{
		parent::__construct();
	}

	function get($filter = FALSE, $order = FALSE)
	{
		$result = array();
		if (is_array($filter) && count($filter) > 0)
		{
			$this->db->where($filter);
		}
		if (is_array($order) && count($order) > 0)
		{
			$this->db->order_by($order);
		}
		$query = $this->db->get($this->table);
		if ($query->num_rows > 0)
		{
			$result = $query->result_array();
		}
		$query->free_result();
		return $result;
	}

	function update($data = array())
	{
		$result = 0;
		if (isset($data['category_name']) && isset($data['category_code']))
		{
			$this->db->select('id,category_name');
			$this->db->where('category_code',$data['category_code']);
			$this->db->where('category_name',$data['category_name']);
			$query = $this->db->get($this->table);
			if($query->num_rows > 0)
			{
				$row = $query->row_array();
				if($row['category_name'] != $row['category_name'])
				{
					$this->db->where('id',$row['id']);
					$this->db->update($this->table,$data);
				}	
				$result = $row['id'];
			} else
			{
				$this->db->insert($this->table,$data);
				$result = $this->db->insert_id();
			}
			$query->free_result();
			
		}
		return $result;
	}

	function delete($id)
	{
		return $this->db->delete($this->table, array('id' => $id));
	}

	function updateCategoryInfoByURL($data = array())
	{
		$oURL = trim($data[1]);
		$cID = FALSE;
		$cName = FALSE;
		if (isset($data[2]) && isset($data[3]))
		{
			$cID = trim($data[2]);
			$cName = trim($data[3]);
		}
		$updated = 0;
		if ($oURL && $cID && $cName)
		{
			$this->db->select('id,category_id');
			$this->db->where('url', $oURL);
			$query = $this->db->get($this->tableResearch);
			if ($query->num_rows > 0)
			{
				$updated = 1;
				$catID = $this->update(array('category_name' => $cName, 'category_code' => $cID));
				$result = $query->row_array();
				if ($catID != $result['category_id'])
				{
					$this->db->where('id', $result['id']);
					$upd['category_id'] = $catID;
					$this->db->update($this->tableResearch, $upd);
					$updated = 2;
				}
			}
			$query->free_result();
		}
		return $updated;
	}

	function getCatsByBatchId($batchId = 0, $order = array('category_name'=>'asc'))
	{
		$result = array();
		$this->db->select('c.*');
		$this->db->from($this->table.' c');
		$this->db->join($this->tableResearch.' r','r.category_id = c.id AND batch_id ='.$batchId);
		$this->db->order_by($order);
		$query = $this->db->get();
		if($query->num_rows > 0)
		{
			$result = $query->result_array();
		}
		$query->free_result();
		return $result();
	}

}