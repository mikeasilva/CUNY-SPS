# CUNY DATA 607 Final Project - Rochester Home Sale Price Model

## Introduction

This model is a final project for the CUNY Masters in Data Science DATA 607 course. It predicts the sales price of a home based on a few characteristics.  All source code is available at [https://github.com/mikeasilva/CUNY-SPS/tree/master/DATA607/Final-Project](https://github.com/mikeasilva/CUNY-SPS/tree/master/DATA607/Final-Project).  The final model is accessible though a shiny app hosted at [https://mikesilva.shinyapps.io/Rochester-Housing-Sale-Price/](https://mikesilva.shinyapps.io/Rochester-Housing-Sale-Price/).

## Replication

In order to replicate this project here are the steps to take:

### Setup

This project requires a system with R and Python installed.  Here are the packages used in this project in alphabetical order (Note: Not all package dependencies are listed.  Additional packages may need to be installed.)

| Python   | R        |
| -------- | :------: |
| asyncio  | caret    |
| bs4      | DBI      | 
| datetime | dplyr    |
| dbfread  | e1071    |
| os       | FNN      |
| pandas   | ggplot2  |
| re       | ggthemes |
| requests | ranger   |
| shutil   | RSQLite  |
| sqlite3  | shiny    |
| time     | stringr  |
| urllib   | tidyr    |
| zipfile  |          |

### Data Acquisition

Two data sources are brought together for this project.  In order to preform the acquisition task, run *[1 Build Monroe Real Property Data.py](https://github.com/mikeasilva/CUNY-SPS/blob/master/DATA607/Final-Project/1%20Build%20Monroe%20Real%20Property%20Data.py)*.  It will collect housing attributes produced by NYS GIS Clearinghouse and scrape Monroe County's Real Propertry Tax Portal.  The data will be stored in a SQLite file.  This is a very time consuming step.  A copy of the database is stored on [GitHub](https://github.com/mikeasilva/CUNY-SPS/raw/9a2023b57a466550646c9190076a53d51ef09ef2/data/Monroe%20Real%20Property%20Data.db.tar.gz).

### Data Wrangling and Model Creation

*[2 Create Model.R](https://github.com/mikeasilva/CUNY-SPS/blob/master/DATA607/Final-Project/2%20Create%20Model.R)* handles both the data wrangling and model creation.  Data from these two sources are combined, cleaned and prepared for modeling.  Variable selection is preformed using recursive feature elimination.  This is a very time intensive step!  Users may want to choose to comment out those lines.  The caret package generates a 10 fold cross-validated random forest model.  Select environmental variables are saved to *model.RData*.

### Visualization

*[App.R](https://github.com/mikeasilva/CUNY-SPS/blob/master/DATA607/Final-Project/App.R)* is a single file shiny app.  It loads the environemental variables used in *model.RData*.  Default settings are chosen using the average (median) for numeric and mode for categorical variables.  The model is available at [https://mikesilva.shinyapps.io/Rochester-Housing-Sale-Price/](https://mikesilva.shinyapps.io/Rochester-Housing-Sale-Price/).
