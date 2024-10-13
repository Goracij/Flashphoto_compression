import time
#import numpy
import os
import sys
import shutil
import math

MAX_AMPLITUDE_VALUE = 0.15   #Recalculated amplitude treshhold
RANGE_MIN = -3.5E-04
RANGE_MAX = -2.5E-05

print('\nThis program does raw data file processing.\n\nEnter the raw *.DAT data file name without extension:')
filename = input()                                              # reading out the source RAW data file name
foldname = filename

# Check wheter the data file exists
if os.path.isfile(filename + '.DAT'):
    print('Processing file ' + filename + '.DAT')
else:
    print('Raw data file ' + filename + '.DAT not found.')
    sys.exit()

pathstr = os.getcwd()
# Check wheter the working folders exist
if os.path.isdir('./' + filename):
    print('Folders ' + pathstr + '\\' + foldname + ' and ' + pathstr + '\\' + foldname + '_AG exist.\nTerminating execution.')
    sys.exit()
else:
    os.mkdir(foldname)
    os.mkdir(pathstr + '\\' + foldname + '_AG')
    print('Directory ' + pathstr + '\\' + foldname + ' successfully created.\n')

# Check of the empty file and double \n symbols
wlnum = 1
wl_num_name = '0' + str(wlnum)
data_file = open(filename + '.DAT', "r")
linebuff = data_file.readlines()
if '\n\n' in linebuff:
    print('ERROR_5: There are doube NEW_LINE symbols in data file. Check the file format. Terminating execution.')
    data_file.close()
    sys.exit()
if len(linebuff) < 5:
    print('ERROR_4: Check the beginning of the file (empty dataset?). Terminating execution.')
    data_file.close()
    sys.exit()
data_file.close()



data_file = open(filename + '.DAT', "r")
linebuff = data_file.readline()
new_file_path = pathstr + '\\' + foldname + '\\' + filename + '_W_' + wl_num_name + '_FAST' + '.DAT'
if linebuff != '':
    wl_buff = open(new_file_path, "x")
else:
    print('---> ERROR_6: There are NEW_LINE symbols at the beginning of data file. Check the file format. Terminating execution.')
    data_file.close()
    sys.exit()

data_points = 1
previous_time = -1
prev_line = ''

while linebuff != '':
    str_buff = linebuff.split()
    
    if linebuff[0] != '-':
        if float(str_buff[1]) < 0 and previous_time >= 0 and prev_line[0] != '-':
            new_file_path = pathstr + '\\' + foldname + '\\' + filename + '_W_' + wl_num_name + '_SLOW' + '.DAT'
            wl_buff.close()
            print('Processed ' + str(data_points - 1) + ' points            FAST')
            data_points = 1
            wl_buff = open(new_file_path, "x")
            wl_buff.write(linebuff)
        else:
            wl_buff.write(linebuff)
        
        previous_time = float(str_buff[1])
        prev_line = linebuff
        linebuff = data_file.readline()
        if linebuff == '' and prev_line[0] != '-':
            print('---> ERROR_7: Unexpected end of dataset. Check the input file.')
    else:
        wl_buff.write(linebuff[:len(linebuff) - 1])
        wl_buff.close()
        wlnum += 1
        data_points += -1
        print('Processed ' + str(data_points) + ' points for ' + linebuff[3:6] + 'nm, SLOW')
        data_points = 0
        if wlnum < 10:
            wl_num_name = '0' + str(wlnum)
        else:
            wl_num_name = str(wlnum)

        previous_time = float(str_buff[1])
        prev_line = linebuff
        linebuff = data_file.readline()
        if linebuff != '':
            new_file_path = pathstr + '\\' + foldname + '\\' + filename + '_W_' + wl_num_name + '_FAST' + '.DAT'
            wl_buff = open(new_file_path, "x")
        elif linebuff == '' and prev_line[0] != '-':
            print('---> WARNING: Unexpected end of dataset. Check the input file.')
        #else:
            #print('Sorting of datapoints completed.')
        
    data_points += 1

data_file.close()
wl_buff.close()

BOOL_SHIFT = False
BOOL_SHIFT_VERT = False
vert_fast = 0

compr_str = ''
compr_str = input('\nDo you want to shift first point for SLOW scope one step behind? (yes/no):\n')
if 'y' in compr_str:
    BOOL_SHIFT = True
    print(BOOL_SHIFT)
else:
    print(BOOL_SHIFT)


