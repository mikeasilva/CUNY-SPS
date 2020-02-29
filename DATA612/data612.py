# -*- coding: utf-8 -*-
"""
Created on Sun Feb  1 08:25:31 2020

@author: Michael Silva
"""
import contractions
import nltk
import numpy as np
import pandas as pd
import re
import sklearn.preprocessing
import sklearn.metrics.pairwise
import sklearn.feature_extraction.text
import string


def bag_of_words(sentences, na_fill=0, normalize=False):
    """Transforms a list of sentences into a bag of words matrix
    Args:
        sentences (list): A list of sentences
        na_fill (mixed): What should fill the NA's? (Optional - 0 default)
        normalize: If the bag of words should be normalized (Optional - False default)
    Returns:
        bag_of_words_df (DataFrame): Dataframe with word counts by sentence.
    """
    # Get the count of words in each sentence
    bag = dict()
    n = 0
    for sentence in sentences:
        n += 1
        sentence = sentence.lower()
        for word in sentence.split():
            # Use a tuple as the key holding the word and the sentence index number
            key = (word, n)
            # Count the word
            bag[key] = bag.get(key, 0) + 1
    # Convert the count into a long data frame
    bag_of_words_data = list()
    for k in bag.keys():
        row = {"word": k[0], "index": k[1], "count": bag[k]}
        bag_of_words_data.append(row)
    bag_of_words_df = pd.DataFrame(bag_of_words_data)
    # Convert from long to wide dataframe
    bag_of_words_df = bag_of_words_df.pivot_table(
        index="index", columns="word", values="count", fill_value=na_fill
    )
    if normalize:
        normalized_bag_of_words = sklearn.preprocessing.normalize(bag_of_words_df)
        bag_of_words_df = pd.DataFrame(
            normalized_bag_of_words,
            columns=bag_of_words_df.columns,
            index=bag_of_words_df.index,
        )

    return bag_of_words_df


def cosine_similarity(df, return_difference=False):
    """Measures the cosine similarity or difference of a data frame
    Args:
        df (DataFrame): The data frame of values to compute the cosine similarity/difference 
        return_difference (bool): Do you want the cosine difference returned? (Optional False default)
    Returns:
        cosine_df (DataFrame): The cosine similarity or difference in data frame form
    """
    cosine_metric = sklearn.metrics.pairwise.cosine_similarity(
        df
    )
    if return_difference:
        cosine_metric = 1 - cosine_metric
    cosine_df = pd.DataFrame(
        cosine_metric, index=df.index, columns=df.index
    )
    return cosine_df


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
    baseline = pd.DataFrame(raw_avg, index=user_bias.index, columns=item_bias.index)
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


def get_cosine_based_joke_recommendations(cosine_similarity_df, joke_id, n_recommendations = 10):
    """Translate a cosine similarity data frame into an ordered list of recommendations.
    Args:
        cosine_similarity_df (DataFrame):
        joke_id (int): the id of the joke (column number)
        n_recommendations (int): The number of recommendations (Optional - 10 default)
    Returns:
        recommendations (list): An ordered list of recommendations
    """
    # Transform the row of cosine values into a three column data frame (level_0 = joke_id, level_1 = cosine_similarity_df.columns, 0 = cosine value)
    temp = cosine_similarity_df[:joke_id].stack().reset_index()
    # Remove the record for the cosine of itself
    temp = temp[temp.level_0 != temp.level_1]
    # Sort the matrix by the values
    temp = temp.sort_values(by=[0], ascending=False)
    # Return the list of recommendations
    recommendations = list(temp[:n_recommendations]['level_1'])
    return recommendations


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


def preprocess_jokes(
    list_of_jokes,
    remove_contractions=False,
    remove_numbers=False,
    remove_punctuation_marks=False,
    remove_stop_words=False,
    stem_words=False,
    lemmatize_words=False,
):
    """Various text preprocessing tools for the jester jokes
    Args:
        list_of_jokes (list): A list containing the character string that makes up the joke
        remove_contractions (bool): Should we remove the contractions? (Optional - False default) 
        remove_numbers (bool): Should we remove the numbers? (Optional - False default)
        remove_punctuation_marks (bool): Should we remove all punctuation marks? (Optional - False default)
        remove_stop_words (bool): Should we remove all stop words? (Optional - False default)
        stem_words (bool): Should we stem all words? (Optional - False default) 
        lemmatize_words (bool): Should we lemmatize the words? (Optional - False default)
    Returns:
        preprocessed_jokes (list): A list containing the character strings after preprocessing
    """
    preprocessed_jokes = list()
    for joke in list_of_jokes:
        joke = joke.lower()
        if remove_contractions:
            joke = contractions.fix(joke)
        if remove_punctuation_marks:
            joke = joke.translate(str.maketrans(dict.fromkeys(string.punctuation)))
        if remove_numbers:
            joke = "".join([i for i in joke if not i.isdigit()])
        if remove_stop_words or stem_words or lemmatize_words:
            word_list = nltk.word_tokenize(joke)
            if stem_words:
                porter_stemmer = nltk.stem.porter.PorterStemmer()
                joke = " ".join([porter_stemmer.stem(word) for word in word_list])
            if lemmatize_words:
                lemmatizer = nltk.stem.WordNetLemmatizer()
                joke = " ".join([lemmatizer.lemmatize(w) for w in word_list])
            if remove_stop_words:
                stop_words = set(nltk.corpus.stopwords.words("english"))
                joke = " ".join([word for word in word_list if word not in stop_words])           
        preprocessed_jokes.append(joke)
    return preprocessed_jokes


def read_joke(n):
    """Reads in the text of the jester joke
    Args:
        n (int): the joke number (1 to 100)
    Returns:
        joke_text (str): the content of the joke in one line
    """
    joke_text = ""
    joke_begin = False
    with open("jokes/init" + str(n) + ".html") as f:
        for line in f.readlines():
            if "end of joke" in line:
                joke_begin = False
            if joke_begin:
                joke_text += line.strip() + " "
            elif "begin of joke" in line:
                joke_begin = True
    # Strip all html tags
    html = re.compile("<.*?>")
    joke_text = re.sub(html, "", joke_text).strip()
    # Remove all the extra spaces
    joke_text = " ".join(joke_text.split())
    return joke_text


def rescale_jester_ratings(df):
    """Convert data to a -5 to 5 integer scale
    Args:
        df (DataFrame): the pandas dataframe of jester ratings.
    Returns:
        rescaled_df (DataFrame): a data frame with valid rescaled ratings.
    """
    df = df / 2
    rescaled_df = df.round(0).astype("Int64").applymap(is_plus_or_minus_five)
    return rescaled_df


def tf_idf(corpus, normalize_results = True):
    """Compute the TF-IDF on the corpus.
    Args:
        corpus (list): a list of text strings
        normalize_results (bool): Should the TF-IDF results be normalized (Optional - True default)
    Returns:
        tfidf_df (DataFrame): a data frame with the TF-IDF values
    """
    tfidf = sklearn.feature_extraction.text.TfidfVectorizer()
    results = tfidf.fit_transform(corpus)
    results = results.toarray()
    if normalize_results:
        results = sklearn.preprocessing.normalize(results)
    tfidf_df = pd.DataFrame(sklearn.preprocessing.normalize(results), columns = tfidf.get_feature_names(), index=range(1, len(corpus) + 1))
    return tfidf_df


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
