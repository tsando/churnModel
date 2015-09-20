__author__ = 'tsando'

# from sklearn import datasets

import pandas as pd
import numpy as np
#import datetime
from sklearn import preprocessing

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
drop_cols = set(cust_df.columns.tolist()) - set(cat_cols+num_cols)

### Create feature matrix
cust_df2 = cust_df
# drop cols
cust_df2 = cust_df2.drop(drop_cols, axis=1)

# transform categorical to dummy vars
le = preprocessing.LabelEncoder() # used instead of pandas get_dummies as too many diff countries
for i in cat_cols:
    le.fit(cust_df2[i])
    cust_df2[i] = le.transform(cust_df2[i])

# cat_df = pd.get_dummies(cust_df2[cat_cols])
# cust_df2 = cust_df2.join(cat_df)
# cust_df2 = cust_df2.drop(cat_cols, axis=1)