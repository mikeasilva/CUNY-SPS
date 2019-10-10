library(dplyr)
library(ggplot2)

confusion_matrix <- function(df, actual, predicted){
  cm <- table(df[[predicted]], df[[actual]])
  if (nrow(cm) == ncol(cm)){
    return(cm)
  }
  # Make sure all missing values are present in the confusion matrix
  fixed_cm <- matrix(0, ncol(cm), ncol(cm))
  colnames(fixed_cm) <- colnames(cm)
  rownames(fixed_cm) <- colnames(cm)
  # Horribly inefficient at large scale but since we're dealing with a
  # confusion matrix...
  for (r in rownames(cm)){
    for (c in colnames(cm)){
      fixed_cm[r, c] <- cm[r, c]
    }
  }
  return(fixed_cm)
}

confusion_matrix_outcomes <- function(cm){
  # This will obviously need some work to handle more than a 2x2 matrix
  TP <- cm[1]
  FN <- cm[2]
  FP <- cm[3]
  TN <- cm[4]
  list("TN" = TN, "FP" = FP, "FN" = FN, "TP" = TP)
}

# Write a function that takes the data set as a dataframe, with actual and 
# predicted classifications identified, and returns the accuracy of the 
# predictions.

accuracy <- function(df, actual, predicted){
  cm <- confusion_matrix_outcomes(confusion_matrix(df, actual, predicted))
  (cm$TP + cm$TN) / (cm$TP + cm$FP + cm$TN + cm$FN)
}

# Write a function that takes the data set as a dataframe, with actual and 
# predicted classifications identified, and returns the classification error 
# rate of the predictions.

classification_error_rate <- function(df, actual, predicted){
  cm <- confusion_matrix_outcomes(confusion_matrix(df, actual, predicted))
  (cm$FP + cm$FN) / (cm$TP + cm$FP + cm$TN + cm$FN)
}

# Write a function that takes the data set as a dataframe, with actual and 
# predicted classifications identified, and returns the precision of the 
# predictions.

precision <- function(df, actual, predicted){
  cm <- confusion_matrix_outcomes(confusion_matrix(df, actual, predicted))
  cm$TP / (cm$TP + cm$FP)
}

# Write a function that takes the data set as a dataframe, with actual and 
# predicted classifications identified, and returns the sensitivity of the 
# predictions. Sensitivity is also known as recall.

sensitivity <- function(df, actual, predicted){
  cm <- confusion_matrix_outcomes(confusion_matrix(df, actual, predicted))
  cm$TP / (cm$TP + cm$FN)
}

recall <- function(df, actual, predicted){
  sensitivity(df, actual, predicted)
}

# Write a function that takes the data set as a dataframe, with actual and
# predicted classifications identified, and returns the specificity of the
# predictions.

specificity <- function(df, actual, predicted){
  cm <- confusion_matrix_outcomes(confusion_matrix(df, actual, predicted))
  cm$TN / (cm$TN + cm$FP)
}

# Write a function that takes the data set as a dataframe, with actual and
# predicted classifications identified, and returns the F1 score of the
# predictions.

f1_score <- function(df, actual, predicted){
  p <- precision(df, actual, predicted)
  s <- sensitivity(df, actual, predicted)
  (2 * p * s) / (p + s)
}

# Write a function that generates an ROC curve from a data set with a true
# classification column (class in our example) and a probability column
# (scored.probability in our example). Your function should return a list
# that includes the plot of the ROC curve and a vector that contains the
# calculated area under the curve (AUC). Note that I recommend using a
# sequence of thresholds ranging from 0 to 1 at 0.01 intervals.

roc_curve <- function(df, actual, probability, interval = 0.01){
  outcome <- data.frame(matrix(ncol = 3, nrow = 0))
  names(outcome) <- c("probability", "TPR", "FPR")
  for (threshold in seq(0, 1, interval)){
    df$roc_prediction <- ifelse(df[[probability]] > threshold, 1, 0)
    tpr <- sensitivity(df, actual, "roc_prediction")
    fpr <- 1 - specificity(df, actual, "roc_prediction")
    row <- data.frame(probability = threshold, TPR = tpr, FPR = fpr)
    outcome <- rbind(outcome, row)
  }
  # Compute the area
  outcome$area <- (outcome$FPR - dplyr::lag(outcome$FPR)) * outcome$TPR
  # Fill in missing values with zeros
  outcome <- outcome %>%
    mutate(area = ifelse(is.na(area), 0, area))
  # Create a vector of area under the curve
  auc_vector <- outcome$area
  names(auc_vector) <- outcome$probability
  # Sum it to get total area under the curve
  auc <- sum(auc_vector)
  # Create a ROC plot
  roc_plot <- ggplot(outcome) +
    geom_line(aes(FPR, TPR), color = "dodger blue") +
    xlab("False Positive Rate (FPR)") +
    ylab("True Positive Rate (TPR)") +
    theme_minimal() +
    annotate(geom = "text", x = 0.7, y = 0.07,
             label = paste("AUC:", round(auc, 3))) +
    geom_abline(intercept = 0, slope = 1, linetype = "dashed") +
    coord_equal(ratio = 1)
  # Return the list
  return(list(plot = roc_plot, auc = auc, auc_vector = auc_vector))
}
