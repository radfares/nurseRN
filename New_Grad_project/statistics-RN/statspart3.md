Handling missing data EPUB version of this book
Susan K. Grove, PhD, RN, ANP-BC, GNP-BC; Daisha J. Cipher, PhD

Statistics for Nursing Research, EXERCISE 26, 308-325

Handling missing values within a dataset is important for all statistical analyses. Missing data can occur when participants are lost to follow-up; where there is a failure of instrumentation, mistakes, and/or omissions by the researcher; refusal of response; and many other possible reasons. Assessment of the missing data problem begins with knowing the extent, pattern, and reasons for the missing data ( Little & Rubin, 1987 ). Improper handling of missing values will distort the statistical analyses because, until proven otherwise, the researcher must assume that missing cases differ in important ways from the cases where values are present. Although the extent of missing data (the degree or scope of missing values in a dataset) is important, the current consensus among experts is that the pattern of the missingness is much more of an issue than the extent of the missingness ( Cheema, 2014 ). A clear pattern of missing data is an indicator that the remaining dataset is biased in some way ( Little & Rubin, 1987 ; Tabachnick & Fidell, 2019 ).

Patterns of the missing data
The pattern of missing data refers to whether the data are missing because of random chance or because of a particular reason. The ability to identify whether the data are missing randomly will inform the researcher on how to remedy the missing data problem.

Random patterns of missing data
A random pattern of missing data occurs when the data are randomly missing throughout the dataset, with no apparent explanation or pattern. The chance of a missing value occurring would be likened to a flip of a coin. Missing data that are scattered randomly throughout the dataset pose the least threat to internal and external validity of the analyses ( Gray & Grove, 2021 ; Little & Rubin, 1987 ; Tabachnick & Fidell, 2019 ).

Data are considered to be missing at random (either completely or partially) if the missing data are unrelated to the study variables. The assumption that the data are missing completely at random (MCAR) can be tested with the Little test, a type of chi-square statistic that tests a quantitative dataset against the assumption of MCAR ( Little, 1988 ). If the Little test is nonsignificant at alpha > 0.05, then the researcher can proceed with missing data imputation (summarized later in this exercise) with the least probable effect on internal and external validity of the analyses ( Little, 1988 ; Little & Rubin, 1987 ).

Nonrandom patterns of missing data
Nonrandom missing data occur when values are missing with an obvious pattern in the dataset. Nonrandom patterns can exist along a continuum from a partial, fragmented pattern to a pervasive, predictable pattern of missingness. The assessment of this continuum should be conducted with statistical software. These nonrandom patterns, when not addressed in the analyses, can distort the internal and external validity of the findings ( Kim et al., 2022 ; Tabachnick & Fidell, 2019 ). Table 26.1 displays an example of a nonrandom pattern of missing data. Using an example from a study by Cipher and Urban (2022) , survey data were collected from recently discontinued nursing students. Among the study variables were gender and ratings of hopefulness. Among these hypothetical data, note that the hopefulness variable consists of missing values for the females, but not the males. In contrast, Table 26.2 displays an example of a random pattern of missing data. The hopefulness variable in Table 26.2 consists of values that are missing evenly across both genders. When a nonrandom pattern of missing data is observed, it is highly recommended that the researcher consults with a statistician before performing the planned statistical analyses ( Gray & Grove, 2021 ).

View full size
TABLE 26.1

EXAMPLE OF A NONRANDOM PATTERN OF MISSING DATA

ID	Gender	Hopefulness at Discontinuation, Nonrandom Pattern
1	F	4
2	F	
3	F	1
4	F	
5	F	
6	F	5
7	F	2
8	F	
9	F	
10	F	3
11	M	3
12	M	3
13	M	4
14	M	3
15	M	1
16	M	4
17	M	3
18	M	2
19	M	3
20	M	4
F, female; M, male.

View full size
TABLE 26.2

EXAMPLE OF A RANDOM PATTERN OF MISSING DATA

ID	Gender	Hopefulness with Randomly Missing Data
1	F	4
2	F	2
3	F	
4	F	3
5	F	
6	F	5
7	F	2
8	F	5
9	F	2
10	F	3
11	M	3
12	M	3
13	M	
14	M	3
15	M	1
16	M	
17	M	3
18	M	2
19	M	
20	M	4
F, female; M, male.

Imputation methods
The term imputation in research refers to the process of estimating missing data values and inserting those estimations into a dataset where the missing values are located ( Little & Rubin, 1987 ). There are several approaches to imputing missing data, and each has advantages and disadvantages. This exercise will not provide a comprehensive review, but for those who are interested in the theoretical underpinnings of each approach, including mathematical explanations, the seminal text on missing data imputation is Little and Rubin (1987).

Missing data are generally imputed for quantitative variables (ordinal/interval/ratio), not categorical (nominal) variables. The approach implemented to address missing data depends on (1) the extent (degree or scope) of the missing data and (2) the randomness of the missing data. Generally, when less than 5% of the data in a dataset are missing, the missing data procedures described as follows yield similar results ( Tabachnick & Fidell, 2019 ). There are many different methods of handling missing data, each of which can have substantially different effects on estimation ( Cheema, 2014 ). For this reason, it is important to consult with a statistician to obtain assistance with missing data estimations.

Listwise and pairwise deletion
Listwise deletion of missing values refers to deleting an entire case (one participant’s data) when one or more data point(s) for that case is(are) missing. The subsequent analysis is performed only on complete sets of data. Pairwise deletion of missing values refers to the partial use of a participant’s data. The statistical procedure would include the participant’s data only for the variables that are nonmissing. Deletion methods of handling missing data can be problematic when statistical power is at risk, because deleting cases can make a small sample even smaller ( Little & Rubin, 1987 ). Recall from Exercises 24 and 25 that a small sample size is a detriment to statistical power.

Mean and median replacement
A frequently applied imputation approach is estimating the missing values using the means or medians of a particular variable. For example, if a participant is missing a value for a variable representing a pain visual analog score, the mean pain score can be calculated from the nonmissing values and inserted into the participant’s missing cell. Likewise, a median approach can be implemented whereby the median pain score can be calculated from the nonmissing values and inserted into the participant’s missing cell. The main disadvantage to imputing missing data with means or medians is that the variance of the imputed variable is artificially lowered and consequently, this will affect the results of subsequent inferential statistics ( Tabachnick & Fidell, 2019 ).

One method to increase the accuracy of imputation with means or medians is to estimate missing data within subgroups wherever possible. For example, if a researcher plans to analyze the data in Table 26.2 by comparing males versus females on hopefulness ratings, it is advisable to impute missing data within each gender subgroup. Table 26.3 displays the missing data imputed regardless of gender, followed by imputation by the gender subgroups using the mean replacement method. Note that the first mean replacement method imputes the value of 3 into all missing cells, whereas the second mean replacement method imputes different values based on whether the participant is a female or male. The mean hopefulness rating for the females is 3.25, and the mean hopefulness rating for the males is 2.71. Therefore we can observe that any subsequent inferential statistics computed on the newly imputed data (such as an independent samples t -test) would differ depending on which mean replacement method were used.

View full size
TABLE 26.3

EXAMPLE OF A MEAN REPLACEMENT METHOD FOR MISSING DATA

ID	Gender	Hopefulness with Randomly Missing Data	Mean Replacement, Whole Sample	Mean Replacement by Gender Group
1	F	4	4	4
2	F	2	2	2
3	F		3	3.25
4	F	3	3	3
5	F		3	3.25
6	F	5	5	5
7	F	2	2	2
8	F	5	5	5
9	F	2	2	2
10	F	3	3	3
11	M	3	3	3
12	M	3	3	3
13	M		3	2.71
14	M	3	3	3
15	M	1	1	1
16	M		3	2.71
17	M	3	3	3
18	M	2	2	2
19	M		3	2.71
20	M	4	4	4
F, female; M, male.

Regression
Multiple regression may be used for data imputation by using nonmissing data to predict the values of missing data. The regression method has similar disadvantages as the mean replacement method, in that all of the cases with the same values on the independent variables will be imputed with the same value on the missing variable. As with the mean replacement method, imputation with multiple regression results in the variance of the imputed variable being artificially lower, and consequently, this will affect the results of subsequent inferential statistics. Moreover, the regression method can be a disadvantage if the variables being used as the predictors in the imputation have a low or no association with the variable(s) with the missing data ( Tabachnick & Fidell, 2019 ).

Expectation maximization
The expectation maximization (EM) method is a two-step iterative process that begins with correlations among the variables in the dataset. The EM method subsequently uses a type of regression called maximum likelihood estimation to iteratively fill in missing values and adjusts the imputed values to ensure that realistic estimates of variance are obtained ( Little & Rubin, 1987 ; Tabachnick & Fidell, 2019 ). Thus the EM method is an improvement over the mean replacement and regression methods by ensuring that variances are not artificially lowered during the imputation process ( Cheema, 2014 ).

Multiple imputation
Multiple imputation (MI) is a method of generating multiple simulated values for each missing value, then iteratively analyzing datasets with each simulated value substituted in turn. The purpose of MI is to generate estimates that better reflect true variability and uncertainty in the data than those of other imputation methods ( Cheema, 2014 ). The MI method involves the creation of more than one newly imputed dataset (typically, five datasets are created by the researcher). Statistical software is used to subsequently compute the planned inferential statistic(s) on each of the new datasets and combines the results, yielding a composite as the final estimate. Like the EM method, the MI method ensures that realistic estimates of variance are obtained ( Little & Rubin, 1987 ; Tabachnick & Fidell, 2019 ).

In general, the consensus among statisticians is that among all available missing data imputation methods, the two best approaches are EM and MI ( Cheema, 2014 ). Both approaches ensure that realistic estimates of variance are obtained ( Little & Rubin, 1987 ; Tabachnick & Fidell, 2019 ). The EM method creates one newly imputed dataset, while the MI method creates multiple datasets. Therefore the MI method is a more complicated process, because multiple analyses are conducted that may yield different results, and it is the responsibility of the researcher to collate and report the composite findings.

SPSS computation
A cross-sectional survey study investigated the attitudes and future plans among registered nurse–to–bachelor of science in nursing (RN-to-BSN) students who had recently discontinued their program ( Cipher & Urban, 2022 ). Age at program enrollment, recent grade point average (GPA), and feelings of stress and hopefulness were among the study variables examined. The study variables of stress at discontinuation and of hopefulness at discontinuation were single items that were assessed on a 5-point Likert scale. Higher values of the stress variable are indicative of higher self-reported stress levels, and higher values of the hopefulness variable are indicative of higher self-reported levels of hopefulness. A simulated subset of the study data is presented in Table 26.4 .

View full size
TABLE 26.4

AGE, GPA, AND FEELINGS OF STRESS AND HOPEFULNESS AMONG FORMER RN-TO-BSN STUDENTS

ID	Age at Enrollment	GPA at Discontinuation	Stress at Discontinuation	Hopefulness at Discontinuation
1	27	4.00	3	
2	25	4.00	2	2
3	29	1.49	5	1
4	29			3
5	28	4.00	1	3
6	30	3.00	5	5
7	32	2.34	5	2
8	37			5
9	28	3.90	4	2
10	40	2.67	5	
11	33	3.00	2	3
12	34	4.00	4	3
13	38	3.14	4	4
14	41			3
15	43	3.75	4	1
16	48	3.79	3	
17	39	1.80	5	3
18	49	4.00	3	
19	62	2.14	2	3
20	68	4.00	3	4
GPA, grade point average.

This is how our dataset looks in SPSS.


A screenshot of S P S S data view table with variables I D, Age, G P A, Stress, and Impact. The screenshot shows the S P S S Data View window displaying a data table with five labeled variables, I D, Age, G P A, Stress, and Impact. The table contains 15 rows representing individual data entries. I D ranges from 1 to 15. Age values range from 21 to 43. G P A includes values such as 4.00, 3.76, 3.00, and 1.00. Stress and Impact are listed as whole numbers from 1 to 9. The toolbar at the top shows standard S P S S options such as File, Edit, View, Data, Transform, Analyze, Graphs, Utilities, Extensions, Windows, and Help. Icons for data management and analysis tools are also visible. The view is set to Data View as indicated by the tab at the bottom left.
Step 1: From the “Analyze” menu, choose “Missing Value Analysis.” Move the four study variables over to the right. Check “EM.”


A screenshot of S P S S data view table with variables I D, Age, G P A, Stress, and Impact. The screenshot shows the S P S S Data View window displaying a data table with five labeled variables, I D, Age, G P A, Stress, and Impact. The table contains 15 rows representing individual data entries. I D ranges from 1 to 15. Age values range from 21 to 43. G P A includes values such as 4.00, 3.76, 3.00, and 1.00. Stress and Impact are listed as whole numbers from 1 to 9. The toolbar at the top shows standard S P S S options such as File, Edit, View, Data, Transform, Analyze, Graphs, Utilities, Extensions, Windows, and Help. Icons for data management and analysis tools are also visible. The view is set to Data View as indicated by the tab at the bottom left.
Step 2: Click “Patterns.” Check “Tabulated cases, grouped by missing values.” Click “Continue.”


