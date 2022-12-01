"""
These are the definitions/classes for the main.py
associated with this macro.

-Skipper Kagamaster
skk317@lehigh.edu
"""

import numpy as np
import pandas as pd
import uproot as up
import os
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter as sgf
from scipy.signal import argrelextrema as arex
from scipy.stats import moyal
from scipy.optimize import curve_fit
from matplotlib.backends.backend_pdf import PdfPages


def back_convert(a):
    """This will convert from [ew, pp, tt] to tile #."""
    pos = 372*a[0]+12*a[1]+a[2]
    return pos


def epd_tile(a):
    """This will convert from tile ID to [ew pp tt] format.
    TODO Test this function and see what breaks (not sure it works properly right now)."""
    ew = (a / 372).astype(int)
    pp = ((a - 372 * ew) / 31 + 1).astype(int)
    tt = ((a % 31) + 1).astype(int)
    return np.asarray((ew, pp, tt)).T


class ADCSpectra:
    """This builds the ADC spectra. """

    def __init__(self, data: bool) -> None:
        """This just defines the variables we'll be using
        in the class."""
        self.data: bool
        self.adc = None
        self.smooth_adc = None
        self.adc_max = None
        self.adc_max_mean = None
        self.adc_argmax = None
        self.adc_extrema = None
        self.tile_names = None
        self.ped_tiles = None
        self.ped_tiles_loc = None

    def import_data(self, data_in):
        """This imports the data. You must have the latest versions
        of uproot and awkward installed on your machine (uproot4 and
        awkward 1.0 as of the time of this writing).
        Use: pip install uproot awkward  """
        adc_data = up.open(data_in)
        self.adc = []
        for i in adc_data.keys():
            self.adc.append(adc_data[i].values())
        self.adc = np.asarray(self.adc)
        self.adc_max = np.max(self.adc, axis=1)
        self.adc_max_mean = np.mean(self.adc_max)
        self.adc_argmax = np.argmax(self.adc, axis=1)
        self.tile_names = epd_tile(np.linspace(0, len(self.adc_max)-1, len(self.adc_max)))
        self.smooth_adc = sgf(sgf(sgf(self.adc, 141, 5), 71, 3), 51, 2)

    def ped_find(self):
        """This finds the maximum values in the spectra, given that it's:
        -Greater than 10 ADC
        -Max value (not position) is > 0.3 times the mean value, to avoid
        places where the pedestal was well subtracted and the maximum is
        thus dominated by the 1st MIP MPV (or 2nd/3rd, for higher energies
        and inner tiles)"""
        ped_index_1 = np.hstack(np.where(self.adc_argmax > 10))
        ped_index_2 = np.hstack(np.where(self.adc_max > 0.3*self.adc_max_mean))
        u, c = np.unique(np.hstack((ped_index_1, ped_index_2)), return_counts=True)
        self.ped_tiles_loc = u[c > 1]
        self.ped_tiles = self.tile_names[self.ped_tiles_loc]
        print("This is from ped_find (self.ped_tiles_loc):", self.ped_tiles_loc)
        print("This is from ped_find (self.ped_tiles):", self.ped_tiles)

    def ped_fix(self):
        """"""
        ped_index_1 = np.hstack(np.where(self.adc_argmax > 10))
        ped_index_2 = np.hstack(np.where(self.adc_max > 0.3 * self.adc_max_mean))
        u, c = np.unique(np.hstack((ped_index_1, ped_index_2)), return_counts=True)
        self.ped_tiles_loc = u[c > 1]
        for i in range(len(self.adc[self.ped_tiles_loc])):
            x = self.ped_tiles_loc[i]
            n = len(self.adc[x][self.adc_argmax[x]:])
            m = len(self.adc[x])
            self.adc[x] = np.pad(self.adc[x][self.adc_argmax[x]:], (0, m-n), 'constant')
            self.smooth_adc[x] = sgf(sgf(sgf(self.adc[x], 141, 5), 71, 3), 51, 2)

    #def ped_plot(self, day, folder=r'C:\PhysicsProcessing'):
    def ped_plot(self, day, folder="/mnt/c/Users/pjska/service/2020_11p5GeV/EpdCalibration/data/"):
        """This will show where pedestal shifts (or other, similar type spikes) were
        found. Inspect the resulting *.pdf to ensure they are indeed pedestal shifts
        (which should be obvious, if so)."""
        r = np.ceil(np.sqrt(len(self.ped_tiles))).astype(object)
        ped_len = int(len(self.ped_tiles))
        #save_place = folder+r'\nMIP_ped_probs_{}.pdf'.format(day)
        save_place = folder+'nMIP_ped_probs_{}.pdf'.format(day)
        print("This is from ped_plot (self.ped_tiles):", self.ped_tiles)
        with PdfPages(save_place) as export_pdf:
            fig, ax = plt.subplots(int(r), int(r), figsize=(16, 10), constrained_layout=True)
            for i in range(int(r)):
                for j in range(int(r)):
                    x = int(i*int(r) + j)
                    if x >= ped_len:
                        ax[i, j].set_axis_off()
                        if x is ped_len:
                            legend_master = ["ADC Spectra", "ADC Smoothed"]
                            color = ["black", "red"]
                            for t in range(int(len(color))):
                                ax[i, j].plot(0)
                            leg = ax[i, j].legend(legend_master, fontsize=10)
                            count = 0
                            for line in leg.get_lines():
                                line.set_linewidth(2)
                                line.set_color(color[count])
                                count += 1
                        if x is ped_len+1:
                            ax[i, j].text(
                                0, 0, "Day {}".format(day), size=40)
                    else:
                        index = self.ped_tiles_loc[x]
                        title = str(self.tile_names[index])
                        ax[i, j].plot(self.adc[index], lw=2,
                                      c="black", label="ADC Spectrum")
                        ax[i, j].plot(self.smooth_adc[index], lw=1,
                                      c="red", label="Smooth ADC Spectrum")
                        # ax[i, j].axvline(self.adc_argmax[index])
                        ax[i, j].set_xlim(0, 250)
                        ax[i, j].set_xlabel("ADC", fontsize=10)
                        ax[i, j].set_ylabel("Counts", fontsize=10)
                        ax[i, j].set_title(title)
            if np.power(r, 2) is ped_len:
                plt.suptitle("Day {}".format(day))
            export_pdf.savefig()
            plt.close()

    #def plot_ped_locs(self, day, folder=r'C:\PhysicsProcessing'):
    def plot_ped_locs(self, day, folder="/mnt/c/Users/pjska/service/2020_11p5GeV/EpdCalibration/data/"):
        """This shows the location of the max ADC positions for all supersectors,
        whether or not they have a shifted pedestal. Values under 10 ADC should
        be about normal for the spectra; any greater and that will have to be
        accounted for."""
        save_place = folder + r'\nMIP_maxes_{}.pdf'.format(day)
        with PdfPages(save_place) as export_pdf:
            fig, ax = plt.subplots(6, 4, figsize=(16, 10), constrained_layout=True)
            for i in range(6):
                for j in range(4):
                    x = 4*i + j
                    ew = 'E'
                    if x > 11:
                        ew = 'W'
                    ax[i, j].plot(self.adc_argmax[31*x:31*(x+1)])
                    ax[i, j].set_title("{} PP {}".format(ew, (x+1 - 12 % (x+1))))
                    ax[i, j].set_xlabel("TT")
                    ax[i, j].set_ylabel("Max ADC count")
            plt.suptitle("Day {}".format(day))
            export_pdf.savefig()
            plt.close()

    #def adc_plot(self, day, folder=r'C:\PhysicsProcessing'):
    def adc_plot(self, day, folder="/mnt/c/Users/pjska/service/2020_11p5GeV/EpdCalibration/data/"):
        """This plots the ADC spectra and the smoothed spectra found via a
        Savitzky-Golay filtering process.
        TODO Add in the start for a fit and 1st MIP MPV guess (which can be found automatically)
        TODO Optimise this portion (it's ridiculously slow right now)."""
        save_place = folder+r'\ADC_pedshifted_{}.pdf'.format(day)
        with PdfPages(save_place) as export_pdf:
            for ew in range(2):
                for pp in range(12):
                    fig, ax = plt.subplots(5, 7, figsize=(16, 10), constrained_layout=True)
                    print("working on Day {} EW{} PP{}".format(day, ew, pp + 1))
                    for i in range(5):
                        for j in range(7):
                            tt = i*7 + j
                            x = back_convert([ew, pp, tt])
                            if tt >= 31:
                                ax[i, j].set_axis_off()
                                if x is 31:
                                    legend_master = ["ADC Spectra", "ADC Smoothed"]
                                    color = ["black", "red"]
                                    for t in range(int(len(color))):
                                        ax[i, j].plot(0)
                                    leg = ax[i, j].legend(legend_master, fontsize=10)
                                    count = 0
                                    for line in leg.get_lines():
                                        line.set_linewidth(2)
                                        line.set_color(color[count])
                                        count += 1
                                if x is 32:
                                    ax[i, j].set_title("EW {} PP {}".format(ew, pp+1),
                                                       fontsize=30)
                            else:
                                ax[i, j].plot(self.adc[x][40:400], lw=2, c="black")
                                ax[i, j].plot(self.smooth_adc[x][40:400], lw=1, c="red")
                                ax[i, j].set_title("TT {}".format(tt+1))
                    # plt.suptitle("EW{} PP{}".format(ew, pp))
                    export_pdf.savefig()
                    plt.close()
