import h5py
from tkinter.filedialog import *
import ntpath
import pickle
import pandas as pd
import numpy as np
from openpyxl import Workbook
from os.path import exists

letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
           'V', 'W', 'X', 'Y', 'Z']

lettersExpanded = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                   'U', 'V', 'W', 'X', 'Y', 'Z']
for i in letters:
    for j in letters:
        lettersExpanded.append(i + j)

sheetList = []
if __name__ == "__main__":

    print("Select the files you'd like to extract Data from")
    wb = Workbook()

    OdorList = set()
    fileList = []
    while True:
        val = askopenfilename()
        fileList.append(val)

        if val == "":
            break
    fileList = fileList[:-1]
    megaCount = 1

    for file in fileList:
        file2 = ntpath.basename(file)
        file2 = file2[:-19]
        file2 = file2.split(",")[-1]
        file2 = file2.split()[1:]
        fileNew = ""

        for i in file2:
            fileNew = fileNew + i + " "

        folder = "Event and Sampling Rates Data/" + fileNew
        splits = folder + "splits.pk"
        with open(splits, 'rb') as fi:
            splits_list = pickle.load(fi)

        rate_file = "Default Values/Default Sampling Rate.pk"
        with open(rate_file, 'rb') as fi:
            sampling = pickle.load(fi)

        events = folder + "events.pk"
        with open(events, 'rb') as fi:
            eventList = pickle.load(fi)

        times = folder + "times.pk"
        with open(times, 'rb') as fi:
            timeList = pickle.load(fi)

        eventTime = []
        print(eventList)
        print(timeList)
        for i in range(0, len(eventList)):
            eventTime.append((eventList[i], timeList[i]))

        print(eventTime)

        splits_list = splits_list[:-1]
        splits_list.insert(0, 0.0)
        splitn = splits_list[1] / sampling

        neurons = []
        names, onsets, offsets = '', '', ''
        with h5py.File(file, 'r+') as f:
            names = f["Odor_Names"][:]
            onsets = f["Odor_Onsets"][:]
            offsets = f["Odor_Offsets"][:]
            neuron_test = f["Neurons"]
            for i in neuron_test:
                neurons.append(neuron_test[i][:])

        timingList = []
        for i in range(0, len(names)):
            timingList.append((names[i], onsets[i]))

        if megaCount == 1:
            print("Type in the number of the option you'd like to run -")
            print("1) Spontaneous Activity before any Odors")
            print("2) Odor responses")
            option = input()

        ####################################################################################################################
        if option == '1':
            if megaCount == 1:
                print("What is the start point of the data?")
                start = float(input())
                postStart = start + splitn
                print("How many seconds of data do you want?")
                length = float(input())

            neuro_pre = {}
            neuro_post = {}
            count = 1
            for n in neurons:
                name = "neuron_" + str(count)
                neuro_pre[name] = []
                neuro_post[name] = []
                count += 1

            count = 1
            for n in neurons:
                name = "neuron_" + str(count)
                ls = []
                ls2 = []
                for n1 in n:
                    if start < n1 < start + length:
                        ls.append(n1)

                    elif postStart < n1 < postStart + length:
                        ls2.append(n1)
                neuro_pre[name].append(len(ls))
                neuro_post[name].append(len(ls2))
                count += 1
            print("Pre Drugs:" + str(neuro_pre))
            print("Post Drugs:" + str(neuro_post))
            print()

            if exists("Default Values/Default Save to Location E.pk"):
                print()
                print(
                    "Using the Default save to location from Default Save to Location E.pk! Delete this file if you do"
                    + " not want to use the default save to location anymore!")

                with open("Default Values/Default Save to Location E.pk", 'rb') as fi:
                    excelName = pickle.load(fi)

                print("Saving to " + excelName)

            else:
                print(
                    "#################################################################################################")
                print("Where do you want to save the files to")
                save_to = askdirectory()
                print("What do you want to name the file?")
                print(
                    "#################################################################################################")

                excelName2 = input()
                excelName = (save_to + '\\' + excelName2 + ".xlsx")

                print("Do you want save this as the default location to save to (y/n)")
                default = input()

                if default == 'y':
                    with open("Default Values/Default Save to Location E.pk", 'wb') as fi:
                        pickle.dump(excelName, fi)

                elif default == 'n':
                    print()

                else:
                    print("Defaulting to n.")

            miniCount = str(megaCount)
            ws = wb.active

            ws['A' + miniCount] = ntpath.basename(file)
            ws['D' + miniCount] = "Neuron ID"
            ws["B" + miniCount] = "Start Time"
            ws["B" + str(megaCount + 1)] = start
            ws["C" + miniCount] = "Duration"
            ws["C" + str(megaCount + 1)] = length
            ws["E" + miniCount] = "Pre Infusion Spikes"
            ws["F" + miniCount] = "Post Infusion Spikes"

            counter = megaCount + 1
            for i in neuro_pre:
                ws['D' + str(counter)] = i
                ws['E' + str(counter)] = neuro_pre[i][0]
                ws['F' + str(counter)] = neuro_post[i][0]
                counter += 1

            wb.save(excelName)
            megaCount += len(neurons) + 2

        ################################################################################################################
        elif option == '2':
            if megaCount == 1:
                print("Enter the number of seconds before odor infusions you'd like to analyze.")
                timeB = float(input())
                print("Enter the number of seconds after odor infusions you'd like to analyze.")
                timeA = float(input())
                print("Enter the size of each bin.")
                binSize = float(input())

                binNoB = int(timeB / binSize)
                binNoA = int(timeA / binSize)
                print("The Number of bins before each odor infusions is " + str(binNoB))
                print("The Number of bins after each odors infusions is " + str(binNoA))

                if exists("Default Values/Default Save to Location E2.pk"):
                    print()
                    print(
                        "Using the Default save to location from Default Save to Location E2.pk! Delete this file if "
                        + "you do not want to use the default save to location anymore!")

                    with open("Default Values/Default Save to Location E2.pk", 'rb') as fi:
                        excelName = pickle.load(fi)

                    print("Saving to " + excelName)

                else:
                    print(
                        "#############################################################################################")
                    print("Where do you want to save the files to")
                    save_to = askdirectory()
                    print("What do you want to name the file?")
                    print(
                        "#############################################################################################")

                    excelName2 = input()
                    excelName = (save_to + '\\' + excelName2 + ".xlsx")

                    print("Do you want save this as the default location to save to (y/n)")
                    default = input()

                    if default == 'y':
                        with open("Default Values/Default Save to Location E2.pk", 'wb') as fi:
                            pickle.dump(excelName, fi)

                    elif default == 'n':
                        print()

                    else:
                        print("Defaulting to n.")

            odorData = {}
            for n in names:
                OdorList.add(n)
                odorData[n] = []

            print(odorData)

            binDivB = []
            binDivA = []
            for i in range(1, binNoB + 1):
                binDivB.append(binSize * i)

            for i in range(1, binNoA + 1):
                binDivA.append(binSize * i)

            ws = wb.active

            binTimingsPre = []
            binTimingsPost = []
            for i in eventTime:
                time = i[1]
                temp = []
                temp2 = []
                for j in binDivB:
                    temp.append(time - j)

                temp.append(time)
                temp.sort()
                temp2.append(time)
                for k in binDivA:
                    temp2.append(time + k)

                binTimingsPre.append((i[0], temp))
                binTimingsPost.append((i[0], temp2))

            print(binTimingsPre)
            print(binTimingsPost)

            prIprO = {}
            pIprO = {}
            prIpO = {}
            pIpO = {}

            count = 1

            for n1 in neurons:
                neuron_ID = "neuron_" + str(count)
                prIprO[neuron_ID] = []
                pIprO[neuron_ID] = []
                prIpO[neuron_ID] = []
                pIpO[neuron_ID] = []
                full_list_prIprO = []
                full_list_pIprO = []
                full_list_prIpO = []
                full_list_pIpO = []

                count += 1
                print(len(n1))
                for [odor, timing] in binTimingsPre:
                    temp1 = [odor]
                    temp2 = [odor]

                    for t in range(0, len(timing) - 1):

                        count1 = 0
                        count2 = 0
                        updated_split = timing[len(timing) - 1]
                        for n in n1:

                            if timing[t] < n < timing[t + 1]:
                                if n < splitn + timeB:
                                    count1 += 1
                                else:
                                    count2 += 1

                        if timing[t] < splitn + timeB:
                            temp1.append(count1)
                        else:
                            temp2.append(count2)

                    if len(temp1) == binNoB + 1:
                        full_list_prIprO.append(temp1)
                    if len(temp2) == binNoB + 1:
                        full_list_pIprO.append(temp2)
                prIprO[neuron_ID] = full_list_prIprO
                pIprO[neuron_ID] = full_list_pIprO

                for [odor, timing] in binTimingsPost:
                    temp1 = [odor]
                    temp2 = [odor]

                    for t in range(0, len(timing) - 1):

                        count1 = 0
                        count2 = 0

                        for n in n1:
                            if timing[t] < n < timing[t + 1]:

                                if n < splitn + timeA:
                                    count1 += 1
                                else:
                                    count2 += 1

                        if timing[t] < splitn + timeA:
                            temp1.append(count1)
                        else:
                            temp2.append(count2)

                    if len(temp1) == binNoA + 1:
                        full_list_prIpO.append(temp1)
                    if len(temp2) == binNoA + 1:
                        full_list_pIpO.append(temp2)

                prIpO[neuron_ID] = full_list_prIpO
                pIpO[neuron_ID] = full_list_pIpO

            print(full_list_prIprO)
            print(prIprO)
            print(pIprO)
            print(prIpO)
            print(pIpO)

            miniCount = str(megaCount)
            miniCountp = str(megaCount + 1)

            ws['A' + miniCount] = "File Name"
            ws['A' + miniCountp] = ntpath.basename(file)
            ws['B' + miniCount] = "Pre Odor Bins"
            ws['B' + miniCountp] = binNoB
            ws['C' + miniCount] = "Post Odor Interval Size"
            ws['C' + miniCountp] = binNoA
            ws['D' + miniCount] = "Bin Size"
            ws['D' + miniCountp] = binSize
            ws['E' + miniCount] = "Odor Identity"
            ws['F' + miniCount] = "Neuron_ID"
            ws['G' + miniCount] = "Pre Inf Pre Odor Spikes"
            ws['H' + miniCount] = "Pre Inf Post Odor Spikes"
            ws['I' + miniCount] = "Post Inf Pre Odor Spikes"
            ws['J' + miniCount] = "Post Inf Post Odor Spikes"

            something = megaCount + 1
            something1 = something
            keys = prIprO.keys()
            keys = sorted(keys)
            buffer = len(keys) + 1
            for i in keys:
                count = 0
                for j in prIprO[i]:
                    ws['E' + str(something)] = j[0]
                    ws['F' + str(something)] = i
                    ws['G' + str(something)] = str(j[1:])

                    something += 1

                for j in prIpO[i]:
                    ws['E' + str(something1)] = j[0]
                    ws['F' + str(something1)] = i
                    ws['H' + str(something1)] = str(j[1:])

                    something1 += 1

            something = max(something, something1) + 1
            something1 = something

            for i in keys:
                count = 0
                for j in pIprO[i]:
                    ws['E' + str(something)] = j[0]
                    ws['F' + str(something)] = i
                    ws['I' + str(something)] = str(j[1:])

                    something += 1

                for j in pIpO[i]:
                    ws['E' + str(something1)] = j[0]
                    ws['F' + str(something1)] = i
                    ws['J' + str(something1)] = str(j[1:])

                    something1 += 1

            # for i in prIprO:
            #     ws['E' + str(something)] = i[0]
            #     ncount = 1
            #     small = something
            #     for j in i[1:]:
            #
            #         ws['G' + str(small)] = j
            #         ws['F' + str(small)] = "Neuron_" + str(ncount)
            #
            #         ncount += 1
            #         small += 1
            #
            #     something += ncount

            something = max(something, something1)
            print(len(prIprO["neuron_1"]))
            print(len(prIpO["neuron_1"]))
            print(splitn)
            megaCount = something + 1
            wb.save(excelName)

    # ####################################################################################################################
    # elif option == '2':
    #     print("How many seconds before and after the Odors?")
    #     inp = input()
    #     inp = int(inp)
    #     print()
    #     nameset = set(names)
    #     count = 1
    #     for i in nameset:
    #         print(str(count) + "." + str(i))
    #         count += 1
    #
    #     print()
    #     print("Enter the numbers of the odors(e.g - 1 2 5) you want, leave blank for all odors")
    #     var = input()
    #
    #     if var:
    #         var = var.split(" ")
    #         var = [int(i) for i in var]
    #         var = [i - 1 for i in var]
    #         var = sorted(var)
    #         selected_names = []
    #         for i in var:
    #             selected_names.append(list(nameset)[i])
    #
    #         print("The Odors selected are :" + str(selected_names))
    #
    #     else:
    #         selected_names = list(nameset)
    #         print("The Odor selected are :" + str(selected_names))
    #
    #     print(nslist)
    #     name_times = {}
    #     for i in selected_names:
    #         name_times[i] = []
    #         for (j, k) in nslist:
    #             if i == j:
    #                 name_times[i].append(k)
    #
    #     print()
    #
    #     name_freq_pre = {}
    #     name_freq_pre2 = {}
    #     name_freq_post = {}
    #     name_freq_post2 = {}
    #     for j in name_times:
    #         name_freq_pre2[str(j)] = {}
    #         name_freq_post2[str(j)] = {}
    #         count = 1
    #         for i in neurons:
    #             name = str(j)
    #             name = name + "_" + str(count)
    #             numb = str(count)
    #             name_freq_pre[name] = []
    #             name_freq_post[name] = []
    #             name_freq_pre2[str(j)][numb] = []
    #             name_freq_post2[str(j)][numb] = []
    #
    #             count += 1
    #
    #     for j in name_times:
    #         count = 1
    #         for i in neurons:
    #             name = str(j)
    #             name = name + "_" + str(count)
    #             for timing in name_times[j]:
    #                 ls = []
    #                 ls2 = []
    #                 for n1 in i:
    #                     if timing - inp < n1 < timing + inp:
    #                         if n1 < splitn:
    #                             ls.append(n1)
    #                         else:
    #                             ls2.append(n1)
    #                 length = len(ls)
    #                 length2 = len(ls2)
    #                 if length != 0:
    #                     name_freq_pre2[str(j)][str(count)].append(length)
    #                     name_freq_pre[name].append(length)
    #                 elif length2 != 0:
    #                     name_freq_post2[str(j)][str(count)].append(length2)
    #                     name_freq_post[name].append(length2)
    #
    #             count += 1
    #
    #     print("Pre Drugs:" + str (name_freq_pre2))
    #     print("Post Drugs:" + str (name_freq_post2))
    #
    #     #EXCEL
    #     wb = Workbook()
    #     sheet_list = []
    #     ws = wb.active
    #
    #     keys = name_freq_pre2.keys()
    #     keylist = list(keys)
    #     ws.title = str(keylist[0])
    #     sheet_list.append(ws)
    #     for i in keylist[1:]:
    #
    #         sheet_list.append(wb.create_sheet(str(i)))
    #
    #     max = []
    #     for i in sheet_list:
    #         wb.active = i
    #         count = 1
    #         i['A1'] = i.title
    #         max1 = 0
    #         for j in name_freq_pre2[i.title]:
    #             cell1 = letters[count] + str(1)
    #             i[cell1] = 'Neuron' + str(count)
    #             count2 = 2
    #
    #             for k in name_freq_pre2[i.title][j]:
    #                 cell = letters[count] + str(count2)
    #                 i[cell] = k
    #                 count2 += 1
    #                 if max1 < count2:
    #                     max1 = count2
    #
    #             count2 += 1
    #             i['A' + str(count2)] = "Postinfusion"
    #
    #             for k in name_freq_post2[i.title][j]:
    #                 cell = letters[count] + str(count2)
    #                 i[cell] = k
    #                 count2 += 1
    #                 if max1 < count2:
    #                     max1 = count2
    #
    #
    #             count += 1
    #         max.append(max1)
    #     print(max)
    #
    #
    #
    #
    #
    #     wb.save(r'C:\Users\Ayaan\Desktop\Lab-Data\Excel\Odor Activity.xlsx')

    ####################################################################################################################
    # count = 2
    # sum = []
    # for i in neurons:
    #     cell = 'A' + str(count)
    #     ws[cell] = 'Neuron_' + str(count - 1)
    #     count += 1
    #
    # count = 0
    # temp = name_freq_pre2.keys()
    # for i in temp:
    #     cell = letters[count + 1] + '1'
    #     ws[cell] = str(i)
    #     count += 1
    #
    # count = 1
    # for i in name_freq_pre2:
    #     count2 = 2
    #     char = letters[count]
    #     for j in name_freq_pre2[i]:
    #         cell = char + str(count2)
    #         ws[cell] = str(name_freq_pre2[i][j])
    #         count2 += 1
    #     count += 1

    # neuronTimingPrIPrO = {}
    # neuronTimingPrIPO = {}
    # neuronTimingPIPrO = {}
    # neuronTimingPIPO = {}
    #
    # count = 1
    #
    # for o in OdorList:
    #     neuronTimingPrIPrO[o] = {}
    #     neuronTimingPrIPO[o] = {}
    #     neuronTimingPIPrO[o] = {}
    #     neuronTimingPIPO[o] = {}
    #     count1 = 1
    #     for n in neurons:
    #         name = "neuron_" + str(count1)
    #         neuronTimingPrIPrO[o][name] = []
    #         neuronTimingPrIPO[o][name] = []
    #         neuronTimingPIPrO[o][name] = []
    #         neuronTimingPIPO[o][name] = []
    #         count1 += 1
    #
    # for o in neuronTimingPrIPrO:
    #     count = 1
    #     for n in neurons:
    #         name = "neuron_" + str(count)
    #
    #         for b in binTimingsPre:
    #             for binT in range(0, len(b[1]) - 1):
    #                 lengthPrIPrO = 0
    #                 lengthPIPrO = 0
    #
    #                 for n1 in n:
    #                     if b[1][binT] < n1 < b[1][binT + 1] and b[0] == str(o)[2:-1]:
    #                         if n1 < splitn:
    #                             lengthPrIPrO += 1
    #                         else:
    #                             lengthPIPrO += 1
    #
    #                 if b[0] == str(o)[2:-1]:
    #                     neuronTimingPrIPrO[o][name].append(lengthPrIPrO)
    #                 if b[0] == str(o)[2:-1]:
    #                     neuronTimingPIPrO[o][name].append(lengthPIPrO)
    #
    #         for b in binTimingsPost:
    #             for binT in range(0, len(b[1]) - 1):
    #                 lengthPrIPO = 0
    #                 lengthPIPO = 0
    #
    #                 for n1 in n:
    #                     if b[1][binT] < n1 < b[1][binT + 1] and b[0] == str(o)[2:-1]:
    #                         if n1 < splitn:
    #                             lengthPrIPO += 1
    #                         else:
    #                             lengthPIPO += 1
    #
    #                 if b[0] == str(o)[2:-1]:
    #                     neuronTimingPrIPO[o][name].append(lengthPrIPO)
    #                 if b[0] == str(o)[2:-1]:
    #                     neuronTimingPIPO[o][name].append(lengthPIPO)
    #
    #         count += 1

    #
    # for i in neuronTimingPrIPrO:
    #     for j in neuronTimingPrIPrO[i]:
    #         sum1 = sum(neuronTimingPrIPrO[i][j])
    #         neuronTimingPrIPrO[i][j] = sum1
    #
    # for i in neuronTimingPIPrO:
    #     for j in neuronTimingPIPrO[i]:
    #         sum1 = sum(neuronTimingPIPrO[i][j])
    #         neuronTimingPIPrO[i][j] = sum1
    #
    # for i in neuronTimingPrIPO:
    #     for j in neuronTimingPrIPO[i]:
    #         sum1 = sum(neuronTimingPrIPO[i][j])
    #         neuronTimingPrIPO[i][j] = sum1
    #
    # for i in neuronTimingPIPO:
    #     for j in neuronTimingPIPO[i]:
    #         sum1 = sum(neuronTimingPIPO[i][j])
    #         neuronTimingPIPO[i][j] = sum1
