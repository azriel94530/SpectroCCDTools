binning = 1;

close("background_fast.fits");
save_dir = "/home/user/SpectroCCD/Images/2016-06-17/background/";

// run single threaded to avoid collisions between the shell script and the macro 
run("Memory & Threads...", "maximum=2332 parallel=1 run"); 

// define the defaul directory of ImageJ
dir = "/home/user/SpectroCCD/Tools/VideoCCD/" 
call("ij.io.OpenDialog.setDefaultDirectory", dir); 

		// upload timing file that has a close shutter for idle
		command = dir + "ccd_upload_timing_file_close.sh" + " " + dir;
		print(command);
		exec(command);

		// execute set fast mode and sets Idle mode to ensure shutter is closed
		command = dir + "ccd_setup_fast_mode.sh" + " " + dir + " " + binning;
		print(command);
		exec(command);
		
		// execute read image (a poor mans clear) 
		command = dir + "ccd_read_raw_new.sh" + " " + dir;
		print(command);
		exec(command);

		// read another image
		command = dir + "ccd_read_raw_new.sh" + " " + dir;
		print(command);
		exec(command);


open("image.fits"); 
rename("background_fast.fits");

makeRectangle(512,492,426,456);
run("Enhance Contrast","saturated=0.35");

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

// put a copy in disk storage
print("Copy image to disk");
file_orig = "image_orig_"+TimeString+".fits";
command = "cp " + dir + "image.fits" + " " + save_dir + file_orig;
exec(command);

print("Move image to standard name");
// rename the working image file to standard name for background subtraction
command = "mv " + dir + "image.fits" + " " + dir + "background_fast.fits";
print(command);
exec(command);
print("Process image for display Only");
// flip horizontal quadrants
// selectWindow(xray_image);
ccd_width =  2496;
ccd_height = 620;
getDimensions(width, height, channels, slices, frames);
makeRectangle(0, height/2, width, height/2);
run("Flip Horizontally");