compr_str = ''
compr_str = input('\nDo you want to shift FAST scope data verticaly up? (yes/no):\n')
if 'y' in compr_str:
    BOOL_SHIFT_VERT = True
    print(BOOL_SHIFT_VERT)
    compr_str = input('\nEnter the shift number (decimal notation). Positive - up, Negative - down:\n')
    vert_fast = float(compr_str)
else:
    BOOL_SHIFT_VERT = False
    vert_fast=0
    print(BOOL_SHIFT_VERT)



new_file_path = pathstr + '\\' + foldname + '\\'
#print('\nCreated new temporaty files in ' + new_file_path)
for file in os.listdir(new_file_path):
# Calculation of sigma and base line
    data_file = open(new_file_path + file, "r")
    linebuff = data_file.readline()
    sigsumm = 0
    data_points = 0
    signal_ave = 0
    variance = 0
    sigma = 0
    prev_line = ''
    str_buff = linebuff.split()
    while linebuff != '' and float(str_buff[1]) <= 0:
        if float(str_buff[1]) >= RANGE_MAX or float(str_buff[1]) <= RANGE_MIN:
            sigsumm += float(str_buff[2])
            data_points += 1
        prev_line = linebuff
        linebuff = data_file.readline()
        str_buff = linebuff.split()
        if linebuff == '' and prev_line[0] != '-':
            print('---> WARNING: Unexpected dataset end in file ' + file)
    data_file.close()
    signal_ave = sigsumm/data_points
    data_file = open(new_file_path + file, "r")
    linebuff = data_file.readline()
    str_buff = linebuff.split()
    prev_line = ''
    while linebuff != '' and float(str_buff[1]) <= 0:
        if float(str_buff[1]) >= RANGE_MAX or float(str_buff[1]) <= RANGE_MIN:
            variance += (float(str_buff[2]) - signal_ave)**2
        prev_line = linebuff
        linebuff = data_file.readline()
        str_buff = linebuff.split()
    variance = variance / data_points
    sigma = math.sqrt(variance)
    weight = 1/sigma
    print('STD for ' + file + ' is ' + f'{sigma:5e}' + '. Number of points: ' + str(data_points))
    data_file.close()
    
# Calculation of delta time
    data_file = open(new_file_path + file, "r")
    linebuff = data_file.readline()
    time_delta = 0
    flag = True
    prev_line = linebuff
    prev_buff = prev_line.split()
    while linebuff != '' and flag:
        str_buff = linebuff.split()
        if float(str_buff[1]) == 0 and float(prev_buff[1]) < 0:
            time_delta = abs(float(prev_buff[1]))
            flag = False
        prev_line = linebuff
        prev_buff = prev_line.split()
        linebuff = data_file.readline()
    if time_delta == 0:
        print('ERROR_7: Impossible to determine the delta t - zero was not found. Processing terminated.')
        data_file.close()
        sys.exit()
    else:
        print('---------------> DELTA ' + str(time_delta) + '\n')
    data_file.close()

# Removal of negative-time points, replacement of time scale, calculation of ABS and assignation of weight
    data_file = open(new_file_path + file, "r")
    wl_buff = open(pathstr + '\\' + foldname + '_AG\\' + file[:len(file) - 4] + '_AG.DAT', "x")
    linebuff = data_file.readline()
    prev_line = linebuff
    prev_buff = prev_line.split()
    if (BOOL_SHIFT) and ('L' in file):
        current_time = 0
    else:
        current_time =  time_delta
    flag = False
    wlnum = 1

    while linebuff != '':
        str_buff = linebuff.split()
        if linebuff[0] != '-' and float(str_buff[1]) > 0 and linebuff != '\n':
            if 'L' in file:
