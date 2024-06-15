#! /usr/bin/env python3

# Copyright 2023 Planet Labs, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This is an example/demo tool showing how to download additional data such as
contributing scene shapefiles, UDMs, etc for Planet mosaics.  It's intened as a
command line tool.  As an example, let's say you wanted to download all data
within a region from a specific mosaic (note that geojson is the only supported
AOI format)::

    python3 download_mosaic_assets.py <mosaic_name> --region some_aoi.geojson

This would download all quads overlapping the AOI into a folder named after the
mosaic.

More generally, this script also allows downloading other assets. For example,
to download (zipped) shapefiles of the contributing scene information for the
mosaic, use::

    python3 download_mosaic_assets.py <mosaic_name> --region some_aoi.geojson --asset provenance_vector

To download UDM2 geotiffs (i.e. what pixels were flagged as cloud/snow/etc),
you'd use::

    python3 download_mosaic_assets.py <mosaic_name> --region some_aoi.geojson --asset ortho_udm2

Note that the examples above assume the PL_API_KEY environment variable has
been set with your API key.  If that's not the case, you'll need to pass along::

    --api-key <your_api_key>

You can find your API key under https://www.planet.com/account

Note that this tool is not formally supported and is provided as a demo.
"""

import os

# 设置环境变量

import re
import json
import shutil
import argparse
import datetime as dt
import itertools as it
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor
import tqdm
import requests
from requests.adapters import HTTPAdapter

idlist = {}
labellist = {}
date = '2022-09'
idlistpos = f'/Users/zgf/Desktop/planet/PK_UID_link/{date}/'+'idlist.json'
labellistpos = f'/Users/zgf/Desktop/planet/PK_UID_link/{date}/'+'labellist.json'

if os.path.exists(idlistpos):
    with open(idlistpos, 'r', encoding='utf-8') as f:
        idlist = json.load(f)
else:
    os.makedirs(f'/Users/zgf/Desktop/planet/PK_UID_link/{date}')
if os.path.exists(labellistpos):
    with open(labellistpos, 'r', encoding='utf-8') as f:
        labellist = json.load(f)

def main():
    global date
    parser = argparse.ArgumentParser()
    # global_monthly_2023_07_mosaic
    # ps_partner_monthly_sen2_normalized_analytic_2023_07_mosaic
    parser.add_argument('--mosaic',default=f'global_monthly_{date[:4]}_{date[5:]}_mosaic',help='Name of the mosaic to download')
    parser.add_argument('--asset', default='quad',
            choices=['quad', 'ortho_udm2', 'provenance_vector', 'provenance_raster'],
            help='Type of data to download.')
            # qq2022-09-2
    parser.add_argument('--region',
            # default=f'/Users/zgf/Desktop/planet/todownload_geojson/qq/qq{date}.geojson',
            default=f'/Users/zgf/Desktop/planet/todownload_geojson/qq/qq2022-09-2.geojson',
            help='Path to a geojson file for the AOI to download')
    parser.add_argument('--bbox',
            help='AOI to download as "lon_min,lat_min,lon_max,lat_max"')
    parser.add_argument('--api-key',default='PLAKadd6dfb9e4b744dea8df84639778c3eb',
            help='Planet credentials in the form of an API key. Will be read'
                 ' from the PL_API_KEY environment variable if not set')
    parser.add_argument('-o', '--output-dir',default=f'/Users/zgf/Desktop/planet/{date}',
            help='Directory to download quads into. If not specified, defaults'
                 ' to the mosaic name.')

    args = parser.parse_args()

    if args.output_dir is None:
        args.output_dir = args.mosaic

    client = BasemapsClient(api_key=args.api_key)
    client.list_all_mosaics()
    mosaic = client.mosaic(args.mosaic)
    # print(mosaic,'mosaic')

    if args.region:
        print('启用了region')
        num = 0
        for PK_UID, poly in polygons_with_id(args.region):
            num += 1 
            files = mosaic.download_quads(
                    # filename_template=str(label)+'.tif',
                    PK_UID,
                    output_dir=args.output_dir,
                    region=poly,
                    asset=args.asset,
            )
            if not files:
                continue
            for item in files:
                print(item)
            if num %10 == 0:
                print(f'已处理{num}张')
                # with open('q2205.log', 'a') as f:
                #     f.write(f'已处理{num}张\n')
                with open(idlistpos, 'w', encoding='utf-8') as f:
                    json_str = json.dumps(idlist)
                    f.write(json_str)
                with open(labellistpos, 'w', encoding='utf-8') as f:
                    json_str = json.dumps(labellist)
                    f.write(json_str)

    # 将字典转换为JSON字符串


    # 将JSON字符串保存到文件
    with open(idlistpos, 'w', encoding='utf-8') as f:
        json_str = json.dumps(idlist)
        f.write(json_str)
    with open(labellistpos, 'w', encoding='utf-8') as f:
        json_str = json.dumps(labellist)
        f.write(json_str)
    print('下载完成')
    # print(idlist)
    # print(labellist)


def _get_client(client):
    if client is None:
        client = BasemapsClient()
    return client


def _chunks(iterable, chunksize):
    iterable = iter(iterable)
    while True:
        v = tuple(it.islice(iterable, chunksize))
        if v:
            yield v
        else:
            return


class BasemapsClient(object):
    """Base client for working with the Planet Basemaps API"""

    base_url = 'https://api.planet.com/basemaps/v1'

    def __init__(self, api_key=None, version="1.5"):
        """
        :param str api_key:
            Your Planet API key. If not specified, this will be read from the
            PL_API_KEY environment variable.
        :param str version:
            Version of the API to use via the "v" argument. Note that currently
            only v1 (None) or "1.5" are supported server-side.
            Selecting "1.5" will result in different metadata responses and
            additional assets available for download, but is generally backwards
            compatible with v1.
        """
        if api_key is None:
            api_key = os.getenv('PL_API_KEY')
        self.api_key = api_key

        if self.api_key is None and 'internal' not in self.base_url:
            msg = 'You are not logged in! Please set the PL_API_KEY env var.'
            raise ValueError(msg)

        if version not in [None, "1.5", "1"]:
            raise ValueError('Invalid version "{}"!'.format(version))

        if version == "1":
            version = None
        self.version = version

        self.session = requests.Session()
        self.session.auth = (api_key, '')

        retries = Retry(total=5, backoff_factor=0.2, status_forcelist=[429, 503])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def _url(self, endpoint):
        return '{}/{}'.format(self.base_url, endpoint)

    def list_all_mosaics(self):
        try:
            mosaics = self._list('mosaics')
            for mosaic in mosaics:
                print(mosaic['name'])
        except Exception as e:
            print("Failed to fetch mosaics:", str(e))

    def _consume_pages(self, endpoint, key, **params):
        """General pagination structure for Planet APIs."""
        url = self._url(endpoint)
        while True:
            response = self._get(url, **params)
            for item in response[key]:
                yield item

            if '_next' in response['_links']:
                url = response['_links']['_next']
            else:
                break

    def _query(self, endpoint, key, json_query):
        """Post and then get for pagination. Being lazy here and repeating."""
        url = None

        while True:
            if url is None:
                url = self._url(endpoint)
                response = self._post(url, json_query)
            else:
                response = self._get(url)

            for item in response[key]:
                yield item

            if '_next' in response['_links']:
                url = response['_links']['_next']
            else:
                break

    def _list(self, endpoint, key=None, **params):
        key = key or endpoint
        for item in self._consume_pages(endpoint, key, **params):
            yield item

    def _get(self, url, **params):
        if self.version:
            params['v'] = self.version
        rv = self.session.get(url, params=params)
        rv.raise_for_status()
        return rv.json()

    def _post(self, url, json_data):
        params = {'v': self.version} if self.version else {}
        rv = self.session.post(url, json=json_data, params=params)
        rv.raise_for_status()
        return rv.json()

    def _item(self, endpoint, **params):
        return self._get(self._url(endpoint), **params)

    def _download(self, url, filename=None, output_dir=None, params=None):
        if not params:
            params = {}
        if self.version:
            params['v'] = self.version
        response = self.session.get(url, stream=True, params=params)
        response.raise_for_status()

        disposition = response.headers['Content-Disposition']
        if filename is None:
            filename = re.findall(r'filename="(.+)"', disposition)[0]

        if filename is None:
            msg = 'Filename not specified and no content-disposition info!'
            raise ValueError(msg)

        if output_dir is not None:
            if not os.path.exists(output_dir):
                os.mkdir(output_dir)
            filename = os.path.join(output_dir, filename)

        # Download in chunks.
        with open(filename, 'wb') as outfile:
            shutil.copyfileobj(response.raw, outfile)
        del response

        return filename

    def mosaic(self, name=None, mosaic_id=None):
        """
        Retrieve a `Mosaic` object for a particular mosaic, either by name or
        ID. You must specify either name or mosaic_id, but not both.

        :param str name:
            The name of the mosaic (e.g. "global_monthly_2019_09_mosaic")
        :param str mosaic_id:
            The mosaic ID (e.g. "431b62a0-eaf9-45e7-acf1-d58278176d52")

        :returns Mosaic:
            An object representing the mosaic
        """
        if name is not None:
            return Mosaic.from_name(name, self)
        elif mosaic_id is not None:
            return Mosaic.from_id(mosaic_id, self)
        else:
            raise ValueError('You must specify either name or mosaic_id!')

    def list_mosaics(self, name_contains=None):
        """
        Iterate through all mosaics you have access to, optionally filtering
        based on name. Yields ``MosaicSeries`` instances.

        :param str name_contains:
            Search only for mosaics that contain the specified substring in
            their names
        """
        for item in self._list('mosaics', name__contains=name_contains):
            yield Mosaic(item, self)


class Mosaic(object):
    """Representation of a single mosaic."""

    def __init__(self, info, client=None):
        self.client = _get_client(client)

        self.id = info['id']
        self.name = info['name']
        self.level = info['level']
        self.datatype = info['datatype']
        self.assets = info.get('assets', [])
        self.info = info

        iso = '%Y-%m-%dT%H:%M:%S.%fZ'
        self.start_date = dt.datetime.strptime(self.info['first_acquired'], iso)
        self.end_date = dt.datetime.strptime(self.info['last_acquired'], iso)

    @classmethod
    def from_name(cls, name, client=None):
        """Look up a mosaic by name in the Planet Basemaps API."""
        client = _get_client(client)
        info = next(client._list('mosaics', name__is=name))
        return cls(info, client)

    @classmethod
    def from_id(cls, mosaic_id, client=None):
        """Look up a mosaic by ID in the Planet Basemaps API."""
        client = _get_client(client)
        info = client._item('mosaics/{}'.format(mosaic_id))
        return cls(info, client)

    @property
    def tileserver(self):
        """The XYZ tile service URL for the mosaic."""
        url = self.info['_links']['tiles']
        if '/internal' in self.client.base_url:
            url = url.replace('/basemaps/v1/', '/internal/')
        return url.split('?')[0]

    def _bbox_search(self, bbox):
        if bbox is None:
            bbox = self.info['bbox']

        endpoint = 'mosaics/{}/quads'.format(self.id)
        bbox = ','.join(str(item) for item in bbox)
        return self.client._consume_pages(endpoint, 'items', bbox=bbox)

    def _region_search(self, region):
        endpoint = 'mosaics/{}/quads/search'.format(self.id)
        return self.client._query(endpoint, 'items', region)

    def quads(self, PK_UID, bbox=None, region=None):
        global idlist
        global labellist

        """
        Retrieve info for all quads within a specific AOI specified as either a
        lon/lat ``bbox`` or a geojson ``region``.

        :param tuple bbox:
            A 4-item tuple of floats.  Expected to be (longitude_min,
            latitude_min, longitude_max, latitude_max).
        :param dict region:
            A GeoJSON geometry (usually polygon or multipolygon, not a feature
            collection) in WGS84 representing the exact AOI.
        """
        if region:
            quads = self._region_search(region)
        else:
            quads = self._bbox_search(bbox)

        count = 0   
        try:
            while True:
                next(quads)
                count += 1
        except StopIteration:
            pass
        # # 如果region和多个quad相交，放弃不下载
        res = None
        if count == 1:
            if region:
                quads = self._region_search(region)
            else:
                quads = self._bbox_search(bbox)
            
            for info in quads:
                
                if not info['id'] in idlist:
                    idlist[info['id']]=1
                    res = MosaicQuad(info, self, self.client)
                     
                else:
                    idlist[info['id']]+=1
            labellist[PK_UID] = info['id']
        yield res


    def download_quads(self, PK_UID, output_dir=None, bbox=None, region=None,
                       nthreads=8, filename_template=None, asset=None):
        """
        Download mosaic data to a local directory for a specific AOI specified
        as either a lon/lat ``bbox`` or a geojson ``region``.

        Note that this is a generator and it must be iterated through to have
        an effect.

        :param tuple bbox:
            A 4-item tuple of floats.  Expected to be (longitude_min,
            latitude_min, longitude_max, latitude_max).
        :param dict region:
            A GeoJSON geometry (usually polygon or multipolygon, not a feature
            collection) in WGS84 representing the exact AOI.
        :param int nthreads:
            Number of concurrent downloads.
        :param str filename_template:
            A {} style format string with the keys "mosaic", "level", "x", "y".
            Defaults to the Content-Deposition sepecified by the API. (i.e.
            typically "L{z}-{x}E-{y}N.tif")
        :param str asset:
            The category of item to download. Will default to downloading the
            main quad data for the mosaic. Other options will depend on the
            mosaic, but are often "provenance_raster", "provenance_vector", and
            "ortho_udm2".

        :returns generator paths:
            A generator over paths (as strings) of the files downloaded
        """

        def download(quad):
            if not quad:
                return 
            if filename_template is not None:
                filename = filename_template.format(mosaic=self.name,
                                                    level=quad.level,
                                                    x=quad.x,
                                                    y=quad.y)
            else:
                filename = None

            return quad.download(
                    filename=filename,
                    output_dir=output_dir,
                    asset=asset,
            )
        # RES = self.quads(PK_UID, bbox, region)
        quads = self.quads(PK_UID, bbox, region)

        groups = _chunks(quads, 4 * nthreads)
        with ThreadPoolExecutor(nthreads) as executor:
            for group in groups:
                for path in executor.map(download, group):
                    yield path


class MosaicQuad(object):
    """A representation of a single quad."""
    def __init__(self, info, mosaic=None, client=None):
        self.client = _get_client(client)
        self.info = info
        self.id = info['id']
        self.coverage = self.info.get('percent_covered')
        self.bounds = self.info.get('bbox')

        if mosaic is None:
            # Bit odd that quads don't include a mosaic ID directly...
            mosaic_id = self.info['_links']['_self'].split('/')[-3]
            mosaic = Mosaic.from_id(mosaic_id)

        self.mosaic = mosaic
        self.mosaic_name = mosaic.name
        self.assets = mosaic.assets

        x, y = self.id.split('-')
        self.x = int(x)
        self.y = int(y)
        self.level = self.mosaic.level

    @property
    def downloadable(self):
        """Whether or not you have download permissions for the quad."""
        return 'download' in self.info['_links']

    @property
    def download_url(self):
        """
        Download URL for this quad. May be used/streamed as a COG. Will be
        ``None`` if you do not have download access to the quad.
        """
        return self.info['_links'].get('download')

    def download(self, filename=None, output_dir=None, asset=None):
        """Download quad data locally."""
        params = {}
        if asset is not None:
            params = {'asset': asset}

        if self.downloadable:
            return self.client._download(self.download_url, filename,
                                         output_dir, params=params)

    def contribution(self):
        """
        Planet data api URLs for each scene that contributed to this quad.
        """
        url = self.info['_links'].get('items')
        if url:
            data = self.client._get(url)
            return [item['link'] for item in data['items']]
        else:
            return []


def _polys_in_multipoly(geom):
    if geom['type'] == 'Polygon':
        yield geom

    elif geom['type'] == 'MultiPolygon':
        coords = geom['coordinates']
        for poly in coords:
            yield {'type': 'Polygon', 'coordinates': poly}

    else:
        raise ValueError('Unsupported type! {}'.format(geom["type"]))


# def polygons_in(filename):
#     """
#     Convert a feature collection or multipolygon into component polygon
#     geometries.

