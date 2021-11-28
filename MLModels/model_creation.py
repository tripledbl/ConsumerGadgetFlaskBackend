from dataIngestion import *
from sklearn.tree import DecisionTreeClassifier

# create_model
# inputs: None
# outputs: A machine learning model based on the data using the decision tree algorithm
def create_model():
    # get the orders data from the users square account
    df = orders_to_dateframe()
    df = add_day_of_week(df)
    # df = add_month(df)

    print(df)

    # convert order_count column to integers
    df['order_count'] = pd.to_numeric(df['order_count'])

    # create the input dataset
    X = df.drop(columns=['order_count', 'date'])
    # create the output dataset
    y = df.drop(columns=['day', 'date'])

    print(X)
    print(y)

    model = DecisionTreeClassifier()
    model.fit(X.values, y)
    predictions = model.predict(
        [
            [3]
        ]
    )
    print(predictions)
    

    return ''