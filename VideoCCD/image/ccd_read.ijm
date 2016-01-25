// run single threaded to avoid collisions between the shell script and the macro 
run("Memory & Threads...", "maximum=2332 parallel=1 run"); 

// define the defaul directory of ImageJ
dir = "/home/user/SpectroCCD/Tools/VideoCCD/" 
call("ij.io.OpenDialog.setDefaultDirectory", dir); 

// copy default image to the working file
command = "cp " + dir + "image_UnShuf_welcome.fits" + " " + dir + "image/image_UnShuf.fits";
exec(command); 

// open the unshuffled image (welcome message)
open("image/image_UnShuf.fits"); 

// execute the read ADC script (send the DIR as an argument so that it can cd to that)
// command = dir + "ccd_read.sh" + " " + dir;
// exec(command); 


// make a rectangular area in the unshuffled image to use to set min and max of display (for contrast)
makeRectangle(100, 70, 1000, 500); 

// obtain values stats in the rectagle
getStatistics(area, mean, min, max, std); 

// set the Min and Max for the entire image so that the brightest is seen and the noise is used as bottom
setMinAndMax(mean-2*std, max);

// the following command changes the ratio of the pixel dimensions, but it does not work with revert trick to 
// open new imagein the same window
// run("Size...", "width=2496 height=22464 interpolation=None");

while (1<2) {
	// execute the read ADC script
	command = dir + "ccd_read.sh" + " " + dir;
	print(command);
	exec(command);
	// this does the trick, reopen the image, which has in the meantime been overwritten
	// but it does so in the same window and with the same zoom, etc 
	run("Revert");
	getStatistics(area, mean, min, max, std);
	setMinAndMax(mean-2*std, max);
	wait(1000);	
}
