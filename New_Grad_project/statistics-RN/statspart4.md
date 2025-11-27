Calculating multiple linear regression EPUB version of this book
Susan K. Grove, PhD, RN, ANP-BC, GNP-BC; Daisha J. Cipher, PhD

Statistics for Nursing Research, EXERCISE 31, 394-411

Multiple linear regression analysis is an extension of simple linear regression in which more than one independent variable is entered into the analysis. Interpretations of multiple regression findings are much the same as with simple linear regression, which is reviewed in Exercise 30 . The beta values of each predictor are tested for significance, and a multiple R and R 2 are computed. In multiple linear regression, however, when all predictors are tested simultaneously, each beta has been adjusted for every other predictor in the regression model. The beta represents the independent relationship between that predictor and y, even after controlling for (or accounting for) the presence of every other predictor in the model ( Stevens, 2009 ; Tabachnick & Fidell, 2019 ).

In multiple linear regression, relationships between multiple predictors and y are tested simultaneously with a series of matrix algebra calculations. Therefore multiple linear regression is best conducted using a statistical software package; however, full explanations and examples of the matrix algebraic computations of multiple linear regression are presented in Stevens (2009) and Tabachnick and Fidell (2019) .

Research designs appropriate for multiple linear regression
Research designs that may use multiple linear regression include any associational design ( Gliner et al., 2017 ; Kazdin, 2022 ). The variables involved in the design are usually attributional, meaning the variables are characteristics of the participant, such as health status, blood pressure, gender, diagnosis, or ethnicity. Regardless of the nature of the predictor variables, the dependent variable submitted to multiple linear regression must be measured as interval or ratio level (see Exercise 1 ; Gray & Grove, 2021 ). Although the predictor can be any scale of measurement, if it is nominal, it must be correctly coded, which is described later in this exercise.

Statistical assumptions
Use of multiple linear regression involves the following assumptions ( Tabachnick & Fidell, 2019 ; Zar, 2010 ):

1.
Normal distribution of the dependent ( y ) variable

2.
Linear relationship between x and y

3.
Independent observations

4.
Homoscedasticity (discussed later in this exercise)

5.
Interval or ratio measurement of the dependent variable; however, if the dependent variable is measured with a Likert scale, and the frequency distribution is approximately normally distributed, these data are usually considered interval-level measurement and are appropriate to serve as the outcome in a linear regression model ( Rasmussen, 1989 ; Waltz et al., 2017 ).

Multiple linear regression equation
The parameters a and b (a beta is computed for each predictor) are computed to obtain a regression equation. The equation looks similar to that of the simple linear regression equation presented in Exercise 30 , but has been expanded to reflect the presence of multiple predictors:

y
=
b
1
x
1
+
b
2
x
2
+
b
3
x
3
⋯
+
a
where

y = the dependent variable
x 1 , x 2 , x 3 , etc. = the independent variables (predictors)
b 1 , b 2 , b 3 , etc. = the slopes of the line for each predictor
a = y -intercept (the point where the regression line intersects the y -axis)
As mentioned earlier, multiple linear regression can be computed by hand but requires knowledge of matrix algebra. Therefore we will use SPSS to compute the regression equation and other important parameters such as the R and R 2 .

Homoscedasticity and heteroscedasticity
Data that are homoscedastic are evenly dispersed both above and below a plotted line of perfect prediction when variable x predicts variable y. Homoscedasticity reflects equal variance of both variables. In other words, for every value of x, the distribution of y values should have equal variability. If the data for the predictor and dependent variable are not homoscedastic, inferences made during significance testing could be invalid ( Cohen & Cohen, 1983 ; Tabachnick & Fidell, 2019 ).

The assumption of homoscedasticity can be checked by visual examination of a plot of the standardized residuals (the errors) by the regression standardized predicted value. Ideally, residuals are randomly scattered around zero (the horizontal line representing perfectly accurate prediction), providing a relatively even distribution. Heteroscedasticity is indicated when the residuals are not evenly scattered around the line. Heteroscedasticity manifests itself in all kinds of uneven shapes. When the plot of residuals appears to deviate substantially from normal, more formal tests for heteroscedasticity should be performed. Formal tests for heteroscedasticity include the Breusch-Pagan Test ( Breusch & Pagan, 1979 ) and the White Test ( White, 1980 ).

Take for example the plots in Figs. 31.1 and 31.2 that follow. Two multiple linear regression analyses were performed, and the predicted y values were plotted against the residuals (actual y − predicted ŷ ). Homoscedasticity occurs when the observations (seen as dots) are equally distributed above the line and below the line. It should look like a “bird’s nest,” such as the shape exhibited in Fig. 31.1 , and not a cone or triangle, such as the shape in Fig. 31.2 .

A scatter plot displays a random distribution of residuals around a horizontal line at zero. The scatter plot shows regression standardized residuals on the yaxis and regression standardized predicted values on the x axis. The data points are scattered randomly above and below a horizontal line at zero, indicating homoscedasticity. The distribution of residuals appears consistent across the range of predicted values, with no discernible pattern or fanning effect. This suggests that the variance of the errors is constant.
FIG. 31.1 ■
EXAMPLE OF HOMOSCEDASTICITY.

A scatter plot shows a fanning out pattern of residuals, with wider spread at higher predicted values. The scatter plot displays regression standardized residuals on the yaxis and regression standardized predicted values on the xaxis. The data points show a clear pattern where the spread of residuals increases as the predicted values increase, forming a fanning out shape. This indicates heteroscedasticity, meaning the variance of the errors is not constant across all levels of the independent variable. The horizontal line at zero represents the mean of the residuals. The increasing vertical spread of the points away from this line demonstrates that the variability of the residuals is not uniform.
FIG. 31.2 ■
EXAMPLE OF HETEROSCEDASTICITY.

Multicollinearity
Multicollinearity occurs when the predictors in a multiple regression equation are strongly correlated ( Cohen & Cohen, 1983 ). Multicollinearity is minimized by carefully selecting the predictors and thoroughly determining the interrelationships among predictors before the regression analysis. Multicollinearity does not affect predictive power (the capacity of the predictors to predict values of the dependent variable in that specific sample); rather it causes problems related to generalizability ( Tabachnick & Fidell, 2019 ). If multicollinearity is present, the equation will not have predictive validity. The amount of variance explained by each variable in the equation will be inflated. The beta values will not remain consistent across samples when crossvalidation (the process of testing a new regression equation’s ability to predict new data) is performed ( Cohen & Cohen, 1983 ; Tabachnick & Fidell, 2019 ).

The first step in identifying multicollinearity is to examine the correlations among the predictor variables. The correlation matrix is carefully examined for evidence of multicollinearity. SPSS provides two statistics (tolerance and variance inflation factor [VIF]) that describe the extent to which your model has a multicollinearity problem. A tolerance of less than 0.20 or 0.10 and/or a VIF of 5 or 10 and above indicates a multicollinearity problem ( Allison, 1999 ).

Dummy coding of nominal predictors
As discussed earlier, a predictor can be any scale of measurement; however, if the predictor is nominal, it must be correctly coded. To use categorical predictors in regression analysis, a coding system is developed to represent group membership. Categorical variables of interest in nursing that might be used in regression analysis include gender, income, ethnicity, social status, level of education, and diagnosis. If the variable is dichotomous, such as gender, members of one category are assigned the number 1, and all others are assigned the number 0. In this case for gender the coding could be:

1 = female, 0 = male
The process of creating dichotomous variables from categorical variables is called dummy coding . If the categorical variable has three values, two dummy variables are used; for example, social class could be classified as lower class, middle class, or upper class. The first dummy variable ( x 1 ) would be classified as:

1 = lower class
0 = not lower class
The second dummy variable ( x 2 ) would be classified as

1 = middle class
0 = not middle class
The three social classes would then be specified in the equation in the following manner:

Lower class x 1 = 1, x 2 = 0
Middle class x 1 = 0, x 2 = 1
Upper class x 1 = 0, x 2 = 0
When more than three categories define the values of the variable, increased numbers of dummy variables are used. The number of dummy variables is always one less than the number of categories ( Aiken & West, 1991 )—otherwise multicollinearity will be very high.

SPSS computations
This example includes data collected from a survey study by Urban et al. (2022) . Newly licensed registered nurses (RNs) were surveyed and administered several questionnaires: Patient Health Questionnaire (PHQ-9), General Anxiety Disorder-7 Scale (GAD), Perceived Stress Scale (PSS), and the Brief Resilience Scale (BRS). Higher scores on the PHQ-9, GAD, and PSS are indicative of increased (worse) depression, anxiety, and stress levels, respectively. Scores on the BRS range from 1 to 5, with higher scores indicating greater (better) self-reported resilience levels.

The null hypothesis is: Self-reported depression, anxiety, and stress do not predict resilience levels among newly licensed RNs. A simulated subset of 45 students was created for this example. In actuality, studies involving linear regression need to be adequately powered ( Aberson, 2019 ; Gaskin & Happell, 2014 ; Taylor & Spurlock, 2018 ). See Exercises 24 and 25 for more information regarding statistical power. The data are presented in Table 31.1 .

View full size
TABLE 31.1

PREDICTORS OF RESILIENCE IN NEWLY LICENSED NURSES

Participant ID	x 1 (Depression)	x 2 (Anxiety)	x 3 (Stress)	y (Resilience)
1	6.00	6.00	24.00	4.17
2	5.00	3.00	14.00	4.00
3	3.00	4.00	10.00	4.00
4	7.00	7.00	7.00	4.67
5	6.00	6.00	15.00	2.50
6	6.00	5.00	15.00	2.50
7	10.00	13.00	24.00	3.17
8	10.00	13.00	24.00	3.17
9	12.00	20.00	30.00	2.67
10	10.00	5.00	24.00	3.83
11	5.00	1.00	7.00	4.50
12	10.00	5.00	24.00	3.83
13	13.00	16.00	34.00	3.00
14	19.00	12.00	24.00	2.17
15	6.00	4.00	15.00	3.50
16	15.00	15.00	29.00	2.83
17	8.00	10.00	10.00	3.17
18	1.00	5.00	13.00	4.50
19	10.00	13.00	24.00	3.17
20	6.00	6.00	24.00	4.17
21	18.00	13.00	28.00	2.17
22	18.00	13.00	28.00	2.17
23	11.00	17.00	19.00	1.83
24	11.00	9.00	25.00	3.00
25	5.00	3.00	14.00	4.00
26	2.00	3.00	21.00	3.17
27	11.00	17.00	19.00	1.83
28	7.00	7.00	7.00	2.00
29	11.00	17.00	19.00	1.83
30	5.00	1.00	7.00	4.50
31	8.00	10.00	10.00	3.17
32	2.00	3.00	21.00	3.17
33	6.00	6.00	24.00	4.17
34	5.00	1.00	7.00	4.50
35	6.00	4.00	15.00	3.50
36	10.00	5.00	24.00	3.83
37	5.00	4.00	11.00	3.33
38	5.00	4.00	11.00	3.33
39	12.00	20.00	30.00	2.67
40	13.00	16.00	34.00	3.00
41	11.00	9.00	25.00	3.00
42	8.00	10.00	10.00	3.17
43	19.00	12.00	24.00	2.17
44	15.00	15.00	29.00	2.83
45	4.00	4.00	10.00	3.80
This is how the dataset looks in SPSS.

A table with columns for subject I D, various measurements, perhaps days and other quantitative data, and calculated values possibly residual. The table shows several columns of numerical data. The table has at least 16 rows, with the first column appearing to be a subject or sample identifier. Subsequent columns contain quantitative data, potential. The final visible column, labeled 'Residual', likely contains calculated residual values from a statistical analysis. The header of the window is partially visible, indicating a data processing or analysis environment. This table is consistent with output from a regression analysis where residuals are examined.

Step 1: From the “Analyze” menu, choose “Regression” and “Linear.”

Step 2: Move the predictors PHQ (depression), GAD (anxiety), and PSS (stress) to the space labeled “Independent(s).” Move the dependent variable, BRS (resilience), to the space labeled “Dependent.”

A diagram shows the new project window with steps and options. The diagram shows the new project window. It has a list on the left with items named new project, saved projects, and recent used files. The center panel shows the steps numbered 1 of 7 with buttons back and next. Step 1 has three options named select vault source, select query source, and select data cache. There are dropdown menus for source details and local paths with text fields and browse buttons. On the right, there are six buttons named options, help, print, reset, next, and back. At the bottom, there is a button labeled new query.
Step 3: Click “Statistics.” Check the box labeled “Collinearity diagnostics.” Click “Continue.”

A dialog box shows linear regression statistics options with checkboxes and buttons. The dialog box is titled linear regression statistics. It contains multiple options for regression coefficients and residuals. Under regression coefficients, there are checkboxes for estimates, confidence intervals, and confidence level. Next to confidence level, there is a text field with a value of 95. There is also a checkbox for exponentiated beta. On the right side, there are checkboxes labeled squared R, R squared change, covariances, and part and partial correlations. Another checkbox labeled collinearity diagnostics is also present. Below the regression coefficients section, there is a section labeled residuals. This section contains checkboxes for student residual, casewise diagnostics, and all cases. Under casewise diagnostics, there is an input field with the number 2 and text stating standard deviations.
Step 4: Click “Plots.” Move the variable “ZPRED” (standardized predictor values) to the box labeled “X.” Move the variable “ZRESID” (standardized residual values) to the box labeled “Y.” Click “Continue” and “OK.”

A screenshot shows the Linear Regression Plots window in SPSS with ZRESID and ZPRED selected for a scatter plot. The screenshot shows the Linear Regression Plots window in SPSS. On the left, a list of variables includes DEPENDNT, ZPRED, ZRESID, DRESID, ADJPRED, SRESID, and SDRESID. In the middle section titled Scatter 1 of 1, ZRESID is selected for the Y axis and ZPRED is selected for the X axis. Below that, options under Standardized Residual Plots include Histogram and Normal probability plot, both of which are unchecked. To the right, the checkbox for Produce all partial plots is also unchecked. At the bottom are three buttons labeled Continue, Cancel, and Help.
Interpretation of SPSS output
The following tables and figure are generated from SPSS. The first table contains the multiple R and the R 2 values. The multiple R is 0.736, indicating that the correlation between the actual y values and the predicted ŷ values using the new regression equation is 0.736. The R 2 is 0.542, indicating that 54.20% of the variance in resilience levels can be explained by knowing the nurse’s depression, anxiety, and stress levels. The adjusted R 2 is 0.509, which is slightly lower because it reflects an elimination of increases in R 2 that occurred because of chance by simply adding predictors to the model ( Allison, 1999 ).


A table shows regression model summary with predictors and dependent variable details. The table is titled regression model summary and presents key values from a regression analysis. It includes the columns labeled model, R, R square, adjusted R square, standard error of the estimate, and F change. Under the header, the first row lists the model number 1, followed by corresponding values for R, R square, adjusted R square, and standard error of the estimate. There are also values corresponding to the F change statistic. Below the table, the predictors and dependent variable are described. The predictors are constant, personal stress scale score, generalized anxiety disorder scale score, and patient health questionnaire depression score. The dependent variable is the staff resilience scale score.
The second table contains the analysis of variance (ANOVA) table. As presented in Exercise 35, the ANOVA is usually performed to test for differences between group means; however, ANOVA can also be performed for regression, where the null hypothesis is that knowing the value of x explains no information about y. This table indicates that knowing the value of x explains a significant amount of variance in y. The contents of the ANOVA table are rarely reported in published manuscripts, because the significance of each predictor is presented in the last SPSS table titled “Coefficients” (see below).


