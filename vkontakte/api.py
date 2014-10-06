# coding: utf-8
import random
import time
import warnings
from hashlib import md5
from functools import partial
try:
    import simplejson as json
except ImportError:
    import json

import requests


SECURE_API_URL = 'https://api.vk.com/method/'
DEFAULT_TIMEOUT = 1
REQUEST_ENCODING = 'utf8'


# See full list of VK API methods here:
# http://vk.com/developers.php?o=-1&p=%D0%A0%D0%B0%D1%81%D1%88%D0%B8%D1%80%D0%B5%D0%BD%D0%BD%D1%8B%D0%B5_%D0%BC%D0%B5%D1%82%D0%BE%D0%B4%D1%8B_API&s=0
# http://vk.com/developers.php?o=-1&p=%D0%9E%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B5_%D0%BC%D0%B5%D1%82%D0%BE%D0%B4%D0%BE%D0%B2_API&s=0
COMPLEX_METHODS = ['secure', 'ads', 'messages', 'likes', 'friends',
    'groups', 'photos', 'wall', 'board', 'newsfeed', 'notifications', 'audio',
    'video', 'docs', 'places', 'storage', 'notes', 'pages',
    'activity', 'offers', 'questions', 'subscriptions', 'database',
    'users', 'status', 'polls', 'account', 'auth', 'stats']


class VKError(Exception):
    __slots__ = ["error"]
    def __init__(self, error_data):
        self.error = error_data
        Exception.__init__(self, str(self))

    @property
    def code(self):
        return self.error['error_code']

    @property
    def description(self):
        return self.error['error_msg']

    @property
    def params(self):
        return self.error['request_params']

    @property
    def captcha(self):
        data = None
        if self.code == 14: # Capcha needed error
            data = {
                'sid': self.error['captcha_sid'],
                'img': self.error['captcha_img'],
            }
        return data

    @property
    def redirect_uri(self):
        data = None
        if self.code == 17: # Validation required
            data = self.error['redirect_uri']
        return data


    def __str__(self):
        return "Error(code = '%s', description = '%s', params = '%s', captcha = '%s', redirect_uri = '%s')" % (self.code, self.description, self.params, self.captcha, self.redirect_uri)


def _json_iterparse(response):
    response = response.strip()
    decoder = json.JSONDecoder(strict=False)
    idx = 0
    while idx < len(response):
        obj, idx = decoder.raw_decode(response, idx)
        yield obj


class _API(object):
    def __init__(self, api_id=None, token=None, **defaults):

        if not (api_id or token):
            raise ValueError("Arguments api_id or token are required")

        self.api_id = api_id
        self.token = token
        self.defaults = defaults
        self.method_prefix = ''

    def _get(self, method, timeout=DEFAULT_TIMEOUT, **kwargs):
        response = self._request(method, timeout=timeout, **kwargs)
        status = response.status_code

        if not (200 <= status <= 299):
            raise VKError({
                'error_code': status,
                'error_msg': "HTTP error",
                'request_params': kwargs,
            })

        # there may be a response after errors
        errors = []
        for data in _json_iterparse(response.text):
            if "error" in data:
                errors.append(data["error"])
            if "response" in data:
                for error in errors:
                    warnings.warn("%s" % error)
                return data["response"]

        raise VKError(errors[0])

    def __getattr__(self, name):
        '''
        Support for api.<method>.<methodName> syntax
        '''
        if name in COMPLEX_METHODS:
            api = _API(api_id=self.api_id, token=self.token, **self.defaults)
            api.method_prefix = name + '.'
            return api

        # the magic to convert instance attributes into method names
        return partial(self, method=name)

    def __call__(self, **kwargs):
        method = kwargs.pop('method')
        params = self.defaults.copy()
        params.update(kwargs)
        return self._get(self.method_prefix + method, **params)


    def _request(self, method, timeout=DEFAULT_TIMEOUT, **kwargs):
        params = dict(
            access_token=self.token,
        )
        params.update(kwargs)
        params['timestamp'] = int(time.time())
        url = SECURE_API_URL + method

        headers = {"Accept": "application/json",
                   "Content-Type": "application/x-www-form-urlencoded"}

        return requests.post(url, data=params, headers=headers, timeout=timeout)


class API(_API):

    def get(self, method, timeout=DEFAULT_TIMEOUT, **kwargs):
        return self._get(method, timeout, **kwargs)
