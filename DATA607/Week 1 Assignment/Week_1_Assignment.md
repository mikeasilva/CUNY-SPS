---
title: "CUNY SPS DATA-607 Week 1 Assignment"
subtitle: "Loading Data into a Data Frame"
author: "Mike Silva"
date: "August 27, 2018"
output:
  html_document:
    keep_md: yes
---

## Description

The assignment is to load the Mushroom Dataset from the [UCI repository](https://archive.ics.uci.edu/ml/datasets/Mushroom) into a data frame, rename the columns into something meaningful, replace the abbreviations used in the data, and subset the columns of the data frame.  It must include the column that indicated if the mushroom is edible or poisonous and three or four other columns.

## Step 1: Acquire the Data

The first step will be to download the data to the local environment:


```r
download.file('https://archive.ics.uci.edu/ml/machine-learning-databases/mushroom/agaricus-lepiota.data', 'agaricus-lepiota.data')
```

## Step 2: Load the Data into Data Frame

Now that we have the dataset locally we will create a data frame:


```r
df <- read.table('agaricus-lepiota.data', sep=',', stringsAsFactors=FALSE)
head(df)
```

```
##   V1 V2 V3 V4 V5 V6 V7 V8 V9 V10 V11 V12 V13 V14 V15 V16 V17 V18 V19 V20
## 1  p  x  s  n  t  p  f  c  n   k   e   e   s   s   w   w   p   w   o   p
## 2  e  x  s  y  t  a  f  c  b   k   e   c   s   s   w   w   p   w   o   p
## 3  e  b  s  w  t  l  f  c  b   n   e   c   s   s   w   w   p   w   o   p
## 4  p  x  y  w  t  p  f  c  n   n   e   e   s   s   w   w   p   w   o   p
## 5  e  x  s  g  f  n  f  w  b   k   t   e   s   s   w   w   p   w   o   e
## 6  e  x  y  y  t  a  f  c  b   n   e   c   s   s   w   w   p   w   o   p
##   V21 V22 V23
## 1   k   s   u
## 2   n   n   g
## 3   n   n   m
## 4   k   s   u
## 5   n   a   g
## 6   k   n   g
```

According to the documentation we should have 8,124 rows and 23 columns of data.


```r
dim(df)
```

```
## [1] 8124   23
```

## Step 3: Rename the columns

Our data checks out, but the names are not very useful.


```r
names(df)
```

```
##  [1] "V1"  "V2"  "V3"  "V4"  "V5"  "V6"  "V7"  "V8"  "V9"  "V10" "V11"
## [12] "V12" "V13" "V14" "V15" "V16" "V17" "V18" "V19" "V20" "V21" "V22"
## [23] "V23"
```

I will rename the columns by using the dplyr package:


```r
library(dplyr)

df <- df %>%
  rename(type = V1,
         cap_shape = V2,
         cap_surface = V3,
         cap_color = V4,
         bruises = V5,
         odor = V6,
         gill_attachment = V7,
         gill_spacing = V8,
         gill_size = V9,
         gill_color = V10,
         stalk_shape = V11,
         stalk_root = V12,
         stalk_surface_above_ring = V13,
         stalk_surface_below_ring = V14,
         stalk_color_above_ring = V15,
         stalk_color_below_ring = V16,
         veil_type = V17,
         veil_color = V18,
         ring_number = V19,
         ring_type = V20,
         spore_print_color = V21,
         population = V22,
         habitat = V23)
```

## Step 4: Subsetting Data Frame

Before changing the data to be more meaningful I want to subset the data frame.  I would like to use this data to predict if a mushroom is poisonous or not.  According to the documentation the odor, spore print color, stalk surface below ring, and stalk color above ring are 4 attributes that can predict if a mushroom is poisonous with a 99.9% accuracy for these 23 species.


```r
df <- df %>%
  select(type, odor, spore_print_color, stalk_color_below_ring, stalk_color_above_ring)
```

Now that we have these subsets, let's examine the values:


```r
lapply(df, function(x) table(x)) 
```

```
## $type
## x
##    e    p 
## 4208 3916 
## 
## $odor
## x
##    a    c    f    l    m    n    p    s    y 
##  400  192 2160  400   36 3528  256  576  576 
## 
## $spore_print_color
## x
##    b    h    k    n    o    r    u    w    y 
##   48 1632 1872 1968   48   72   48 2388   48 
## 
## $stalk_color_below_ring
## x
##    b    c    e    g    n    o    p    w    y 
##  432   36   96  576  512  192 1872 4384   24 
## 
## $stalk_color_above_ring
## x
##    b    c    e    g    n    o    p    w    y 
##  432   36   96  576  448  192 1872 4464    8
```

## Step 5: Recoding Variables

Now that we have the subset of columns we can recode the variables.  I will accomplish this with dplyr and recode statements.


```r
df <- df %>%
  mutate(type = recode(type, p="Poisonous", e="Edible"),
         odor = recode(odor, a="Almond", c="Creosote", f="Foul", l="Anise", m="Musty", n="None", p="Pungent", s="Spicy", y="Fishy"),
         spore_print_color = recode(spore_print_color, b="Buff", h="Chocolate", k="Black", n="Brown", o="Orange", r="Green", u="Purple", w="White", y="Yellow"),
         stalk_color_below_ring = recode(stalk_color_below_ring, b="Buff", c="Cinnamon", e="Red", g="Gray", n="Brown", o="Orange", p="Pink", w="White", y="Yellow"),
         stalk_color_above_ring = recode(stalk_color_above_ring, b="Buff", c="Cinnamon", e="Red", g="Gray", n="Brown", o="Orange", p="Pink", w="White", y="Yellow"))
```

Now to examine the final product:


```r
head(df)
```

```
##        type    odor spore_print_color stalk_color_below_ring
## 1 Poisonous Pungent             Black                  White
## 2    Edible  Almond             Brown                  White
## 3    Edible   Anise             Brown                  White
## 4 Poisonous Pungent             Black                  White
## 5    Edible    None             Brown                  White
## 6    Edible  Almond             Black                  White
##   stalk_color_above_ring
## 1                  White
## 2                  White
## 3                  White
## 4                  White
## 5                  White
## 6                  White
```

```r
tail(df)
```

```
##           type  odor spore_print_color stalk_color_below_ring
## 8119 Poisonous  Foul             White                  White
## 8120    Edible  None              Buff                 Orange
## 8121    Edible  None              Buff                 Orange
## 8122    Edible  None              Buff                 Orange
## 8123 Poisonous Fishy             White                  White
## 8124    Edible  None            Orange                 Orange
##      stalk_color_above_ring
## 8119                   Pink
## 8120                 Orange
## 8121                 Orange
## 8122                 Orange
## 8123                  White
## 8124                 Orange
```
