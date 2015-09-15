var webserver = {
    init: function() {
	/* Web Page communication */  
	 /* obtain a pointer to the dac_form and its result */
		webserver.timing_form = document.getElementById('timing_form');
        YAHOO.util.Event.addListener(webserver.timing_form, 'submit', webserver.timing_submit);
		
        webserver.adc_form = document.getElementById('adc_form');
        webserver.noise_form = document.getElementById('noise_form');
        YAHOO.util.Event.addListener(webserver.adc_form, 'submit', webserver.adc_submit);
        webserver.adc_deb = document.getElementById('adc_deb');
        YAHOO.util.Event.addListener(webserver.adc_deb, 'submit', webserver.adc_deb_submit);
	
		YAHOO.util.Event.addListener("ccdclear", "click", webserver.ccdclear);
		YAHOO.util.Event.addListener("ccderase", "click", webserver.ccderase);
		YAHOO.util.Event.addListener("ccdepurge", "click", webserver.ccdepurge);
		
		webserver.barelement = document.getElementById("bar");
		webserver.barper = document.getElementById("percent");
		webserver.readoutcomp = 0;		// time readoutcomplete
		webserver.readstate = 0;
		
		YAHOO.util.Event.addListener("idle", "click", webserver.idlemode);
		YAHOO.util.Event.addListener("nomode", "click", webserver.timnoimod);		//timerfunction noisemode
		YAHOO.util.Event.addListener("mfs_to_flash", "click", webserver.newdefaults);
		YAHOO.util.Event.addListener("reboot", "click", webserver.rebootsys);
},

 timing_submit: function(e) {
	/*alert('test');*/
        YAHOO.util.Event.preventDefault(e);
       	YAHOO.util.Connect.setForm(webserver.timing_form);
		webserver.timing_form.config.value = "???";
        YAHOO.util.Connect.asyncRequest('POST', '/cmd/timing', webserver.timing_callback);
    	 var result_fade_out = new YAHOO.util.Anim(webserver.timing_form.config,{opacity: { to: 0 }}, 0.25, YAHOO.util.Easing.easeOut);
        result_fade_out.animate();
   },

 timing_callback: {															
	success: function(o) {														
			 // Set up the animation on the results div.
	var result_fade_in = new YAHOO.util.Anim(webserver.timing_form.config, {opacity: { to: 1 } }, 0.25, YAHOO.util.Easing.easeIn);
	var strJSON = '{'+ o.responseText + '}';
	var objJSON = eval("(function(){return " + strJSON + ";})()");
	webserver.timing_form.config.value = objJSON.toggle;
	result_fade_in.animate();
    },
	   failure: function(o) {
                   alert('XHR request failed DATA: ' + o.statusText);
    },
    timeout: 10000
  },
   
 adc_deb_submit: function(e) {
	/*alert('test');*/
        YAHOO.util.Event.preventDefault(e);
       	YAHOO.util.Connect.setForm(webserver.adc_deb);
        YAHOO.util.Connect.asyncRequest('POST', '/cmd/ledxhr', webserver.adc_deb_callback);
   },

 adc_deb_callback: {															
	success: function(o) {														
    },
	   failure: function(o) {
                   alert('XHR request failed DATA: ' + o.statusText);
    },
    timeout: 10000
  },


 adc_submit: function(e) {
    YAHOO.util.Event.preventDefault(e);
    YAHOO.util.Connect.setForm(webserver.adc_form);
    YAHOO.util.Connect.asyncRequest('POST', '/cmd/adcxhr');
	webserver.adc_form.reply.value = "exposing";
	setTimeout(webserver.expose_done,webserver.timing_form.exptim.value);
},
		
 expose_done:function(){
	webserver.adc_form.reply.value = "reading";
	webserver.readstate = 0;
	var delays = 1*webserver.timing_form.dlya.value + 1*webserver.timing_form.dlyb.value + 1*webserver.timing_form.dlyc.value + 1*webserver.timing_form.dlyd.value;  
	delays = delays + 6*webserver.timing_form.dlye.value + 1*webserver.timing_form.dlyf.value + 1*webserver.timing_form.dlyg.value; 
	delays = 100000/delays;
	webserver.readoutcomp = (webserver.timing_form.pixelX.value * webserver.timing_form.pixelY.value)/(400*delays) ;
	webserver.barinterval= setInterval (function(){webserver.progressbar()}, webserver.readoutcomp);
	setTimeout(webserver.adc_done,webserver.readoutcomp*100);
},
   
 progressbar :function(){
	webserver.readstate = webserver.readstate + 1;
    webserver.barelement.style.width=webserver.readstate+'%';
	webserver.barper.innerHTML=webserver.readstate;

},

 adc_done: function(){
		clearInterval(webserver.barinterval);
        YAHOO.util.Connect.asyncRequest('POST', '/cmd/adcdon', webserver.adc_callback);
},

 adc_callback: {															
	success: function(o) {														
	var strJSON = '{'+ o.responseText + '}';
	var objJSON = eval("(function(){return " + strJSON + ";})()");
	webserver.adc_form.reply.value = objJSON.toggle;
   },
	failure: function(o) {
                   alert('CCD DATA wait: ' + o.statusText);
    },
    timeout: 100000
},

 ccdclear: function(e) {
    YAHOO.util.Event.preventDefault(e);
	YAHOO.util.Connect.asyncRequest('POST','/cmd/ccd1/clrcol/', webserver.adc_callback);
},

 ccderase: function(e) {
    YAHOO.util.Event.preventDefault(e);
	YAHOO.util.Connect.asyncRequest('POST', '/cmd/ccd2', webserver.adc_callback);
},

 ccdepurge: function(e) {
    YAHOO.util.Event.preventDefault(e);
	YAHOO.util.Connect.asyncRequest('POST', '/cmd/ccd3', webserver.adc_callback);
},
 idlemode: function(e) {
    YAHOO.util.Event.preventDefault(e);
	YAHOO.util.Connect.asyncRequest('POST', '/cmd/idle', webserver.idle_callback);
},
 idle_callback: {															
	success: function(o) {														
	var strJSON = '{'+ o.responseText + '}';
	var objJSON = eval("(function(){return " + strJSON + ";})()");
	webserver.adc_form.idlestat.value = objJSON.toggle;
   },
	failure: function(o) {
                   alert('CCD DATA wait: ' + o.statusText);
    },
    timeout: 100000
},
 timnoimod: function(e) {
	if (webserver.noise_form.nomodestat.value == "Noisemode Off" ){
    webserver.livnoiinterval=setInterval(function(){webserver.noisemode()},1000);
//	webserver.noise_form.nomodestat.value = "Noisemode On" 
//	YAHOO.util.Connect.asyncRequest('POST', '/cmd/livnoi', webserver.noise_callback);
	}
	else{
	clearInterval(webserver.livnoiinterval);
	webserver.noise_form.nomodestat.value = "Noisemode Off";
	}
},
 noisemode: function() {
	YAHOO.util.Connect.asyncRequest('POST', '/cmd/livnoi', webserver.noise_callback);
},
 noise_callback: {															
	success: function(o) {														
	var strJSON = '{'+ o.responseText + '}';
	var objJSON = eval("(function(){return " + strJSON + ";})()");
	webserver.noise_form.nomodestat.value = objJSON.toggle;
	webserver.noise_form.noise01.value = (Math.sqrt(objJSON.noise01/16).toFixed(2));
	webserver.noise_form.noise02.value = (Math.sqrt(objJSON.noise02/16).toFixed(2));
	webserver.noise_form.noise03.value = (Math.sqrt(objJSON.noise03/16).toFixed(2));
	webserver.noise_form.noise04.value = (Math.sqrt(objJSON.noise04/16).toFixed(2));
   },
	failure: function(o) {
                   alert('CCD DATA wait: ' + o.statusText);
    },
    timeout: 100000
},
 newdefaults: function(e) {
    YAHOO.util.Event.preventDefault(e);
	if( window.confirm('Do you really want to set new default values? \n')){YAHOO.util.Connect.asyncRequest('POST','/cmd/sector', webserver.adc_deb_callback)}
},
 rebootsys: function(e) {
    YAHOO.util.Event.preventDefault(e);
	if( window.confirm('Do you really want to reboot the System? \n')){YAHOO.util.Connect.asyncRequest('POST','/cmd/reboot', webserver.adc_deb_callback)}
},
};

YAHOO.util.Event.addListener(window, 'load', webserver.init);

function popup(url) {
	newwindow = window.open(url, 'image', 'height=400,width=550,resizeable=1,scrollbards,menubar=0,toolbar=0');
	if (window.focus) {newwindow.focus()}
	return false;
}
