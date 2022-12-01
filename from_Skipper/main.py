"""The purpose of this code is to find "spikes" in ADC spectra,
which are indicative of pedestal shifts or some other data
anomoly. spikes.py holds the definitions/classes to be run in
this macro. Set the folder and days (day_set) you want to look
over. You may also, of course, tweak this to run over runs
instead of days.

You will have to have uproot and awkward installed for this to
run; versions as of this writing are uproot 4 and awkward 1.0.

-Skipper Kagamaster
skk317@lehigh.edu
"""

import spikes
import numpy as np
import os
import matplotlib.pyplot as plt

# arr = spikes.ADCSpectra(True)
# arr.import_data(r"C:\PhysicsProcessing\7.7GeV\2125.root")
# arr.adc_plot(25, r"C:\PhysicsProcessing\7.7GeV")
# print("All done!")

#folder = r"C:\PhysicsProcessing\run_files"
folder = "/mnt/c/Users/pjska/service/2020_11p5GeV/EpdCalibration/data/"
os.chdir(folder)
# day_set = np.asarray((31, 32, 33, 34, 35, 36, 37))
day_set = np.asarray((1, 2))
spectra = []

print("Getting spectra for day:")
for i in range(len(day_set)):
    print(day_set[i])
    try:
        print("Importing data.")
        spectra.append(spikes.ADCSpectra(True))
        spectra[i].import_data(folder + r"\0{}.root".format(day_set[i]))
        print("Finding pedestal shifts.")
        spectra[i].ped_find()
        spectra[i].plot_ped_locs(day_set[i], folder)
        print("Plotting tiles with pedestal shifts.")
        spectra[i].ped_plot(day_set[i], folder)
        # TODO Make the below actually, you know, work.
        # print("Resetting ADCs with pedestals subtracted.")
        # spectra[i].ped_fix()
        # print("Plotting reset ADC spectra.")
        spectra[i].adc_plot(day_set[i], folder)
    except Exception as e:  # For any issues that might pop up.
        print("Darn it!", e.__class__, "occurred on day", day_set[i])
        continue

# The below was for when I was running over Runs, not Days.
# TODO Integrate this in the code so it's not so ad hoc.

#folder = r"C:\PhysicsProcessing\run_files"
os.chdir(folder)
count = 0
print("Working on file")
for i in os.listdir():
    print(count, "of", len(os.listdir()))
    try:
        spectra.append(spikes.ADCSpectra(True))
        spectra[count].import_data(i)
        spectra[count].ped_find()
        spectra[count].plot_ped_locs(i)
        spectra[count].ped_plot(i)
    except Exception as e:  # For any issues that might pop up.
        print("Darn it!", e.__class__, "occurred in run", i)
        count += 1
        continue
    count += 1
