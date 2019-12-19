# CoIL Challenge Source Code
library(tidyverse)
library(caret)

## Download the data sets from UCI if they are not present
url <- "https://archive.ics.uci.edu/ml/machine-learning-databases/tic-mld/"
files <- c("ticdata2000.txt", "ticeval2000.txt", "tictgts2000.txt")
for (file_name in files) {
  file_path <- paste0("data/", file_name)
  file_url <- paste0(url, file_name)
  if (!file.exists(file_path)) {
    message(paste("Downloading", file_name))
    download.file(file_url, file_path)
  }
}

## Read in and clean the data
prepare_data <- function(df){
  names(df) <- c(
    "MOSTYPE", "MAANTHUI", "MGEMOMV", "MGEMLEEF", "MOSHOOFD", "MGODRK",
    "MGODPR", "MGODOV", "MGODGE", "MRELGE", "MRELSA", "MRELOV", "MFALLEEN",
    "MFGEKIND", "MFWEKIND", "MOPLHOOG", "MOPLMIDD", "MOPLLAAG", "MBERHOOG",
    "MBERZELF", "MBERBOER", "MBERMIDD", "MBERARBG", "MBERARBO", "MSKA",
    "MSKB1", "MSKB2", "MSKC", "MSKD", "MHHUUR", "MHKOOP", "MAUT1", "MAUT2",
    "MAUT0", "MZFONDS", "MZPART", "MINKM30", "MINK3045", "MINK4575",
    "MINK7512", "MINK123M", "MINKGEM", "MKOOPKLA", "PWAPART", "PWABEDR", 
    "PWALAND", "PPERSAUT", "PBESAUT", "PMOTSCO", "PVRAAUT",  "PAANHANG",
    "PTRACTOR", "PWERKT", "PBROM", "PLEVEN", "PPERSONG", "PGEZONG",
    "PWAOREG", "PBRAND", "PZEILPL", "PPLEZIER", "PFIETS", "PINBOED",
    "PBYSTAND", "AWAPART", "AWABEDR", "AWALAND", "APERSAUT", "ABESAUT",
    "AMOTSCO", "AVRAAUT", "AAANHANG", "ATRACTOR", "AWERKT", "ABROM",
    "ALEVEN", "APERSONG", "AGEZONG", "AWAOREG",  "ABRAND", "AZEILPL",
    "APLEZIER", "AFIETS", "AINBOED", "ABYSTAND", "CARAVAN")
  
  MOSTYPE_labels <- c(
    "1" = "1 High Income, expensive child",
    "2" = "2 Very Important Provincials",
    "3" = "3 High status seniors",
    "4" = "4 Affluent senior apartments",
    "5" = "5 Mixed seniors",
    "6" = "6 Career and childcare",
    "7" = "7 Dinki's (double income no kids)",
    "8" = "8 Middle class families",
    "9" = "9 Modern, complete families",
    "10" = "10 Stable family",
    "11" = "11 Family starters",
    "12" = "12 Affluent young families",
    "13" = "13 Young all american family",
    "14" = "14 Junior cosmopolitan",
    "15" = "15 Senior cosmopolitans",
    "16" = "16 Students in apartments",
    "17" = "17 Fresh masters in the city",
    "18" = "18 Single youth",
    "19" = "19 Suburban youth",
    "20" = "20 Ethnically diverse",
    "21" = "21 Young urban have-nots",
    "22" = "22 Mixed apartment dwellers",
    "23" = "23 Young and rising",
    "24" = "24 Young, low educated",
    "25" = "25 Young seniors in the city",
    "26" = "26 Own home elderly",
    "27" = "27 Seniors in apartments",
    "28" = "28 Residential elderly",
    "29" = "29 Porchless seniors: no front yard",
    "30" = "30 Religious elderly singles",
    "31" = "31 Low income catholics",
    "32" = "32 Mixed seniors",
    "33" = "33 Lower class large families",
    "34" = "34 Large family, employed child",
    "35" = "35 Village families",
    "36" = "36 Couples with teens 'Married with children'",
    "37" = "37 Mixed small town dwellers",
    "38" = "38 Traditional families",
    "39" = "39 Large religous families",
    "40" = "40 Large family farms",
    "41" = "41 Mixed rurals")
  
  MGEMLEEF_labels <- c(
    "1" = "20-30 years",
    "2" = "30-40 years",
    "3" = "40-50 years",
    "4" = "50-60 years",
    "5" = "60-70 years",
    "6" = "70-80 years")
  
  MOSHOOFD_labels <- c(
    "1" = "Successful hedonists",
    "2" = "Driven Growers",
    "3" = "Average Family",
    "4" = "Career Loners",
    "5" = "Living well",
    "6" = "Cruising Seniors",
    "7" = "Retired and Religeous",
    "8" = "Family with grown ups",
    "9" = "Conservative families",
    "10" = "Farmers")
  
  MGODRK_labels <- c(
    "0" = "0%",
    "1" = "1 - 10%",
    "2" = "11 - 23%",
    "3" = "24 - 36%",
    "4" = "37 - 49%",
    "5" = "50 - 62%",
    "6" = "63 - 75%",
    "7" = "76 - 88%",
    "8" = "89 - 99%",
    "9" = "100%")
  
  PWAPART_labels <- c(
    "0" = "f 0",
    "1" = "f 1 - 49",
    "2" = "f 50 - 99",
    "3" = "f 100 - 199",
    "4" = "f 200 - 499",
    "5" = "f 500 - 999",
    "6" = "f 1000 - 4999",
    "7" = "f 5000 - 9999",
    "8" = "f 10,000 - 19,999",
    "9" = "f 20,000 - ?")
  
  set_to_1 <- c(12, 8, 6, 7, 1, 2, 36, 3, 37, 10, 20, 38, 11)
  
  df %>%
    mutate(LIKELY_CUSTOMERS = ifelse(MOSTYPE %in% set_to_1, 1, 0)) %>%
    mutate(LIKELY_CUSTOMERS = as.factor(LIKELY_CUSTOMERS)) %>%
    mutate(DRIVEN_GROWERS = ifelse(MOSHOOFD == "2", 1, 0)) %>%
    mutate(DRIVEN_GROWERS = as.factor(DRIVEN_GROWERS)) %>%
    mutate(MOSTYPE = as.factor(MOSTYPE),
           MGEMLEEF = as.factor(MGEMLEEF),
           MOSHOOFD = as.factor(MOSHOOFD),
           MGODRK = as.factor(MGODRK),
           PWAPART = as.factor(PWAPART),
           CARAVAN = as.factor(CARAVAN)) %>%
    mutate(MOSTYPE = recode(MOSTYPE, !!!MOSTYPE_labels),
           MGEMLEEF = recode(MGEMLEEF, !!!MGEMLEEF_labels),
           MOSHOOFD = recode(MOSHOOFD, !!!MOSHOOFD_labels),
           MGODRK = recode(MGODRK, !!!MGODRK_labels),
           PWAPART = recode(PWAPART, !!!PWAPART_labels))
}

