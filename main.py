import datetime
from flask import Flask, render_template, jsonify
import pyarrow
import gcloud
from gcloud import storage
import pandas as pd


app = Flask(__name__)

songs = [
    {
        "title": "Hello World!",
        "to": "MSDS 434",
        "note": "working GAE deployed flask engine",
    },
    {
        "title": "Second Hello World!",
        "to": "Everyone else",
        "note": "Just another note",
    }
]

@app.route('/')
def root():
    # For the sake of example, use static information to inflate the template.
    # This will be replaced with real information in later steps.
    dummy_times = [datetime.datetime(2018, 1, 1, 10, 0, 0),
                   datetime.datetime(2018, 1, 2, 10, 30, 0),
                   datetime.datetime(2018, 1, 3, 11, 0, 0),
                   ]

    return render_template('index.html', times=dummy_times)

@app.route('/hello')
def home():
    return jsonify(songs)

@app.route('/predict')
def predict():
    # First get appropriate BQ credentials
    import google.auth
    #import json
    from google.cloud import bigquery
    from google.cloud import bigquery_storage

    # Explicitly create a credentials object. This allows you to use the same
    # credentials for both the BigQuery and BigQuery Storage clients, avoiding
    # unnecessary API calls to fetch duplicate authentication tokens.
    credentials, your_project_id = google.auth.default(
       scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )

    # Make clients.
    bqclient = bigquery.Client(credentials=credentials, project=your_project_id,)
    bqstorageclient = bigquery_storage.BigQueryReadClient(credentials=credentials)
    
    # Query BQ model prediction results table
    # Download query results.
    query_string = """SELECT * FROM `my-project-434-gcp.export_evaluated_examples_google_automl_20210210105125_2021_02_10T17_08_53_829Z.evaluated_examples` LIMIT 1000"""

    dataframe = (
        bqclient.query(query_string)
        .result()
        .to_dataframe(bqstorage_client=bqstorageclient)
    )
    results = dataframe.to_json(orient="index")
    #parsed = json.loads(results) 

    return results


@app.route('/update')
def update():

    import numpy as np
    import pandas as pd
    from yahoofinancials import YahooFinancials as yf

    # Picking the stock to predict and get historical data

    def get_stock_data(tickers, start_date='2020-01-01', end_date='2021-01-26', freq='daily'):
        '''This function takes the list of stock ticker and get historical OHLC data
        
        Parameters
        ----------
        tickers : list/iterable
            Iterable object containing ticker symbols as strings
        start_date : str, optional
            Takes start date of data, format = 'yyyy-mm-dd'
        end_date : str, optional
            Takes end date of data, format = 'yyyy-mm-dd'
            
        Returns
        -------
        pandas DataFrame containing pricing data and list containing tickers whose data was not found
        
        '''

        ticker_not_found=[]
        for ticker in tickers:
            yf_engine = yf(ticker)
            price = yf_engine.get_historical_price_data(start_date,end_date,freq)
            #store the data in DataFrame
            try:
                ticker_data = pd.DataFrame(price[ticker]['prices'])
                ticker_data = ticker_data.drop('date', axis=1) # We will use formatted_date columns instead
            except:
                ticker_not_found.append(ticker)
                continue
                
        return ticker_data, ticker_not_found
        


    def get_clean_data (df, start_date, end_date):
        '''This function takes the historical OHLC data and return features as we defined above
        
        Parameters
        ----------
        df : DataFrame
            Dataframe containing pricing data
        start_date : str, optional
            Takes start date of data for vix, format = 'yyyy-mm-dd'
        end_date : str, optional
            Takes ebd date of data for vix, format = 'yyyy-mm-dd'
            
        Returns
        -------
        pandas DataFrame containing scaled features except categorical features
        '''
        
        features = df.copy()
        #features = features.drop(['formatted_date'], axis=1)
        #creating features as stated above
        features['volume'] = features['volume'].shift(1)
        features['SMA'] = features['adjclose'].rolling(window=20).mean().shift(1)
        features['Std_20'] = features['adjclose'].rolling(window=20).std().shift(1)
        features['Band_1'] = features['SMA'] - features['Std_20']
        features['Band_2'] = features['SMA'] + features['Std_20']
        features['ON_returns'] = features['close'] - features['open'].shift(-1)
        features['ON_returns'] = features['ON_returns'].shift(1)
        features['ON_returns_signal'] = np.where(features['ON_returns']<0, 'up', 'down')
        features['dist_from_mean'] = features['adjclose'].shift(1) - features['SMA']
        #Obtaining Vix Data and combining with existing features of stock
        ticker = ['^VIX']
        start_date = start_date
        end_date = end_date
        vix_data, ticker_not_found = get_stock_data(ticker, start_date, end_date)
        vix_data = pd.DataFrame(vix_data['adjclose'].shift(1))
        vix_data = vix_data.rename(columns = {'adjclose':'vix_data'})
        comb_features = pd.concat([features,vix_data], axis=1)
        comb_features = comb_features.dropna() #dropping NaN values
        comb_features = pd.get_dummies(comb_features, columns=['ON_returns_signal']) #for categorical variables
        comb_features = comb_features.drop('ON_returns', axis=1) #dropping original categorical column
        comb_features = comb_features.drop('close', axis=1) #not really needed this value since we have adj close now
        ###Create return column to predict
        comb_features['stock_move'] = np.where(comb_features['adjclose']-
                                            comb_features['adjclose'].shift(-1)<0, "Buy", "Sell")
        features_clean = comb_features.dropna() #Dropping Nan values
        features_clean = features_clean[:-1] #Drop last row which do not have any stock signal
        features_clean.tail()
        return features_clean

    ups = [
    {
        "title": "Success",
        "to": "Goog",
        "note": "updated goog stock data",
    }]
    my_df = pd.DataFrame(data=[{1,2,3},{4,5,6}],columns=['a','b','c']).to_csv(sep=",", index=False, quotechar='"', encoding="UTF-8")
    client = storage.Client()
    bucket = client.get_bucket('my-new-bucket-holyshit')
    blob = bucket.blob('my-test-file5.csv')

    blob.upload_from_string(data=my_df) 

    #We will use Google stock ticker to predict its prices
    ticker = ['GOOG']
    start_date = '2019-07-01'
    end_date = '2020-10-01'

    df, ticker_not_found = get_stock_data(ticker, start_date, end_date)
    features = get_clean_data(df, start_date, end_date)
    #features.to_csv('Goog.csv', encoding='utf-8')
    
    #Create csv file and store on GCP cloud storage
    #my_df = pd.DataFrame(data=[{1,2,3},{4,5,6}],columns=['a','b','c']).to_csv(sep=",", index=False, quotechar='"', encoding="UTF-8")
    my_df = features.to_csv(sep=",", index=False, quotechar='"', encoding="UTF-8")
    client = storage.Client()
    bucket = client.get_bucket('my-project-434-gcp-data')
    blob = bucket.blob('goog.csv')

    blob.upload_from_string(data=my_df) 

    return jsonify(my_df) 


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)