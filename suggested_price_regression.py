
# coding: utf-8

# In[15]:  

def predict_price(property_type,room_type,cancellation_policy,minimum_nights,accommodates,review_scores_cleanliness,review_scores_communication, review_scores_location):
    import pandas as pd
    from sklearn.linear_model import LinearRegression
    
    ##################Query the data from database to run regression#################
    data = pd.read_csv('table/listings.csv',encoding = "ISO-8859-1")
    
    #Select the data we needed and remove NAs
    keep_list =['latitude', 'longitude','id', 'price','neighbourhood_cleansed', 'accommodates', 'property_type', 'room_type', 'minimum_nights', 'cancellation_policy','review_scores_cleanliness', 'review_scores_communication', 'review_scores_location']
    data = data[keep_list].dropna()
    
    #create X and Y
    #be aware the order of these X variables
    X_col= ['property_type', 'room_type', 'cancellation_policy','minimum_nights', 'accommodates','review_scores_cleanliness','review_scores_communication', 'review_scores_location']
    X = data[X_col]
    X_dummies = pd.get_dummies(X.ix[:,0:3], drop_first=True)
    X = pd.concat([X.ix[:,3:], X_dummies], axis=1)
    
    Y = data['price'].str.slice(1)
    Y = Y.replace({',': ''}, regex=True)
    Y = Y.convert_objects(convert_numeric=True)
    
    linreg = LinearRegression()  
    model=linreg.fit(X, Y)
    coef_ = linreg.coef_
    intercept_ = linreg.intercept_
    
    ##############Deal with the inputs####################
    #convert the inputs to dummy variables to fit in the model
    convert_dummie_inputs = []
    for j in range(22):
        if property_type in list(X_dummies)[j]:
            convert_dummie_inputs.append(1)
        else:
            convert_dummie_inputs.append(0)
    for j in range(22,24):
        if room_type in list(X_dummies)[j]:
            convert_dummie_inputs.append(1)
        else:
            convert_dummie_inputs.append(0)
    for j in range(24,28):
        if cancellation_policy in list(X_dummies)[j]:
            convert_dummie_inputs.append(1)
        else:
            convert_dummie_inputs.append(0)
    
    #combine the dummy variables with real-value variables
    all_inputs = [minimum_nights,accommodates,review_scores_cleanliness,review_scores_communication,review_scores_location] + convert_dummie_inputs
    
    #evaluate the price with the model
    #x = zip(all_inputs,coef_)
    #price = 0
    #for i in list(x):
        #price += (i[0]*i[1])
    #price = int(price + intercept_)
    price=int(model.predict(all_inputs))
    
    return price

