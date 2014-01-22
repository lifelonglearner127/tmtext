<div class="tabbable">
      <?php $this->load->view('system/_tabs', array(
		'active_tab' => 'system/batch_review'
	)) ?>
    <div class="tab-content">
        <link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/smoothness/jquery-ui-1.8.2.custom.css" />
        <link type="text/css" rel="stylesheet" href="<?php echo base_url();?>css/styles.css" />
        <div class="row-fluid">
            <div id="ajaxLoadAni">
                <span>Loading...</span>
            </div>

            <div id="tabs" class="mt_10">

                <ul>
                    <li><a href="#read">Review</a></li>
                    <!--li><a href="#create"></a></li-->
                </ul>

                <div id="read">
                    <table id="records">
                        <thead>
                        <tr>
                            <th>Date Created</th>
                            <th>Customer</th>
                            <th>Batch Name</th>
                            <th># Items</th>
                            <th><div class="draggable">Actions</div></th>
                        </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
                <div id="create">
                </div>

            </div> <!-- end tabs -->

            <!-- update form in dialog box -->
            <div id="updateDialog" title="Update">
                <div>
                    <form action="" method="post">
                        <p>
                            <label for="title">Batch Name:</label>
                            <input type="text" id="title" name="title" />
                        </p>

                        <input type="hidden" id="userId" name="id" />
                    </form>
                </div>
            </div>

            <!-- delete confirmation dialog box -->
            <div id="delConfDialog" title="Confirm">
                <p>Are you sure you want to delete batch <span class="batch_name"></span>?</p>
            </div>


            <!-- message dialog box -->
            <div id="msgDialog"><p></p></div>

         
            <script type="text/template" id="readTemplate">
                <tr id="${id}">
                    <td>${created}</td>
                    <td>${name}</td>
                    <td>${title}</td>
                    <td>${items}</td>
                   <td nowrap><a class="updateBtn icon-edit" style="float:left;" href="${updateLink}"></a>
                        <a class="deleteBtn icon-remove ml_5" href="${deleteLink}"></a>
                    </td>
                </tr>
            </script>

            <script type="text/javascript" src="<?php echo base_url();?>js/batch_review.js"></script>
        </div>
    </div>
</div>
