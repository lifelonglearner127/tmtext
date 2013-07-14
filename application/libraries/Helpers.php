<?php if ( ! defined('BASEPATH')) exit('No direct script access allowed');


class Helpers {

  public function __construct() {

  }

  public function test_screenshot() {
        include("GrabzItClient.class.php");
        $grabzIt = new GrabzItClient("M2NhMmU0MzkxZjJmNGVhNGE5N2M5YjZlZjI4M2QwODE=", "PzVPVDoIGj8/Pz8/Pz9lTD8tEj9sJhtHIj8CUz8/BWE=");
        $grabzIt->SetImageOptions("http://www.google.com");
        $filepath = $_SERVER["DOCUMENT_ROOT"]."/webroot/img/test.jpg";
        $grabzIt->SaveTo($filepath);
        return $filepath;
  }

  public function measure_analyzer_keywords($primary_ph, $secondary_ph, $tertiary_ph, $short_desc, $long_desc) {
    // --- default res array and values (start)
    $res = array(
        "primary" => array(0, 0),
        "secondary" => array(0, 0),
        "tertiary" => array(0, 0)
    );
    $short_desc_words_count = count(explode(" ", $short_desc));
    $long_desc_words_count = count(explode(" ", $long_desc));
    // --- default res array and values (end)

    // --- primary calculation (start)
    if($primary_ph !== "") {
        $primary_ph_words_count = count(explode(" ", $primary_ph));
        if($short_desc !== "") {
            // if($this->keywords_appearence($short_desc, $primary_ph) !== 0) $res['primary'][0] = $short_desc_words_count / ($this->keywords_appearence($short_desc, $primary_ph) * $primary_ph_words_count);
            $res['primary'][0] = ($this->keywords_appearence($short_desc, $primary_ph) * $primary_ph_words_count) / $short_desc_words_count;
        }
        if($long_desc !== "") {
            // if($this->keywords_appearence($long_desc, $primary_ph) !== 0) $res['primary'][1] = $long_desc_words_count / ($this->keywords_appearence($long_desc, $primary_ph) * $primary_ph_words_count);
            $res['primary'][1] = ($this->keywords_appearence($long_desc, $primary_ph) * $primary_ph_words_count) / $long_desc_words_count;
        }
    }
    // --- primary calculation (end)

    // --- secondary calculation (start)
    if($secondary_ph !== "") {
        $secondary_ph_words_count = count(explode(" ", $secondary_ph));
        if($short_desc !== "") {
            // if($this->keywords_appearence($short_desc, $secondary_ph) !== 0) $res['secondary'][0] = $short_desc_words_count / ($this->keywords_appearence($short_desc, $secondary_ph) * $secondary_ph_words_count);
            $res['secondary'][0] = ($this->keywords_appearence($short_desc, $secondary_ph) * $secondary_ph_words_count) / $short_desc_words_count;
        }
        if($long_desc !== "") {
            // if($this->keywords_appearence($long_desc, $secondary_ph) !== 0) $res['secondary'][1] = $long_desc_words_count / ($this->keywords_appearence($long_desc, $secondary_ph) * $secondary_ph_words_count);
            $res['secondary'][1] = ($this->keywords_appearence($long_desc, $secondary_ph) * $secondary_ph_words_count) / $long_desc_words_count;
        }
    }
    // --- secondary calculation (end)

    // --- tertiary calculation (start)
    if($tertiary_ph !== "") {
        $tertiary_ph_words_count = count(explode(" ", $tertiary_ph));
        if($short_desc !== "") {
            // if($this->keywords_appearence($short_desc, $tertiary_ph) !== 0) $res['tertiary'][0] = $short_desc_words_count / ($this->keywords_appearence($short_desc, $tertiary_ph) * $tertiary_ph_words_count);
            $res['tertiary'][0] = ($this->keywords_appearence($short_desc, $tertiary_ph) * $tertiary_ph_words_count) / $short_desc_words_count;
        }
        if($long_desc !== "") {
            // if($this->keywords_appearence($long_desc, $tertiary_ph) !== 0) $res['tertiary'][1] = $long_desc_words_count / ($this->keywords_appearence($long_desc, $tertiary_ph) * $tertiary_ph_words_count);
            $res['tertiary'][1] = ($this->keywords_appearence($long_desc, $tertiary_ph) * $tertiary_ph_words_count) / $long_desc_words_count;
        }
    }
    // --- tertiary calculation (end)

    return $res;
  }

  private function keywords_appearence($desc, $phrase) {
    return substr_count($desc, $phrase);
  }

  // public function measure_analyzer_start_v2($clean_t) { // !!! OLD ONE !!!
  //   $clean_t = preg_replace('/[^a-zA-Z0-9_ %\[\]\.\(\)%&-]/s', '', $clean_t);
  //   $text = $clean_t;

  //   // ---- convert to array (start)
  //   $words = explode(" ", $text); // !!! LOOP TARGET !!!
  //   $orig = explode(" ", $clean_t);
  //   $overall_words_count = count($words);
  //   // ---- convert to array (end)