A screenshot shows the Missing Value Analysis Patterns window in SPSS. The screenshot shows the Missing Value Analysis Patterns window in S P S S. In the Display section, Tabulated cases grouped by missing value patterns is selected. Omit patterns with less than 1 percent of cases is enabled with the value set to 1. Sort variables by missing value pattern is also selected. The options Cases with missing values sorted by missing value patterns and All cases optionally sorted by selected variable are not selected. In the Variables section, the box under Missing Patterns for includes Age, GPA, Stress, and Hopeful. The box for Additional Information for is empty. The field labeled Sort by is blank and the Sort Order is set to Ascending. At the bottom, the buttons Continue, Cancel, and Help are shown.
Step 3: Click “Descriptives.” Check “Univariate Statistics” and “ t tests with groups formed by indicator variables.” Click “Continue” and then “OK.”


A dialog box shows Missing Value Analysis in SPSS with variables and estimation method options. The dialog box titled Missing Value Analysis Descriptives displays several options. The Univariate statistics checkbox is selected. Under Indicator Variable Statistics, the t tests with groups formed by indicator variables option is also selected, while other checkboxes such as Percent mismatch, Sort by missing value patterns, Include probabilities in table, and Crosstabulations of categorical and indicator variables remain unselected. At the bottom, there is a setting labeled Omit variables missing less than with a value of 5 percent. Below the settings are three buttons labeled Continue, Cancel, and Help.
Interpretation of SPSS output
The following tables are generated from SPSS. The first table contains descriptive statistics of the four study variables, along with information about the extent to which each variable contains missing data. Note that in the row labeled “Age,” the last column notes that there is one extreme value, and this value is high, not low. When looking at the actual dataset, that outlier is the value of 68. The variable of age is also the only variable in the dataset to have no missing values. The extent of missing data can be calculated by adding the values in the column in the table labeled “Count” and dividing by the total possible values: (0 + 3 + 3 + 4) ÷ 80 = 0.125 × 100% = 12.5%. Thus 12.5% of the data in this dataset are missing.


A table presents univariate statistics for age, grade point average, stress, and hostility including mean, standard deviation, missing values, and outlier counts. The table titled Univariate Statistics presents data for four variables, age, grade point average, stress, and hostility. It includes columns for number of cases, mean, standard deviation, count and percent of missing values, and number of outliers at low and high ends. For age, the number of cases is 20, mean is 38, standard deviation is 11.553, with 3 missing cases accounting for 15 percent, and one outlier on the high end. Grade point average has 17 cases, a mean of 3.3256, standard deviation of 0.660, 5 missing cases forming 23 percent, and 2 high outliers. Stress data includes 17 cases, mean of 3.53, standard deviation of 1.581, 5 missing cases forming 23 percent, and no outliers. Hostility data includes 16 cases, mean of 2.94, standard deviation of 1.611, 6 missing cases forming 27 percent, and no outliers. A note under the table states that the number of outliers is based on values outside the range of first quartile minus 1.5 times the interquartile range or third quartile plus 1.5 times the interquartile range.
The next two tables contain means and standard deviations for each study variable. The first row, labeled “All Values,” displays the means and standard deviations as computed in the dataset, excluding the missing values. The second row, labeled “EM,” displays the means and standard deviations if the EM method were used to impute all of the missing values ( IBM Corporation, 2022 ).


A table presents estimated means for age, grade point average, stress, and hopeful across all values and estimated mean categories. The table titled Summary of Estimated Means presents values for age grade point average stress and hopeful. The row labeled All Values shows thirty eight for age three point two three six five for grade point average three point five three for stress and two point nine four for hopeful. The row labeled Estimated Means shows thirty eight for age three point two five three one for grade point average three point five three for stress and two point nine eight for hopeful.

A table presents standard deviations for age, grade point average, stress, and hopeful for all values and expectation maximization. The table titled Summary of Estimated Standard Deviations presents values for age, grade point average, stress, and hopeful. The row labeled All Values shows eleven point five three nine for age, zero point eight six eight six four for grade point average, one point two eight one for stress, and one point one eight one for hopeful. The row labeled Expectation Maximization shows eleven point five three nine for age, zero point eight six eight nine eight for grade point average, one point two seven nine for stress, and one point one seven nine for hopeful.
The next table, titled “Separate Variance t Tests,” displays independent samples t -test results with missingness as the independent variable (missing versus present) and the study variable as the dependent variable. Note the first column for “Age” and the results for “Hopefulness.” The mean age for participants that had nonmissing (present) values for hopefulness is 37.25, while the mean age for participants that had missing values for hopefulness is 41.00. If the t -test were significant, it would indicate a pattern of missing data whereby older participants were less likely to provide hopefulness ratings than younger participants. However, the t value is −0.60, which is not significant, indicating no pattern of missingness between age and hopefulness ratings.


A table shows separate variance t tests comparing age, grade point average, stress, and hostility across present and missing values for GPA, stress, and hostility. The table titled Separate Variance t Tests presents comparisons of means for age, grade point average, stress, and hostility across groups based on the presence or absence of data for grade point average, stress, and hostility. For grade point average, the mean age for the present group is 35.41 and for the missing group is 39.67. The t value is minus 0.93 and the significance value is 0.36. For stress, the mean age for the present group is 35.41 and for the missing group is 39.67, with a t value of minus 0.93 and significance value of 0.36. For hostility, the mean age for the present group is 37.25 and for the missing group is 43.17, with a t value of minus 1.22 and significance value of 0.24. Grade point average, stress, and hostility are each compared between groups where values are present or missing, and corresponding mean scores are shown for all variables. A note below the table indicates that t tests are used to compare means of groups defined by indicator variables for present or missing data, and variables with over 25 percent missing are not displayed.
The table titled “Tabulated Patterns” displays an “X” where there is a possibility of missing data patterns. The column for “Age” is blank, indicating that the variable of age contains no missing data. The second and third columns for “GPA” and “Stress,” respectively, displays an “X” together on the same row, indicating that there are three instances where three participants were missing pairs of GPA and stress values. There were 13 participants who had complete sets of data, with no missing values for any variable.


A table shows missing data patterns across age, grade point average, stress, and hopeful, with the number of cases and complete cases per pattern. The table titled Tabulated Patterns presents missing data patterns for four variables, age, grade point average, stress, and hopeful. The first column lists the number of cases corresponding to each missing data pattern. In the first row, 13 cases have no missing data. In the second row, 4 cases have hopeful marked as missing, indicated by X. In the third row, 3 cases have both grade point average and stress marked as missing, indicated by X. The final column labeled Complete if shows the number of complete cases if variables marked with X in that pattern are excluded. These values are 13, 17, and 16 respectively. A footnote indicates that variables are sorted based on missing patterns, and that the number of complete cases reflects values if variables with missing data are not used.
The table titled “EM Means” contains the same information provided in the earlier tables by displaying the means of the study variables if the EM method were used to impute all of the missing values. The new piece of information is found in the footnote below the table: Little’s MCAR test. Little’s test is reported as a type of chi-square test, with an exact p value of 0.652. This statistic tests the assumption that the data are missing completely at random ( Little, 1988 ). If the result is not significant, then the researcher can assume that the data are missing completely at random and the researcher can proceed with missing data imputation with the least probable effect on internal and external validity of the analyses ( Gray & Grove, 2021 ; Shadish et al., 2002 ). If the result is significant, then the researcher can assume that there is evidence of nonrandom patterns of missing data ( Little, 1988 ). In this example, Little’s test is not significant, suggesting that the data are missing completely at random, and that any possible patterns of missing data that exist in the dataset are too small and not meaningful enough to be detected by Little’s statistic ( Little, 1988 ).


A table shows expectation maximization means for age, grade point average, stress, and hopeful, along with Little's test results. The table titled E M Estimated Statistics presents expectation maximization means for four variables, age, grade point average, stress, and hopeful. The mean values are as follows, age is 38, grade point average is 3.2531, stress is 3.53, and hopeful is 2.98. A note below the table provides results from Little's Missing Completely at Random test, with chi square equal to 3.313, degrees of freedom equal to 5, and significance value equal to 0.652.
Study questions

1.
Provide one possible cause or reason for missing data in a dataset.

2.
What is meant by the extent of missing data? Define and give an example.

3.
What is meant by the pattern of missing data? Define and give an example.

4.
Which is the most important component of assessing missing data: the extent of the missingness or the pattern of the missingness? Provide a rationale for your response and include documentation.

5.
What does a significant Little’s test indicate?

6.
Name one disadvantage of using the mean replacement method for missing data imputation.

7.
In the example data, calculate the extent of missing data for the variable of stress. Show your work.

8.
In the example data, calculate the extent of missing data for the variable of hopefulness. Show your work.

9.
In the example data, does there appear to be a pattern of missing data for GPA? Provide a rationale for your response.

10.
In the SPSS output tabled titled “Separate Variance t Tests,” the mean stress rating for participants that had nonmissing (i.e., present) values for the variable of hopefulness is 3.54. What is the mean stress rating for participants that had missing values for hopefulness? Is there a disparity between the two means?

Answers to study questions

1.
No follow-up of study participants is a common cause of missing data. Other reasons include failure of instrumentation, mistakes and/or omissions by the researcher, and refusal of response ( Tabachnick & Fidell, 2019 ).

2.
The extent of missing data refers to the amount of data missing in a dataset. For example, in a hypothetical dataset with 10 participants and two study variables (for a total of 20 potential values), if one value is missing from the first variable, and two values missing from the second variable, the extent of missing data is calculated as: (1 + 2) ÷ 20 = 0.15 × 100% = 15.0%.

3.
The pattern of missing data refers to whether the data are missing because of random chance or because of a particular reason. One example of data that have a nonrandom pattern would be the presence of missing income for study participants who are retired, but no missing income data for those who are currently employed. This pattern would suggest that the retired participants were less likely to divulge their income than the employed participants. One reason might be that the participants might have no income related to a job, so they left this item blank.

4.
The pattern of the missing data is the most important component of assessing missing data. A clear pattern of missing data is an indicator that the remaining dataset is biased in some way ( Little & Rubin, 1987 ; Tabachnick & Fidell, 2019 ). The ability to identify whether the data are missing randomly will inform the researcher on how to remedy the missing data problem.

5.
A significant Little’s test indicates that there is evidence of nonrandom patterns of missing data (Little, 1988). This finding implies a more complicated approach to the imputation process because a nonrandom pattern of missing data is an indicator that the remaining dataset is biased in some way ( Little & Rubin, 1987 ; Tabachnick & Fidell, 2019 ).

6.
The main disadvantage of imputing missing data with means or medians is that the variance of the imputed variable is lowered and, consequently, this will affect the results of subsequent inferential statistics ( Tabachnick & Fidell, 2019 ).

7.
The extent of missing data for the variable of stress is calculated as: (3 ÷ 20) × 100% = 0.15 × 100% = 15.0%.

8.
The extent of missing data for the variable of hopefulness is calculated as: (4 ÷ 20) × 100% = 0.20 × 100% = 20.0%.

9.
Yes, there appears to be a pattern of missing data for GPA. Upon visual inspection of the raw data, it appears that with every missing value for GPA, there is also a missing value for stress. Moreover, in the SPSS output tabled titled “Tabulated Patterns,” the columns for GPA and stress display an “X” together on the same rows, indicating that there are three instances where three participants were missing pairs of GPA and stress values. There are zero instances where there is a missing value for GPA but not for stress, and vice versa.

10.
The mean stress rating for participants that had missing values for the variable of hopefulness is 3.50. No, there is no notable disparity between the stress ratings for participants with present and missing hopefulness data because the difference between 3.50 and 3.54 is clinically insignificant ( Gray & Grove, 2021 ).

Data for additional computational practice
The following questions for additional study refer to the same example from Cipher and Urban (2022) . The data are presented in Table 26.4 .

EXERCISE 26
Questions for additional study

Name: _____________________________________________________ Class: _______________________

Date: ___________________________________________________________________________________

Answer the following questions with hand calculations using the data presented in Table 26.4 or the SPSS dataset called “Exercise 26 Example” available on the Evolve website. Follow your instructor’s directions to submit your answers to the following questions for additional study. Your instructor may ask you to write your answers below and submit them as a hard copy for evaluation. Alternatively, your instructor may ask you to submit your answers online.

1.
In the example data, calculate the extent of missing data for grade point average (GPA). Show your work.

2.
In the SPSS output table titled “Tabulated Data,” the column titled “Complete if...” lists 13 “complete cases.” Explain the meaning of this number.

3.
In a hypothetical dataset, a Little’s MCAR test is computed. The results are χ²(2) = 8.83, p = 0.02. How woul

Determining the normality of a distribution EPUB version of this book
Susan K. Grove, PhD, RN, ANP-BC, GNP-BC; Daisha J. Cipher, PhD

Statistics for Nursing Research, EXERCISE 27, 326-345

Most parametric statistics require that the variables being studied are normally distributed. The normal curve has a symmetric or equal distribution of scores around the mean with a small number of outliers in the two tails. The first step to determining normality is to create a frequency distribution of the variable(s) being studied. A frequency distribution can be displayed in a table or figure. A line graph figure can be created whereby the x axis consists of the possible values of that variable, and the y axis is the tally of each value. The frequency distributions presented in this exercise focus on values of continuous variables. With a continuous variable, higher numbers represent more of that variable and the lower numbers represent less of that variable, or vice versa. Common examples of continuous variables are age, income, blood pressure, weight, height, pain levels, and health status (see Exercise 1 ; Grove & Gray, 2023 ; Waltz et al., 2017 ).

