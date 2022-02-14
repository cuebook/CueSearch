# Datasets

Datasets are similar to aggregated SQL VIEWS of your data. When you run an anomaly detection job, the associated dataset's SQL query is run and the results are stored as a Pandas dataframe in memory.

![](.gitbook/assets/DATASET\_SQL\_VIEW.png)

You write a SQL GROUP BY query with aggregate functions to roll-up your data. You then map the columns as dimensions or measures.

![](.gitbook/assets/Dataset\_map\_table.png)

1. Dataset must have only one timestamp column. This timestamp column is used to generate chart for card.
2. Dataset can have one or more dimension columns.

## SQL GROUP BY Query

Your SQL must group by timestamp and all dimension columns. You must truncate the timestamp column to HOUR or DAY before grouping. For example, if you want to track hourly anomalies on the dataset, truncate the timestamp to HOUR.

Below is a sample GROUP BY query for Druid.&#x20;

```sql
SELECT DATE_TRUNC('DAY', __time) as OrderDate,
Brand, Color, State,
SUM("count") as Orders, ROUND(sum(OrderAmount),2) as OrderAmount, sum(OrderQuantity) as OrderQuantity
FROM FAKEORDERS
WHERE __time >= CURRENT_TIMESTAMP - INTERVAL '13' MONTH 
GROUP BY 1, 2, 3, 4
ORDER BY 1
```
