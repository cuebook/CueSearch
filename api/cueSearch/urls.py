"""
Contains urls mapped with CueSearch app views
"""
from django.urls import path
from . import views

urlpatterns = [
    # Global Dimension
    path("dimension/", views.DimensionView.as_view(), name="dimension"),
    # path("metrics/", views.MetricsView.as_view(), name="metrics"),
    path(
        "global-dimension/", views.GlobalDimensionView.as_view(), name="globalDimension"
    ),
    path(
        "global-dimension/create/",
        views.GlobalDimensionView.as_view(),
        name="globalDimensionCreate",
    ),
    path(
        "global-dimension/delete/<int:id>",
        views.GlobalDimensionView.as_view(),
        name="global-dimension-delete",
    ),
    path(
        "global-dimension/publish", views.pubGlobalDimension, name="pubGlobalDimension"
    ),
    path(
        "global-dimension/<int:id>", views.globalDimensionById, name="globalDimensionId"
    ),
    path(
        "global-dimension/update/<int:id>",
        views.updateGlobalDimension,
        name="updateGlobalDimension",
    ),
    # Card Templates
    path("cardTemplates/", views.getCardTemplates, name="getCardTemplate"),
    path("getSearchCards/", views.getSearchCards, name="getSearchCards"),
    path("getSearchCardData/", views.getSearchCardData, name="getSearchCardData"),
    path(
        "searchsuggestions/",
        views.getSearchSuggestionsView,
        name="getSearchSuggestionsView",
    ),
    path("runIndexing/", views.elasticSearchIndexingView, name="runIndexing"),
    # Custom Card Templates
    # path("createTemplates/", views.createCardTemplates, name="createCardTemplates"),
    path("card-templates/", views.getTemplates, name="getTemplates"),
    path(
        "card-templates/create/", views.createCardTemplates, name="createCardTemplates"
    ),
]
