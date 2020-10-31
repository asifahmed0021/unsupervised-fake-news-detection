#imports
import csv
import pandas as pd
import random
import matplotlib.pyplot as plt
from utils import *


#Gibbs Sampling Algorithm
def gibbs_sampling(alpha,beta,gamma,iter_num,burnin,thin,optimised,actual,mCred={},nCred={}):
    resultTemp={}
    resultFinal={}
    track=[]
    mCount={}
    nCount={}


    for userName in list(verifiedDataset.username.unique()):
        mCount[(userName, 0, 0)] = 0
        mCount[(userName, 0, 1)] = 0
        mCount[(userName, 1, 0)] = 0
        mCount[(userName, 1, 1)] = 0

    for userName in list(unverifiedDataset.username.unique()):
        nCount[(userName, 0, 0, 0)] = 0
        nCount[(userName, 0, 0, 1)] = 0
        nCount[(userName, 0, 1, 0)] = 0
        nCount[(userName, 0, 1, 1)] = 0
        nCount[(userName, 1, 0, 0)] = 0
        nCount[(userName, 1, 0 ,1)] = 0
        nCount[(userName, 1, 1, 0)] = 0
        nCount[(userName, 1, 1, 1)] = 0  

    
    # initializing counts
    print('Initializing...')
    for newsId, group in verifiedDataset.groupby('newsId'):
        resultTemp[newsId] = random.randint(0,1)
        for i in range(len(group)):
            if not optimised:
                mCount[(group.iloc[i].username, resultTemp[newsId], group.iloc[i].score)] += 1
            else:
                mCount[(group.iloc[i].username, resultTemp[newsId], group.iloc[i].score)] +=1+mCred[group.iloc[i].username]

            currTweet = group.iloc[i].tweet_id
            reTweets = unverifiedDataset[unverifiedDataset.tweet_id == currTweet]
            for j in range(len(reTweets)):
                nCount[(reTweets.iloc[j].username, resultTemp[newsId], group.iloc[i].score, reTweets.iloc[j].score)] += 1


    print('gibbs sampling started...')  
    
    #Gibbs Sampling
    for iter_i in range(iter_num):
        print(iter_i+1, 'th iteration: ')
        for newsId, group in verifiedDataset.groupby('newsId'):
            
            pseudoRes = resultTemp[newsId]
            p = {pseudoRes: gamma[pseudoRes], 1-pseudoRes: gamma[1-pseudoRes]}

            for i in range(len(group)):
                verfiedUser = group.iloc[i].username
                verfiedObservation = group.iloc[i].score
                tweet = group.iloc[i].tweet_id
                den1=(mCount[(verfiedUser, pseudoRes, 1)] + mCount[(verfiedUser, pseudoRes, 0)] - 1 + alpha[(pseudoRes, 0)] + alpha[(pseudoRes, 1)])
                den2=(mCount[(verfiedUser, 1-pseudoRes, 1)] + mCount[(verfiedUser, 1-pseudoRes, 0)] + alpha[(1-pseudoRes, 0)] + alpha[(1-pseudoRes, 1)])
                if(den1==0):
                    # den1=1
                    continue
                if den2==0:
                    # den2=1
                    continue
                p[pseudoRes] *= (mCount[(verfiedUser, pseudoRes, verfiedObservation)] - 1 + alpha[(pseudoRes, verfiedObservation)]) /den1
                p[1-pseudoRes] *= (mCount[(verfiedUser, 1-pseudoRes, verfiedObservation)] + alpha[(1-pseudoRes, verfiedObservation)]) /den2

                reTweets = unverifiedDataset[unverifiedDataset.tweet_id == tweet]
                for j in range(len(reTweets)):
                    unverfiedUser = reTweets.iloc[j].username
                    unverfiedObservation = reTweets.iloc[j].score
                    den1=(nCount[(unverfiedUser, pseudoRes, verfiedObservation, 0)] + nCount[(unverfiedUser, pseudoRes, verfiedObservation, 1)] - 1 + beta[(pseudoRes, verfiedObservation, 0)] + beta[(pseudoRes, verfiedObservation, 1)])
                    den2=(nCount[(unverfiedUser, 1-pseudoRes, verfiedObservation, 0)] + nCount[(unverfiedUser, 1-pseudoRes, verfiedObservation, 1)] + beta[(1-pseudoRes, verfiedObservation, 0)] + beta[1-pseudoRes, verfiedObservation, 1])
                    if(den1==0):
                        # den1==1
                        continue
                    if(den2==0):
                        # den2=1
                        continue
                    p[pseudoRes] *= (nCount[(unverfiedUser, pseudoRes, verfiedObservation, unverfiedObservation)] - 1 + beta[(pseudoRes, verfiedObservation, unverfiedObservation)]) /den1
                    p[1-pseudoRes] *= (nCount[(unverfiedUser, 1-pseudoRes, verfiedObservation, unverfiedObservation)] + beta[(1-pseudoRes, verfiedObservation, unverfiedObservation)]) /den2

            #if the probability we found does not match with the initialised assumption then update the counts
            if (p[1-pseudoRes]+p[pseudoRes]==0):
                continue
            if ( pseudoRes==0 and p[pseudoRes]/(p[1-pseudoRes]+p[pseudoRes])>.5 ) or (pseudoRes==1 and p[pseudoRes]/(p[1-pseudoRes]+p[pseudoRes])<.5 ):
                pseudoRes = 1 - pseudoRes
                resultTemp[newsId] = pseudoRes
                # pseudoRes changed, update count
                
                for i in range(len(group)):
                    verfiedUser = group.iloc[i].username
                    verfiedObservation = group.iloc[i].score
                    tweet = group.iloc[i].tweet_id
                    if not optimised:
                        mCount[(verfiedUser, 1-pseudoRes, verfiedObservation)] -= 1
                        mCount[(verfiedUser, pseudoRes, verfiedObservation)] += 1
                    else:
                        mCount[(verfiedUser, 1-pseudoRes, verfiedObservation)] -= 1+mCred[verfiedUser]
                        mCount[(verfiedUser, pseudoRes, verfiedObservation)] += 1+mCred[verfiedUser]

                    reTweets = unverifiedDataset[unverifiedDataset.tweet_id == tweet]
                    for j in range(len(reTweets)):
                        unverfiedUser = reTweets.iloc[j].username
                        unverfiedObservation = reTweets.iloc[j].score
                        nCount[(unverfiedUser, 1-pseudoRes, verfiedObservation, unverfiedObservation)] -= 1
                        nCount[(unverfiedUser, pseudoRes, verfiedObservation, unverfiedObservation)] += 1
            if iter_i > burnin and iter_i % thin == 0:
                resultFinal[newsId] = p[1]/(p[1]+p[0])  > 0.5


        
        
        if iter_i > burnin and iter_i % thin == 0:
            lossResult = 0
            for key, value in resultFinal.items():
                if value != actual[key]:
                    lossResult += 1
            track.append([iter_i,lossResult])
            t,f=getNewHyper(mCount)
            if optimised:
                alpha={(0,0):t+3,(0,1):f-3,(1,1):t+3,(1,0):f-3}

    
    return  mCount, nCount,track,alpha,resultFinal

