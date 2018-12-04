library(shiny)
library(dplyr)
library(ggplot2)
library(ggthemes)
library(tidyr)
library(caret)
library(ranger)
library(FNN)

load("model.RData")

# Get the unique set of architectural styles
building_description_options <- testing %>%
  select(BLDG_DESC) %>%
  arrange(BLDG_DESC) %>%
  unique() 
building_description_options <- building_description_options$BLDG_DESC

# Get the architectural style that is most prevalant in the data
building_description_mode <- testing %>%
  group_by(BLDG_DESC) %>%
  summarise(count = n()) %>%
  arrange(-count)
building_description_mode <- building_description_mode[1, ]$BLDG_DESC

# Define the User Interface
ui <- navbarPage("Rochester Housing Sale Price",
                 tabPanel("Get a Prediction",
                          # List the housing price determinants
                          sidebarPanel(
                            # The size in square feet
                            sliderInput("SQFT_LIV", 
                                        "Square Footage:",
                                        min = min(testing$SQFT_LIV), 
                                        max = max(testing$SQFT_LIV),
                                        value = median(testing$SQFT_LIV), 
                                        step = 1,
                                        pre = "", 
                                        sep = ",",
                                        animate = TRUE),
                            
                            # Display the acres from the data
                            sliderInput("CALC_ACRES", 
                                        "Plot Size (Acres):",
                                        min = round(min(testing$CALC_ACRES), 1), 
                                        max = round(max(testing$CALC_ACRES), 1),
                                        value = round(median(testing$CALC_ACRES), 1), 
                                        step = 0.1,
                                        pre = "", 
                                        sep = "",
                                        animate = TRUE),
                            
                            # Display the year from the data
                            sliderInput("YR_BLT", 
                                        "Year Built:",
                                        min = min(testing$YR_BLT), 
                                        max = max(testing$YR_BLT),
                                        value = median(testing$YR_BLT), 
                                        step = 1,
                                        pre = "", 
                                        sep = "",
                                        animate = TRUE),
                            
                            # Display the number of full bathrooms from the data
                            sliderInput("NBR_F_BATH", 
                                        "Full Bathrooms:",
                                        min = min(testing$NBR_F_BATH), 
                                        max = max(testing$NBR_F_BATH),
                                        value = median(testing$NBR_F_BATH), 
                                        step = 1,
                                        pre = "", 
                                        sep = "",
                                        animate = TRUE),
                            
                            # Display the list of building styles extracted from the data
                            selectInput("BLDG_DESC", 
                                        "Architectural Style:",
                                        choices = building_description_options,  
                                        selected = building_description_mode)
                          ),
                          
                          # Show prediction and reliability plot
                          mainPanel(
                            h1(textOutput("prediction")),
                            htmlOutput("moe"),
                            plotOutput(outputId = "prediction_plot")
                            
                          )
                 ),
                 tabPanel("About this Model",
                          h2("Introduction"),
                          p("The Rochester Housing Sale Price is a project created by Mike Silva.  It is a final project for the CUNY Masters in Data Science DATA 607 course. It predicts the sales price of a home based on a few characteristics.  All code is reproducible and available at https://github.com/mikeasilva/CUNY-SPS/tree/master/DATA607/Final-Project."),
                          ## Add note about leaving out location as a variable although it would increase the predictive value
                          plotOutput(outputId = "acs_plot")
                 )
)

