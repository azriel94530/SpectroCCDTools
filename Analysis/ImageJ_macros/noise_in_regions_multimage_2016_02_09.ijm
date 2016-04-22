input = "/home/user/SpectroCCD/Images/2016-02-09/";
print(input);

list = getFileList(input);

print("Full list length: ",list.length);
run("Set Measurements...", "area mean standard min bounding median limit display nan redirect=None decimal=3");

// the pixel counts in the taken image (should be obtained from the images, or the first one)
sizex = 1448;
sizey = 1440;
// the pixel counts in the actual ccd
sizeccdx = 2496;
sizeccdy = 620;
// offset in x in the image due to header issue, no longer
offset_x = 0;
// stay clear length
stay_clear = 20;
// calculate the overscan areas sizes
oversc_h = sizex - sizeccdx/2;
oversc_v = sizey - sizeccdy*2;
// set the size of the area to use for averages means 
size_area = 250;

setBatchMode(true); 

for (i=0; i < list.length; i++) {
	if (endsWith(list[i],".fits") && startsWith(list[i],"image_orig")) {
		print(list[i]);
		this_image = list[i];
		open(input + this_image);

		// convert to 32-bit float for threshold operations on measurements
		run("32-bit");	
		
		// upper left signal
		makeRectangle(sizex/2-oversc_h/2-stay_clear-size_area+1,
			      sizey/2-oversc_v/2-stay_clear-size_area+1, 
			      size_area, size_area);
		run("Measure");
		// attempt to remove xray tail
		getStatistics(area, mean, min, max, std);
		setThreshold(mean-3*std, mean+3*std);
		// run("Measure");
		mean1 = getResult("Mean");
		std1 = getResult("StdDev");
		setThreshold(mean1-3*std1, mean1+3*std1);
		run("Measure");
		run("Revert"); // to get back to an unthresholded image
		// vertical overscan (make a horizontal band)
		makeRectangle(sizex/2-oversc_h/2-stay_clear-size_area+1,
			      sizey/2-oversc_v/2+1, 
			      size_area, oversc_v/2);
		run("Measure");
		// horizontal overscan (make vertical band)
		makeRectangle(sizex/2-oversc_h/2+1,
			      sizey/2-oversc_v/2-stay_clear-size_area+1, 
			      oversc_h/2, size_area);
		run("Measure");
		
		// upper right
		makeRectangle(sizex/2+oversc_h/2+stay_clear+1,
			      sizey/2-oversc_v/2-stay_clear-size_area+1, 
			      size_area, size_area);
		run("Measure");
		// attempt to remove xray tail
		getStatistics(area, mean, min, max, std);
		setThreshold(mean-3*std, mean+3*std);
		//run("Measure");
		mean1 = getResult("Mean");
		std1 = getResult("StdDev");
		setThreshold(mean1-3*std1, mean1+3*std1);
		run("Measure");
		run("Revert"); // to get back to an unthresholded image
		// vertical overscan
		makeRectangle(sizex/2+oversc_h/2+stay_clear+1,
			      sizey/2-oversc_v/2+1, 
			      size_area, oversc_v/2);
		run("Measure");
		// horizontal overscan
		makeRectangle(sizex/2+1,
			      sizey/2-oversc_v/2-stay_clear-size_area+1, 
			      oversc_h/2, size_area);
		run("Measure");


		// bottom left
		makeRectangle(sizex/2-oversc_h/2-stay_clear-size_area+1,
			      sizey/2+oversc_v/2+stay_clear+1, 
			      size_area, size_area);
		// attempt to remove xray tail
		run("Measure");
		getStatistics(area, mean, min, max, std);
		setThreshold(mean-3*std, mean+3*std);
		//run("Measure");
		mean1 = getResult("Mean");
		std1 = getResult("StdDev");
		setThreshold(mean1-3*std1, mean1+3*std1);
		run("Measure");
		run("Revert"); // to get back to an unthresholded image
		// vertical overscan
		makeRectangle(sizex/2-oversc_h/2-stay_clear-size_area+1,
			      sizey/2+1, 
			      size_area, oversc_v/2);
		run("Measure");
		// horizontal overscan
		makeRectangle(sizex/2-oversc_h/2+1,
			      sizey/2+oversc_v/2+stay_clear+1, 
			      oversc_h/2, size_area);
		run("Measure");

		// bottom right
		makeRectangle(sizex/2+oversc_h/2+stay_clear+1,
			      sizey/2+oversc_v/2+stay_clear+1, 
			      size_area, size_area);
		run("Measure");
		// attempt to remove xray tail
		getStatistics(area, mean, min, max, std);
		setThreshold(mean-3*std, mean+3*std);
		// run("Measure");
		mean1 = getResult("Mean");
		std1 = getResult("StdDev");
		setThreshold(mean1-3*std1, mean1+3*std1);
		run("Measure");
		run("Revert"); // to get back to an unthresholded image
		// vertical overscan
		makeRectangle(sizex/2+oversc_h/2+stay_clear+1,
			      sizey/2+1, 
			      size_area, oversc_v/2);
		run("Measure");
		// horizontal overscan
		makeRectangle(sizex/2+1,
			      sizey/2+oversc_v/2+stay_clear+1, 
			      oversc_h/2, size_area);
		run("Measure");

		close();
		
	}
}

setBatchMode("exit & display"); 