#declaring hyperparameters
alpha={(0,0):7,(0,1):3,(1,1):7,(1,0):3}
gamma={0:5,1:5}
beta={(0,0,0):9,(0,1,0):9,(1,0,0):9,(1,1,0):9,(0,0,1):1,(0,1,1):1,(1,0,1):1,(1,1,1):1}
burnin=20
thin=4
iter_num=100

#setting axis size for graphs
axes = plt.gca()
axes.set_ylim([70,300])
#importing datasets

verifiedDataset=pd.read_csv('verified_dataset_sample.csv')
unverifiedDataset=pd.read_csv('unverified_dataset_sample.csv')

#fetching ground truth from csv file for comparision
filedata=verifiedDataset.newsId
gtdata=verifiedDataset.ground_truth
ground_truth={}
for i in range(len(gtdata)):
    if gtdata.iloc[i]==1:
        ground_truth[filedata.iloc[i]]=True
    else:
        ground_truth[filedata.iloc[i]]=False 


#calling initial algorithm
mCount,nCount,track1,newalpha,result1=gibbs_sampling(alpha,beta,gamma,iter_num,burnin,thin,False,ground_truth)

i1=[]
l1=[]
for i in range(len(track1)):
    i1.append(track1[i][0])
    l1.append(track1[i][1])
plt.plot(i1,l1)
plt.show()



#getting parameters for optimised algorithm
mCred,nCred=find_credibility(mCount,nCount)
#calling optimised algorithm
print('optimised algo......................................................')
nCount,mCount,track2,_,result2=gibbs_sampling(newalpha,beta,gamma,iter_num,burnin,thin,True,ground_truth,mCred,nCred)

i2=[]
l2=[]
for i in range(len(track2)):
    i2.append(track2[i][0])
    l2.append(track2[i][1])
plt.plot(i2,l2)
plt.show()





#calculating performance of algorithm 1
tp1=0
tn1=0
fp1=0
fn1=0
for key,value in result1.items():
    if result1[key]==1 and ground_truth[key]==1:
        tp1+=1
    elif result1[key]==0 and ground_truth[key]==0:
        tn1+=1
    elif result1[key]==1 and ground_truth[key]==0:
        fp1+=1
    else:
        fn1+=1
        
accuracy1=(tp1+tn1)/(tp1+tn1+fp1+fn1)
recall1=tp1/(tp1+fn1)
precision1=tp1/(tp1+fp1)
f1=2*precision1*recall1/(precision1+recall1)


#calculating performance of optimised algorithm
tp2=0
tn2=0
fp2=0
fn2=0
for key,value in result2.items():
    if result2[key]==1 and ground_truth[key]==1:
        tp2+=1
    elif result2[key]==0 and ground_truth[key]==0:
        tn2+=1
    elif result2[key]==1 and ground_truth[key]==0:
        fp2+=1
    else:
        fn2+=1
        
accuracy2=(tp2+tn2)/(tp2+tn2+fp2+fn2)
recall2=tp2/(tp2+fn2)
precision2=tp2/(tp2+fp2)
f2=2*precision2*recall2/(precision2+recall2)


print('Result of normal algorithm')
for key,value in result1.items():
    print('News with id:{} is {}'.format(key,value))
print('Result of optimised algorithm')
for key,value in result2.items():
    print('News with id:{} is {}'.format(key,value))




















