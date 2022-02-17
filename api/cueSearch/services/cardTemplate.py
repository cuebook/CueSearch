from typing import Dict
from utils.apiResponse import ApiResponse
from django.template import Template, Context
from cueSearch.serializers import SearchCardTemplateSerializer
from cueSearch.models import SearchCardTemplate
from dataset.services import Datasets


class CardTemplates:
    '''
    Service to create, read, update & delete operation on card template
    '''
    @staticmethod
    def createCardTemplate(payload: dict):
        """Method to create card template"""
        res = ApiResponse('Error occur while creating card template')
        try:
            renderType = "table"
            templateName = payload['templateName']
            title = payload['title']
            bodyText = payload['bodyText']
            sql = payload['sql']
            published = True

            data = SearchCardTemplate(
                templateName=templateName,
                title = title,
                bodyText = bodyText,
                sql = sql,
                renderType = renderType
                )
            data.save()
            res.update(True,"Card template created successfully",data)
        except Exception as ex:
            res.update('Exception occured while creating card template')
        return res

    @staticmethod
    def getcardTemplate():
        """Method to fetch all card templates"""
        res = ApiResponse("Error in fetching card templates")
        try:
            templates = SearchCardTemplate.objects.all()
            data = SearchCardTemplateSerializer(templates, many=True).data
            res.update(True, "Fetched card templates", data)

        except Exception as ex:
            res.update(False, [])
        return res

    def updateCardTemplate(id, payload):
        try:
            res = ApiResponse()

            renderType = "table"
            templateName = payload['templateName']
            title = payload['title']
            bodyText = payload['bodyText']
            sql = payload['sql']
            published = True

            targetTemplate = SearchCardTemplate.objects.get(id=id)
            newId = targetTemplate.id
            targetTemplate.delete()
            updatedTemplate = SearchCardTemplate(
                    id=newId,
                    templateName=templateName,
                    title = title,
                    bodyText = bodyText,
                    sql = sql,
                    renderType = renderType,
                    published = published
                )
            updatedTemplate.save()

        except Exception as ex:
            res.update(False, [])
        return res

    def deleteCardTemplate(id):
        """Method to delete card template"""
        res = ApiResponse()
        try:
            instance = SearchCardTemplate.objects.get(id=id)
            instance.delete()
            res.update(True,"Card template deleted successfully")
        except Exception as ex:
            res.update(False,"Error occured while deleting card template")
        return res

    @staticmethod
    def getcardTemplateById(id):
        """Method to fetch all card templates"""
        res = ApiResponse("Error in fetching card templates")
        try:
            templates = SearchCardTemplate.objects.filter(id=id)
            data = SearchCardTemplateSerializer(templates, many=True).data
            res.update(True, "Fetched card templates", data)

        except Exception as ex:
            res.update(False, [])
        return res

    @staticmethod
    def publishedCardTemplate(payload):
        try:
            res = ApiResponse()
            published = payload.get("published",False)
            id =  payload['id']
            templates =  SearchCardTemplate.objects.filter(id=id).update(published=True)
            res.update(True,"Card Template updated successfully")
        except Exception as ex:
            res.update(False,"Error occured while updating Card Template")
