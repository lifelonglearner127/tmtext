<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Sites_model extends CI_Model {

    var $tables = array(
        'sites' => 'sites'
    );

    function __construct()
    {
        parent::__construct();
    }

    function get($id)
    {
        $query = $this->db->where('id', $id)
            ->limit(1)
            ->get($this->tables['sites']);

        return $query->result();
    }

    function getAll()
    {
        $query = $this->db->order_by('name', 'asc')->get($this->tables['sites']);

        return $query->result();
    }

    function getIdByName($name)
    {
        $query = $this->db->where('name', $name)
            ->limit(1)
            ->get($this->tables['sites']);

        if($query->num_rows() > 0) {
            return $query->row()->id;
        }
        return '';
    }
    function get_name_by_url($url){
        
        $query1 = $this->db->get($this->tables['sites']);
        $all=$query1->result_array();
        $name='';
        foreach($all as $val){
                        
            $n = parse_url($val['url']);
                
            if( $n['host']==$url){
                $name=$val['name'];
              
            }
        }
       
        return $name;
    }
    function insertSiteByName($name)
    {
        $this->name = $name;
        $this->db->insert($this->tables['sites'], $this);
        return $this->db->insert_id();
    }

    function delete($id)
    {
        return $this->db->delete($this->tables['sites'], array('id' => $id));
    }

    function updateSite($id, $logo)
    {
        $data = array(
            'image_url' => $logo,
        );
        $this->db->update( 'sites', $data, array( 'id' => $id ) );
    }

    function update($id, $name, $url, $image_url)
    {
        $this->url = $url;
        $this->name = $name;
        $this->image_url = $image_url;

        return $this->db->update($this->tables['sites'],
            $this,
            array('id' => $id));
    }
}