eval <- read.delim("data/ticeval2000.txt", header = FALSE)
temp <- read.delim("data/tictgts2000.txt", header = FALSE)
eval$CARAVAN <- temp$V1
eval <- prepare_data(eval)
df <- prepare_data(read.delim("data/ticdata2000.txt", header = FALSE))

## Create the train and test sets
set.seed(42)
train_index <- createDataPartition(df$CARAVAN, p = .7, list = FALSE)
train <- df[train_index,]
test <- df[-train_index,]

## Correct the data imbalance through over sampling
up_train <- upSample(x = select(train, -CARAVAN), 
                     y = train$CARAVAN,
                     yname = "CARAVAN") 

## Looking for important variables
# set.seed(42)
# library(randomForest)
# rf_fit <- randomForest(CARAVAN ~ ., up_train)
# varImpPlot(rf_fit)

## Find likely customer types
MOSTYPE_crosstab <- up_train %>%
  select(CARAVAN, MOSTYPE) %>%
  table() %>%
  data.frame()

MOSTYPE_crosstab <- MOSTYPE_crosstab %>%
  group_by(MOSTYPE) %>%
  summarise(total = sum(Freq)) %>%
  merge(MOSTYPE_crosstab) %>%
  mutate(share = Freq / total) %>%
  filter(CARAVAN == 1, share > 0.5) %>%
  arrange(desc(share)) %>%
  select(MOSTYPE, share)

MOSTYPE_crosstab

## Model Building & Evaluation

score_model <- function(model, data, threshold = 0.5, predictions = FALSE){
## Provides model scoring data
#
# INPUTS
#
# model = logit model object
# data = data frame to make predictions for
# threshold (optional) = the cutpoint to assign a 1 or 0 response
# predictions (optional) = 1 or 0 you want to use for the predicitions
# 
# RETURNS (list)
#
# cm = Confusion Matrix output from caret
# correct = the number of correct CARAVAN = 1 predictions
# specificity = the specificity of the CARAVAN = 1 predictions
  
  # Generate the predicted outcome
  if(!predictions){
    glm_predictions <- suppressWarnings(predict.glm(model, data, "response"))
    predictions <- ifelse(glm_predictions >= threshold, 1, 0)
  }
  data$yhat <- predictions
  
  # Generate a confusion matrix
  cm <- confusionMatrix(factor(predictions), factor(data$CARAVAN))
  
  # Get the number of correct CARAVAN = 1 Predictions
  correct <- data %>%
    filter(yhat == 1,
           yhat == CARAVAN) %>%
    nrow(.)
  
  # Get the specificity of the model's CARAVAN = 1 Predictions
  specificity <- correct / nrow(data[data$CARAVAN == 1,])
  
  # Return the data as a list
  return(list("cm" = cm, "correct" = correct, "specificity" = specificity))
}

