# -*- coding: utf-8 -*-
"""
stellarPY
@file: primary
@author: Brunston Poon
@org: UH-IFA / SPS
@namingConvention: lowerCamelCase
"""

import numpy as np
import math
from scipy import ndimage
from PIL import Image
from matplotlib import pyplot as plt
import pdb
import sys

"""
figure 0: pixelDistribution
figure 1: intensity
figure 2: regression from spectrum against points
"""

def converter(imageToConvert):
    """
    Converts image given in filepath format as tif to a numpy array and returns
    """
    #note- for some reason, Lightroom-cropped tif files do not play nice.
    #Use original files.

    image = Image.open(imageToConvert)
    imageArray = np.array(image)

    #troubleshooting statements
    # print("ndarray imageArray:\n", imageArray)
    print("imageArray shape:", imageArray.shape)
    print("imageArray dtype:", imageArray.dtype)

    return imageArray

def restorer(arrayToConvert):
    """
    Converts array given as ndarray to a tif and returns None
    """
    image = Image.fromarray(arrayToConvert)
    image.save("image.tiff", "TIFF")
    return None

def pixelDistribution(data):
    """
    Creates a plot which shows the relative pixel distribution of data given
    in ndarray format so that we can figure out how much "noise" is feasible
    to get rid of without harming the rest of the data
    """
    numRow = len(data)
    numCol = len(data[0])
    distributionArray = np.zeros(766, dtype=np.uint8)
    x = np.arange(765+1)
    for row in range(numRow):
        for col in range(numCol):
            pixelSum = np.sum(data[row][col])
            distributionArray[pixelSum] += 1

    plt.figure(0)
    plt.clf() #clears figure
    plt.plot(x, distributionArray,'b.',markersize=4)
    return distributionArray

def intensity(data,degreeOffset=0):
    """
    Creates an intensity array for the data given in a numpy array. Also allows
    for the insertion of an absolute response function.
    degreeOffset (float) refers to the offset of the data from the horizontal.
    Counter-clockwise (i.e. 'above horizontal') is positive
    Clockwise (i.e. 'below horizontal') is negative
    """
    intensity = []
    if degreeOffset == 0: #i.e. we just want to add vertically
        for k in range(len(data[0])): #goes by column
            vertSlice = data[:,k] # a single column k with all rows
            #print("vertSlice:\n", vertSlice)
            runningTotal = 0
            for pixel in vertSlice:
                for color in pixel:
                    runningTotal = color + runningTotal
            intensity.append(runningTotal)
    intensityNP = np.array(intensity)
    return intensityNP

def intensityP(img, data, regArray):
    """
    Creates a 'proper' intensity array for the data given in a numpy array and
    using an open Image given in img. Degree offset is calculated by a
    y = mx + c function as done in regression()
    regArray = [xvals_n, yvals_n, A, m, c]
    """
    #logging begin
    f = open('log_intensity.txt', 'w')
    sys.stdout = f
    np.set_printoptions(threshold=np.nan)

    xvals_n, yvals_n = regArray[0], regArray[1]
    A, m, c = regArray[2], regArray[3], regArray[4]
    lowerx, lowery, upperx, uppery = img.getbbox()
    sumArray = []
    for xpixel in range(lowerx, upperx):
        #this loop should run across the image by pixel
        sumPerX = 0
        ypixel = m * xpixel + c #we need to floor this value to get a pixel value
        ypixelfi = uppery - math.floor(ypixel) #f=floor, i=inverted
        n = -1/m
        modpixel = xpixel
        while True: #this is the loop which side-walks up
            print("- a pixel from modpixel, value: ", modpixel)
            modpixel -= 1
            if (modpixel) >= 0: #b/c -1 is a valid index
                try:
                    print("doing crossDispersion calculations")
                    crossDispersion = n * (modpixel - xpixel) + ypixel
                    #taken from y - y1 = m(x - x1) which becomes
                    #y = m(x - x1) + y1
                    crossDispersionfi = uppery - math.floor(crossDispersion)
                    print("summing data")
                    sumPerElement = 0
                    for element in data[xpixel][crossDispersionfi]:
                        sumPerElement += element
                    sumPerX += sumPerElement
                    #doing xpixel because the sum is per xpixel on the line...
                except IndexError:
                    print("reached end of image, breaking")
                    break
            else:
                break
        modpixel = xpixel
        while True: #this is the loop which side-walks down
            modpixel += 1
            print("+ a pixel from modpixel, value: ", modpixel)
            try:
                print("doing crossDispersion calculations")
                crossDispersion = n * (modpixel - xpixel) + ypixel
                #taken from y - y1 = m(x - x1) which becomes
                #y = m(x - x1) + y1
                crossDispersionfi = uppery - math.floor(crossDispersion)
                print("summing data")
                sumPerElement = 0
                for element in data[xpixel][crossDispersionfi]:
                    sumPerElement += element
                sumPerX += sumPerElement
            except IndexError:
                print("reached end of image, breaking")
                break
        sumArray.append(sumPerX)
    sumArrayn = np.array(sumArray)
    print("sumArrayn:\n", sumArrayn)

    #logging end
    sys.stdout = sys.__stdout__
    np.set_printoptions(threshold=1000)

    return sumArrayn

