#
# Use for debugging only!
# Usage: just open web-browser and type http://localhost:5000/get_data?url=http://www.amazon.in/Philips-AquaTouch-AT890-16-Shaver/dp/B009H0B8FU
#

import os
import sys
import json

from flask import Flask, jsonify, abort, request
app = Flask(__name__)


ajax_template = """
<html>
<head>
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js"></script>

  <script>
  !function($){

	"use strict";

  	$.fn.jJsonViewer = function (jjson) {
	    return this.each(function () {
	    	var self = $(this);
        	if (typeof jjson == 'string') {
          		self.data('jjson', jjson);
        	}
        	else if(typeof jjson == 'object') {
        		self.data('jjson', JSON.stringify(jjson))
        	}
        	else {
          		self.data('jjson', '');
        	}
	      	new JJsonViewer(self);
	    });
  	};

	function JJsonViewer(self) {
		var json = $.parseJSON(self.data('jjson'));
  		self.html('<ul class="jjson-container"></ul>');
  		self.find(".jjson-container").append(json2html([json]));
	}


	function json2html(json) {
		var html = "";
		for(var key in json) {
			if (!json.hasOwnProperty(key)) {
				continue;
			}

			var value = json[key],
				type = typeof json[key];

			html = html + createElement(key, value, type);
		}
		return html;
	}

	function encode(value) {
		return $('<div/>').text(value).html();
	}

	function createElement(key, value, type) {
		var klass = "object",
        	open = "{",
        	close = "}";
		if ($.isArray(value)) {
			klass = "array";
      		open = "[";
      		close = "]";
		}
		if(value === null) {
			return '<li><span class="key">"' + encode(key) + '": </span><span class="null">"' + encode(value) + '"</span></li>';
		}
		if(type == "object") {
			var object = '<li><span class="expanded"></span><span class="key">"' + encode(key) + '": </span> <span class="open">' + open + '</span> <ul class="' + klass + '">';
			object = object + json2html(value);
			return object + '</ul><span class="close">' + close + '</span></li>';
		}
		if(type == "number" || type == "boolean") {
			return '<li><span class="key">"' + encode(key) + '": </span><span class="'+ type + '">' + encode(value) + '</span></li>';
		}
		return '<li><span class="key">"' + encode(key) + '": </span><span class="'+ type + '">"' + encode(value) + '"</span></li>';
	}

	$(document).on("click", '.jjson-container .expanded', function(event) {
    	event.preventDefault();
    	event.stopPropagation();
    	$(this).addClass('collapsed').parent().find(">ul").slideUp(100);
  	});

	$(document).on('click', '.jjson-container .expanded.collapsed', function(event) {
  		event.preventDefault();
  		event.stopPropagation();
  		$(this).removeClass('collapsed').parent().find(">ul").slideDown(100);
	});

}(window.jQuery);
</script>
<style>
.jjson-container {
    font-size: 13px;
    line-height: 1.2;
    font-family: monospace;
    padding-left: 0;
    margin-left: 20px;
}
.jjson-container,
.jjson-container ul{
    list-style: none !important;
}
.jjson-container ul{
    padding: 0px !important;
    padding-left: 20px !important;
    margin: 0px !important;
}

.jjson-container li {
    position: relative;
}

.jjson-container > li  > .key,
.jjson-container .array .key{
    display: none;
}

.jjson-container .array .object .key{
    display: inline;
}

.jjson-container li:after {
    content: ",";
}

.jjson-container li:last-child:after {
    content: "";
}

.jjson-container .null{
    color: #999;
}
.jjson-container .string{
    color: #4e9a06;
}
.jjson-container .number{
    color: #a40000;
}
.jjson-container .boolean{
    color: #c4a000;
}
.jjson-container .key{
    color: #204a87;
}
.jjson-container .expanded{
    cursor: pointer;
}

.jjson-container .expanded:before{
    content: "-";
    font-size: 16px;
    width: 13px;
    text-align: center;
    line-height: 13px;
    font-family: sans-serif;
    color: #933;
    position: absolute;
    left: -15px;
    top: 3px;
}

.jjson-container .collapsed:before{
    content: "+";
    font-size: 14px;
    color: #000;
    top: 1px;
}

.jjson-container li .collapsed ~ .close:before {
    content: "... ";
    color: #999;
}
</style>
</head>
<body>
  <h4>URL: <span id="url">{{ url }}</span></h4>
  <p>
    <pre id="result" class="jjson">
      PROCESSING URL, PLEASE WAIT. DO NOT REFRESH THE PAGE.
    </pre>
  </p>
  <script>
    $.ajax({
      url: "/get_data_ajax",
      method: "GET",
      data: {url: $('#url').text()},
      success: function(result){
        $("#result").html(result);
        //alert( JSON.parse($("#result").html()) );
        $(".jjson").jJsonViewer( JSON.parse($("#result").html()) );
      }
    });
  </script>
</body>
</html>
"""


@app.route('/get_data_ajax')
def get_data_ajax():
    url = request.args.get('url', '').strip()
    print 'URL', url
    import time
    time.sleep(1)
    # TODO: process URL
    spider_result = {'abc': 1, 'list': [1,2,3]}
    return json.dumps(spider_result, sort_keys=True)


@app.route('/get_data', methods=['GET'])
def get_data():
    url = request.args.get('url', '').strip()
    if not url:
        return 'Invalid URL param given'
    return ajax_template.replace('{{ url }}', url)  # django-like templates =)


if __name__ == "__main__":
    app.run(debug=True)