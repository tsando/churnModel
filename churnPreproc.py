__author__ = 'tsando'

###########################
#
# DATA PREP STAGE
#
###########################

import pandas as pd
import numpy as np  # to use unique
import datetime
from IPython import embed

# Read csv files. Must have tab as delimiter
cust_df = pd.read_csv("data/customer_000000_0.csv", header=None, delimiter="\t")
rec_df = pd.read_csv("data/receipts_000000_0.csv", header=None, delimiter="\t")
ret_df = pd.read_csv("data/returns_000000_0.csv", header=None, delimiter="\t")
# sess_df = pd.read_csv("data/sessionsummary_000000_0.csv", header=None, delimiter="\t")

# Set column names
cust_df.columns = ['customerId2', 'churnlabel', 'gender', 'shippingCountry',
                   'dateCreated', 'yearOfBirth', 'premier']

rec_df.columns = ['customerId2', 'productId', 'divisionId', 'sourceId', 'itemQty', 'signalDate',
                  'receiptId', 'price']

ret_df.columns = ['customerId2', 'productId', 'divisionId', 'sourceId', 'itemQty',
                  'signalDate', 'receiptId', 'returnId', 'returnAction', 'returnReason']


# Find duplicates and show duplicated rows for one case
# dups = rec_df.duplicated('customerId2')
# dups.head()
# rec_df[dups==True].head()
# rec_df[rec_df.customerId2 == 1548585].head()


##################################################

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

# Create feature matrix
cust_df2 = cust_df
# drop cols
cust_df2 = cust_df2.drop(drop_cols, axis=1)
