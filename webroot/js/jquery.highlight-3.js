$(document).ready(function() {
var cmd = true;
    $('.cmp-btn').live('click',function() {
        if(cmd){
			test_page = $(this).attr('test_page');
			if( test_page )
				var thisText = $(this).parent().parent().parent().parent().parent().parent().find('.compare').text();
            else
				var thisText = $(this).parent().next().text();
            
            thisText = thisText.split(' ');
            var twoWordArr = new Array();
            for(var i=0; i<thisText.length; i++){
                if(thisText[i+1])
                    twoWordArr[i] = clean_text(thisText[i])+' '+clean_text(thisText[i+1]);
            }
            $('.compare').each(function(){
    //            if(!$(this).hasClass('clicked')){
                    for(var j=0; j<twoWordArr.length; j++){
                        var re = new RegExp(twoWordArr[j],"i");
                        $(this).html($(this).html().replace(re, '<span style="background-color: yellow;" >'+twoWordArr[j]+'</span>'));
                    }
    //            }
            });
            cmd = false;
        } else {
            $('.compare').each(function(){
                $(this).html($(this).text());
//                $(this).children('span').each(function(){
//                    $(this).html();
//                });
            });
                    
            cmd = true;
        }
    });
    
});
function clean_text(text) {
    var new_text = text;
    new_text = new_text.replace(/\,/g, '');	 new_text = new_text.replace(/!/g, '');
    new_text = new_text.replace(/@/g, '');	 new_text = new_text.replace(/#/g, '');
    new_text = new_text.replace(/№/g, '');	 new_text = new_text.replace(/\"/g, '');
    new_text = new_text.replace(/\;/g, '');	 new_text = new_text.replace(/\$/g, '');
    new_text = new_text.replace(/\%/g, '');	 new_text = new_text.replace(/\:/g, '');
    new_text = new_text.replace(/\^/g, '');	 new_text = new_text.replace(/\&/g, '');
    new_text = new_text.replace(/\?/g, '');	 new_text = new_text.replace(/\*/g, '');
    new_text = new_text.replace(/\(/g, '');	 new_text = new_text.replace(/\)/g, '');
    new_text = new_text.replace(/\-/g, '');	 new_text = new_text.replace(/\_/g, '');
    new_text = new_text.replace(/\=/g, '');	 new_text = new_text.replace(/\+/g, '');
    new_text = new_text.replace(/\//g, '');	 new_text = new_text.replace(/\`/g, '');
    new_text = new_text.replace(/\~/g, '');	 new_text = new_text.replace(/\{/g, '');
    new_text = new_text.replace(/\}/g, '');	 new_text = new_text.replace(/\[/g, '');
    new_text = new_text.replace(/\]/g, '');	 new_text = new_text.replace(/\\/g, '');
    new_text = new_text.replace(/\|/g, '');	 new_text = new_text.replace(/\'/g, '');
    new_text = new_text.replace(/\</g, '');	 new_text = new_text.replace(/\>/g, '');
    new_text = new_text.replace(/\./g, '');
    return new_text;
}
