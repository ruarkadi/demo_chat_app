from distutils.log import error
import string
import random
import secrets
from urllib import response
from mongoengine import QuerySet, Document, EmbeddedDocument
from mongoengine.base.datastructures import EmbeddedDocumentList
import json
from bson import ObjectId
from ..api.responses.response_filters import filter_dict_response, filter_queryset_response
from ..api.responses.response_normalization import normalize_data

def generate_random_string(length = 6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def generate_complex_random_string(length = 8):

    string_list = random.choices(string.ascii_uppercase, k=1) + random.choices(string.digits, k=1) + random.choices(string.punctuation, k=1) + random.choices(string.ascii_lowercase, k=length-3)

    random.shuffle(string_list)

    return ''.join(string_list)

def is_file_exists(path):
    try:
        with open(path, 'r') as file:
            content = file
    except:
        raise FileNotFoundError("File not found in specified path")

    return True

def build_api_response_data(data, success, label=None):

    if not label:
        label = "data" if success else "error"

    # if isinstance(data, QuerySet):

    #     if len(data) >= 1:
    #         # Here we are getting the first objects class name to be used in the filter_queryset_response method
    #         filter_type = data.first().__class__.__name__.lower()

    #         # Here we are filtering the result before normalizing because queryset has built-in filtering capabilities that we can utilize
    #         data = filter_queryset_response(data, filter_type)
    #         print(type(data[0]))

    #     # Here we are normalizing the id fields using the MongoDecoder cls
    #     data = normalize_data(data)

    # if isinstance(data, Document) or isinstance(data, EmbeddedDocument):

    #     filter_type = data.__class__.__name__.lower()

    #     # Here we are first normalizing because we Document object type doesn't have built in filtering capabilities like Queryset
    #     data = normalize_data(data)

    #     # here will be filters

    #     data = filter_dict_response(data, filter_type)

    if isinstance(data, EmbeddedDocumentList) \
        or (isinstance(data, QuerySet) and len(data) and isinstance(data[0], Document)) \
        or isinstance(data, Document) \
        or isinstance(data, EmbeddedDocument):

        if isinstance(data, Document) or isinstance(data, EmbeddedDocument):
            data = [data]

        return_list = []

        for obj in data:

            filter_type = obj.__class__.__name__.lower()

            obj = normalize_data(obj)

            obj = filter_dict_response(obj, filter_type)

            return_list.append(obj)

        data = return_list

        if isinstance(data, Document) or isinstance(data, EmbeddedDocument):
            data = data[0]

    if isinstance(data, ObjectId):
        data = str(data)

    return {"success": success, label: data}

