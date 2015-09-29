__author__ = 'tsando'

###########################
#
# DATA PREP STAGE
#
###########################

import pandas as pd
import numpy  # to use unique
import datetime
from IPython import embed
import matplotlib
from matplotlib import pylab, mlab, pyplot
np = numpy
plt = pyplot

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


# ## Convert string dates to datetime objects

# rec_df['signalDate'] = pd.to_datetime(pd.Series(rec_df['signalDate']))
def convertStrToDatetime(df, colName):
    df[colName] = pd.to_datetime(pd.Series(rec_df[colName]))

# ## Plot time series for a particular customer
def plotCustTimeSeries(rec_df, my_customerId2):
    # e.g. my_customerId2 = 397211
    b = rec_df[rec_df.customerId2 == my_customerId2][['signalDate', 'TotalSpent']]
    b['month'] = b.signalDate.apply(datetime.date.strftime, args=('%Y.%m',))
    a = b.groupby(['month'])['TotalSpent'].aggregate(sum)
    a.plot()


# ## RECEIPTS

# Convert date string to datetime object
convertStrToDatetime(rec_df, 'signalDate')

# Create TotalSpent column
rec_df2 = rec_df
rec_df2['TotalSpent'] = rec_df2['price']*rec_df2['itemQty']

# Add total no. of transasctions per customer
rec_series = rec_df2.groupby('customerId2')['customerId2'].count()  # returns a panda series
N_max = max(rec_series)
N_max_cust = rec_series[rec_series == N_max]
s = "INFO:: Largest transaction volume was N_max = {} for customer(s): {}".format(N_max, N_max_cust)
print s
print "INFO:: Plotting time series for this customer"

rec_series.sort(ascending=False)
for i in rec_series[0:5].index:
    print i, rec_series[i]
    plotCustTimeSeries(rec_df2, i)
plt.show()

# ## Find duplicates in rec_df to show customers with more than one transaction i.e. with purchase history
# dups = rec_df.duplicated('customerId2')
# dups.head()
# rec_df[dups==True].head()
# rec_df[rec_df.customerId2 == 1548585].head()
# rec_df[rec_df.customerId2 == 397211].head()




##################################################

# # Create customer age metric
# cust_df['age'] = datetime.date.today().year - cust_df['yearOfBirth']
#
# # Convert string dates to datetime objects
# cust_df['dateCreated'] = pd.to_datetime(pd.Series(cust_df['dateCreated']))
# cust_df['year'] = cust_df['dateCreated'].dt.year
# cust_df['month'] = cust_df['dateCreated'].dt.month
# cust_df['day'] = cust_df['dateCreated'].dt.day
#
# # Define target
# y = cust_df['churnlabel']
#
# # Define categorical and numerical features
# cat_cols = ['gender', 'shippingCountry']
# num_cols = ['premier', 'year', 'month', 'day', 'age']
#
# # Define drop columns
# drop_cols = set(cust_df.columns.tolist()) - set(cat_cols + num_cols)
#
# # Create feature matrix
# cust_df2 = cust_df
# # drop cols
# cust_df2 = cust_df2.drop(drop_cols, axis=1)
