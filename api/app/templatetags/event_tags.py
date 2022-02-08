# pylint: disable=C0103, E0102
import json
from typing import List, Dict
from django import template

register = template.Library()

@register.simple_tag(takes_context=True, name="stringify")
def render_values(context, value):
    """
    Render query to their value
    """

    if value in context.dicts[-1]:
        return json.dumps(context.dicts[-1][value])

    return ""

@register.simple_tag(name="conditionalCount")
def conditionalCount(givenDictList: List[Dict], givenKey: str, givenValue: str) -> int:
    """
    Counts number of items where key equals value in list of dict
    :givenDictList: list of dicitionary
    :givenKey: key against which value is to be matched
    :givenValue: to match value
    """
    count = 0
    for givenDict in givenDictList:
        if givenKey in givenDict and givenDict[givenKey]:
            count += 1

    return count

@register.filter
def getDictKey(dictionary, index):
    return list(dictionary.keys())[index]


@register.filter
def getDictValue(dictionary, index):
    return dictionary[list(dictionary.keys())[index]]