A screenshot shows an A N O V A table with results for a regression model predicting resilience. he screenshot shows an A N O V A table from SPSS output for a regression model. The table includes three rows labeled Regression, Residual, and Total. For the regression row, the sum of squares is 15.541, degrees of freedom is 3, mean square is 5.180, F value is 16.185, and the significance value is less than point 001. For the residual row, the sum of squares is 13.123, degrees of freedom is 41, and mean square is point 320. The total sum of squares is 28.664 with 44 degrees of freedom. A footnote states that the dependent variable is Brief Resilience Scale Score. The predictors are Constant, Perceived Stress Scale Score, General Anxiety Disorder Scale Score, and Patient Health Questionnaire Depression Score.
The third table contains the b and a values, standardized beta (β), t, exact p values, and collinearity diagnostics. The a is listed in the first row, next to the label “Constant.” The b is listed in the following rows, next to the name of each predictor. The remaining information that is important to extract when interpreting regression results can be found in the second through fourth rows, which list the standardized beta and the p values. It should be noted that in some versions of SPSS, a very low p value might display as “. 000.” However, p is never zero and should more accurately be written as less than 0.001 or <0.001. Finally, the collinearity diagnostics, tolerance, and VIF are listed for each predictor. A tolerance of less than 0.20 or 0.10 and/or a VIF of 5 or 10 and above indicates a multicollinearity problem ( Allison, 1999 ). Here, there does not appear to be a multicollinearity problem, as the tolerance values are greater than 0.20, and the VIF values are less than 5.0.


A screenshot shows a regression coefficients table with values for predictors of resilience. The screenshot shows a regression coefficients table from SPSS for a model predicting Brief Resilience Scale Score. Under Unstandardized Coefficients, the constant has a value of 4.103 with standard error.225. Patient Health Questionnaire Depression Score has a coefficient of negative.063 with standard error.030, General Anxiety Disorder Scale Score has a coefficient of negative.085 with standard error.024, and Perceived Stress Scale Score has a coefficient of.023 with standard error.015. In the Standardized Coefficients column, the beta values are negative.357 for depression, negative.577 for anxiety, and.224 for perceived stress. The t values are 18.213 for the constant, negative 2.121 for depression, negative 3.510 for anxiety, and 1.504 for perceived stress. The p values are less than point 001 for the constant, point 040 for depression, point 001 for anxiety, and point 140 for perceived stress. Collinearity Statistics show tolerance values of point 394, point 413, and point 505 for the three predictors, and V I F values of 2.539, 2.423, and 1.980, indicating no multicollinearity. Arrows and annotations explain that the first row contains the constant, the next rows contain the b values for each predictor, the standardized beta values, the exact p values, and the collinearity statistics.
The last figure in the output is the scatterplot that assists us in identifying heteroscedasticity. Recall that homoscedasticity occurs when the observations (seen as dots in the figure) are equally distributed above a horizontal line representing perfectly accurate prediction drawn at y = 0 and below the line at y = 0. In this example, our data appear to have met the homoscedasticity assumption, because the values appear to be evenly dispersed above and below the line.


A scatter plot shows regression standardized residuals against predicted values. The scatter plot is titled scatterplot with the subtitle dependent variable staff resilience scale score. The horizontal axis is labeled regression standardized predicted value and ranges from negative two to three. The vertical axis is labeled regression standardized residual and ranges from negative two to two. The plot contains multiple data points scattered across the graph with no clear pattern, and a horizontal reference line is drawn at zero on the vertical axis.
Final interpretation in American Psychological Association format
The following interpretation is written as it might appear in a research article, formatted according to the American Psychological Association (APA) guidelines ( APA, 2020 ). It should be noted that all statistical values reported here are rounded to two decimal places, with the exception of the p value, which is rounded to three decimal places.

Multiple linear regression was performed with newly licensed RNs’ levels of self-reported depression, anxiety, stress as the predictors and resilience as the dependent variable. Collinearity diagnostics indicated no multicollinearity, and visual inspection of the scatterplot of the residuals revealed no heteroscedasticity. The nurses’ depression and anxiety levels significantly predicted their levels of resilience, R 2 = 54.20%, adjusted R 2 = 50.90%. Higher levels of depression significantly predicted lower levels of resilience (β = −0.36, p = 0.040). Higher levels of anxiety also significantly predicted lower levels of resilience (β = −0.58, p = 0.001). However, stress levels did not significantly predict resilience among the newly licensed RNs after controlling for self-reported depression and anxiety.

Study questions

1.
State the null hypothesis for this study where depression, anxiety, and stress are tested as predictors of resilience among newly licensed nurses.

2.
If you have access to SPSS, compute the Pearson correlation between stress and resilience. Note the differences between the Pearson r results and the β (standardized beta) in the multiple regression output. Provide an explanation for the differences in findings between the two sets of results.

3.
Write the newly computed regression equation, predicting resilience.

4.
Using the new regression equation, compute the predicted resilience score if the nurse’s PHQ score is 5, GAD score is 1, and PSS score is 7. Show your calculations.

5.
Using the new regression equation, compute the predicted resilience score if the nurse’s PHQ score is 12, GAD score is 20, and PSS score is 30. Show your calculations.

6.
What was the correlation between the actual y values and the predicted ŷ values using the new regression equation in the example?

7.
What was the exact likelihood of obtaining a β value for PSS (stress) that is at least as extreme or as close to the one that was actually observed, assuming that the null hypothesis is true and after controlling for the other two predictors?

8.
Which predictor has the strongest association with y ? Provide a rationale for your answer.

9.
How much variance in resilience is explained by the three model predictors?

10.
How would you characterize the magnitude of the R 2 in the example? Provide a rationale for your answer.

Answers to study questions

1.
The null hypothesis is: Self-reported depression, anxiety, and stress do not predict resilience levels among newly licensed RNs.

2.
The Pearson correlation between stress and resilience is r (43) = −0.386, p = 0.009. The β (standardized beta) between stress and resilience in the multiple linear regression model with three predictors is 0.224, p = 0.14. When predictors in a regression model are being adjusted for the presence of other predictors in the model, the β values can change substantially depending on the extent to which the other predictors are associated with y and with one another ( Tabachnick & Fidell, 2019 ). This explains why the Pearson r is significant but the β is not significant.

3.
The newly computed regression equation is: ŷ = −0.063 x 1 + −0.085 x 2 + 0.023 x 3 + 4.103, where x 1 = PHQ (depression), x 2 = GAD (anxiety), x 3 = PSS (stress), and a = 4.103.

4.
The predicted resilience score if the nurse’s PHQ score is 5, GAD score is 1, and PSS score is 7 is: ŷ = −0.063(5) + −0.085(1) + 0.023(7) + 4.103 = −0.315 + −0.085 + 0.161 + 4.103 ŷ = 3.864, rounded to 3.86.

5.
The predicted resilience score if the nurse’s PHQ score is 12, GAD score is 20, and PSS score is 30 is: ŷ = −0.063(12) + −0.085(20) + 0.023(30) + 4.103 = −0.756 + −1.70 + 0.69 + 4.103

ŷ = 2.337, rounded to 2.34

6.
The multiple R is 0.736. This value can be observed in the “Model Summary” table of the SPSS output.

7.
The exact likelihood of obtaining a β value for PSS (stress) at least as extreme as or as close to the one that was actually observed, assuming that the null hypothesis is true and after controlling for the other two predictors, is 14.00%. This value was obtained by taking the p value listed in the SPSS output table titled “Coefficients” in the column labeled “Sig.” and multiplying by 100%: 0.14 × 100% = 14.00%. Because this value is greater than the study alpha of 0.05 or 5%, stress is not a significant predictor of resilience after controlling for the other two predictors.

8.
The predictor GAD (anxiety) has the strongest association with y , with a standardized β of −0.577. The other two predictors had lower standardized beta values, as presented in the “Coefficients” Table.

9.
Of the variance in resilience, 54.20% is explained by the three model predictors. This value (× 100%) is located in the “Model Summary” table.

10.
The magnitude of the R 2 , 0.542 or 54.20%, is considered a large effect according to the effect size tables in Exercises 24 and 25 ( Tables 24.1 and 25.1 respectively).

Calculating t -tests for independent samples EPUB version of this book
Susan K. Grove, PhD, RN, ANP-BC, GNP-BC; Daisha J. Cipher, PhD

Statistics for Nursing Research, EXERCISE 32, 412-425

One of the most common statistical tests chosen to investigate significant differences between two independent samples is the independent samples t -test. The samples are independent if the study participants in one group are unrelated or different participants than those in the second group (see Exercise 16 for an introduction to the independent samples t -test). The dependent variable in an independent samples t -test must be scaled as interval or ratio. If the dependent variable is measured with a Likert scale, and the frequency distribution is approximately normally distributed, these data are usually considered interval-level measurement and are appropriate for an independent samples t -test (see Exercise 1 ; de Winter & Dodou, 2010 ; Rasmussen, 1989 ; Waltz et al., 2017 ).

Research designs appropriate for the independent samples t -test
Research designs that may use the independent samples t -test include the randomized experimental, quasi-experimental, and comparative designs ( Gliner et al., 2017 ; Gray & Grove, 2021 ; Kazdin, 2022 ). The independent variable (the grouping variable for the t -test) may be active or attributional. An active independent variable refers to an intervention, treatment, or program. An attributional independent variable refers to a characteristic of the participant, such as gender, diagnosis, or ethnicity. Regardless of the nature of the independent variable, the independent samples t -test only compares two groups at a time.

Example 1: Researchers conduct a randomized experimental study where the participants are randomized to either a novel weight loss intervention or a placebo. The number of pounds lost from baseline to posttreatment for both groups is measured. The research question is: Is there a difference between the two groups in weight loss? The active independent variable is the weight loss intervention, and the dependent variable is the number of pounds lost over the treatment span.

Null hypothesis: There is no difference between the intervention and the control (placebo) groups in weight loss.

Example 2: Researchers conduct a retrospective comparative descriptive study where a chart review of patients is done to identify patients who recently underwent a colonoscopy. The patients were divided into two groups: those who used statins continuously in the past year, and those who did not. The dependent variable is the number of polyps found during the colonoscopy, and the independent variable is statin use. The research question is: Is there a significant difference between the statin users and nonusers in number of colon polyps found?

Null hypothesis: There is no difference between the group taking statins versus the group not taking statins (control) in number of colon polyps found.

Statistical formula and assumptions
Use of the independent samples t -test involves the following assumptions ( Zar, 2010 ):

1.
Sample means from the population are normally distributed.

2.
The dependent variable is measured at the interval/ratio level.

3.
The two samples have equal variance.

4.
All observations within each sample are independent.

The formula and calculation of the independent samples t -test are presented in this exercise.

The formula for the independent samples t -test ( t ) is:

t
=
X
¯
1
−
X
¯
2
s
X
1
−
X
2
where

X
¯
1
=
mean of group 1
X
¯
2
=
mean of group 2
s
X
1
−
X
2
=
standard error of the difference between the two groups
To compute the t -test, one must compute the denominator in the formula, which is the standard error of the difference between the means. If the two groups have different sample sizes, then one must use this formula:

s
X
¯
1
−
X
¯
2
=
(
n
1
−
1
)
s
1
2
+
(
n
2
−
1
)
s
2
2
n
1
+
n
2
−
2
(
1
n
1
+
1
n
2
)
where

n 1 = group 1 sample size
n 2 = group 2 sample size
s 1 = group 1 variance
s 2 = group 2 variance
If the two groups have the same number of participants in each group, then one can use this simplified formula:

s
X
¯
1
−
X
¯
2
=
s
1
2
+
s
2
2
n
where

n
=
the sample size in each group and not the total sample of both groups
Hand calculations
A randomized experimental study examined the effect of the discontinuation of proton pump inhibitors (PPIs) on gastrointestinal symptoms among those with gastroesophageal reflux disease (GERD; Hendricks et al., 2021 ). The researchers followed two randomized groups of participants over time: those who underwent abrupt PPI discontinuation and those who underwent tapered PPI discontinuation.

The data from this study are presented in Table 32.1 . A simulated subset was selected for this example so that the computations would be small and manageable. In actuality, studies involving independent samples t -tests need to be adequately powered ( Aberson, 2019 ; Cohen, 1988 . See Exercises 24 and 25 for more information regarding statistical power).

View full size
TABLE 32.1

DSSI SCORES BY GROUP

Abrupt Discontinuation Group	Tapered Discontinuation Group
Participant #	DSSI Score (Dyspepsia Symptoms)	Participant #	DSSI Score (Dyspepsia Symptoms)
1	3.20	11	3.30
2	4.10	12	2.70
3	3.90	13	2.90
4	3.60	14	2.60
5	3.80	15	3.10
6	3.70	16	3.20
7	2.90	17	3.40
8	2.80	18	2.90
9	3.10	19	3.00
10	3.20	20	2.40
DSSI, Dyspepsia Symptom Severity Index.

The independent variable in this example is the type of PPI discontinuation (abrupt versus tapered). The dependent variable was the score on the Dyspepsia Symptom Severity Index (DSSI) assessed at a follow-up assessment 14 weeks postdiscontinuation. The items on the DSSI are rated on a 5-point Likert scale ranging from 0 (absent) to 4 (very severe). The null hypothesis is: There is no difference between the abrupt and tapered discontinuation groups on the severity of dyspepsia symptoms among persons with GERD.

The computations for the independent samples t -test are as follows:

Step 1: Compute means for both groups, which involves the sum of scores for each group divided by the number in the group.

The mean for Group 1, Abrupt Discontinuation Group:
X
¯
1
=
3.43
The mean for Group 2, Tapered Discontinuation Group:
X
¯
2
=
2.95
Step 2: Compute the numerator of the t -test:

3.43
−
2.95
=
0
.
48
It does not matter which group is designated as “group 1” or “group 2.”

Another possible correct method for Step 2 is to subtract group 1’s mean from group 2’s mean, such as: 
X
¯
 2 – 
X
¯
 1 : 2.95 − 3.43 = −0.48

Step 3: Compute the standard error of the difference.

a.
Compute the variances for each group:

s
2
for
group 1
=
0.20
s
2
for
group 2
=
0.10
b.
Plug into the standard error of the difference formula:

s
X
¯
1
−
X
¯
2
=
s
2
1
+
s
2
2
n
s
X
¯
1
−
X
¯
2
=
0.20
+
0.10
10
s
X
¯
1
−
X
¯
2
=
.030
s
X
¯
1
−
X
¯
2
=
0
.
1732
Step 4: Compute t value:

t
=
X
¯
1
−
X
¯
2
s
X
¯
1
−
X
¯
2
t
=
0
.
48
0.1732
t
=
2
.
77
Step 5: Compute the degrees of freedom (df):

df
=
n
1
+
n
2
−
2
df
=
10
+
10
−
2
df
=
18
Step 6: Locate the critical t value in the t distribution table ( Appendix A ) and compare it to the obtained t value.

The critical t value for a two-tailed test with 18 df at alpha (α) = 0.05 is 2.101, rounded to 2.10. This means that if we viewed the t distribution for df = 18, the middle 95% of the distribution would be marked by −2.10 and 2.10. The obtained t is 2.77, exceeding the critical value, which means our t -test is statistically significant and represents a real difference between the two groups. Therefore we can reject our null hypothesis. It should be noted that if the obtained t was −2.77, it would also be considered statistically significant, because the absolute value of the obtained t is compared with the critical t tabled value ( Kim et al., 2022 ).

SPSS computations
This is how our dataset looks in SPSS.

A screenshot shows the Data View tab in SPSS with values for I D, Group, and D S S I. The screenshot shows the Data View tab in SPSS. Three columns are visible, labeled I D, Group, and D S S I. The I D column lists participant numbers from 1 to 16. The Group column contains values of either 1 or 2, indicating two groups of participants. The D S S I column contains numeric values ranging from 2.60 to 4.10. The top menu shows options including File, Edit, View, Data, Transform, Analyze, and Graphs. The active tab is Data View, and Variable View is also available at the bottom.