The frequency distribution of a variable can be presented in a frequency table, which is a way of organizing the data by listing every possible value in the first column of numbers, and the frequency (tally) of each value as the second column of numbers. For example, consider the following hypothetical age data for patients from a primary care clinic. The ages of 20 patients were: 45, 26, 59, 51, 42, 28, 26, 32, 31, 55, 43, 47, 67, 39, 52, 48, 36, 42, 61, and 57.

First, we must sort the patients’ ages from lowest to highest values:

View full size
26
26
28
31
32
36
39
42
42
43
45
47
48
51
52
55
57
59
61
67
Next, each age value is tallied to create the frequency. This is an example of an ungrouped frequency distribution. In an ungrouped frequency distribution , researchers list all categories of the variable on which they have data and tally each datum on the listing ( Grove & Gray, 2023 ). In this example, all the different ages of the 20 patients are listed and then tallied for each age.

View full size
Age	Frequency
26	2
28	1
31	1
32	1
36	1
39	1
42	2
43	1
45	1
47	1
48	1
51	1
52	1
55	1
57	1
59	1
61	1
67	1
Because most of the ages in this dataset have frequencies of “1,” it is better to group the ages into ranges of values. These ranges must be mutually exclusive (i.e., a patient’s age can only be classified into one of the ranges). In addition, the ranges must be exhaustive, meaning that each patient’s age will fit into at least one of the categories ( Exercise 1 ). For example, we may choose to have ranges of 10, so that the age ranges are 20 to 29, 30 to 39, 40 to 49, 50 to 59, and 60 to 69. We may choose to have ranges of 5, so that the age ranges are 20 to 24, 25 to 29, 30 to 34, etc. The grouping should be devised to provide the greatest possible meaning to the purpose of the study. If the data are to be compared with data in other studies, groupings should be similar to those of other studies in this field of research. Classifying data into groups results in the development of a grouped frequency distribution . Table 27.1 presents a grouped frequency distribution of patient ages classified by ranges of 10 years. Note that the range starts at “20” because there are no patient ages lower than 20, nor are there ages higher than 69.

View full size
TABLE 27.1

GROUPED FREQUENCY DISTRIBUTION OF PATIENT AGES WITH PERCENTAGES

Adult Age Range	Frequency ( f )	Percentage (%)	Cumulative Percentage
20–29	3	15%	15%
30–39	4	20%	35%
40–49	6	30%	65%
50–59	5	25%	90%
60–69	2	10%	100%
Total	20	100%	
Table 27.1 also includes percentages of patients with an age in each range; the cumulative percentages for the sample should add up to 100%. This table provides an example of a percentage distribution that indicates the percentage of the sample with scores falling into a specific group. Percentage distributions are particularly useful in comparing this study’s data with results from other studies.

As discussed earlier, frequency distributions can be presented in figures. The common figures used to present frequencies include graphs, charts, histograms, and frequency polygons ( Gray & Grove, 2021 ). Fig. 27.1 is a line graph of the frequency distribution for age ranges, where the x axis represents the different age ranges and the y axis represents the frequencies (tallies) of patients with ages in each of the ranges.

A line graph displays the frequency of individuals across age ranges from 20 to 29 to 60 to 69. The line graph plots frequency on the vertical axis, which ranges from 0 to 7, against age range on the horizontal axis with categories 20 to 29, 30 to 39, 40 to 49, 50 to 59, and 60 to 69. The line starts at a frequency of 0 for 20 to 29, rises to 3 for 30 to 39, 4 for 40 to 49, peaks at 6 for 50 to 59, then drops to 5 for 60 to 69 and returns to 0 beyond that range.
FIG. 27.1 ■
FREQUENCY DISTRIBUTION OF PATIENT AGE RANGES.

The normal curve
The theoretical normal curve is an expression of statistical theory. It is a theoretical frequency distribution of all possible scores ( Fig. 27.2 ). However, no real distribution exactly fits the normal curve. This theoretical normal curve is symmetric, unimodal, and has continuous values. The mean, median, and mode are equal in a normal curve (see Fig. 27.2 ). The distribution is completely defined by the mean and standard deviation ( s ), which are calculated and discussed in Exercises 8 , 9 and 28 .

A bell shaped graph shows a normal distribution curve with labeled percentages across standard deviations with increasing values. The bell shaped graph displays a normal distribution curve centered on the mean. The horizontal axis is labeled with standard deviations as minus 2 s, minus 1 s, mean, plus 1 s, and plus 2 s. Vertical lines divide the curve into segments. The labeled percentages for each section are 2.28 percent in each tail beyond minus 2 s and plus 2 s, 13.59 percent between minus 2 s and minus 1 s, 34.13 percent between minus 1 s and the mean, 34.13 percent between the mean and plus 1 s, and 13.59 percent between plus 1 s and plus 2 s. Two arrows on the left and right sides point directly to the values.
FIG. 27.2 ■
THE NORMAL CURVE.

Skewness
Any frequency distribution that is not symmetric is referred to as skewed or asymmetric ( Holmes, 2018 ). Skewness may be exhibited in the curve in a variety of ways. A distribution may be positively skewed , which means that the largest portion of data is below the mean. For example, data on length of enrollment in hospice are positively skewed because most of the people die within the first 3 weeks of enrollment, whereas increasingly smaller numbers of people survive as time increases. A distribution can also be negatively skewed , which means that the largest portion of data is above the mean ( Terrell, 2021 ). For example, data on the occurrence of chronic illness in an older age group are negatively skewed, because more chronic illnesses occur in seniors. Fig. 27.3 includes both a positively skewed distribution and a negatively skewed distribution ( Gray & Grove, 2021 ).

Two curved graphs show positively and negatively skewed distribution curves with labeled mode, median, and mean at the curved areas. The two curved graphs display two distribution curves side by side. Below the left visual curve is labeled positively skewed and shows a curve where the mode is at the peak, the median is positioned to the right of the mode, and the mean is further to the right in the curved area, which indicates a long tail, that extends towards higher values. The right visual is labeled negatively skewed and shows a curve where the mode is at the peak, the median is positioned to the left of the mode, and the mean is further to the left, which indicates a long tail, which extends towards lower values.
FIG. 27.3 ■
EXAMPLES OF POSITIVELY AND NEGATIVELY SKEWED DISTRIBUTIONS.

In a skewed distribution, the mean, median, and mode are not equal. Skewness interferes with the validity of many statistical analyses; therefore statistical procedures have been developed to measure the skewness of the distribution of the sample being studied. Few samples will be perfectly symmetric; however, as the deviation from symmetry increases, the seriousness of the effect on statistical analysis increases. In a positively skewed distribution, the mean is greater than the median, which is greater than the mode. In a negatively skewed distribution, the mean is less than the median, which is less than the mode (see Fig. 27.3 ; Terrell, 2021 ). The effects of skewness on the types of statistical analyses conducted in a study are discussed later in this exercise.

Kurtosis
Another term used to describe the shape of the distribution curve is kurtosis. Kurtosis explains the degree of peakedness of the frequency distribution, which is related to the spread or variance of scores. An extremely peaked distribution is referred to as leptokurtic , an intermediate degree of kurtosis as mesokurtic , and a relatively flat distribution as platykurtic (see Fig. 27.4 ; Terrell, 2021 ). Extreme kurtosis can affect the validity of statistical analysis because the scores have little variation. Many computer programs analyze kurtosis before conducting statistical analyses. A kurtosis of zero indicates that the curve is mesokurtic, kurtosis values above zero indicate that the curve is leptokurtic, and values below zero that are negative indicate a platykurtic curve ( Gray & Grove, 2021 ; Holmes, 2018 ).

Three visuals show bell shaped curves labeled leptokurtic, mesokurtic, and platykurtic to represent different data distributions. The visuals show three bell shaped distribution curves with different shapes and labels. The first visual on the left shows the leptokurtic curve, which is tall and narrow with a sharp peak and thin tails. This suggests that most data values lie close to the mean. The second visual in the center shows the mesokurtic curve, which has moderate height and width and represents a typical normal distribution. The third visual on the right shows the platykurtic curve, which is short and wide with a flat peak and thick tails. This suggests that data values are more spread out from the mean.
FIG. 27.4 ■
EXAMPLES OF KURTOTIC DISTRIBUTIONS.

Tests of normality
Skewness and kurtosis should be assessed prior to statistical analysis, and the importance of such non-normality needs to be determined by both the researcher and the statistician. Skewness and kurtosis statistic values of ≥+1 or ≥−1 are fairly severe and could affect the outcomes from parametric analysis techniques ( Kim et al., 2022 ). Because the severity of the deviation from symmetry compromises the validity of the parametric tests, nonparametric analysis techniques should be computed instead ( Field, 2013 ). Nonparametric statistics have no assumption that the distribution of scores be normally distributed ( Daniel, 2000 ; Pett, 2016 ).

There are statistics that obtain an indication of both the skewness and kurtosis of a given frequency distribution. The Shapiro-Wilk W test is a formal test of normality that assesses whether a variable’s distribution is skewed and/or kurtotic ( Kim et al., 2022 ; Tabachnick & Fidell, 2018 ). Thus this test has the ability to calculate both skewness and kurtosis by comparing the shape of the variable’s frequency distribution to that of a perfect normal curve. For large samples ( n > 2000) the Kolmogorov-Smirnov D test is an alternative test of normality for large samples ( Field, 2013 ; Marsaglia et al., 2003 ).

SPSS computation
A cross-sectional survey study investigated the attitudes and future plans among former registered nurse–to–bachelor of science in nursing (RN-to-BSN) students who had recently discontinued their program ( Cipher & Urban, 2022 ). Age at program enrollment, recent grade point average (GPA), and feelings of stress and hopefulness were among the study variables examined. The study variables of stress at discontinuation and of hopefulness at discontinuation were assessed on a 5-point Likert scale. Higher values of the variable of stress are indicative of higher self-reported stress levels, and higher values of the variable of hopefulness are indicative of higher self-reported levels of hopefulness. A simulated subset of the study data is presented in Table 27.2 .

View full size
TABLE 27.2

AGE, GPA, AND FEELINGS OF STRESS AND HOPEFULNESS AMONG FORMER RN-TO-BSN STUDENTS

ID	Age at Enrollment	GPA at Discontinuation	Stress at Discontinuation	Hopefulness at Discontinuation
1	27	4.00	3	4
2	25	4.00	2	2
3	29	1.49	5	1
4	29	3.10	4	3
5	28	4.00	1	3
6	30	3.00	5	5
7	32	2.34	5	2
8	37	3.85	3	5
9	28	3.90	4	2
10	40	2.67	5	3
11	33	3.00	2	3
12	34	4.00	4	3
13	38	3.14	4	4
14	41	2.90	5	3
15	43	3.75	4	1
16	48	3.79	3	4
17	39	1.80	5	3
18	49	4.00	3	2
19	62	2.14	2	3
20	68	4.00	3	4
GPA, grade point average.

Below is how our dataset looks in SPSS.


A visual shows a Statistical Package for the Social Sciences data view window with columns for identification number, age, grade point average, stress, and hopeful. The visual shows a table of the Statistical Package for the Social Sciences software window in the data view tab. The top menu bar shows options such as File, Edit, View, Data, Transform, Analyze, Graphs, Utilities, Extensions, Window, and Help. Below the menu bar, toolbars show icons for actions such as open file, save, print, undo,o, find, go to case, variables, cases, run descriptive statistics, and transform variables. The central part of the window shows a spreadsheet layout with columns labeled identification number, age, grade point average, stress, and hopeful. 16 rows of numerical data appear in the table. The first row shows identification number 1, age 27, grade point average 4.00, stress 3, and hopeful 4.
Step 1: From the “Analyze” menu, choose “Descriptive Statistics” and “Frequencies.” Move the four study variables over to the right.


A visual shows a Statistical Package for the Social Sciences frequencies dialogue box with options for variable selection and frequency table display. The visual shows the frequencies dialogue box in the Statistical Package for the Social Sciences software. The title bar at the top reads Frequencies with a close button on the right. On the left, a list of available variables appears with the participant identification number labeled as identification number highlighted. In the center, a right arrow button allows selection of variables. On the right, under variables, selected items include age at enrolment labeled as age, grade point average at discontinuation labeled as grade point average, feelings of stress, and feelings of hopefulness. To the right of the variable list are buttons labeled Statistics, Charts, Format, Style, and Bootstrap. At the bottom, two checkboxes are present. The display frequency tables checkbox is checked, and the create American Psychological Association style tables checkbox is unchecked. Below the checkboxes are five command buttons labeled OK, Paste, Reset, Cancel, and Help, which show a Statistical Package for the Social Sciences frequencies dialogue box with options for variable selection and frequency table display.
Step 2: Click “Statistics.” Check “Skewness” and “Kurtosis.” Click “Continue.”


