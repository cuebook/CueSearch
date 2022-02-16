import json
from rest_framework import serializers
from dataset.models import Dataset
from cueSearch.models import GlobalDimension, SearchCardTemplate


class AllDimensionsSerializer(serializers.ModelSerializer):
    """
    Serializes data to get all dimensions
    """

    connectionName = serializers.SerializerMethodField()
    dimensions = serializers.SerializerMethodField()

    def get_connectionName(self, obj):
        """
        Gets connection name
        """
        return obj.connection.name

    def get_dimensions(self, obj):
        dimensions = json.loads(obj.dimensions) if obj.dimensions else []
        return dimensions if dimensions else []

    class Meta:
        model = Dataset
        fields = ["id", "name", "connectionName", "dimensions", "granularity"]


class AllMeticsSerializer(serializers.ModelSerializer):
    """
    Serializes data to get all metrics
    """

    connectionName = serializers.SerializerMethodField()
    metrics = serializers.SerializerMethodField()

    def get_connectionName(self, obj):
        """
        Gets connection name
        """
        return obj.connection.name

    def get_metrics(self, obj):
        metrics = json.loads(obj.metrics) if obj.metrics else []
        return metrics if metrics else []

    class Meta:
        model = Dataset
        fields = ["id", "name", "connectionName", "metrics", "granularity"]


class GlobalDimensionSerializer(serializers.ModelSerializer):
    """
    Serializers for get Global dimensions
    """

    values = serializers.SerializerMethodField()

    def get_values(self, obj):
        paramsList = []
        gdValues = obj.globaldimensionvalues_set.all()
        for gdValue in gdValues:
            params = {}
            datasetId = gdValue.dataset.id
            dataset = gdValue.dataset.name
            id = gdValue.id
            dimension = gdValue.dimension
            params["datasetId"] = datasetId
            params["dataset"] = dataset
            params["id"] = id
            params["dimension"] = dimension
            paramsList.append(params)
        return paramsList

    class Meta:
        model = GlobalDimension
        fields = ["id", "name", "published", "values"]


class SearchCardTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchCardTemplate
        fields = [
            "id",
            "templateName",
            "title",
            "bodyText",
            "sql",
            "published",
        ]
