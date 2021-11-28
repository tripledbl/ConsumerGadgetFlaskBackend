from dataIngestion import *
import numpy as np
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# create_model
# inputs: None
# outputs: A machine learning model based on the data using the decision tree algorithm
def create_model():
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
    model_rf = RandomForestRegressor(n_estimators=5000, oob_score=True, random_state=100)
    model_rf.fit(X_train.values, y_train)
    pred_train_rf = model_rf.predict(X_train.values)
    print(np.sqrt(mean_squared_error(y_train, pred_train_rf)))
    print(r2_score(y_train, pred_train_rf))

    pred_test_rf = model_rf.predict(X_test.values)
    print(np.sqrt(mean_squared_error(y_test, pred_test_rf)))
    print(r2_score(y_test, pred_test_rf))

    print(pred_test_rf)

    return ''