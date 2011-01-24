#!/usr/bin/python2.4
#
# Copyright 2007 The Python-Bandcamp Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''A library that provides a Python interface to the Bandcamp API'''

__author__ = 'eric@hardlycode.com'
__version__ = '0.0.1'

import base64
import calendar
import datetime
import httplib
import os
import rfc822
import sys
import tempfile
import textwrap
import time
import calendar
import urllib
import urllib2
import urlparse
import gzip
import StringIO

try:
  # Python >= 2.6
  import json as simplejson
except ImportError:
  try:
    # Python < 2.6
    import simplejson
  except ImportError:
    try:
      # Google App Engine
      from django.utils import simplejson
    except ImportError:
      raise ImportError, "Unable to load a json library"

# parse_qsl moved to urlparse module in v2.6
try:
  from urlparse import parse_qsl, parse_qs
except ImportError:
  from cgi import parse_qsl, parse_qs

try:
  from hashlib import md5
except ImportError:
  from md5 import md5

import oauth2 as oauth

# A singleton representing a lazily instantiated FileCache.
DEFAULT_CACHE = object()

class BandcampError(Exception):
  '''Base class for Bandcamp errors'''

  @property
  def message(self):
    '''Returns the first argument used to construct this error.'''
    return self.args[0]

class Band(object):
	'''A class representing the Band structure used by the bandcamp API.
	
	The Band structure esposes the following properties:
	
	band.name
	band.subdomain
	band.url
	band.id
	'''
	def __init__(self,
				name=None,
				subdomain=None,
				url=None,
				id=None):
		'''An object to hold a Bandcamp band.
		
		This class is normally instantiated by the bandcamp.Api class.
		
		Args:
			name:
				The name of the band.
			subdomain:
				The subdomain of the band.
			url:
				The bandcamp url of the band.
			id: 
				The unique id of the band in the bandcamp api.			
		'''
		self.name = name
		self.subdomain = subdomain
		self.url = url
		self.id = id

	def GetName(self):
		'''Get the name of this band.'''
		
		return self._name
		
	def _SetName(self, name):
		'''Set the name of this band.'''
		self._name = name
		
	name = property(GetName, _SetName, doc='The name of this band.')
	
	def GetSubdomain(self):
		'''Get the subdomain of this band for bandcamp url.'''
		
		return self._subdomain
	
	def _SetSubdomain(self, subdomain):
		'''Set the subdomain of this band for bandcamp url.'''
		self._subdomain = subdomain
	
	subdomain = property(GetSubdomain, _SetSubdomain, doc='The subdomain for this band on bandcamp.')
	
	def GetUrl(self):
		'''Get the url of this band for bandcamp.'''
		
		return self._url
	
	def _SetUrl(self, url):
		'''Set the url of this band for bandcamp.'''
		self._url = url
	
	url = property(GetUrl, _SetUrl, doc='The url for this band on bandcamp.')
	
	def GetId(self):
		'''Get the unique id of this band'''
		
		return self._id
		
	def _SetId(self, id):
		'''Set the unique id of this band.'''
		self._id = id
		
	id = property(GetId, _SetId, doc='The unique id for this band.')
	
	def AsJsonString(self):
		'''A JSON string representation of this bandcamp.Band instance.

	    Returns:
	      A JSON string representation of this bandcamp.Band instance
		'''
		return simplejson.dumps(self.AsDict(), sort_keys=True)
	
	def AsDict(self):
		'''A dict representation of this bandcamp.Band instance.

		The return value uses the same key names as the JSON representation.

		Return:
			A dict representing this bandcamp.Band instance
		'''
		data = {}
		if self.name:
		  data['name'] = self.name
		if self.subdomain:
		  data['subdomain'] = self.subdomain
		if self.url:
		  data['url'] = self.url
		if self.id:
		  data['id'] = self.id
		return data

	@staticmethod
	def NewFromJsonDict(data):
	  '''Create a new instance based on a JSON dict.

	  Args:
	    data: A JSON dict, as converted from the JSON in the bandcamp API
	  Returns:
	    A bandcamp.Band instance
	  '''
	  return Band(name=data.get('name', None),
	                subdomain=data.get('subdomain', None),
	                url=data.get('url', None),
	                id=data.get('band_id', None))
	
