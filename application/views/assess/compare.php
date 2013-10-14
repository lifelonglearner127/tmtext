<?php if(count($results)>0){ ?>
<table class="products_tb">
    
       <tr class="products_tb_heading">
         <td>Snapshot</td>
         <td>Product Name</td>
         <td class="url_style">URL</td>
         <td>Words Short</td>
         <td>Words Long</td>
         <td>Snapshot</td>
         <td>Product Name</td>
         <td class="url_style">URL</td>
         <td>Words Short</td>
         <td>Words Long</td>
     </tr>
    
   <?php foreach($results as $res){
       $cmp = $res->cmp_item;
   ?>
    <tr>
        <td>Snapshot</td>
         <td><?php echo $res->product_name;  ?></td>
         <td class="url_style"><span><?php echo $res->url;  ?></span></td>
         <td><?php echo $res->short_description_wc;?></td>
         <td><?php echo $res->short_description_wc;?></td>
         <td>Snapshot</td>
         <td><?php echo $cmp->product_name;  ?></td>
         <td class="url_style"><span><?php echo $cmp->url;  ?></span></td>
         <td><?php echo $cmp->short_description_wc;?></td>
         <td><?php echo $cmp->short_description_wc;?></td>
    </tr>   

  <?php    } ?>
</table>
<?php }?>