from typing import List, Dict

from typing_extensions import TypedDict


class SearchCardsPayload(TypedDict):
    """
    Payload for getting search cards
    """
    value: str
    user_entity_identifier: str
    id: str
    datasetId: int
    globalDimensionId: str
    type: str
    label: str
    searchType: str


class SearchResults(TypedDict):
    """
    """
    value: str
    dimension: str
    globalDimensionName: str
    user_entity_identifier: str
    id: str
    dataset: str
    datasetId: int
    type: str


class GroupedResults(TypedDict, total=False):
    """
    """
    int: List[SearchResults]
