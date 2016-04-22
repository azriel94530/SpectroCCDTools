input = "/home/user/SpectroCCD/Images/2016-01-22/";
print(input);

list = getFileList(input);

print("Full list length: ",list.length);
run("Set Measurements...", "area mean standard min bounding limit display nan redirect=None decimal=3");

// the pixel counts in the taken image (should be obtained from the images, or the first one)
sizex = 1448;
sizey = 1440;
// the pixel counts in the actual ccd
sizeccdx = 2496;
sizeccdy = 620;
// offset in x in the image due to header issue
offset_x = -396;

// to do: convert absolute postions from above parameters
setBatchMode(true); 

for (i=0; i < list.length; i++) {
	if (endsWith(list[i],".fits") && startsWith(list[i],"image_orig")) {
		print(list[i]);
		this_image = list[i];
		open(input + this_image);

		// convert to 32-bit float for threshold operations on measurements
		run("32-bit");	
		
		// upper left signal
		makeRectangle(500, 100, 250, 250);
		// attempt to remove xray tail
		getStatistics(area, mean, min, max, std);
		setThreshold(mean-3*std, mean+3*std);
		run("Measure");
		mean1 = getResult("Mean");
		std1 = getResult("StdDev");
		setThreshold(mean1-3*std1, mean1+3*std1);
		run("Measure");
		run("Revert"); // to get back to an unthresholded image
		// vertical overscan (make a horizontal band)
		makeRectangle(500, 650, 250, 50);
		run("Measure");
		// horizontal overscan (make vertical band)
		makeRectangle(1050, 100, 50, 250);
		run("Measure");
		
		// upper right
		makeRectangle(30, 100, 250, 250);
		// attempt to remove xray tail
		getStatistics(area, mean, min, max, std);
		setThreshold(mean-3*std, mean+3*std);
		run("Measure");
		mean1 = getResult("Mean");
		std1 = getResult("StdDev");
		setThreshold(mean1-3*std1, mean1+3*std1);
		run("Measure");
		run("Revert"); // to get back to an unthresholded image
		// vertical overscan
		makeRectangle(30, 650, 250, 50);
		run("Measure");
		// horizontal overscan
		makeRectangle(1150, 100, 50, 250);
		run("Measure");


		// bottom left
		makeRectangle(500, 900, 250, 250);
		// attempt to remove xray tail
		getStatistics(area, mean, min, max, std);
		setThreshold(mean-3*std, mean+3*std);
		run("Measure");
		mean1 = getResult("Mean");
		std1 = getResult("StdDev");
		setThreshold(mean1-3*std1, mean1+3*std1);
		run("Measure");
		run("Revert"); // to get back to an unthresholded image
		// vertical overscan
		makeRectangle(500, 750, 250, 50);
		run("Measure");
		// horizontal overscan
		makeRectangle(1050, 900, 50, 250);		
		run("Measure");

		// bottom right
		makeRectangle(30, 900, 250, 250);
		// attempt to remove xray tail
		getStatistics(area, mean, min, max, std);
		setThreshold(mean-3*std, mean+3*std);
		run("Measure");
		mean1 = getResult("Mean");
		std1 = getResult("StdDev");
		setThreshold(mean1-3*std1, mean1+3*std1);
		run("Measure");
		run("Revert"); // to get back to an unthresholded image
		// vertical overscan
		makeRectangle(30, 750, 250, 50);
		run("Measure");
		// horizontal overscan
		makeRectangle(1150, 900, 50, 250);
		run("Measure");

		close();
		
	}
}

setBatchMode("exit & display"); 
