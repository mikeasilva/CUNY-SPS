# -*- coding: utf-8 -*-
"""
Created on Sun Feb  1 08:25:31 2020

@author: Michael Silva
"""
import re
import numpy as np
import pandas as pd


def get_baseline_predictions(raw_avg, user_bias, item_bias):
    """Creates baseline predictions using the user and item biases
    Args:
        raw_avg (float): the mean of the user item matrix.
        user_bias (pandas.Series): A vector with the user biases.
        item_bias (pandas.Series): A vector with the item bises.
    Returns:
        baseline_predictions (DataFrame): The predictions.
    """
    # Create a data frame by repeating the raw avg
    baseline = pd.DataFrame(
        raw_avg, index=user_bias.index, columns=item_bias.index
    )
    # Create a data frame by repeating the user bias series
    user = pd.concat([pd.DataFrame(user_bias)] * len(item_bias), axis=1)
    user.columns = item_bias.index
    # Create a data frame by repeating the item bias series
    item = pd.concat([pd.DataFrame(item_bias)] * len(user_bias), axis=1)
    item.columns = user_bias.index
    item = item.transpose()
    # Bring the three components together to make the baseline predictions
    baseline_predictions = baseline + user + item
    return baseline_predictions

def get_biases(user_item_df, predictor):
    """Calculates the user and item biases for the dataframe
    Args:
        user_item_df (DataFrame): the pandas dataframe of that is a user item matrix.
        predictor (float): the predicted value.
    Returns:
        user_bias (pandas.Series): The biases for all of the rows.  
        item_bias (pandas.Series): The biases for all of the columns.
    """
    user_mean = user_item_df.mean(axis=1)
    item_mean = user_item_df.mean(axis=0)
    user_bias = user_mean - predictor
    item_bias = item_mean - predictor
    return (user_bias, item_bias)

def get_RMSE(user_item_df, predictor):
    """Calculates the RMSE for the predictor for the dataframe
    Args:
        user_item_df (DataFrame): the pandas dataframe of that is a user item matrix.
        predictor (float): the predicted value.
    Returns:
        RMSE_df (DataFrame): a data frame with the RMSE values.
    """
    predictors = user_item_df.applymap(one_or_na) * predictor
    errors = user_item_df - predictors
    squared_errors = errors ** 2
    mean_squared_errors = squared_errors.stack().mean()
    RMSE = mean_squared_errors ** (1 / 2)
    return RMSE

def get_valid_jester_predictions(baseline_predictions):
    """Round the values to the nearest integer between -10 and 10
    Args:
        baseline_predictions (DataFrame): the pandas dataframe of predictions.
    Returns:
        baseline_predictions (DataFrame): a data frame with valid predictions.
    """
    baseline_predictions = (
        baseline_predictions.round(0).astype("Int64").applymap(valid_jester_val)
    )
    return baseline_predictions

def is_plus_or_minus_five(x):
    """Returns a value between -5 and 5.
    Args:
        x (int): value that may be outside of the -5 to 5 range
    Returns:
        valid_x (int): x within the -5 to 5 range
    """
    if x > 5:
        return 5
    elif x < -5:
        return -5
    else:
        return x

def one_or_na(x):
    """Returns NA if it's an NA or 1.
    Args:
        x (mixed): value from pandas dataframe
    Returns:
        one_or_na (mixed): Either 1 or NA
    """
    if np.isnan(x):
        return x
    else:
        return 1

def read_joke(n):
    """Reads in the text of the jester joke
    Args:
        n (int): the joke number (1 to 100)
    Returns:
        joke_text (str): the content of the joke in one line
    """
    joke_text = ""
    joke_begin = False
    with open('jokes/init'+str(n)+'.html') as f:
        for line in f.readlines():
            if "end of joke" in line:
                joke_begin = False
            if joke_begin:
                joke_text += line.strip() + " "
            elif "begin of joke" in line:
                joke_begin = True
    # Strip all html tags
    html = re.compile('<.*?>')
    joke_text = re.sub(html, '', joke_text).strip()
    # Remove all the extra spaces
    joke_text = ' '.join(joke_text.split())
    return joke_text

def rescale_jester_ratings(df):
    """Convert data to a -5 to 5 integer scale
    Args:
        df (DataFrame): the pandas dataframe of jester ratings.
    Returns:
        rescaled_df (DataFrame): a data frame with valid rescaled ratings.
    """
    df = df / 2
    rescaled_df = (
        df.round(0).astype("Int64").applymap(is_plus_or_minus_five)
    )
    return rescaled_df
    
def train_test_split(user_item_df, train_proportion=0.8, random_seed=42):
    """Splits a data frame into two data frames.
    Args:
        user_item_df (DataFrame): the pandas dataframe of that is a user item matrix.
        train_proportion (float): the proportion of the non N/A data in the training set (Optional - 80% default)
        random_seed (int): the random number seed (Optional - 42 default).
    Returns:
        train_df (DataFrame): The training set dataframe.
        test_df (DataFrame): The testing set dataframe.
    """
    train_df = user_item_df.copy()
    np.random.seed(random_seed)
    # Count how many non N/A values are in the data frame
    has_data = train_df.count().sum(axis=0)
    # Determine how many values we need in the test set (there is no N/A's in the test set)
    n_test = has_data - int(round(has_data * train_proportion, 0))
    # Create an empty test data frame
    test_df = pd.DataFrame(np.nan, index=train_df.index, columns=train_df.columns)
    # Fill it with randomly selected values
    while test_df.count().sum(axis=0) < n_test:
        # Randomly select a row & column
        row_id = np.random.choice(list(train_df.index), 1)
        col_id = np.random.choice(list(train_df.columns), 1)
        # Get the data at that location
        val = train_df.iloc[row_id][col_id].values[0][0]
        # Check to see if it is not N/A
        if not np.isnan(val):
            # Remove it from the training set
            train_df.at[row_id, col_id] = None
            # Save it to the test set
            test_df.at[row_id, col_id] = val
    return (train_df, test_df)

def valid_jester_val(x):
    """Validates the jester predicted rating
    Args:
        x (float): the predicted rating to validate.
    Returns:
        valid_rating (float): a number between -10 and 10.
    """
    if x > 10:
        return 10
    elif x < -10:
        return -10
    else:
        return x