#     :param str filename:
#         The local path to a geojson file.
#     """
#     with open(filename, 'r') as infile:
#         data = json.load(infile)

#     try:
#         featuretype = data['type']
#     except KeyError:
#         raise ValueError('{} does not appear to be GeoJSON!'.format(filename))

#     if featuretype in ['Polygon', 'MultiPolygon']:
#         for poly in _polys_in_multipoly(data):
#             yield poly

#     elif featuretype == 'FeatureCollection':
#         for item in data['features']:
#             if item['geometry']['type'] not in ['Polygon', 'MultiPolygon']:
#                 msg = 'Unsupported type: {}'.format(item['geometry']['type'])
#                 raise ValueError(msg)

#             for poly in _polys_in_multipoly(item['geometry']):
#                 yield poly

#     else:
#         raise ValueError('Unsupported geometry type: {}'.format(featuretype))
import json

def polygons_with_id(filename):
    """
    Convert a feature collection into component polygon geometries,
    preserving the ID from properties.

    :param str filename:
        The local path to a geojson file.
    """
    with open(filename, 'r') as infile:
        data = json.load(infile)

    try:
        featuretype = data['type']
    except KeyError:
        raise ValueError('{} does not appear to be GeoJSON!'.format(filename))

    if featuretype == 'FeatureCollection':
        for item in data['features']:
            geom_type = item['geometry']['type']
            if geom_type not in ['Polygon', 'MultiPolygon']:
                raise ValueError('Unsupported type: {}'.format(geom_type))

            # Extract the ID from properties
            PK_UID = item['properties']['PK_UID']

            # Assuming _polys_in_multipoly is defined to handle extracting polygons
            # from both Polygon and MultiPolygon types
            for poly in _polys_in_multipoly(item['geometry']):
                yield PK_UID, poly

    else:
        raise ValueError('Unsupported geometry type: {}'.format(featuretype))

def _polys_in_multipoly(geometry):
    """
    A helper function to yield polygons from a Polygon or MultiPolygon geometry.
    """
    if geometry['type'] == 'Polygon':
        yield geometry
        # ['coordinates']
    elif geometry['type'] == 'MultiPolygon':
        for poly in geometry['coordinates']:
            yield poly

# Example usage
# You would call polygons_with_id with the filename of your GeoJSON file:
# for id, polygon in polygons_with_id('path_to_your_geojson_file.geojson'):
#     print(f"ID: {id}, Polygon: {polygon}")


if __name__ == '__main__':
    main()
    