# Заплатка - вместо L должно быть SLOW но тогда всегда True
                if BOOL_SHIFT_VERT:
                    if current_time != 0:
                        try:
                            wl_buff.write(str(wlnum) + '     ' + f'{current_time:.8e}' + '     ' + f'{-math.log10(float(str_buff[2])/signal_ave):.8e}' + '     ' + f'{weight:.5f}' + '\n')
                        except:
                            wl_buff.write(str(wlnum) + '     ' + f'{current_time:.8e}' + '     ' + '0' + '     ' + '0' + '\n')
                            flag = True
                        current_time = current_time + time_delta
                        wlnum += 1
                    else:
                        current_time = current_time + time_delta
                else:
                    try:
                        wl_buff.write(str(wlnum) + '     ' + f'{current_time:.8e}' + '     ' + f'{(-math.log10(float(str_buff[2])/signal_ave)):.8e}' + '     ' + f'{weight:.5f}' + '\n')
                    except:
                        wl_buff.write(str(wlnum) + '     ' + f'{current_time:.8e}' + '     ' + '0' + '     ' + '0' + '\n')
                        flag = True
                    current_time = current_time + time_delta
                    wlnum += 1
            else:
                try:
                    wl_buff.write(str(wlnum) + '     ' + f'{current_time:.8e}' + '     ' + f'{-math.log10(float(str_buff[2])/signal_ave)+vert_fast:.8e}' + '     ' + f'{weight:.5f}' + '\n')
                except:
                    wl_buff.write(str(wlnum) + '     ' + f'{current_time:.8e}' + '     ' + '0' + '     ' + '0' + '\n')
                    flag = True
                current_time = current_time + time_delta
                wlnum += 1
        elif linebuff[0] == '-':
            wl_buff.write(linebuff + '\n')
        prev_line = linebuff
        prev_buff = prev_line.split()
        linebuff = data_file.readline()
        str_buff = linebuff.split()
    if flag:
        print('---->ERROR: Negative LOG argument detected! Replaced values with 0 AMP and 0 WHGT.')
    data_file.close()
    wl_buff.close()




# Writing non-compressed, weighted data file without negative-time points with voltages transformed to AUs
new_file_name = 'INPUT' + filename[3:]
while os.path.isfile(new_file_name + '.DAT_RAW'):
    print('Raw data file ' + new_file_name + '.DAT_RAW' + ' already exists. Input new name without extention:\n')
    input(new_file_name)
print('New non-compressed, weighted data file without negative-time points with voltages transformed to AUs:\n' + new_file_name + '.DAT_RAW')
wl_buff = open(new_file_name + '.DAT_TEMP', "x")
for file in os.listdir(pathstr + '\\' + foldname + '_AG\\'):
    data_file = open(pathstr + '\\' + foldname + '_AG\\' + file, "r")
    linebuff = data_file.readline()
    while linebuff != '':
        wl_buff.write(linebuff)
        linebuff = data_file.readline()
    data_file.close()
wl_buff.close()
data_file = open(new_file_name + '.DAT_TEMP', "r")
wl_buff = open(new_file_name + '.DAT_RAW', "x")
linebuff = data_file.readline()
data_points = 1
while linebuff != '':
    str_buff = linebuff.split()
    if linebuff[0] != '-':
        wl_buff.write(str(data_points) + '     ' + str_buff[1] + '     ' + str_buff[2] + '     ' + str_buff[3]+ '\n')
        data_points += 1
    else:
        wl_buff.write(linebuff)
        data_points = 1
    linebuff = data_file.readline()
data_file.close()  
wl_buff.close()
os.remove(pathstr + '\\' + new_file_name + '.DAT_TEMP')


# Writing COMPRESSED (final), weighted data file without negative-time points with voltages transformed to AUs
new_file_name = 'INPUT' + filename[3:]
while os.path.isfile(new_file_name + '.DAT_COMP'):
    print('Raw data file ' + new_file_name + '.DAT_COMP' + ' already exists. Input new name without extention:\n')
    input(new_file_name)
print('\n\nNew COMPRESSED, weighted data file without negative-time points with voltages transformed to AUs:\n' + new_file_name + '.DAT_COMP')


