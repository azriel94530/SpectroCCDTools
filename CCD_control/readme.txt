
PicVideo.X --> mplab x project directory (the project started in mplabx as we did not know of the issues with the pickit3, mplab just referenced those files)
xps --> project folder for the xilinx plattform studio contains the code for microblaze as well as the file system (sdk/sdk_export) 

building filesystem is bus dependant. for our axi based system (used in xilinx tools -> shell):
"mfsgen -cvbf image.mfs 512 css images js yui index.html clkboard.html image.fits fitsheader.txt timing.txt"	

In Chipscope you should configure the device by supplying the files  in xps/implementation. cdc file is in the implementation directory

then download the file via the xmd shell: (current directory is sdk/sdk_export/ccd_readout_web)
 connect mb mdm
 dow -data image.mfs 0xBE000000
the base address of the file system is set in the bsp settings

to generate the  quad SPI in XPS use bitgen settings: -g TdoPin:PULLNONE -g SPI_buswidth:4  #-g StartUpClk:JTAGCLK
Then select ELF bootloader (project/select ELF), update bitfile (device configuration, update)

to generate binary from ELF use:
open xilinx tools -> shell and choose ccd_readout_web/debug folder
mb-objcopy  -O  binary  -R .vectors.reset -R .vectors.sw_exception -R .vectors.interrupt -R .vectors.debug_sw_break -R .vectors.hw_exception CCD_readout_web.elf  CCD_readout.b
mb-objcopy  -O  binary  -j .vectors.reset -j .vectors.sw_exception -j .vectors.interrupt -j .vectors.debug_sw_break -j .vectors.hw_exception CCD_readout_web.elf  vectors.b
then run S3ADSPSK_bootload.bat script in FLASH_BURN (project/xps) as Admin (this generates an vectorizedapp.mcs from elf) 
Use IMPACT to burn the mcs from above into the flash(use current Impact project). This takes 10+ minutes. Or use update mcs button

TODO 
done --implement shift digital gain
done -- fix resolution limit
done -- test large file buffer performance 2.4ms for 8kB copy/deinterlac
done image acquisition status

probably done, test more-- not sure if bitfile upload works. Seems to write flash, but could not make it configure without going through impact. This seems to work. 

-- timing file upload can crash webserver. this seems to be packet length dependant. add timeout or something.
-- fix pic command string. use command length, timeout, don't use start and end
-- fix hv dac setting after initial startup. requires two apply settings.
-- fix error that causes the readout to not complete. Unknown issue, requires reboot of entire system currently.
-- add abort button to expose/read. needs to clear trigger, pending bit, reset state machine.
-- write arbitrary file to mfs.
-- find a better way to save files, currently webpage save is not handled correctly (script references get modified).
-- auto offset  --read offset working, updates during idlemode only.
-- scope mode
-- interupt based image read
-- implement jumper to select if MFS is read from Flash HW/platform_fs.c currently we need to disable flashread manually untill an MFS exists in flash to prevent error/abort of boot code.
-- implement DAC updates from wave file

Bugs
--state machine gets triggered during BRAM configure, bad waveform, fix this
-- readout during live noise mode not possible
-- Reset/power down of controller during life noise mode causes crash. Need to close webpage before controller re-boot to recover.