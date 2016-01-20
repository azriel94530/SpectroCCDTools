run("Memory & Threads...", "maximum=2332 parallel=1 run");
exec("cp /home/user/SpectroCCD/sandbox_azriel/image/image_UnShuf_welcome.fits /home/user/SpectroCCD/sandbox_azriel/image/image_UnShuf.fits");
// exec("/home/user/SpectroCCD/sandbox_azriel/ccd_read.sh");
open("/home/user/SpectroCCD/sandbox_azriel/image/image_UnShuf.fits");
makeRectangle(100, 70, 1000, 500);
getStatistics(area, mean, min, max, std);
setMinAndMax(mean-2*std, max);

// the following command changes the ratio of the pixel dimensions, but 
// run("Size...", "width=2496 height=22464 interpolation=None");

for (i=1;i<10000000;i++) {
    exec("/home/user/SpectroCCD/sandbox_azriel/ccd_read.sh");
    run("Revert");
    getStatistics(area, mean, min, max, std);
    setMinAndMax(mean-2*std, max);
    wait(1000);	
}