class Album(object):
	'''A class representing the Album structure used by the bandcamp API.
	
	The Album structure exposes the following properties:
	
	album.id
	album.band_id
	album.title
	album.release_date
	album.downloadable
	album.url
	album.tracks
	album.about
	album.credits
	album.small_art_url
	album.large_art_url
	album.artist
	'''	
	def __init__(self,
				id=None,
				band_id=None,
				title=None,
				release_date=None,
				downloadable=None,
				url=None,
				tracks=None,
				about=None,
				credits=None,
				small_art_url=None,
				large_art_url=None,
				artist=None):
		self._id = id
		self._band_id = band_id
		self._title = title
		self._release_date = release_date
		self._downloadable = downloadable
		self._url = url
		self._tracks = tracks
		self._about = about
		self._credits = credits
		self._small_art_url = small_art_url
		self._large_art_url = large_art_url
		self._artist = artist
		
	def GetId(self):
		'''Get the unique id of this album.'''
		
		return self._id
		
	def _SetId(self, id):
		'''Set the unique id of this album.'''
		self._id = id
	
	id = property(GetId, _SetId, doc='The unique id of this album.')
	
	def GetBandId(self):
		'''Get the unqiue band id of this album.'''
		
		return self._band_id
		
	def _SetBandId(self, band_id):
		'''Set the unique band id of this album.'''
		self._band_id = band_id
	
	band_id = property(GetBandId, _SetBandId, doc='The unique id of the band who created this album.')
	
	def GetTitle(self):
		'''Get the title of this album'''
		
		return self._title
		
	def _SetTitle(self, title):
		'''Set the title of this album.'''
		self._title = title
	
	title = property(GetTitle, _SetTitle, doc='The title of this album.')
	
	def GetReleaseDate(self):
		'''Get the date this album was released.'''
		
		return self._release_date
		
	def _SetReleaseDate(self, release_date):
		'''Set the date this album was released.'''
		self._release_date = release_date
		
	release_date = property(GetReleaseDate, _SetReleaseDate, doc='The date this album was released.')
		
	def GetDownloadable(self):
		'''Get whether or not this album is downloadable.  1 = free, 2 = paid, None = not downloadable'''	
		return self._downloadable
		
	def _SetDownloadable(self, downloadable):
		'''Set whether or not this album is downloadable'''
		self._downloadable = downloadable
		
	downloadable = property(GetDownloadable, _SetDownloadable, doc='Determines if album is downloadable')

	def GetUrl(self):
		'''Get the url of this album.'''
		return self._url
		
	def _SetUrl(self, url):
		'''Set the url of this album.'''
		self._url = url
	
	url = property(GetUrl, _SetUrl, doc='The url of this album.')
	
	def GetTracks(self):
		'''Get the tracks for this album.'''
		return self._tracks
		
	def _SetTracks(self, tracks):
		'''Set the tracks for this album.'''
		self._tracks = tracks
		
	tracks = property(GetTracks, _SetTracks, doc='The tracks on this album.')

	def GetAbout(self):
		'''Get the about info for this album.'''
		return self._about
		
	def _SetAbout(self, about):
		'''Set the about info for this album.'''
		
	about = property(GetAbout, _SetAbout, doc='The about info for this album.')
	
	def GetCredits(self):
		'''Get the credits for this album.'''
		return self._credits
		
	def _SetCredits(self, credits):
		'''Set the credits for this album.'''
		self._credits = credits
	
	credits = property(GetCredits, _SetCredits, doc='The credits for this album.')
	
	def GetSmallArtUrl(self):
		'''Get the small album art.  100x100'''
		return self._small_art_url
		
	def _SetSmallArtUrl(self, small_art_url):
		'''Set the small album art for this album.'''
		self._small_art_url = small_art_url
		
	small_art_url = property(GetSmallArtUrl, _SetSmallArtUrl, doc='The small album art url. Image size: 100x100')

	def GetLargeArtUrl(self):
		'''Get the small album art.  350x350'''
		return self.large_art_url
		
	def _SetLargeArtUrl(self, large_art_url):
		'''Set the small album art for this album.'''
		self.large_art_url = large_art_url
		
	large_art_url = property(GetLargeArtUrl, _SetLargeArtUrl, doc='The large album art url. Image size: 350x350')
	
	def GetArtist(self):
		'''Get the album art artist, if different than band's name.'''
		return self._artist
		
	def _SetArtist(self, artist):
		'''Set the album art artist.'''
		self._artist = artist
		
	artist = property(GetArtist, _SetArtist, doc='The album art artist, if different than the band\'s name.')

	def AsJsonString(self):
		'''A JSON string representation of this bandcamp.Album instance.

	    Returns:
	      A JSON string representation of this bandcamp.Album instance
		'''
		return simplejson.dumps(self.AsDict(), sort_keys=True)
	
	def AsDict(self):
		'''A dict representation of this bandcamp.Album instance.

		The return value uses the same key names as the JSON representation.

		Return:
			A dict representing this bandcamp.Album instance
		'''
		data = {}
		if self.id:
			data['id'] = self.id
		if self.band_id:
			data['band_id'] = self.band_id
		if self.title:
			data['title'] = self.title
		if self.release_date:
			data['release_date'] = self.release_date
		if self.downloadable:
			data['downloadable'] = self.downloadable
		if self.url:
			data['url'] = self.url
		if self.tracks:
			data['tracks'] = self.tracks
		if self.about:
			data['about'] = self.about
		if self.credits:
			data['credits'] = self.credits
		if self.small_art_url:
			data['small_art_url'] = self.small_art_url
		if self.large_art_url:
			data['large_art_url'] = self.large_art_url
		if self.artist:
			data['artist'] = self.artist
		
		return data

	@staticmethod
	def NewFromJsonDict(data):
		'''Create a new instance based on a JSON dict.

		Args:
		  data: A JSON dict, as converted from the JSON in the bandcamp API
		Returns:
		  A bandcamp.Album instance
		'''
		# need to convert json tracks to tracks
		tracks = [Track.NewFromJsonDict(x) for x in data['tracks']]
	
		return Album(id=data.get("album_id", None),
					band_id=data.get("band_id", None),
					title=data.get("title", None),
					release_date=data.get("release_date", None),
					downloadable=data.get("downloadable", None),
					url=data.get("url", None),
					tracks=tracks,
					about=data.get("about", None),
					credits=data.get("credits", None),
					small_art_url=data.get("small_art_url", None),
					large_art_url=data.get("large_art_url", None),
					artist=data.get("artist", None))
					