def plotIntensityP(intensityP):
    #for element in intensityP:
    pass

def plotGraph(intensity):
    """
    Plots the intensity array generated and returns None
    """
    x = []
    for i in range(len(intensity)):
        #instead of pixel values as is by simply appending 0,1,2, this portion
        #of the function can be set up to use a wavelength-to-pixel ratio.
        x.append(i*1)
    xNP = np.array(x)
    plt.figure(1)
    plt.clf() #clears figure
    plt.plot(xNP, intensity,'b.',markersize=4)
    plt.title("intensity plot, intensity vs wavelength")
    # plt.xlbl("wavelength (nm)")
    # plt.ylbl("intensity (8-bit pixel addition)")
    return None

def sumGenerator(data):
    """
    Creates a 2d matrix of intensity values from a given ndarray data which
    has values in uint8 RGB form
    """
    new = []
    for row in data:
        rowArray = []
        for pixel in row:
            pixelSum = 0
            for value in pixel:
                pixelSum += value
            rowArray.append(pixelSum)
        new.append(rowArray)
    newNP = np.array(new)
    return newNP

def rotate(data, angle):
    """
    Rotates an ndarray data which has already gone through the sumGenerator
    process at an angle (float) given.
    """
    #TODO needs work
    return ndimage.interpolation.rotate(data, angle)

def absResponse(wavelength):
    """
    Would normally have a response function that changes based on the
    wavelength. In this case, a response function has not been found or
    created for the Canon 5D Mk I, so we are using a "response function"
    of 1 across all wavelengths, resulting in no change.
    """
    return 1*wavelength

# def identifyTargetPixels(data):
#     """
#     Identifies target pixels much like the relevant/non-relevant indicator
#     in the crop() function. Takes data as ndarray, uint8
#     """
#     for row in data:
#         for pixel in row:

def regression(img, threshold=127):
    """
    Performs least-squares regression fitting on a given intensityMatrix
    generated using sumGenerator()

    ndarrays are top-left 0,0. To account for this in least-squares regression
    fit, we will use a positional y-value of
    (len of column i.e. numRows) - (y-value )
    """
    #point-gathering code
    lowerx, lowery, upperx, uppery = img.getbbox()
    xvals, yvals = [], []
    for x in range(lowerx, upperx):
        for y in range(lowery, uppery):
            pixel = img.getpixel((x,y))
            if pixel[0]+pixel[1]+pixel[2] > threshold: #intensitymatrix style sum
                xvals.append(x)
                yvals.append(uppery-y) #accounting for upperleft vs lowerleft 0,0
    print(xvals)
    print(yvals)
    #regression code
    xvals_n, yvals_n = np.array(xvals), np.array(yvals)
    A = np.vstack([xvals_n, np.ones(len(xvals_n))]).T
    print("A:\n", A)
    m,c = np.linalg.lstsq(A, yvals_n)[0]
    print("M, C:", m,c)
    return [xvals_n,yvals_n,A,m,c]

