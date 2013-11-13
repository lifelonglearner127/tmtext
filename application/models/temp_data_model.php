<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Temp_data_model extends CI_Model {


    function __construct()
    {
        parent::__construct();
    }
    public function createMatchUrlsTable(){
        $sql = "CREATE TABLE IF NOT EXISTS `urlstomatch` (
            id INT NOT NULL AUTO_INCREMENT,
            url1 VARCHAR(5000),
            url2 VARCHAR(5000),
            PRIMARY KEY (id)
            )";
        $this->db->query($sql);
    }
    public function dropTable($table){
        $sql = "DROP TABLE IF EXISTS `$table`";
        $this->db->query($sql);
    }

    public function addUrlToMatch($url1,$url2){
        $data = array(
            'url1'=>$url1,
            'url2'=>$url2
        );
        $this->db->insert('urlstomatch',$data);
    }
    public function getLineFromTable($table){
        $this->db->select('url1, url2, id');
        $this->db->from($table);
        $this->db->limit(1);
        $query = $this->db->get();
        if($query->num_rows===0)return FALSE;
        $row = $query->first_row('array');
        $this->db->where('id',$row['id']);
        $this->db->delete($table);
        return $row;
    }
    public function createNonFoundTable(){
        $sql = "CREATE TABLE IF NOT EXISTS `notfoundurls`(
            id INT NOT NULL AUTO_INCREMENT
            ,url VARCHAR(5000)
            ,proc VARCHAR(20)
            ,PRIMARY KEY (id)
            )";
        $this->db->query($sql);
    }
    public function addUrlToNonFound($url,$pr){
        $data = array(
            'url'=>$url,
            'proc'=>$pr
        );
        $this->db->insert('notfoundurls',$data);
    }
    public function emptyTable($table){
        $sql= "SHOW TABLES LIKE '$table'";
        $query = $this->db->query($sql);
        if($query->num_rows==0)return 0;
        $sql = "TRUNCATE `$table`";
        $this->db->query($sql);
    }
    public function getNotFount(){
        $this->db->select('*');
        $this->db->from('notfoundurls');
        $query = $this->db->get();
        if($query->num_rows==0)return false;
        return $query;
    }
    public function createJLdata(){
        $sql = "CREATE TABLE IF NOT EXISTS `jldatatoimport`(
            id INT NOT NULL AUTO_INCREMENT
            ,jlline VARCHAR(2000)
            ,PRIMARY KEY (id)
            )";
        $this->db->query($sql);
    }
    public function download_send_headers($file){
        header('Content-disposition: attachment; filename='.$file);
        header('Content-type: text/plain');
    }
    public function array2file($array){
        if(empty($array)){return false;}
        ob_start();
        $df = fopen("php://output", 'w');
        foreach($array as $row){
            file_put_contents($df, $row);
        }
        fclose($df);
        return ob_get_clean();
    }
    //public 

}