class Track(object):
	'''A class representing the Track structure used by the bandcamp API.
	
	The Track structure exposes the following properties:
	
	track.id
	track.album_id
	track.band_id
	track.number
	track.title
	track.about
	track.credits
	track.streaming_url
	track.duration
	track.downloadable
	track.url
	track.lyrics
	'''
	
	def __init__(self,
				id=None,
				album_id=None,
				band_id=None,
				number=None,
				title=None,
				about=None,
				credits=None,
				streaming_url=None,
				duration=None,
				downloadable=None,
				url=None,
				lyrics=None):
		self.id = id
		self.album_id = album_id
		self.band_id = band_id
		self.number = number
		self.title = title
		self.about = about
		self.credits = credits
		self.streaming_url = streaming_url
		self.duration = duration
		self.downloadable = downloadable
		self.url = url
		self.lyrics = lyrics
		
	def GetId(self):
		'''Get the unique id of this track.'''
		return self._id
		
	def _SetId(self, id):
		'''Set the unique id of this track.'''
	
	id = property(GetId, _SetId, doc='The unique id of this track.')
	
	def GetAlbumId(self):
		'''Get the album id of this track.'''
		return self._album_id
		
	def _SetAlbumId(self, album_id):
		'''Set the album id of this track.'''
		self._album_id = album_id
		
	album_id = property(GetAlbumId, _SetAlbumId, doc='The album id of this track.')
	
	def GetBandId(self):
		'''Get the band id of this track.'''
		return self._band_id
		
	def _SetBandId(self, band_id):
		'''Set the band id of this track.'''
		self._band_id = band_id
		
	band_id = property(GetBandId, _SetBandId, doc='The band id of this track.')
	
	def GetNumber(self):
		'''Get the track number of this track.'''
		return self._number
		
	def _SetNumber(self, number):
		'''Set the track number of this track.'''
		self._number = number
	
	number = property(GetNumber, _SetNumber, doc='The track number of this track.')
	
	def GetTitle(self):
		'''Get the title of this track.'''
		
		return self._title
		
	def _SetTitle(self, title):
		'''Set the title of this track.'''
		self._title = title
	
	title = property(GetTitle, _SetTitle, doc='The title of this track.')
	
	def GetAbout(self):
		'''Get the about info for this track.'''
		return self._about
		
	def _SetAbout(self, about):
		'''Set the about info for this track.'''
		
	about = property(GetAbout, _SetAbout, doc='The about info for this track.')

	def GetCredits(self):
		'''Get the credits for this track.'''
		return self._credits
		
	def _SetCredits(self, credits):
		'''Set the credits for this track.'''
		self._credits = credits
	
	credits = property(GetCredits, _SetCredits, doc='The credits for this track.')

	def GetStreamingUrl(self):
		'''Get streaming url for this track.'''
		return self._streaming_url
		
	def _SetStreamingUrl(self, streaming_url):
		'''Set streaming url for this track.'''
		self._streaming_url = streaming_url
		
	streaming_url = property(GetStreamingUrl, _SetStreamingUrl, doc='The streaming url for this track.')
	
	def GetDuration(self):
		'''Get the duration of this track.'''
		return self._duration
		
	def _SetDuration(self, duration):
		'''Set the duration of this track.'''
		self._duration = duration
		
	duration = property(GetDuration, _SetDuration, doc='The duration of this track, in seconds (float)')

	def GetDownloadable(self):
		'''Get whether or not this track is downloadable.'''	
		return self._downloadable
		
	def _SetDownloadable(self, downloadable):
		'''Set whether or not this track is downloadable'''
		self._downloadable = downloadable
		
	downloadable = property(GetDownloadable, _SetDownloadable, doc='Determines if track is downloadable. 1 = free, 2 = paid, None = not downloadable')
	
	def GetUrl(self):
		'''Get the url of this track.'''
		return self._url
		
	def _SetUrl(self, url):
		'''Set the url of this track.'''
		self._url = url
		
	url = property(GetUrl, _SetUrl, doc='The url of this track.')
	
	def GetLyrics(self):
		'''Get the lyrics of this track.'''
		return self._lyrics
		
	def _SetLyrics(self, lyrics):
		'''Set the lyrics of this track.'''
		self._lyrics = lyrics
		
	lyrics = property(GetLyrics, _SetLyrics, doc='The lyrics of this track.')
	
	def AsJsonString(self):
		'''A JSON string representation of this bandcamp.Track instance.

	    Returns:
	      A JSON string representation of this bandcamp.Track instance
		'''
		return simplejson.dumps(self.AsDict(), sort_keys=True)

	def AsDict(self):
		'''A dict representation of this bandcamp.Track instance.

		The return value uses the same key names as the JSON representation.

		Return:
			A dict representing this bandcamp.Track instance
		'''
		data = {}
		if self.id:
			data['id'] = self.id
		if self.album_id:
			data['album_id'] = self.album_id
		if self.band_id:
			data['band_id'] = self.band_id
		if self.number:
			data['number'] = self.number
		if self.title:
			data['title'] = self.title
		if self.about:
			data['about'] = self.about
		if self.credits:
			data['credits'] = self.credits
		if self.streaming_url:
			data['streaming_url'] = self.streaming_url
		if self.duration:
			data['duration'] = self.duration
		if self.downloadable:
			data['downloadable'] = self.downloadable
		if self.url:
			data['url'] = self.url
		if self.lyrics:
			data['lyrics'] = self.lyrics

		return data

	@staticmethod
	def NewFromJsonDict(data):
		'''Create a new instance based on a JSON dict.

		Args:
		  data: A JSON dict, as converted from the JSON in the bandcamp API
		Returns:
		  A bandcamp.Track instance
		'''
		
		return Track(id=data.get("track_id", None),
					album_id=data.get("album_id", None),
					band_id=data.get("band_id", None),
					number=data.get("number", None),
					title=data.get("title", None),
					about=data.get("about", None),
					credits=data.get("credits", None),
					streaming_url=data.get("streaming_url", None),
					duration=data.get("duration", None),
					downloadable=data.get("downloadable", None),
					url=data.get("url", None),
					lyrics=data.get("lyrics", None))	
						
