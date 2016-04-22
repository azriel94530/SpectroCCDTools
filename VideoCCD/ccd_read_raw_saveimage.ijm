// run single threaded to avoid collisions between the shell script and the macro 
run("Memory & Threads...", "maximum=2332 parallel=1 run"); 

// define the defaul directory of ImageJ
dir = "/home/user/SpectroCCD/Tools/VideoCCD/" 
call("ij.io.OpenDialog.setDefaultDirectory", dir); 

// copy default image to the working file
// command = "cp " + dir + "image_UnShuf_welcome.fits" + " " + dir + "image/image_UnShuf.fits";
// exec(command); 

// open the unshuffled image (welcome message)
// open("image/image_UnShuf.fits"); 

// execute the read ADC script (send the DIR as an argument so that it can cd to that)
// command = dir + "ccd_read.sh" + " " + dir;
// exec(command); 


// make a rectangular area in the unshuffled image to use to set min and max of display (for contrast)
// makeRectangle(100, 70, 1000, 500); 

// obtain values stats in the rectagle
// getStatistics(area, mean, min, max, std); 

// set the Min and Max for the entire image so that the brightest is seen and the noise is used as bottom
// setMinAndMax(mean-2*std, max);

// the following command changes the ratio of the pixel dimensions, but it does not work with revert trick to 
// open new imagein the same window
// run("Size...", "width=2496 height=22464 interpolation=None");

command = dir + "ccd_read_raw.sh" + " " + dir;
print(command);
exec(command);

wait(1000);
open("image.fits"); 

makeRectangle(512,492,426,456);
run("Enhance Contrast","saturated=0.35");
num = 1000;
skip_save = 50

while (num>0) {
	// execute the read ADC script
	command = dir + "ccd_read_raw.sh" + " " + dir;
	print(command);
	exec(command);
	// this does the trick, reopen the image, which has in the meantime been overwritten
	// but it does so in the same window and with the same zoom, etc 
	selectWindow("image.fits");
	run("Revert");
	run("Enhance Contrast","saturated=0.35");
//	getStatistics(area, mean, min, max, std);
//	setMinAndMax(mean-2*std, max);
// save files original and unshuffled
	getDateAndTime(year, month, dayOfWeek, dayOfMonth, hour, minute, second, msec);
	TimeString ="D"+year+"-";
	if (month<10) {TimeString = TimeString+"0";}
	TimeString = TimeString+(month+1)+"-";
     	if (dayOfMonth<10) {TimeString = TimeString+"0";}
     	TimeString = TimeString+dayOfMonth+"T";
     	if (hour<10) {TimeString = TimeString+"0";}
     	TimeString = TimeString+hour+":";
     	if (minute<10) {TimeString = TimeString+"0";}
     	TimeString = TimeString+minute+":";
     	if (second<10) {TimeString = TimeString+"0";}
     	TimeString = TimeString+second;

	file_orig = "image_orig_"+TimeString+".fits";
	if ( ( num % skip_save ) == 0 ) {
		command = "cp " + dir + "image.fits" + " " + "/home/user/SpectroCCD/Images/2016-04-07/" + file_orig;
		exec(command);
	}
	wait(0*60*1000);
	num--;	
}
