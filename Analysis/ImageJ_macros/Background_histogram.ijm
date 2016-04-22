run("32-bit");
// get the median and the sigma and plothitogram with those limits
run("Set Measurements...", "standard median");
run("Measure");
List.setMeasurements();
median = List.getValue("Median");
stdv =  List.getValue("StdDev");
run("Histogram", "bins=256 x_min="+(median-3*stdv)+" x_max="+(median+3*stdv)+" y_max=Auto");
