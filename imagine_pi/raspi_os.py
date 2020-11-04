
###########
# Stdlib

import requests
import json
import os
from datetime import date
from urllib.parse import urlparse, urlunparse

####################
# Globals
OS_LIST_URL = "https://downloads.raspberrypi.org/os_list_imagingutility.json"


class _RaspBerryUrlAccess:

    def __get__(self, obj, objtype=None):
        if obj._url:
            return urlunparse(obj.__dict__.get('_url'))
        else:
            return None

    def __set__(self, obj, value):
        obj.__dict__['_url'] = urlparse(value)
        id_base = os.path.basename(os.path.normpath(obj.__dict__.get('_url').path))
        filename, ext = os.path.splitext(id_base)
        if ext != 'zip':
            filename, ext = os.path.splitext(filename)
        obj.__dict__['_image_name'] = filename


class _RaspBerryImageNAmeAccess:
    def __get__(self, obj, objtype=None):
        return obj.__dict__.get('_image_name') or None


class RaspberryOS:

    url = _RaspBerryUrlAccess()
    image_name = _RaspBerryImageNAmeAccess()

    def __init__(
        self,
        name,
        description,
        url,
        item_parents=[],
        extract_size=None,
        extract_sha256=None,
        image_download_size=None,
        release_date=None,
        image_download_sha256=None,
        contains_multiple_files=None,
    ):
        self.name = name
        self.description = description
        self.item_parents = item_parents
        self.url = url
        self.extract_size = extract_size
        self.extract_sha256 = extract_sha256
        self.image_download_size = image_download_size
        self.image_download_sha256 = image_download_sha256
        self.contains_multiple_files = contains_multiple_files

        self.release_date = None
        if release_date:
            self.release_date = date.fromisoformat(release_date)

    def __dir__(self):
        return [
            'name',
            'description',
            'url',
            'image_name',
            'release_date',
            'extract_size',
            'extract_sha256',
            'image_download_size',
            'image_download_sha256',
            'contains_multiple_files'
        ]


def _get_jsonparsed_data(url):
    response = requests.get(url)
    data = response.content.decode("utf-8")
    return json.loads(data)


def _fetch_oslist(os_url):
    os_list = _get_jsonparsed_data(os_url)["os_list"]
    for os_item in os_list:
        if 'subitems_url' in os_item:
            os_item['subitems'] = _fetch_oslist(os_item['subitems_url'])
    return os_list


def _normalize_os_list(os_list):
    results = []
    for os_item in os_list:
        os_item['item_parents'] = []
        if 'subitems' in os_item:
            subitems = _normalize_os_list(os_item['subitems'])
            for subitem in subitems:
                subitem['item_parents'].insert(0, os_item['name'])
                results.append(subitem)
        else:
            results.append(os_item)
    return results


def get_raspi_os_list():
    os_list = _normalize_os_list(_fetch_oslist(OS_LIST_URL))
    raspi_os_list = []
    for os_obj in os_list:
        raspos = RaspberryOS(
            name=os_obj['name'],
            description=os_obj['description'],
            url=os_obj['url'],
            extract_size=os_obj['extract_size'],
            item_parents=os_obj['item_parents'],
            extract_sha256=None,
            image_download_size=None,
            release_date=None,
            image_download_sha256=None,
            contains_multiple_files=None
        )
        if 'extract_sha256' in os_obj:
            raspos.extract_sha256 = os_obj['extract_sha256']
        if 'image_download_size' in os_obj:
            raspos.image_download_size = os_obj['image_download_size']
        if 'release_date' in os_obj:
            raspos.release_date = date.fromisoformat(os_obj['release_date'])
        if 'image_download_sha256' in os_obj:
            raspos.image_download_sha256 = os_obj['image_download_sha256']
        if 'contains_multiple_files' in os_obj:
            raspos.contains_multiple_files = os_obj['contains_multiple_files']

        raspi_os_list.append(raspos)

    return raspi_os_list


def get_raspi_os_from_url(url):
    os_list = get_raspi_os_list()
    for os_obj in os_list:
        if os_obj.url == url:
            return os_obj

    raise Exception("no raspberry pi os found with url {}".format(url))


def get_raspi_os_from_name(name):
    os_list = get_raspi_os_list()
    for os_obj in os_list:
        if os_obj.name == name:
            return os_obj

    raise Exception("no raspberry pi os found with name '{}'".format(name))
