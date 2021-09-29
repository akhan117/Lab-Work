from os.path import exists

# All this program does is create the config file and print the instructions for it.

Config_path = 'Config.txt'

if exists(Config_path):
    mode = 'a'
else:

    print("Config created")
    print("READ - You must configure the config file for the program to work!")

    mode = 'w'
    with open(Config_path, mode) as f:
        f.write('Replace this line with the path for the first spike2 set.\n')
        f.write('Replace this line with the path for the second spike2 data set.\n')
        f.write('Replace this line to the path you want to save to.\n')
        f.write('Enter the channels you want to record - for example, if you want to use the channels called U1\n')
        f.write('and U2, simply replace these lines with "U1, U2" (without the quotations). You do not need to edit ')
        f.write('these lines until you want to run Channel_extract.')

    exit()
