##################################
#encoding=utf8                   #
#version =py27, py33             #
#author  =sanhe                  #
#date    =2014-10-29             #
#                                #
#    (\ (\                       #
#    ( -.-)o    I am a Rabbit!   #
#    o_(")(")                    #
#                                #
##################################

"""
Import:
    from HSH.DataSci.knn_classifier import dist, knn_find
"""

from __future__ import print_function
from sklearn.neighbors import DistanceMetric
from sklearn.neighbors import NearestNeighbors
from sklearn.neighbors import KNeighborsClassifier
from sklearn import preprocessing
from geopy.distance import vincenty
import numpy as np

def earthdist(coordinate1, coordinate2): # latitude, longitude earth surface distance
    return vincenty( (coordinate1[0], coordinate1[1]), 
                     (coordinate2[0], coordinate2[1]) ).miles

def dist(X, Y, distance_function = "euclidean"):
    """calculate X, Y distance matrix
    [Args]
    ------
    X : m samples
    Y : n samples
    distance_function : user_defined distance
    
    [Returns]
    ---------
    distance_matrix: n * m distance matrix
    
    
    we have those built-in function. Default = euclidean
    
    "euclidean"    EuclideanDistance    sqrt(sum((x - y)^2))
    "manhattan"    ManhattanDistance    sum(|x - y|)
    "chebyshev"    ChebyshevDistance    sum(max(|x - y|))
    "minkowski"    MinkowskiDistance    sum(|x - y|^p)^(1/p)
    "wminkowski"    WMinkowskiDistance    sum(w * |x - y|^p)^(1/p)
    "seuclidean"    SEuclideanDistance    sqrt(sum((x - y)^2 / V))
    "mahalanobis"    MahalanobisDistance    sqrt((x - y)' V^-1 (x - y))
    """
    distance_calculator = DistanceMetric.get_metric(distance_function)
    return distance_calculator.pairwise(X, Y)

def knn_find(train, test, k = 2):
    """find first K knn neighbors of test samples from train samples
    
    [Args]
    ----
    train: train data {array like, m x n, m samples, n features}
        list of sample, each sample are list of features.
        e.g. [[age = 18, weight = 120, height = 167],
              [age = 45, weight = 180, height = 173],
              ..., ]
        
    test: test data {array like, m x n, m samples, n features}
        data format is the same as train data
    
    k: number of neighbors
        how many neighbors you want to find
        
    [Returns]
    -------
    distances: list of distance of knn-neighbors from test data
        [[dist(test1, train_knn1), dist(test1, train_knn2), ...],
         [dist(test2, train_knn1), dist(test2, train_knn2), ...],
         ..., ]
    
    indices: list of indice of knn-neighbors from test data
        [[test1_train_knn1_index, test1_train_knn2_index, ...],
         [test2_train_knn1_index, test2_train_knn2_index, ...],
         ..., ]    
    """
    nbrs = NearestNeighbors(n_neighbors=k, algorithm="kd_tree").fit(train) # default = "kd_tree" algorithm
    return nbrs.kneighbors(test)

def prep_standardize(train, test, enable_verbose = False):
    """pre-processing, standardize data by eliminating mean and variance
    """
    scaler = preprocessing.StandardScaler().fit(train) # calculate mean and variance
    train = scaler.transform(train) # standardize train
    test = scaler.transform(test) # standardize test
    if enable_verbose:
        print("mean = %s" % scaler.mean_)
        print("var = %s" % scaler.std_)
    return train, test

def knn_classify(train, train_label, test, k=1, standardize=True):
    """classify test using KNN (k=1) algorithm
    
    usually the KNN classifier works good if all the features of the train
    data are continual value
    
    [Args]
    ------
    train: train data (see knn_find), {array like, m x n, m samples, n features}
    
    train_label: train data's label, {array like, m x n, m samples, n features}
    
    test: test data
    
    k: knn classify value
    
    standardize: remove mean and variance or not
    
    [Returns]
    ---------
    test_label: test data's label
    
    [Notice]
    --------
        The sklearn.neighbors.KNeighborsClassifier doesn't do pre-processing
        this wrapper provide an option for that
    """
    if standardize:
        train, test = prep_standardize(train, test) # eliminate mean and variance
    neigh = KNeighborsClassifier(n_neighbors=k) # knn classifier
    neigh.fit(train, train_label) # training
    return neigh.predict(test) # classifying

def knn_impute(train, k):
    """nearest neighbor data imputation algorithm
    [Args]
    ------
    train: data set with missing value, {array like, m x n, m samples, n features}
    
    k: use the first k nearest neighbors' mean to fill the missing-value cell
    
    [Returns]
    ---------
    train: with filled missing value
    
    """
    for i in np.where(np.isnan(train).sum(axis=1)!=0)[0]: # for the row has NA value
        sample = train[i] # i = row index, sample = ith sample in train
        na_col_ind, usable_col_ind = (np.where(np.isnan(sample) )[0], # NA value column index
                                      np.where(~np.isnan(sample))[0]) # Non-NA value column index 
        usable_row_ind = np.where(np.isnan(train[:, usable_col_ind]).sum(axis=1)==0)[0]
                             # Non-NA row index if in Non-NA value column index has no NA value
        
        sub_train = train[np.ix_(usable_row_ind, usable_col_ind)] # select sub data set
        scaler = preprocessing.StandardScaler().fit(sub_train) # find the mean and var to remove
        
        if k**2 > sub_train.shape[0]: # usually to ensure we have more than k non-va value 
            potential_k = sub_train.shape[0] # we have to find k**2 nearest neighboor
        else:
            potential_k = k ** 2
              
        _, indices = knn_find(scaler.transform(sub_train), # standardize
                              scaler.transform(sample[usable_col_ind][np.newaxis]), # standardize
                              potential_k)
 
        candidates = train[np.ix_(usable_row_ind[indices[0]], na_col_ind)].T
         
        for j, candidate in enumerate(candidates): # use the average of first k non-NA value 
            train[(i, na_col_ind[j])] = candidate[~np.isnan(candidate)][:k+1].mean()
    
    return train

if __name__ == "__main__":
    def dist_UT():
        train, test = ([[27.8, -124.3]], 
                       [[34.1, -127.5]])
        
        distances = dist(train, test, earthdist)
        print("=== distance matrix ===\n%s\n" % distances)
        
    dist_UT()