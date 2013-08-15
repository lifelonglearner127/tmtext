<script>
   var customers=[];  
 </script>
<?php if(!empty($same_pr)){
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
 <style>
     #table_view td{
         width: 400px ;
         text-align: center;
     }
      #table_view .table_titles{
         width: 150px !important;
     }
     .h{
         
         margin-left: 47px;
     }
 </style>
<table  id="table_view" border="2" >
    <tr>
        <td class="table_titles"></td>
        <td class="table_results" id="drop_1">
            <div id="h_1" class='h'>
               <input type="hidden" name='dd_customer' value="<?php echo $customers[0]; ?>">
               <div id="an_grd_view_drop_gr0" class='an_grd_view_drop'></div>
            </div>
        </td>
         <?php if(count($same_pr)>1){?>
          
            <td id="drop_2">
                <div id="h_1" class='h'>
                    <input type="hidden" name='dd_customer' value="<?php echo $customers[1]; ?>">
                    <div id="an_grd_view_drop_gr1" class='an_grd_view_drop'></div>
               </div>

            </td>
        <?php }?>
    </tr>
    <tr>
        <td class="table_titles"><b>URL</b></td>
        
        <td><?php echo $same_pr[0]['url']; ?></td>
         <?php if(count($same_pr)>1){?>
          <td><?php echo  $same_pr[1]['url']; ?></td>
         <?php }?>
    </tr>
    <tr>
        <td class="table_titles"><b>Product</b></td>
        <td><?php echo $same_pr[0]['product_name']; ?></td>
         <?php if(count($same_pr)>1){?>
          <td><?php echo  $same_pr[1]['product_name']; ?></td>
         <?php }?>
    </tr>
    <tr>
        <td class="table_titles"><b>Price</b></td>
        <td>
            <?php
            if(isset($same_pr[0]['three_last_prices'][0])){
            echo '$'.$same_pr[0]['three_last_prices'][0]->price;
            }else{echo '-';}
            ?>
        </td>
         <?php if(count($same_pr)>1){?>
          <td><?php 
           if(isset($same_pr[1]['three_last_prices'][0])){
            echo '$'.$same_pr[1]['three_last_prices'][0]->price;
            }else{echo '-';}
            ?>
          </td>
         <?php }?>
    </tr>
    <tr>
        <td class="table_titles"><b>Short Description</b></td>
        <td><?php 
                
                if ($same_pr[0]['description'] !== null && trim($same_pr[0]['description']) !== "") {
                    $description = preg_replace('/\s+/', ' ', $same_pr[0]['description']);
                    $s_product_short_desc_count1 = count(explode(" ", $description));
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
        <?php if(count($same_pr)>1){?>
          <td >
              <?php 
               if ($same_pr[1]['description'] !== null && trim($same_pr[1]['description']) !== "") {
                    $description = preg_replace('/\s+/', ' ', $same_pr[1]['description']);
                    $s_product_short_desc_count2 = count(explode(" ", $description));
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
        <td class="table_titles">SEO Keywords</td>
        <td>
            <?php
           if (count($same_pr[0]['seo']['short']) > 0) {
               $k=0;
                foreach ($vs['seo']['short'] as $key => $value) {
                    $k++;
                    echo $value['ph']. '('.$value['count'].')';
                    if($k<count($same_pr[0]['seo']['short'])){echo " - ";}
                }
           }else{
               echo "None";
           }
            ?>
        </td>
         <?php if(count($same_pr)>1){?>
          <td><?php
          if (count($same_pr[1]['seo']['short']) > 0) {
              $k=0;
                foreach ($same_pr[1]['seo']['short'] as $key => $value) {
                    $k++;
                    echo $value['ph']. '('.$value['count'].')';
                    if($k<count($same_pr[1]['seo']['short'])){echo " - ";}
                }
           }else{
               echo "None";
           }
          ?>
          </td>
         <?php }?>
    </tr>
    <tr>
        <td class="table_titles">Dublicate Content</td>
        <td><?php
            if($s_product_short_desc_count1 >0){
               echo $same_pr[0]['short_original'];  
            }else{
                echo "-";
            } ?>
        </td>
        <?php if(count($same_pr)>1){?>
          <td><?php
          if($s_product_short_desc_count2 >0){
            echo  $same_pr[1]['short_original'];
          }else{
              echo '-';
          }
          ?>
          </td>
        <?php }?>
    </tr>
    <tr>
         <td class="table_titles"><b>Long Description</b></td>
        <td>
            <?php 
                
                if ($same_pr[0]['long_description'] !== null && trim($same_pr[0]['long_description']) !== "") {
                    $long_description = preg_replace('/\s+/', ' ', $same_pr[0]['long_description']);
                    $s_product_long_desc_count1 = count(explode(" ", $long_description));
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
        <?php if(count($same_pr)>1){?>
          <td>
              <?php 
               if ($same_pr[1]['long_description'] !== null && trim($same_pr[1]['long_description']) !== "") {
                    $long_description = preg_replace('/\s+/', ' ', $same_pr[1]['long_description']);
                    $s_product_long_desc_count2 = count(explode(" ", $long_description));
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
        <td class="table_titles">SEO Keywords</td>
        <td>
            <?php
           if (count($same_pr[0]['seo']['long']) > 0) {
               $k=0;
                foreach ($same_pr[0]['seo']['long'] as $key => $value) {
                    $k++;
                    echo $value['ph']. '('.$value['count'].')';
                    if($k<count($same_pr[0]['seo']['long'])){echo " - ";}
                }
           }else{
               echo "None";
           }
            ?>
        </td>
         <?php if(count($same_pr)>1){?>
          <td><?php
          if (count($same_pr[1]['seo']['long']) > 0) {
              $k=0;
                foreach ($same_pr[1]['seo']['long'] as $key => $value) {
                    $k++;
                    echo $value['ph']. '('.$value['count'].')';
                    if($k<count($same_pr[1]['seo']['long'])){echo " - ";}
                }
           }else{
               echo "None";
           }
          ?>
          </td>
         <?php }?>
    </tr>
    <tr>
        <td class="table_titles">Dublicate Content</td>
        <td><?php
            if($s_product_long_desc_count1 >0){
               echo $same_pr[0]['long_original'];  
            }else{
                echo "-";
            } ?>
        </td>
        <?php if(count($same_pr)>1){?>
          <td><?php
          if($s_product_long_desc_count2 >0){
            echo  $same_pr[1]['long_original'];
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
var count =<?php echo count($same_pr); ?>;
    var ddData_grids = [];
//    var customers= [];
  
        var newc_data=[];
        
        setTimeout(function() {
            selected_customers=[];
            var customers_list = $.post(base_url + 'index.php/measure/getsiteslist_new', { }, function(c_data) {
            //console.log(c_data);
            var j=0;
            for (var key in c_data){

               if(inArray(c_data[key].value,customers)){
                  //console.log(c_data[key].value);
                  newc_data[j]=c_data[key];
                  j++;
               }
            };
          console.log(customers);
            for (var i = 0; i < 2; i++) {
                    var grid1 = $('#an_grd_view_drop_gr' + i).msDropDown({byJson: {data: newc_data}}).data("dd");
                    if (grid1 != undefined) {
                        grid1.setIndexByValue(customers[i]);
                    }
                }

            });
        }, 100);
    
       </script>