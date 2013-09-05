<script>
var customers=[]; 
   var result_data = <?php echo json_encode($same_pr); ?>;
 </script>
<?php if(!empty($same_pr)){
$same_pr  = array_values($same_pr);
 //   echo "<pre>";
 //   print_r($same_pr);
//   echo "<pre>";

$count=count($same_pr);
if(!isset($ind0)|| !isset($ind1)){
    $ind0=0;
    $ind1=1;
}

$min_price = 1000000000;
$j = 0;
$customers=array();
foreach ($same_pr as $ks => $vs) {
    $customers[]=$vs['customer'];
    foreach ($vs['three_last_prices'] as $key => $last_price) {
        
        $price = sprintf("%01.2f", floatval($last_price->price));
        if ($price < $min_price) {
            $min_price = $price;
        }


    }


}   

foreach($customers as $val){
 ?> 
 <script>
     var customer="<?php echo $val; ?>";
     customers.push(customer);
 </script>
<?php }
  
?>
 
<table  id="table_view" border="2" >
    <tr>
        <td class="table_titles" style=" border-top: 1px solid white;border-left: 1px solid white;"></td>
        <td style="background: #D6D6D6;" class="table_results" id="drop_1">
            <div id="h_1" class='h'>
               <input type="hidden" name='dd_customer' value="<?php echo $customers[$ind0]; ?>">
               <div id="an_grd_view_drop_gr0" class='an_grd_view_drop' style="display: block;margin: 0 auto;"></div>
            </div>
        </td>
         <?php if($count>1){?>
          
            <td style="background: #D6D6D6;" id="drop_2">
                <div id="h_1" class='h'>
                    <input type="hidden" name='dd_customer' value="<?php echo $customers[$ind1]; ?>">
                    <div id="an_grd_view_drop_gr1" class='an_grd_view_drop' style="display: block;margin: 0 auto;"></div>
               </div>

            </td>
        <?php }?>
    </tr>
    <tr>
        <td class="table_titles"><b>URL</b></td>
        
        <td><a style="font-size: 12px;text-decoration: underline;" target="_blank" href="<?php echo $same_pr[$ind0]['url']; ?>"><?php echo $same_pr[$ind0]['url']; ?></a></td>
         <?php if($count>1){?>
          <td><a style="font-size: 12px;text-decoration: underline;" target="_blank" href="<?php echo $same_pr[$ind1]['url']; ?>"  ><?php echo  $same_pr[$ind1]['url']; ?></a></td>
         <?php }?>
    </tr>
    <tr>
        <td class="table_titles"><b>Product</b></td>
        <td><?php echo $same_pr[$ind0]['product_name']; ?></td>
         <?php if($count>1){?>
          <td><?php echo  $same_pr[$ind1]['product_name']; ?></td>
         <?php }?>
    </tr>
    
    
    <?php 
    $pri= $same_pr[$ind0]['snap'][0];
    $pri1= $same_pr[$ind1]['snap'][0];
    $filename = './webroot/webshoots/'.$pri->snap;
    $filename1 ='./webroot/webshoots/'.$pri1->snap;
    $filename_img =  base_url().'webshoots/'.$pri->snap;
    $filename1_img =base_url().'webshoots/'.$pri1->snap;

    if (file_exists($filename) || file_exists($filename1)) {
        if( $pri->snap!= null ||  $pri1->snap!= null){
        ?>
    <tr>
        <td class="table_subtitles"></td>
        <td>
           <?php if(file_exists($filename)&& $pri->snap!= null){?>
               <img src="<?php echo $filename_img ; ?>" style="width:250px;padding:30px;" title = 'screenshot'">
           <?php }?>
        </td>
        <?php if($count>1){?>
        <td>
             <?php if(file_exists($filename1)&& $pri1->snap!= null){?>
                <img src="<?php echo $filename1_img; ?>" style="width:250px;padding:30px;" title='screenshot'">
             <?php } ?>
         </td>
         <?php }?>
    </tr>
    <?php }} ?>  
    
    <tr>
        <td class="table_titles"><b>Price</b></td>
        <td>
            <?php
            if(isset($same_pr[$ind0]['three_last_prices'][0])){
               $pr= $same_pr[$ind0]['three_last_prices'][0];
                
                if($ind0==0 && $pr->price!=$min_price ){
                    echo "<span style='color: red;'><b>$$pr->price</b></span>";
                }
                elseif($pr->price==$min_price){
                    echo "<span><b>$$pr->price</b></span>";
                }else{
                    echo '$'.$pr->price;
                }
               
            }else{echo '-';}
            ?>
        </td>
         <?php if($count>1){?>
          <td><?php 
           if(isset($same_pr[$ind1]['three_last_prices'][0])){
                $pr= $same_pr[$ind1]['three_last_prices'][0];
                
                if($ind1==0 && $pr->price!=$min_price ){
                    echo "<span style='color: red;'><b>$$pr->price</b></span>";
                }
                elseif($pr->price==$min_price){
                    echo "<span><b>$$pr->price</b></span>";
                }else{
                    echo '$'.$pr->price;
                }
           
           }else{echo '-';}
            ?>
          </td>
         <?php }?>
    </tr>
    <tr style="background: #e2e2e4;">
        <td class="table_titles"><b>Short Description</b></td>
        <td><?php 
                
                if ($same_pr[$ind0]['description'] !== null && trim($same_pr[$ind0]['description']) !== "") {
                    
                    if(!isset($same_pr[$ind0]['short_description_wc'])){
                        $description = preg_replace('/\s+/', ' ', $same_pr[$ind0]['description']);
                        $description = preg_replace('/[a-zA-Z]-/', ' ', $description);
                        $s_product_short_desc_count1 = count(explode(" ", $description));
                    }else{
                         $s_product_short_desc_count1 =$same_pr[$ind0]['short_description_wc'];
                    }
                }else{
                    $s_product_short_desc_count1=0;
                }
                if( $s_product_short_desc_count1>0){
                    echo $s_product_short_desc_count1.' words';
                }else{
                    echo '-';
                }
            ?>
        </td>
        <?php if($count>1){?>
          <td >
              <?php 
               if ($same_pr[$ind1]['description'] !== null && trim($same_pr[$ind1]['description']) !== "") {
                    if(!isset($same_pr[$ind1]['short_description_wc'])){ 
                        $description = preg_replace('/\s+/', ' ', $same_pr[$ind1]['description']);
                        $description = preg_replace('/[a-zA-Z]-/', ' ', $description);
                        $s_product_short_desc_count2 = count(explode(" ", $description));
                    }else{
                        $s_product_short_desc_count2=$same_pr[$ind1]['short_description_wc'];
                    }
                }else{
                    $s_product_short_desc_count2=0;
                }
                if( $s_product_short_desc_count2>0){
                    echo $s_product_short_desc_count2.' words';
                }else{
                    echo '-';
                }
                ?>
          </td>
         <?php }?>
    </tr>
    <tr>
        <td class="table_subtitles">SEO Keywords</td>
        <td>
            <?php
           if (count($same_pr[$ind0]['seo']['short']) > 0) {
                $k=0;
                foreach ($same_pr[$ind0]['seo']['short'] as $key => $value) {
                    $k++;
                    echo $value['ph']. ' ('.$value['count'].') ';
                    if($k<count($same_pr[$ind0]['seo']['short'])){echo " - ";}
                }
           }else{
               echo "None";
           }
            ?>
        </td>
         <?php if($count>1){?>
          <td><?php
          if (count($same_pr[$ind1]['seo']['short']) > 0) {
              $k=0;
                foreach ($same_pr[$ind1]['seo']['short'] as $key => $value) {
                    $k++;
                    echo $value['ph']. ' ('.$value['count'].') ';
                    if($k<count($same_pr[$ind1]['seo']['short'])){echo " - ";}
                }
           }else{
               echo "None";
           }
          ?>
          </td>
         <?php }?>
    </tr>
    <tr>
        <td class="table_subtitles">Duplicate Content</td>
        <td><?php
            if($s_product_short_desc_count1 >0){
				echo $same_pr[$ind0]['short_original'];
            }else{
                echo "-";
            } ?>
        </td>
        <?php if($count>1){?>
          <td><?php
          if($s_product_short_desc_count2 >0){
            echo  $same_pr[$ind1]['short_original'];
          }else{
              echo '-';
          }
          ?>
          </td>
        <?php }?>
    </tr>
    <tr style="background: #e2e2e4;">
         <td class="table_titles"><b>Long Description</b></td>
        <td>
            <?php 
                
                if ($same_pr[$ind0]['long_description'] !== null && trim($same_pr[$ind0]['long_description']) !== "") {
                   if(!isset($same_pr[$ind0]['long_description_wc'])){ 
                        $long_description = preg_replace('/\s+/', ' ', $same_pr[$ind0]['long_description']);
                        $long_description= preg_replace('/[a-zA-Z]-/', ' ', $long_description);
                        $s_product_long_desc_count1 = count(explode(" ", $long_description));
                   }else{
                       $s_product_long_desc_count1=$same_pr[$ind0]['long_description_wc'];
                   }
                }else{
                    $s_product_long_desc_count1=0;
                }
                if( $s_product_long_desc_count1>0){
                    echo $s_product_long_desc_count1.' words';
                }else{
                    echo '-';
                }
            ?>
        </td>
        <?php if($count>1){?>
          <td>
              <?php 
               if ($same_pr[$ind1]['long_description'] !== null && trim($same_pr[$ind1]['long_description']) !== "") {
                  if(!isset($same_pr[$ind1]['long_description_wc'])){   
                    $long_description = preg_replace('/\s+/', ' ', $same_pr[$ind1]['long_description']);
                    $long_description=preg_replace('/[a-zA-Z]-/', ' ', $long_description);
                    $s_product_long_desc_count2 = count(explode(" ", $long_description));
                  }else{
                       $s_product_long_desc_count2 = $same_pr[$ind1]['long_description_wc'];
                  }
                }else{
                    $s_product_long_desc_count2=0;
                }
                if( $s_product_long_desc_count2>0){
                    echo $s_product_long_desc_count2.' words';
                }else{
                    echo '-';
                }
                ?>
          </td>
         <?php }?>
    </tr>
    <tr>
        <td class="table_subtitles">SEO Keywords</td>
        <td>
            <?php
           if (count($same_pr[$ind0]['seo']['long']) > 0) {
               $k=0;
                foreach ($same_pr[$ind0]['seo']['long'] as $key => $value) {
                    $k++;
                    echo $value['ph']. ' ('.$value['count'].') ';
                    if($k<count($same_pr[$ind0]['seo']['long'])){echo " - ";}
                }
           }else{
               echo "None";
           }
            ?>
        </td>
         <?php if($count>1){?>
          <td><?php
          if (count($same_pr[$ind1]['seo']['long']) > 0) {
              $k=0;
                foreach ($same_pr[$ind1]['seo']['long'] as $key => $value) {
                    $k++;
                    echo $value['ph']. ' ('.$value['count'].') ';
                    if($k<count($same_pr[$ind1]['seo']['long'])){echo " - ";}
                }
           }else{
               echo "None";
           }
          ?>
          </td>
         <?php }?>
    </tr>
    <tr>
        <td class="table_subtitles">Duplicate Content</td>
        <td><?php
            if($s_product_long_desc_count1 >0){
               echo $same_pr[$ind0]['long_original'];  
            }else{
                echo "-";
            } ?>
        </td>
        <?php if($count>1){?>
          <td><?php
          if($s_product_long_desc_count2 >0){
            echo  $same_pr[$ind1]['long_original'];
          }else{
              echo '-';
          }
          ?>
          </td>
         <?php }?>
    </tr>
</table>
<?php }?>


