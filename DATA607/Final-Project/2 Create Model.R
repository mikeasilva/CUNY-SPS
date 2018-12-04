library(DBI)
library(RSQLite)
library(dplyr)
library(stringr)
library(caret)
library(ranger)

## Final Data Wrangling

# Get the SQLite database
if(!file.exists("Monroe Real Property Data.db")){
  if(!file.exists("Monroe Real Property Data.db.tar.gz")){
    # Download this specific commit from my GitHub repo
    download.file("https://github.com/mikeasilva/CUNY-SPS/raw/9a2023b57a466550646c9190076a53d51ef09ef2/data/Monroe%20Real%20Property%20Data.db.tar.gz", "Monroe Real Property Data.db.tar.gz")
  }
  # Decompress the file
  untar("Monroe Real Property Data.db.tar.gz")
  # Delete the zipped file
  unlink("Monroe Real Property Data.db.tar.gz")
}

# Connect to the database
con <- dbConnect(RSQLite::SQLite(), "Monroe Real Property Data.db")

# Get the latest unduplicated sales price data
results <- dbSendQuery(con, "SELECT MAX(sale_date) AS sale_date, SWIS, SBL FROM sales_data GROUP BY SWIS, SBL HAVING sale_date > '2015-12-31'")
df <- dbFetch(results) 

dbClearResult(results)

df <- dbReadTable(con, "sales_data") %>% # Pull all the records
  distinct() %>% # remove any duplicates
  merge(df) # Merge with the targeted sales observations

df <- df %>%
  group_by(SWIS, SBL) %>% 
  summarise(count = n()) %>% # Get the number of records
  ungroup() %>%
  filter(count == 1) %>% # Only keep the observations with one price
  select(-count) %>% # Drop the count column
  merge(df) # subset the price observations

df <- dbReadTable(con, "property_info") %>% # Pull all the housing attributes
  distinct() %>% # remove any duplicates
  merge(df) # Merge with the targeted sales observations

# Disconnect from the database
dbDisconnect(con)

# Clean up the data
df <- df %>%
  select(-sale_date, -index, -SBL, -SWIS, -SQ_FT, -ACRES) %>% # Drop the unneeded columns
  filter(YR_BLT > 0) %>% # Must have a year it was built
  filter(SQFT_LIV > 0) %>% # Must have a square footage
  filter(NBR_KITCHN > 0) %>% # Must have a kitchen
  filter(NBR_BEDRM > 0) %>% # Must have a bedroom
  filter(price > 9999) %>% # Can't be absurdly low
  filter(price < 300001) %>% # Can't be really high
  filter(str_length(HEAT_DESC) > 1) %>% # Must have a heat description
  filter(str_length(FUEL_DESC) > 1) %>% # Must have a fueld description
  select(-MUNI_NAME, -SCH_NAME) %>% # Drop the location attributes
  mutate_if(is.character, as.factor) # Convert all character data to factors


## Model Building

# Make this reproducible
set.seed(1234)

# Split the data into training and test sets
in_training <- createDataPartition(df$price, p = 0.8, list = FALSE)
training <- df[ in_training,]
testing  <- df[-in_training,]

# Simplify the model using recursive feature elimination
outcome <- 'price'
predictors <- names(training)[!names(training) %in% outcome]

#Sys.time()
#results <- rfe(training[, predictors], training[, outcome], rfeControl = rfeControl(rfFuncs, method = "repeatedcv", repeats = 3))
#Sys.time()

results

# Pick the top five predictors and the outcome variable as the model features
features <- c(outcome, 'SQFT_LIV', 'YR_BLT', 'CALC_ACRES', 'BLDG_DESC', 'NBR_F_BATH')

training <- training[, features]
testing <- testing[, features]

# Build the random forest model using 10-fold CV
fit_control <- trainControl(method = "cv", number = 10)
rf_model <- train(price ~ ., data = training, method = "ranger", trControl = fit_control)

# Summary of the rf_model object
#
# Random Forest 
# 
# 16068 samples
# 5 predictor
# 
# No pre-processing
# Resampling: Cross-Validated (10 fold) 
# Summary of sample sizes: 14462, 14461, 14461, 14463, 14461, 14460, ... 
# Resampling results across tuning parameters:
#   
#   mtry  splitrule   RMSE      Rsquared   MAE     
# 2    variance    39808.92  0.5851907  29899.16
# 2    extratrees  45716.32  0.4678293  35243.95
# 9    variance    37096.30  0.6164472  26828.11
# 9    extratrees  37179.45  0.6149292  27051.34
# 16    variance    37638.39  0.6059070  27231.60
# 16    extratrees  37635.24  0.6055927  27254.98
# 
# Tuning parameter 'min.node.size' was held constant at a
# value of 5
# RMSE was used to select the optimal model using the
# smallest value.
# The final values used for the model were mtry = 9,
# splitrule = variance and min.node.size = 5.

## Cleanup the environment
rm(con)
rm(df)
rm(fit_control)
rm(in_training)
rm(outcome)
rm(predictors)
rm(results)

## Save the environment
save.image(file = "model.RData")