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
import matplotlib as mpl
# from matplotlib import pylab, mlab, pyplot as plt
from scipy import stats  # required for stats.mode function


# ## Function to concatenate to single df multiple CSVs from the same source table
def getCSVsDF(path):
    allFiles = glob.glob(path)
    list = []
    for f in allFiles:
        df = pd.read_csv(f, header=None, delimiter="\t")  # Must have tab as delimiter
        list.append(df)
    return pd.concat(list)


# ## Check for duplicates
def getDuplicatesDF(key, df):
    dups = df.duplicated(key)
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

# ## Calculate linear regression slope
def getLRslope(df):
    # df.index = df.monthyear
    # Required to fix bug in linregress
    x = mpl.dates.date2num(df.index.to_pydatetime())
    y = df.Total
    # Fit linear regression and get only slope/gradient
    return stats.linregress(x, y).slope

# #### CUSTOMER

# Read CSVs
path = 'data/customer_*.csv'
cust_df = getCSVsDF(path)
cust_df.columns = ['customerId2', 'churnlabel', 'gender', 'shippingCountry',
                   'dateCreated', 'yearOfBirth', 'premier']

# Convert date to datetime object
convertStrToDatetime(cust_df, 'dateCreated')

# Check for duplicates wrt common key
# hasDuplicates('customerId2', cust_df)

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

# # Check for duplicates wrt common key
# hasDuplicates('customerId2', rec_df)

# Duplicate sourceId col to calculate 2 diff metrics in agg below
rec_df['sourceId2'] = rec_df['sourceId']

# Extract month and year from datetime variable
rec_df['monthyear'] = rec_df.signalDate.apply(datetime.date.strftime, args=('%Y.%m',))

# Convert from object type back to datetime type
rec_df['monthyear'] = pd.to_datetime(rec_df.monthyear, format='%Y.%m')

# Calculate total spent on receipt/order
rec_df['Total'] = rec_df['itemQty'] * rec_df['price']

# Create groupby object
grouped = rec_df.groupby('customerId2')

# Prepare data frame for linear regression (Total per customer per monthyear);
# reset_index used to remove multiindex format
rec_df2 = rec_df.groupby(['customerId2','monthyear'])['Total'].sum().reset_index()
rec_df2.index = rec_df2.monthyear
rec_df2 = rec_df2.drop('monthyear', axis=1)
# This takes about 15 min!
print "INFO:: Calculating gradient of Total Spent time series per customer"
rec_df2 = rec_df2.groupby('customerId2').apply(getLRslope)

# Fill NaNs with zero (inplace=True to change contents of df itself)
rec_df2.fillna(0, inplace=True)

# Convert to data frame object with a column name to be able to join to rec_df3 below
rec_df2 = pd.DataFrame(rec_df2)
rec_df2.columns = ['slope']

# Calculate stats for grouby object
print "INFO:: Calculating stats at customer level"
rec_df3 = grouped.agg({'productId': 'nunique',  # n distinct products
                       'divisionId': 'nunique',  # purchased from n distinct departments
                       'sourceId': 'nunique',  # at n distinct sources
                       #  function can be replaced by more elegant lambda x:x.value_counts().index[0]
                       # http://stackoverflow.com/questions/15222754/group-by-pandas-dataframe-and-select-most-common-string-factor
                       'sourceId2': lambda x: stats.mode(x)[0][0],  # with most freq source being this
                       'itemQty': 'sum',
                       'price': 'sum',  # total spent
                       'receiptId': 'nunique'  # n transactions per customer
                       })

# Rename columns
# x = x.rename(columns={'receipt_id': 'total_returns', '...'})

rec_df3 = rec_df3.rename(columns={'customerId2': 'customerId2',
                                  'productId': 'productId_N',
                                  'divisionId': 'divisionId_N',
                                  'sourceId': 'sourceId_N',
                                  'sourceId2': 'sourceId_mode',
                                  'itemQty': 'itemQty_sum',
                                  'price': 'price_sum',
                                  'receiptId': 'receiptId_N'})

# Join linear regression slope (rec_df2) with other stats (rec_df3) on index customerId2
rec_df4 = rec_df3.join(rec_df2)

# Pre X matrix (some additional steps required to make it X in churnModel.py)
X0 = cust_df2.join(rec_df4, on='customerId2')

# # ################### RETURNS
#
# path = 'data/returns_*.csv'
# ret_df = getCSVsDF(path)
# ret_df.columns = ['customerId2', 'productId', 'divisionId', 'sourceId', 'itemQty', 'signalDate',
#                   'receiptId', 'returnId', 'returnAction', 'returnReason']
#
# # ################### RECEIPTS
#
# # Convert date string to datetime object
# convertStrToDatetime(rec_df, 'signalDate')
# hasDuplicates('customerId2', rec_df)


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