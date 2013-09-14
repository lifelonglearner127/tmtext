$(document).ready(function() {
var cmd = true;
    $('.cmp-btn').live('click',function() {
        if(cmd){
			test_page = $(this).attr('test_page');
			if( test_page )
				var thisText = $(this).parent().parent().parent().parent().parent().parent().find('.compare').text();
            else
				var thisText = $(this).parent().next().text();
            $(this).parent().next().addClass('clicked');
            //var thisText = $(this).parent().next().text();
            thisText = thisText.split(' ');
            var twoWordArr = new Array();
            for(var i=0; i<thisText.length; i++){
                if(thisText[i+1] && thisText[i])
                    twoWordArr[i] = clean_text(thisText[i])+' '+clean_text(thisText[i+1]);
            }
            $('.compare').each(function(){
                if(!$(this).hasClass('clicked')){
                    for(var j=0; j<twoWordArr.length; j++){
                        if(twoWordArr[j]){
                        var re = new RegExp(twoWordArr[j],"i");
                        $(this).html($(this).html().replace(re, '<span class="highlight">'+twoWordArr[j]+'</span>'));
                    }}
                }
            });
            
            cmd = false;
        } else {
            $('.compare').each(function(){
                $(this).html($(this).text());
                $(this).removeClass('clicked');
                 $(this).removeClass('seleckted_seo');
            });
                    
            cmd = true;
        }
    });
    
 
    $('.primary_name').live('click',function() {
        	
        if(!$(this).hasClass('is_selected')){
        
	$(this).closest('.seo_container').find('.is_selected').removeClass('is_selected');
        $(this).addClass('is_selected');
        var thisValue = $(this).next().find('.keyword_input').val();
        var arr = [];
        var re = new RegExp(thisValue,"gi");
        $(this).parent().parent().parent().next().find('.compare').addClass('seleckted_seo');
            $('.seleckted_seo').each(function(){
                arr = $(this).text().match(re);
                if(arr){
                 for(var i = 0; i<arr.length;i++){
                    var regv = new RegExp(arr[i],"g");
                    $(this).html($(this).html().replace(regv, '<span class="highlight">'+arr[i]+'</span>')); 
                    
                 }
                }
                arr = null;
            });
                  
            cmd_seo = false;

        } else { 
            
            $(this).removeClass('is_selected');
             $('.seleckted_seo').html($('.seleckted_seo').text());              
        
             $(this).parent().parent().parent().next().find('.compare').removeClass('seleckted_seo');
            
        }
    });
    
    
    
    $('.primary_name1').live('click',function() {
        	
        if(!$(this).hasClass('is_selected')){
        
	$(this).closest('.seo_container').find('.is_selected').removeClass('is_selected');
        $(this).addClass('is_selected');
        var thisValue = $(this).next().find('.primary_name_long').text();
        var arr = [];
        var re = new RegExp(thisValue,"gi");
        $(this).parent().parent().parent().next().find('.compare').addClass('seleckted_seo');
            $('.seleckted_seo').each(function(){
                arr = $(this).text().match(re);
                if(arr){
                 for(var i = 0; i<arr.length;i++){
                    var regv = new RegExp(arr[i],"g");
                    $(this).html($(this).html().replace(regv, '<span class="highlight">'+arr[i]+'</span>')); 
                    
                 }
                }
                arr = null;
            });
                  
            cmd_seo = false;

        } else { 
            
            $(this).removeClass('is_selected');
             $('.seleckted_seo').html($('.seleckted_seo').text());              
        
             $(this).parent().parent().parent().next().find('.compare').removeClass('seleckted_seo');
            
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
