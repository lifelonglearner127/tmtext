<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Brand_data_model extends CI_Model {

    var $brand_id = '';
    var $date = '';
    var $tweet_count = 0;
    var $twitter_followers = 0;
    var $youtube_video_count = 0;
    var $youtube_view_count = 0;

    var $tables = array(
        'brand_data' => 'brand_data',
    );

    function __construct()
    {
        parent::__construct();
    }

    function getAll()
    {
        $this->db->order_by("name", "asc");
        $query = $this->db->get($this->tables['brand_data']);

        return $query->result();
    }

    function get($id)
    {
        $query = $this->db->where('id', $id)
            ->limit(1)
            ->get($this->tables['brand_data']);

        return $query->result();
    }
    
    function insert($brand_id, $date='', $tweet_count=0, $twitter_followers=0, $youtube_video_count=0, $youtube_view_count=0)
    {
        $this->brand_id = $brand_id;
        $this->date = $date;
        $this->tweet_count = $tweet_count;
        $this->twitter_followers = $twitter_followers;
        $this->youtube_video_count = $youtube_video_count;
        $this->youtube_view_count = $youtube_view_count;

        $this->db->insert($this->tables['brand_data'], $this);
        return $this->db->insert_id();
    }

    function update($id, $brand_id, $date='', $tweet_count=0, $twitter_followers=0, $youtube_video_count=0, $youtube_view_count=0)
    {
        $this->brand_id = $brand_id;
        $this->date = $date;
        $this->tweet_count = $tweet_count;
        $this->twitter_followers = $twitter_followers;
        $this->youtube_video_count = $youtube_video_count;
        $this->youtube_view_count = $youtube_view_count;

    	return $this->db->update($this->tables['brand_data'],
                $this,
                array('id' => $id));
    }

    function delete($id)
    {
        return $this->db->delete($this->tables['brand_data'], array('id' => $id));
    }

}