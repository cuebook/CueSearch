import logging
from celery import shared_task
from cueSearch.elasticSearch import ESIndexingUtils


@shared_task
def indexingJob():
    try:
        logging.info(
            "************************ Indexing Job starts ! ************************ "
        )
        ESIndexingUtils.indexGlobalDimensionsDataForSearchSuggestion()  # Used for search suggestion
        ESIndexingUtils.indexNonGlobalDimensionsDataForSearchSuggestion()  # Used for index auto global dimension
        ESIndexingUtils.indexGlobalDimensionsData()
        ESIndexingUtils.indexNonGlobalDimensionsData()

        logging.info(
            "*********************** Indexing Job completed ! ********************** "
        )
    except Exception as ex:
        logging.error("Error occured while indexing ! %s", str(ex))