Step 1: From the “Analyze” menu, choose “Compare Means” and “Independent-Samples T Test.” Move the dependent variable, “DSSI” (dyspepsia symptoms), over to the right, like the window below and click OK.

A screenshot shows the Independent Samples T Test window in S P S S. The screenshot shows the Independent Samples T Test window in S P S S. On the left side, Participant I D is listed as the available variable. On the right side, under Test Variables, Score on the Dyspepsia Symptom is selected. The Grouping Variable is set to Group with values 1 and 2. The Define Groups button is greyed out. Estimate effect sizes is checked. On the right side of the window, there are buttons for Options and Bootstrap. At the bottom are buttons labeled O K, Paste, Reset, Cancel, and Help.
Step 2: Move the independent variable, “Group,” into the space titled “Grouping Variable.” Click “Define Groups” and enter 1 and 2 to represent the coding chosen to differentiate between the two groups. Click “Continue” and “OK.”

A dialog box shows options to define groups with input fields and buttons. The dialog box is titled define groups. It has two main options for specifying group values. The first option labeled use specified values is selected. Below it there are two text input fields labeled group 1 and group 2 with the values 1 and 2 entered respectively. The second option labeled cut point is available but not selected. At the bottom there are three buttons labeled continue cancel and help. This interface is used to define grouping variables by manually entering specific group values or selecting a cut point for classification.
Interpretation of SPSS output
The following tables are generated from SPSS. The first table contains descriptive statistics for dyspepsia symptom scores, separated by the two groups. The second table contains the t- test results.


A screenshot shows group statistics for T Test comparing abrupt and tapered discontinuation. The screenshot shows group statistics from a T Test in S P S S comparing two groups, abrupt and tapered discontinuation. The test variable is Score on the Dyspepsia Symptom Severity Index. For the abrupt group, the sample size is 10, the mean is 3.4300, the standard deviation is point 44734, and the standard error of the mean is point 14146. For the tapered group, the sample size is 10, the mean is 2.9500, the standard deviation is point 31710, and the standard error of the mean is point 10028. A note at the bottom of the image points to the means and states observe the means for the two groups.
The first table displays descriptive statistics that allow us to observe the means for both groups. This table is important because it indicates that the participants in the abrupt discontinuation group had a mean DSSI score of 3.43, and the participants in the tapered discontinuation group had a mean DSSI score of 2.95.


A screenshot shows Independent Samples Test results for two groups using a T Test. The screenshot shows results from an Independent Samples Test in S P S S comparing two groups based on the Score on the Dyspepsia Symptom Severity Index. The first row shows results under the assumption of equal variances. Levene's Test for Equality of Variances reports an F value of 3.150 and significance value of point 093. The t value is 2.768 with 18 degrees of freedom. The one sided p value is point 006 and the exact two sided p value is point 013. The mean difference between groups is point 48000, with standard error of point 17340. The 95 percent confidence interval of the difference ranges from point 11571 to point 84429.
The last table contains the actual t -test value, the p value, along with the values that compose the t -test formula. The first value in the table is the Levene test for equality of variances. The Levene test is a statistical test of the equal variances assumption ( Field, 2013 ; Tabachnick & Fidell, 2019 ). The p value is 0.093, indicating there was no significant difference between the two groups’ variances. If there had been a significant difference, the second row of the table, titled “Equal variances not assumed,” would be reported in the results.

Following the Levene test results are the t -test value of 2.768 and the two-sided p value of 0.013, otherwise known as the probability of obtaining a statistical value at least as extreme or as close to the one that was actually observed, assuming that the null hypothesis is true. In this example, the two-sided p value (also known as two-tailed p value ) is being reported instead of the one-sided p value. This is because the one-sided p value only allows for a one-sided or directional hypothesis, where the hypothesized difference is only tested in one direction or one tail of the normal curve. For a two-sided test, we allow for the possibility that one group could either be higher or lower than the other group on the dependent variable.

Following the t -test value, the next value in the table is 0.48, which is the mean difference that we computed in Step 2 of our hand calculations. The next value in the table is 0.1734, similar to the value we computed in Steps 3a and 3b of our hand calculations.

Final interpretation in American Psychological Association format
The following interpretation is written as it might appear in a research article, formatted according to American Psychological Association (APA) guidelines ( APA, 2020 ). It should be noted that all statistical values reported here are rounded to two decimal places, with the exception of the p value, which is rounded to three decimal places.

An independent samples t -test revealed that participants in the abrupt discontinuation group reported significantly more dyspepsia symptoms at the 14-week follow-up assessment than the participants in the tapered discontinuation group, t (18) = 2.77, p = 0.013; 
X
¯
 = 3.43 versus 2.95, respectively. Thus the particular type of discontinuation that was implemented appears to have had an impact on GERD symptoms several months after the participants stopped taking PPIs.

Study questions

1.
If you have access to SPSS, compute the Shapiro-Wilk test of normality for the dependent variable of DSSI (dyspepsia symptoms; as demonstrated in Exercise 27 ). What do the results indicate?

2.
Do the data meet criteria for the equality of variances assumption? Provide a rationale for your answer.

3.
Do the data meet criteria for independent samples? Provide a rationale for your answer.

4.
What is the null hypothesis in the example?

5.
What was the exact likelihood of obtaining a t- test value at least as extreme or as close to the one that was actually observed, assuming that the null hypothesis is true?

6.
If Levene’s test for equality of variances was significant at p ≤ 0.05, what SPSS output would the researcher need to report?

7.
What does the numerator of the independent samples t -test represent?

8.
What does the denominator of the independent samples t -test represent?

9.
What kind of design was implemented in the example?

10.
Was the sample size adequate to detect differences between the two groups in this example? Provide a rationale for your answer.

Answers to study questions

1.
As shown below, the Shapiro-Wilk p value for DSSI score was 0.807, indicating that the frequency distribution did not significantly deviate from normality.

A screenshot shows normality test results for Dyspepsia Symptom Severity Index. The screenshot shows the Tests of Normality table in S P S S for the Score on the Dyspepsia Symptom Severity Index. Two tests are shown, Kolmogorov Smirnov and Shapiro Wilk. In the Kolmogorov Smirnov test, the statistic is point 141, degrees of freedom is 20, and the significance value is point 200. A note indicates that point 200 is the lower bound of the true significance. In the Shapiro Wilk test, the statistic is point 973, degrees of freedom is 20, and the significance value is point 807. A footnote states that the Kolmogorov Smirnov test uses the Lilliefors Significance Correction.
2.
The two groups’ variances did not significantly differ, as evidenced by the nonsignificant Levene test result, p = 0.093. This value is found on the top row in the column labeled “Sig.” of the “Independent Samples t -Test” table, indicating that there was no significant difference between the two groups’ variances.

3.
Yes, the data meet criteria for independent samples because the dependent variable data were collected from two mutually exclusive groups of study participants. In addition, the study participants were randomly assigned to either the abrupt or tapered discontinuation group, which makes the groups independent ( Grove & Gray, 2023 ).

4.
The null hypothesis is: There is no difference between the abrupt and tapered discontinuation groups on the severity of dyspepsia symptoms.

5.
The exact likelihood of obtaining a t- test value at least as extreme or as close to the one that was actually observed, assuming that the null hypothesis is true, is 1.30%. This value can be found in the “Independent Samples t -Test” table in the SPSS output, where the exact p value is reported as 0.013. The value is calculated as follows: 0.013 × 100% = 1.30%.

6.
If Levene’s test for equality of variances was significant at p ≤ 0.05, the researcher would need to report the second row of values from the “Independent Samples t -Test” table in the SPSS output, containing the t -test value that has been adjusted for unequal variances.

7.
The numerator represents the mean difference between the two groups (see formula for the independent samples t -test).

8.
The denominator represents the extent to which there is dispersion among the values of the dependent variable.

9.
The study design in the example was a randomized experimental design, as evidenced by the fact that the participants were randomly assigned to receiving the abrupt or tapered discontinuation conditions ( Gliner et al., 2017 ; Kazdin, 2022 ).

10.
The sample size was adequate to detect differences between the two groups, because a significant difference was found, p = 0.013. However, this sample is considered small, and as emphasized in Exercises 24 and 25 , it is strongly recommended that a power analysis be conducted prior to the study beginning in order to avoid the risk of Type II error ( Taylor & Spurlock, 2018 ).

Data for additional computational practice
This example involves additional data collected in the same study by Hendricks et al. (2021) .

The researchers compared the two randomized groups, abrupt PPI discontinuation versus tapered PPI discontinuation, on the self-reported number (raw count) of GERD symptoms at the 14-week follow-up assessment. Examples of GERD symptoms include acid reflux, nausea, vomiting, abdominal pain, and early satiety. The null hypothesis is: There is no difference between the abrupt and tapered discontinuation groups on the participants’ number of GERD symptoms.

A simulated subset of 20 observations was created for this example. The data are presented in Table 32.2 below.

View full size
TABLE 32.2

NUMBER OF GERD SYMPTOMS BY GROUP

Abrupt Discontinuation Group	Tapered Discontinuation Group
Participant #	Number of GERD Symptoms	Participant #	Number of GERD Symptoms
1	6	11	6
2	7	12	4
3	8	13	2
4	7	14	3
5	7	15	6
6	3	16	5
7	6	17	5
8	6	18	3
9	5	19	6
10	6	20	5
GERD, gastroesophageal reflux disease.

EXERCISE 32
Questions for additional study

Name: _____________________________________________________ Class: _______________________

Date: ___________________________________________________________________________________

Answer the following questions with hand calculations using the data presented in Table 32.2 or the SPSS dataset called “Exercise 32 Example 2.sav” available on the Evolve website. Follow your instructor’s directions to submit your answers to the following questions for additional study. Your instructor may ask you to write your answers below and submit them as a hard copy for evaluation. Alternatively, your instructor may ask you to submit your answers online.

1.
Do the example data meet the assumptions for the independent samples t -test? Provide a rationale for your answer.

2.
If calculating by hand, draw the frequency distributions of the dependent variable of number of GERD symptoms. What is the shape of the distribution? If using SPSS, what is the result of the Shapiro-Wilk test of normality for the dependent variable?

3.
List the mean number of GERD symptoms for the two groups. Which group had the highest mean number of GERD symptoms at the 14-week follow-up assessment?

4.
Compute the independent samples t -test. What is the t value?

5.
Is the t -test significant at α = 0.05? Specify how you arrived at your answer.

6.
If using SPSS, what is the exact likelihood of obtaining a t -test value at least as extreme or as close to the one that was actually observed, assuming that the null hypothesis is true?

7.
Why are the mean group values important in the interpretation of the t -test results?

8.
Write your interpretation of the results as you would in an APA-formatted journal ( American Psychological Association, 2020 ).

9.
What do the results indicate regarding the effect of the proton pump inhibitor (PPI) discontinuation approach used by persons suffering from GERD on their gastrointestinal symptoms?

10.
Calculating t -tests for paired (dependent) samples EPUB version of this book
Susan K. Grove, PhD, RN, ANP-BC, GNP-BC; Daisha J. Cipher, PhD

Statistics for Nursing Research, EXERCISE 33, 426-441

A paired samples t -test (also referred to as a dependent samples t -test) is a statistical procedure that compares two sets of data from one group of people. The paired samples t -test was introduced in Exercise 17 , which is focused on understanding these results in research reports. This exercise focuses on calculating and interpreting the results from paired samples t -tests. When samples are related, the formula used to calculate the t statistic is different from the formula for the independent samples t -test (see Exercise 32 ).

Research designs appropriate for the paired samples t -test
The term paired samples refers to a research design that repeatedly assesses the same group of people, an approach commonly referred to as repeated measures . Paired samples can also refer to naturally occurring pairs, such as siblings or spouses. The most common research design that may use a paired samples t -test is the one-group pretest–posttest design, wherein a single group of participants is assessed at baseline and once again after receiving an intervention ( Gliner et al., 2017 ; Gray & Grove, 2021 ). Another design that may use a paired samples t -test is where one group of participants is exposed to one level of an intervention and then those scores are compared with the same participants’ responses to another level of the intervention, resulting in paired scores. This is called a one-sample crossover design ( Gliner et al., 2017 ).

Example 1: A researcher conducts a one-sample pretest–posttest study wherein she assesses her sample for health status at baseline, and again posttreatment. Her research question is: Is there a difference in health status from baseline to posttreatment? The dependent variable is health status.

Null hypothesis: There is no difference between the baseline and posttreatment health status scores.

Example 2: A researcher conducts a crossover study wherein participants receive a randomly generated order of two medications. One is a standard Food and Drug Administration (FDA)-approved medication to reduce blood pressure, and the other is an experimental medication. The dependent variable is reduction in blood pressure (systolic and diastolic), and the independent variable is medication type. Her research question is: Is there a difference between the experimental medication and the control medication in blood pressure reduction?

Null hypothesis: There is no difference between the two medication trials in blood pressure reduction.

Statistical formula and assumptions
Use of the paired samples t -test involves the following assumptions ( Zar, 2010 ):

1.
The distribution of values is normal or approximately normal.

2.
The dependent variable(s) is (are) measured at interval or ratio levels.

3.
Repeated measures data are collected from one group of participants, resulting in paired scores.

4.
The differences between the paired scores are independent ( Gray & Grove, 2021 ; Kazdin, 2022 ; Shadish et al., 2002 ).

The formula for the paired samples t -test is:

t
=
D
¯
s
D
¯
where:

D
¯
=
the mean difference of the paired data
s
D
¯
=
the standard error of the difference
To compute the t -test, one must calculate the denominator in the formula, the standard error of the difference:

s
D
¯
=
s
D
n
where:

s
D
=
the standard deviation of the differences between the paired data
n = the number of participants in the sample (or number of paired scores in the case of sibling or spousal data)
Hand calculations
Using an example from a study of adults with gastroesophageal reflux disease (GERD), symptoms of gastroesophageal reflux were examined over time ( Dunbar et al., 2016 ). Twelve adults with GERD were followed over a period of 2 weeks while being required to be free of all proton pump inhibitor (PPI) medications (the intervention). A subset of these data ( n = 10) is presented in Table 33.1 . One of the dependent variables was esophageal impedance, which is an index of mucosal integrity, where higher numbers are more desirable and indicative of healthy esophageal functioning. Impedance was measured with a pH electrode positioned 5 cm above the lower esophageal sphincter. For this example, the null hypothesis is: There is no change in esophageal impedance from baseline to follow-up for patients with GERD who had stopped taking PPI medications.

View full size
TABLE 33.1

ESOPHAGEAL IMPEDANCE VALUES AT BASELINE AND 2-WEEK FOLLOW-UP

Participant #	Esophageal Impedance, Baseline	Esophageal Impedance, 2-Week Follow-Up	Difference Scores
1	2249	773	1476
2	3993	1329	2664
3	1422	1113	309
4	3676	1670	2006
5	2004	1231	773
6	3271	2660	611
7	2130	1784	346
8	2947	2000	947
9	2000	850	1150
10	3021	1674	1347
The computations for the paired t -test are as follows:

Step 1: Compute the difference between each participant’s pair of data (see last column of Table 33.1 ).

Step 2: Compute the mean of the difference scores, which becomes the numerator of the t -test:

D
¯
=
11
,
629.00
÷
10
D
¯
=
1162.90
Step 3: Compute the standard error of the difference.

a.
Compute the standard deviation of the difference scores.

s
D
=
∑
(
X
−
X
¯
)
2
n
−
1
s
D
=
4
,
995
,
908.90
10
−
1
s
D
=
745.05
b.
Plug the result into the standard error of the difference formula.

