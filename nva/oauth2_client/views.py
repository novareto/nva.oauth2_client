# -*- coding: utf-8 -*-

import grok
import json
import urllib2
import uvcsite

from urllib2 import HTTPError, URLError
from oauth2.compatibility import urlencode
from uvcsite.interfaces import IMyHomeFolder
from zope.app.homefolder.interfaces import IHomeFolder
from zope.app.appsetup.product import getProductConfiguration
from grokcore.chameleon.components import ChameleonPageTemplateFile

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


class RequestAccessTokenMenu(uvcsite.MenuItem):
    grok.title(u'Access Token erstellen')
    grok.require('zope.View')
    grok.viewletmanager(uvcsite.IPersonalMenu)

    @property
    def action(self):
        return self.view.url(
            IHomeFolder(self.request.principal).homeFolder, 'request_token')


class RequestToken(uvcsite.Page):
    grok.context(IMyHomeFolder)
    grok.name('request_token')
    grok.require('uvc.EditContent')

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
            print e
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