def plotRegression(regArray):
    """
    Plots the regression provided against the points provided in the regArray
    """
    x, y, A = regArray[0], regArray[1], regArray[2]
    m, c = regArray[3], regArray[4]


    plt.figure(2)
    plt.clf()
    plt.plot(x, y,'o',label='original data',markersize=4)
    plt.plot(x, m*x + c,'r',linestyle='-', label='fitted line')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.show()

def crop(image,deletionThreshold=127):
    """
    Crops image based on the number of empty pixels [0,0,0]
    Crops top-to-bottom, bottom-to-top, right-to-left, and then left-to-right
    based on the way that the current set of data has been collected.
    """
    duplicate = np.copy(image)
    print("duplicate:\n", duplicate)
    #these get initialized now and updated in each while loop.
    numCol = len(duplicate[0]) #number of columns in image
    numRow = len(duplicate) #number of rows in image
    #cropping from top
    toggleTop = True
    while toggleTop == True:
        numRow = len(duplicate)
        a = 0
        counterPerRow = 0
        for i in range(numCol):
            if not (np.sum(duplicate[a][i]) <= deletionThreshold):
                toggleTop = False
                break
            # if not np.array_equal(duplicate[a][i], np.array([0,0,0])):
            #     toggleTop = False
            #     break
            else:
                counterPerRow += 1
        if counterPerRow == len(duplicate[a]):
            #if the entire row of pixels is empty, delete row
            duplicate = np.delete(duplicate, a, 0)
            print("cropping row:", a)
        # else: #is this else redundant?
        #     #will the first 'if not' catch all that we need to catch?
        #     toggle = False

    print("beginning bottom crop, top ran fine")

    #cropping from bottom
    toggleBot = True
    while toggleBot == True:
        numRow = len(duplicate)
        a = numRow-1
        counterPerRow = 0
        for i in range(numCol):
            if not (np.sum(duplicate[a][i]) <= deletionThreshold):
                toggleBot = False
                break
            # if not np.array_equal(duplicate[a][i], np.array([0,0,0])):
            #     toggleBot = False
            #     break
            else:
                counterPerRow += 1
        if counterPerRow == numCol:
            #if the entire row of pixels is empty, delete row
            duplicate = np.delete(duplicate, a, 0)
            print("cropping row:", a)
        # else: #is this else redundant?
        #     #will the first 'if not' catch all that we need to catch?
        #     toggle = False

    print("beginning right->left crop, bottom ran fine")

    #cropping from right to left
    toggleRight = True
    while toggleRight == True:
        numRow = len(duplicate)
        numCol = len(duplicate[0]) #needs to be updated each time loop iterates
        a = numCol - 1
        counterPerCol = 0
        for i in range(numRow):
            if not (np.sum(duplicate[i][a]) <= deletionThreshold):
                toggleRight = False
                break
            # if not np.array_equal(duplicate[i][a], np.array([0,0,0])):
            #     #note the reverse of the i and a ^^ for vertical crop
            #     toggleRight = False
            #     break
            else:
                counterPerCol += 1
        if counterPerCol == numRow:
            #if the entire col of pixels is empty, delete col
            duplicate = np.delete(duplicate, a, 1)
            print("cropping col:", a)

    print("beginning left->right crop, right->left ran fine")
    #cropping from left to right
    toggleLeft = True
    while toggleLeft == True:
        numRow = len(duplicate)
        numCol = len(duplicate[0]) #needs to be updated each time loop iterates
        a = 0
        counterPerCol = 0
        for i in range(numRow):
            if not (np.sum(duplicate[i][a]) <= deletionThreshold):
                toggleLeft = False
                break
            # if not np.array_equal(duplicate[i][a], np.array([0,0,0])):
            #     #note the reverse of the i and a ^^ for vertical crop
            #     toggleLeft = False
            #     break
            else:
                counterPerCol += 1
        if counterPerCol == numRow:
            #if the entire col of pixels is empty, delete col
            duplicate = np.delete(duplicate, a, 1)
            print("cropping col:", a)

    #troubleshooting
    print("duplicate shape:", duplicate.shape)
    print("duplicate dtype:", duplicate.dtype)

    return duplicate
