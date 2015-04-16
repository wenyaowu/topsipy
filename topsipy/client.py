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

            tp = topsipy.Topsipy(api_key=API_KEY)

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

        if api_key == '':
            print 'Warn: You need to provide API key in order to use the API.'
            return

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

    def _get(self, get_url, args=None, payload=None, **kwargs):
        if args:
            kwargs.update(args)
        retries = self.max_get_retries
        while retries > 0:
            try:
                return self._internal_call('GET', get_url, payload, kwargs)
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
        """
        if result['next']:
           return self._get(result['next'])
        else:
           return None

    def previous(self, result):
        """
        :param result: a previously returned paged result
        """
        if result['previous']:
           return self._get(result['previous'])
        else:
           return None

    def _warn(self, msg):
        print('warning:' + msg)

#------------------------------------------------------------------------------------#
#                                    Content APIs:                                   #
# These resources let you retrieve every single tweet or only the most relevant ones #
# (e.g. newest or oldest tweets, tweets with the most reach) for any topic.          #
# You can also find content (links, photos and videos) shared on Twitter and all the #
# tweets related to them, among other things.                                        #
#------------------------------------------------------------------------------------#

    def tweet(self, postids):
        """ Returns tweet(s) given tweet id(s).
        If a tweet is not found, a ’200 OK’ response will still be sent, but the response body will be empty
        :param postids:
        A tweet id/ list of ids
        """
        if isinstance(postids, list):
            postid = ','.join(postids)
        return self._get('content/tweet.json', postids=postids)


    def bulktweets(self, q=None, limit=10, *args):
        """
        Provides a large set of tweets that match the specified query and filter parameters.
        The maximum number of items returned per query is 20,000.
        :param q:(optional)
        Terms to retrieve trending posts on.
        If no term is entered, then trending posts results are returned for all of Twitter.
        :param limit:(optional)
        Maximum number of results returned. (default: 10, max: 20000).
        """
        return self._get('content/bulktweets.json', q=q, limit=limit, args=args)

    def tweets(self, q=None, sort_by=None, offset=0, limit=5, *args):
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
        """
        return self._get('content/tweets.json', q=q, sort_by=sort_by, offset=offset, limit=limit, args=args)

    def photos(self, q=None, sort_by=None, offset=0, limit=5, *args):
        """
        Provides the top photos for a list of terms and additional search parameters.
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
        """
        return self._get('content/photos.json', q=q, sort_by=sort_by, offset=offset, limit=limit, args=args)

    def links(self, q=None, sort_by=None, offset=0, limit=5, *args):
        """
        Provides the top links for a list of terms and additional search parameters.
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
        """
        return self._get('content/links.json', q=q, sort_by=sort_by, offset=offset, limit=limit, args=args)

    def videos(self, q=None, sort_by=None, offset=0, limit=5, *args):
        """
        Provides the top videos for a list of terms and additional search parameters.
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
        """
        return self._get('content/videos.json', q=q, sort_by=sort_by, offset=offset, limit=limit, args=args)

    def citations(self, url=None, sort_by=None, offset=0, limit=5, *args):
        """
        Returns the full trackback history of a URL in reverse chronological order (up to 10,000 results).
        :param q_url: (optional)
        URL for the target.
        This may be a permalink for a tweet, or any other URL for a photo, video or link.
        If omitted, trending tweets from all Twitter are shown.
        :param sort_by: (optional)
        Sort Method
        :param offset: (optional)
        Offset from which to start the results. (default=0)
        :param limit: (optional)
        Maximum number of results returned. (default: 5, max: 500).
        """
        return self._get('content/citations.json', url=url, sort_by=sort_by, offset=offset, limit=limit, args=args)

    def conversation(self, url=None):
        """
        Provides the full reply thread to a specific tweet.
        :param url:The permalink of the tweet.
        """
        return self._get('content/conversation.json', url=url)

    def validate(self, postid):
        """
        Returns true if a tweet is still valid, false otherwise.
        This is useful to check for tweet deletions that occur after a tweet was first returned.
        :param postid: A comma-separated list of tweet IDs.
        """
        return self._get('content/validate.json', postid=postid)

