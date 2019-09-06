DATA 621 Week \#2 Textbook Exercises
================
Mike Silva
2019-09-05

## MARR 2.1

The web site www.playbill.com provides weekly reports on the box office
ticket sales for plays on Broadway in New York. We shall consider the
data for the week Octover 11-17, 2004 (reffered to below as the current
week). The data are in the form of the gross box office results for the
current week and the gross box office results for the previous wek
(i.e., October 3-10, 2004).

Fit the following model to the data: \(Y=\beta_0 + \beta_1 x + e\) where
\(Y\) is the gross box office results for the current week (in $) and
\(x\) is the gross box office results for the previous week (in $).
Compleete the following tasks:

``` r
playbill <- read.csv("data/playbill.csv")
fit <- lm(CurrentWeek ~ LastWeek, data = playbill)
summary(fit)
```

``` 

Call:
lm(formula = CurrentWeek ~ LastWeek, data = playbill)

Residuals:
   Min     1Q Median     3Q    Max 
-36926  -7525  -2581   7782  35443 

Coefficients:
             Estimate Std. Error t value Pr(>|t|)    
(Intercept) 6.805e+03  9.929e+03   0.685    0.503    
LastWeek    9.821e-01  1.443e-02  68.071   <2e-16 ***
---
Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1

Residual standard error: 18010 on 16 degrees of freedom
Multiple R-squared:  0.9966,    Adjusted R-squared:  0.9963 
F-statistic:  4634 on 1 and 16 DF,  p-value: < 2.2e-16
```

A. Find a 95% confidence interval for the slope of the regression model,
\(\beta_1\). Is 1 a plausible value for \(\beta_1\)? Give a reason to
support your answer.

``` r
confint(fit, "LastWeek")
```

``` 
             2.5 %   97.5 %
LastWeek 0.9514971 1.012666
```

**Yes. It is plausible because it falls within the range of the 95%
confidence interval.**

B. Test the null hypothesis \(H_0 : \beta_0 = 10000\) against a
two-sided alternative. Interpret your result.

## MARR 2.2

## LMR 2.4

## LMR 2.5