s
D
¯
=
s
D
n
s
D
¯
=
745.05
10
s
D
¯
=
745.05
3.16
s
D
¯
=
235.78
Step 4: Compute t value:

t
=
D
¯
s
D
¯
t
=
1162.90
235.78
t
=
4.93
Step 5: Compute the degrees of freedom ( df ):

df
=
n
−
1
df
=
10
−
1
df
=
9
Step 6: Locate the critical t value on the t distribution table in Appendix A and compare it to the obtained t .

The critical t value for 9 df at alpha (α) = 0.05 is 2.262 (rounded to 2.26) for a two-tailed test. Our obtained t is 4.93, exceeding the critical value (see Appendix A ), which means our t -test is statistically significant and represents a real difference between the two pairs. Therefore we can reject our null hypothesis. This means that if we viewed the t distribution for df = 9, the middle 95% of the distribution would be marked by −2.26 and 2.26. It should be noted that if the obtained t was −4.93, it would also be considered statistically significant because the absolute value of the obtained t is compared with the critical t value ( Gray & Grove, 2021 ).

SPSS computations
This is how our dataset looks in SPSS.

A screenshot shows S P S S Data View with columns for I D, Imped Baseline, and Imped 2 Week. The screenshot shows the Data View tab in S P S S. Three columns are visible labeled I D, Imped Baseline, and Imped 2 Week. Each row represents data for a participant, with I D values from 1 to 10. The Imped Baseline column contains impedance measurements at baseline ranging from 1422 to 3993. The Imped 2 Week column contains impedance values at the two week mark, ranging from 773 to 2660. The top menu displays options including File, Edit, View, Data, Transform, Analyze, Graphs, and Utilities. The Data View tab is active at the bottom left, and the Variable View tab is also visible.

Step 1: From the “Analyze” menu, choose “Compare Means” and “Paired-Samples T Test.”

Step 2: Move both variables over to the right, as in the window shown. Click “OK.”


A screenshot shows the Paired Samples T Test window in S P S S with esophageal impedance data selected. The screenshot shows the Paired Samples T Test window in S P S S. On the left, the variable list includes I D, Esophageal Impedance Baseline, and Esophageal Impedance 2 Week Follow Up. On the right, under Paired Variables, Pair 1 has Variable 1 as Esophageal Impedance Baseline and Variable 2 as Esophageal Impedance 2 Week Follow Up. Estimate effect sizes is checked. The selected method for calculating the standardizer is Standard deviation of the difference. Other available options are Corrected standard deviation of the difference and Average of variances. Buttons for Options and Bootstrap are on the top right. At the bottom, there are buttons labeled O K, Paste, Reset, Cancel, and Help.
Interpretation of SPSS output
The following tables are generated from SPSS. The first table contains descriptive statistics for the two variables. The second table contains the Pearson product-moment correlation between the two variables. The last table contains the t -test results.


A screenshot shows paired samples statistics comparing esophageal impedance at baseline and two week follow up. The screenshot shows a Paired Samples Statistics table from S P S S for Pair 1, comparing esophageal impedance at baseline and at two week follow up. The mean impedance at baseline is 2671.30 with standard deviation of 832.819 and standard error of the mean 263.360. The mean impedance at the two week follow up is 1508.40 with standard deviation of 571.268 and standard error of the mean 180.651. Both rows have a sample size of 10. A note at the bottom highlights the difference in means, stating observe the means for the two assessments.

A screenshot shows paired samples correlation between baseline and two week esophageal impedance. The screenshot shows a Paired Samples Correlations table from S P S S for Pair 1, comparing esophageal impedance at baseline and at two week follow up. The sample size is 10. The correlation between the two time points is point 489. The one sided p value is point 076 and the two sided p value is point 152.

A screenshot shows results of a paired samples T Test comparing esophageal impedance at baseline and two week follow up. The screenshot shows the Paired Samples Test table from S P S S for esophageal impedance measured at baseline and at two week follow up. The mean paired difference is 1162.90, standard deviation is 745.051, and standard error of the mean is 235.606. The 95 percent confidence interval of the difference ranges from 629.923 to 1695.877. The t value is 4.936 with 9 degrees of freedom. Both the one sided and two sided p values are less than point 001. Annotations highlight the t value and the exact two sided p value.
The first table displays descriptive statistics that include the means at baseline and follow-up. This table is important because we can observe that the mean impedance at baseline was 2,671.30, and the mean impedance at follow-up was 1,508.40, indicating a decrease in esophageal impedance. Recall that higher numbers are indicative of healthy esophageal functioning, and therefore a decrease over time is undesirable for persons with GERD.

The second table displays the Pearson product-moment correlation coefficient ( r ) that was computed between the two variables. It is common that the two variables are significantly correlated, because the sample is being assessed twice, and therefore it is logical that a person’s follow-up value is affected by his or her baseline value in a repeated measures design. Although this table is a standard part of the SPSS output for a paired samples t -test, the contents are not reported in the results of published studies.

The last table contains the actual t -test value, along with the values that compose the t -test formula. Note that the first value in the table, 1,162.90, was the mean difference that we computed in Step 2 of our hand calculations. The next two values in the table, 745.05 and 235.61, were the values we computed in Steps 3a and 3b of our hand calculations. The t -test value of 4.936 is slightly higher than what we obtained in our hand calculations. This is because we rounded to the hundredth decimal place in our hand calculations, when the standard error value is actually 235.606, which yields a t -test value of 1,162.90 ÷235.606 = 4.936. Therefore 4.936 (rounded to 4.94) is more accurate and will be reported as 4.94 in the interpretation below.

The last value in the table is the two-sided p value, otherwise known as the probability of obtaining a statistical value at least as extreme or as close to the one that was actually observed, assuming that the null hypothesis is true. SPSS has printed a value of “<.001,” indicating a less than 0.10% probability of obtaining a t -test value at least as extreme or as close to the one that was actually observed, assuming that the null hypothesis is true ( Gray & Grove, 2021 ). In this example, the two-sided p value (also known as two-tailed p value ) will be reported instead of the one-sided p value. This is because the one-sided p value only allows for a one-sided or directional hypothesis, where the hypothesized difference is only tested in one direction or one tail of the normal curve. For a two-sided test, we allow for the possibility that the baseline dependent variable values could either be higher or lower than the follow-up dependent variable values.

Final interpretation in American Psychological Association format
The following interpretation is written as it might appear in a research article, formatted according to American Psychological Association ( APA, 2020 ) guidelines. It should be noted that all statistical values reported here are rounded to two decimal places, with the exception of the p value, which is rounded to three decimal places.

A paired samples t -test computed on esophageal impedance revealed that the patients with GERD undergoing the withdrawal of PPIs had significantly lower impedance from baseline to posttreatment, t (9) = 4.94, p <0.001; 
X
¯
 = 2,671.30 versus 1,508.40, respectively. Thus the removal of PPI medications appeared to play a role in the deterioration of the esophageal mucosal integrity.

Study questions

1.
Use SPSS to create a frequency distribution for the two study variables of esophageal impedance at baseline and follow-up. Describe the appearance of the distributions.

2.
Use SPSS to compute the Shapiro-Wilk tests of normality for those two variables (esophageal impedance at baseline and follow-up) as demonstrated in Exercise 27 .

3.
Do the data meet criteria for paired samples? Provide a rationale for your answer.

4.
On average, did esophageal impedance improve or deteriorate over time? Provide a rationale for your answer.

5.
What was the exact likelihood of obtaining a t -test value at least as extreme or as close to the one that was actually observed, assuming that the null hypothesis is true?

6.
Identify the Pearson correlation ( r ) between the two study variables. Why do you think the baseline and follow-up variables were correlated?

7.
What is the numerator for the paired samples t -test in this example? What does the numerator of the paired samples t -test represent?

8.
What is the denominator for the paired samples t -test in this example? What does the denominator of the paired samples t -test represent?

9.
Why would a one-sample crossover design also be suitable for a paired samples t -test?

10.
The researchers concluded that the removal of PPI medications appeared to deteriorate the mucosal integrity of the esophagus. What are some alternative explanations for these changes? (These alternative scientific explanations would apply to any one-sample repeated measures design.) Document your response.

Answers to study questions

1.
See the two SPSS frequency distributions below. Because the sample size is very small ( n = 10), the shapes of the distributions do not follow a normal bell-shaped curve, but contain gaps in the x -axis.

A histogram shows baseline esophageal impedance values with frequency distribution. The histogram shows the frequency distribution of esophageal impedance values at baseline. The horizontal axis is labeled Esophageal Impedance Baseline and ranges from 1000 to 4000. The vertical axis is labeled Frequency and ranges from 0 to 4. The tallest bar shows a frequency of 4 in the 2000 to 2500 range. Other bars indicate frequencies of 1 or 2 for ranges between 1000 to 4000. Summary statistics in the top right corner report the mean as 2671.3, standard deviation as 832.819, and sample size as 10.
A histogram shows esophageal impedance values at two week follow up with frequency distribution. The histogram shows the frequency distribution of esophageal impedance values at two week follow up. The horizontal axis is labeled Esophageal Impedance 2 Week Follow up and ranges from 500 to 3000. The vertical axis is labeled Frequency and ranges from 0 to 3. The highest bars show frequencies of 3 in the ranges of 1000 to 1500 and 1500 to 2000. Other bars show frequencies of 2 or 1 in other intervals. Summary statistics in the top right corner report the mean as 1508.4, standard deviation as 571.268, and sample size as 10.
2.
The Shapiro-Wilk p values for baseline and follow-up esophageal impedance were 0.67 and 0.70, respectively, indicating that the two frequency distributions did not significantly deviate from normality. Moreover, visual inspection of the frequency distributions in the answer to Question 1 indicates that the variables are approximately normally distributed.

A screenshot shows tests of normality for esophageal impedance at baseline and two week follow up. The screenshot shows the Tests of Normality table from S P S S for esophageal impedance at baseline and at two week follow up using Kolmogorov Smirnov and Shapiro Wilk tests.
3.
Yes, the data meet criteria for paired samples because the two esophageal impedance values were collected from the same single group of study participants over time.

4.
The mean impedance at baseline was 2,671.30, and the mean impedance at follow-up was 1,508.40, indicating a decrease in esophageal impedance, and therefore an undesirable trend for persons with GERD. As noted earlier, higher numbers are more desirable and indicative of healthy esophageal functioning.

5.
The exact likelihood of obtaining a t -test value at least as extreme as or as close to the one that was actually observed, assuming that the null hypothesis is true, is less than 0.10%.

6.
The baseline and follow-up variables were correlated ( r = 0.489) because the sample of patients was assessed twice, and therefore it is logical that a person’s follow-up value is affected by his or her baseline value in a repeated measures design ( Kim et al., 2022 ).

7.
As shown in the SPSS output, the numerator of the paired samples t -test in this example is 1,162.90. The numerator represents the mean difference between the two variables (see formula for the paired samples t -test in this exercise).

8.
As shown in the SPSS output, the denominator of the paired samples t -test in this example is 235.606 (rounded to 235.61). The denominator represents the extent to which there is dispersion among the entire dataset’s values.

9.
A one-sample crossover design also would be suitable for a paired samples t -test because one group of participants is exposed to one level of an intervention and then those scores are compared with the same participants’ responses to another level of the intervention. This meets criteria for paired samples because the two variables were collected from the same single group of people ( Gliner et al., 2017 ).

10.
When changes occur in a one-sample pretest–posttest design, we cannot be certain that the intervention caused the changes. Other explanations may include the passing of time, the inadvertent use of other treatments during the time elapsed from baseline to posttreatment, or statistical regression (a phenomenon that refers to artificially high baseline levels that naturally decrease to the actual population mean at posttreatment, or vice versa) ( Gliner et al., 2017 ; Gray & Grove, 2021 ; Shadish et al., 2002 ).

Data for additional computational practice
Using an example from a study examining the gastroesophageal reflux among 12 adults with GERD, changes over time were investigated ( Dunbar et al., 2016 ). These data are presented in Table 33.2 . The independent variable in this example is intervention over time, meaning that all of the participants were followed over time while being required to be free of all PPI medications for 2 weeks (the intervention). The dependent variable was esophageal reflux symptoms, measured by the GERD Health-Related Quality of Life (HRQL) questionnaire, a validated instrument for GERD symptom severity, with higher scores representing more GERD symptoms ( Velanovich, 2007 ). The data in Table 33.2 were transformed to approximate normality. The null hypothesis is: There is no change in esophageal reflux symptoms from baseline to follow-up for patients with GERD.

View full size
TABLE 33.2

ESOPHAGEAL SYMPTOM SCORES AT BASELINE AND 2-WEEK FOLLOW-UP

Participant #	Esophageal Symptom Scores, Baseline	Esophageal Symptom Scores, 2-Week Follow-Up	Difference Scores
1	.00	3.00	3.00
2	5.00	4.69	−.31
3	4.12	5.39	1.26
4	1.00	1.73	.73
5	4.36	4.47	.11
6	3.32	4.00	.68
7	.00	3.74	3.74
8	1.41	2.00	.59
9	.00	2.24	2.24
10	1.41	2.00	.59
11	2.00	4.24	2.24
12	.00	2.00	2.00
Compute the paired samples t -test on the data in Table 33.2 below.

EXERCISE 33
Questions for additional study

Name: _____________________________________________________ Class: _______________________

Date: ___________________________________________________________________________________

Answer the following questions with hand calculations using the data presented in Table 33.2 or the SPSS dataset called “Exercise 33 Example 2.sav” available on the Evolve website. Follow yourCalculating the Mann-Whitney U test EPUB version of this book
Susan K. Grove, PhD, RN, ANP-BC, GNP-BC; Daisha J. Cipher, PhD

Statistics for Nursing Research, EXERCISE 34, 442-455

One of the most common nonparametric statistical tests chosen to investigate significant differences between two independent samples is the Mann-Whitney U test . When assumptions are not met for an independent samples t -test, such as equal group variances and/or non-normality, the Mann-Whitney U test is an appropriate alternative ( Terrell, 2021 ). The samples are independent if the study participants in one group are unrelated or different participants than those in the second group. Exercise 12 provides an algorithm that will assist you in determining whether the Mann-Whitney U is an appropriate statistical technique. It should be noted that the Mann-Whitney U test is also known as the Wilcoxon rank-sum test, which is not to be confused with the Wilcoxon signed-rank test , which is covered in Exercise 22 .

Research designs appropriate for the Mann-Whitney U test
Research designs that may use the Mann-Whitney U test include the randomized experimental, quasi-experimental, and comparative designs ( Gray & Grove, 2021 ; Gliner et al., 2017 ). The independent variable (the grouping variable) may be active or attributional. An active independent variable refers to an intervention, treatment, or program. An attributional independent variable refers to a characteristic of the participant, such as gender, diagnosis, or ethnicity. Regardless of the nature of the independent variable, the Mann-Whitney U test only compares two groups at a time.

Example 1: Researchers conduct a randomized experimental study where the participants are randomized to either a novel weight loss intervention or a placebo. The number of pounds lost from baseline to posttreatment for both groups is measured. The research question is: Is there a difference between the two groups in weight loss? The active independent variable is the weight loss intervention, and the dependent variable is the number of pounds lost over the treatment span. The frequency distribution of the dependent variable significantly deviates from normality.

Null hypothesis: There is no difference in weight loss between the intervention group exposed to a novel weight loss program and the comparison (placebo) group receiving a standard diet.

Example 2: Researchers conduct a retrospective comparative descriptive study where a chart review of patients is done to identify patients who recently underwent a colonoscopy. The patients were divided into two groups: those who used statin drugs continuously in the past year, and those who did not. The dependent variable is the number of polyps found during the colonoscopy, and the independent variable is statin drug use. The frequency distribution of the dependent variable significantly deviates from normality. The research question is: Is there a difference between the statin drug users and nonusers in number of colon polyps found?

