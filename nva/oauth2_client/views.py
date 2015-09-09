# -*- coding: utf-8 -*-

import grok
import json
import urllib2
from urllib2 import HTTPError, URLError
from uvc.api import Page
from dolmen.forms.base import ApplicationForm
from zope.interface import Interface
from grokcore.chameleon.components import ChameleonPageTemplateFile
from oauth2.compatibility import urlencode
from uvcsite.content.api import RestLayer
from uvcsite.interfaces import IUVCSite

grok.templatedir('templates')


no_service = {
    "error": "Service Unavailable",
    "error_description": ("The access granting service is not available"
                          " at the moment. Please try later"),
    }

no_authorization = {
    "error": "Request is malformed",
    "error_description": ("Request can't be processed. "
                          "Make sure the 'Authorization' header is set."),
    }

auth_header_malformed = {
    "error": "Authorization header is malformed",
    "error_description": ("Request can't be processed. Make sure "
                          "the 'Authorization' header is set properly."),
    }

token_expired = {
    "error": "The token is expired",
    "error_description": "The access token is no longer valid.",
    }

invalid_token = {
    "error": "The token is invlid",
    "error_description": "The access token is not valid.",
    }


class RequestToken(Page):
    grok.context(Interface)
    grok.require('zope.Public')

    client_id = "novareto"
    client_secret = "test"

    template = ChameleonPageTemplateFile('templates/request.cpt')

    @property
    def token_endpoint(self):
        config = getProductConfiguration('oauth2')
        return config.get('token_endpoint', False)

    def login(self):
        params = {
            "grant_type": "password",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": self.request.form.get('username', ''),
            "password": self.request.form.get('password', ''),
        }
        try:
            response = urllib2.urlopen(self.token_endpoint, urlencode(params))
        except HTTPError as he:
            if he.code == 400:
                error_body = json.loads(he.read())
                return 400, error_body, None
            if he.code == 401:
                return 401, None, None
        except URLError as e:
            return 503, no_service, None

        token = json.load(response)
        return 200, None, token

    def update(self):
        self.action = self.request.getURL()
        method = self.request.method.lower()
        if method == 'post':
            self.code, self.error, self.token = self.login()
        else:
            self.code = None
            self.error = None
            self.token = None


class APIPage(grok.REST):
    grok.layer(RestLayer)
    grok.context(IUVCSite)
    grok.require('zope.View')
    
    template = ChameleonPageTemplateFile('templates/secret.cpt')

    def GET(self):
        return "SECRET !"

    
    # def verify(self, token):
    #     params = {
    #         "access_token": token,
    #     }
    #     try:
    #         response = urllib2.urlopen(self.token_endpoint, urlencode(params))
    #     except HTTPError as he:
    #         error_body = json.loads(he.read())
    #         return 401, error_body
    #     except URLError as e:
    #         return 503, no_service

    #     token = json.load(response)
    #     return 200, token

    # def set_error(self):
    #     if self.code != 200:
    #         self.request.response.setStatus(401)
    #         self.request.response.setHeader(
    #             'Expires', 'Mon, 26 Jul 1997 05:00:00 GMT')
    #         self.request.response.setHeader(
    #             'Cache-Control', 'no-store, no-cache, must-revalidate')
    #         self.request.response.setHeader(
    #             'Pragma', 'no-cache')
    #         self.template = self.error_template

    # def update(self):
    #     self.data = {}
    #     authorization = self.request._auth
    #     if authorization:
    #         ctype, token = authorization.split(' ', 1)
    #         if ctype == 'Bearer' and token:
    #             self.code, self.data = self.verify(token)
    #             if self.code != 200:
    #                 self.error = self.data
    #         else:
    #             self.code = 401
    #             self.error = auth_header_malformed
    #     else:
    #         self.code = 400
    #         self.error = no_authorization

    #     self.set_error()