A visual shows the Statistical Package for the Social Sciences frequencies statistics dialogue box with options for percentile values, central tendency, dispersion, and distribution. The visual shows the frequencies statistics dialogue box in the Statistical Package for the Social Sciences software. The title bar at the top reads frequency statistics with a close button on the right. The visual contains four main sections. The percentile values section includes checkboxes for quartiles, cut points for with a text box followed by equal groups, and percentiles with an input field. Below are three buttons labeled add, change, and remove. The central tendency section has checkboxes for mean, median, mode, and sum. The dispersion section includes checkboxes for standard deviation, variance, range, minimum, maximum, and standard error mean. The distribution section includes checkboxes for values that are group midpoints, skewness, and kurtosis. The skewness and kurtosis checkboxes are checked. At the bottom of the dialogue box are three command buttons Continue, Cancel, and Help.
Step 3: Click “Charts.” Check “Histograms.” Click “Continue” and then “OK.”


A visual displays the Statistical Package for the Social Sciences Frequencies Charts dialogue box with options to select chart type, which includes histograms, bar charts, and pie charts. The visual displays the Frequencies Charts dialogue box in the Statistical Package for the Social Sciences software. The title bar shows the text Frequency Charts and a close button. The main section is labeled Chart Type and has four radio buttons arranged vertically, which are None, Bar charts, Pie charts, and Histograms. The Histograms option is selected as shown by a filled circle. Below the Histograms option is an unchecked checkbox labeled Show normal curve on histogram. Below the Chart Type section is another section labeled Chart Values with two radio buttons, which are Frequencies and Percentages. The Frequencies option is selected. At the bottom of the dialogue box are three rectangular buttons labeled Continue, Cancel, and Help.
Interpretation of SPSS output
The following tables are generated from SPSS. The first table contains the skewness and kurtosis statistics for the four variables.

A visual shows a Statistical Package for the Social Sciences. Explore the dialogue box used to select variables for analysis. The visual shows a visual of the Explore dialogue box in the Statistical Package for the Social Sciences software. The dialogue box has a title bar labeled Explore and a close button marked with the letter X in the top right corner. On the left side, there is a list of available variables, with Participant Identification in square brackets. Identification is highlighted. In the center, there are three input fields for assigning variables using right pointing arrow buttons Dependent List, Factor List, and Label Cases by. The Dependent List includes Age at Enrolment and Grade Point Average at Discontinuation. To the right of these lists are four buttons labeled Statistics, Plots, Options, and Bootstrap. At the bottom of the dialogue box, under a section labeled Display, there are three radio buttons. Both, which are selected, Statistics and Plots. Below this section are five command buttons OK, Paste, Reset, Cancel, and Help.
The next four tables contain the frequencies, or tallies, of the variable values. The last four tables contain the frequency distributions of the four variables.


A visual shows a Statistical Package for the Social Sciences Explore Plots dialogue box used to configure plot options. The visual shows a visual of the Explore Plots dialogue box in the Statistical Package for the Social Sciences software. The title bar at the top reads Explore Plots and includes a close button marked with the letter X. The dialogue box is divided into multiple sections. In the Boxplots section, there are three radio buttons labeled Factor levels together, which is selected, Dependents together, and None. The Descriptive section contains two checkboxes labeled Stem and leaf, which is checked, and Histogram, which is unchecked. Below this, there is a checked checkbox labeled Normality plots with tests. In the Spread versus Level with Levene Test section, there are four radio buttons. None, which is selected, power estimation, Transformed with an associated power input box and an out natural logarithm radio button, and untransformed. At the bottom of the dialogue box are three command buttons labeled Continue, Cancel, and Help.
A table presents results of Kolmogorov Smirnov and Shapiro Wilk tests for normality across four variables in the Statistical Package for the Social Sciences. The visual displays a table titled Tests of Normality generated in Statistical Package for the Social Sciences software. The table presents the results of two normality tests Kolmogorov Smirnov and Shapiro Wilk for four variables Age at enrolment, grade point average at discontinuation, feelings of stress at discontinuation, and feelings of hopefulness at discontinuation. For each variable and each test, the table includes three columns labeled Statistic, Degrees of Freedom, and Significance. Under the Kolmogorov Smirnov test, the values are as follows Age at Enrolment has a statistic of 0.147, degrees of freedom of 20, and significance of 0.200 with a footnote labeled a, which indicates Lilliefors Significance Correction. Grade Point Average at Discontinuation has a statistic of 0.233, degrees of freedom of 20, and significance of 0.006. Feelings of stress at discontinuation have a statistic of 0.177, degrees of freedom of 20, and significance of 0.099. Feelings of Hopefulness at Discontinuation has a statistic of 0.200, degrees of freedom of 20, and significance of 0.035. Under the Shapiro Wilk test, the values are Age at Enrolment has a statistic of 0.869, degrees of freedom of 20, and significance of 0.011. Grade Point Average at Discontinuation has a statistic of 0.855, degrees of freedom of 20, and significance of 0.006. Feelings of stress at discontinuation have a statistic of 0.893, degrees of freedom of 20, and significance of 0.030. Feelings of Hopefulness at Discontinuation has a statistic of 0.925, degrees of freedom of 20, and significance of 0.126. A footnote below the table includes two notes an asterisk, which indicates that this is a lower bound of the true significance, and the letter a, referring to the Lilliefors Significance Correction.

A line graph displays data with two distinct peaks and a flat section. The visual shows a line graph with values on the vertical axis, which ranges from 0 to 5, and values on the horizontal axis, which ranges from 0 to 15. In this line graph, one peak, which is on the left, is smaller, and one peak, which is on the right, is bigger. The line starts at 0 on the vertical axis at horizontal value 0, rises to approximately 1.2 at horizontal value 2, and then drops back to 0 at horizontal value 3. The line remains flat at 0 from horizontal value 3 to horizontal value 8. From horizontal value 8, the line rises sharply to a peak of 4 at approximately horizontal value 12 and then decreases to 0 at horizontal value 15.

A line graph displays data with one primary peak and a smaller secondary peak. The line graph shows values on the vertical axis, which have two distinct peaks one is bigger and is a primary peak, and the other is smaller and is a secondary peak, which range from 0 to 6, and values on the horizontal axis, which range from 0 to 15. The line starts at 0 on the vertical axis at horizontal value 0, rises to a primary peak of 5 at approximately horizontal value 3.5, and then decreases to 0 at horizontal value 6. The line remains flat at 0 from horizontal value 6 to horizontal value 9. From horizontal value 9, the line rises to a smaller peak slightly above 1 at approximately horizontal value 11 and then returns to 0 at horizontal value 12.5.
Histogram

A visual shows a table of descriptive statistics for age, grade point average, stress, and hopefulness, which includes skewness and kurtosis values. The visual displays a table from the Statistical Package for the Social Sciences output titled Frequencies with a subsection labeled Statistics. The table presents descriptive statistics for four variables, which are age at enrolment, grade point average at discontinuation, feelings of stress at discontinuation, and feelings of hopefulness at discontinuation. For each variable, the number of valid cases is 20 and the number of missing cases is 0. Skewness values are Age at Enrolment equals 1.348. Grade Point Average at Discontinuation equals negative. 0.798 Feelings of stress at discontinuation equal negative 0.444 Feelings of hopefulness at discontinuation equal 0.000. The standard error of skewness is 0.512 for all variables. Kurtosis values are Age at Enrolment equals 1.552. Grade Point Average at Discontinuation equals negative. 0.488. Feelings of stress at discontinuation equal negative 0.735. Feelings of hopefulness at discontinuation equal negative 0.279 The standard error of kurtosis is 0.992 for all variables.

A frequency table displays the distribution of ages at enrolment. The visual shows a frequency table titled Frequency Table for the variable Age at Enrolment. The table displays discrete age values with their corresponding frequencies, percentages, and cumulative percentages. Age 25 has a frequency of 1, which represents 5.0 percent of the total and a cumulative percentage of 5.0 percent. Age 27 also has a frequency of 1, which makes up 5.0 percent and brings the cumulative percentage to 10.0 percent. Ages 28 and 29 each have a frequency of 2, which accounts for 10.0 percent individually, with cumulative percentages of 20.0 percent and 30.0 percent, respectively. The table continues with frequencies of 1 for ages 30, 32, 33, 34, 37, 38, 39, 40, 41, 43, 48, 49, 62, and 68, in which each contributes 5.0 percent to the total. The cumulative percentages increase gradually and reach 100.0 percent at age 68. The total number of valid cases is 20, which represents 100.0 percent of the data.

A frequency table displays the distribution of grade point average at discontinuation. The visual displays a frequency table titled Grade Point Average at Discontinuation. The table presents various grade point average values along with their corresponding frequencies, percentages, and cumulative percentages. For example, a grade point average of 1.49 has a frequency of 1, which represents 5.0 percent of the total, with a cumulative percentage of 5.0 percent. Grade Point Average values 1.80, 2.14, 2.34, 2.67, 2.90, 3.10, 3.14, 3.75, 3.79, 3.85, and 3.90 each have a frequency of 1, which represents 5.0 percent individually. A grade point average of 3.00 has a frequency of 2, which represents 10.0 percent. The most frequent grade point average is 4.00, with a frequency of 6, which accounts for 30.0 percent of the total. The cumulative percentages increase sequentially reach 100.0 percent for the grade point average of 4.00. The total number of valid cases is 20, which represents 100.0 percent of the data.

A frequency table displays the distribution of feelings of stress at discontinuation. The visual displays a frequency table titled Feelings of Stress at Discontinuation. The table presents various stress levels from 1 to 5 along with their corresponding frequencies, percentages, and cumulative percentages. A stress level of 1 has a frequency of 1, which represents 5.0 percent, with a cumulative percentage of 5.0 percent. A stress level of 2 has a frequency of 3, which represents 15.0 percent, with a cumulative percentage of 20.0 percent. Stress levels 3 and 4 each have a frequency of 5, which represents 25.0 percent individually, with cumulative percentages of 45.0 percent and 70.0 percent, respectively. The highest frequency is for stress level 5, which has a frequency of 6, accounting for 30.0 percent of the total and a cumulative percentage of 100.0 percent. The total number of valid cases is 20, which represents 100.0 percent of the data.
In terms of skewness, the frequency distribution for the variable of age at enrollment appears to be positively skewed, the variables of GPA and stress are negatively skewed, and the variable of hopefulness is normally distributed. The absolute values of the skewness statistics for the variable of age at enrollment is greater than 1.0. The kurtosis statistic for the variable of age at enrollment is also greater than 1.0. No other skewness or kurtosis statistics were greater than 1.0. Note that the skewness statistic for the variable of hopefulness is 0.00, indicating no skewness.

In order to obtain a comparison of the study variables’ deviation from normality (and thereby assessing skewness and kurtosis simultaneously), we must compute a Shapiro-Wilk test of normality.

Step 1: From the “Analyze” menu, choose “Descriptive Statistics” and “Explore.” Move the four study variables over to the box labeled “Dependent List.”


A frequency table shows the distribution of feelings of hopefulness at discontinuation. The frequency table is titled Feelings of Hopefulness at Discontinuation. The table presents hopefulness levels from 1 to 5 along with their frequencies, percentages, and cumulative percentages. Hopefulness level 1 has a frequency of 2, which represents 10.0 percent, with a cumulative percentage of 10.0 percent. Hopefulness level 2 has a frequency of 4, which represents 20.0 percent, with a cumulative percentage of 30.0 percent. The highest frequency is for level 3, with a frequency of 8, which accounts for 40.0 percent, with a cumulative percentage of 70.0 percent. Hopefulness level 4 has a frequency of 4, which represents 20.0 percent, with a cumulative percentage of 90.0 percent. Hopefulness level 5 has a frequency of 2, which represents 10.0 percent, with a cumulative percentage of 100.0 percent. The total number of valid cases is 20, which represents 100.0 percent of the data.
Step 2: Click “Plots.” Check “Normality plots with tests.” Click “Continue” and “OK.”


A histogram displays the frequency distribution of age at enrolment with summary statistics. The histogram is titled Age at Enrolment. The horizontal axis is labeled Age at Enrolment and ranges from 20 to 80 in 10 year intervals. The vertical axis is labeled Frequency and ranges from 0 to 6. The histogram bars represent the following age groups. The 20 to 30 age group has a frequency of 2, the 30 to 40 age group has a frequency of 6, the 40 to 50 age group has a frequency of 4, the 50 to 60 age group has a frequency of 2, and the 60 to 70 and 70 to 80 age groups each have a frequency of 1. In the upper right corner, a text box shows summary statistics mean equals 38, standard deviation equals 11.539, and N equals 20.
For this example, SPSS produces many tables and figures. In the interest of saving space, we will focus on the table of interest, titled “Tests of Normality.” This table contains the Shapiro-Wilk tests of normality for the four study variables. The last column contains the p values of the Shapiro-Wilk statistics. Of the four p values, three are significant at p < 0.05. Hopefulness is the only variable that did not significantly deviate from normality ( p = 0.126).

