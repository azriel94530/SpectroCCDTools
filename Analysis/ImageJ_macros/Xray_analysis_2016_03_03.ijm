run("Close All");

// get a background image (no x-rays)
root_dir =  "/home/user/SpectroCCD/";
images_dir = "Images/2016-03-02/";
background_image = "image_orig_D2016-03-02T17:29:27.fits";

background_file =  root_dir + images_dir + background_image;

print(background_file);

open(background_file);

// process background image
// average over to reduce the noise
run("32-bit");
run("Mean...", "radius=10");
makeRectangle(444, 474, 546, 492);
run("Enhance Contrast", "saturated=0.35");

// possible loop over x-ray images

// get x-ray image
xray_image = "image_orig_D2016-03-02T17:32:48.fits";
xray_file = root_dir + images_dir + xray_image;

open(xray_file);

// process xray image
run("32-bit");
makeRectangle(444, 474, 546, 492);
run("Enhance Contrast", "saturated=0.35");

// background subtract
imageCalculator("Subtract 32-bit", xray_image, background_image);
makeRectangle(444, 474, 546, 492);
run("Enhance Contrast", "saturated=0.35");

// remove residual flat field

// unshuffle
// get info from xray image
selectWindow(xray_image);
getDimensions(width, height, channels, slices, frames)
ccd_width =  2496;
ccd_height = 620;

// create output unshuffled image area
newImage("Unshuffling_top", "32-bit black", 1248, 620, 1);

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

// create output unshuffled image area
newImage("Unshuffling_bottom", "32-bit black", 1248, 620, 1);

// take bottom left image quadrant (no overscans) copy it to the new image
selectWindow(xray_image);
makeRectangle(0, height-ccd_height, ccd_width/4, ccd_height);
run("Flip Horizontally");
run("Copy");

selectWindow("Unshuffling_bottom");
makeRectangle(ccd_width/4, 0, ccd_width/4, ccd_height);
run("Paste");

// take bottom right image quadrant (no overscans) copy it to the new image
selectWindow(xray_image);
makeRectangle(width-ccd_width/4, height-ccd_height, ccd_width/4, ccd_height);
run("Flip Horizontally");
run("Copy");

selectWindow("Unshuffling_bottom");
makeRectangle(0, 0, ccd_width/4, ccd_height);
run("Paste");

// resize it so that each pixel now represents two pixels horizontally
run("Select All");
run("Size...", "width=2496 height=620 interpolation=None");

// show image background noise

// find and integrate x-rays

// show distributions for x-rays

// quantify S/N and RMS/sigma of xray energy peak
