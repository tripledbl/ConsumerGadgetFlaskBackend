from numpy.core.fromnumeric import mean
from dataIngestion import *
import numpy as np
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from extensions import *
import gridfs
import pickle
import io

# create_model
# inputs: None
# outputs: A machine learning model based on the data using the decision tree algorithm
def create_model(user_id):
    # get the orders data from the users square account
    df = orders_to_dateframe()

    # add relevant date columns derived from the current date column
    df = add_date_columns(df)

    # split into input and response datasets
    X = df.drop(columns=['order_count'])
    y = df['order_count']

    # split into training and testing datasets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    
    # create random forrest model
    model_rf = RandomForestRegressor(n_estimators=2500, oob_score=True, random_state=100)
    model_rf.fit(X_train.values, y_train)

    # make a prediction using the original training values
    pred_train_rf = model_rf.predict(X_train.values)
    print(np.sqrt(mean_squared_error(y_train, pred_train_rf)))
    print(r2_score(y_train, pred_train_rf))

    # make a prediction using the testing values
    pred_test_rf = model_rf.predict(X_test.values)
    print(np.sqrt(mean_squared_error(y_test, pred_test_rf)))
    print(r2_score(y_test, pred_test_rf))

    # store these fields as attributes of the model for later use
    model_rf.mean_error = np.sqrt(mean_squared_error(y_test, pred_test_rf))
    model_rf.accuracy = r2_score(y_test, pred_test_rf)
    model_rf.features = X_train.columns

    # insert model info into db
    download_model(model_rf)

# insert_model_info
# inputs: model name, model accuracy, and average model error
# outputs: the information regarding an ML model is inserted into the database (the actual model file is not inserted)
def download_model(model):
    
    with open('trainedModels/customer_volume_model', 'wb') as f:
        pickle.dump(model, f)

    return 'downloaded'

# make_prediction
# inputs: model name, a date to predict for
# outputs: a float value that is the output of the model
def make_prediction(date, model_name):
    # cast the date string to a date
    date = datetime.strptime(date, '%Y-%m-%d').date()

    # cast to datetime so the column conversions below work
    time = datetime.min.time()
    date = datetime.combine(date, time)

    # initialize a dataframe with the given columns
    df = pd.DataFrame(columns=['date'])

    # populate the dataframe with the given date
    df.loc[len(df)] = [date]

    # add columns for the relevant date features
    df['year'] = pd.DatetimeIndex(df['date']).year
    df['month'] = pd.DatetimeIndex(df['date']).month
    df['day'] = pd.DatetimeIndex(df['date']).day
    df['dayofyear'] = pd.DatetimeIndex(df['date']).dayofyear
    df['weekofyear'] = pd.DatetimeIndex(df['date']).weekofyear
    df['weekday'] = pd.DatetimeIndex(df['date']).weekday
    df['quarter'] = pd.DatetimeIndex(df['date']).quarter
    df['is_month_start'] = pd.DatetimeIndex(df['date']).is_month_start
    df['is_month_end'] = pd.DatetimeIndex(df['date']).is_month_end

    # dummy encoding technique to create categorical variables from necessary columns
    df = pd.get_dummies(df, columns=['year'], prefix='year')
    df = pd.get_dummies(df, columns=['month'], prefix='month')
    df = pd.get_dummies(df, columns=['weekday'], prefix='wday')
    df = pd.get_dummies(df, columns=['quarter'], prefix='qrtr')
    df = pd.get_dummies(df, columns=['is_month_start'], prefix='m_start')
    df = pd.get_dummies(df, columns=['is_month_end'], prefix='m_end')

    # remove the date column because we dont need it anymore
    df = df.drop(['date'], axis=1)

    # retrieve the ml model
    model_path = 'trainedModels/' + model_name
    with open(model_path, 'rb') as f:
        model = pickle.load(f)

    # get missing columns
    missing_cols = set(model.features) - set(df.columns)
    # add missing columns with default value set to 0
    for c in missing_cols:
        df[c] = 0
    # ensure that the order of the columns is the same
    df = df[model.features]

    return model.predict(df.values)
