"""
Contains urls mapped with Anomalys app views
"""
from django.urls import path
from . import views

urlpatterns = [
    # Datasets
    path("datasets", views.DatasetsView.as_view(), name="datasets"),
    path("dataset/<int:datasetId>", views.DatasetView.as_view(), name="dataset"),
    path("dataset/create", views.CreateDatasetView.as_view(), name="createDataset"),
    # Connections
    path("connections", views.connections, name="connections"),
    path("connection/<int:connection_id>", views.connection, name="connection"),
    path("connectiontypes", views.connectionTypes, name="connectionTypes"),
    # Settings
    path("settings", views.SettingsView.as_view(), name="settings"),
    # Installtion
    #path("installationId", views.InstallationView.as_view(), name="installationId" )
]
