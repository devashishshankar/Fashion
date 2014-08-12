Fashion
=======

An image processing module to recognize style of users based on his images/ selfies.

Current approach:
1) Run skeleton identification on each image
2) Put the skeleton csv (bodyPart,x1,x2,y1,y2) in a text file with the image in dataset (Code not committed)
3) Calculate dense SIFT features for selected bounding box for each image
4) Store the BOW histogram of the SIFT features for each image as a vector (This vector has a fixed size unlike SIFT keypoints)
5) Index the vectors obtained in above step into a KD tree
5) For the query image, compute vector using 1-4 and query KD tree with the obtained vector


Note: This code is V0 and under developement
