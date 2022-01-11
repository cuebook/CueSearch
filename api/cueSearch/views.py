import json
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpRequest
from cueSearch.services import GlobalDimensionServices

# Create your views here.
class DimensionView(APIView):
    def get(self, request):
        """Get Dimension"""
        # res = search.SearchUtils.getAllDimensions()
        # return Response(res.json())
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
