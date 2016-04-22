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
size_area = 400;

// convert image to 32 bit to be able to threshold
//run("32-bit");

function test(bx,by,sx,sy) {
open("/home/user/SpectroCCD/Images/2016-02-09/image_orig_D2016-01-10T13:58:19.fits");
run("32-bit");

// obtain image background level (use median of region or the fancier method) 
makeRectangle(bx,by,sx,sy);

run("Set Measurements...", "standard median");
run("Measure");

List.setMeasurements();
median = List.getValue("Median");
stdv =  List.getValue("StdDev");
print(median+2*stdv);

run("Subtract...", "value=median");

setThreshold(3*stdv, 1e20);

run("Set Measurements...", "area center bounding integrated redirect=None decimal=3");

run("Analyze Particles...", "size=0-9 display clear summarize");

run("Distribution...", "parameter=RawIntDen or=20 and=0-3000");
}

test(sizex/2+oversc_h/2,sizey/2-oversc_v/2-size_area, size_area,size_area);
test(sizex/2-oversc_h/2-size_area,sizey/2-oversc_v/2-size_area, size_area,size_area);