Null hypothesis: There is no difference between the group taking statin drugs versus the group not taking statins (control) in number of colon polyps found.

Statistical formula and assumptions
Unlike the independent samples t -test, the use of the Mann-Whitney U test makes no assumptions regarding the variances or the distributions of the data. The only assumption required by the Mann-Whitney U test is that all observations within each sample are independent ( Daniel, 2000 ).

To calculate the value of U, the data of both samples are combined, and each data value is assigned a rank. The lowest value is ranked 1, the next value is ranked 2, and so forth until all values are ranked, regardless from which sample the score was obtained. The idea is that if two distributions came from the same population, the average of the ranks of values would be equal as well.

When calculating the Mann-Whitney U by hand, one must compute two U values, and choose the smallest of the two U values when determining significance of the result ( Daniel, 2000 ). Therefore when reporting the Mann-Whitney U test results, researchers should identify the sample size of each of the independent groups, the value of the z statistic (converted from the smallest U value) and its associated p value, and the medians for the two groups ( Terrell, 2021 ). The z statistic for the Mann-Whitney U test represents the extent to which the two groups differ on the dependent variable. The higher the z statistic, the more likely the groups significantly differ on the values of the dependent variable ( Gray & Grove, 2021 ).

A median can be more informative than a mean in describing a variable when the variable’s frequency distribution is positively or negatively skewed. Although the mean is sensitive to or increases or decreases based on the values of the outliers, the median is relatively unaffected (see Exercises 27 and 28 ).

The formula for the Mann-Whitney U test is:

U
=
∑
R
−
n
(
n
+
1
)
2
where

R
=
the
ranked
values
n
=
sample
size
for
one
group
As noted previously, one must apply this U formula twice: once for each of the two groups. Therefore when computing the U by hand, one must compute two U values.

Hand calculations
Deng and colleagues (2021) conducted a cross-sectional study ( n = 260) to describe and compare fear of childbirth, in-labor pain intensity, and pain relief between primipara and multipara women living in Guangzhou, China. A simulated subset ( n = 10) was created for this example so that the computations would be small and manageable ( Table 34.1 ). In actuality, studies involving Mann-Whitney U tests need to be adequately powered, as determined by a power analysis ( Aberson, 2019 ; Cohen, 1988 ). See Exercises 24 and 25 for more information regarding statistical power.

View full size
TABLE 34.1

DURATION OF LABOR ANALGESIA BY GROUP

Primipara Group	Multipara Group
Participant #	Duration of Labor Analgesia	Participant #	Duration of Labor Analgesia
1	6.20	6	5.20
2	8.10	7	6.30
3	19.00	8	2.50
4	19.40	9	3.30
5	7.20	10	2.30
The independent variable in this example is primipara (i.e., the individual had given birth for the first time) in group 1 or multipara (i.e., the individual had given birth more than once) in group 2. The dependent variable was the duration (hours) of analgesia during labor. The null hypothesis is: There is no difference between the primipara and multipara groups on the duration of analgesia during labor.

The computations for the Mann-Whitney U test are as follows:

Step 1: Rank-order the dependent variable, regardless of group or condition.

View full size
Group	Ordered Value, Lowest to Highest	Assigned Rank
2	2.30	1
2	2.50	2
2	3.30	3
2	5.20	4
1	6.20	5
2	6.30	6
1	7.20	7
1	8.10	8
1	19.00	9
1	19.40	10
Step 2: Add the ranks for each group separately.

Primipara group (group 1): 5 + 7 + 8 + 9 + 10 = 39
Multipara group (group 2): 1 + 2 + 3 + 4 + 6 = 16
Step 3: Compute U 1 where Σ R 1 = the sum of ranks for group 1 and n 1 = n for group 1. It should be noted that it does not matter which of the groups is assigned “group 1” and “group 2.” In this example, the primipara group is coded as “1” and the multipara group is coded as “2,” but the results would not differ if these designations were to be switched.

U
1
=
∑
R
1
−
n
1
(
n
1
+
1
)
2
U
1
=
39
−
5
(
5
+
1
)
2
U
1
=
39
−
15
U
1
=
24
Step 4: Compute U 2 where Σ R 2 = the sum of ranks for group 2 and n 2 = n for group 2

U
2
=
∑
R
2
−
n
2
(
n
2
+
1
)
2
U
2
=
16
−
5
(
5
+
1
)
2
U
2
=
16
−
15
U
2
=
1
Step 5: Choose the smaller of the U values for your observed U.

The two computed U values are 24 and 1, respectively. The smaller U is 1.

Step 6: Compare the observed (calculated) U to the tabled critical U ( Plichta & Kelvin, 2013 , pp. 523–524). If the observed U is smaller than the critical U, then the observed U is statistically significant and indicates a difference between the two groups. The critical U value for n 1 = 5 and n 2 = 5 at alpha (α) = 0.05 is 2, and the observed (smaller) U value is 1. Therefore the U is statistically significant and represents a real difference between the two groups. Therefore we can reject the null hypothesis: There is no difference between the primipara and multipara groups on the duration of analgesia during labor.

SPSS computations
This is how the dataset looks in SPSS.


A spreadsheet shows columns labeled ID, Group, and Duration Analgesia with numeric entries. The display shows a spreadsheet within data based on group and id. The top section contains a menu bar listing options such as File, Edit, View, Data, Transform, Analyze, Graphs, and Utilities. Beneath it, icons allow quick access to tasks like opening, saving, printing, transforming, and analyzing data. Below, a spreadsheet presents three columns. The first column, labeled ID, contains numbers from 1 to 10. The second column, labeled Group, contains numbers 1 and 2. The third column, labeled Duration Analgesia, shows decimal values including 6.20, 8.10, 19.00, 19.40, 7.20, 5.20, 6.30, 2.50, 3.30, and 2.30. Group 1 includes entries from IDs 1 to 5. Group 2 includes entries from IDs 6 to 10.
Step 1: From the “Analyze” menu, choose “Nonparametric Tests,” “Legacy Dialogs,” and “2 Independent Samples.” Move the dependent variable, “Duration Analgesia” (duration of labor analgesia), over to the right as shown and click “OK.”


A screenshot shows a window setting for a test comparing two independent samples, which includes selected variables and test type. The screenshot shows a dialog box titled Two Independent Samples Tests presents several elements. Duration of Labor appears as the selected test variable. Group shows in the grouping variable field with values 1 and 2. The test type section displays four options Mann Whitney U, Kolmogorov mirnov Z, Moses extreme reactions, and Wald Wolfowitz runs. Mann Whitney U appears marked. Buttons include Exact, Options, Define Groups, OK, Paste, Reset, Cancel, and Help. A list of IDs appears on the left side.
Step 2: Move the independent variable, group, into the space titled “Grouping Variable.” Click “Define Groups” and enter “1” and “2” to represent the coding chosen to differentiate between the two groups. Click “Continue” and “OK.”


A diagram shows a window with values for Group 1 and Group 2 with buttons. The diagram shows a dialog box titled Two Independent Samples Define Groups presents entry fields and buttons. Group 1 shows a text box with the number 1 entered. Group 2 shows a text box with the number 2 entered. Below these fields, three buttons appear labeled Continue, Cancel, and Help.
Interpretation of SPSS output
The following tables are generated from SPSS. The first table contains descriptive statistics for duration of labor analgesia, separated by the two groups. The second table contains the Mann-Whitney U test results.

NPar tests

A table presents ranks and total values for two groups labeled Primiparas and Multiparas. The illustration shows a table titled Ranks shows comparative data for duration of labor analgesia. The first column lists group labels Primiparas and Multiparas. The second column displays the number of participants marked N with the value 5 for each group. The third column provides mean rank values 7.80 for Primiparas and 3.20 for Multiparas. The fourth column shows total rank values 39.00 for Primiparas and 16.00 for Multiparas. A row below shows total cases as 10. A note below the table states to interpret the mean ranks and not the original values for the two groups.
The first table displays descriptive statistics that allow us to observe the mean ranks for both groups. This table does not display the means of the original values, because nonparametric tests assume potentially non-normally distributed data. Recall that the mean is sensitive to increases or decreases based on the values of the outliers ( Exercises 27 and 28 ). This table is important because it indicates that the participants in the primipara group had a mean rank of 7.80, and the participants in the multipara group had a mean rank of 3.20, indicating that the primipara group had the higher ranked values of labor analgesia durations. The median labor analgesia duration for the primipara group was 8.10, compared with 3.30 for the multipara group.


A representation displays test statistics and significance values for two sample groups. The diagram shows test statistics for the duration of labor analgesia between two groups. Mann Whitney U presents the value 1.000. Wilcoxon W displays the value 16.000. Z shows the value negative 2.402. Asymptotic significance two tailed presents.016. Exact significance based on two times one tailed significance also presents.016 superscript b. Group serves as the grouping variable. Text notes that the correction for ties does not apply. A note on the right explains that the smallest of the two U values appears here, and the correct p value for small samples comes from the exact result.
The second table contains the Mann-Whitney U test value, the z statistic, and two p values. Note that only the smallest of the two U values is reported here (1.0). The z statistic, which was created with a formula involving the smallest of the U values and sums of ranks, is often reported in published articles instead of the U value. The first p value ( p = 0.016) is the asymptotic p value for large samples. The last p value ( p = 0.016) is an exact p value and is the more appropriate p to report for small samples. Sometimes these values slightly differ, and other times these values are the same, as in this example. The exact two-sided p value is 0.016, otherwise known as the probability of obtaining a statistical value at least as extreme or close to the one that was actually observed, assuming that the null hypothesis is true.

In this example, the two-sided p value (also known as two-tailed p value ) is being reported instead of the one-sided p value. This is because the one-sided p value only allows for a one-sided or directional hypothesis, where the hypothesized difference is only tested in one direction or one tail of the normal curve. For a two-sided test, we allow for the possibility that one group could either be higher or lower than the other group on the dependent variable. Because the exact two-sided p value is 0.016, which is less than the alpha of 0.05, we can reject our null hypothesis ( Gray & Grove, 2021 ).

Final interpretation in American Psychological Association format
The following interpretation is written as it might appear in a research article, formatted according to American Psychological Association (APA) guidelines (2020). It should be noted that all statistical values reported here are rounded to two decimal places, with the exception of the p value, which is rounded to three decimal places.

A Mann-Whitney U test revealed that the primipara group had a significantly longer duration of labor analgesia than the multipara group, z = −2.40, p = 0.016, Mdn = 8.10 versus 3.30 hours, respectively. Thus parity may have an influence on the duration of labor analgesia and associated pain management. Further research is needed in this area.

Study questions

1.
Use SPSS to obtain the frequency distribution and skewness statistic for duration of labor analgesia as demonstrated in Exercise 27 . What do the results indicate?

2.
Use SPSS to compute the Shapiro-Wilk test of normality for the dependent variable, duration of labor analgesia in hours (h), as demonstrated in Exercise 27 . What do the results indicate?

3.
Do the data meet criteria for independent samples? Provide a rationale for your response.

4.
What is the null hypothesis in this example?

5.
Use SPSS to determine the exact likelihood of obtaining a U value at least as extreme or close to the one that was actually observed, assuming that the null hypothesis is true. Report the answer as a percentage.

6.
What scale of measurement is used for the duration of labor analgesia ?

7.
Why were medians reported in the interpretation of the results instead of means?

8.
If the dependent variable duration of labor analgesia was normally distributed, what would be the appropriate statistic to compare the two groups?

9.
What kind of design was implemented in the example? Does this design allow causal statements to be made for the effect of number of births on labor analgesia and pain management?

10.
Was the sample size adequate to detect differences between the two groups in this example? Provide a rationale for your answer.

Answers to study questions

1.
As shown here, the frequency distribution appears to be non-normally distributed. The skewness statistic is 1.359, indicating substantial positive skewness.

Calculating analysis of variance (ANOVA) and post hoc analyses after ANOVA EPUB version of this book
Susan K. Grove, PhD, RN, ANP-BC, GNP-BC; Daisha J. Cipher, PhD

Statistics for Nursing Research, EXERCISE 35, 456-473

Analysis of variance (ANOVA) is a statistical procedure that compares data between two or more groups or conditions to investigate the presence of differences between those groups on some continuous dependent variable (see Exercise 18 ). In this exercise, we will focus on the one-way ANOVA , which involves testing one independent variable and one dependent variable (as opposed to other types of ANOVAs, such as factorial ANOVAs that incorporate multiple independent variables).

Why ANOVA and not a t -test? Remember that a t -test is formulated to compare two sets of data or two groups at one time (see Exercise 23 for guidance on selecting appropriate statistics). Thus data generated from a clinical trial that involves four groups—treatment 1, treatment 2, treatments 1 and 2 combined, and a control—would require six t -tests. Consequently, the chance of making a Type I error (alpha error) increases substantially (or is inflated) because so many computations are being performed. Specifically, the chance of making a Type I error is the number of comparisons multiplied by the alpha level. Thus ANOVA is the recommended statistical technique for examining differences between more than two groups ( Tabachnick & Fidell, 2019 ; Zar, 2010 ).

ANOVA is a procedure that culminates in a value called the F statistic. It is this value that is compared against an F distribution (see Appendix C ) to determine whether the groups significantly differ from one another on the dependent variable. The formulas for ANOVA actually compute two estimates of variance: one estimate represents differences between the groups/conditions, and the other estimate represents differences among (within) the data.

Research designs appropriate for the one-way ANOVA
Research designs that may use the one-way ANOVA include the randomized experimental, quasi-experimental, and comparative designs ( Gliner et al., 2017 ). The independent variable (the grouping variable for the ANOVA) may be active or attributional. An active independent variable refers to an intervention, treatment, or program. An attributional independent variable refers to a characteristic of the participant, such as gender, diagnosis, or ethnicity. The ANOVA can compare two groups or more. In the case of a two-group design, the researcher can either select an independent samples t -test or a one-way ANOVA to answer the research question. The results will always yield the same conclusion, regardless of which test is computed; however, when examining differences between more than two groups, the one-way ANOVA is the preferred statistical test ( Tabachnick & Fidell, 2019 ).

Example 1: A researcher conducts a randomized experimental study wherein she randomizes participants to receive a high-dosage weight loss pill, a low-dosage weight loss pill, or a placebo. She assesses the number of pounds lost from baseline to posttreatment for the three groups. Her research question is: Is there a difference between the three groups in weight loss? The independent variables are the treatment conditions (high-dose weight loss pill, low-dose weight loss pill, and placebo) and the dependent variable is number of pounds lost over the treatment span.

Null hypothesis: There is no difference in weight lost among the high-dose weight loss pill, low-dose weight loss pill, and placebo groups in a population of overweight adults.

Example 2: A nurse researcher working in dermatology conducts a retrospective comparative study wherein she conducts a chart review of patients and divides them into three groups: psoriasis, psoriatic symptoms, or control. The dependent variable is health status, and the independent variable is disease group: psoriasis, psoriatic symptoms, and control. Her research question is: Is there a difference between the three groups on levels of health status?

Null hypothesis: There is no difference in health status among the psoriasis, psoriatic, and control groups of selected patients.

Statistical formula and assumptions
Use of the ANOVA involves the following assumptions ( Zar, 2010 ):

1.
Sample means from the population are normally distributed.

2.
The groups are mutually exclusive.

3.
The dependent variable is measured at the interval/ratio level.

4.
The groups should have equal variance, termed homogeneity of variance.

5.
All observations within each sample are independent.

