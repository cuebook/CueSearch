from typing import Dict
from utils.apiResponse import ApiResponse
from django.template import Template, Context
from cueSearch.serializers import SearchCardTemplateSerializer
from cueSearch.models import SearchCardTemplate
from dataset.models import Dataset
from cueSearch.elasticSearch import ESQueryingUtils, ESIndexingUtils
from dataset.services import Datasets


class CardTemplates:
    '''
    Service to create, read, update & delete operation on Search card template
    '''
    @staticmethod
    def createSearchCardTemplate(payload: dict):
        '''
        Create search card template
        '''
        try:
            res = ApiResponse('Error occur while creating search card template')
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
            res.update(True,"Search card template created successfully",data)
        except Exception as ex:
            res.update('Exception occured while creating templates')
        return res

    @staticmethod
    def getCardTemplates():
        """
        Service to fetch all card templates
        """
        res = ApiResponse("Error in fetching card templates")
        try:
            templates = SearchCardTemplate.objects.all()
            data = SearchCardTemplateSerializer(templates, many=True).data
            res.update(True, "Fetched card templates", data)

        except Exception as ex:
            res.update(False, [])
        return res

    def updateSearchCardTemplate(id, payload):
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
            pass

    def deleteSearchCardTemplate():
        pass
