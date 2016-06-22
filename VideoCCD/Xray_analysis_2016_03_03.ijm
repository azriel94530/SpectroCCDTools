run("Close All");
run("Memory & Threads...", "maximum=2332 parallel=1 run"); 

// get a background image (no x-rays)
do_background_subtraction = true;

if (do_background_subtraction) {
	root_dir =  "C:\\Users\\azriel\\Documents\\Work\\DetectorsENG\\SpectroCCD\\";
	images_dir = "Images\\2016-03-02\\";
	background_image = "image_orig_D2016-03-02T17_29_27.fits";
	background_file =  root_dir + images_dir + background_image;
	open(background_file);

	// process background image
	// average over to reduce the noise
	run("32-bit");
	run("Mean...", "radius=10");
	makeRectangle(444, 474, 546, 492);
	run("Enhance Contrast", "saturated=0.35");
}
// possible loop over x-ray images

// get x-ray image
xray_image = "image_orig_D2016-03-02T17_32_48.fits";
xray_file = root_dir + images_dir + xray_image;

open(xray_file);

// process xray image
run("32-bit");
makeRectangle(444, 474, 546, 492);
run("Enhance Contrast", "saturated=0.35");

if (do_background_subtraction) {
	// background subtract
	imageCalculator("Subtract 32-bit", xray_image, background_image);
	makeRectangle(444, 474, 546, 492);
	run("Enhance Contrast", "saturated=0.35");

// remove residual flat field
	run("Select All");
	// get the median and the sigma and plot histogram with those limits
	run("Set Measurements...", "standard median");
	run("Measure");
	List.setMeasurements();
	median = List.getValue("Median");
	stdv =  List.getValue("StdDev");
	run("Histogram", "bins=256 x_min="+(median-100)+" x_max="+(median+100)+" y_max=Auto");
	close();
	// this median is not perfect, it would be best to threshold or zoom in to get the statistics...
	selectWindow(xray_image);
	run("Subtract...", "value="+median);
}

// unshuffle
// get info from xray image
selectWindow(xray_image);
getDimensions(width, height, channels, slices, frames);
ccd_width =  2496;
ccd_height = 620;

// create mask/s for unshuffling 
newImage("Mask1", "32-bit black", ccd_width, ccd_height, 1);
run("Macro...", "code=[v=x%2]");
newImage("Mask2", "32-bit black", ccd_width, ccd_height, 1);
run("Macro...", "code=[v=1-(x%2)]");

// create output unshuffled image area
pixel_shift = 1;
newImage("Unshuffled", "32-bit black", ccd_width, ccd_height, 1);
newImage("Unshuffling_top", "32-bit black", ccd_width/2, ccd_height, 1);
// the bottom one is made intentionally one pixel taller, because we will need to move it up by removing the top row
newImage("Unshuffling_bottom", "32-bit black", ccd_width/2, ccd_height+pixel_shift, 1);

// take upper left image quadrant (no overscans) copy it to the new image
selectWindow(xray_image);
makeRectangle(0, 0, ccd_width/4, ccd_height);
run("Copy");

selectWindow("Unshuffling_top");
makeRectangle(0, 0, ccd_width/4, ccd_height);
run("Paste");

// take upper right image quadrant (no overscans) copy it to the new image
selectWindow(xray_image);
makeRectangle(width-ccd_width/4, 0, ccd_width/4, ccd_height);
run("Copy");

selectWindow("Unshuffling_top");
makeRectangle(ccd_width/4, 0, ccd_width/4, ccd_height);
run("Paste");

// resize it so that each pixel now represents two pixels horizontally
run("Select All");
run("Size...", "width=2496 height=620 interpolation=None");

// now repeat steps for the bottom regions with additional horizontal flips
// and switching the locations of the bottom lefft and bottom right

// take bottom right image quadrant (no overscans) copy it to the new image
selectWindow(xray_image);
makeRectangle(width-ccd_width/4, height-ccd_height, ccd_width/4, ccd_height);
run("Flip Horizontally");
run("Copy");

selectWindow("Unshuffling_bottom");
// the pixel_shift in the y is to be able to move the image one pixel down by removing the bottom row
makeRectangle(0, pixel_shift, ccd_width/4, ccd_height);
run("Paste");

// take bottom left image quadrant (no overscans) copy it to the new image
selectWindow(xray_image);
makeRectangle(0, height-ccd_height, ccd_width/4, ccd_height);
run("Flip Horizontally");
run("Copy");

selectWindow("Unshuffling_bottom");
makeRectangle(ccd_width/4, pixel_shift, ccd_width/4, ccd_height);
run("Paste");

// resize it so that each pixel now represents two pixels horizontally
run("Select All");
// +pixel_shift because we will need to crop the top
run("Size...", "width="+ccd_width+" height="+(ccd_height+pixel_shift)+" interpolation=None");
makeRectangle(0, 0, ccd_width, ccd_height);
run("Crop","");

// merge top and bottom using the mask/s
imageCalculator("Multiply 32-bit", "Unshuffling_top", "Mask1");
imageCalculator("Multiply 32-bit", "Unshuffling_bottom", "Mask2");
imageCalculator("Add 32-bit", "Unshuffling_top", "Unshuffling_bottom");
imageCalculator("Add 32-bit", "Unshuffled", "Unshuffling_top");
close("Unshuffling_top");
close("Unshuffling_bottom");
close("Mask1");
close("Mask2");

// show image background noise
// get the median and the sigma and plot histogram with those limits
selectWindow("Unshuffled");
run("Select All");
run("Set Measurements...", "standard median");
run("Measure");
List.setMeasurements();
median = List.getValue("Median");
stdv =  List.getValue("StdDev");
run("Histogram", "bins=256 x_min="+(median-10)+" x_max="+(median+10)+" y_max=Auto");

// find and integrate x-rays

selectWindow("Unshuffled");
// integrate in a circle
radius_integration = 3;
run("Mean...", "radius="+radius_integration);

// get the number of pixels in the chosen radius -mask-
newImage("Radius", "32-bit black", 10, 10, 1);
makeRectangle(5, 5, 1, 1);
run("Set...", "value=1");
run("Select All");
run("Mean...", "radius=3");
pixels_integration = 1/getPixel(5,5);
close();

// find the maxima
selectWindow("Unshuffled");
run("Select All");
run("Find Maxima...", "noise=2 output=[Single Points] exclude");
rename("Maxima");
// 
run("32-bit");
imageCalculator("Multiply 32-bit", "Maxima", "Unshuffled");
selectWindow("Maxima");
run("Multiply...", "value="+(pixels_integration/255.0));
run("Histogram", "bins=256 x_min=1 x_max=2000 y_max=Auto");
selectWindow("Maxima");
run("Histogram", "bins=256 x_min=500 x_max=800 y_max=Auto");


// show distributions for x-rays

// quantify S/N and RMS/sigma of xray energy peak