The dependent variable in an ANOVA must be scaled as interval or ratio. If the dependent variable is measured with a Likert scale and the frequency distribution is approximately normally distributed, these data are usually considered interval-level measurements and are appropriate for an ANOVA (see Exercise 1 ; de Winter & Dodou, 2010 ; Rasmussen, 1989 ; Waltz et al., 2017 ).

The basic formula for the F without numerical symbols is:

F
=
Mean Square Between Groups
Mean Square Within Groups
The term mean square ( MS ) is used interchangeably with the word variance . The formulas for ANOVA compute two estimates of variance: the between-groups variance and the within-groups variance. The between-groups variance represents differences between the groups/conditions being compared, and the within-groups variance represents differences among (within) each group’s data. Therefore the formula is F = MS between/ MS within.

Hand calculations
This example involves a study of patients with inflammatory bowel disease (IBD) who underwent various types of treatment for prostate cancer ( Feagins et al., 2020 ). A retrospective multisite cohort study investigated three different types of treatment received for prostate cancer among persons with IBD: external radiotherapy (XRT), brachytherapy (a type of internal radiation therapy), or treatments that did not involve radiation, such as chemotherapy and hormonal therapy. Persons in the nonradiation group received hormonal therapy, chemotherapy, both hormonal and chemotherapy, or some other type of treatment that did not involve radiation.

The data are presented in Table 35.1 . A simulated subset was selected for this example so that the computations would be small and manageable. In actuality, studies involving one-way ANOVAs need to be adequately powered ( Aberson, 2019 ; Cohen, 1988 ). See Exercises 24 and 25 for more information regarding statistical power.

View full size
TABLE 35.1

GLEASON SCORES BY TREATMENT GROUP FOR PATIENTS WITH INFLAMMATORY BOWEL DISEASE AND PROSTATE CANCER

Participant#	XRT	Participant #	Brachytherapy	Participant #	Nonradiation
1	7	11	7	21	6
2	9	12	8	22	5
3	6	13	5	23	8
4	8	14	5	24	7
5	8	15	6	25	6
6	6	16	7	26	4
7	9	17	6	27	7
8	7	18	5	28	5
9	7	19	5	29	6
10	6	20	7	30	6
XRT, external radiotherapy.

The independent variable in this example is type of treatment (XRT, brachytherapy, or nonradiation treatment), and the dependent variable is a grading score related to prostate cancer cells, the Gleason score. The Gleason score ranges from 2 to 10, with higher numbers reflecting faster cancer growth and aggression ( Prostate Cancer Foundation, 2022 ).

The null hypothesis is: There is no difference between the treatment groups (XRT, brachytherapy, and nonradiation treatment) on prostate cancer grading scores among persons with IBD.

The computations for the ANOVA are as follows:

Step 1: Compute correction term, C .

Square the grand sum ( G ), and divide by total N:

C
=
194
2
30
=
1254.53
Step 2: Compute the Total sum of squares (SS).

Square every value in dataset, sum, and subtract C :

(
7
2
+
9
2
+
6
2
+
8
2
+
8
2
+
6
2
+
6
2
+
⋯
6
2
)
−
1254.53
=
1300.00
−
1254.53
=
45.47
Step 3: Compute Between-groups sum of squares.

Square the sum of each column and divide by N . Add each, and then subtract C :

73
2
10
+
61
2
10
+
60
2
10
−
1020.83
(
532.90
+
372.10
+
360.00
)
−
1254.53
=
10.47
Step 4: Compute Within-groups sum of squares.

Subtract the between-groups sum of squares (Step 3) from Total sum of squares (Step 2):

45.47
−
10.47
=
35.00
Step 5: Create ANOVA summary table (see Table 35.2 ).

a.
Insert the sum of squares values in the first column.

b.
The degrees of freedom ( df ) are in the second column. Because the F is a ratio of two separate statistics (mean square between groups and mean square within groups) both have different df formulas—one for the numerator and one for the denominator :

Mean square between-groups
df
= number of groups
−
1
Mean square within-groups
df
=
N
−
number of groups
For this example, the
df
for the numerator is 3
−
1 = 2.
The
df
for the denominator is 30
−
3 = 27.
c.
The mean square between groups and mean square within groups are in the third column. These values are computed by dividing the SS by the df . Therefore the MS between = 10.47 ÷ 2 = 5.235 rounded to 5.24. The MS within = 35.00 ÷ 27 = 1.30.

d.
The F is the final column and is computed by dividing the MS between by the MS within. Therefore F = 5.24 ÷ 1.30 = 4.03.

View full size
TABLE 35.2

ANOVA SUMMARY TABLE

Source of Variation	SS	df	MS	F
Between groups	10.47	2	5.24	4.03
Within groups	35.00	27	1.30	
Total	45.47	29		
Step 6: Locate the critical F value on the F distribution table (see Appendix C ) and compare it to our obtained F = 4.03 value. The critical F value for 2 and 27 df at α = 0.05 is 3.35, which indicates the F value in this example exceeds the critical value in the table. Thus the F is statistically significant and the population means are not equal. Therefore we can reject our null hypothesis that the three groups do not differ on prostate cancer grading scores among persons with IBD. However, the F does not indicate which groups differ from one another, and this F value does not identify which groups are significantly different from one another. Further testing, termed multiple comparison tests or post hoc tests , is required to complete the ANOVA process and determine all the significant differences among the study groups ( Field, 2013 ; Tabachnick & Fidell, 2019 ).

Post hoc tests
Post hoc tests have been developed specifically to determine the location of group differences after ANOVA is performed on data from more than two groups. These tests were developed to reduce the incidence of a Type I error. Frequently used post hoc tests are the Newman-Keuls test, the Tukey Honestly Significant Difference (HSD) test, the Scheffé test, and the Dunnett test ( Zar, 2010 ; see Exercise 18 for examples). When these tests are calculated, the alpha level is reduced in proportion to the number of additional tests required to locate statistically significant differences. For example, for several of the aforementioned post hoc tests, if many groups’ mean values are being compared, the magnitude of the difference is set higher than if only two groups are being compared. Thus post hoc tests are tedious to perform by hand and are best handled with statistical computer software programs. Accordingly, the rest of this example will be presented with the assistance of SPSS.

SPSS computations
This is how our dataset looks in SPSS.

A table displays participant data including I Ds, treatment groups, and Gleason scores. The interface includes a toolbar at the top, featuring multiple drop down options labeled File, Edit, View, Data, Transform, Analyze, Graphs, Utilities, and Extensions. Below the menu options, a row of icons supports quick actions a folder symbol, a floppy disk icon, a printer icon, undo and redo arrows, a data view shortcut, a graph shortcut, and other task related tools. The table underneath contains 16 rows of participant data, with columns showing I D numbers, treatment group codes, and Gleason scores. The Participant I D column lists numbers from 1 to 16. The Treatment Group column includes entries marked 1 or 2. The Gleason score column shows values that range between 5 and 9. Below this, two tabs show one data view and another variable view.

Step 1: Because the dependent variable, Gleason score, is measured ordinally, it must be examined for normality prior to submitting the data for a one-way ANOVA. Normality will be examined for all treatment groups, and within each treatment group. As reviewed in Exercise 27 , from the “Analyze” menu, choose “Descriptive Statistics” and “Explore.” Move Gleason score over to the box labeled “Dependent List.” Click “Plots.” Check “Normality plots with tests.” Click “Continue” and “OK.” As shown, the distribution of Gleason scores did not significantly deviate from normality according to the Shapiro-Wilk test ( p = 0.081).

A table presents normality test results for Gleason Score Post Treatment using two methods. The table displays outcomes of normality checks for the Gleason Score Post Treatment. Kolmogorov-Smirnov superscript a method shows a statistic of.179, degrees of freedom as 30, and significance as.016. Shapiro-Wilk method shows a statistic of.938, degrees of freedom 30, and significance of.081. A note at the bottom mentions Lilliefors Significance Correction with label a.
Step 2: Subsequently, normality of the Gleason scores will be examined within each treatment group. From the “Analyze” menu, choose “Descriptive Statistics” and “Explore.” Move Gleason score over to the box labeled “Dependent List” and move “Treatment Group” over to the box labeled “Factor List.” Click “Plots.” Check “Normality plots with tests.” Click “Continue” and “OK.”

A configuration window displays a selection of the Gleason Score as a dependent list and Treatment Group as a factor list. The window shows a dialog for defining variables. The left side presents a list box titled Participant I D. To its right, arrows allow variables to move into three destination boxes labeled Dependent List, Factor List, and Label cases by. The Dependent List contains Gleason Score, the Factor List contains Treatment Group, and the Label cases by with blank space. To the right, display buttons labeled Statistics, Plots, Options, and Bootstrap. A section underneath shows radio buttons titled Display with choices Both, Statistics, and Plots. At the bottom, there are buttons titled OK, Paste, Reset, Cancel, and Help.
As shown, the distribution of Gleason scores did not significantly deviate from normality for any of the groups according to the Shapiro-Wilk test, with p values ranging from 0.067 for the brachytherapy group to 0.703 for the nonradiation group. Therefore we will proceed with the one-way ANOVA analysis.

A table presents normality test results for the Gleason Score Post Treatment grouped by different treatment groups. The table shows normality test outcomes for Gleason Score Post Treatment across X R T, Brachytherapy, and Non Radiation treatment groups. The Kolmogorov Smirnov superscript a section reports statistics as.202,.241, and.200 respectively for each group, with degrees of freedom marked as 10 for all and significance values shows as.200,.103, and.200. The Shapiro Wilk section reports statistics as.878 for X R T,.855 for Brachytherapy, and.953 for Non Radiation, with each group listed as 10 degrees of freedom and significance values shows as.124,.067, and.703. An asterisk note explains the significance as a lower bound. A note at the bottom mentions Lilliefors Significance Correction with label a.

Step 3: From the “Analyze” menu, choose “Compare Means” and “One-Way ANOVA.” Move the dependent variable, “Gleason Score”, over to the right, as shown.

Step 4: Move the independent variable, “Treatment Group”, to the right in the space labeled “Factor.”

A dialog box shows selection of Gleason Score Post Treatment as dependent and Treatment Group as factor for one way A N O V A. The dialog box presents a setup for one way A N O V A testing. The left section displays a box titled Participant I D. A right pointing arrow moves this item into the selection boxes. Gleason Score Post Treatment appears in the Dependent List, and Treatment Group appears in the Factor List. A checkbox marked Estimate effect size for overall tests appears below the Factor box. On the right side of these, four buttons titled Contrasts, Post Hoc, Options, and Bootstrap enable test configuration. The lower section presents five buttons named OK, Paste, Reset, Cancel, and Help.
Step 5: Click “Options.” Check the boxes next to “Descriptive” and “Homogeneity of variance test.” Click “Continue” and “OK.”

A dialog box presents selected options for one way A N O V A testing with confidence interval and missing values settings. The dialog box title with One Way A N O V A Options includes three rectangular shaped box with names Statistics, Missing Values, and Confidence Interval. In Statistics, two options show selected, which include Descriptive and Homogeneity of Variance Test. Fixed and Random effects, Brown Forsythe Test, Welch Test, and Means Plot show unselected. The Means plot lies outside the rectangle. The section titled Missing Values presents two options. Exclude Cases Analysis by Analysis shows selected, and Exclude Cases Listwise shows unselected. The Confidence Intervals section displays the level set to 0.95 in percentage. Buttons at the bottom present Continue, Cancel, and Help.
Interpretation of SPSS output
The following tables are generated from SPSS. The first table contains descriptive statistics for Gleason score, separated by the three groups. The second table contains the Levene’s test of homogeneity of variances. The third table contains the ANOVA summary table, along with the F and p values.

The first table displays descriptive statistics that allow us to observe the means for the three groups. This table is important because it indicates that the patients who received XRT had a mean Gleason score of 7.30, compared with 6.10 for patients who received brachytherapy, and 6.00 for patients who received nonradiation treatment. Recall that the higher the Gleason score, the more aggressive and rapid growing are the prostate cancer cells.


A table presents descriptive statistics for Gleason Score Post Treatment across three treatment categories. The table presents numerical summaries for Gleason Score Post Treatment under three treatment categories X R T, Brachytherapy, and Non Radiation. Each group includes ten observations. Mean values for X R T, Brachytherapy, and Non Radiation appear as 7.30, 6.10, and 6.00, respectively. The overall mean is 6.47. Standard deviation shows 1.160, 1.101, and 1.155, respectively. Standard error values show.367,.348, and.365, respectively. Confidence interval bounds for the mean appear with lower limits shows 6.47, 5.31, and 5.17, and upper limits shows 8.13, 6.89, and 6.83, respectively. Minimum and maximum scores range from 4 to 9. The final total values show for N 30, Standard deviation 1.252, Standard error.229, Lower bound 6.00, Upper bound 6.93, Minimum 4, and Maximum 9.
The second table contains the Levene’s test for equality of variances. The Levene’s test is a statistical test of the equal variances assumption ( Field, 2013 ; Tabachnick & Fidell, 2019 ). As is shown on the first row of the table, the p value is 0.843, indicating there was no significant difference among the three groups’ variances; thus the data have met the equal variances assumption for ANOVA.


A table presents four statistical outputs from tests of homogeneity of variances on Gleason Score Post Treatment. The table titled Tests of Homogeneity of Variances presents results based on four statistical methods for evaluating Gleason Score Post Treatment. The first row labeled Based on Mean displays Levene Statistic as.171, degrees of freedom 1 and 2 show as 2 and 27, and significance presents.843. The second row labeled Based on Median displays Levene Statistic as.067, degrees of freedom 1 and 2 show as 2 and 27, and significance presents.935. The third row, labeled Based on Median and with adjusted degrees of freedom, displays Levene Statistic as.067, degrees of freedom 1 and 2 show as 2 and 25.338, and significance presents.935. The fourth row labeled Based on Trimmed Mean displays Levene Statistic as.155, degrees of freedom 1 and 2 show as 2 and 27, and significance presents.857.
The last table contains the contents of the ANOVA summary table, which looks much like Table 35.2 . It should be noted that the F value of 4.037 in the output table differs slightly from our hand calculations of 4.03 because we used two decimal places in our hand calculations, while SPSS uses many decimals in computations and is therefore more accurate. Thus when reporting results, the values from the SPSS output should be reported because they have higher accuracy. This table also contains an additional value that we did not compute by hand—the exact p value, which is 0.029. Because the SPSS output indicates that we have a significant ANOVA, post hoc testing must be performed.


A table titled A N O V A displays variance analysis results for Gleason Score Post Treatment across groups, showing significant group level differences. The table titled A N O V A presents results from an analysis of variance conducted on Gleason Score Post Treatment across two groups. The first row labeled Between Groups shows a sum of squares value of 10.467 with degrees of freedom marked as 2, and a mean square value of 5.233. The second row labeled Within Groups presents a sum of squares value of 35.000, degrees of freedom marked as 27, and a mean square value of 1.296. The third row labeled Total shows a sum of squares value of 45.467 and degrees of freedom marked as 29. In the first row, the last two columns for F value display as 4.037, and the significance level presents as 0.029.
Return to the ANOVA window and click “Post Hoc.” You will see a window similar to the one shown. Select the “LSD” and “Tukey” options. Click “Continue” and “OK.”


