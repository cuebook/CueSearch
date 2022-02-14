import logging
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpRequest
from cueSearch.services import GlobalDimensionServices, SearchCardTemplateServices
from cueSearch.elasticSearch import ESIndexingUtils
from utils.apiResponse import ApiResponse


# Create your views here.
class DimensionView(APIView):
    """
    Method to get all dimension
    """

    def get(self, request):
        """Get Dimension"""
        res = GlobalDimensionServices.getDimension()
        return Response(res.json())


class GlobalDimensionView(APIView):
    """Global Dimesion views"""

    def get(self, request):
        """Method to get global dimensions"""
        res = GlobalDimensionServices.getGlobalDimensions()
        return Response(res.json())

    def post(self, request):
        """Method to create global diensions"""
        payloads = request.data
        res = GlobalDimensionServices.createGlobalDimension(payloads)
        return Response(res.json())

    def delete(self, request, id):
        """Method to delete global diemension"""
        res = GlobalDimensionServices.deleteGlobalDimension(id)
        return Response(res.json())


@api_view(["POST"])
def pubGlobalDimension(request: HttpRequest) -> Response:
    """
    Method for run Publish global dimension
    :param request: HttpRequest
    """
    payload = request.data
    res = GlobalDimensionServices.publishGlobalDimension(payload)
    return Response(res.json())


@api_view(["GET"])
def globalDimensionById(request: HttpRequest, id) -> Response:
    """Method to get global dimension by Id"""
    res = GlobalDimensionServices.getGlobalDimensionById(id)
    return Response(res.json())


@api_view(["POST"])
def updateGlobalDimension(request: HttpRequest, id) -> Response:
    """Method to update global dimension"""
    payload = request.data
    res = GlobalDimensionServices.updateGlobalDimensionById(id, payload)
    return Response(res.json())


@api_view(["GET"])
def getCardTemplates(request: HttpRequest) -> Response:
    """Method to get card templates"""
    res = SearchCardTemplateServices.getCardTemplates()
    return Response(res.json())


@api_view(["POST"])
def getSearchCards(request: HttpRequest) -> Response:
    """Method to get search cards"""
    payload = request.data
    res = SearchCardTemplateServices.getSearchCards(payload)
    return Response(res.json())


@api_view(["POST"])
def getSearchCardData(request: HttpRequest) -> Response:
    """Method to get data for search card"""
    params = request.data
    res = SearchCardTemplateServices.getSearchCardData(params)
    return Response(res.json())


@api_view(["POST"])
def getSearchSuggestionsView(request: HttpRequest) -> Response:
    """Method to get search suggestion"""
    searchQuery = request.data
    res = SearchCardTemplateServices.getSearchSuggestions(searchQuery)
    return Response(res.json())


@api_view(["GET"])
def elasticSearchIndexingView(request: HttpRequest) -> Response:
    """Method to index elastic search via api call"""
    res = ApiResponse("Indexing is not completed !")
    logging.info(
        "********************** Indexing Starts via API Call !**********************"
    )
    ESIndexingUtils.indexGlobalDimensionsDataForSearchSuggestion()  # Used for search suggestion
    ESIndexingUtils.indexNonGlobalDimensionsDataForSearchSuggestion()  # Used for index auto global dimension
    # ESIndexingUtils.indexGlobalDimensionName()
    ESIndexingUtils.indexGlobalDimensionsData()
    logging.info("************** Indexing Completed !****************")
    res.update(True, "Indexing completed !", [])
    return Response(res.json())
