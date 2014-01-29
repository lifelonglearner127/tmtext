<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');

class Statistics_trendline_dates_model extends CI_Model {

    var $tables = array(
        'statistics_trendline_dates' => 'statistics_trendline_dates',
    );

    function __construct()
    {
        parent::__construct();
    }
    
    function updateStats(&$trendline_dates_items, $graph_build, $batch_id, $batch_compare_id) {

        $this->db->where('graph_build', $graph_build)
                ->where('batch_id', $batch_id)
                ->where('batch_compare_id', $batch_compare_id);
        $query= $this->db->get($this->tables['statistics_trendline_dates']);    
        if($query->num_rows()>0){
            $arr = $query->result();
            $trendline_dates_items_cach = json_decode($arr[0]->trendline_dates_items,true);
            $id = $arr[0]->id;
            if(is_array($trendline_dates_items_cach) && is_array($trendline_dates_items))
            {
                $coun_new = $coun_cach = $coun_val_new = $coun_val_cach = 0;
                foreach ($trendline_dates_items as $key => $value) {
                    ++$coun_new;
                    $coun_val_new += $trendline_dates_items[$key];
                }
                foreach ($trendline_dates_items_cach as $key => $value) {
                    ++$coun_cach;
                    $coun_val_cach += $trendline_dates_items_cach[$key];
                }
                
                if( $coun_val_cach > $coun_val_new )
                {
                    $trendline_dates_items = $trendline_dates_items_cach;
                } else {
                    $idata['trendline_dates_items']  = json_encode($trendline_dates_items);
                    $this->db->where('id', $id);
                    $this->db->update($this->tables['statistics_trendline_dates'], $idata);
                }
            }
        } else {
            $idata['graph_build']       = $graph_build;
            $idata['batch_id']          = $batch_id;
            $idata['batch_compare_id']  = $batch_compare_id;
            $idata['trendline_dates_items']  = json_encode($trendline_dates_items);
            $this->db->insert($this->tables['statistics_trendline_dates'], $idata);
        }
    }

}