A dialog box with three sections used for selecting post hoc tests in a one way analysis of variance multiple comparisons. The illustration shows a dialog box for selecting post hoc tests following one way analysis of variance for multiple comparisons. The interface has three sections labeled Equal Variances Assumed, Equal Variances Not Assumed, and Null Hypothesis test. In Equal Variances Assumed, checkboxes are provided for L S D, Bonferroni, Sidak, Scheffe, R E G W F, R E G W Q, S N K, Tukey, Tukeys b, Duncan, Hochberg s G T 2, Gabriel, Waller Duncan, and Dunnett. L S D and Tukey selected with tick mark. Dunnett includes three radio buttons labeled Control Category Last, Test two sided, less than Control, and greater than Control. Two sided mark with the right sign other two remain unselected. The Equal Variances Not Assumed section includes Tamhanes T 2, Dunnetts T 3, Games Howell, and Dunnetts C. No option selected. The Null Hypothesis test section shows two options use the same significance level alpha as the setting in Options and Specify the significance level alpha for the post hoc test. The first option mark with the right sign. The second shows a level value set to 0.05. Buttons labeled Continue, Cancel, and Help appear at the bottom of the dialog box.Calculating sensitivity and specificity EPUB version of this book
Susan K. Grove, PhD, RN, ANP-BC, GNP-BC; Daisha J. Cipher, PhD

Statistics for Nursing Research, EXERCISE 36, 474-489

An important part of building evidence-based practice is the ability to differentiate between people who have a disease and those who do not. This is accomplished by using the most accurate and precise measure or test to promote quality outcomes. Regardless of whether the test is used by clinicians or researchers, the same issue is raised—how good is the screening test in separating patients with and without a disease? This question is best answered by current, quality research to determine the sensitivity and specificity of the test ( Celentano & Szklo, 2018 ).

The accuracy of a screening test or a test used to confirm a diagnosis is evaluated in terms of its ability to correctly assess the presence or absence of a disease or condition compared with a gold standard. The gold standard is the most accurate means of currently diagnosing a particular disease and serves as a basis for comparison with newly developed diagnostic or screening tests ( Campo et al., 2010 ; Celentano & Szklo, 2018 ). As shown in Table 36.1 , there are four possible outcomes of a screening test for a disease: (1) sensitivity , or true positive, which accurately identifies the presence of a disease; (2) false positive , which indicates a disease is present when it is not; (3) specificity , or true negative, which indicates accurately that a disease is not present; or (4) false negative , which indicates that a disease is not present when it is ( Celentano & Szklo, 2018 ; Straus et al., 2019 ).

View full size
TABLE 36.1

RESULTS OF SENSITIVITY AND SPECIFICITY OF SCREENING TESTS

Disease Present	Disease Not Present
Positive test	True positive = sensitivity	False positive
Negative test	False negative	True negative = specificity
Statistical formula and assumptions
Sensitivity and specificity
Sensitivity and specificity can be calculated based on research findings and clinical practice outcomes to determine the most accurate diagnostic or screening tool to use in identifying the presence or absence of a disease for a population of patients. The calculations for sensitivity and specificity are provided as follows. Table 36.2 displays the following notation to assist the researcher in calculating the sensitivity and specificity of a screening test, where:

a = The number of people who have the disease and the test is positive (true positive)
b = The number of people who do not have the disease and the test is positive (false positive)
c = The number of people who have the disease and the test is negative (false negative)
d = The number of people who do not have the disease and the test is negative (true negative)
View full size
TABLE 36.2

STRUCTURE OF DATA FOR SENSITIVITY AND SPECIFICITY CALCULATIONS

Disease Present	Disease Not Present
Positive test	a	b
Negative test	c	d
The disease variable (present/absent) is often called the state variable. It is always dichotomous. The screening test variable can be either dichotomous or continuous (such as a lab value). If the screening test is continuous, sensitivity and specificity are repeatedly calculated for each individual test value ( Melnyk & Fineout-Overholt, 2023 ; Straus et al., 2019 ).

Sensitivity calculation = probability of having the disease
= a /( a + c )
= true positive rate
Specificity calculation = probability of the absence of disease
= d /( b + d )
= true negative rate
False positive calculation = probability of no disease but having a positive test
= b /( b + d )
= false positive rate
False negative calculation = probability of having the disease but having a negative test
= c /( c + a )
= false negative rate
Sensitivity is the proportion of patients with the disease who have a positive test result, or true positive. The ways the researcher or clinician might refer to the test sensitivity include the following:

■
A highly sensitive test is very good at identifying the patient with a disease.

■
If a test is highly sensitive, it has a low percentage of false negatives.

■
A low-sensitivity test is limited in identifying the patient with a disease.

■
If a test has low sensitivity, it has a high percentage of false negatives.

■
If a sensitive test has negative results, the patient is less likely to have the disease.

Specificity of a screening or diagnostic test is the proportion of patients without the disease who have a negative test result, or true negative. The ways the researcher or clinician might refer to the test specificity include the following:

■
A highly specific test is very good at identifying patients without a disease.

■
If a test is very specific, it has a low percentage of false positives.

■
A low-specificity test is limited in identifying patients without a disease.

■
If a test has low specificity, it has a high percentage of false positives.

■
If a specific test has positive results, the patient is more likely to have the disease.

Likelihood ratios
Likelihood ratios (LRs) are additional calculations that can help researchers to determine the accuracy of diagnostic or screening tests, which are based on the sensitivity and specificity results. LRs are calculated to determine the likelihood that a positive test result is a true positive and a negative test result is a true negative.

The ratio of the true positive results to false positive results is known as the positive LR ( Melnyk & Fineout-Overholt, 2023 ). The positive LR is calculated as follows:

Positive LR = Sensitivity ÷ (1– Specificity)
The ratio of true negative results to false negative results is known as the negative LR , and it is calculated as follows:

Negative LR = (1– Sensitivity) ÷ Specificity
A LR greater than 1.0 represents an increase in the likelihood of the disease, while a LR of less than 1.0 represents a decrease in the likelihood of the disease. The very high LRs (or LRs that are >10) rule in the disease or indicate that the patient has the disease. The very low LRs (or LRs that are <0.1) virtually rule out the chance that the patient has the disease ( Campo et al., 2010 ; Celentano & Szklo, 2018 ). Understanding sensitivity, specificity, and LR increases the researcher’s ability to read clinical studies and to determine the most accurate diagnostic test to use in research and clinical practice ( Celentano & Szklo, 2018 ; Elmore et al., 2020 ).

Receiver operating characteristic curves
In studies that compute sensitivity and specificity, a receiver operating characteristic (ROC), or ROC curve, is often created. An ROC curve is a descriptive graph that plots the true positive rate against the false positive rate. The x -axis represents the false positive rate (1 − specificity), and the y -axis represents the true positive rate (sensitivity). The actual rates are plotted and a line is drawn between the numbers. The larger the area under that line, the more accurate the test. The actual area under the line can be calculated by a value called the C statistic. The C statistic , or area under the curve, is the probability that the test result from a randomly selected person with the disease will be positive ( Austin & Steyerberg, 2012 ; Elmore et al., 2020 ).

Hand calculations
This example uses simulated data involving the alpha fetoprotein (AFP) test and its ability to identify a prenatal diagnosis of neural tube defects (NTDs). AFP testing involves the detection of AFP levels in amniotic fluid, and the results yield either a normal or abnormal result ( Mayo Foundation for Medical Education and Research, 2022 ). As shown in Table 36.3 , to analyze the sensitivity and specificity of these data, a pregnancy outcome of NTD will be considered the disease, also known as the state variable. The screening test variable is the presence of an abnormal AFP test result or a normal AFP test result.

View full size
TABLE 36.3

ALPHA FETOPROTEIN TEST RESULTS AND NEURAL TUBE DEFECTS AS A PREGNANCY OUTCOME

NTDs	Normal
Abnormal AFP test	127	180
Normal AFP test	20	99,673
AFP, alpha fetoprotein; NTDs, neural tube defects.

The computations for sensitivity, specificity, positive LR, and negative LR are as follows:

Sensitivity calculation

Sensitivity = a/(a + c)
127
127
+
20
=
0.8639
×
100
%
=
86.39
%
Specificity calculation

Specificity = d/(b + d)
99
,
673
180
+
99
,
673
=
0.9982
×
100
%
=
99.82
%
Positive LR calculation

Positive LR = Sensitivity ÷ (1– Specificity)
0.8639 ÷ (1–0.9982) = 479.94
Negative LR calculation

Negative LR = (1–Sensitivity) ÷ Specificity
(1–0.8639) ÷ 0.9982 = 0.1363
The sensitivity of the test was 86.39%, indicating that the proportion of pregnancy outcomes identified as NTD who were correctly identified as positive by their AFP tests was 86.39%. The specificity of the test was 99.82%, indicating that the proportion of patients with normal pregnancy outcomes who were correctly identified as normal by their AFP test was 99.82%. The positive LR was 479.94, indicating a large likelihood of NTDs among those with abnormal AFP test results. The negative LR was 0.1363, indicating a very low likelihood of NTDs among those who with normal AFP test results ( Celentano & Szklo, 2018 ).

SPSS computations
This is how our dataset looks in SPSS. The data for observations 17 through 100,000 are viewable by scrolling down in the SPSS screen. The values in the dataset must be coded as “1” or “0” for the state variable and the test variable, where a “1” indicates the presence of NTD for the pregnancy outcome and the presence of an abnormal AFP test, respectively.

A screenshot of a data view table with variables labeled A P P T Test and H T D. The screenshot shows a data view window from statistical software containing two variables labeled A P P T Test and H T D. The table includes 16 rows, all filled with the value 0 under both columns. The top menu bar displays dropdown options including File, Edit, View, Data, Transform, and Analyze.
Step 1: From the “Analyze” menu, choose “Descriptive Statistics” and “Crosstabs.” Move the two variables to the right, where either variable can be in the “Row” or “Column” space. Click “OK.”

A screenshot of a Crosstabs dialog box with APPT Test Result in rows and HTD as Pregnancy Outcome in columns. The screenshot shows a Crosstabs dialog box from statistical software. The variable A P P T Test Result is assigned to the Rows field, and H T D as Pregnancy Outcome is assigned to the Columns field. There is an option for adding a layer variable, which is empty. Two checkboxes at the bottom are labeled Display clustered bar charts and Suppress tables, both left unchecked. Buttons for OK, Paste, Reset, Cancel, and Help appear at the bottom.
Step 2: From the “Analyze” menu, choose “Classify,” and “ROC Curve.” Move AFP test to the box labeled test variable, and move NTD to the box labeled “State Variable.” Enter the number “1” next to the box labeled “Value of State Variable.” Check all of the boxes underneath (“ROC Curve,” “With diagonal reference line,” “Standard error and confidence interval,” and “Coordinate points of the ROC Curve”). Click “OK.”

A screenshot of R O C Curve dialog box with A P P T Test Result as test variable and H T D as Pregnancy Outcome as state variable. The screenshot shows the R O C Curve dialog box. The test variable is set as A P P T Test Result, and the state variable is set as H T D as Pregnancy Outcome. Below the state variable, the value of the state variable is set to 1. Display options include R O C Curve, Standard error and confidence interval, Diagonal reference line, and Coordinate points along the R O C Curve.
Interpretation of SPSS output
The following tables are generated from SPSS. The first table contains the contingency table, similar to Table 36.3 , presented previously. The following tables and figure are generated from the “ROC Curve” menu.

Crosstabs

A screenshot of a cross tabulation table between A P P T Test Result and H T D as Pregnancy Outcome. The screenshot displays a cross tabulation table with rows labeled A P P T Test Result and columns labeled H T D as Pregnancy Outcome. The table includes count values arranged under Yes and No columns. The APPT Test Result row shows values for Yes and No, and the total row aggregates those counts. Totals are aligned in both rows and columns, and values are shown for the combination of test results and outcomes.
The first table is the cross-tabulation table of the two variables. The values are the same as in Table 36.3 . The next set of output is generated from the ROC menu selections. The first table contains the number of women whose pregnancy outcomes were positive and negative for NTDs.

A screenshot of a case processing summary table for R O C Curve analysis. The screenshot shows a case processing summary table labeled R O C Curve. The table lists H T D as Pregnancy Outcome with two categories Positive and Negative. Valid N for Positive is 147, and for Negative is 36853
The second table contains the ROC curve, where the x -axis represents the false positive rate (1 − specificity), and the y -axis represents the true positive rate (sensitivity). The blue line represents our actual data, and the black line is the reference line that represents a 50/50 chance of accurately predicting NTDs. The greater the distance the blue line is from the black line, the more accurate the test.


A screenshot of an R O C Curve graph comparing sensitivity and 1 minus specificity. The screenshot displays an R O C Curve graph. The xaxis is labeled 1 minus Specificity, and the yaxis is labeled Sensitivity. The graph shows a diagonal reference line and an R O C Curve above it, indicating performance of a binary classification test. A label inside the graph marks the R O C Curve line.
In the table titled “Area Under the Curve,” the first value labeled “Area” is also considered the C statistic. The area under the curve is the probability that the AFP test from a randomly selected pregnancy outcome of NPDs will be abnormal. For the example data, the probability that an AFP test from a randomly selected pregnancy outcome of NTD will be abnormal is 0.931 or 93.1%. The p value is listed as “.000,” which is interpreted as p < 0.001, indicating that knowing the AFP test value (abnormal AFP test) is significantly better than guessing. The 95% confidence interval for the C statistic was 0.898 to 0.964, which can be interpreted as the interval of 89.8% to 96.4% estimates the population C statistic with 95% confidence ( Kline, 2004 ; United States Census, 2021).


A screenshot of the Area Under the Curve table shows A U C value and confidence interval for A P P T Test Result. The screenshot displays a table titled Area Under the Curve. The test result variable is A P P T Test Result, and the area under the curve is shown as 0.931. The standard error is 0.017, with an asymptotic significance value of less than 0.00. The 95 percent confidence interval ranges from 0.898 to 0.964. A note below the table states that the C statistic is 0.931, with a 93.10 percent confidence interval.
The last table contains the sensitivity and 1 − specificity of AFP tests, which is listed as 0.864 and 0.002, respectively. Because 1 − specificity is 0.002, the specificity equals 0.998, or 99.8%.


A screenshot of R O C Curve coordinates table shows sensitivity and 1 minus specificity for different threshold values. The screenshot shows a table titled Coordinates of the Curve with test result variable labeled as A P P T Test Result. It lists threshold values with corresponding Sensitivity and 1 minus Specificity values. For a test value of 1.00, sensitivity is 1.000 and 1 minus specificity is 0.118. For a value of 2.00, sensitivity is 0.864 and 1 minus specificity is 0.002. A note below the table explains that sensitivity is 86.4 percent and 1 minus specificity is 0.2 percent, indicating specificity is 99.8 percent.
Study questions

1.
Discuss the sensitivity of a screening test and its importance in diagnosing a disease.

2.
Discuss the specificity of a screening test and its importance in diagnosing a disease.

3.
Define false positive rate.

4.
What is the difference between a test variable and a state variable when calculating sensitivity and specificity?

5.
Define the C statistic and how it relates to sensitivity and specificity.

6.
The specificity of the screening test for the AFP test was 99.82%. What are the implications for the ability of the test to identify patients with a normal AFP test result?

7.
What was the false positive rate of the AFP test?

8.
What was the false negative rate of the AFP test?

9.
In the ROC curve for the AFP test example, what were the coordinates used to represent the blue line?

10.
List the 95% confidence interval of the C statistic and state your interpretation of that interval.

Calculating the Pearson chi-square EPUB version of this book
Susan K. Grove, PhD, RN, ANP-BC, GNP-BC; Daisha J. Cipher, PhD

Statistics for Nursing Research, EXERCISE 37, 490-503

The Pearson chi-square test ( χ 2 ) compares differences between groups on variables measured at the nominal level. The chi-square compares the frequencies that are observed with the frequencies that are expected. When a study requires that researchers compare proportions (percentages) in one category versus another category, the chi-square is a statistic that will reveal if the difference in proportion is statistically improbable.