A line graph displays a single symmetrical bell shaped curve. The line graph shows values on the vertical axis, which range from 0 to 10, and values on the horizontal axis, which range from 2 to 8. The line begins near 0 at horizontal value 2.5, rises symmetrically to a peak of approximately 9 at horizontal value 5, and then descends back to near 0 at horizontal value 7, forming a bell shaped curve.
In summary, the skewness statistics, Shapiro-Wilk values, and visual inspections of the variables of age at enrollment, of GPA, and of stress indicated significant deviations from normality. Hopefulness did not yield skewness, kurtosis, or Shapiro-Wilk values that indicated deviations from normality. Sometimes, Shapiro-Wilk values may conflict with skewness and kurtosis statistics because the Shapiro-Wilk test examines the entire shape of the distribution, while skewness and kurtosis statistics examine only skewness and kurtosis, respectively. When a Shapiro-Wilk value is significant and visual inspection of the frequency distribution indicates non-normality, the researcher must consider a nonparametric statistical alternative ( Field, 2013 ; Pett, 2016 ). See Exercise 23 for a review of nonparametric statistics that would be appropriate when the normality assumption for a parametric statistic is not met.

Study questions

1.
Define skewness.

2.
Define kurtosis.

3.
Given this set of numbers, plot the frequency distribution:

1, 2, 9, 9, 11, 11, 11, 12, 12, 12, 12, 13, 13, 13, 14, 14.

4.
How would you characterize the skewness of the distribution in Question 3: positively skewed, negatively skewed, or approximately normal? Provide a rationale for your answer.

5.
Given this set of numbers, plot the frequency distribution:

1, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 5, 5, 10, 11.

6.
How would you characterize thCalculating descriptive statistics EPUB version of this book
Susan K. Grove, PhD, RN, ANP-BC, GNP-BC; Daisha J. Cipher, PhD

Statistics for Nursing Research, EXERCISE 28, 346-362

There are two major classes of statistics: descriptive statistics and inferential statistics. Descriptive statistics are computed to reveal characteristics of the sample dataset and to describe study variables. Inferential statistics are computed to gain information about effects and associations in the population being studied. For some types of studies, descriptive statistics will be the only approach to analysis of the data. For other studies, descriptive statistics are the first step in the data analysis process, to be followed by inferential statistics. For all studies that involve numerical data, descriptive statistics are crucial in understanding the fundamental properties of the variables being studied. Exercise 28 focuses only on descriptive statistics and will illustrate the most common descriptive statistics computed in nursing research and provide examples using actual study data from empirical publications.

Measures of central tendency
A measure of central tendency is a statistic that represents the center or middle of a frequency distribution. The three measures of central tendency commonly used in nursing research are the mode, median ( MD ), and mean ( 
X
¯
). The mean is the arithmetic average of all of a variable’s values in a study. The median is the exact middle value (or the average of the middle two values if there is an even number of observations). The mode is the most commonly occurring value or values (see Exercise 8 ).

The following data were collected during a cross-sectional survey study that investigated the attitudes and future plans among former registered nurse–to–bachelor of science in nursing (RN-to-BSN) students who had recently discontinued their program ( Cipher & Urban, 2022 ). Table 28.1 contains a simulated subset of data collected from 10 former nursing students who discontinued their programs, and the variable represents the extent to which the student reported feeling relieved at the time of discontinuation, with higher values representing more self-reported relief.

View full size
TABLE 28.1

RATINGS OF RELIEF AMONG NURSING STUDENTS WHO DISCONTINUED THEIR PROGRAMS ( n = 10)

Self-Reported Ratings of Relief at Discontinuation
1
2
2
2
2
3
3
3
4
5
n , sample size.

Because the number of study participants represented is 10, the correct statistical notation to reflect that number is:

n = 10
Note that the n is lowercase because we are referring to a sample of discontinued nursing students. If the data being presented represented the entire population of discontinued nursing students, the correct notation is the uppercase N . Because most nursing research is conducted using samples, not populations, all formulas in the subsequent exercises will incorporate the sample notation, n .

Mode
The mode is the numerical value or score that occurs with the greatest frequency; it does not necessarily indicate the center of the dataset. The data in Table 28.1 contain one mode: 2.0. This value occurred four times in the dataset. When two modes exist, the dataset is referred to as bimodal ; a dataset that contains more than two modes would be multimodal ( Gray & Grove, 2021 ).

Median
The median or MD is the value at the exact center of the ungrouped frequency distribution. It is the 50th percentile. To obtain the MD, sort the values from lowest to highest. If the number of values is an uneven number, the MD is the exact middle number in the dataset. If the number of values is an even number, the MD is the average of the two middle values. Thus the MD may not be an actual value in the dataset. For example, the data in Table 28.1 consist of 10 observations, and therefore the MD is calculated as the average of the two middle values ( Gray & Grove, 2021 ).

MD
=
(
2.0
+
3.0
)
2
=
2.50
Mean
The most commonly reported measure of central tendency is the mean. The mean is the sum of the values divided by the number of values being summed. Thus like the median, the mean may not be a member of the dataset. The formula for calculating the mean is as follows:

X
¯
=
∑
X
n
where

X
¯
 = mean

Σ = sigma, the statistical symbol for summation

X = a single value in the sample

n = total number of values in the sample

The mean of the self-reported ratings for the variable of relief is calculated as follows:

X
¯
=
(
1
+
2
+
2
+
2
+
2
+
3
+
3
+
3
+
4
+
5
)
10
=
2.70
The mean is an appropriate measure of central tendency for approximately normally distributed populations with variables measured at the interval or ratio level. It is also appropriate for ordinal-level data such as the Likert scale variable of relief, where higher numbers represent more of the construct being measured and lower numbers represent less of the construct. Common examples of ordinal data include pain levels, patient satisfaction, depression, and health status ( Waltz et al., 2017 ).

The mean is sensitive to extreme values such as outliers. An outlier is a value in a sample dataset that is unusually low or unusually high in the context of the rest of the sample data ( Kim et al., 2022 ). An example of an outlier in the data presented in Table 28.1 might be a value such as 10. The existing values range from 1 to 5, meaning that no participant rated their relief level beyond a value of 5. If a study participant accidentally rated their level of relief as a 10, the mean would be much larger: 3.36 instead of 2.70. The outlier would also change the frequency distribution. Without the outlier, the frequency distribution is slightly positively skewed, with a skewness statistic of 0.73, as shown in Fig. 28.1 . Including the outlier changes the shape of the distribution to appear substantially positively skewed, with a skewness statistic of 2.24.

Two line graphs compare relief rating frequency distributions in two different conditions. The graph on the left presents a line graph with the horizontal axis labeled as Relief Rating, ranging from 0 to 6, and the vertical axis labeled as Frequency, ranging from 0 to 5. The curve peaks around a relief rating of 2 and gradually declines. The graph on the right shows a similar line graph with the horizontal axis labeled as Relief Rating, ranging from 0 to 11, and the vertical axis labeled as Frequency, also ranging from 0 to 5. This graph features multiple peaks, including one around a relief rating of 2 and another near a rating of 10, with lower frequencies in between. Both graphs are vertically aligned and show different distributions of relief ratings.
FIG. 28.1 ■
FREQUENCY DISTRIBUTION OF SELF-REPORTED RATINGS OF RELIEF, WITHOUT AND WITH AN OUTLIER.

Outliers can also be identified by using the approach called the three-sigma rule , which involves taking the suspected outlier and determining its distance from the mean (Lehmann, 2013). First, the suspected outlier is subtracted from the mean. If that result (in absolute value) is greater than 3 × SD , then the suspected value is identified as an outlier. Using the example from Fig. 28.1 , the mean of the data with the suspected outlier of 10 is 3.60, and the standard deviation or SD is 2.10. When the suspected outlier is subtracted from the mean, the result in absolute value is: 10– 3.60 = 6.40. This difference is compared with 3 × SD : 3 × 2.10 = 6.30. Because the suspected outlier of 10 lies outside of three standard deviations above the mean, the value is identified as an outlier.

Although the use of summary statistics has been the traditional approach to describing data or describing the characteristics of the sample before inferential statistical analysis, its ability to clarify the nature of data is limited. For example, using measures of central tendency, particularly the mean, to describe the nature of the data obscures the effect of extreme values or deviations in the data. Thus significant features in the data may be concealed or misrepresented. Often, anomalous, unexpected, or problematic data and discrepant patterns are evident, but are not regarded as meaningful. Measures of dispersion, such as the range, difference scores, variance, and standard deviation, provide important insights into the nature of the data ( King & Eckersley, 2019 ; Terrell, 2021 ).

Measures of dispersion
Measures of dispersion , or variability, are measures of individual differences of the members of the population and sample. They indicate how values in a sample are dispersed around the mean. These measures provide information about the data that is not available from measures of central tendency. They indicate how different the values are—the extent to which individual values deviate from one another. If the individual values are similar, measures of variability are small, and the sample is relatively homogeneous in terms of those values. Heterogeneity (i.e., wide variation in values) is important in some statistical procedures, such as correlation. Heterogeneity is determined by measures of variability. The measures of variability most commonly conducted include range, difference scores, variance, and SD (see Exercise 9 ; Gray & Grove, 2021 ; Kim et al., 2022 ).

Range
The simplest measure of dispersion is the range . In published studies, range is presented in two ways: (1) the range is the set of lowest and highest values, or (2) the range is calculated by subtracting the lowest value from the highest value. The range for the values in Table 28.1 is 1.0 to 5.0, or it can be calculated as follows: 5.0 − 1.0 = 4.0. In this form, the range is a difference score that uses only the two extreme values for the comparison. Therefore a very large range can indicate the presence of an outlier.

Difference scores
Difference scores are obtained by subtracting the mean from each value. Sometimes a difference score is referred to as a deviation score because it indicates the extent to which a score (or value) deviates from the mean. Of course, most variables in nursing research are not “scores,” yet the term difference score is used to represent a value’s deviation from the mean. The difference score is positive when the value is above the mean, and it is negative when the value is below the mean (see Table 28.2 ). Difference scores are the basis for many statistical analyses and can be found within many statistical equations. The formula for difference scores is:

X
−
X
¯
∑
of absolute values: 9.0
View full size
TABLE 28.2

DIFFERENCE SCORES OF SELF-REPORTED RELIEF RATINGS

X	− 
X
¯
X − 
X
¯
|
X
−
X
¯
|
1	2.70	–1.70	1.70
2	2.70	–.70	.70
2	2.70	–.70	.70
2	2.70	–.70	.70
2	2.70	–.70	.70
3	2.70	.30	.30
3	2.70	.30	.30
3	2.70	.30	.30
4	2.70	1.30	1.30
5	2.70	2.30	2.30
The mean deviation is the average difference score, using the absolute values. The formula for the mean deviation is:

X
¯
deviation
=
∑
|
X
−
X
¯
|
n
In this example, the mean deviation is 0.90. This value was calculated by taking the sum of the absolute value of each difference score (1.70, 0.70, 0.70, 0.70, 0.70, 0.30, 0.30, 0.30, 1.30, 2.30) and dividing by 10. The result indicates that, on average, participants’ ratings of the variable of relief deviated from the mean by 0.90 units.

Variance
Variance is another measure commonly used in statistical analysis. The equation for a sample variance ( s 2 ) is below.

s
2
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
Note that the lowercase letter s 2 is used to represent a sample variance. The lowercase Greek sigma (σ 2 ) is used to represent a population variance, in which the denominator is N instead of n − 1. Because most nursing research is conducted using samples, not populations, formulas in the subsequent exercises that contain a variance or standard deviation will incorporate the sample notation, using n − 1 as the denominator. Moreover, many statistical software packages compute the variance and standard deviation using the sample formulas, not the population formulas, unless otherwise programmed.

The variance is always a positive value and has no upper limit. In general, the larger the variance, the larger the dispersion of sample values. The variance is most often computed to derive the standard deviation because, unlike the variance, the standard deviation reflects important properties about the frequency distribution of the variable it represents. Table 28.3 displays how we would compute a variance by hand, using the discontinued nursing student variable of relief.

s
2
=
12.10
9
s
2
=
1.3444, rounded to 1.34
View full size
TABLE 28.3

VARIANCE COMPUTATION OF SELF-REPORTED RELIEF RATINGS

X	− 
X
¯
X − 
X
¯
( X − 
X
¯
) 2
1	2.70	−1.70	2.89
2	2.70	−.70	.49
2	2.70	−.70	.49
2	2.70	−.70	.49
2	2.70	−.70	.49
3	2.70	.30	.09
3	2.70	.30	.09
3	2.70	.30	.09
4	2.70	1.30	1.69
5	2.70	2.30	5.29
∑	12.10
X, a single value in the sample; 
X
¯
, mean.

Standard deviation
Standard deviation is a measure of dispersion that is the square root of the variance. The standard deviation is represented by the notation s or SD . The equation for obtaining a standard deviation is

SD
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
Table 28.3 displays the computations for the variance. To compute the SD , simply take the square root of the variance. We know that the variance of the variable of relief is s 2 = 1.3444, rounded to 1.34. Therefore the s of relief is SD = 1.1595, rounded to 1.16. The SD is an important statistic, both for understanding dispersion within a distribution and for interpreting the relationship of a particular value to the distribution ( Gray & Grove, 2021 ).

Sampling error
A standard error describes the extent of sampling error. For example, a standard error of the mean is calculated to determine the magnitude of the variability associated with the mean. A small standard error is an indication that the sample mean is close to the population mean, while a large standard error yields less certainty that the sample mean approximates the population mean. The formula for the standard error of the mean ( 
s
X
¯
) is:

s
X
¯
=
s
n
Using the discontinued nursing student data, we know that the standard deviation of the relief variable is s or SD = 1.16. Therefore the standard error of the mean for relief is computed as follows:

