# coding: utf-8
__author__ = 'evanwu'

import sys
import base64
import requests
import json
import datetime,time


""" A simple library for Topsy Web API (http://api.topsy.com/doc/)
"""


class TopsipyExcepetion(Exception):
    def __init__(self, http_status, code, msg):
        self.http_status = http_status
        self.code = code
        self.msg = msg

    def __str__(self):
        return u'http status:{0}, code:{1} - {2}'.format(self.http_status, self.code, self.msg)


class Topsipy(object):

    """
        Example usage::
            import topsipy

            tp = topsipy.Topsipy()

    """
    trace = False  # Enable tracing?
    max_get_retries = 5  # Max attempts for GET request

    def __init__(self, api_key='', requests_session=True, client_credentials_manager=None):

        """
            Create a Topsipy API object.
            :param api_kei:
            The api key allows you to send the request to Topsy API.
            :param requests_session:
            A Requests session object or a truthy value to create one.
            A False value disables sessions.
            It should generally be a good idea to keep sessions enabled
            for performance reasons.
            :param client_credentials_manager:
            TopsipyClientCredentials object
        """
        self.prefix = 'http://api.topsy.com/v2/'
        self.client_credentials_manager = client_credentials_manager
        self.api_key = api_key

        if isinstance(requests_session, requests.Session):
            self._session = requests_session
        else:
            if requests_session:  # Build a new session.
                self._session = requests.Session()
            else:  # Use the Requests API module as a "session".
                from requests import api
                self._session = api

    def _internal_call(self, method, url, payload=None, params={}):
        params['apikey']=self.api_key
        args = dict(params=params)

        if not url.startswith('http'):
            url = self.prefix + url

        headers={}

        if payload:
            args["data"] = json.dumps(payload)

        r = self._session.request(method, url, headers=headers, **args)

        if self.trace:
            print()
            print(method, r.url)
            if payload:
                print("DATA", json.dumps(payload))

        try:
            r.raise_for_status()
        except:
            raise TopsipyExcepetion(r.status_code, -1, u'%s:\n %s' % (r.url, r.json()['error']['message']))

        if len(r.text) > 0:
            results = r.json()
            if self.trace:
                print('RESPONSE', results)
                print()
            return results
        else:
            return None

    def _get(self, url, args=None, payload=None, **kwargs):
        if args:
            kwargs.update(args)
        retries = self.max_get_retries
        while retries > 0:
            try:
                return self._internal_call('GET', url, payload, kwargs)
            except TopsipyExcepetion as e:
                if 500 <= e.http_status < 600:  # Server error
                    retries -= 1
                    if retries < 0:
                        raise
                    else:
                        time.sleep(1)
                else:
                    raise

    def _post(self, url, args=None, payload=None, **kwargs):
        if args:
            kwargs.update(args)
        return self._internal_call('POST', url, payload, kwargs)

    def _delete(self, url, args=None, payload=None, **kwargs):
        if args:
            kwargs.update(args)
        return self._internal_call('DELETE', url, payload, kwargs)

    def _put(self, url, args=None, payload=None, **kwargs):
        if args:
            kwargs.update(args)
        return self._internal_call('PUT', url, payload, kwargs)

    def next(self, result):
        """
        :param result: a previously returned paged result
        :return: the next result given a paged result
        """
        if result['next']:
           return self._get(result['next'])
        else:
           return None

    def previous(self, result):
        """
        :param result: a previously returned paged result
        :return: a previously returned paged result
        """
        if result['previous']:
           return self._get(result['previous'])
        else:
           return None

    def _warn(self, msg):
        print('warning:' + msg)

    def tweet(self, postid):
        """ Returns a tweet given a tweet id.
        If a tweet is not found, a ’200 OK’ response will still be sent, but the response body will be empty
        :param: A tweet id
        :return: a tweet
        """
        return self._get('content/tweet.json', postids=postid)

    def tweets(self, postids):
        """ Returns several tweets given tweet ids.
        If a tweet is not found, a ’200 OK’ response will still be sent, but the response body will be empty
        :param: A list of tweet ids
        :return: tweets
        """
        return self._get('content/tweet.json', postids=','.join(postids))

    def top_tweets(self, q=None, sort_by=None, offset=0, limit=5):
        """
        Provides the top tweets for a list of terms and additional search parameters.
        The ranking is determined by the sort method.
        :param q: (optional)
        Query term(s) to return matching results for.
        If omitted, trending tweets from all Twitter are shown.
        :param sort_by: (optional)
        Sort Method
        :param offset: (optional)
        Offset from which to start the results. (default=0)
        :param limit: (optional)
        Maximum number of results returned. (default: 5, max: 500).
        :return: List of tweets
        """
        return self._get('content/tweets.json', q=q, sort_by=sort_by, offset=offset, limit=limit)

