var webserver = {
    init: function() {
	/* Web Page communication */  
        webserver.ena_form = document.getElementById('ena_form');
        YAHOO.util.Event.addListener(webserver.ena_form, 'submit', webserver.ena_submit);
        YAHOO.util.Event.addListener("biasoff", "click", webserver.biasoff);
        YAHOO.util.Event.addListener("poweron", "click", webserver.poweron);
        YAHOO.util.Event.addListener("poweroff", "click", webserver.poweroff);

        webserver.biasdac_form = document.getElementById('biasdac_form');
        YAHOO.util.Event.addListener(webserver.biasdac_form, 'submit', webserver.biasdac_submit);
        YAHOO.util.Event.addListener("biasread", "click", webserver.biasreadback);
        webserver.clkdac_form = document.getElementById('clkdac_form');
        YAHOO.util.Event.addListener(webserver.clkdac_form, 'submit', webserver.clkdac_submit);
		YAHOO.util.Event.addListener("clkread", "click", webserver.clk_button);

},

 clkdac_submit: function(e) {
    YAHOO.util.Event.preventDefault(e);
    YAHOO.util.Connect.setForm(webserver.clkdac_form);
	YAHOO.util.Connect.asyncRequest('POST', '/cmd/clkdac', webserver.dac_callback);
   },
	
 clk_button: function(e) {
    YAHOO.util.Event.preventDefault(e);
	YAHOO.util.Connect.asyncRequest('POST', '/cmd/readclk', webserver.clk_read_callback);
},
clk_read_callback: {															
	success: function(o) {														
        /* This turns the JSON string into a JavaScript object. */
        var strJSON = '{'+ o.responseText + '}';
	var objJSON = eval("(function(){return " + strJSON + ";})()");
	webserver.clkdac_form.ch0.value = objJSON.ch0;
	webserver.clkdac_form.ch1.value = objJSON.ch1;
 	webserver.clkdac_form.ch2.value = objJSON.ch2;
	webserver.clkdac_form.ch3.value = objJSON.ch3;
	webserver.clkdac_form.ch4.value = objJSON.ch4;
	webserver.clkdac_form.ch5.value = objJSON.ch5;
	webserver.clkdac_form.ch6.value = objJSON.ch6;
	webserver.clkdac_form.ch7.value = objJSON.ch7;
	webserver.clkdac_form.ch8.value = objJSON.ch8;
	webserver.clkdac_form.ch9.value = objJSON.ch9;
	webserver.clkdac_form.ch10.value = objJSON.ch10;
	webserver.clkdac_form.ch11.value = objJSON.ch11;
	webserver.clkdac_form.ch12.value = objJSON.ch12;	
	webserver.clkdac_form.ch13.value = objJSON.ch13;
	webserver.clkdac_form.ch14.value = objJSON.ch14;
	webserver.clkdac_form.ch15.value = objJSON.ch15;
	webserver.clkdac_form.ch16.value = objJSON.ch16;
	webserver.clkdac_form.ch17.value = objJSON.ch17;
	webserver.clkdac_form.ch18.value = objJSON.ch18;	
	webserver.clkdac_form.ch19.value = objJSON.ch19;
	webserver.clkdac_form.ch20.value = objJSON.ch20;
     },
    failure: function(o) {
                   alert('XHR request failed readback: ' + o.statusText);
    },
    timeout: 10000
  },

biasdac_submit: function(e) {
    YAHOO.util.Event.preventDefault(e);
    YAHOO.util.Connect.setForm(webserver.biasdac_form);
	YAHOO.util.Connect.asyncRequest('POST', '/cmd/dacxhr', webserver.dac_callback);
   },
	
biasreadback: function(e) {
    YAHOO.util.Event.preventDefault(e);
 	YAHOO.util.Connect.asyncRequest('POST', '/cmd/readxhr', webserver.biasread_callback);
},
biasread_callback: {															
	success: function(o) {														
        /* This turns the JSON string into a JavaScript object. */
    var strJSON = '{'+ o.responseText + '}';
	var objJSON = eval("(function(){return " + strJSON + ";})()");
	webserver.biasdac_form.ch9.value = objJSON.ch9;
	webserver.biasdac_form.ch10.value = objJSON.ch10;
	webserver.biasdac_form.ch11.value = objJSON.ch11;
	webserver.biasdac_form.ch12.value = objJSON.ch12;	
	webserver.biasdac_form.ch13.value = objJSON.ch13;
	webserver.biasdac_form.ch14.value = objJSON.ch14;
	webserver.biasdac_form.ch15.value = objJSON.ch15;
	webserver.biasdac_form.ch16.value = objJSON.ch16;
	webserver.biasdac_form.ch17.value = objJSON.ch17;
	webserver.biasdac_form.ch18.value = objJSON.ch18;	
	webserver.biasdac_form.ch19.value = objJSON.ch19;
	webserver.biasdac_form.ch20.value = objJSON.ch20;
	webserver.biasdac_form.vioff01.value = objJSON.vioff01;
	webserver.biasdac_form.vioff02.value = objJSON.vioff02;
	webserver.biasdac_form.vioff03.value = objJSON.vioff03;
	webserver.biasdac_form.vioff04.value = objJSON.vioff04;
    },
    failure: function(o) {
                   alert('XHR request failed readback: ' + o.statusText);
    },
    timeout: 10000
  },
  
ena_submit: function(e) {
	/*alert('test');*/
        YAHOO.util.Event.preventDefault(e);
       	YAHOO.util.Connect.setForm(webserver.ena_form);
        YAHOO.util.Connect.asyncRequest('POST', '/cmd/enable', webserver.ena_callback);
   },

ena_callback: {															
	success: function(o) {														
	var strJSON = '{'+ o.responseText + '}';
	var objJSON = eval("(function(){return " + strJSON + ";})()");
	webserver.ena_form.onoff.value = objJSON.toggle;
    },
	   failure: function(o) {
                   alert('XHR request failed DATA: ' + o.statusText);
    },
    timeout: 10000
  },
biasoff: function(e) {
	/*alert('test');*/
        YAHOO.util.Event.preventDefault(e);
        YAHOO.util.Connect.asyncRequest('POST', '/cmd/enableoff', webserver.ena_callback);
   },
 poweron: function(e) {
	/*alert('test');*/
        YAHOO.util.Event.preventDefault(e);
        YAHOO.util.Connect.asyncRequest('POST', '/cmd/power1', webserver.ena_callback);
   },
 poweroff: function(e) {
	/*alert('test');*/
        YAHOO.util.Event.preventDefault(e);
        YAHOO.util.Connect.asyncRequest('POST', '/cmd/power0', webserver.ena_callback);
   },
   
 dac_callback: {															
	success: function(o) {														
        /* TODO acknowledge update. */								
    },
    failure: function(o) {
                   alert('XHR request failed DATA: ' + o.statusText);
    },
    timeout: 10000
  }
  
};

YAHOO.util.Event.addListener(window, 'load', webserver.init);

function popup(url) {
	newwindow = window.open(url, 'image', 'height=400,width=550,resizeable=1,scrollbards,menubar=0,toolbar=0');
	if (window.focus) {newwindow.focus()}
	return false;
}