#------------------------------------------------------------------------------------#
#                                    Metrics APIs:                                   #
# Metrics are statistics derived from analyzing the full Twitter Firehose, available #
# in real time (up to the minute) as data is being posted on Twitter, as well as     #
# going back to July 2010. Metrics are available in minute, hour, or day granularity.#                                       #
#------------------------------------------------------------------------------------#

    def mentions(self, q=None, slice=None, cumulative=0, *args):
        """
        Provides volume of tweet mentions over time for a list of keywords.
        :param q: (Optional)
        Query string.
        :param slice: (Optional)
        Value in seconds for each time slice.
        :param cumulative: (Optional)
        When enabled (cumulative=1), metrics are cumulative from previous slice values.
        """
        return self._get('metrics/mentions.json', q=q, slice=slice, cumulative=cumulative, args=args)

    def citation_metrics(self, url, *args):
        """
        Provides volume of tweet mentions over time for a list of keywords.
        :param url:
        Query string.
        """
        return self._get('metrics/mentions.json', url=url, args=args)

    def impressions(self, q=None, slice=None, cumulative=0, *args):
        """
        Provides volume of tweet mentions over time for a list of keywords.
        :param q: (Optional)
        Query string.
        :param slice: (Optional)
        Value in seconds for each time slice.
        :param cumulative: (Optional)
        When enabled (cumulative=1), metrics are cumulative from previous slice values.
        """
        return self._get('metrics/impressions.json', q=q, slice=slice, cumulative=cumulative, args=args)

    def sentiment(self, q=None, slice=None, *args):
        """
        Returns the Topsy Sentiment Score over time.
        The Topsy Sentiment Score, ranging from 0 to 100, is a normalized score based on
        sentiment on all tweet mentioning the query term(s) in the specified time period.
        :param q:(Optional)
        Query string
        :param slice:(Optional)
        Value in seconds for each time slice.
        """
        return self._get('metrics/sentiment.json', q=q, slice=slice, args=args)

    def geo(self, q=None, scope=None):
        """
        Provides mention metrics in a specific region and its corresponding subregions for a list of query terms.
        If no region is specified, mentions for all countries are returned.
        :param q:
        :param scope:
        Location filter to restrict results by city, U.S. state or country.
        If no region is specified, mentions for all countries are returned.
        """
        return self._get('metrics/geo.json', q=q, scope=scope)

#------------------------------------------------------------------------------------#
#                                    Insights APIs:                                  #
# Topsy Insights APIs leverage full-Firehose analysis to surface key influencers,    #
# hashtags, and topics related to your topic of interest.                            #
#------------------------------------------------------------------------------------#

    def related_terms(self, q=None, sort_by=None, *args):
        """
        Returns a list of related terms for terms entered.
        :param q:
        Query term(s) to return related terms for. If omitted, trending terms from all Twitter are shown.
        :param sort_by: Sorting Method.
        """
        return self._get('insights/relatedterms.json', q=q, sort_by=sort_by, args=args)

    def influencers(self, q=None, sort_by=None, *args):
        """
        Provides a list of authors who mention the specified query term(s),
        sorted by frequency of tweets and the author’s influence level.
        :param q:
        Terms to find influencers for. If no term is entered, no influencers are returned.
        :param sort_by: Sorting Method.
        """
        return self._get('insights/influencers.json', q=q, sort_by=sort_by, args=args)

    def author(self, authors, *args):
        """
        return the information of the author on twitter
        :param authors:
        Twitter author’s handle (@username), can be a comma-separated list for multiple authors.
        :return:
        """
        if isinstance(authors, list):
            authors = ','.join(authors)

        return self._get('insights/author.json', authors=authors, args=args)