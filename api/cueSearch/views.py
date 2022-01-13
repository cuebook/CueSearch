
import json
from django.shortcuts import render
from utils.apiResponse import ApiResponse
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpRequest
from cueSearch.services import GlobalDimensionServices, SearchCardTemplateServices
from cueSearch.elasticSearch import ESIndexingUtils, ESQueryingUtils

# Create your views here.
class DimensionView(APIView):
    def get(self, request):
        """Get Dimension"""
        res = GlobalDimensionServices.getDimension()
        return Response(res.json())

class  GlobalDimensionView(APIView):
    def get(self, request):
        res = GlobalDimensionServices.getGlobalDimensions()
        return Response(res.json())
    def post(self, request):
        payloads = request.data
        res = GlobalDimensionServices.createGlobalDimension(payloads)
        return Response(res.json())
    def delete(self, request, id):
        print("id", type(id))
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
def globalDimensionById(request: HttpRequest,id) -> Response:
    res = GlobalDimensionServices.getGlobalDimensionById(id)
    return Response(res.json())


@api_view(["POST"])
def updateGlobalDimension(request: HttpRequest, id) -> Response:
    payload = request.data
    res = GlobalDimensionServices.updateGlobalDimensionById(id, payload)
    return Response(res.json())

# from elasticSearch import ESIndexingUtils

# @app.route("/search/cardTemplates/", methods=["GET"])
@api_view(["GET"])
def getCardTemplates(request: HttpRequest) -> Response:
    res = SearchCardTemplateServices.getCardTemplates()
    return Response(res.json())


# @app.route("/search/getCards/", methods=['POST'])
@api_view(["POST"])
def getSearchCards(request: HttpRequest) -> Response:
    payload = request.data
    res = SearchCardTemplateServices.getSearchCards(payload)
    return Response(res.json())



# @app.route("/search/searchsuggestions/", methods=['POST'])
@api_view(["POST"])
def getSearchSuggestionsView(request: HttpRequest) -> Response:
    searchQuery = request.data
    res = SearchCardTemplateServices.getSearchSuggestions(searchQuery)
    return Response(res.json())



# @app.route("/search/runIndexing/", methods=['GET'])
@api_view(["GET"])
def elasticSearchIndexingView(request: HttpRequest)-> Response:
    res = ApiResponse("Indexing is not completed !")
    ESIndexingUtils.indexGlobalDimensionsDataForSearchSuggestion() # Used for search suggestion
    ESIndexingUtils.indexGlobalDimensionName()
    ESIndexingUtils.indexGlobalDimensionsData()
    res.update(True, "Indexing completed !", [])
    # res = {"success":True, "message":"indexing completed !"}
    return Response(res.json())
    # return jsonify(res)

# class DimValsView(APIView):
#     def post(self, request):
#         payload = request.data
#         res = GlobalDimensionServices.getDimValues(payload)
#         return Response(res.json())
