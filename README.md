# CPX M0 dream monocle
See blog post and Youtube video for info and I should advise that although this is less than 300 lines of code and generally intuitive, it is not a copy and paste job and you will likely need to test and refine as per notes:

Also if you’re not familiar with the CPX and similar boards, check the overview site and try some of the tutorial projects first:
https://learn.adafruit.com/adafruit-circuit-playground-express/overview

There are 4 files required:
1.	boot.py – you’ll probably already have this when you setup circuitpython but you’ll need to copy the code from my one so that it enables code.py to write to the system memory for logging.
2.	lucid_setting.txt – this is to load and save settings for delay offset and NeoPixel brightness for dream cues.
3.	logfile.csv – logs data such as eye and face movement, I've kept some short sample data in this one as an example.
4.	code.py – main source code of the project.

The code should be self expanatory but essentially:
1.	When you turn it on, the CPX resets the log file and checks if the user presses either of the 2 buttons for 20 seconds. The first button can be used to set the time delay on REM checking, the other is for setting LED brightness. For the timer setting button, if only the first LED is lit then the CPX will check for REM movement immediately and this is only for testing REM check is working; each time you press and light another LED after that, 30mins are added to the time delay. All settings are saved to the settings file and persist so long as the CPX’s toggle switch is in the relevant position.

2.	After changing the settings or waiting for the initial 20 seconds, the CPX hibernates until the delay time is reached. The main loop then checks for face movement and eye movement and these checks are based on taking standard deviations of analogue inputs to assess variations within a sample. The thresholds can be set through the variables which are listed under ‘advanced settings’ in the code. You’ll notice there’s quite specific timings for how the IR readings are taken and this might need to be different for your specific board as there’s a few factors involved e.g. variances in hardware tolerance and shape/speed of your eye and movement. See this video for an understanding of the IR and sensor on the CPX (special thanks to Ladyada for the detail in this):
https://www.youtube.com/watch?v=SEUnLiQlxN0

3.	There is a log file that is generated as long as you have the board’s toggle switch in the appropriate position that enables the script to write to file. The log file first records raw analogue readings from both the accelerometer and IR sensor over a set sample time, it then provides a summary of these readings in order: time (seconds since device was turned on),  face movement standard deviation, eye movement standard deviation, CPU temperature. I do suggest keeping an eye on the CPU temp – I don’t expect any overheating because most of the time the device is hibernating but I generally advise monitoring temp for all wearable projects.

When powering the board, I’ve used 3 AAA batteries, anything less and this probably won’t work – with 2 AAA’s the board will power up but that’s about all. I wouldn't use lipo batteries, these are generally not safe for hobbyist use in front of your face.

There’s probably a number of improvements that can be made, perhaps alternative approaches to detecting eye-movement, where I’ve used standard deviation there might be other ways that are more effective or efficient, there’s some interesting algorythms used in seismology where you compare long and short averages. Also, although CircuitPython is much easier to work with than Arduino, doing this as an Arduino project would definitely work better – you don’t need to keep the IR LED on for as long (I already fried one mistakenly) and you have more memory to work with if you wanted to add additional features. I may look to convert this into Arduino when I get a chance, otherwise feel free to fork your own – would be interested to see other implementations.

Happy Dreaming.