class Api(object):
	'''A python interface into the Bandcamp API.
	
	By default, the Api caches results for 1 minute.
	
	Example usage:
	
		To create an instance of the bandcamp.Api class:
		
		  >>> import bandcamp
		  >>> api = bandcamp.Api(key)
		
		To fetch a band:
		
		  >>> band = api.GetBand(band_id)
		  >>> print band


	Included Methods:
		api.GetBand(band_id, band_subdomain, band_url)
		api.GetAlbum(album_id)
		api.GetTrack(track_id)
	'''
	
	DEFAULT_CACHE_TIMEOUT = 60 # cache for 1 minute
	_API_REALM = 'Bandcamp API'
	
	def __init__(self,
				developer_key=None,
				cache_timeout=DEFAULT_CACHE_TIMEOUT,
				cache=DEFAULT_CACHE,
				base_url=None,
				debugHTTP=False):
		'''Instantiate a new bandcamp.Api object.
		
		Args:
			key:
				Your Bandcamp developer key.
			cache:
				The cache instance to use.  Defaults to DEFAULT_CACHE.
				Use None to disable caching. [Optional]
			debugHTTP:
				Set to True to enable deboug output from urllib2 when performing
				any HTTP requests.  Defaults to False. [Optional]
		
		'''
		self.SetCache(cache)
		self._urllib			= urllib2
		self._cache_timeout		= cache_timeout
		self._debugHTTP			= debugHTTP
		#self._InitializeUserAgent()
		self._InitializeDefaultParameters()

		if base_url is None:
			self.base_url = 'https://api.bandcamp.com/api/'
		else:
			self.base_url = base_url

		if developer_key is None:
			raise BandcampError('Bandcamp requires a developer key for all API access. \
							Please email support@bandcamp.com with your name and contact email to get access.')

		self.SetCredentials(developer_key)

	def SetCredentials(self,
						developer_key=None):
		'''Set the developer key for this instance

	    Args:
	      key:
	        The developer key of the bancamp account.
		'''
		self._developer_key = developer_key
		self._default_params['key'] = self._developer_key

	def ClearCredentials(self):
		'''Clear the any credentials for this instance.'''
		self._developer_key = None
		self._default_params['key'] = None
		
	def GetBand(self,
				band_id=None,
				band_subdomain=None,
				band_url=None):
		'''Fetch the bandcamp.Band for the given band_id.
		
		Must provide one of the three arguments.
		
		Args:
			band_id:
				The band id you want to fetch. [Optional]
			band_subdomain:
				The band subdomain you want to fetch. [Optional]
			band_url:
				The band url you want to fetch. [Optional]
				
		Returns:
			A bandcamp.Band instance
		'''
		
		if band_id is None and band_subdomain is None and band_url is None:
			raise BandcampError('GetBand requires at least one of the three arguments: band_id, band_subdomain, band_url.')
			
		parameters = {}
		
		if band_id:
			parameters['band_id'] = band_id
		elif band_subdomain:
			parameters['band_url'] = band_subdomain
		elif band_url:
			parameters['band_url'] = band_url
			
		url = '%s/band/1/info' % self.base_url
		json = self._FetchUrl(url, parameters=parameters)
		data = simplejson.loads(json)
		
		return Band.NewFromJsonDict(data)
	
	def GetDiscography(self,
						band_id=None,
						band_subdomain=None,
						band_url=None):
		'''Fetch the '''
		
		if band_id is None and band_subdomain is None and band_url is None:
			raise BandcampError('GetDiscography requires at least one of the three arguments: band_id, band_subdomain, band_url.')
		
		parameters = {}
		
		if band_id:
			parameters['band_id'] = band_id
		elif band_subdomain:
			parameters['band_url'] = band_subdomain
		elif band_url:
			parameters['band_url'] = band_url
			
		url = '%s/band/1/discography' % self.base_url
		json = self._FetchUrl(url, parameters=parameters)
		data = simplejson.loads(json)
		
		self._CheckForBandcampError(data)
		
		results = []		
		for x in data['discography']:
			if x['track_id']:
				results.append(Track.NewFromJsonDict(x))
			if x['album_id']:
				results.append(Album.NewFromJsonDict(x))
		
		# Return built list of discography
		return results
		
	def GetAlbum(self, album_id):
		'''Fetch the bandcamp.Album for the given album_id.

		Args:
			album_id:
				The album id you want to fetch.
		
		Returns:
			A bandcamp.Album instance
		'''
		parameters = {}
		parameters['album_id'] = album_id
			
		url = '%s/album/1/info' % self.base_url
		json = self._FetchUrl(url, parameters=parameters)
		data = simplejson.loads(json)
		
		self._CheckForBandcampError(data)
		
		return Album.NewFromJsonDict(data)
		
	def GetTrack(self, track_id):
		'''Fetch the bandcamp.Track for the given track_id.
		
		Args:
			track_id:
				The track id you want to fetch.
				
		Returns:
			A bandcamp.Track instance
		'''
		parameters = {}
		parameters['track_id'] = track_id
			
		url = '%s/track/1/info' % self.base_url
		json = self._FetchUrl(url, parameters=parameters)
		data = simplejson.loads(json)
		
		self._CheckForBandcampError(data)
		
		return Track.NewFromJsonDict(data)
	
	def SetCache(self, cache):
		'''Override the default cache.  Set to None to prevent caching.
		
		Args:
			cache:
				An instance that supports the same API as the bandcamp._FileCache
		'''
		if cache == DEFAULT_CACHE:
			self._cache = _FileCache()
		else:
			self._cache = cache

	def SetCacheTimeout(self, cache_timeout):
		'''Override the default cache timeout.

		Args:
			cache_timeout:
				Time, in seconds, that response should be reused.
		'''
		self._cache_timeout = cache_timeout
			
	def SetUrllib(self, urllib):
		'''Override the default urllib implmentation.
		
		Args:
			urllib:
				An instance that supporst the same API as the urllib2 module
			
		'''
		self._urllib = urllib
		
	def _InitializeDefaultParameters(self):
		self._default_params = {}
		
	def _CheckForBandcampError(self, data):
		'''Raises a BandcampError if bandcamp returns an error message.
		
		Args:
			data:
				A python dict created from the Bandcamp json response
				
		Raises:
			BandcampError wrapping the bandcamp error message if one exists.
		'''
		
		# Bandcamp errors are relatively unlikely, so it is faster
		# to check first, rather than try and catch the exception.
		if 'error' in data:
			raise BandcampError(data['error'])
			
	def _FetchUrl(self,
				  url,
				  post_data=None,
				  parameters=None,
				  no_cache=None):
		'''Fetch a URL, optional caching for a sepcified time.
		
		Args:
			url:
				The URL to retrieve
			post_data:
				A dict of (str, unicode) key/value pairs.
				If set, POST will be used [Optional]
			parameters:
				A dict whose key/value pairs should be encoded
				and added to the query string. [Optional]
			no_cache:
				If true, overrides the cache on the current request.
				
		Returns:
			A string containing the body of the response.
		'''
		
		# Build the extra parameteres dict
		extra_params = {}
		if self._default_params:
			extra_params.update(self._default_params)
		if parameters:
			extra_params.update(parameters)
			
		http_method = "GET"
		if post_data:
			http_method = "POST"
			
		_debug = 0
		if self._debugHTTP:
			_debug = 1
			
		http_handler = self._urllib.HTTPHandler(debuglevel=_debug)
		https_handler = self._urllib.HTTPSHandler(debuglevel=_debug)
		
		opener = self._urllib.OpenerDirector()
		opener.add_handler(http_handler)
		opener.add_handler(https_handler)
		
		url = self._BuildUrl(url, extra_params=extra_params)
		encoded_post_data = self._EncodePostData(post_data)
		
		# Open and return the URL immediately if we're not going to cache
		if encoded_post_data or no_cache or not self._cache or not self._cache_timeout:
			response = opener.open(url, encoded_ost_data)
			url_data = self._DecompressGzippedResponse(response)
			opener.close()
		else:
			# Unique keys are a combination of the url and the developer key
			if self._developer_key:
				key = self._developer_key + ':' + url
			else:
				key = url
				
			# See if it has been cached before
			last_cached = self._cache.GetCachedTime(key)
			
			# If the cached version is outdated then fetch another and store it
			if not last_cached or time.time() >= last_cached + self._cache_timeout:
				try:
					response = opener.open(url, encoded_post_data)
					url_data = self._DecompressGzippedResponse(response)
					self._cache.Set(key, url_data)
				except urllib2.HTTPError, e:
					print e
				opener.close()
			else:
				url_data = self._cache.Get(key)
		
		# Alwyas return the latest version
		return url_data
		
	def _BuildUrl(self, url, path_elements=None, extra_params=None):
		# Break url into consituent parts
		(scheme, netloc, path, params, query, fragment) = urlparse.urlparse(url)
		
		# Add any additional path elements to the path
		if path_elements:
			#Filter out the path elements that have a value of None
			p = [i for i in path_elemnts if i]
			if not path.endswith('/'):
				path += '/'
			path += '/'.join(p)
		
		# Add any additional query parameters to the query string
		if extra_params and len(extra_params) > 0:
			extra_query = self._EncodeParameters(extra_params)
			# Add it to the existing query
			if query:
				query += '&' + extra_query
			else:
				query = extra_query
		
		# Return the rebuilt URL
		return urlparse.urlunparse((scheme, netloc, path, params, query, fragment))

	def _DecompressGzippedResponse(self, response):
		raw_data = response.read()
		if response.headers.get('content-encoding', None) == 'gzip':
			url_data = gzip.GzipFile(fileobj=StringIO.StringIO(raw_data)).read()
		else:
			url_data = raw_data
		return url_data

	def _Encode(self, s):
		'''if self._input_encoding:
			return unicode(s, self._input_encoding).encode('utf-8')
		else:'''
		return unicode(s).encode('utf-8')

	def _EncodeParameters(self, parameters):
		'''Return a string in key=value&key=value form
		
		Values of None are not included in the output string.
		
		Args:
			parameters:
				A dict of (key, value) tuples, where value is encoded as
				specified by self._encoding
				
		Returns:
			A URL-encoded string in "key=value&key=value" form
		'''
		
		if parameters is None:
			return None
		else:
			return urllib.urlencode(dict([(k, self._Encode(v)) for k, v in parameters.items() if v is not None]))
	
	def _EncodePostData(self, post_data):
		'''Return a string in key=value&key=value form
		
		Values are assumed to be encoded in the format sprecified by self._encoding,
		and are subsequently URL encoded.
		
		Args:
			post_data:
				A dict of (key, value) tuples, where value is encoded as specified by self._encoding
				
		Returns:
			A URL-encoded string in "key=value&key=value" form
		'''
		if post_data is None:
			return None
		else:
			return urllib.urlencode(dict([(k, self._Encode(v)) for k, v in post_data.items()]))

