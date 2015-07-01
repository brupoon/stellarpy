# -*- coding: utf-8 -*-
"""
stellarPY
@file: tests
@author: Brunston Poon
@org: UH-IFA / SPS
"""

import stellar as st
import debug as de
import numpy as np

blah = input("0 for actual, 1 for sample> ")
if blah == "0":
    file = 'IMG_2860.tif'
    fileArray = st.converter(file)
    cropped = st.crop(fileArray)
    st.restorer(cropped)
    distribution = st.pixelDistribution(cropped)
    intensity = st.intensity(cropped)
    st.plotGraph(intensity)
# writeLogToFile(fileArray,'log.log')
if blah == "1":
    test = de.testArray() #will print out the array generated.
    # sums = st.sumGenerator(test)
    # print(sums)
    cropped = st.crop(test)
    print("duplicate returned from crop():\n", cropped)