s
X
¯
=
1
.
16
10
s
X
¯
=
0.367, rounded to 0.37
The standard error of the mean for relief is 0.367.

Confidence intervals
To determine how closely the sample mean approximates the population mean, the standard error of the mean is used to build a confidence interval (CI). For that matter, a CI can be created for many statistics, such as a mean, proportion, and odds ratio. To build a CI around a statistic, you must have the standard error value and the t value to adjust the standard error. The degrees of freedom ( df ) to use to compute a CI is df = n – 1.

To compute the CI for a mean, the lower and upper limits of that interval are created by multiplying the s x by the t statistic, where df = n – 1. For a 95% CI, the t value should be selected at α = 0.05. For a 99% CI, the t value should be selected at α = 0.01.

Using the discontinued nursing student data, we know that the standard error of the mean for the variable of relief is 
s
X
¯
=
0
.
37
. The mean for relief is 2.70. Therefore the 95% CI for the mean of relief is computed as follows:

X
¯
±
s
X
¯
t
2.70
±
(
0.37
)
(
2.262
)
2.70
±
0.84
As referenced in Appendix A , the t value required for the 95% CI with df = 9 is 2.262 for a two-tailed test. The computation here results in a lower limit of 1.86 and an upper limit of 3.54. This means that our CI of 1.86 to 3.54 estimates the population mean of the relief rating with 95% confidence ( Kline, 2004 ). Technically and mathematically, it means that if we computed the mean relief ratings on an infinite number of discontinued nursing students, exactly 95% of the intervals would contain the true population mean, and 5% would not contain the population mean ( Gliner et al., 2017 ). If we were to compute a 99% CI, we would require the t value of 3.25 that is referenced at α = 0.01. Therefore the 99% CI for the mean relief rating is computed as follows:

2.70
±
(
0.37
)
(
3.25
)
2.70
±
1.20
As referenced in Appendix A , the t value required for the 99% CI with df = 9 is 3.250 for a two-tailed test. This computation results in a lower limit of 1.50 and an upper limit of 3.90. This means that our CI of 1.50 to 3.90 estimates the population mean variable of relief rating with 99% confidence.

Degrees of freedom
The concept of df was used in reference to computing a CI. For any statistical computation, df means the number of independent pieces of information that are free to vary to estimate another piece of information (Zar, 2010). In the case of the CI, the degrees of freedom are n − 1. This means that there are n − 1 independent observations in the sample that are free to vary (to be any value) to estimate the lower and upper limits of the CI.

SPSS computations
A cross-sectional survey study was conducted to investigate the attitudes and future plans among former RN-to-BSN students who had recently discontinued their program ( Cipher & Urban, 2022 ). Gender, age at program enrollment, recent grade point average (GPA), ratings of hopefulness and relief, and potential reasons for discontinuation (e.g., family responsibilities and financial issues) were among the study variables examined. The study variables of hopefulness at discontinuation and relief at discontinuation were assessed on a 5-point Likert scale. Higher values of hopefulness and relief are indicative of higher self-reported levels of hopefulness and relief, respectively. The variables of family (i.e., family responsibilities) and finance (i.e., financial issues) are binary variables that represent potential reasons for discontinuation, assessed as yes/no. A simulated subset of the study data is presented in Table 28.4 .

This is how our dataset looks in SPSS.


A spreadsheet interface shows student data entries for variables including gender, age, grade point average, hopeful, relieved, family, and finance. The spreadsheet interface shows a data table with ten rows and ten columns, each representing a student entry. The column headers are I D, Female, Age, G P A, Hopeful, Relieved, Family, and Finance. The I D column ranges from 1 to 10. The Female column contains categorical values of either Female or Male. The Age column shows values between 25 and 68. The G P A column lists grade point averages, mostly around 3.00 to 4.00. The Hopeful and Relieved columns include integer scores between 1 and 5. The Family and Finance columns have Yes or No values. The software interface includes menu options such as File, Edit, View, Data, Transform, Analyze, Graphs, Utilities, Extensions, Window, and Help, with tool icons displayed below the menu bar.
Step 1: For a nominal variable, the appropriate descriptive statistics are frequencies and percentages. There are three nominal variables in this dataset: gender, family, and finance. From the “Analyze” menu, choose “Descriptive Statistics” and “Frequencies.” Move gender over to the right. Click “OK.”


A frequencies window interface displays the variable Female Gender selected for analysis with options for statistics and charts. The frequencies window interface displays a list of variables on the left, including Participant I D, Age at Enrollment, G P A at Discontinuation, Feelings of Hopeful, Feelings of Relief at Discontinuation, Family Responsibilities, and Financial Issues. The selected variable Female Gender appears in the central Variable s box. Below the list are two checkboxes labeled Display frequency tables and Create A P A style tables, with only the Display frequency tables option selected. To the right, there are five buttons labeled Statistics, Charts, Format, Style, and Bootstrap. At the bottom, there are six buttons labeled O K, Paste, Reset, Cancel, and Help. The window is part of a statistical analysis software interface used for selecting and configuring frequency analysis.
Step 2: For ordinal and interval/ratio variables, the appropriate descriptive statistics are means and standard deviations. There are four ordinal and interval/ratio variables in this dataset: age, GPA, hopefulness, and relief. From the “Analyze” menu, choose “Descriptive Statistics” and “Explore.” Move GPA and relief over to the right. Click “OK.”


An explore window interface displays selected variables G P A at Discontinuation and Feelings of Relief in the dependent list. The explore window interface displays a list of variables on the left, including Participant I D, Female Gender, Age at Enrollment, Feelings of Hopeful, Feelings of Relief, Family Responsibilities, and Financial Issues. Two variables, G P A at Discontinuation and Feelings of Relief, appear in the dependent list box on the right. The factor list and label cases by boxes are empty. Below the variable list is a display section with three radio button options labeled Both, Statistics, and Plots, with Both selected. To the right are four buttons labeled Statistics, Plots, Options, and Bootstrap. At the bottom of the window are six buttons labeled O K, Paste, Reset, Cancel, and Help. The interface is part of statistical analysis software used for exploring relationships between selected variables.
Interpretation of SPSS output
The following tables are generated from SPSS. The first set of tables (from the first set of SPSS commands in Step 1) contains the frequencies of gender. Most participants (80%) were female.


A frequency table displays gender distribution with values for male and female categories. The table presents frequency analysis results under the heading Frequencies and Frequency Table for the variable Female Gender. It includes a row for Male with a frequency of 2, percent of 20.0, valid percent of 20.0, and cumulative percent of 20.0. The row for Female shows a frequency of 8, percent of 80.0, valid percent of 80.0, and cumulative percent of 100.0. The Total row displays a frequency of 10, percent of 100.0, and valid percent of 100.0. The layout summarises the distribution of gender responses in tabular form.
The second set of output (from the second set of SPSS commands in Step 2) contains the descriptive statistics for the variables of GPA and relief, including the mean, SD (standard deviation), SE, 95% CI for the mean, median, variance, minimum value, maximum value, range, and skewness and kurtosis statistics.


A screenshot shows descriptive statistics for G P A and feelings of relief at discontinuation. The screenshot shows a Descriptives table from SPSS under the Explore function. It presents statistics for two variables, G P A at discontinuation and feelings of relief at discontinuation. For G P A at discontinuation, the mean is 3.2823 with a standard error of.24234, the lower bound of the 95 percent confidence interval is 2.7341, and the upper bound is 3.8305. The 5 percent trimmed mean is 3.3248, the median is 3.4465, the variance is.587, the standard deviation is.76636, the minimum is 1.80, the maximum is 4.00, the range is 2.20, the interquartile range is 1.17, the skewness is negative.864 with standard error.687, and kurtosis is negative.201 with standard error 1.334. For feelings of relief at discontinuation, the mean is 2.70 with a standard error of.367, the lower bound of the 95 percent confidence interval is 1.87, and the upper bound is 3.53. The 5 percent trimmed mean is 2.67, the median is 2.50, the variance is 1.344, the standard deviation is 1.160, the minimum is 1, the maximum is 5, the range is 4, the interquartile range is 1, the skewness is.727 with a standard error of.687, and the kurtosis is.512 with a standard error 1.334.
Study questions

1.
Define mean.

2.
What does this symbol, s 2 , represent?

3.
Define outlier.

4.
Are there any outliers among the values of the variable relief? Provide a rationale for your answer.

5.
List the 95% CI (lower and upper limits) for the mean of GPA. How would you interpret these values?

6.
What percentage of participants listed family responsibilities as a reason for program discontinuation?

7.
Can you compute the variance for the variable of GPA by using the information presented in the SPSS output in the example? If so, calculate the variance.

8.
Plot the frequency distribution of the variable of age.

9.
Where is the mean in relation to the median in the frequency distribution of the variable of age? What does this mean indicate regarding the distribution of values?

10.
When would a median be more informative than a mean in describing a variable?

Answers to study questions

1.
The mean is defined as the arithmetic average of a set of numbers.

2.
s 2 represents the sample variance of a given variable.

3.
An outlier is a value in a sample dataset that is unusually low or unusually high in the context of the rest of the sample data ( Gray & Grove, 2021 ; Kim et al., 2022 ).

4.
There are no outliers among the ratings of the variable relief at discontinuation. The frequency distribution is approximately normal. Using the three-sigma rule, there are no values for ratings of relief that exceed three standard deviations from the mean in absolute value ( Lehmann, 2013 ).

5.
The 95% CI is 2.73 to 3.83, meaning that our CI of [2.73, 3.83]Calculating the Pearson product-moment correlation coefficient EPUB version of this book
Susan K. Grove, PhD, RN, ANP-BC, GNP-BC; Daisha J. Cipher, PhD

Statistics for Nursing Research, EXERCISE 29, 363-377

Correlational analyses identify associations between two variables. There are many different kinds of statistics that yield a measure of correlation. All of these statistics address a research question or hypothesis that involves an association or relationship. Examples of research questions that are answered with correlation statistics are: Is there an association between weight loss and depression? and Is there a relationship between patient satisfaction and health status? A hypothesis is developed to identify the nature (positive or negative) of the relationship between the variables being studied. Examples of hypotheses that are answered with correlation statistics are: Lower amounts of weight loss are associated with higher levels of depression and Higher levels of patient satisfaction are associated with increased health status.

The Pearson product-moment correlation was the first of the correlation measures developed and is the most commonly used. As is explained in Exercise 13 , this coefficient (statistic) is represented by the letter r , and the value of r is always between −1.00 and + 1.00. A value of zero indicates no relationship between the two variables. A positive correlation indicates that higher values of x are associated with higher values of y . A negative or inverse correlation indicates that higher values of x are associated with lower values of y . The r value is indicative of the slope of the line (called a regression line) that can be drawn through a standard scatterplot of the two variables (see Exercise 11 ). The strengths of different relationships are identified in Table 29.1 ( Cohen, 1988 ).

View full size
TABLE 29.1

STRENGTH OF ASSOCIATION FOR PEARSON r

Strength of Association	Positive Association	Negative Association
Weak association	0.00−<0.30	0.00−<−0.30
Moderate association	0.30–0.49	−0.49 to −0.30
Strong association	≥0.50	−1.00 to −0.50
Research designs appropriate for the Pearson r
Research designs that may use the Pearson r include any associational design ( Gliner et al., 2017 ; Kazdin, 2022 ). The variables involved in the design are often attributional, meaning the variables are characteristics of the participant, such as health status, blood pressure, gender, diagnosis, or race/ethnicity. Regardless of the nature of variables, the variables submitted to a Pearson correlation calculation must be measured at the interval or ratio level and in certain circumstances, ordinal level, explained below.

Statistical formula and assumptions
Use of the Pearson correlation coefficient involves the following assumptions:

1.
Interval or ratio measurement of both variables (e.g., age, income, blood pressure, cholesterol levels); however, if the variables are measured with a Likert scale, and the frequency distribution is approximately normally distributed, these data are usually treated as interval-level measurements and are appropriate for the Pearson r ( de Winter & Dodou, 2010 ; Rasmussen, 1989 ).

2.
There is normal distribution of at least one variable.

3.
There is independence of observational pairs.

4.
Homoscedasticity is present.

Data that are homoscedastic are evenly dispersed both above and below a line of perfect prediction when variable x predicts variable y (see Exercise 30 for illustrations of homoscedasticity and heteroscedasticity). Homoscedasticity reflects equal variance of both variables. In other words, for every value of x , the distribution of y values should have equal variability. If the data for the two variables being correlated are not homoscedastic, inferences made during significance testing could be invalid ( Cohen & Cohen, 1983 ).

The Pearson product-moment correlation coefficient is computed using one of several formulas—the one here is considered the computational formula because it makes computation by hand easier ( Zar, 2010 ):

r
=
n
∑
xy
−
∑
x
∑
y
[
n
∑
x
2
−
(
∑
x
)
2
]
[
n
∑
y
2
−
(
∑
y
)
2
]
where

r = Pearson correlation coefficient

n = total number of subjects

x = value of the first variable

y = value of the second variable

xy = x multiplied by y

