<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Matchurls_data_model extends CI_Model {

    var $tables = array(
        'matchurls_csvfile' => 'matchurls_csvfile',
        'matchurls' => 'matchurls'
    );
    
    function __construct()
    {
        parent::__construct();
    }

    public function getIdCSVFile($file_name) {
        $query = $this->db->get_where($this->tables['matchurls_csvfile'], array('file_name' => $file_name),1);
        if (($result = $query->result()) && isset($result[0]->file_id))
        {
            return $result[0]->file_id;
        }
        return false;
    }
    
    function getAll()
    {
        $this->db->order_by("file_name", "asc");
        $query = $this->db->get($this->tables['matchurls_csvfile']);

        return $query->result();
    }
    
    public function getUrlsCSVFile($fileCSV_id) {
        $query = $this->db->get_where($this->tables['matchurls'], array('file_id' => $fileCSV_id));
//        $query = $this->db->select(' url1, url2 ');
        return $query->result();
    }
    
    public function createCSVFileTables(){
        $this->createCSVFileTable();
        $this->createMatchUrlsTable();
    }
    
    public function createCSVFileTable(){
        $sql = "CREATE TABLE IF NOT EXISTS `{$this->tables['matchurls_csvfile']}`(
            file_id INT NOT NULL AUTO_INCREMENT
            ,file_name VARCHAR(255)
            ,description VARCHAR(40)
            ,PRIMARY KEY (file_id)
            )";
        $this->db->query($sql);
    }
    
    public function addCSVFile($file_name,$description = ''){
        $data = array(
            'file_name'=>$file_name,
            'description'=>$description
        );
        if( $this->db->insert($this->tables['matchurls_csvfile'],$data))
        {
            return $this->db->insert_id();
        }
        return false;
    }

    public function createMatchUrlsTable() {
        $sql = "CREATE TABLE IF NOT EXISTS `{$this->tables['matchurls']}` (
            id INT NOT NULL AUTO_INCREMENT,
            file_id INT NOT NULL DEFAULT '0',
            url1 VARCHAR(5000),
            url2 VARCHAR(5000),
            PRIMARY KEY (id),
            KEY (file_id)
            )";
        $this->db->query($sql);
    }

    
    public function addUrlToMatch($fileCSV_id,$url1,$url2){
        $data = array(
            'file_id' => $fileCSV_id,
            'url1'=>$url1,
            'url2'=>$url2
        );
        $this->db->insert($this->tables['matchurls'], $data);
    }
    /**
    * delete CSV file info
    *
    * @return bool
    * @author aditya menon
    **/
    public function deleteCSV($file_id = FALSE)
    {
            // bail if mandatory param not set
            if(!$file_id || empty($file_id))
            {
                    return FALSE;
            }

//            $this->db->trans_begin();

            // remove all urls from this file
            $this->db->delete($this->tables['matchurls'], array('file_id' => $file_id));
            // remove the file
            $this->db->delete($this->tables['matchurls_csvfile'], array('file_id' => $file_id));

//            if ($this->db->trans_status() === FALSE)
//            {
//                    $this->db->trans_rollback();
////                    $this->set_error('file_delete_unsuccessful');
//                    return FALSE;
//            }
//
//            $this->db->trans_commit();
            
            return TRUE;
    }
    
}