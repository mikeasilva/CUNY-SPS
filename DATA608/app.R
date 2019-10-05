library(shiny)
library(dplyr)
library(ggplot2)
library(plotly)
library(scales)
#library(usmap)
#library(gridExtra)
#library(socviz)
#library(ggthemes)

xwalk <- read.csv("data/xwalk.csv", colClasses=c("state_fips"="character"))

df <- read.csv("data/cleaned-cdc-mortality-1999-2010-2.csv") %>%
    merge(xwalk)

# 2010 Ranking options
options <- filter(df, Year == 2010) %>%
    mutate(ICD.Chapter = as.character(ICD.Chapter))
options <- unique(sort(options$ICD.Chapter))


ui <- navbarPage("Cause of Death",
                 tabPanel("States by Rank in 2010",
                          selectInput("cause_of_death", "Cause of Death:", options, width = "100%"),
                          mainPanel(
                              plotlyOutput("rank_plot", height = "700px")
                            , width = 12)
                          )
                 )

server <- function(input, output) {
    
    output$rank_plot <- renderPlotly({
        # Wrangle the data
        plot_df <- df %>%
            filter(Year == 2010 & ICD.Chapter == input$cause_of_death) %>%
            arrange(Crude.Rate) %>%
            rename(`Mortality Rate` = Crude.Rate,
                   `State Name` = state_name) %>%
            mutate(Rank = row_number())
        n_group <- nrow(plot_df) / 5
        plot_df <- plot_df %>%
            mutate(color = as.factor(ceiling(Rank / n_group))) 
        # This is to help position the text
        text_y <- max(plot_df$`Mortality Rate`) / - 100
        max_rank <- max(plot_df$Rank) - 2
        # Create the ggplot
        p <- ggplot(plot_df, aes(x = Rank, y = `Mortality Rate`, text = paste("State:", `State Name`),  fill = color)) +
            scale_fill_brewer(palette = "Set1") +
            geom_bar(stat = "identity")+
            scale_x_continuous(limits=c(2, max_rank), oob = rescale_none) +
            theme_minimal() +
            theme(legend.position = "none", 
                  panel.grid.major.y = element_blank(),
                  axis.title.y = element_blank(),
                  axis.text.y = element_blank(),
                  axis.ticks.y = element_blank()) +
            labs(y = "Deaths per 100,000", x = "") +
            geom_text(data = plot_df, aes(x = Rank, y = text_y, label = State), color = "black", size = 2) + 
            coord_flip()
        # Load it into plotly
        ggplotly(p) %>% 
            config(displayModeBar = F) %>%
            layout(margin = list(t = 0))
    })
    
    output$ranking_map <- renderPlot({
        df %>%
            filter(Year == 2010 & ICD.Chapter == input$cause_of_death) %>%
            rename(state = State) %>%
            plot_usmap("state", data = ., values = "Crude.Rate",  color = "white") +
            scale_fill_continuous(type = "viridis", name = "Death Rate") +
            theme(legend.position = "right")
    })
}

# Run the application 
shinyApp(ui = ui, server = server)
