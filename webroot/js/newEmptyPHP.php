<html>
    <head runat="server">
        <title>Untitled Page</title>
        <script type="text/javascript" language="javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.4/jquery.min.js"></script>
        <script type="text/javascript" language="javascript" src="http://johannburkard.de/resources/Johann/jquery.highlight-3.js"></script>
        <style type="text/css">
            .highlight { background-color: yellow }
        </style>
        <script language="javascript" type="text/javascript">
            $(document).ready(function(){
                var s = $('#id1').text();
                var arr = s.split(' ');
                var divs =  $('.compare');
                $('.compare').removeHighlight();
                if(divs.length>0){
                    $('.compare').each(function(k,v){
                        for(i = 0;i < arr.length;i++){
                            if(arr[i].length>1){
                                var k = $.trim(arr[i]).replace('.','');
                                $(this).highlight(k);
                            }
                                    
                        }
                    });
                }
            });
        </script>
    </head>
    <body>
        <div id="id1" class="compare">hajan text. world.</div>
        <div id="id2" class="compare">
            hajan text text text hello hajan text another text hajan hajan text.hajan.
        </div>
        <div id="id3" class="compare">
            hajan text text text hello world hajan text another text hajan hajan text.hajan.
        </div>
    </body>
</html>



















jQuery.fn.highlight = function(pat) {
    function innerHighlight(node, pat) {
        var skip = 0;
        if (node.nodeType == 3) {
            var pos = node.data.toUpperCase().indexOf(pat);
            if (pos >= 0) {
                var spannode = document.createElement('span');
                spannode.className = 'highlight';
                var middlebit = node.splitText(pos);
                var endbit = middlebit.splitText(pat.length);
                var middleclone = middlebit.cloneNode(true);
                spannode.appendChild(middleclone);
                middlebit.parentNode.replaceChild(spannode, middlebit);
                skip = 1;
            }
        }
        else if (node.nodeType == 1 && node.childNodes && !/(script|style)/i.test(node.tagName)) {
            for (var i = 0; i < node.childNodes.length; ++i) {
                i += innerHighlight(node.childNodes[i], pat);
            }
        }
        return skip;
    }
    return this.each(function() {
        innerHighlight(this, pat.toUpperCase());
    });
};

jQuery.fn.removeHighlight = function() {
    return this.find("span.highlight").each(function() {
        this.parentNode.firstChild.nodeName;
        with (this.parentNode) {
            replaceChild(this.firstChild, this);
            normalize();
        }
    }).end();
};
function short_long_dublicate(txt) {
    var arr = txt.split(' ');
    var divs = $('.compare');
    $(document).removeHighlight();
    if (divs.length > 0) {for(var j in arr){console.log(arr[j]+"<br>")}
        $('.compare').each(function(k, v) {
            for (i = 0; i < arr.length; i++) {
                if (arr[i].length > 1) {
                    var k = $.trim(arr[i]).replace('.', '');
                    $(this).highlight(k);
                }

            }
        });
    }
}
