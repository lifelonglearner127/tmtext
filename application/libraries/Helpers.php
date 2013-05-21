<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');


class Helpers {

  public function __construct() {

  }

  public function measure_analyzer_start($clean_t) {
    // --- analyzer config (start)
    $min_phrase_size = 2;
    $max_phrase_size = 7;
    // --- analyzer config (end)

    // --- ANALYZER ALGO CODE (START)
    $text = trim($clean_t);
    $orig = $text; // ---- initial original text
    $text = strtolower($text);
    // ---- convert to array (start)
    $words = explode(" ", $text);
    $orig = explode(" ", $orig);
    // ---- convert to array (end)

    $repeats = array();
    for($s = $max_phrase_size; $s >= $min_phrase_size; $s=$s-1) {
        // --- loop through every phrase of that size
        for($p = 0; $p < (count($words) - $s); $p++) {
            // --- check to make sure the phrase doesn't end or begin with a punctuation mark
            if(preg_match("/[a-z'A-Z<>\/]+/", $words[$p]) && preg_match("/[a-zA-Z<>\/]+/", $words[$p+$s-1])) {
                // --- represent phrase as a single string
                $p_str = "";
                $s_temp = $s;
                $period = false;
                for($w = 0; $w < $s_temp; $w++) {
                    $phrase[] = $words[$p+$w];
                    $p_str .= $words[$p+$w]." ";
                    if(preg_match("/[^A-Za-z]/", $words[$p+$w])) {
                        $s_temp++;
                        if(preg_match("/[.]/", $words[$p+$w])) {
                            $period = true;
                        }
                    }
                }
                if(!isset($repeats[$p_str])) {
                    $repeats[$p_str] = array();
                    $repeats[$p_str][0] = $s_temp; // --- save the size of the phrase in the first index
                    $repeats[$p_str][1] = $p; // --- add first occurrence of phrase
                } else if(!$period) {   
                    $repeats[$p_str][] = $p;
                }
            }
        }
    }

    $final_repeats = array();
    foreach($repeats as $phrase => $pos) {
        if($repeats[$phrase][0] > 1 && count($pos) > 2) { // --- collect phrase which appears more then one time 
            // --- find phrase in original text (start)
            $len = $pos[0];
            for($i = 1; $i < count($pos); $i++) {
                $orig[$pos[$i]] = "".$orig[$pos[$i]];
                $orig[$pos[$i]+$len-1] = $orig[$pos[$i]+$len-1]."";
                $final_ph = $orig[$pos[$i]]." ".$orig[$pos[$i]+$len-1];
            }
            // --- find phrase in original text (end)
            $mid = array(
              "ph" => trim($final_ph),
              "count" => $pos[0],
              "ph_length" => strlen(trim($final_ph))
            );
            $final_repeats[] = $mid; 
        }
    }

    // --- sort final result (start)
    $ph_length = array();
    foreach ($final_repeats as $key => $row) {
        $ph_length[$key] = $row['ph_length'];
    }
    array_multisort($ph_length, SORT_DESC, $final_repeats);
    // --- sort final result (end)

    return $final_repeats;

  }

}
