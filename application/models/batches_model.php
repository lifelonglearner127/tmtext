<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Batches_model extends CI_Model {

    var $title = '';
    var $user_id = 0;
    var $customer_id = 0;
    var $created = '';
    var $modified = '';

    var $tables = array(
        'batches' => 'batches',
        'customers' => 'customers',
        'research_data' => 'research_data',
        'secondary_batches' => 'secondary_batches'
    );

    function __construct()
    {
        parent::__construct();
    }

    function getFullBatchReviewByBatchId($bid) {
        $this->db->order_by("created", "asc");
        $query = $this->db->where('batch_id', $bid)->get($this->tables['research_data']);
        return $query->result();
    }

    function get($id)
    {
        $query = $this->db->where('id', $id)
            ->get($this->tables['batches']);

        return $query->row();
    }

    function getAll($order = "title")
    {
        $this->db->order_by($order, "asc");
        $query = $this->db->get($this->tables['batches']);

        return $query->result();
    }

    function getCustomerById($batch_id)
    {
        $query = $this->db->select('c.name, c.url')
            ->from($this->tables['batches'].' as b')
            ->join($this->tables['customers'].' as c', 'b.customer_id = c.id', 'left')
            ->where('b.id', $batch_id)
            ->get();

        return $query->row();
    }
    /*function getAll()
    {
        $query =  $this->db->select('b.created as created,b.title as title ,c.name as name , b.id as id, count(r.batch_id) as items')
            ->from($this->tables['batches'].' as b')
            ->join($this->tables['research_data'].' as r', 'r.batch_id = b.id', 'left')
            ->join($this->tables['customers'].' as c', 'c.id = b.customer_id', 'left')
            ->group_by("r.batch_id")    
            ->order_by("b.title", "asc")->get();
        
        return $query->result();
    }*/

    function getAllByCustomer($customer_id='')
    {
        $this->db->order_by("title", "asc");
        $query = $this->db->where('customer_id', $customer_id)->get($this->tables['batches']);

        return $query->result();
    }

    function insert($title, $customer_id=0)
    {
        $CI =& get_instance();
        $this->title = $title;
        $this->user_id = $CI->ion_auth->get_user_id();
        $this->customer_id = $customer_id;
        $this->created = date('Y-m-d h:i:s');
        $this->modified = date('Y-m-d h:i:s');

        $this->db->insert($this->tables['batches'], $this);
        return $this->db->insert_id();
    }

    function getIdByName($title)
    {
        $query = $this->db->where('title', $title)
            ->limit(1)
            ->get($this->tables['batches']);

        if($query->num_rows() > 0) {
            return $query->row()->id;
        }
        return false;
    }

    function update($id, $title)
    {
        $CI =& get_instance();
        $data = array();
        $data['user_id'] = $CI->ion_auth->get_user_id();
        $data['title'] = $title;
        $data['modified'] = date('Y-m-d h:i:s');
        
        return $this->db->update($this->tables['batches'],
            $data,
            array('id' => $id));
    }

    function delete($id)
    {
        return $this->db->delete($this->tables['batches'], array('id' => $id));
    }

    function getCustomerByBatch($batch)
    {
        $query =  $this->db->select('c.name')
            ->from($this->tables['batches'].' as b')
            ->join($this->tables['customers'].' as c', 'c.id = b.customer_id', 'left')
            ->where('b.title', trim($batch))->limit(1)->get();
        if($query->num_rows() > 0) {
            return $query->row()->name;
        }
        return false;
    }
    
    
     function getCustomerUrlByBatch($batch_id)
    {
        $query =  $this->db->select('c.url')
            ->from($this->tables['batches'].' as b')
            ->join($this->tables['customers'].' as c', 'c.id = b.customer_id', 'left')
            ->where('b.id', $batch_id)->limit(1)->get();
        if($query->num_rows() > 0) {
            $url=$query->row()->url;
            $n = parse_url($url);
            $url = $n['host'];
            $url = str_replace("www1.", "", $url);
            $url = str_replace("www.", "", $url);
            return $url;
        }
        return false;
    }
    
    function getAllCustomerDataByBatch($batch) {
        $query =  $this->db->select('*')
            ->from($this->tables['batches'].' as b')
            ->join($this->tables['customers'].' as c', 'c.id = b.customer_id', 'left')
            ->where('b.title', trim($batch))->limit(1)->get();
        if($query->num_rows() > 0) {
            return $query->row();
        }
        return false;
    }

    function getByName($name) {
        $query = $this->db->where('title', $name)
            ->limit(1)
            ->get($this->tables['batches']);
        if($query->num_rows() > 0) {
            return $query->row();
        }
        return false;
    }

     function getCustomerByBatchId($batch_id)//max
    {
        $query =  $this->db->select('c.name')
            ->from($this->tables['batches'].' as b')
            ->join($this->tables['customers'].' as c', 'c.id = b.customer_id', 'left')
            ->where('b.id',$batch_id )->limit(1)->get();
        if($query->num_rows() > 0) {
            return $query->row()->name;
        }
        return false;
    }//max

    public function getBatchReview()
    {
        $query =  $this->db->select('b.created as created,b.title as title ,c.name as name , b.id as id, count(r.batch_id) as items')
                ->from($this->tables['batches'].' as b')
                ->join($this->tables['research_data'].' as r', 'r.batch_id = b.id', 'left')
                ->join($this->tables['customers'].' as c', 'c.id = b.customer_id', 'left')
                ->group_by("r.batch_id")
                ->order_by("b.title", "asc")->get();

        return $query->result();
    }
    
    public function updateById($id,$title){
        $result = $this->db->query("
            UPDATE 
                `batches`
            SET 
                `title`='{$title}'
            WHERE 
                `id`='{$id}'
                ");
        return $result;
    }
    
    function getBatchesForComparingByBatchId($batch_id = 0, $withSecond = TRUE)
    {
	$result = array();    
        $this->db->select('b.id,b.title,b.customer_id,c.name');
	$this->db->from($this->tables['batches']. ' b');
	$this->db->join($this->tables['customers'].' c','c.id = b.customer_id');
	if($withSecond)
	{	
		$this->db->select('s.secondary_batch_id');
		$this->db->join($this->tables['secondary_batches'].' s','s.secondary_customer_id = b.customer_id AND s.primary_batch_id = '.$batch_id,'LEFT');
	}
	$this->db->where('b.customer_id != (SELECT customer_id FROM '.$this->tables['batches'].' WHERE id = '.$batch_id.' )',NULL,FALSE );
	$query = $this->db->get();
        if($query->num_rows() > 0) 
	{
             $results = $query->result_array();
	     if($withSecond)
	     {	     
		foreach($results as $row)
		{
		    $result[$row['customer_id']]['name'] = $row['name'];     
		    $result[$row['customer_id']]['secondary_id'] = $row['secondary_batch_id'];     
		    $result[$row['customer_id']]['batches'][$row['id']] = $row['title'];     
		}
	     } else
	     {
		   foreach($results as $row)
		   {
			 $result[$row['id']] = $row['title'];     
		   }  
	     }
        }
        return $result;
    }
    
    function addSecondaryBatch($data = array())
    { 
	    if(isset($data['primary_batch_id']) && isset($data['secondary_batch_id']) && isset($data['secondary_customer_id']))
	    {
		  $this->db->where('primary_batch_id',$data['primary_batch_id']);  
		  $this->db->where('secondary_customer_id',$data['secondary_customer_id']);  
		  $query = $this->db->get($this->tables['secondary_batches']);
		  if($query->num_rows > 0)
		  {
			  $this->db->where('primary_batch_id',$data['primary_batch_id']);  
			  $this->db->where('secondary_customer_id',$data['secondary_customer_id']);
			  $this->db->update($this->tables['secondary_batches'],array('secondary_batch_id'=>$data['secondary_batch_id']));
		  } else
		  { 
			  $this->db->insert($this->tables['secondary_batches'],$data);
		  }
	    }	    
    }
    
    function getSecondaryBatch($where = array())
    {
	    $result = FALSE;
	    $this->db->select('secondary_batch_id');
	    $this->db->where($where);
	    $query = $this->db->get($this->tables['secondary_batches']);
	    if($query->num_rows > 0)
	    {
		    $result = $query->row();
		    $result = $result->secondary_batch_id;
	    }
	    return $result;
    }
}