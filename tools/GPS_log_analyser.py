# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 11:03:07 2019

@author: benes
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import signal
from scipy.stats import norm

LANG = "DE"
DF=pd.read_csv('data/timing0_7.log',sep=';',skiprows=range(1,5))

splipostion = np.array([2702,16896])
#splipostion = np.array([])
for i in np.arange(splipostion.size):
    DF["unix_time_nsecs"][splipostion[i] :]+=100
DF["nSecDev"] = DF["unix_time_nsecs"] - DF["unix_time_nsecs"][0]
#remove glitches more than 0.1 ms deviation
DF.drop(DF.index[DF['nSecDev'] < -100000], inplace = True)
DF.drop(DF.index[DF['nSecDev'] > 100000], inplace = True)
DF["nSecDev"] = DF["unix_time_nsecs"] - DF["unix_time_nsecs"][0] - np.mean(DF["nSecDev"])
AK = signal.correlate(DF["nSecDev"], DF["nSecDev"], mode="same")

fig1, ax1 = plt.subplots()
if LANG == "EN":
    nSecDevLabel = r"time deviation $t_{(is)}-t_{(shold)}$"
    uncerLabel = "Measurement uncertainty $u$"
if LANG == "DE":
    nSecDevLabel = r"Zeitabweichung $t_{(ist)}-t_{(soll)}$"
    uncerLabel = "Messunsicherheit $u$"
ax1.plot(DF["time_uncertainty"], color="C1", label=uncerLabel)
ax1.plot(-DF["time_uncertainty"], color="C1")
ax1.plot(DF["nSecDev"], color="C0", label=nSecDevLabel)
if LANG == "EN":
    ax1.set_ylabel(r"time deviation $t_{(is)}-t_{(should)}$in ns")
    ax1.set_xlabel("Time in s")
    ax1.set_title("Timingdeviation PTB PPS signal stamped with Data aqusition unit")
if LANG == "DE":
    ax1.set_ylabel(r"Zeitabweichung $t_{(ist)}-t_{(soll)}$ in ns")
    ax1.set_xlabel("Zeit in s")
    ax1.set_title(
        "Abweichung der zeitgestempelten PTB PPS Signale nach Zeitstemplung durch DAQ Hardware"
    )
ax1.grid(True)
ax1.legend()
fig1.show()
DF["inRange"] = (abs(DF["nSecDev"]) <= (DF["time_uncertainty"])).astype(int)
coverage = np.mean(DF["inRange"])
print("uncertantiy coverage is " + str(coverage * 100) + " %")

# best fit of data
(mu, sigma) = norm.fit(DF["nSecDev"])

bincount = int(DF["nSecDev"].max() - DF["nSecDev"].min())
fig2, ax2 = plt.subplots()
# the histogram of the data
n, bins, patches = ax2.hist(
    DF["nSecDev"], bincount, density=1, facecolor="green", alpha=0.75
)

# add a 'best fit' line
y = norm.pdf(bins, mu, sigma)

ax2.plot(bins, y, "r--", linewidth=2)

# plot
if LANG == "EN":
    ax2.set_xlabel("time deviation $t_{(is)}-t_{(should)}$in ns")
    ax2.set_ylabel("Frequency ")
    ax2.set_title(
        r"$\mathrm{Histogram\ of\ time deviation:}\ 2\sigma=%.3f ~ns,\ \sigma = %.3f$ ~ns n = $%i$"
        % (2 * sigma, sigma, DF["nSecDev"].size)
    )
if LANG == "DE":
    ax2.set_xlabel("Zeitabweichung $t_{(ist)}-t_{(soll)}$ in ns")
    ax2.set_ylabel("Häufigkeit")
    ax2.set_title(
        r"$\mathrm{Histogram~der~Zeitabweichungen:} \sigma = %.3f$ ns ,n = $%i$"
        % (sigma, DF["nSecDev"].size)
    )
ax2.grid(True)

fig2.show()