class _FileCacheError(Exception):
	'''Base exception class for Fileache related errors'''
	
class _FileCache(object):
	
	DEPTH = 3
	
	def __init__(self, root_directory=None):
		self._InitializeRootDirectory(root_directory)
		
	def Get(self, key):
		path = self._GetPath(key)
		if os.path.exists(path):
			return open(path).read()
		else:
			return None
	def Set(self, key, data):
		path = self._GetPath(key)
		directory = os.path.dirname(path)
		if not os.path.exists(directory):
			os.makedirs(directory)
		if not os.path.isdir(directory):
			raise _FileCacheError('%s exists but is not a direcotyr' % directory)
		temp_fd, temp_path = tempfile.mkstemp()
		temp_fp = os.fdopen(temp_fd, 'w')
		temp_fp.write(data)
		temp_fp.close()
		if not path.startswith(self._root_directory):
			raise _FileCacheError('%s does not appear to live under %s' %
									(path, self._root_directory))
		
		if os.path.exists(path):
			os.remove(path)
		os.rename(temp_path, path)
		
	def Remove(self, key):
		path = self._GetPath(key)
		if not path.startswith(self._root_diretory):
			raise _FileCacheError('%s does not appear to live under %s' %
									(path, self._root_directory))
		
		if os.path.exists(path):
			os.remove(path)
	
	def GetCachedTime(self, key):
		path = self._GetPath(key)
		if os.path.exists(path):
			return os.path.getmtime(path)
		else:
			return None
		
	def _GetUsername(self):
		'''Attempt to find the username in a cross-platform fashion.'''
		try:
			return os.getenv('USER') or \
					os.getenv('LOGNAME') or \
					os.getenv('USERNAME') or \
					os.getlogin() or \
					'nobody'
		except (IOError, OSError):
			return 'nobody'
	
	def _GetTmpCachePath(self):
		username = self._GetUsername()
		cache_directory = 'python.cache_' + username
		return os.path.join(tempfile.gettempdir(), cache_directory)
		
	def _InitializeRootDirectory(self, root_directory):
		if not root_directory:
			root_directory = self._GetTmpCachePath()
		root_directory = os.path.abspath(root_directory)
		if not os.path.exists(root_directory):
			os.mkdir(root_directory)
		if not os.path.isdir(root_directory):
			raise _FileCacheError('%s exists but is not a direcotry' % root_direcotry)
		
		self._root_directory = root_directory
		
	def _GetPath(self, key):
		try:
			hashed_key = md5(key).hexdigest()
		except TypeError:
			hashed_key = md5.new(key).hexdigest()
		
		return os.path.join(self._root_directory,
							self._GetPrefix(hashed_key),
							hashed_key)

	def _GetPrefix(self, hashed_key):
		return os.path.sep.join(hashed_key[0:_FileCache.DEPTH])
		
			