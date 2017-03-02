
# coding: utf-8

# In[2]:

import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, precision_score, recall_score, f1_score
from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestClassifier
from sklearn import linear_model, svm, tree


# ## Functions

# In[39]:

def process_data(filename):
    
    # load dataset
    df = pd.read_csv(filename)

    # transform boolean features to numeric features
    df['first'] = df['first_letter_uppercase'].map({False:0, True:1}).astype(int)
    df['all'] = df['all_uppercase'].map({False:0, True:1}).astype(int)
    df['part'] = df['part_of_upper_seq'].map({False:0, True:1}).astype(int)
    df['next'] = df['next_word_has_numerals'].map({False:0, True:1}).astype(int)
    df['the'] = df['previous_word_is_the'].map({False:0, True:1}).astype(int)
#     df['from'] = df['previous_word_is_from'].map({False:0, True:1}).astype(int)
    df['by'] = df['previous_word_is_by'].map({False:0, True:1}).astype(int)
    df['letter'] = df['word_only_contains_letters'].map({False:0, True:1}).astype(int)
    df['class'] = df['label'].map({False:0, True:1}).astype(int)
    
    # drop redundant columns and rows
#     df = df.drop(['id', 'word', 'txt_file'], axis=1)
    df = df.drop(['first_letter_uppercase', 'all_uppercase', 
                  'part_of_upper_seq', 'next_word_has_numerals', 
                  'previous_word_is_the', 'previous_word_is_from', 'previous_word_is_by',
                  'word_only_contains_letters', 'label'], axis=1)
    df = df.dropna()
    df = df.drop_duplicates()
    data = np.random.permutation(df.values)
    
    return data


# In[40]:

# Thresholding for linear regression
def label(x, threshold): 
    if x > threshold:
        return 1
    return 0

# cross validation
def get_cv(X, y, model, modelType=0, nFold=5):
    precisionLst = []
    recallLst = []
    f1Lst = []
    kf = KFold(n_splits=nFold)
    for train, test in kf.split(X):
        X_train = X[train]
        y_train = list(y[train])
        X_test = X[test]
        y_test = list(y[test])
        
        model.fit(X_train, y_train)
        y_prediction = model.predict(X_test)
        if modelType == 1:
            pred= [label(x, 0.5) for x in y_prediction]
            y_prediction = pred
        elif modelType == 2:
            y_score = model.predict_proba(X_test)
            y_prediction = [label(x[1], 0.8) for x in y_score]

        f1Lst.append(f1_score(y_test, y_prediction))
        precisionLst.append(precision_score(y_test, y_prediction))
        recallLst.append(recall_score(y_test, y_prediction))
    
    precision = np.mean(precisionLst)
    recall = np.mean(recallLst)
    f1 = np.mean(f1Lst)
    print("\tPrecision: ", precision)
    print("\tRecall: ", recall)
    print("\tF1: ", f1)
    return [precision, recall]


# In[41]:

def test(X_test, y_test, model):
    #predict
    y_prediction = model.predict(X_test)
    target_names = ['False', 'True']
    print(classification_report(y_test, y_prediction, target_names = target_names))


# ## Data 

# In[42]:

# load dataset
train_data = process_data('dataset/train_vectors.csv')
test_data = process_data('dataset/test_vectors.csv')


# ## CV on I

# In[43]:

# Development set
X = train_data[:, 3:-1] # keep id
y = train_data[:, -1]


# In[44]:

#Linear Regression
lg = linear_model.LinearRegression()
print("Linear Regression")
get_cv(X, y, lg, 1)

# Logistic
logistic = linear_model.LogisticRegression(C=1e5)
print("Logistic")
get_cv(X, y, logistic)

svc = svm.SVC()
print("SVM")
get_cv(X, y, svc)

dtree = tree.DecisionTreeClassifier()
print("Decision Tree")
get_cv(X, y, dtree)

rf = RandomForestClassifier(n_estimators=100)
print("Random Forest")
get_cv(X, y, rf, 2)
print("---End--")


# ## Debug 60-40

# In[45]:

# split train data
size = train_data.shape[0]
split = int(size * 0.6)
X_train = X[:split]
y_train = list(y[:split])

#test data
X_test = X[split:]
y_test = list(y[split:])

print("Random Forest")
rf = RandomForestClassifier(n_estimators=100)
rf = rf.fit(X_train, y_train)


# ### Increase positive confidence level (improve precision)

# In[46]:

y_score = rf.predict_proba(X_test)
threshold = 0.8
pred = [label(x[1], threshold) for x in y_score]

precision = precision_score(y_test, pred)
recall = recall_score(y_test, pred)

target_names = ['False', 'True']
print(classification_report(y_test, pred, target_names = target_names))
    
print("Precision: ", precision)
print("Recall: ", recall)


# ## Test on J

# In[49]:

# create training data
X_test = test_data[:, 3:-1]
y_test = list(test_data[:, -1])

print("RandomForrest Testing")
rf = RandomForestClassifier(n_estimators=100)
rf = rf.fit(X, list(y))

y_score = rf.predict_proba(X_test)
threshold = 0.8
pred = [label(x[1], threshold) for x in y_score]

target_names = ['False', 'True']
print(classification_report(y_test, pred, target_names = target_names))

precision = precision_score(y_test, pred)
recall = recall_score(y_test, pred)

print("Precision: ", precision)
print("Recall: ", recall)


# In[ ]:



