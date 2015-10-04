__author__ = 'tsando'

###########################
#
# MODEL SELECTION & SCORING
#
###########################

from churnPreproc import *  # data preprocessing stage

from sklearn import preprocessing  # to use LabelEnconder
from sklearn.preprocessing import StandardScaler  # to use StandardScaler
from sklearn.cross_validation import KFold  # to use KFold

# ML algorithms
# from sklearn.svm import SVC # takes too long to run on this dataset
# from sklearn.ensemble import RandomForestClassifier as RF
# from sklearn.neighbors import KNeighborsClassifier as KNN
from sklearn.tree import DecisionTreeClassifier as DT
from sklearn.ensemble import GradientBoostingClassifier as GB

# ------------------------------------------------------------

# Split into train and test data using KFold (both X and y must be np arrays)

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


# Define own score measure

def accuracy(y_true, y_pred):
    # NumPy interprets True and False as 1. and 0.
    return np.mean(y_true == y_pred)


# ------------------------------------------------------------

def main(y, X0, cat_cols, num_cols, args):
    # Drop unused columns
    drop_cols = set(X0.columns.tolist()) - set(cat_cols + num_cols)
    X = X0
    X = X.drop(drop_cols, axis=1)

    # Transform categorical to dummy vars using Label Encoder - currently gives 2 FutureWarnings
    le = preprocessing.LabelEncoder()  # used instead of pandas.get_dummies as too many levels in countries
    for i in cat_cols:
        le.fit(X[i])  # get no. of diff categories in 1-d vector
        X[i] = le.transform(X[i])

    # Normalise data to standard normally distributed data
    X = X.as_matrix().astype(np.float)
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    print "INFO:: Feature space holds %d observations and %d features" % X.shape
    print "INFO:: Unique target labels:", np.unique(y)
    print "----------------------------------------------------------"

    # Run different ML models for same X and y

    models = args  # list of ML algorithms
    for i in models:
        print "INFO:: Running models %s" % str(i)
        y_pred = run_model(X, y, i)
        print "INFO:: MY OWN SCORE:" + str(accuracy(y, y_pred))


# ------------------------------------------------------------

# Define target
y = X0['churnlabel']

# Define categorical and numerical features
cat_cols = ['gender', 'shippingCountry']
num_cols = ['premier', 'age', 'year', 'month', 'day',
            'itemQty_sum', 'sourceId_N', 'price_sum', 'divisionId_N' 'sourceId_mode',
            'receiptId_N', 'productId_N']

main(y, X0, cat_cols, num_cols, [GB])  # DT stands for DecisionTree algo
