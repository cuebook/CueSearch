# from requests.models import Response
import traceback

# from search import app, db
# from sqlalchemy import desc
from utils.apiResponse import ApiResponse
import requests
from dataset.models import Dataset
from cueSearch.models import GlobalDimensionValues, GlobalDimension
from cueSearch.serializers import AllDimensionsSerializer, GlobalDimensionSerializer


# from .models import GlobalDimension, GlobalDimensionValues
# from .serializer import GlobalDimensionSchema
# from config import DIMENSION_URL
# from elasticSearch import ESIndexingUtils


class GlobalDimensionServices:
    """Services for Global Dimension"""

    def createGlobalDimension(payloads):
        """Create global dimension"""
        try:
            print("payloads", payloads)
            res = ApiResponse("Error in creating dimensionalValues")
            name = payloads["name"]
            globalDimension = GlobalDimension.objects.create(name=name)
            objs = payloads["dimensionalValues"]
            dimensionalValueObjs = []
            for obj in objs:
                datasetId = obj["datasetId"]
                dataset = Dataset.objects.get(id=datasetId)
                GlobalDimensionValues.objects.create(
                    dataset=dataset,
                    dimension=obj["dimension"],
                    globalDimension=globalDimension,
                )
                # dimensionalValueObjs.append(gdValues)

            # db.session.bulk_save_objects(dimensionalValueObjs)
            # try:
            # app.logger.info("Indexing starts")
            # ESIndexingUtils.indexGlobalDimension()
            # app.logger.info("Indexing completed")
            # except Exception as ex:
            # app.logger.error("Indexing Failed %s", ex)

            # res = {"success":True}
            res.update(True, "GlobalDimension created successfully")
        except Exception as ex:
            res.update(False, "Global Dimension name already exists")
            # res = {"success":False, "message":"Global Dimension name already exists."}
        return res

    def deleteGlobalDimension(globalDimensionId):
        try:
            res = ApiResponse("Error occurs while deleting global dimension")
            globalDimension = GlobalDimension.objects.filter(
                id=globalDimensionId
            ).delete()
            res.update(True, "successfully deleted")
        except Exception as ex:
            # app.logger.error("Error occured while delete global dimension of Id : ",id)
            # db.session.rollback()
            # res = {"success":False, "message": "Error occured while deleting global dimension "}
            res.update(False, "Error occured while deleting global dimension ")
        return res

    def getDimension():
        """Get dimension from cueObserve"""
        try:
            res = ApiResponse()
            # url = DIMENSION_URL
            # response = requests.get(url)
            # payloads  = response.json().get("data", [])

            datasets = Dataset.objects.all()  # Get all datasets
            data = AllDimensionsSerializer(datasets, many=True).data
            payloads = data
            payloadDicts = []
            for payload in payloads:
                for dimension in payload.get("dimensions", []):
                    dictObjs = {}
                    dictObjs["dataset"] = payload["name"]
                    dictObjs["datasetId"] = payload["id"]
                    dictObjs["dimension"] = dimension
                    payloadDicts.append(dictObjs)

            # res = {"success":True, "data":payloadDicts}
            res.update(True, "Successfully get dimension of datasets ", payloadDicts)
        except Exception as ex:
            # app.logger.error*("Failed to get dimension %s", ex)
            res.update(False, "Successfully get dimension of datasets ", [])

            # res = {"success":False, "data":[], "message":"Error occured to get dimension from cueObserve"}
        return res

    def getGlobalDimensions():
        """Services to get Global dimension and their linked dimension"""
        res = ApiResponse("Error while fetching global dimensions")
        try:
            # globalDimensions = GlobalDimension.query.order_by(desc(GlobalDimension.id)).all()
            globalDimensions = GlobalDimension.objects.all().order_by("-id")
            # data = GlobalDimensionSchema(many=True).dump(globalDimensions)
            data = GlobalDimensionSerializer(globalDimensions, many=True).data
            res.update(True, "Successfully fetched global dimension data", data)
            # res = {"success":True, "data":data}
        except Exception as ex:
            # app.logger.error("Failed to get global dimension %s", ex)
            # res = {"success":False, "data":[], "message":"Error occured to get data in global dimension"}
            res.update(False, "Error occured to get data in global dimension", [])
        return res

    def publishGlobalDimension(payload):
        """Service to publish / unpublish global dimension"""
        try:
            res = ApiResponse()
            published = payload.get("published", False)
            globalDimensionId = payload.get("id", None)
            if globalDimensionId:
                globalDimensionObj = GlobalDimension.objects.get(id=globalDimensionId)
                globalDimensionObj.published = published
                # db.session.commit()
                globalDimensionObj.save()
                # res = {"success":True, "message":"Global Dimension updated successfully"}
                res.update(True, "Global Dimension updated successfully")
            else:
                # res = {"success":False, "message": "Id is mandatory"}
                res.update(False, "Id is mandatory")
        except Exception as ex:
            # app.logger.error("Failed to publish/unpublish global dimension %s", ex)
            # db.session.rollback()
            # res = {"success":False, "message": "Error occured while updating global dimension"}
            res.update(False, "Error occured while updating global dimension")
        return res

    def getGlobalDimensionById(id):
        """Service to get global dimension of given id"""
        try:
            res = ApiResponse("Error occurs while fetching global dimension by Id")
            globalDimensionObj = GlobalDimension.objects.get(id=id)
            # data = GlobalDimensionSchema().dump(globalDimensionObj)
            data = GlobalDimensionSerializer(globalDimensionObj).data
            # app.logger.info("data %s", data)
            # res = {"success":True, "data": data }
            res.update(True, "Successfully fetched global dimension Id", data)

        except Exception as ex:
            # app.logger.error("Failed to get global dimension of id %s", id)
            # app.logger.error("Error %s", ex)
            # res = {"success":True, "data": [], "message":"Failed to get global dimension of id : " + id }
            res.update(False, "Error occurs while fetching global dimension by Id", [])
        return res

    def updateGlobalDimensionById(id, payload):
        try:
            res = ApiResponse()
            name = payload.get("name", "")
            objs = payload.get("dimensionalValues", [])
            published = payload.get("published", False)
            dimensionalValueObjs = []
            globalDimension = GlobalDimension.objects.get(id=id)
            newId = globalDimension.id
            globalDimension.delete()
            # db.session.delete(globalDimension)
            # db.session.flush()
            # app.logger.info("flushed global dimension %s", globalDimension)
            gd = GlobalDimension.objects.create(
                id=newId, name=name, published=published
            )
            # db.session.add(gd)
            # db.session.flush()

            for obj in objs:
                datasetId = obj["datasetId"]
                dataset = Dataset.objects.get(id=datasetId)
                gdValues = GlobalDimensionValues.objects.create(
                    dataset=dataset, dimension=obj["dimension"], globalDimension=gd
                )
                # dimensionalValueObjs.append(gdValues)
            # db.session.bulk_save_objects(dimensionalValueObjs)
            # db.session.commit()
            # Global dimension indexing on Global dimension update
            # try:
            #     ESIndexingUtils.indexGlobalDimension()
            #     app.logger.info("Indexing completed")
            # except Exception as ex:
            #     app.logger.error("Indexing Failed %s", ex)
            # res = {"success":True, "message":"Global Dimension updated successfully"}
            res.update(True, "Global Dimension updated successfully")
        except Exception as ex:
            # app.logger.error("Failed to update global dimension of Id : %s", id)
            # app.logger.error("Traces of failure %s", ex)
            # db.session.rollback()
            # res = {"success":False, "message":"Error occured while updating global dimension"}
            res.update(False, "Error occured while updating global dimension")
        return res
