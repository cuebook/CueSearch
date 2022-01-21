import logging
from celery import shared_task
from cueSearch.elasticSearch import ESIndexingUtils
import logging

@shared_task
def indexingJob():
    try:
        logging.info("Indexing starts")
        ESIndexingUtils.indexGlobalDimensionsDataForSearchSuggestion() # Used for search suggestion
        ESIndexingUtils.indexGlobalDimensionName()
        ESIndexingUtils.indexGlobalDimensionsData()
        logging.info("Indexing completed !")
    except Exception as ex:
        logging.error("Error occured while indexing ! %s", str(ex))
