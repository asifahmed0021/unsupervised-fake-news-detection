#optimised algorithm
def callOptimised(alpha,beta,gamma,iter_num,burnin,thin,actual):
    mCount,nCount,track1,newalpha,result1=gibbs_sampling(alpha,beta,gamma,iter_num,burnin,thin,False,actual)
    mCred,nCred=find_credibility(mCount, nCount)
    nCount,mCount,track2,_,result2=gibbs_sampling(newalpha,beta,gamma,30,burnin,thin,True,actual,mCred,nCred)
    return result2,actual

#credibility score function
def find_credibility(mCount,nCount):
    mCred={}
    nCred={}
    for username,value1,value2 in mCount:
        den=mCount[(username,1,1)]+mCount[(username,0,0)]+mCount[(username,1,0)]+mCount[(username,0,1)]
        if(den==0):
            mCred[username]=0
            continue
        cred=(mCount[(username,1,1)]+mCount[(username,0,0)])/den
        mCred[username]=cred
        
    for username,value1,value2,value3 in nCount:
        den=nCount[(username,0,1,0)]+nCount[(username,0,1,1)]+nCount[(username,1,0,0)]+nCount[(username,1,0,0)]+nCount[(username,1,1,0)]+nCount[(username,1,1,1)]+nCount[(username,0,0,0)]+nCount[(username,0,0,1)]
        if(den==0):
            nCred[username]=0
            continue
        cred=(nCount[(username,0,0,0)]+nCount[(username,1,1,1)])/den
        nCred[username]=cred
    return mCred,nCred

#function to get new hyper parameters
def getNewHyper(mCount):
    truepositive=0
    truenegative=0
    falsepositive=0
    falsenegative=0
    
    for (username,val1,val2),key in mCount.items():
        if(val1==1 and val2==1):
            truepositive+=key
        elif (val1==1 and val2==0):
            falsenegative+=key
        elif (val1==0 and val2==0):
            truenegative+=key
        else:
            falsepositive+=key
    truerate=(truepositive+truenegative)/2
    falserate=(falsepositive+falsenegative)/2
    tr=truerate*10/(truerate+falserate)
    fr=falserate*10/(truerate+falserate)
    return tr,fr
