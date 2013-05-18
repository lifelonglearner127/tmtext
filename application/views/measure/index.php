<script>
$(document).ready(function () {
    $('#websites_first').ddslick({
        data: ddData_first,
        defaultSelectedIndex: 0
    });

    $('#websites_second').ddslick({
        data: ddData_second,
        defaultSelectedIndex: 0
    });

    $('#websites_third').ddslick({
        data: ddData_third,
        defaultSelectedIndex: 0
    });
});
</script>

    <div class="row-fluid">
            <input type="text" name="compare_text" style="width:90%" value="KDL-55EX640" id="compare_text" class="span11" placeholder=""/>
            <button type="submit" class="btn pull-right">Compare</button>
	</div>
	<div class="row-fluid">
            <div id="websites_first" class="dropdowns"></div>
            <div id="websites_second" class="dropdowns"></div>
            <div id="websites_third" class="dropdowns"></div>
        </div>
        <div class="row-fluid mt_10">
            <div class="span9"><b>Item description</b></div>
        </div>
	<div class="row-fluid">            
            <div class="span9 search_area uneditable-input cursor_default" style="height:350px; overflow : auto;" id="items">                
                <p>Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. 
                       Vestibulum tortor quam, feugiat vitae, ultricies eget, tempor sit amet, ante. 
                       Donec eu libero sit amet quam egestas semper. Aenean ultricies mi vitae est. 
                       Mauris placerat eleifend leo. Quisque sit amet est et sapien ullamcorper pharetra. 
                       Vestibulum erat wisi, condimentum sed, commodo vitae, ornare sit amet, wisi. 
                       Aenean fermentum, elit eget tincidunt condimentum, eros ipsum rutrum orci, 
                       sagittis tempus lacus enim ac dui. Donec non enim in turpis pulvinar facilisis. Ut felis. 
                       Praesent dapibus, neque id cursus faucibus, tortor neque egestas augue, eu vulputate magna eros eu erat. 
                       Aliquam erat volutpat. Nam dui mi, tincidunt quis, accumsan porttitor, facilisis luctus, metus</p>
                        <dl>
                            <dt>Definition list</dt>
                            <dd>Consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna 
                         aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea 
                         commodo consequat.</dd>
                            <dt>Lorem ipsum dolor sit amet</dt>
                            <dd>Consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna 
                         aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea 
                         commodo consequat.</dd>
                         </dl>                
            </div>
            <div class="span3" style="width:195px; margin-top: -80px;" id="attributes">
                    <h3>Metrics</h3>
                    <ul>
                        <li><a href="#">Site Metrics</a></li>
                        <li>Alexa: 156</li>
                        <li>SKUs: 1,278,400</li>
                        <li>&nbsp;</li>
                        <li><a href="#">Page Metrics</a></li>
                        <li>SKU: KDL-55EX640</li>
                     </ul>
	    </div>
	</div>