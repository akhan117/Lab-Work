These programs work together in order to be able to create files that can be fed to Spyking-Circus, using Spike2 recordings.

The Steps are as follows -
1) Run Spyking2Numpy. This will create a config file for you to edit.
2) Edit the config to add the location and names of the two Spyke2 files. Also add the folder you want to save the processed file to. (I suggest a different folder from the program)
3) Run Spyking2Numpy again. The file that contains data from all the channels will be created at the folder you specified.
4) If you want to extract certain Channels from the files that's been created, add them to the Config file as well. Then run Channel_Extract.
5) Channel_Extract will extract the Channels you need and put them into a new file in the same folder you saved to previously.

Notes - 
1) The files are processed in the order they are put in the config file. Basically, put the pre infusion file before the post infusion one.
2) Events.txt will be created after running Spyking2Numpy the second time. This notes all the events and their timings during the recordings.
3) Channels.txt will be created at the same time. This contains all the channels and more importantly, their sampling rates.
4) Spyking-Circuses parameter files will ask you for a probe file. I've provided two for you here, probe3 works for 3 channels and probe4 works for 4.

