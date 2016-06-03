close("background.fits");
save_dir = "/home/user/SpectroCCD/Images/2016-04-29/background/";

// run single threaded to avoid collisions between the shell script and the macro 
run("Memory & Threads...", "maximum=2332 parallel=1 run"); 

// define the defaul directory of ImageJ
dir = "/home/user/SpectroCCD/Tools/VideoCCD/" 
call("ij.io.OpenDialog.setDefaultDirectory", dir); 

command = dir + "ccd_read_raw.sh" + " " + dir;
print(command);
exec(command);
print("Obtained first image, will read the next one as a most realistic Clear function");

// open("image.fits"); 
// rename("background.fits");

// makeRectangle(512,492,426,456);
// run("Enhance Contrast","saturated=0.35");

// getDateAndTime(year, month, dayOfWeek, dayOfMonth, hour, minute, second, msec);
// TimeString ="D"+year+"-";
// if (month<10) {TimeString = TimeString+"0";}
// TimeString = TimeString+(month+1)+"-";
// if (dayOfMonth<10) {TimeString = TimeString+"0";}
// TimeString = TimeString+dayOfMonth+"T";
// if (hour<10) {TimeString = TimeString+"0";}
// TimeString = TimeString+hour+":";
// if (minute<10) {TimeString = TimeString+"0";}
// TimeString = TimeString+minute+":";
// if (second<10) {TimeString = TimeString+"0";}
// TimeString = TimeString+second;

// put a copy in disk storage
// file_orig = "image_orig_"+TimeString+".fits";
// command = "cp " + dir + "image.fits" + " " + save_dir + file_orig;
// exec(command);
// rename the working image file to standard name for background subtraction
// command = "mv " + dir + "image.fits" + " " + dir + "background.fits";
// exec(command);

command = dir + "ccd_read_raw.sh" + " " + dir;
print(command);
exec(command);

// close first background image (with artificially long exposure)
// close("background.fits");

open("image.fits"); 
rename("background.fits");

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
command = "mv " + dir + "image.fits" + " " + dir + "background.fits";
exec(command);
print("Process image for display");
// flip horizontal quadrants
// selectWindow(xray_image);
ccd_width =  2496;
ccd_height = 620;
getDimensions(width, height, channels, slices, frames);
makeRectangle(0, height/2, width, height/2);
run("Flip Horizontally");

