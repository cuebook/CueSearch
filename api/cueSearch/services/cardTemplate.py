import logging
from utils.apiResponse import ApiResponse
from cueSearch.serializers import SearchCardTemplateSerializer
from cueSearch.models import SearchCardTemplate
from dataset.models import ConnectionType
from django.template import Template, Context

logger = logging.getLogger(__name__)

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
            connectionTypeId = int(payload.get("connectionTypeId", 1))
            connectionType = ConnectionType.objects.get(id=connectionTypeId)
            renderType = payload.get("renderType", "table")
            templateName = payload.get("templateName", "")
            title = payload.get("title", "")
            bodyText = payload.get("bodyText", "")
            sql = payload.get("sql", "")

            cardTemplateObj = SearchCardTemplate.objects.create(
                templateName=templateName,
                title=title,
                bodyText=bodyText,
                sql=sql,
                renderType=renderType,
                connectionType=connectionType,
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

    def updateCardTemplate(templateId: int, payload: dict):
        """Method to update card template"""
        try:
            res = ApiResponse("Error while updating card template")
            connectionTypeId = int(payload.get("connectionTypeId"))
            connectionType = ConnectionType.objects.get(id=connectionTypeId)
            renderType = payload.get("renderType", "table")
            templateName = payload.get("templateName", "")
            title = payload.get("title", "")
            bodyText = payload.get("bodyText", "")
            sql = payload.get("sql", "")
            published = payload.get("published", False)
            templateObj = SearchCardTemplate.objects.get(id=templateId)
            templateObj.published = published
            templateObj.sql = sql
            templateObj.bodyText = bodyText
            templateObj.title = title
            templateObj.templateName = templateName
            templateObj.renderType = renderType
            templateObj.connectionType = connectionType
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
            templateId = payload.get("id", None)
            if templateId:
                templates = SearchCardTemplate.objects.get(id=templateId)
                templates.published = published
                templates.save()
                res.update(True, "Card Template published successfully")
        except Exception as ex:
            logging.error("Error %s", str(ex))
            res.update(False, "Error occured while publishing Card Template")
        return res

    def deleteCardTemplate(templateId: int):
        """Method to delete card template"""
        res = ApiResponse()
        try:
            instance = SearchCardTemplate.objects.get(id=templateId)
            instance.delete()
            res.update(True, "Card template deleted successfully")
        except Exception as ex:
            logging.error("Error while deleting %s", str(ex))
            res.update(False, "Error occured while deleting card template")
        return res

    @staticmethod
    def getCardTemplateById(templateId: int):
        """Method to fetch card templates by Id"""
        res = ApiResponse("Error in fetching card templates")
        try:
            templates = SearchCardTemplate.objects.get(id=templateId)
            data = SearchCardTemplateSerializer(templates).data
            res.update(True, "Fetched card templates", data)
        except Exception as ex:
            logging.error("Error while get card template by Id %s", str(ex))
            res.update(False, "Error occured while getting template by id")
        return res

    @staticmethod
    def verifyCardTemplate(param: dict):
        response = []
        delimiter = "+-;"
        try:
            sqls = (
                Template(param["templateSql"]).render(Context(param)).split(delimiter)
            )
            for i in range(len(sqls)):
                if str.isspace(sqls[i]):
                    continue
                response.append({"sql": sqls[i]})

        except Exception as ex:
            logger.error("Error in rendering templates: %s", str(ex))
            logger.error(param)