A one-way chi-square is a statistic that compares different levels of one variable only. For example, a researcher may collect information on gender and compare the proportions of males to females. If the one-way chi-square is statistically significant, it would indicate that proportions of one gender are significantly higher than proportions of the other gender than what would be expected by chance ( Daniel, 2000 ; Pett, 2016 ). If more than two groups are being examined, the chi-square does not determine where the differences lie; it only determines that a significant difference exists. Further testing on subgroups of the data with the Pearson chi-square test would then be warranted to identify the significant differences.

A two-way chi-square is a statistic that tests whether proportions in levels of one nominal variable are significantly different from proportions of the second nominal variable. For example, Conlon and colleagues (2021) conducted a large retrospective cohort study to examine demographic and clinical differences between those who tested negative versus positive for novel coronavirus of 2019 (COVID-19) (see Exercise 19 ). One of the null hypotheses tested was: There is no difference between persons who tested negative versus positive for COVID-19 on the presence of diabetes. The results of the chi-square test indicated that the rates of diabetes were significantly higher among those who tested positive for COVID-19 ( Conlon et al., 2021 ), suggesting that diabetes may be a risk factor for developing COVID-19. Further examples of two-way chi-square tests are reviewed in Exercise 19 .

Research designs appropriate for the Pearson chi-square
Research designs that may use the Pearson chi-square include the randomized experimental, quasi-experimental, and comparative designs ( Gliner et al., 2017 ). The variables may be active, attributional, or a combination of both. An active variable refers to an intervention, treatment, or program. An attributional variable refers to a characteristic of the participant, such as gender, diagnosis, or race/ethnicity. Regardless of the whether the variables are active or attributional, all variables submitted to chi-square calculations must be measured at the nominal level.

Statistical formula and assumptions
Use of the Pearson chi-square involves the following assumptions ( Daniel, 2000 ):

1.
Only one datum entry is made for each participant in the sample. Therefore if repeated measures from the same participant are being used for analysis, such as pretests and posttests, chi-square is not an appropriate test.

2.
The variables must be categorical (nominal), either inherently or transformed to categorical from quantitative values.

3.
For each variable, the categories are mutually exclusive and exhaustive. No cells may have an expected frequency of zero. In the actual data, the observed cell frequency may be zero. However, the Pearson chi-square test is not sensitive to small sample sizes, and other tests, such as the Fisher exact test, are more appropriate when testing very small samples ( Daniel, 2000 ; Yates, 1934 ).

The test is distribution free, or nonparametric, which means that no assumption has been made for a normal distribution of values in the population from which the sample was taken ( Daniel, 2000 ).

The formula for a two-way chi-square is:

χ
2
=
n
[
(
A
)
(
D
)
−
(
B
)
(
C
)
]
2
(
A
+
B
)
(
C
+
D
)
(
A
+
C
)
(
B
+
D
)
A contingency table displays the relationship between two or more categorical variables ( Daniel, 2000 ). The contingency table is labeled as follows.

View full size
Columns	
Rows	A	B
C	D
With any chi-square analysis, the degrees of freedom ( df ) must be calculated to determine the significance of the value of the statistic. The following formula is used for this calculation:

df
=
(
R
−
1
)
(
C
−
1
)
where

R
=
Number
of
rows
C
=
Number
of
columns
Hand calculations
Conlon and colleagues (2021) conducted a retrospective cohort study to assess the role of the influenza vaccine on COVID-19 susceptibility and severity. The primary study aim was the comparison of positive and negative COVID-19 testing in those who received the influenza vaccine versus those who did not. Other study variables included baseline patient characteristics and the presence of comorbidities. Over 4.5 million unique patient charts within the Michigan Medicine healthcare system were extracted, and of those, 27,201 patients received laboratory testing for COVID-19.

The data are presented in Table 37.1 . The null hypothesis is: There is no difference between persons who tested negative versus those who tested positive for COVID-19 on history of a recent influenza vaccine.

View full size
TABLE 37.1

COVID-19 TEST RESULTS BY INFLUENZA VACCINE

COVID–19 Positive ( n = 1218)	COVID–19 Negative ( n = 25,983)	Totals	
Influenza vaccine	525	12,472	12,997	
No influenza vaccine	693	13,511	14,204	
Totals	1,218	25,983	27,201	←︎Total N
COVID-19, novel coronavirus of 2019.

The computations for the Pearson chi-square test are as follows:

Step 1: Create a contingency table of the two nominal variables (see Table 37.1 ).

Step 2: Fit the cells into the formula:

χ
2
=
n
[
(
A
)
(
D
)
−
(
B
)
(
C
)
]
2
(
A
+
B
)
(
C
+
D
)
(
A
+
C
)
(
B
+
D
)
χ
2
=
27
,
201
[
(
525
)
(
13
,
511
)
−
(
12
,
472
)
(
693
)
]
2
(
525
+
12
,
472
)
(
693
+
13
,
511
)
(
525
+
693
)
(
12
,
472
+
13
,
511
)
χ
2
=
27
,
201
(
−
1
,
549
,
821
)
2
(
12
,
997
)
(
14
,
204
)
(
1
,
218
)
(
25
,
983
)
χ
2
=
65
,
335
,
309
,
536
,
647
,
200
5
,
842
,
387
,
577
,
196
,
070
χ
2
=
11.18
Step 3: Compute the df :

df
=
(
2
−
1
)
(
2
−
1
)
=
1
Step 4: Locate the critical chi-square value in the chi-square distribution table ( Appendix D )and compare it to the obtained chi-square value.

The table in Appendix D includes the critical values of chi-square for specific df at selected levels of significance. If the value of the statistic is equal to or greater than the value identified in the chi-square table, the difference between the two variables is statistically significant. The critical chi-square for df =1 is 3.8415, which was rounded to 3.84, and our obtained chi-square is 11.18. Thus the obtained chi-square value exceeds the critical value, which indicates a significant difference between persons who tested negative versus positive for COVID-19 on history of a recent influenza vaccine.

Furthermore we can compute the rates of influenza vaccines among those with positive and negative COVID-19 tests by using the numbers in the contingency table from Step 1. The influenza vaccine rate among those who tested positive can be calculated as 525 ÷ 1218 = 0.4310 × 100% = 43.1%. The influenza vaccine rate among those who tested negative can be calculated as 12,472 ÷ 25,983 = 0.4800 × 100% = 48.0%.

SPSS computations
The following screenshot is a replica of what the SPSS dataset will look like. The data for participants 17 through 27,201 are viewable by scrolling down in the SPSS screen.

A screenshot of a data entry table with two columns labeled COVID Positive and Flu Income. The screenshot shows a data view window from a statistical software displaying two variables labeled COVID Positive and Flu Income. Each variable has 16 rows of data populated with binary values of 0 and 1. The toolbar above contains dropdown menus labeled File, Edit, View, Data, Transform, Analyze, Graphs, Utilities, and Extensions. Below the table, two tabs labeled Data View and Variable View are visible.

Step 1: From the “Analyze” menu, choose “Descriptive Statistics” and “Crosstabs.” Move the two variables to the right, where either variable can be in the “Row” or “Column” space.

A screenshot of a Crosstabs dialog box with COVID Positive in rows and Flu Income in columns. The screenshot shows the Crosstabs dialog box in a statistical software interface. The dialog contains a list of variables on the left and three fields labeled Rows, Columns, and Layer. The variable COVID Positive is placed in the Rows field, and Flu Income is placed in the Columns field. Options for clustered bar charts, count display, and cell percentages are also shown on the right side of the dialog box.
Step 2: Click “Statistics” and check the box next to “Chi-square.” Click “Continue” and “OK.”

A screenshot of the Crosstabs Statistics dialog box with Chi square selected. The screenshot displays the Crosstabs Statistics dialog box with a list of statistical options including Chi square, Phi, Cramer's V, Contingency coefficient, Lambda, and Risk. The Chi square option is selected, and buttons for Continue, Cancel, and Help are visible at the bottom of the window.
Interpretation of SPSS output
The following tables are generated from SPSS. The first table contains the contingency table, similar to Table 37.1 , presented previously. The second table contains the chi-square results.

A crosstab shows the relationship between influenza vaccination and COVID 19 test results. The screenshot shows a crosstabulation table from S P S S examining the relationship between receiving the influenza vaccine and testing positive for COVID 19. Among those who did not receive the influenza vaccine, 13511 tested negative and 693 tested positive, totaling 14204 individuals. Among those who received the influenza vaccine, 12472 tested negative and 525 tested positive, totaling 12997 individuals. The overall total is 25983 negative and 1218 positive cases, with a grand total of 27201 participants. The table header reads Received Influenza Vaccine by Tested Positive for COVID 19 Crosstabulation, and the rows are grouped by vaccination status with test result counts presented in the columns.
A screenshot shows Chi Square test results indicating a significant association. The screenshot shows the Chi Square Tests table from S P S S evaluating the association between receiving the influenza vaccine and testing positive for COVID 19. The Pearson Chi Square value is 11.183 with 1 degree of freedom and a significance value less than point 001. The Continuity Correction value is 10.988 with significance less than point 001. The Likelihood Ratio is 11.228 with significance less than point 001. Fisher's Exact Test also reports two sided and one sided p values both less than point 001. The Linear by Linear Association value is 11.183 with 1 degree of freedom and significance less than point 001. The number of valid cases is 27201. A footnote indicates that no cells have expected counts less than 5 and the minimum expected count is 581.98. Another note mentions the Continuity Correction is computed only for a 2 by 2 table.
The last table contains the chi-square value in addition to other statistics that test associations between nominal variables. The Pearson chi-square test is located in the first row of the table, which contains the chi-square value, df , and p value.

Final interpretation in American Psychological Association format
The following interpretation is written as it might appear in a research article, formatted according to American Psychological Association (APA) guidelines (2020). It should be noted that all statistical values reported here are rounded to two decimal places, with the exception of the p value, which is rounded to three decimal places.

A Pearson chi-square analysis indicated that those who tested negative for COVID-19 had significantly higher rates of influenza vaccines than those who tested positive for COVID-19, chi-square(1, N = 27,201) = 11.18, p < 0.001 (48.00% versus 43.10%, respectively). This finding suggests that receiving a recent influenza vaccine may be a protective factor for acquiring COVID-19, and further research is needed to investigate the effect of influenza vaccines on testing positive for COVID-19.

Study questions

1.
Do the example data meet the assumptions for the Pearson chi-square test? Provide a rationale for your answer.

2.
State the null hypothesis. Was the null hypothesis accepted or rejected? Provide a rationale for your answer.

3.
What is the exact likelihood of obtaining a chi-square value at least as extreme or close to the one that was actually observed, assuming that the null hypothesis is true?

4.
Using the numbers in the contingency table, calculate the percentage of people who tested positive for COVID-19 among those who received a recent influenza vaccine. In other words, calculate the COVID-19 positivity rate among those who received an influenza vaccine. Show your calculations.

5.
Using the numbers in the contingency table, calculate the percentage of people who tested negative for COVID-19 among those who received a recent influenza vaccine. In other words, calculate the COVID-19 negativity rate among those who received an influenza vaccine. Show your calculations.

6.
Using the numbers in the contingency table, calculate the percentage of people who tested positive for COVID-19 among those who did not receive a recent influenza vaccine. In other words, calculate the COVID-19 positivity rate for those who did not receive an influenza vaccine. Show your calculations.

7.
Using the numbers in the contingency table, calculate the percentage of people who tested negative for COVID-19 among those who did not receive a recent influenza vaccine. In other words, calculate the COVID-19 negativity rate among those who did not receive an influenza vaccine. Show your calculations.

8.
Was this an appropriate research design for a Pearson chi-square analysis? Provide a rationale for your answer.

9.
What result would have been obtained if the variables in the SPSS “Crosstabs” window had been switched, with the COVID-19 test variable placed in the “Row” and the influenza vaccine variable placed in the “Column”?

10.
Was the sample size adequate to detect differences between the two groups in this example? Provide a rationale for your answer.

Answers to study questions

1.
Yes, the data meet the assumptions of the Pearson chi-square:

a.
Only one datum per participant was entered into the contingency table, and no participant was counted twice.

b.
Both COVID-19 test result (positive/negative) and influenza vaccine (yes/no) are categorical (nominal-level data).

c.
For each variable, the categories are mutually exclusive and exhaustive. It was not possible for a participant to belong to both groups, and the two categories (COVID-19 positive and negative tests) included all study participants.

2.
The null hypothesis is: There is no difference between persons who tested negative versus those who tested positive for COVID-19 on history of a recent influenza vaccine. The null hypothesis is rejected. The critical chi-square value for 1 df at alpha (α) = 0.05 is 3.84 (see Appendix D , which includes the critical values for the chi-square distribution). Our obtained chi-square is 11.18, exceeding the critical value in the table. Moreover, the SPSS reported the exact p value as <0.001. This value can be found in the “Chi-Square Tests” table in the SPSS output. This p value is less than α = 0.05, indicating a significant result.

3.
The exact likelihood of obtaining a chi-square value at least as extreme as or close to the one that was actually observed, assuming that the null hypothesis is true, is less than 0.10%. This value can be found in the “Chi-Square Tests” table in the SPSS output, where the exact p value is reported as “<.001.” The value is calculated as follows: 0.001 × 100% = <0.10%.

4.
The percentage of people who tested positive for COVID-19 among those who received a recent influenza vaccine is calculated as 525 ÷ 12,997 = 0.0404 × 100% = 4.04%.

5.
The percentage of people who tested negative for COVID-19 among those who received a recent influenza vaccine is calculated as 12,472 ÷ 12,997 = 0.9596 × 100% = 95.96%.

6.
The percentage of people who tested positive for COVID-19 among those who did not receive a recent influenza vaccine is calculated as 693 ÷ 14,204 = 0.0488 × 100% = 4.88%.

7.
The percentage of people who tested negative for COVID-19 among those who did not receive a recent influenza vaccine is calculated as 13,511 ÷ 14,204 = 0.9512 × 100% = 95.12%.

8.
The study design in the example was a retrospective cohort design ( Gliner et al., 2017 ; Gray & Grove, 2021 ). Both of the variables (COVID-19 test result and influenza vaccination) were nominal (yes/no). Therefore the design was appropriate for a Pearson chi-square analysis.

9.
Switching the variables in the SPSS “Crosstabs” window would have resulted in the exact same chi-square result. It does not matter which variable is placed in the column section and which is placed in the row section.

10.
The sample size is N = 27,201, which is extremely large, and the vast majority of the statistical results were significant, indicating adequate statistical power (see Exercises 24 and 25 ; Aberson, 2019 ; Cohen, 1988 ).

Data for additional computational practice
This example uses additional data from Conlon and colleagues (2021) , who conducted a retrospective cohort study to compare patients who tested positive with patients who tested negative for COVID-19 on key clinical and demographic variables. In this example, persons who tested positive versus negative for COVID-19 were compared on the presence (rate) of diabetes. The null hypothesis is: There is no difference between persons who tested negative versus positive for COVID-19 on the presence of diabetes. These data are presented in Table 37.2 as a contingency table.

View full size
TABLE 37.2

COVID-19 TEST RESULTS BY PRESENCE OF DIABETES

COVID–19 Positive ( n = 1,218)	COVID–19 Negative ( n = 25,983)	Totals	
Diabetes	262	2,556	2,818	
No diabetes	956	23,427	24,383	
Totals	1,218	25,983	27,201	←︎ Total N
COVID-19, novel coronavirus of 2019.

EXERCISE 37
Questions for additional study

Name: ________________________________________ Class:____________________

Date: __________________________________________________________________

Answer the following questions with hand calculations using the data presented in Table 37.2 or the SPSS dataset called “Exercise 37 Example 2.sav” available on the Evolve website. Follow your instructor’s directions to submit your answers to the following questions for additional study. Your instructor may ask you to write your answers below and submit them as a hard copy for evaluation. Alternatively, your instructor may ask you to submit your answers online.

1.
Calculate t
