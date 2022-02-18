import logging
from utils.apiResponse import ApiResponse
from cueSearch.serializers import SearchCardTemplateSerializer
from cueSearch.models import SearchCardTemplate


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

            cardTemplateObj = SearchCardTemplate.objects.create(
                templateName=templateName,
                title=title,
                bodyText=bodyText,
                sql=sql,
                renderType=renderType,
            )
            res.update(True, "Search card template created successfully")
        except Exception as ex:
            logging.error("Error %s", str(ex))
            res.update(False, "Exception occured while creating templates")
        return res

    @staticmethod
    def getCardTemplates():
        """
        Service to fetch all card templates
        """
        res = ApiResponse("Error in fetching card templates")
        try:
            templates = SearchCardTemplate.objects.all().order_by("-id")
            data = SearchCardTemplateSerializer(templates, many=True).data
            res.update(True, "Fetched card templates", data)

        except Exception as ex:
            logging.error("Error %s", str(ex))
            res.update(False, "Error while fetching card templates")
        return res

    def updateCardTemplate(id: int, payload: dict):
        """Method to update card template"""
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

    @staticmethod
    def publishedCardTemplate(payload: dict):
        """Method to publish/unpublish card template"""
        try:
            res = ApiResponse()
            published = payload.get("published", False)
            id = payload.get("id", None)
            if id:
                templates = SearchCardTemplate.objects.get(id=id)
                templates.published = published
                templates.save()
                res.update(True, "Card Template published successfully")
        except Exception as ex:
            logging.error("Error %s", str(ex))
            res.update(False, "Error occured while publishing Card Template")
        return res

    def deleteCardTemplate(id: int):
        """Method to delete card template"""
        res = ApiResponse()
        try:
            instance = SearchCardTemplate.objects.get(id=id)
            instance.delete()
            res.update(True, "Card template deleted successfully")
        except Exception as ex:
            logging.error("Error while deleting %s", str(ex))
            res.update(False, "Error occured while deleting card template")
        return res

    @staticmethod
    def getCardTemplateById(id: int):
        """Method to fetch card templates by Id"""
        res = ApiResponse("Error in fetching card templates")
        try:
            templates = SearchCardTemplate.objects.filter(id=id)
            data = SearchCardTemplateSerializer(templates).data
            res.update(True, "Fetched card templates", data)
        except Exception as ex:
            logging.error("Error while get card template by Id %s", str(ex))
            res.update(False, "Error occured while getting template by id")
        return res