  //   $res_stack = array();
  //   for($l = 6; $l >= 1; $l--) {
  //       for($i = 0, $j = $l; $j < $overall_words_count; $i++, $j++) {
  //           // --- PREPARE PHRASE STRING FOR CHECK
  //           $w = "";
  //           for($k = $i; $k <= $j; $k++ ) {
  //               $w = $w.$words[$k]." "; 
  //           }
  //           $w = substr($w, 0, strlen($w)-1);
  //           $w = trim($w);
  //           // --- CHECK OUT STRING DUPLICATIONS
  //           $r = substr_count($text, $w);
  //           if($r > 1) {
  //               $mid = array(
  //                   "ph" => trim($w),
  //                   "count" => $r,
  //                   "ph_length" => strlen($w)  
  //               );
  //               $res_stack[] = $mid;
  //           }
  //       }
  //   }

  //   // --- sort final result (start)
  //   $ph_length = array();
  //   foreach ($res_stack as $key => $row) {
  //       $ph_length[$key] = $row['ph_length'];
  //   }
  //   array_multisort($ph_length, SORT_DESC, $res_stack);
  //   // --- sort final result (end)

  //   $res_stack = array_unique($res_stack, SORT_REGULAR);

  //   // -- FILTER  OUT SUBSETS (START)
  //   if(count($res_stack) > 1) {
  //       foreach ($res_stack as $key => $value) {
  //           $inv_str = $value['ph'];
  //           // ----  CHECK OUT VALUE (START)
  //           foreach ($res_stack as $ka => $va) {
  //               if(($va['ph'] !== $inv_str) && strlen($va['ph']) > strlen($inv_str) && strpos($va['ph'], $inv_str) !== false) {
  //                   unset($res_stack[$key]);
  //               } 
  //           }
  //           // ----  CHECK OUT VALUE (END)
  //       }
  //   }
  //   // -- FILTER  OUT SUBSETS (END)

  //   return $res_stack;
  // }

  private function keywords_appearence_count($desc, $phrase) {
    return substr_count($desc, $phrase);
  }

  // private function keywords_appearence_count_exp($desc, $phrase) {
  //     $phrase_array = explode(" ", trim($phrase));
  //     $desc_array = explode(" ", trim($desc));
  //     $res = null;
  //     $res_debug = array();
  //     if(count($phrase_array) > 1) {
  //       $scan = array();
  //       foreach($phrase_array as $k => $v) {
  //         if(in_array($v, $desc_array)) {
  //           $mid = array(
  //             'word' => $v,
  //             'pos' => strpos($desc, $v)
  //           );
  //           $scan[] = $mid;
  //         } 
  //       }
  //       if(count($scan) == count($phrase_array)) {
  //         $res = $scan;
  //       }
  //     }
  //     return $res;
  // }

  private function keywords_appearence_count_expV2($desc, $phrase) {
      // $phrase_array = explode(" ", trim($phrase));
      // $desc_array = explode(" ", trim($desc));
      // $res = null;
      // $res_debug = array();
      // if(count($phrase_array) > 1) {
      //   $scan = array();
      //   foreach($phrase_array as $k => $v) {
      //     if(in_array($v, $desc_array)) {
      //       $mid = array(
      //         'word' => $v,
      //         'pos' => strpos($desc, $v)
      //       );
      //       $scan[] = $mid;
      //     } 
      //   }
      //   if(count($scan) == count($phrase_array)) {
      //     $res = $scan;
      //   }
      // }
      // return $res;
      $res = array();
      $string = "/$phrase/";
      if (preg_match_all($string, $desc, &$matches)) {
        $mid = array(
          'w' => $matches[0][0],
          'c' => count($matches[0])
        );
        $res[] = $mid;
      }
      return $res;
  }

  public function measure_analyzer_start_v2($clean_t) { // !!! NEW ONE !!!
    $clean_t = preg_replace('/[^a-zA-Z0-9_ %\[\]\.\(\)%&-]/s', '', $clean_t);
    // $clean_t = trim(str_replace('.', ' ', $clean_t));
    $text = $clean_t;

    // ---- convert to array (start)
    $words = explode(" ", $text); // !!! LOOP TARGET !!!
    $orig = explode(" ", $clean_t);
    $overall_words_count = count($words);
    // ---- convert to array (end)

    $res_stack = array();
    // $log = array();
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
            $r = $this->keywords_appearence_count(strtolower($text), strtolower($w));
            // --- debug logger (start)
            // $r_exp = $this->keywords_appearence_count_expV2(strtolower($text), strtolower($w));
            // $mid_debug = array(
            //   's_ph' => $w,
            //   'count' => $r,
            //   'count_exp' => $r_exp
            // );
            // $log[] = $mid_debug;
            // --- debug logger (end)
            if($r > 1 && count(explode(" ", trim($w))) > 1) {
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
        // $ph_length[$key] = $row['ph_length'];
        $ph_length[$key] = $row['count'];
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
    // die(var_dump($log));
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
