<div class="modal-body" style='overflow: hidden'>
    <div class='snap_holder'>
        <div class='snap_area'><a target='_blank' href="<?php echo $data->snap_path ?>"><img src="<?php echo $data->snap_path ?>"></a></div>
        <div class='info_area'>
            <b>Description word count: <?php echo $data->description_words; ?></b><br><br>
            <?php if($data->description_words != 0) { ?>
            <b>Category description: <?php echo $data->description_text; ?></b><br>
            <?php } else { ?>
            <b>Category description: N/A</b>
            <?php } ?>
            <b></b>
        </div>
    </div>
</div>
<div class="modal-footer">
    <a href="javascript:void(0)" class="btn" data-dismiss="modal">Close</a>
</div>