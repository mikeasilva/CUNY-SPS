-- Hands On Lab 2-2: Export SQL data to a CSV file

/*
THE TASK:

Specifically, we want to export a .CSV file that contains total tuberculosis cases by
country by year. So we need to do some data transformation work in SQL to get
our SELECT statement how we want it, then wrap the SELECT statement into a
statement that exports the data to a .CSV file. Then we load the .CSV file into
Excel.
*/

SELECT 
    `country`, `year`, SUM(child + adult + elderly) AS `cases`
FROM
    `tb`
GROUP BY `country`, `year`
HAVING `cases` IS NOT NULL
INTO OUTFILE '/var/lib/mysql-files/tb_export.csv'
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n';