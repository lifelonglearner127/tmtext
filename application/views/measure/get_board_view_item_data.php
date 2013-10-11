<div class="modal-body" style='overflow: hidden'>
    <div class='snap_holder'>
        <div class='snap_area'><a target='_blank' href="<?php echo $data->url ?>"><img src="<?php echo $data->snap_path ?>"></a></div>
        <div class='info_area'>
            <div id='bi_info_bar' style='float: left; width: 180px; padding-top: 20px;'>
                <p style='font-weight: bold; font-size: 12px;'>Description word count: <?php echo $data->description_words; ?></p>
                <?php 
                    $k_words = array();
                    $tkdc_decoded = json_decode($data->title_keyword_description_count);
                    if(count($tkdc_decoded) > 0) {
                        foreach($tkdc_decoded as $ki => $vi) {
                            $mid = array(
                                'w' => $ki,
                                'c' => $vi,
                                'd' => 0
                            );
                            $k_words[] = $mid;
                        }
                    }
                    if(count($k_words) > 0) { 
                        $tkdd_decoded = json_decode($data->title_keyword_description_density);
                        if(count($tkdd_decoded) > 0) {
                            foreach($tkdd_decoded as $kd => $vd) { // === search for density
                                foreach ($k_words as $ks => $vs) {
                                    if($vs['w'] == $kd) {
                                        $k_words[$ks]['d'] = $vd;
                                    }
                                }
                            }
                        }
                    }
                ?>
                <?php if(count($k_words) > 0) { ?>
                    <p style='font-weight: bold; font-size: 12px;'>Keywords (frequency, density):</p>
                    <ul style='margin-left: 0px;'>
                    <?php foreach($k_words as $kw => $vw) { ?>
                        <li style='font-size: 12px; list-style: none; list-style-position: inside;'><span><?php echo $vw['w']; ?>: </span><span><?php echo $vw['c']; ?></span> - <span><?php echo $vw['d'] ?>%</span></li>
                    <?php } ?>
                    </ul>
                <?php } ?>
                <?php if($data->description_words != 0) { ?>
                <div>
                    <p class='bitem_desc_text_head'>Category description</p>
                    <div class='bitem_desc_text' style='display: none;'><?php echo $data->description_text; ?></div>
                </div>
                <?php } else { ?>
                <p>Category description: N/A</p>
                <?php } ?>
            </div>
            <div style='float: left; width: 40px;'><button id='bi_expand_bar_cnt' type='button' class='btn btn-success'><i class='icon-arrow-left icon-white'></i></button></div>
        </div>
    </div>
</div>
<div class="modal-footer">
    <a href="javascript:void(0)" class="btn" data-dismiss="modal">Close</a>
</div>

<script type='text/javascript'>
    $(document).ready(function() {
        $(".bitem_desc_text_head").click(function(e) {
            if($(".bitem_desc_text").is(":visible")) {
                $(".bitem_desc_text").slideUp();
            } else {
                $(".bitem_desc_text").slideDown();
            }
        });

        $("#bi_expand_bar_cnt").click(function(e) {
            if($("#bi_info_bar").is(":visible")) {
               $("#bi_info_bar").fadeOut('fast', function() {
                    $("#bi_expand_bar_cnt > i").removeClass('icon-arrow-left');
                    $("#bi_expand_bar_cnt > i").addClass('icon-arrow-right');
                    $("#preview_board_item_modal").animate({
                        width: '652px'
                    }, 200);
               }); 
            } else {
                $("#bi_expand_bar_cnt > i").removeClass('icon-arrow-right');
                $("#bi_expand_bar_cnt > i").addClass('icon-arrow-left');
                $("#preview_board_item_modal").animate({
                    width: '830px'
                }, 200, function() {
                    $("#bi_info_bar").fadeIn('fast');
                });
            }
        });

        // $("#bi_expand_bar_cnt").click(function(e) {
        //     $("#bi_info_bar").animate({
        //        width: '4px'
        //     }, { duration: 200, queue: false });
        //     $("#preview_board_item_modal").animate({
        //        width: '602px'
        //     }, { duration: 200, queue: false });
        // });

    });
</script>
