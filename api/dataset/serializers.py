import json
import dateutil.parser as dp
import datetime as dt
from dataset.settingDetails import settingDicts
from rest_framework import serializers
from dataset.models import Connection,ConnectionType, Dataset, Setting

class ConnectionSerializer(serializers.ModelSerializer):
    connectionTypeId = serializers.SerializerMethodField()
    connectionType = serializers.SerializerMethodField()
    datasetCount = serializers.SerializerMethodField()


    def get_connectionTypeId(self, obj):
        return obj.connectionType.id

    def get_connectionType(self, obj):
        return obj.connectionType.name

    def get_datasetCount(self, obj):
        connectionId = obj.id
        datasetCount = Dataset.objects.filter(connection_id = connectionId).count()
        return datasetCount

    class Meta:
        model = Connection
        fields = [
            "id",
            "name",
            "description",
            "connectionTypeId",
            "connectionType",
            "datasetCount"
        ]


class ConnectionDetailSerializer(serializers.ModelSerializer):
    params = serializers.SerializerMethodField()
    connectionTypeId = serializers.SerializerMethodField()
    connectionType = serializers.SerializerMethodField()

    def get_params(self, obj):
        params = {}
        for val in obj.cpvc.all():
            params[val.connectionParam.name] = val.value if not val.connectionParam.isEncrypted else "**********"
        return params

    def get_connectionTypeId(self, obj):
        return obj.connectionType.id

    def get_connectionType(self, obj):
        return obj.connectionType.name

    class Meta:
        model = Connection
        fields = [
            "id",
            "name",
            "description",
            "params",
            "connectionTypeId",
            "connectionType",
        ]


class ConnectionTypeSerializer(serializers.ModelSerializer):
    
    params = serializers.SerializerMethodField()

    def get_params(self, obj):
        paramList = []
        for param in obj.connectionTypeParam.all():
            params = {}
            params["id"] = param.id
            params["name"] = param.name
            params["label"] = param.label
            params["isEncrypted"] = param.isEncrypted
            params["properties"] = param.properties
            paramList.append(params)
        return paramList

    class Meta:
        model = ConnectionType
        fields = ["id", "name", "params"]


class DatasetsSerializer(serializers.ModelSerializer):
    """
    Serializes data related to anomaly tree 
    """
    connection = ConnectionSerializer()
    anomalyDefinitionCount = serializers.SerializerMethodField()
    connectionName = serializers.SerializerMethodField()
    def get_connectionName(self, obj):
        """
        Gets connection name
        """
        return obj.connection.name

    class Meta:
        model = Dataset
        fields = ['id', 'name', 'granularity', 'connection',"connectionName"]


class DatasetSerializer(serializers.ModelSerializer):
    """
    Serializes data related to anomaly tree 
    """
    connection = ConnectionSerializer()
    dimensions = serializers.SerializerMethodField()
    metrics = serializers.SerializerMethodField()


    def get_dimensions(self, obj):
        dimensions = json.loads(obj.dimensions) if obj.metrics else []
        return dimensions if dimensions else []

    def get_metrics(self, obj):
        metrics = json.loads(obj.metrics) if obj.metrics else []
        return metrics if metrics else []

    class Meta:
        model = Dataset
        fields = ['id', 'name', 'sql', 'connection', 'dimensions', 'metrics', 'granularity', 'timestampColumn']



class SettingSerializer(serializers.ModelSerializer):
    """
    Serializer for the model Setting
    """
    details = serializers.SerializerMethodField()
    def get_details(self, obj):
        """ Details for settings UI"""
        settingdicts = settingDicts()
        for settingdict in settingdicts:
            if obj.name == settingdict["name"]:
                return settingdict

    class Meta:
        model = Setting
        fields = ["name", "value", "details"]






