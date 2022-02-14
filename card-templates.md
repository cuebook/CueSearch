# Card Templates

Card templates are written using [Django Templates](https://docs.djangoproject.com/en/4.0/topics/templates/) (similar to [Jinja](https://jinja.palletsprojects.com/en/2.10.x/templates/)).&#x20;

On search, the query is mapped to various `datasets` it is applicable on. It is then passed to  various templates with certain parameters.&#x20;

A template consists of card `title`, `text`, `sql` and `renderType`. These variables are defined using [Django Templates](https://docs.djangoproject.com/en/4.0/topics/templates/) where you'll have access to these parameters (case sensitive) :&#x20;

* granularity - granularity of the dataset, either "day" or "hour"&#x20;
* datasetSql - original SQL of the dataset&#x20;
* timestampColumn - timestamp column name in dataset
* metrics - a list of metrics in dataset
* dimensions - a list of dimensions in dataset
* dataset - dataset on which template will run&#x20;
* renderType - type of view, either "line" or "table"&#x20;
* filterDimensions - list of dimensions on which filter is applied&#x20;
* filter - filter in SQL format \`(Brand = "Adidas" OR Brand = "Puma")
*   searchResults - a list of dictionary of selected query items, dictionary looks like -&#x20;

    &#x20;                  { 'dimension': 'Brand', 'value': 'Adidas' }

**Note:** Sql delimiter in template is `+-;`

### Sample Templates

Some sample templates are already added on installation

```
{% raw %}
{% load event_tags %} 
{% for filterDim in filterDimensions %} 
	{% conditionalCount searchResults 'dimension' filterDim as dimCount %} 
	{% if dimCount > 1 %} 
		{% for metricName in metrics %} 
			SELECT ({{ timestampColumn }}), {{ filterDim }}, SUM({{ metricName }}) as {{metricName}} FROM ({{ datasetSql|safe }}) WHERE {{filter|safe}} GROUP BY 1, 2 limit 500 +-; 
		{% endfor %} 
	{% endif %} 
{% endfor %}
{% endraw %}
```

The above template results to multiple cards depending on parameters passed.
