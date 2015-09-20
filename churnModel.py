__author__ = 'tsando'

import pandas as pd
import numpy as np # to use unique
import datetime
from IPython import embed

from sklearn import preprocessing # to use LabelEnconder
from sklearn.preprocessing import StandardScaler # to use StandardScaler
from sklearn.cross_validation import KFold # to use KFold

# ML algorithms
# from sklearn.svm import SVC # takes too long to run on this dataset
# from sklearn.ensemble import RandomForestClassifier as RF
#from sklearn.neighbors import KNeighborsClassifier as KNN
from sklearn.tree import DecisionTreeClassifier as DT

# Read 1st csv file of customer table. Must have tab as delimiter

cust_df = pd.read_csv("data/customer_000000_0.csv", header=None, delimiter="\t")

# Set column names
cust_df.columns = ['customerId2', 'churnlabel', 'gender', 'shippingCountry',
                   'dateCreated', 'yearOfBirth', 'premier']

# Create customer age metric
cust_df['age'] = datetime.date.today().year - cust_df['yearOfBirth']

# Convert string dates to datetime objects
cust_df['dateCreated'] = pd.to_datetime(pd.Series(cust_df['dateCreated']))
cust_df['year'] = cust_df['dateCreated'].dt.year
cust_df['month'] = cust_df['dateCreated'].dt.month
cust_df['day'] = cust_df['dateCreated'].dt.day

# Define target
y = cust_df['churnlabel']

# Define categorical and numerical features
cat_cols = ['gender', 'shippingCountry']
num_cols = ['premier', 'year', 'month', 'day', 'age']

# Define drop columns
drop_cols = set(cust_df.columns.tolist()) - set(cat_cols + num_cols)

### Create feature matrix
cust_df2 = cust_df
# drop cols
cust_df2 = cust_df2.drop(drop_cols, axis=1)

# transform categorical to dummy vars # currently gives 2 FutureWarnings
le = preprocessing.LabelEncoder()  # used instead of pandas.get_dummies as too many levels in countries
for i in cat_cols:
    le.fit(cust_df2[i])  # get no. of diff categories in 1-d vector
    cust_df2[i] = le.transform(cust_df2[i])

# Normalise data to standard normally distributed data
X = cust_df2.as_matrix().astype(np.float)
scaler = StandardScaler()
X = scaler.fit_transform(X)

print "Feature space holds %d observations and %d features" % X.shape
print "Unique target labels:", np.unique(y)

### Split into train and test data using KFold (both X and y must be np arrays)

def run_model(X, y, clf_class, **kwargs):
    n = len(X)
    kf = KFold(n=len(X), n_folds=5, shuffle=True)
    y_pred = y.copy()
    # Loop through folds
    i = 0
    for train_index, test_index in kf:
        i += 1
        print "INFO:: start looping over fold no." + str(i)
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]
        clf = clf_class(**kwargs)
        print "INFO:: FIT"
        clf.fit(X_train, y_train)
        print "INFO:: PREDICT"
        y_pred[test_index] = clf.predict(X_test)
        print "INFO:: SCORE = %f" % clf.score(X_test, y_test)
    return y_pred

def accuracy(y_true, y_pred):
    # NumPy interprets True and False as 1. and 0.
    return np.mean(y_true == y_pred)

### Run different ML models for same X and y

models = [DT]
for i in models:
    print "INFO:: Running models %s" % str(i)
    y_pred = run_model(X, y, i)
    print "INFO:: MY OWN SCORE:" + str(accuracy(y, y_pred))
