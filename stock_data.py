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

if __name__ == '__main__':
    #We will use Google stock ticker to predict its prices
    ticker = ['GOOG']
    start_date = '2019-07-01'
    end_date = '2021-02-09'

    df, ticker_not_found = get_stock_data(ticker, start_date, end_date)
    features = get_clean_data(df, start_date, end_date)
    features.to_csv('Goog.csv', encoding='utf-8')