Hand calculations
This example includes data collected from a survey study by Urban et al. (2022) . Newly licensed registered nurses (RNs) were surveyed and administered several questionnaires. Two of these were the Perceived Stress Scale (PSS) and the Brief Resilience Scale (BRS). Scores on the PSS range from 0 to 40, with higher scores indicating increased (worse) self-reported stress levels. Scores on the BRS range from 1 to 5, with higher scores indicating greater (better) self-reported resilience levels. These Likert-scale variables were normally distributed and therefore suitable for parametric statistics ( de Winter & Dodou, 2010 ; Rasmussen, 1989 ).

The null hypothesis is: There is no correlation between stress levels and resilience levels among new RNs. A simulated subset of 20 students was created for this example so that the computations would be small and manageable. In actuality, studies involving Pearson correlations need to be adequately powered ( Cohen, 1988 ; Taylor & Spurlock, 2018 ). Observe that the data in Table 29.2 are arranged in columns that correspond to the elements of the formula. The summed values in the last row of Table 29.2 are inserted into the appropriate place in the Pearson r formula.

View full size
TABLE 29.2

SELF-REPORTED STRESS AND RESILIENCE LEVELS AMONG NEWLY LICENSED NURSES

Participant Number	x (Stress)	y (Resilience)	x 2	y 2	xy
1	24.00	4.17	576.00	17.39	100.08
2	7.00	4.50	49.00	20.25	31.50
3	10.00	3.17	100.00	10.05	31.70
4	24.00	3.83	576.00	14.67	91.92
5	24.00	3.17	576.00	10.05	76.08
6	19.00	1.83	361.00	3.35	34.77
7	25.00	4.67	625.00	21.81	116.75
8	30.00	2.67	900.00	7.13	80.10
9	34.00	3.00	1156.00	9.00	102.00
10	31.00	2.83	961.00	8.01	87.73
11	28.00	2.17	784.00	4.71	60.76
12	24.00	2.17	576.00	4.71	52.08
13	13.00	4.67	169.00	21.81	60.71
14	21.00	3.17	441.00	10.05	66.57
15	10.00	4.00	100.00	16.00	40.00
16	7.00	4.67	49.00	21.81	32.69
17	15.00	2.50	225.00	6.25	37.50
18	21.00	3.33	441.00	11.09	69.93
19	14.00	4.00	196.00	16.00	56.00
20	15.00	3.50	225.00	12.25	52.50
sum Σ	396.00	68.02	9,086.00	246.37	1,281.37
The computations for the Pearson r are as follows:

Step 1: Plug the values from the bottom row of Table 29.2 into the Pearson r formula.

r
=
n
∑
xy
−
∑
x
∑
y
[
n
∑
x
2
−
(
∑
x
)
2
]
[
n
∑
y
2
−
(
∑
y
)
2
]
r
=
20
(
1
,
281.37
)
−
(
396
)
(
68.02
)
[
(
20
)
(
9
,
086.00
)
−
396.00
2
]
[
(
20
)
(
246.37
)
−
68.02
2
]
Step 2: Solve for r .

r
=
20
(
1
,
281.37
)
−
(
396.00
)
(
68.02
)
[
24
,
904.00
]
[
300.68
]
r
=
25
,
627.40
−
26
,
935.92
[
24
,
904.00
]
[
300.68
]
r
=
−
1
,
308.52
2
,
736.45
=
−
0.48
Step 3: Compute the degrees of freedom ( df ).

df
=
n
−
2
df
=
20
−
2
df
=
18
Step 4: Locate the critical r value in the r distribution table ( Appendix B ) and compare it to our obtained r value.

The r is −0.48, indicating a moderate negative (inverse) correlation between stress and resilience among new RNs. To determine whether this relationship is improbable to have been caused by chance alone, we consult the r probability distribution table in Appendix B . The formula for df for a Pearson r is n − 2. With r of −0.48 and df = 18, the critical r value at α = 0.05, df = 18 is 0.4438, rounded to 0.444, for a two-tailed test. Our obtained r was −0.48, which in absolute value exceeds the critical value in the table. Thus the r value of −0.48 is considered statistically significant. It should be noted that the absolute value of the obtained r is compared with the critical r value. The sign of the r is only used to indicate whether the association is positive or negative.

SPSS computations
This is how our dataset looks in SPSS.


A spreadsheet interface displays participant data with I D, perceived stress scores, and resilience scores. The spreadsheet interface presents participant data in three columns labeled I D, P S S, and B R S. The I D column contains participant numbers from 9 to 20. The P S S column includes Perceived Stress Scale scores ranging from 7.00 to 34.00. The B R S column contains Brief Resilience Scale scores ranging from 2.17 to 4.67. Each row represents a unique participant's data entry. The software toolbar at the top includes menus labeled File, Edit, View, Data, Transform, Analyze, and Graphs, along with icons for file handling and data navigation. The layout belongs to a statistical analysis software used for data entry and variable management.
Step 1: From the “Analyze” menu, choose “Correlate” and “Bivariate.”

Step 2: Move the two variables, PSS and BRS, over to the right, as shown. Click “OK.”


A correlation analysis window displays selected variables and settings for Pearson correlation. The correlation analysis window displays the variable Participant I D on the left and two selected variables on the right Perceived Stress Scale Score and Brief Resilience Scale Score. Pearson is selected under Correlation Coefficients, while Kendall tau b and Spearman are unchecked. The Test of Significance section has Two tailed selected. Additional options include checkboxes for Flag significant correlations and Show only the lower triangle, which are both checked. The buttons on the right side include Options, Style, Bootstrap, and Confidence interval. At the bottom, there are buttons for O K, Paste, Reset, Cancel, and Help. The interface belongs to statistical analysis software used for bivariate correlation analysis.
Interpretation of SPSS output
The following table is generated from SPSS. The table contains a correlation matrix that includes the Pearson r between stress and resilience, along with the p value and df . The r is listed as −0.478 rounded to −0.48, and the p is 0.033.


A correlation table displays Pearson correlation values between perceived stress and resilience scores. The correlation table presents Pearson correlation results between Perceived Stress Scale Score and Brief Resilience Scale Score. The table is symmetrical, with the upper diagonal mirroring the lower diagonal. The correlation between Perceived Stress Scale Score and itself is 1. The correlation between Perceived Stress Scale Score and Brief Resilience Scale Score is negative 0.478, with a significance value of 0.033. Similarly, the correlation between Brief Resilience Scale Score and Perceived Stress Scale Score is negative 0.478, with a significance value of 0.033. The table includes a note stating that the exact p value is 0.033 and highlights that the upper diagonal is a mirror image of the lower diagonal. A footnote indicates that the correlation is significant at the 0.05 level based on a two tailed test.
Final interpretation in American Psychological Association format
The following interpretation is written as it might appear in a research article, formatted according to American Psychological Association (APA) guidelines ( APA, 2020 ). It should be noted that all statistical values reported here are rounded to two decimal places, with the exception of the p value, which is rounded to three decimal places.

A Pearson correlation analysis indicated that there was a significant correlation between stress and resilience among new RNs, r (18) = −0.48, p = 0.033. Higher levels of stress were associated with lower levels of resilience and vice versa, lower levels of stress were associated with higher resilience.

Effect size
After establishing the statistical significance of the r value, it must subsequently be examined for clinical importance. There are ranges for strength of association suggested by Cohen (1988) , as displayed in Table 29.1 . One can also assess the magnitude of association by obtaining the coefficient of determination for the Pearson correlation. Computing the coefficient of determination simply involves squaring the r value. The r 2 multiplied by 100% represents the percentage of variance shared between the two variables ( Cohen & Cohen, 1983 ). In our example, the r was −0.48, and therefore the r 2 was 0.2304. This indicates that stress and resilience shared 23.04% (0.2304 × 100%) of the same variance. More specifically, 23.04% of the variance in stress can be explained by knowing the nurse’s resilience level, and vice versa—23.04% of the variance in resilience can be explained by knowing the nurse’s level of stress.

Study questions

1.
If you have access to SPSS, compute the Shapiro-Wilk test of normality for the variables of stress (PSS) and resilience (BRS) (as demonstrated in Exercise 27 ). If you do not have access to SPSS, plot the frequency distributions by hand. What do the results indicate with regard to the normality of the distributions?

2.
What is the null hypothesis in the example?

3.
What was the exact likelihood of obtaining an r value at least as extreme or close to the one that was actually observed, assuming that the null hypothesis is true?

4.
How would you characterize the magnitude of the effect between stress and resilience? Provide a rationale for your answer.

5.
In the study of newly licensed nurses, depression levels were also measured. If the Pearson correlation between resilience and depression is r = −0.609, how much variance in resilience levels is explained by knowing the new RN’s level of depression? Show your calculations for this value.

6.
What kind of design was used in the example? Provide a rationale for your answer.

7.
Was the sample size adequate to detect a significant correlation in this example? Provide a rationale for your answer.

8.
A researcher computed a Pearson r and obtained an r of 0.57. How would you characterize the magnitude of the r value? What is the percentage of variance explained by this r value? Show your calculations.

9.
A researcher computed a Pearson r and obtained an r of 0.12. How would you characterize the magnitude of the r value? Provide a rationale for your answer.

10.
A researcher computed a Pearson r on two different samples, one with n = 15, and the other with n = 40. In both samples, she obtained an r of 0.50. What is the critical tabled r for each sample at α = 0.05, two-tailed? Discuss the meaning of the critical table values of r for the samples of different sizes.

Calculating simple linear regression EPUB version of this book
Susan K. Grove, PhD, RN, ANP-BC, GNP-BC; Daisha J. Cipher, PhD

Statistics for Nursing Research, EXERCISE 30, 378-393

Simple linear regression is a procedure that provides an estimate of the value of a dependent variable (outcome) based on the value of an independent variable (predictor). Knowing that estimate with some degree of accuracy, we can use regression analysis to predict the value of one variable if we know the value of the other variable ( Cohen & Cohen, 1983 ). The regression equation is a mathematical expression of the influence that a predictor has on a dependent variable, based on a theoretical proposition or framework ( Gray & Grove, 2021 ). For example, in Exercise 14 , Fig. 14.2 illustrates the linear relationship between gestational age and birth weight. As shown in the scatterplot, there is a strong positive relationship between the two variables. Advanced gestational ages predict higher birth weights.

A regression equation can be generated with a dataset containing study participants’ x and y values. Once this equation is generated, it can be used to predict future participants’ y values, given only their x values. In simple or bivariate regression, predictions are made in cases with two variables. The score on variable y (dependent variable, or outcome) is predicted from the same individual’s known score on variable x (independent variable, or predictor; Gray & Grove, 2021 ).

Research designs appropriate for simple linear regression
Research designs that may use simple linear regression include any associational design ( Gliner et al., 2017 ; Kazdin, 2022 ). The variables involved in the design are attributional, meaning the variables are characteristics of the participant, such as health status, blood pressure, gender, diagnosis, or ethnicity. Regardless of the nature of variables, the dependent variable submitted to simple linear regression must be measured at the interval or ratio level (see Exercise 1 ).

Statistical formula and assumptions
Use of simple linear regression involves the following assumptions ( Zar, 2010 ):

1.
Normal distribution of the dependent ( y ) variable

2.
Linear relationship between x and y

3.
Independent observations

4.
No (or little) multicollinearity

5.
Homoscedasticity

Data that are homoscedastic are evenly dispersed both above and below a plotted line of perfect prediction when variable x predicts variable y . If the data for the predictor and dependent variable are not homoscedastic, inferences made during significance testing could be invalid ( Cohen & Cohen, 1983 ; Zar, 2010 ). Visual examples of homoscedasticity and heteroscedasticity are presented in Exercise 31 .

In simple linear regression, the dependent variable is measured as interval or ratio. However, if the variable is measured with a Likert scale, and the frequency distribution is approximately normally distributed, these data are usually considered interval-level measurements and are appropriate to serve as the outcome in a linear regression model ( Rasmussen, 1989 ; Waltz et al., 2017 ). The predictor can be any scale of measurement; however, if the predictor is nominal, it must be correctly coded. Once the data are ready, the parameters a and b are computed to obtain a regression equation. To understand the mathematical process, recall the algebraic equation for a straight line:

y
=
bx
+
a
where

y
=
the dependent variable (outcome)
x
=
the independent variable (predictor)
b
=
the slope of the line, also referred to as unstandardized beta
a = y -intercept (the point where the regression line intersects the y -axis)
No single regression line can be used to predict with complete accuracy every y value from every x value. In fact, you could draw an infinite number of lines through the scattered paired values ( Zar, 2010 ). However, the purpose of the regression equation is to develop the line to allow the highest degree of prediction possible—the line of best fit. The procedure for developing the line of best fit is the method of least squares ( Tabachnick & Fidell, 2019 ). The formulas for the unstandardized beta ( b ) and y -intercept ( a ) of the regression equation are computed as follows. Note that once the b is calculated, the value is inserted into the formula for a.

b
=
n
∑
xy
−
∑
x
∑
y
n
∑
x
2
−
(
∑
x
)
2
a
=
∑
y
−
b
∑
x
n
Hand calculations
This example includes data collected from a survey study by Urban et al. (2022) . Newly licensed registered nurses (RNs) were surveyed and administered several questionnaires. Two of these were the Patient Health Questionnaire (PHQ-9) and the Brief Resilience Scale (BRS). Scores on the PHQ-9 range from 0 to 27, with higher scores indicating increased (worse) self-reported depression levels. Scores on the BRS range from 1 to 5, with higher scores indicating greater (better) self-reported resilience levels.