robust_results <- function(model_formula, correction = "upSample", n_tries = 250){
## Trains and evaluates the model multiple times
#
# INPUTS
#
# model_formula = The formula for the logit model
# correction (optional) = Correct for imbalanced data (i.e. upSample, downSample, none)
# n_tries (optional) =  The number of runs (250 default)
# 
# RETURNS (data.frame)
#
# seed = random number seed
# correct = the number of correct CARAVAN = 1 predictions
# specificity = the specificity of the CARAVAN = 1 predictions
  
  # Convert the formula from a string
  model_formula <- as.formula(model_formula)
  # Begin the loop
  for(seed in 1:n_tries){
      set.seed(seed)
      # Because some models fail we need to use a try except
      success = tryCatch({
        # Split the data
        train_index <- createDataPartition(df$CARAVAN, p = .7, list = FALSE)
        train <- df[train_index,]
        test_df <- df[-train_index,]
        if(correction == "upSample"){
          # Correct the data imbalance through over sampling
          training_df <- upSample(x = select(train, -CARAVAN), 
                                  y = train$CARAVAN, 
                                  yname = "CARAVAN")
        } else if(correction == "downSample"){
          # Correct the data imbalance through under sampling
          training_df <- downSample(x = select(train, -CARAVAN), 
                                    y = train$CARAVAN, 
                                    yname = "CARAVAN")
        } else {
          # No correction
          training_df <- train
        }
        # Build the model
        model <- glm(model_formula, 
                     family = binomial(link = "logit"), 
                     training_df)
        # See how it preforms
        results <- score_model(model, test_df)
        # Store the results
        temp <- data.frame("seed" = seed,
                           "correct" = results$correct,
                           "specificity" = results$specificity)
        if(exists("the_results")){
          the_results <- bind_rows(the_results, temp)
        } else {
          the_results <- temp
        }
      }, error = function(e) {
        # Something bad happened
        return(FALSE)
      })
  }
  # Return the data.frame of results
  return(the_results)
}

### Model 1 - Top 5 Important Variables from Random Forest
model1 <- glm(CARAVAN ~ MOSTYPE + PPERSAUT + MOSHOOFD + PBRAND + APERSAUT, 
              family = binomial(link = "logit"),
              up_train)
model1_results <- score_model(model1, test)
model1_results$specificity
model1_robust_results <- robust_results("CARAVAN ~ MOSTYPE + PPERSAUT + MOSHOOFD + PBRAND + APERSAUT")
summary(model1_robust_results$specificity)

### Model 2 - Likely Customers and Car Policies Contribution Level
model2 <- glm(CARAVAN ~ LIKELY_CUSTOMERS + PPERSAUT,
              family = binomial(link = "logit"),
              up_train)
model2_results <- score_model(model2, test)
model2_results$specificity
model2_robust_results <- robust_results("CARAVAN ~ LIKELY_CUSTOMERS + PPERSAUT")
summary(model2_robust_results$specificity)

### Model 3 - Likely Customers and Car Policies Contribution Level and whether or not they are a driven grower
model3 <- glm(CARAVAN ~ LIKELY_CUSTOMERS + PPERSAUT + DRIVEN_GROWERS,
              family = binomial(link = "logit"),
              up_train)
model3_results <- score_model(model3, test)
model3_results$specificity
model3_robust_results <- robust_results("CARAVAN ~ LIKELY_CUSTOMERS + PPERSAUT + DRIVEN_GROWERS")
summary(model3_robust_results$specificity)

## Final Model Accuracy
final_model <- score_model(model3, eval)
final_model$correct
final_model$specificity

## Test Final Model
set.seed(42)
down_train <- downSample(x = select(train, -CARAVAN),
                         y = train$CARAVAN,
                         yname = "CARAVAN") 
model3_down <- glm(CARAVAN ~ LIKELY_CUSTOMERS + PPERSAUT + DRIVEN_GROWERS,
                   family = binomial(link = "logit"),
                   down_train)
model3_down_robust_results <- robust_results("CARAVAN ~ LIKELY_CUSTOMERS + PPERSAUT + DRIVEN_GROWERS", "downSample")

model3_down_score <- score_model(model3_down, eval)