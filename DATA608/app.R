library(shiny)
library(dplyr)
library(ggplot2)
library(plotly)
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
                 tabPanel("2010 Ranking",
                          selectInput("cause_of_death", "Cause of Death:", options, width = "100%"),
                          mainPanel(
                              plotlyOutput("rank_plot", height = "600px")
                            )
                          )
                 )

server <- function(input, output) {
    
    # change_over_time <- reactive({
    #     temp <- df %>%
    #         filter(ICD.Chapter == cause_of_death)
    #     
    #     us <- temp %>%
    #         group_by(Year) %>%
    #         summarise(Deaths = sum(Deaths),
    #                   Population = sum(Population)) %>%
    #         mutate(ICD.Chapter = input$cause_of_death,
    #                State = "US",
    #                Crude.Rate = round(Deaths / Population * 100000, 1)) %>%
    #         select(ICD.Chapter, State, Year, Deaths, Population, Crude.Rate)
    #     
    #     return(bind_rows(temp, us))
    # })
    
    output$rank_plot <- renderPlotly({
        temp <- df %>%
            filter(Year == 2010 & ICD.Chapter == input$cause_of_death) %>%
            arrange(Crude.Rate) %>%
            rename(`Mortality Rate` = Crude.Rate,
                   `State Name` = state_name) %>%
            mutate(Rank = row_number())
        n_group <- nrow(temp) / 5
        p <- temp %>%
            mutate(color = as.factor(ceiling(Rank / n_group))) %>%
            ggplot(aes(y = `Mortality Rate`, x = Rank, text = `State Name`,  fill = color)) +
            scale_fill_brewer(palette = "Set1") +
            geom_bar(stat = "identity")+
            #geom_text(aes(label=Crude.Rate), color="white", size=2, nudge_x = 2)+
            theme_minimal() +
            theme(legend.position = "none", 
                  axis.title.y = element_blank(),
                  axis.text.y = element_blank(),
                  axis.ticks.y = element_blank()) +
            labs(y = "Mortality Rate", x = "") +
            coord_flip()
        
            ggplotly(p) %>% 
                config(displayModeBar = F) %>% 
                layout(dragmode = "select")
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
