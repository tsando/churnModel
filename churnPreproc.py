__author__ = 'tsando'

###########################
#
# DATA PREP STAGE
#
###########################

# Std lib
import datetime as datetime
import glob as glob

# Non-std lib
import pandas as pd
import numpy  as np # to use unique
from IPython import embed # needed to use globa variables inside functions in IPython
from matplotlib import pylab, mlab, pyplot as plt

# ## Function to concatenate to single df multiple CSVs from the same source table
def getCSVsDF(path):
    allFiles = glob.glob(path)
    list = []
    for f in allFiles:
        df = pd.read_csv(f, header=None, delimiter="\t")
        list.append(df)
    return pd.concat(list)

# ## Check for duplicates
def getDuplicatesDF(var, df):
    dups = df.duplicated(var)
    return df[dups == True]

def hasDuplicates(key, df):
    dups = getDuplicatesDF(key, df)
    if len(dups) != 0:
        print "INFO:: df has duplicates - TEST FAILED"
        return True
    print "INFO:: df doesn't have duplicates - TEST PASSED"
    return False

# ## Convert string dates to datetime objects
def convertStrToDatetime(df, colName):
    df[colName] = pd.to_datetime(pd.Series(df[colName]))

# ##### Read csv files. Must have tab as delimiter

# #### CUSTOMER

# Read CSVs
path = 'data/customer_*.csv'
cust_df = getCSVsDF(path)
cust_df.columns = ['customerId2', 'churnlabel', 'gender', 'shippingCountry',
                   'dateCreated', 'yearOfBirth', 'premier']

# Convert date to datetime object
convertStrToDatetime(cust_df, 'dateCreated')

# Check for duplicates wrt common key
hasDuplicates('customerId2', cust_df)

# Create customer age metric
cust_df['age'] = datetime.date.today().year - cust_df['yearOfBirth']

# Convert string dates to datetime objects
cust_df['year'] = cust_df['dateCreated'].dt.year
cust_df['month'] = cust_df['dateCreated'].dt.month
cust_df['day'] = cust_df['dateCreated'].dt.day

# Drop unused columns
drop_cols = ['dateCreated', 'yearOfBirth']
cust_df2 = cust_df
cust_df2 = cust_df2.drop(drop_cols, axis=1)

# ################### RECEIPTS

# Read CSVs
path = 'data/receipts_*.csv'
rec_df = getCSVsDF(path)
rec_df.columns = ['customerId2', 'productId', 'divisionId', 'sourceId', 'itemQty', 'signalDate',
                  'receiptId', 'price']

# Convert date to datetime object
convertStrToDatetime(rec_df, 'signalDate')

# Check for duplicates wrt common key
hasDuplicates('customerId2', rec_df)

# Create groupby object
g = rec_df.groupby('customerId2')
rec_df2 = g.agg({'productId' : 'nunique', 'divisionId': 'nunique'})


# ################### RETURNS

path = 'data/returns_*.csv'
ret_df = getCSVsDF(path)
ret_df.columns = ['customerId2', 'productId', 'divisionId', 'sourceId', 'itemQty', 'signalDate',
                  'receiptId', 'returnId', 'returnAction', 'returnReason']

# ################### RECEIPTS

# Convert date string to datetime object
convertStrToDatetime(rec_df, 'signalDate')
hasDuplicates('customerId2', rec_df)


# # Create TotalSpent column
# rec_df2 = rec_df
# rec_df2['TotalSpent'] = rec_df2['price']*rec_df2['itemQty']
#
# # Add total no. of transactions per customer
# rec_series = rec_df2.groupby('customerId2')['customerId2'].count()  # returns a panda series
# N_max = max(rec_series)
# N_max_cust = rec_series[rec_series == N_max]
# s = "INFO:: Largest transaction volume was N_max = {} for customer(s): {}".format(N_max, N_max_cust)
# print s
# print "INFO:: Plotting time series for this customer"
#
# # Plot Customer Time Series for TotalSpent vs Month
# rec_series.sort(ascending=False)
# for i in rec_series[0:5].index:
#     print i, rec_series[i]
#     plotCustTimeSeries(rec_df2, i)
# plt.show()


# ## Find duplicates in rec_df to show customers with more than one transaction i.e. with purchase history
# dups = rec_df.duplicated('customerId2')
# dups.head()
# rec_df[dups==True].head()
# rec_df[rec_df.customerId2 == 1548585].head()
# rec_df[rec_df.customerId2 == 397211].head()

##################################################
# PLOTTING
##################################################

# # ## Plot time series for a particular customer
# def plotCustTimeSeries(rec_df, my_customerId2):
#     # e.g. my_customerId2 = 397211
#     b = rec_df[rec_df.customerId2 == my_customerId2][['signalDate', 'TotalSpent']]
#     b['month'] = b.signalDate.apply(datetime.date.strftime, args=('%Y.%m',))
#     a = b.groupby(['month'])['TotalSpent'].aggregate(sum)
#     a.plot()


##################################################
# APPENDIX
##################################################


