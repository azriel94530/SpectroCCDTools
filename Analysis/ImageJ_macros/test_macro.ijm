input = "/Users/azrielgoldschmidt/LBNL/Work/detectorsENG/SpectroCCD/DAQ/network";
print(input);

list = getFileList(input);

print("Full list length: ",list.length);
run("Set Measurements...", "area mean standard min bounding limit display nan redirect=None decimal=3");

for (i=0; i < list.length; i++) {
	if (endsWith(list[i],".fits") && startsWith(list[i],"image_orig")) {
		print(list[i]);
		this_image = list[i];
		open(this_image);
		
		// upper left signal
		makeRectangle(522, 138, 250, 250);
		run("Measure");
		// vertical overscan (make a horizontal band)
		makeRectangle(588, 654, 250, 50);
		run("Measure");
		
		// upper right
		makeRectangle(33, 123, 250, 250);
		run("Measure");
		// vertical overscan
		makeRectangle(51, 642, 250, 50);
		run("Measure");
		
		// bottom left
		makeRectangle(546, 903, 250, 250);
		run("Measure");
		// vertical overscan
		makeRectangle(570, 729, 250, 50);
		run("Measure");
		
		// bottom right
		makeRectangle(33, 867, 250, 250);
		run("Measure");
		makeRectangle(42, 726, 250, 50);
		run("Measure");
		setThreshold(-20000, 30000, "raw");
		run("Measure");
		//
		
	}
}


