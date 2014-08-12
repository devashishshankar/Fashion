import operator

__author__ = 'devashish.shankar'

import cv2
import numpy as np
import csv
import os

'''
This code trains a kdt into an object 'kdt'

Input data format:
In the current directory keep directories by store names. In each directory keep the image file along with the skeleton CSV as a .txt file

Skeleton CSV: A CSV file with format: tag,x1,x2,y1,y2

Currently supported tags:
['neck', 'Left_shoulder', 'Right_shoulder', 'Upper_body',
                                                       'Middle_body', 'Lower_body', 'Right_hand', 'Lower_body_right',
                                                       'Right_wrist', 'Left_hand', 'Left_wrist']

Current TODOs:
-> Move parsing functions in a common util file
-> Move display functions in a common util file

'''




#Will return a mask
def getMask(img, coor):
    print coor
    mask = np.uint8(np.zeros(img.shape))
    for i in range(int(coor[0].strip()), int(coor[1].strip())):
        for j in range(int(coor[2].strip()),int(coor[3].strip())):
            mask[i][j] = 1
    return mask

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

#Calculate dense sift vector for an image given labels
def getHistogramVector(imgPath,labels,featureDetectorLabel):
    print "Getting HV for ",imgPath
    img = cv2.imread(imgPath)
    gray= cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    csvFile = imgPath+".txt"
    masks = []
    if labels == None:
        mask = np.ones(gray.shape)
        masks.append(mask)
    else:
        for label in labels:
            coor = getLabelCoordinatesFromCSV(csvFile, label)
            if coor == None:
                print "Returning None from gethv"
                return None
            mask = getMask(gray, coor)
            masks.append(mask)
    # print img.shape
    # print gray.shape
    # print mask.shape
    mHistogram = []
    for mask in masks:
        featDetector = cv2.FeatureDetector_create(featureDetectorLabel)
        kp =  featDetector.detect(gray,mask=mask)
        sift = cv2.SIFT()
        k,desc = sift.compute(gray,kp)
        if(desc == None):
            return None
        histogram = getConcatenatedHistogram(desc)
        mHistogram.extend(histogram)
    if(len(mHistogram) % 32768 == 0):
        return mHistogram
    else:
        return None

def getConcatenatedHistogram(desc):
    histogram = []
    for i in desc.transpose():
        histogram.extend(normalize(getHistogram(i)))
    return histogram

def getHistogram(desc):
    return np.bincount(desc.astype(int).flatten(),minlength=256)

def normalize(l):
    l = l.astype(float)
    summ = sum(l)
    #print "sum",summ
    for i in range(len(l)):
        l[i] = (float(l[i])/float(summ))
    return l


def displayImage(category,resImage):
    resPath = category+"/"+resImage
    print category,resImage
    img = cv2.imread(resPath)
    cv2.imshow(resPath,img)
    cv2.waitKey(2000)


def displayImageWithBox(hist,category,resImage):
    resPath = category+"/"+resImage
    coor = hist[category][resImage]
    print category,resImage
    img = cv2.imread(resPath)
    cv2.rectangle(img, (int(coor[2].strip()), int(coor[0].strip())), (int(coor[3].strip()), int(coor[1].strip())), (0, 255, 0), 2)
    cv2.imshow(resPath,img)
    cv2.waitKey(2000)





def analyseKDResult(hist,index,cat,imgName):
    print "Query image:"
    displayImage(cat,imgName)
    distance,points = kdt.query(hist[cat][imgName], k=20, return_distance=True)
    print points,distance
    i = 0
    for point in points[0]:
        print "Result #",i
        imgTuple = index[point]
        category = imgTuple[0]
        resImage = imgTuple[1]
        displayImage(category,resImage)
        i+=1


def getCategoryToImageToHist():
    categoryToImageToHist = {}
    partToCategoryNameToHist = {}
    categoryToImageToCoor = {}
    for root, dirnames, filenames in os.walk(os.getcwd()):
        for filename in filenames:
            if (not ".json" in filename) and (not ".txt" in filename) and (not ".DS_Store" in filename):
                dirName = root.split('/')[len(root.split('/')) - 1]
                print dirName, filename
                if not dirName in categoryToImageToHist:
                    categoryToImageToHist[dirName] = {}
                    categoryToImageToCoor[dirName] = {}
                imageFileName = dirName + "/" + filename
                if (not os.path.isfile(imageFileName)):
                    continue
                if (not os.path.isfile(imageFileName + ".txt")):
                    continue
                histogram_vector = getHistogramVector(imageFileName,
                                                      ['neck', 'Left_shoulder', 'Right_shoulder', 'Upper_body',
                                                       'Middle_body', 'Lower_body', 'Right_hand', 'Lower_body_right',
                                                       'Right_wrist', 'Left_hand', 'Left_wrist'], 'Dense')
                # print "histogram_vector",histogram_vector
                if not histogram_vector == None:
                    categoryToImageToHist[dirName][filename] = histogram_vector
    return categoryToImageToHist


#KD TREE

def getKDDFromHistogram(hist):
    catalogue = np.zeros(32768 * 11)
    index = {}
    i = 1
    for cat in hist.keys():
        for img in hist[cat]:
            catalogue = np.vstack((catalogue, hist[cat][img]))
            index[i] = (cat, img)
            i = i + 1
    from sklearn.neighbors import KDTree
    kdt = KDTree(catalogue, leaf_size=30, metric='euclidean')
    return kdt,index


if __name__=="__main__":
    hist = getCategoryToImageToHist()
    kdt,index = getKDDFromHistogram(hist)
    print "KDT trained"
    analyseKDResult(hist,index,'Blazers','BZRDG3FAKTCYTHGX_1100x1360.jpeg')
    analyseKDResult(hist,index,'Kurtas','KTADPSWY8N7KNCTT_1100x1360.jpeg')


