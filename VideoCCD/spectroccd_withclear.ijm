save_dir = "/home/user/SpectroCCD/Images/2016-04-29/";
// get a background image (no x-rays)
do_background_subtraction = true;
do_gains = false;
do_unshuffle = true;
exposure_minutes = 30.; // in continuos mode operation the exposure is controlled by two settings
	              // the DLY1 field in the controllers CCD timing web page and this
	              // exposure_minutes variable.
	              // DLY1 of 14,000 is an exposure of 23 seconds (field can be set from 0-16,383)
	              // the readout time is about 14 seconds so without a shutter short exposures
	              // will suffer from the readout band background (due to the angle between the
	              // columns and the spectrometer horizontal plane.
	              // the exposure_minutes is an additional exposure time (im minutes units) on top of the 
	              // DLY1 exposure
	              // From the experience 
exposure_minutes = getNumber("Enter exposure time in minutes", exposure_minutes );

rotation_angle = -0.65; // the true angle in degrees missaligment between x axis of spectrometer 
	          // and the columns of the ccd
show_profile_processed = true;
show_profile_unshuffled = do_unshuffle && true;

pixel_length = 45.;
pixel_width = 5.;
do_fake_image = false;

run("Close All");
setBatchMode(true);

// assumed that background image is the same as the flat_light image
background_image = "background.fits";
ccd_width =  2496;
ccd_height = 620;

// create mask/s for unshuffling 
newImage("Mask1", "32-bit black", ccd_width, ccd_height, 1);
// shrink size of window
unzoom25(); 
run("Macro...", "code=[v=x%2]");

newImage("Mask2", "32-bit black", ccd_width, ccd_height, 1);
run("Macro...", "code=[v=1-(x%2)]");
unzoom25(); 

// if the background has a lot of pattern (like columns high) set to false and do not do avergaging (at the expense of sqrt(2) of noise)
average_background = false;
limit_image_area = false;

// run single threaded to avoid collisions between the shell script and the macro 
run("Memory & Threads...", "maximum=2332 parallel=1 run"); 

// define the defaul directory of ImageJ
dir = "/home/user/SpectroCCD/Tools/VideoCCD/"; 
call("ij.io.OpenDialog.setDefaultDirectory", dir); 

Gain_TL =  1.;
Gain_TR =  1.;
Gain_BL =  1.;
Gain_BR =  1.;

height = 1;
width =1;

num = 1;

if ( do_unshuffle ) {
	// create output unshuffled image area and apply relative gains
	newImage("Unshuffled", "32-bit black", ccd_width, ccd_height, 1);
}



