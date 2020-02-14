## Prophet Example
library(tidyverse)
library(prophet)

## Download NIFRS data
if(!file.exists("NIFRS.csv")){
  download.file("https://github.com/mikeasilva/CUNY-SPS/raw/master/DATA624/NIFRS.csv", "NIFRS.csv")
}

## Read in the data
df <- read.csv("NIFRS.csv")

## Split out training set
training <- df %>%
  filter(YEAR < 2018) %>%
  rename(ds = IN_DATE) %>%
  group_by(ds) %>%
  tally() %>%
  rename(y = n)

## Build a model & produce forecasts
model <- prophet(training)
future_df <- make_future_dataframe(model, periods = 365)
forecast <- predict(model, future_df)

## Plot the model forecasts
plot(model, forecast)

## Plot the decomposition
prophet_plot_components(model, forecast)