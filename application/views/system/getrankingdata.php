<?php if(isset($track_data) && isset($track_data->data) && count($track_data->data) > 0) { ?>
    <?php foreach($track_data->data as $k => $v) { ?>
        <div class="alert"><?php echo $v->site; ?> <?php if(!isset($v->keywords) || count($v->keywords) == 0) { ?>(no data)<?php } ?></div>
        <?php if(isset($v->keywords) && count($v->keywords) > 0) { ?>
            <table class='table'>
                <thead>
                    <tr>
                        <th>keyword</th>
                        <th>location</th>
                        <th>engine</th>
                        <th>ranking</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach($v->keywords as $ks => $kv) { ?>
                        <tr>
                            <td>
                                <?php echo $kv->keyword; ?><br>
                                <button type='button' style='margin-top: 10px;' class='btn btn-danger' onclick="deleteKeyword('<?php echo $v->site; ?>', '<?php echo $kv->keyword; ?>')">Delete</button>
                            </td>
                            <td><?php echo $kv->location; ?></td>
                            <td><?php echo $kv->searchengine; ?></td>
                            <td>
                                <?php if(isset($kv->rankings) && count($kv->rankings) > 0) { ?>
                                    <?php foreach($kv->rankings as $ks => $vs) { ?>
                                        <p><span>Ranking: </span><span><?php echo $vs->ranking ?></span></p>
                                        <p><span>Ranked url: </span><span><?php echo $vs->rankedurl ?></span></p>
                                        <p><span>Date: </span><span><?php echo date('F jS, Y', $vs->datetime) ?></span></p>
                                    <?php } ?>
                                <?php } else { ?>
                                    <p>no ranking data</p>
                                <?php } ?>
                            </td>
                        </tr>
                    <?php } ?>
                </tbody>
            </table>
        <?php } ?>
    <?php } ?>
<?php } ?>