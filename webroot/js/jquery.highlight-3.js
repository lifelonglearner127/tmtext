
$.fn.highlight = function (b, k) {
     function l() {
         $("." + c.className).each(function (c, e) {
             var a = e.previousSibling,
                 d = e.nextSibling,
                 b = $(e),
                 f = "";
             a && 3 == a.nodeType && (f += a.data, a.parentNode.removeChild(a));
             e.firstChild && (f += e.firstChild.data);
             d && 3 == d.nodeType && (f += d.data, d.parentNode.removeChild(d));
             b.replaceWith(f)
         })
     }

     function h(b) {
         b = b.childNodes;
         for (var e = b.length, a; a = b[--e];)
             if (3 == a.nodeType) {
                 if (!/^\s+$/.test(a.data)) {
                     var d = a.data,
                         d = d.replace(m, '<span class="' + c.className + '">$1</span>');
                     $(a).replaceWith(d)
                 }
             } else 1 == a.nodeType && a.childNodes && (!/(script|style)/i.test(a.tagName) && a.className != c.className) && h(a)
     }
     var c = {
         split: "\\s+",
         className: "highlight",
         caseSensitive: !1,
         strictly: !1,
         remove: !0
     }, c = $.extend(c, k);
     c.remove && l();
     b = $.trim(b);
     var g = c.strictly ? "" : "\\S*",
         m = RegExp("(" + g + b.replace(RegExp(c.split, "g"), g + "|" + g) + g + ")", (c.caseSensitive ? "" : "i") + "g");
     return this.each(function () {
         b && h(this)
     })
 };
 var cnt = 0;
$('.cmp-btn').live('click', function() {
    if(cnt == 0){
        var settings = {};
         var pattern = $(this).parent().parent('.cmp-area').find('p.compare').text();
       
       // $("#right").prop("checked") && (settings.strictly = true);
       // $("#case").prop("checked") && (settings.caseSensitive = true);
       // $("#remove").prop("checked") && (settings.remove = false);
        pattern && $("p.compare").highlight(pattern, settings);f1();
    cnt = 1;    
    }else{
        $('.highlight').removeAttr("class");
        cnt = 0;
    }
 });

function f1(){
    var arr =[];
    $(".highlight").each(function(index,val){
         arr.push($(this).text());
         arr = arr.sort();
    });
    for(var i = 0; i<= arr.length;i++){ 
        if(arr[i] != arr[i+1] && arr[i] != arr[i-1]){
            $(".highlight").each(function(index,val){
                if($(this).text() == arr[i])
                    $(this).removeAttr("class");
           });
           delete arr[i];
        }
    }
} 

//
//function generate_password(number)
//  {
//      var arr = [];
//    arr = ['a','b','c','d','e','f',
//            'g','h','i','j','k','l',
//            'm','n','o','p','r','s',
//            't','u','v','x','y','z',
//            'A','B','C','D','E','F',
//            'G','H','I','J','K','L',
//            'M','N','O','P','R','S',
//            'T','U','V','X','Y','Z',
//            '1','2','3','4','5','6',
//            '7','8','9','0']; 
//    var pass = "#";
//    for(var i = 0; i < number; i++)
//    {
//      // Вычисляем случайный индекс массива
//      var index = Math.floor(Math.random( ) * (arr.length-1));
//      pass += arr[index];
//    }
//    return pass;
//  }  style="color:'+generate_password(6)+'"