for (i = 0; i<num; i++) {
	
	if ( do_fake_image ) {
		// will use whatever image.fits in the directory
		wait(0);
	} else {
		// execute the read ADC script
		command = dir + "ccd_read_raw_withclr.sh" + " " + dir + " " + exposure_minutes;
		print(command);
		exec(command);
	}

	

	// this does the trick, reopen the image, which has in the meantime been overwritten
	// but it does so in the same window and with the same zoom, etc
	if (i == 0) {
		open("image.fits"); 
		// create a processed image
		newImage("image_processed.fits", "32-bit black", ccd_width/2, ccd_height*2, 1);
		selectWindow("image.fits");	
		
		getDimensions(width, height, channels, slices, frames);

		// open background image or create a blank
		if (do_background_subtraction) {
			background_file =  background_image;
 			open(background_file);
		} else {
			// create a blank background image
			newImage(background_image, "32-bit black", width, height, 1);
		}    
		// create also the background image that does not have the overscans
		// and that has the flip of the bottom half

		makeRectangle(0, height/2, width, height/2);
		run("Flip Horizontally");
		newImage("background_processed.fits", "32-bit black", ccd_width/2, ccd_height*2, 1);
		
		//TL
		selectWindow(background_image);
		makeRectangle(0, 0, ccd_width/4, ccd_height);
		run("Copy");
		selectWindow("background_processed.fits");
		makeRectangle(0, 0, ccd_width/4, ccd_height);
		run("Paste");

		//TR
		selectWindow(background_image);
		makeRectangle(width-ccd_width/4, 0, ccd_width/4, ccd_height);
		run("Copy");
		selectWindow("background_processed.fits");
		makeRectangle(ccd_width/4, 0, ccd_width/4, ccd_height);
		run("Paste");

		//BL
		selectWindow(background_image);
		makeRectangle(0,height-ccd_height, ccd_width/4, ccd_height);
		run("Copy");
		selectWindow("background_processed.fits");
		makeRectangle(0, ccd_height, ccd_width/4, ccd_height);
		run("Paste");

		//BR
		selectWindow(background_image);
		makeRectangle(width-ccd_width/4, height-ccd_height, ccd_width/4, ccd_height);
		run("Copy");
		selectWindow("background_processed.fits");
		makeRectangle(ccd_width/4, ccd_height, ccd_width/4, ccd_height);
		run("Paste");
		unzoom25();

		if (do_gains ) {
			selectWindow(background_image);
			run("Set Measurements...", "mean");	

			run("Enhance Contrast", "saturated=0.35");

			box_center = 100;
			makeRectangle(ccd_width/4, ccd_height/2, (width-ccd_width/2)/2, ccd_height/2);
			run("Measure");
			List.setMeasurements();
			TL_hovsc = List.getValue("Mean");
			makeRectangle(ccd_width/4-box_center, ccd_height-box_center, box_center, box_center);
			run("Measure");
			List.setMeasurements();
			TL_flat = List.getValue("Mean");
			Gain_TL = TL_flat-TL_hovsc;


			makeRectangle(width/2, ccd_height/2, (width-ccd_width/2)/2, ccd_height/2);
			run("Measure");
			List.setMeasurements();
			TR_hovsc = List.getValue("Mean");
			makeRectangle(width-ccd_width/4, ccd_height-box_center, box_center, box_center);
			run("Measure");
			List.setMeasurements();
			TR_flat = List.getValue("Mean");
			Gain_TR = TR_flat-TR_hovsc;
	
			makeRectangle(ccd_width/4, height-ccd_height, (width-ccd_width/2)/2, ccd_height/2);
			run("Measure");
			List.setMeasurements();
			BL_hovsc = List.getValue("Mean");
			makeRectangle(ccd_width/4-box_center, height-ccd_height, box_center, box_center);
			run("Measure");
			List.setMeasurements();
			BL_flat = List.getValue("Mean");
			Gain_BL = BL_flat-BL_hovsc;

			makeRectangle(width/2, height-ccd_height, (width-ccd_width/2)/2, ccd_height/2);
			run("Measure");
			List.setMeasurements();
			BR_hovsc = List.getValue("Mean");	
			makeRectangle(width-ccd_width/4, height-ccd_height, box_center, box_center);
			run("Measure");
			List.setMeasurements();
			BR_flat = List.getValue("Mean");
			Gain_BR = BR_flat-BR_hovsc;

			close();
 		} // end of if do_gains

		print("Gains " + Gain_TL + " " + Gain_TR + " " + Gain_BL + " " + Gain_BR );

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
		
		command = "cp " + dir + "image.fits" + " " + save_dir + file_orig;
		exec(command);

	} else {
		// store the selected region on the processed image for the spectrum/profile
		selectWindow("image_processed.fits");
		if ( selectionType() != -1) { 
			Roi.getBounds(x_rect, y_rect, width_rect, height_rect);
		} else {
			makeRectangle(10, 10, 1200, 600);
			Roi.getBounds(x_rect, y_rect, width_rect, height_rect);
		}
		selectWindow("Unshuffled");
		if ( selectionType() != -1) { 
			Roi.getBounds(x_rect_unsh, y_rect_unsh, width_rect_unsh, height_rect_unsh);
		} else {
			makeRectangle(10, 10, 2400, 590);
			Roi.getBounds(x_rect_unsh, y_rect_unsh, width_rect_unsh, height_rect_unsh);
		}


		selectWindow("image.fits");
		run("Revert");
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
		
		command = "cp " + dir + "image.fits" + " " + save_dir + file_orig;
		exec(command);	

	}
	// assemble the processed image 
	
	// show the raw image just taken with ONLY the horizontal bottom flip
	selectWindow("image.fits");
	makeRectangle(0, height/2, width, height/2);
	run("Flip Horizontally");
	makeRectangle(width/4, height/4, width/2, height/2);
	run("Enhance Contrast","saturated=0.35");
	setBatchMode("show");

	// duplicate and rename to hide from wide further usage of image.fits
	selectWindow("image.fits");
	run("Select None"); 
	run("Duplicate...","title=temp");

	//TL
	selectWindow("temp");
	makeRectangle(0, 0, ccd_width/4, ccd_height);
	run("Copy");
	selectWindow("image_processed.fits");
	makeRectangle(0, 0, ccd_width/4, ccd_height);
	run("Paste");

	//TR
	selectWindow("temp");
	makeRectangle(width-ccd_width/4, 0, ccd_width/4, ccd_height);
	run("Copy");
	selectWindow("image_processed.fits");
	makeRectangle(ccd_width/4, 0, ccd_width/4, ccd_height);
	run("Paste");

	//BL
	selectWindow("temp");
	makeRectangle(0,height-ccd_height, ccd_width/4, ccd_height);
	run("Copy");
	selectWindow("image_processed.fits");
	makeRectangle(0, ccd_height, ccd_width/4, ccd_height);
	run("Paste");

	//BR
	selectWindow("temp");
	makeRectangle(width-ccd_width/4, height-ccd_height, ccd_width/4, ccd_height);
	run("Copy");
	selectWindow("image_processed.fits");
	makeRectangle(ccd_width/4, ccd_height, ccd_width/4, ccd_height);
	run("Paste");

	close("temp");

	// background subtract

	imageCalculator("Subtract 32-bit", "image_processed.fits", "background_processed.fits");
	makeRectangle(444, 474, 546, 492);
	run("Enhance Contrast", "saturated=0.35");

	// make unshuffled image if requested
	if ( do_unshuffle ) {
		selectWindow("Unshuffled");
		setMinAndMax(0.0, 1e20);
		run("Select All");
		run("Clear", "slice");
		// create processing imagings for Unshuffling
		newImage("Unshuffling_top", "32-bit black", ccd_width/2, ccd_height, 1);
		newImage("Unshuffling_bottom", "32-bit black", ccd_width/2, ccd_height, 1);

		// take upper left image quadrant (no overscans) copy it to the new image
		selectWindow("image_processed.fits");
		makeRectangle(0, 0, ccd_width/4, ccd_height);
		run("Copy");

		selectWindow("Unshuffling_top");
		makeRectangle(0, 0, ccd_width/4, ccd_height);
		run("Paste");
		run("Multiply...", "value="+Gain_TL/Gain_TL);

		selectWindow("image_processed.fits");
		makeRectangle(ccd_width/4, 0, ccd_width/4, ccd_height);
		run("Copy");

		selectWindow("Unshuffling_top");
		makeRectangle(ccd_width/4, 0, ccd_width/4, ccd_height);
		run("Paste");
		run("Multiply...", "value="+Gain_TL/Gain_TR);

		// resize it so that each pixel now represents two pixels horizontally
		run("Select All");
		run("Size...", "width="+ccd_width+" height="+ccd_height+" interpolation=None");

		// now repeat steps for the bottom regions (already flipped)

		selectWindow("image_processed.fits");
		makeRectangle(0, ccd_height, ccd_width/4, ccd_height);
		run("Copy");

		selectWindow("Unshuffling_bottom");
		// the pixel_shift in the y is to be able to move the image one pixel down by removing the bottom row
		makeRectangle(0, 0, ccd_width/4, ccd_height);
		run("Paste");
		run("Multiply...", "value="+Gain_TL/Gain_BR);

		selectWindow("image_processed.fits");
		makeRectangle(ccd_width/4, ccd_height, ccd_width/4, ccd_height);
		run("Copy");

		selectWindow("Unshuffling_bottom");
		makeRectangle(ccd_width/4, 0, ccd_width/4, ccd_height);
		run("Paste");
		run("Multiply...", "value="+Gain_TL/Gain_BL);

		// resize it so that each pixel now represents two pixels horizontally
		run("Select All");
		run("Size...", "width="+ccd_width+" height="+(ccd_height)+" interpolation=None");
		makeRectangle(0, 0, ccd_width, ccd_height);

		// merge top and bottom using the mask/s
		imageCalculator("Multiply 32-bit", "Unshuffling_top", "Mask1");
		imageCalculator("Multiply 32-bit", "Unshuffling_bottom", "Mask2");
		imageCalculator("Add 32-bit", "Unshuffling_top", "Unshuffling_bottom");
		imageCalculator("Add 32-bit", "Unshuffled", "Unshuffling_top");
		selectWindow("Unshuffled");
		makeRectangle(ccd_width/4, ccd_height/4, ccd_width/2, ccd_height/2);
		run("Enhance Contrast", "saturated=0.35");
		if (rotation_angle != 0.) {
			run("Select All");
			run("Rotate... ", "angle="+(rotation_angle*pixel_length/pixel_width)+" grid=1 interpolation=Bilinear");	
		}
		saveAs("Tiff", save_dir + "us_" + TimeString + ".tif");

		setBatchMode("show");
	
		// make a profile plot of the image (to ge a spectrum
	
		if (i==0) {
			// a default image area to produce the profile
			makeRectangle(10, 10, 2400, 590);
		} else {
			makeRectangle(x_rect_unsh, y_rect_unsh, width_rect_unsh, height_rect_unsh);
	
		}
	
		if (i == 0) {
			run("Profile Plot Options...", "width=2500 height=200 minimum=0 maximum=0 interpolate draw");
			run("Plot Profile");
			saveAs("Tiff", dir+"spectrum_unshuffled.tiff");	
		} else  {
			run("Plot Profile");
			saveAs("Tiff", dir+"spectrum_unshuffled.tiff");
			// move aside to go back to our original profile and update it
			rename("junk");
			selectWindow("spectrum_unshuffled.tiff");
			run("Revert");
		}
		if ( show_profile_unshuffled) {
			setBatchMode("show");
		}
		close("Unshuffling_top");
		close("Unshuffling_bottom");

	}

	// rotation
	selectWindow("image_processed.fits");

	if (rotation_angle != 0.) {
		run("Select All");
		// the factor of 2 inthe width is because this image is still every second column
		run("Rotate... ", "angle="+(rotation_angle*pixel_length/(2*pixel_width))+" grid=1 interpolation=None");	
	}
	// make the processed image visible
	setBatchMode("show");
	
	// make a profile plot of the image (to ge a spectrum
	
	if (i==0) {
		// a default image area to produce the profile
		makeRectangle(10, 10, 1200, 600);
	} else {
		makeRectangle(x_rect, y_rect, width_rect, height_rect);
		print("rectangle",x_rect, y_rect, width_rect, height_rect);
	
	}
	
	if (i == 0) {
		run("Profile Plot Options...", "width=1500 height=200 minimum=0 maximum=0 interpolate draw");
		run("Plot Profile");
		saveAs("Tiff", dir+"spectrum.tiff");	
	} else  {
		run("Plot Profile");
		saveAs("Tiff", dir+"spectrum.tiff");
		// move aside to go back to our original profile and update it
		rename("junk");
		selectWindow("spectrum.tiff");
		run("Revert");
	}
	if ( show_profile_processed) {
		setBatchMode("show");
	}
	wait(exposure_minutes*60*1000);
}


function unzoom25 (){ 
i=1; 
do{ 
run("Out"); 
i++; 
}while(i<5); 
} 
