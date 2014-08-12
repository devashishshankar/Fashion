import operator

__author__ = 'devashish.shankar'

import cv2
import numpy as np
import csv
import os

min_YCrCb = np.array([0,133,77],np.uint8)   #[0,133,77],

max_YCrCb = np.array([255,173,127],np.uint8)   #[255,173,127]

def getSkinRatioFeature(img,coor):
    if(coor == None):
        return
    imageYCrCb = cv2.cvtColor(img,cv2.COLOR_BGR2YCR_CB)
    skinRegion = cv2.inRange(imageYCrCb,min_YCrCb,max_YCrCb)
    #print "sum of skinRegion",sum(skinRegion)
    #print "coor",coor
    c = skinRegion[int(coor[0].strip()):int(coor[1].strip()),int(coor[2].strip()):int(coor[3].strip())]
    #print "sum of c",sum(c)
    binc = np.bincount(c.flatten())
    #print "skinRegion",skinRegion
    #print "c",c
    #print "binc",binc,len(binc),binc[0]
    if len(binc) == 1:
        skinCount = 0.000
    else:
        skinCount=binc[255] + 0.00
    print "skinCount",skinCount
    print "total",(skinCount+binc[0])
    ratio = skinCount/(skinCount+binc[0])
    print "ratio, ",ratio
    return ratio


#PARSE CSV
def parseCSVFile(csvFile):
    imageDict = {}
    with open(csvFile, 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            if(len(row)>2):
                imageDict[row[0]] = row[1:5]
    return imageDict



#Return 4 coordinates
def getLabelCoordinatesFromCSV(csvFile, label):
    imageDict = parseCSVFile(csvFile)
    print imageDict
    if label in imageDict:
        return imageDict[label]
    else:
        print "Returning None"
        return None



def getSkinRatioFeatures(imgPath):
    img = cv2.imread(imgPath)
    feat = []
    feat.append(getSkinRatioFeature(img,getLabelCoordinatesFromCSV(imgPath+'.txt','Right_shoulder')))
    feat.append(getSkinRatioFeature(img,getLabelCoordinatesFromCSV(imgPath+'.txt','Left_shoulder')))
    feat.append(getSkinRatioFeature(img,getLabelCoordinatesFromCSV(imgPath+'.txt','Right_hand')))
    feat.append(getSkinRatioFeature(img,getLabelCoordinatesFromCSV(imgPath+'.txt','Left_hand')))
    feat.append(getSkinRatioFeature(img,getLabelCoordinatesFromCSV(imgPath+'.txt','Right_wrist')))
    feat.append(getSkinRatioFeature(img,getLabelCoordinatesFromCSV(imgPath+'.txt','Left_wrist')))
    return feat

import sys

#Gets skin features from CWD
def getSkinFeaturesAsCSV():
    global featD, root, dirnames, filenames, filename, dirName, imageFileName, feat, i, j, f
    featD = {}
    for root, dirnames, filenames in os.walk(os.getcwd()):
        for filename in filenames:
            if (not ".json" in filename) and (not ".txt" in filename) and (not ".DS_Store" in filename):
                dirName = root.split('/')[len(root.split('/')) - 1]
                print dirName, filename
                imageFileName = dirName + "/" + filename
                if (not os.path.isfile(imageFileName)):
                    continue
                if (not os.path.isfile(imageFileName + ".txt")):
                    continue
                sys.stdout.write(imageFileName + ",")
                feat = getSkinRatioFeatures(imageFileName)
                featD[imageFileName] = feat
    print featD
    print "len ", len(featD)
    for (i, j) in featD.iteritems():
        sys.stdout.write(str(i) + ",")
        for f in j:
            # print feat
            sys.stdout.write(str(f) + ",")
            sys.stdout.flush()
        print

