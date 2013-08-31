<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Brand_data_summary_model extends CI_Model {

    var $brand_id = '';
    var $total_tweets = '';
    var $total_youtube_videos = '';
    var $total_youtube_views = '';

    var $tables = array(
        'brand_data_summary' => 'brand_data_summary',
    );

    function __construct()
    {
        parent::__construct();
    }

    function getAll()
    {
        $this->db->order_by("name", "asc");
        $query = $this->db->get($this->tables['brand_data_summary']);

        return $query->result();
    }

    function get($id)
    {
        $query = $this->db->where('id', $id)
            ->limit(1)
            ->get($this->tables['brand_data_summary']);

        return $query->result();
    }
    
    function getByBrandId($brand_id)
    {
        $query = $this->db->where('brand_id', $brand_id)
            ->limit(1)
            ->get($this->tables['brand_data_summary']);
        
        return $query->row();
    }
    
    function insert($brand_id, $total_tweets=0, $total_youtube_videos=0, $total_youtube_views=0)
    {
        $this->brand_id = $brand_id;
        $this->total_tweets = $total_tweets;
        $this->total_youtube_videos = $total_youtube_videos;
        $this->total_youtube_views = $total_youtube_views;

        $this->db->insert($this->tables['brand_data_summary'], $this);
        return $this->db->insert_id();
    }

    function update($id, $brand_id, $total_tweets=0, $total_youtube_videos=0, $total_youtube_views=0)
    {
        $this->brand_id = $brand_id;
        $this->total_tweets = $total_tweets;
        $this->total_youtube_videos = $total_youtube_videos;
        $this->total_youtube_views = $total_youtube_views;

    	return $this->db->update($this->tables['brand_data_summary'],
                $this,
                array('id' => $id));
    }
    
    function updateByBrandId($brand_id, $tweet_count=0, $youtube_video_count=0, $youtube_view_count=0)
    {
        $data =$this->getByBrandId($brand_id);
        if(!empty($data)) {
            $this->update(
                    $data->id,
                    $brand_id,
                    ($data->total_tweets + $tweet_count),
                    ($data->total_youtube_videos + $youtube_video_count),
                    ($data->total_youtube_views + $youtube_view_count)
                );
        } else {
            $this->insert($brand_id, $tweet_count, $youtube_video_count, $youtube_view_count);
        }
    }

    function delete($id)
    {
        return $this->db->delete($this->tables['brand_data_summary'], array('id' => $id));
    }

}