<script>
    function inArray(needle, haystack) {
    var length = haystack.length;
    for(var i = 0; i < length; i++) {
        if(haystack[i] == needle)
            return true;
    }
    return false;
  }
//var count = <?php echo $count; ?>;
    var ddData_grids = [];
//    var customers= [];
  
        var newc_data=[];
       
        setTimeout(function() {
            selected_customers=[];
            var customers_list = $.post(base_url + 'index.php/measure/getsiteslist_new', { }, function(c_data) {
            //console.log(c_data);
            var j=0;
            
            for (var key in c_data){
               console.log(customers);
               if(inArray(c_data[key].value,customers)){
                  //console.log(c_data[key].value);
                  newc_data[j]=c_data[key];
                  j++;
               }
            };
            
           var drops=[];
           drops.push("<?php echo $customers[$ind0]; ?>");
           drops.push("<?php echo $customers[$ind1]; ?>");
           for (var i = 0; i < 2; i++) {
                    var grid1 = $('#an_grd_view_drop_gr' + i).msDropDown({byJson: {data: newc_data}}).data("dd");
                    if (grid1 != undefined) {
                        grid1.setIndexByValue(drops[i]);
                    }
                }

            });
        }, 100);
        
   $("#table_view .an_grd_view_drop select").live('change', function(){
       var drop1=$("#an_grd_view_drop_gr0 select").val();
       var drop2=$("#an_grd_view_drop_gr1 select").val();
       $.each(customers,function(index, value){
           if(value===drop1){
               drop1=index;
           }
           if(value===drop2){
               drop2=index;
           }
       });
       var grid_view = $.post(editorTableViewBaseUrl, {ind0:drop1,ind1:drop2,result_data:result_data,selectedUrl: $('#products li[data-status=selected] span').eq(1).text()}, 'html').done(function(data) {
       $("#compet_area_grid").html(data);  
       });
   });     
        
 </script>