The null hypothesis is: Self-reported depression levels do not predict resilience levels among newly licensed RNs. A simulated subset of 20 participants was created for this example so that the computations would be small and manageable. In actuality, studies involving linear regression need to be adequately powered ( Aberson, 2019 ; Gaskin & Happell, 2014 ; Taylor & Spurlock, 2018 ;). Observe that the data in Table 30.1 are arranged in columns that correspond to the elements of the formula. The summed values in the last row of Table 30.1 are inserted into the appropriate place in the formula for b.

View full size
TABLE 30.1

SELF-REPORTED DEPRESSION AND RESILIENCE LEVELS AMONG NEWLY LICENSED NURSES

Participant Number	x (Depression)	y (Resilience)	x 2	xy
1	6.00	4.17	36.00	25.02
2	5.00	4.50	25.00	22.50
3	8.00	3.17	64.00	25.36
4	10.00	3.83	100.00	38.30
5	10.00	3.17	100.00	31.70
6	11.00	1.83	121.00	20.13
7	11.00	4.67	121.00	51.37
8	12.00	2.67	144.00	32.04
9	13.00	3.00	169.00	39.00
10	15.00	2.83	225.00	42.45
11	18.00	2.17	324.00	39.06
12	19.00	2.17	361.00	41.23
13	1.00	4.67	1.00	4.67
14	2.00	3.17	4.00	6.34
15	3.00	4.00	9.00	12.00
16	4.00	4.67	16.00	18.68
17	4.00	2.50	16.00	10.00
18	4.00	3.33	16.00	13.32
19	5.00	4.00	25.00	20.00
20	6.00	3.50	36.00	21.00
Sum Σ	167.00	68.02	1,913.00	514.17
The computations for the b and a are as follows:


Step 1: Calculate b .

From the values in Table 30.1 , we know that n = 20, Σx = 167.00, Σy = 68.02, Σx 2 = 1,913.00, and Σxy = 514.17. These values are inserted into the formula for b , as follows:

b
=
20
(
514.17
)
−
(
167.00
)
(
68.02
)
20
(
1913.00
)
−
167.00
2
b
=
−
1
,
075.94
10
,
371.00
b
=
−
0.104

Step 2: Calculate a .

From Step 1, we now know that b = −0.104, and we plug this value into the formula for a . Note that the three decimal places in b are being retained so that the resulting values for the remaining steps will be more accurate.

a
=
68.020
−
(
−
0.104
)
(
167.000
)
20
a
=
85.388
20
a
=
4.269

Step 3: Write the new regression equation:

y
=
−
0.104
x
+
4.269

Step 4: Calculate R .

The multiple R is defined as the correlation between the actual y values and the predicted y values using the new regression equation. The predicted y value using the new equation is represented by the symbol ŷ to differentiate from y , which represents the actual y values in the dataset. We can use our new regression equation from Step 3 to compute predicted resilience levels for each RN, using their self-reported level of depression. For example, participant #1 had a PHQ (depression) score of 6.00, and their predicted level of resilience is calculated as:

ŷ =−0.104(6)+4.269
ŷ = 3.645, rounded to 3.65
Thus the predicted ŷ is 3.65. This procedure would be continued for the rest of the participants, and the Pearson correlation between the resilience score ( y ) and the predicted resilience score ( ŷ ) would yield the multiple R value. In this example, the R = 0.609, rounded to 0.61. The higher the R, the more likely that the new regression equation accurately predicts y, because the higher the correlation, the closer the actual y values are to the predicted ŷ values. Fig. 30.1 displays the regression line where the x -axis represents possible depression scores, and the y -axis represents the predicted resilience scores ( ŷ values).

Step 5: Determine whether the predictor significantly predicts y.

t
=
R
n
−
2
1
−
R
2
A line graph presents a negative linear relationship between self reported depression and resilience. The line graph presents a regression line representing the relationship between self reported depression and resilience. The horizontal axis is labeled x as Self reported Depression and ranges from 0 to 20. The vertical axis is labeled y as Resilience and ranges from 2 to 5. The graph displays a downward sloping line with the regression equation y equals negative 0.104 x plus 4.269 placed near the center. The graph visually indicates that as self reported depression increases, resilience scores tend to decrease.
FIG. 30.1 ■
REGRESSION LINE REPRESENTED BY NEW REGRESSION EQUATION.

To know whether the predictor significantly predicts y, the b must be tested against zero. In simple regression, this is most easily accomplished by using the R value from Step 4:

t
=
0.61
20
−
2
1
−
0.371
t
=
0.61
(
5.35
)
t
=
3.26
The t value is then compared with the t probability distribution table (see Appendix A ). The degrees of freedom ( df ) for this t statistic is n −2. The critical t value at alpha (α) = 0.05, df = 18 is 2.101, rounded to 2.10 for a two-tailed test. Our obtained t was 3.26, which exceeds the critical value in the table, thereby indicating a significant association between the predictor ( x ) and outcome ( y ).

Step 6: Calculate R 2 .

After establishing the statistical significance of the R value, it must subsequently be examined for clinical importance. This is accomplished by obtaining the coefficient of determination for regression—which simply involves squaring the R value. The R 2 represents the percentage of variance explained in y by the predictor. Cohen describes R 2 values of 0.02 as small, 0.13 as moderate, and 0.26 or higher as large effect sizes ( Cohen, 1988 ). In our example, the R was 0.609, and, therefore, the R 2 was 0.371. Multiplying 0.371 × 100% indicates that 37.10% of the variance in resilience levels can be explained by knowing the participant’s depression score ( Cohen & Cohen, 1983 ).

The R 2 can be very helpful in testing more than one predictor in a regression model. Unlike R , the R 2 for one regression model can be compared with another regression model that contains additional predictors ( Cohen & Cohen, 1983 ). The R 2 is discussed further in Exercise 31 .

The standardized beta (β) is another statistic that represents the magnitude of the association between x and y . The standardized beta has limits just like a Pearson r, meaning that the standardized beta cannot be lower than −1.00 or higher than +1.00. This value can be calculated by hand but is best computed with statistical software. The standardized beta is calculated by converting the x and y values to z scores and then correlating the x and y value using the Pearson r formula, located in Exercise 29 . The standardized beta (β) is often reported in the literature instead of the unstandardized beta ( b ), because the unstandardized beta does not have lower or upper limits and therefore the magnitude of the unstandardized beta cannot be judged. The standardized beta, on the other hand, is interpreted as a Pearson r and the descriptions of the magnitude of the standardized beta can be applied, as recommended by Cohen (1988) . In this example, the standardized beta is −0.609. Thus the magnitude of the association between x and y in this example is considered a large predictive association ( Cohen, 1988 ; Tabachnick & Fidell, 2019 ).

SPSS computations
This is how our dataset looks in SPSS.


A spreadsheet interface shows participant data with I D, P H Q scores, and B R S scores. The spreadsheet interface displays participant data in a tabular format with three labeled columns I D, P H Q, and B R S. The I D column lists participant numbers from 1 to 16. The P H Q column shows self reported scores ranging from 1.00 to 19.00. The BRS column contains resilience scores ranging from 1.83 to 4.67. Each row corresponds to one participant’s data entry. The top menu includes options such as File, Edit, View, Data, Transform, Analyze, and Graphs, along with standard tool icons for file handling and navigation. The interface is part of statistical analysis software.

Step 1: From the “Analyze” menu, choose “Regression” and “Linear.”


A linear regression window interface assigns Brief Resilience Scale Score as dependent and Patient Health Questionnaire as independent variable. The linear regression window interface shows two variables on the left I D and Patient Health Questionnaire. The variable Brief Resilience Scale Score appears in the dependent field, while Patient Health Questionnaire is listed in the independent field. The Method dropdown menu is set to Enter. Other sections include Selection Variable, Case Labels, and W L S Weight, all of which are empty. On the right side, there are six buttons labeled Statistics, Plots, Save, Options, Style, and Bootstrap. At the bottom are six action buttons labeled O K, Paste, Reset, Cancel, and Help. The interface is part of statistical software used for conducting linear regression analysis.

Step 2: Move the predictor, PHQ (depression), to the space labeled “Independent(s).” Move the dependent variable, BRS (resilience), to the space labeled “Dependent.” Click “OK.”

Interpretation of SPSS output
The following tables are generated from SPSS. The first table contains the multiple R and the R 2 values. The multiple R is 0.609, indicating that the correlation between the actual y values and the predicted y values using the new regression equation is 0.609. The R 2 is 0.371, indicating that 37.10% of the variance in resilience levels can be explained by knowing the participant’s depression score.


A regression model summary table presents R, R Square, Adjusted R Square, and standard error values for a linear analysis. The regression output shows a model summary table with statistical values for a linear regression analysis. The table has five columns labeled Model, R, R Square, Adjusted R Square, and Standard Error of the Estimate. For Model 1, the value of R is 0.609, R Square is 0.371, Adjusted R Square is 0.336, and the standard error of the estimate is 0.72485. A note below the table states that the predictors include Constant and Patient Health Questionnaire Depression Score. The table summarizes the strength and fit of the regression model.
The second table contains the analysis of variance (ANOVA) table. As presented in Exercises 18 and 35 , the ANOVA is usually performed to test for differences between group means. However, ANOVA can also be performed for regression, where the null hypothesis is that knowing the value of x explains no information about y . This table indicates that knowing the value of x explains a significant amount of variance in y . The contents of the ANOVA table are rarely reported in published articles, because the significance of each predictor is presented in the last SPSS table titled “Coefficients” (see below).

An A N O V A table presents regression analysis values for Brief Resilience Scale Score based on depression scores. The A N O V A table displays statistical values for a regression model using Brief Resilience Scale Score as the dependent variable and Patient Health Questionnaire Depression Score as the predictor. The table includes three rows labeled Regression, Residual, and Total, and five columns labeled Sum of Squares, Degrees of Freedom, Mean Square, F, and Significance. For the regression row, the values are 5.581 for Sum of Squares, 1 for Degrees of Freedom, 5.581 for Mean Square, 10.622 for F, and 0.004 for Significance. The residual row shows 9.457 for Sum of Squares, 18 for Degrees of Freedom, and 0.525 for Mean Square. The total row includes 15.039 for Sum of Squares and 19 for Degrees of Freedom. A note below the table confirms the dependent variable is Brief Resilience Scale Score, and the predictor is Patient Health Questionnaire Depression Score.
The third table contains the unstandardized beta and a values, standardized beta, t, and exact p value. The a is listed in the first row, next to the label “Constant.” The standardized beta is listed in the second row, next to the name of the predictor. The remaining information that is important to extract when interpreting regression results can be found in the second row. The standardized beta is −0.609. This value has limits just like a Pearson r, meaning that the standardized beta cannot be lower than −1.00 or higher than +1.00. The t value is −3.259, and the exact p value is 0.004.

A coefficients table presents regression values for the Brief Resilience Scale Score using depression score as predictor. The coefficients table from a regression analysis shows values for the constant and the Patient Health Questionnaire Depression Score as predictors of the dependent variable Brief Resilience Scale Score. The table has six columns labeled Model, Unstandardized Coefficients B, Standard Error, Standardized Coefficients Beta, t, and Significance. For Model 1, the constant has a B value of 4.269, a standard error of 0.311, a t value of 13.707, and a significance value less than 0.001. The depression score has a B value of negative 0.104, a standard error of 0.032, a beta value of negative 0.609, a t value of negative 3.260, and a significance value of 0.004. The table summarizes the contribution of each variable in predicting resilience.
Final interpretation in American Psychological Association format
The following interpretation is written as it might appear in a research article, formatted according to American Psychological Association (APA) guidelines ( APA, 2020 ). It should be noted that all statistical values reported here are rounded to two decimal places, with the exception of the p value, which is rounded to three decimal places.

Simple linear regression was performed with newly licensed RNs’ level of depression as the predictor and resilience as the dependent variable. The nurses’ depression levels significantly predicted their levels of resilience, β = −0.61, p = 0.004, and R 2 = 37.10%. Higher levels of depression significantly predicted lower levels of resilience among newly licensed RNs.

Study questions

1.
If you have access to SPSS, compute the Shapiro-Wilk test of normality for BRS (resilience) as demonstrated in Exercise 27 . If you do not have access to SPSS, plot the frequency distributions by hand. What do the results indicate?

2.
State the null hypothesis for the example where depression levels were tested as a predictor of resilience among newly licensed RNs.

3.
In the formula y = bx + a , what does b represent?

4.
In the formula y = bx + a , what does a represent?

5.
Using the new regression equation, ŷ = −0.104 x + 4.27, compute the predicted BRS (resilience) score if a RN’s PHQ (depression) score is 1. Show your calculations.

6.
Using the new regression equation, ŷ = −0.104 x + 4.27, compute the predicted BRS (resilience) score if a RN’s PHQ (depression) score is 13. Show your calculations.

7.
What is the correlation between the actual y values and the predicted ŷ values using the new regression equation in the example?

8.
What is the exact likelihood of obtaining a t value at least as extreme as or as close to the one that was actually observed, assuming that the null hypothesis is true?

9.
How much variance in resilience levels is explained by knowing the participant’s depression score?

10.
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