# Define server logic required to draw a histogram
server <- function(input, output) {
  prediction_inputs <- reactive({
    # Build a data frame to make a prediction
    bd <- testing %>%
      filter(BLDG_DESC == input$BLDG_DESC)
    
    bd <- bd[1,]$BLDG_DESC
    data.frame(SQFT_LIV = input$SQFT_LIV, YR_BLT = input$YR_BLT, CALC_ACRES = input$CALC_ACRES, BLDG_DESC = bd, NBR_F_BATH = input$NBR_F_BATH)
  })
  
  predicted_price <- reactive({
    # Build a data frame to make a prediction
    newdata <- prediction_inputs()
    # Return the predicted price
    round(predict.train(rf_model, newdata), 0)
  })
  
  nearest_neighbors <- reactive({
    # Send back the 20 nearest neighbor indices from the testing data
    test_data <- testing %>%
      filter(BLDG_DESC == input$BLDG_DESC)
    
    data <- test_data %>%
      select(-price) %>% # Remove the price
      mutate_if(is.factor, as.numeric) # Convert factor to numeric
    
    query <- prediction_inputs() %>%
      mutate_if(is.factor, as.numeric) # Convert factor to numeric
    
    k <- FNN::knn(data, query, test_data$price, k = 20)
    attr(k, "nn.index")
  })
  
  output$prediction <- renderText({
    # Get the predicted price
    predicted_price <-predicted_price()
    paste0("The predicted sale price is: $", prettyNum(predicted_price, big.mark = ",", scientific = FALSE))
  })
  
  output$moe <- renderText({
    # Get the predicted price
    predicted_price <-predicted_price()
    
    # Compute the "margin of error"
    moe <- testing[nearest_neighbors(),] 
    moe$predicted_price <- predict.train(rf_model, moe)
    
    moe <- moe %>%
      mutate(difference = predicted_price - price) %>%
      summarise(difference = mean(difference))
    
    moe <- round(moe$difference, 0)
    
    if(moe > 0){
      over_under = "over"
    } else {
      over_under = "under"
    }
    
    paste0("<h2>How accurate is the prediction?</h2><p>Predicting housing prices is a tricky business.  To give an idea of the accuracy of the prediction look at the twenty peer houses.  The actual sales price is on the x-axis and the prediction on the y-axis.  If the prediction is 100% accurate, the points would fall on the dashed red line.  The model <b>", over_under, " estimates by $", prettyNum(moe, big.mark = ",", scientific = FALSE), "</b> on average.</p>")
  })
  
  output$prediction_plot <- renderPlot({
    
    viz_data <- testing[nearest_neighbors(),] 
    viz_data$predicted_price <- predict.train(rf_model, viz_data)
    
    
    g <- ggplot(viz_data, aes(x=price/1000, y=predicted_price/1000, color='red')) +
      geom_point() + 
      scale_color_fivethirtyeight() +
      xlim(0, max(testing$price)/1000) + 
      ylim(0, max(testing$price)/1000) +
      geom_abline(intercept=0, slope=1, color="red", linetype = 2) +
      labs(title = "Predicted vs Actual Sale Price (thousands)", x = "Actual Sale Price (thousands)", y = "Predicted Sale Price (thousands)") + 
      theme_fivethirtyeight(base_size = 12, base_family = "sans") +
      guides(fill = FALSE, color = FALSE, shape = FALSE)  
    
    print(g)
  })
  
  output$acs_plot <- renderPlot({
    # Used to map observations to ACS value categories
    get_acs_value <- function(price){
      if(price < 50000){
        return("1. Less than $50,000")
      } else if(price < 100000){
        return("2. $50,000 to $99,999")
      }else if(price < 150000){
        return("3. $100,000 to $149,999")
      }else if(price < 200000){
        return("4. $150,000 to $199,999")
      }else if(price < 300000){
        return("5. $200,000 to $299,999")
      }else if(price < 500000){
        return("6. $300,000 to $499,999")
      }else if(price < 1000000){
        return("7. $500,000 to $999,999")
      }else{
        return("8. $1,000,000 or more")
      }
    }
    # Wrangle the data
    check <- training %>%
      rowwise() %>%
      mutate(acs_value = get_acs_value(price)) %>%
      ungroup() %>%
      group_by(acs_value) %>%
      summarise(study = n()) %>%
      arrange(acs_value)
    
    # Add in the missing last two categories
    check <- rbind(check, data.frame("acs_value" = c("7. $500,000 to $999,999", "8. $1,000,000 or more"), study = c(0)))
    
    # Monroe County Home Value Table C25075
    check$acs <- c(9747, 32746, 54988, 38988, 34563, 14926, 3247, 924)
    
    # Compute the shares
    check <- check %>%
      mutate(acs_total = sum(acs)) %>%
      mutate(study_total = sum(study)) %>%
      mutate(acs_share = (acs / acs_total)*100) %>%
      mutate(study_share = (study / study_total)*100) %>%
      select(acs_value, acs_share, study_share) %>%
      rename(ACS = acs_share) %>%
      rename(`Model Data` = study_share) %>%
      gather(Dataset, Share, -acs_value) %>%
      rename(Value = acs_value) 
    
    g <- ggplot(check, aes(x = reorder(Value, desc(Value)), Share, color=Dataset, fill=Dataset)) +
      geom_bar(position = "dodge", stat = "identity") +
      coord_flip() + 
      ggtitle("Percent of Homes by Value and Data Set") +
      scale_color_fivethirtyeight() +
      scale_fill_fivethirtyeight() + 
      theme_fivethirtyeight(base_size = 12, base_family = "sans")
    
    print(g)
  })
  
}

# Run the application 
shinyApp(ui = ui, server = server)
