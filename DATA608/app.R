library(shiny)
library(dplyr)
library(ggplot2)
library(plotly)
library(scales)

xwalk <- read.csv("data/xwalk.csv", colClasses=c("state_fips"="character"))
df <- read.csv("data/cleaned-cdc-mortality-1999-2010-2.csv") %>% merge(xwalk)
state_options <- sort(df$state_name)

# 2010 Ranking options
options <- filter(df, Year == 2010) %>%
    mutate(ICD.Chapter = as.character(ICD.Chapter))
options <- unique(sort(options$ICD.Chapter))

ui <- navbarPage("Cause of Death",
                 
                 tabPanel("States by Rank in 2010",
                          selectInput("cause_of_death", "Cause of Death:", options, width = "100%"),
                          mainPanel(plotlyOutput("rank_plot", height = "700px"), width = 12)
                          ),
                 
                 tabPanel("Improvement vs National Average",
                          selectInput("cause_of_death_2", "Cause of Death:", options, width = "100%"),
                          selectInput("highlight", "Highlight:", state_options, width = "100%"),
                          mainPanel(plotlyOutput("improvement_plot"), width = 12)
                 )
)

server <- function(input, output) {
    
    output$rank_plot <- renderPlotly({
        # Wrangle the data
        plot_df <- df %>%
            filter(Year == 2010 & ICD.Chapter == input$cause_of_death) %>%
            arrange(Crude.Rate) %>%
            mutate(Rank = row_number())
        
        n_group <- nrow(plot_df) / 5
        
        plot_df <- plot_df %>%
            mutate(color = as.factor(ceiling(Rank / n_group))) 
        
        # This is to help position the text
        text_y <- max(plot_df$Crude.Rate) / - 100
        max_rank <- max(plot_df$Rank) - 2
        
        # Create the ggplot
        p <- ggplot(plot_df, aes(x = Rank, y = Crude.Rate, text = paste("<b>", state_name, "</b><br>Rank:", Rank, "out of", max(Rank),"<br>Rate:", round(Crude.Rate,1 )),  fill = color)) +
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
        ggplotly(p, tooltip = c("text")) %>% 
            config(displayModeBar = F) %>%
            layout(margin = list(t = 0))
    })
    
    output$improvement_plot <- renderPlotly({
        # Wrangle the data
        plot_df <- df %>%
            merge(xwalk) %>%
            filter(ICD.Chapter == input$cause_of_death_2)
        
        n_years <- plot_df %>%
            select(Year) %>%
            unique() %>%
            nrow()
        
        us <- plot_df %>%
            group_by(ICD.Chapter, Year) %>%
            summarise(Deaths = sum(Deaths), 
                      Population = sum(Population)) %>%
            mutate(State = "US",
                   state_fips = "00",
                   state_name = "United States",
                   Crude.Rate = round(Deaths / Population * 100000, 1)) %>%
            select(State, state_fips, state_name, ICD.Chapter, Year, Deaths, Population, Crude.Rate)
        
        plot_df <- plot_df %>%
            bind_rows(us)
        
        plot_df <- plot_df %>%
            filter(Year == 1999) %>%
            rename(base_rate = Crude.Rate) %>%
            select(State, base_rate) %>%
            merge(plot_df) %>%
            mutate(Index = round(Crude.Rate / base_rate * 100, 0))
        
        plot_df <- plot_df %>%
            filter(State == "US") %>%
            rename(US_Index = Index) %>%
            select(US_Index, Year) %>%
            merge(plot_df) %>%
            mutate(interpretation = ifelse(Index > US_Index, "Doing Worse than US", "Doing Better or Equal to US"))
        
        plot_df <- plot_df %>%
            mutate(color = ifelse(State == "US", "2", "1")) %>%
            mutate(color = ifelse(state_name == input$highlight, "3", color))
        
        
        plot_df$color <- as.factor(plot_df$color)
        
        p <- ggplot(plot_df) +
            geom_line(aes(x = Year, y = Index, group = state_name, text = paste0("<b>", state_name, "</b><br>", interpretation, "<br>Year: ", Year, "<br>Mortality Rate: ", Crude.Rate, "<br>Index: ", Index, " (US: ", US_Index,")"), color = color)) +
            scale_x_continuous(breaks = 1999:2010) +
            theme_minimal() +
            scale_color_manual(values=c("#bbbbbb", "#e41a1c", "#377eb8")) +
            theme(panel.grid.major.x = element_blank(),
                  legend.position = "none") +
            labs(x = "", y = "1999 Mortality Rate = 100")
        
        # Load it into plotly
        ggplotly(p, tooltip = c("text")) %>% 
            style(mode = "markers+lines") %>%
            config(displayModeBar = F) %>%
            layout(margin = list(t = 0), clickmode = "select") %>%
            highlight("plotly_selected")
    })
}

# Run the application 
shinyApp(ui = ui, server = server)