wl_buff = open(new_file_name + '.DAT_COMP', "x")
comp_number = 50
lines_counter_new = 0
comp_number = int(input('Enter integer number of points per compression interval:'))
for file in os.listdir(pathstr + '\\' + foldname + '_AG\\'):
    data_file = open(pathstr + '\\' + foldname + '_AG\\' + file, "r")
    if 'FAST' in file: 
        lines_counter_new = 0   # number of compressed point in new file
    data_points = 0         # number of current line in original file
    n = 1                   # number of points to average
    flag = True             # bool flag: True if line is not starting with '-', False if it starts with '-'
    error_flag = False
    error_counts_new = 0
    large_amplitude_counter = 0
    linebuff = data_file.readlines()
    lines_number = len(linebuff)    # amount of lines in original file
    data_file.close()
    if lines_number < comp_number:
        while lines_number < comp_number:
            comp_number = int(input('WARNING: Each scope set contains ' + str(lines_number) + '<' + str(comp_number) + '. Enter new number less than ' + str(lines_number) + ': '))
    data_file = open(pathstr + '\\' + foldname + '_AG\\' + file, "r")
    while data_points < lines_number and flag:            #while we processed less lines then there are in file
        iterator = 0                             #number of iteration within the given compression number
        while data_points < lines_number and iterator < comp_number and flag:   #while we got less compressed points in compression window
            k = 0
            actual_k = 0                        #number of points where logarithm exists (amp and average of the same sign), i.e. diod worked fine
            time_summ = 0
            amp_summ = 0
            sigma_new = 0
            flag = True
            while data_points < lines_number and iterator < comp_number and k < n and flag:                #while took less points that we should for the given compression window
                linebuff = data_file.readline()
                if linebuff != '' and linebuff[0] != '-':
                    str_buff = linebuff.split()
                    amp_summ = amp_summ + float(str_buff[2])
                    sigma_new = float(str_buff[3])
                    time_summ = time_summ + float(str_buff[1])
                    data_points += 1        #added +1 to the counter of total points that we read from original file
                    k += 1                  #added +1 to the counter of averaging points, i.e. processed less then 1, 2, 4, 8... For each next window we double the number of averaged points
                    if str_buff[2] != '0':  #EXCEPTION processing - negative logarithm argument
                        actual_k += 1
                else:
                    flag = False
            if flag:
                if actual_k == k:
                    time_summ = time_summ/k
                    amp_summ = amp_summ/k
                    sigma_new = sigma_new * (math.sqrt(n))
                    lines_counter_new += 1
                    if abs(amp_summ) < MAX_AMPLITUDE_VALUE:          #cut-off for MAX_AMPLITUDE_VALUE 
                        wl_buff.write(str(lines_counter_new) + '     ' + f'{time_summ:.8e}' + '     ' + f'{amp_summ:.8e}' + '     ' + f'{sigma_new:.5f}' + '\n')
                    else:
                        wl_buff.write(str(lines_counter_new) + '     ' + f'{time_summ:.8e}' + '     ' + '0' + '     ' + '0' + '\n')
                        large_amplitude_counter += 1
                else:
                    time_summ = time_summ/k
                    amp_summ = 0
                    sigma_new = 0
                    lines_counter_new += 1
                    wl_buff.write(str(lines_counter_new) + '     ' + f'{time_summ:.8e}' + '     ' + '0' + '     ' + '0' + '\n')
                    error_flag = True
                    error_counts_new += 1
                iterator += 1
            else:
                if actual_k == k:
                    time_summ = time_summ/k
                    amp_summ = amp_summ/k
                    sigma_new = sigma_new * (math.sqrt(n))
                    lines_counter_new += 1
                    if abs(amp_summ) < MAX_AMPLITUDE_VALUE:          #cut-off for MAX_AMPLITUDE_VALUE 
                        wl_buff.write(str(lines_counter_new) + '     ' + f'{time_summ:.8e}' + '     ' + f'{amp_summ:.8e}' + '     ' + f'{sigma_new:.5f}' + '\n')
                    else:
                        wl_buff.write(str(lines_counter_new) + '     ' + f'{time_summ:.8e}' + '     ' + '0' + '     ' + '0' + '\n')
                        large_amplitude_counter += 1
                else:
                    time_summ = time_summ/k
                    amp_summ = 0
                    sigma_new = 0
                    lines_counter_new += 1
                    wl_buff.write(str(lines_counter_new) + '     ' + f'{time_summ:.8e}' + '     ' + '0' + '     ' + '0' + '\n')
                    error_flag = True
                    error_counts_new += 1
                wl_buff.write(linebuff)
                iterator += 1
        n = n * 2                       # since we are done with averaging "window" - we double the number off points for the next window
    data_file.close()
    if error_flag:
        print('--->WARNING: ' + str(error_counts_new) + ' points in ' + file + ' were ZEROed - negative logarithm argument.')
    if large_amplitude_counter != 0:
        print('--->WARNING: ' + str(large_amplitude_counter) + ' points in ' + file + ' were ZEROed - Exceeding AMPLITUDE (Max = ' + str(MAX_AMPLITUDE_VALUE) + 'AU)')
print('Number of data points per WL set: ' + str(lines_counter_new) + '\n')
wl_buff.close()


print("Processing finished.")
shutil.rmtree(pathstr + '\\' + foldname + '\\')
shutil.rmtree(pathstr + '\\' + foldname + '_AG\\')

time.sleep(1)