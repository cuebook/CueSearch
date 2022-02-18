import logging
from typing import Dict
from utils.apiResponse import ApiResponse
from django.template import Template, Context
from cueSearch.serializers import SearchCardTemplateSerializer
from cueSearch.models import SearchCardTemplate
from dataset.models import Dataset
from cueSearch.elasticSearch import ESQueryingUtils, ESIndexingUtils
from dataset.services import Datasets


class CardTemplates:
    """
    Service to create, read, update & delete operation on Search card template
    """

    @staticmethod
    def createCardTemplate(payload: dict):
        """
        Create search card template
        """
        try:
            res = ApiResponse("Error occur while creating search card template")
            renderType = payload["renderType"]
            templateName = payload["templateName"]
            title = payload["title"]
            bodyText = payload["bodyText"]
            sql = payload["sql"]
            # published = True

            cardTemplateObj = SearchCardTemplate.objects.create(
                templateName=templateName,
                title=title,
                bodyText=bodyText,
                sql=sql,
                renderType=renderType,
            )
            res.update(True, "Search card template created successfully")
        except Exception as ex:
            res.update(False, "Exception occured while creating templates")
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

    def updateCardTemplate(id, payload):
        try:
            res = ApiResponse("Error while updating card template")

            renderType = payload.get("renderType", "table")

            templateName = payload.get("templateName", "")
            title = payload.get("title", "")
            bodyText = payload.get("bodyText", "")
            sql = payload.get("sql", "")
            published = payload.get("published", False)

            templateObj = SearchCardTemplate.objects.get(id=id)
            templateObj.published = published
            templateObj.sql = sql
            templateObj.bodyText = bodyText
            templateObj.title = title
            templateObj.templateName = templateName
            templateObj.renderType = renderType
            templateObj.save()
            res.update(True, "Successfully updated template")
        except Exception as ex:
            logging.error("Error %s", str(ex))
            res.update(False, "Error while updating template")
        return res

    def deleteSearchCardTemplate():
        pass
