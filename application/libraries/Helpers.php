<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');


class Helpers {

  public function __construct() {

  }

  public function measure_analyzer_start_v2($clean_t) { // !!! EXPREIMENTAL !!!
    // $clean_t = "3D ready, allows playback of full 3D high-definition content 480 Clear Motion Rate, less motion blur for your fast-paced videos HDMI and USB ports, lets you connect to a wide variety of devices WiFi capable, allows you to access countless hours visual content from the Internet";
    $clean_t = preg_replace('/[^a-zA-Z0-9_ %\[\]\.\(\)%&-]/s', '', $clean_t);
    // $r = substr_count($clean_t, 'to a');
    // $w = 'to a';
    // preg_match_all("/($w)/", $clean_t, $matches);
    // die("TEST ME: ".var_dump($matches));
    // $text = strtolower($clean_t);
    $text = $clean_t;

    // ---- convert to array (start)
    $words = explode(" ", $text); // !!! LOOP TARGET !!!
    $orig = explode(" ", $clean_t);
    $overall_words_count = count($words);
    // ---- convert to array (end)

    $res_stack = array();
    for($l = 6; $l >= 1; $l--) {
        for($i = 0, $j = $l; $j < $overall_words_count; $i++, $j++) {
            // --- PREPARE PHRASE STRING FOR CHECK
            $w = "";
            for($k = $i; $k <= $j; $k++ ) {
                $w = $w.$words[$k]." "; 
            }
            $w = substr($w, 0, strlen($w)-1);
            $w = trim($w);
            // --- CHECK OUT STRING DUPLICATIONS
            $r = substr_count($text, $w);
            if($r > 1) {
                $mid = array(
                    "ph" => trim($w),
                    "count" => $r,
                    "ph_length" => strlen($w)  
                );
                $res_stack[] = $mid;
            }
        }
    }

    // --- sort final result (start)
    $ph_length = array();
    foreach ($res_stack as $key => $row) {
        $ph_length[$key] = $row['ph_length'];
    }
    array_multisort($ph_length, SORT_DESC, $res_stack);
    // --- sort final result (end)

    $res_stack = array_unique($res_stack, SORT_REGULAR);

    // -- FILTER  OUT SUBSETS (START)
    if(count($res_stack) > 1) {
        foreach ($res_stack as $key => $value) {
            $inv_str = $value['ph'];
            // ----  CHECK OUT VALUE (START)
            foreach ($res_stack as $ka => $va) {
                if(($va['ph'] !== $inv_str) && strlen($va['ph']) > strlen($inv_str) && strpos($va['ph'], $inv_str) !== false) {
                    unset($res_stack[$key]);
                } 
            }
            // ----  CHECK OUT VALUE (END)
        }
    }
    // -- FILTER  OUT SUBSETS (END)

    return $res_stack;
  }

  public function measure_analyzer_start($clean_t) {
    // --- analyzer config (start)
    $min_phrase_size = 2;
    $max_phrase_size = 7;
    // --- analyzer config (end)

    // --- ANALYZER ALGO CODE (START)
    $text = trim($clean_t);
    // $text = preg_replace("/([a-zA-z])([^a-z ])/", "$1 $2", $text);
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
                    // echo $words[$p+$w]."<br />";
                    if(gettype($words[$p+$w]) !== "undefined" && $words[$p+$w] !== null) {
                        $phrase[] = $words[$p+$w];
                        $p_str .= $words[$p+$w]." ";
                        if(preg_match("/[^A-Za-z]/", $words[$p+$w])) {
                            $s_temp++;
                            if(preg_match("/[.]/", $words[$p+$w])) {
                                $period = true;
                            }
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
    // die(\var_dump($repeats));
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
            $final_ph = preg_replace('/[^A-Za-z0-9 ]/', '', $final_ph);
            $mid = array(
              "ph" =>  trim($final_ph),
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
