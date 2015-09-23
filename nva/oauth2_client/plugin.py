# -*- coding: utf-8 -*-

import grok
import json
import urllib2
from urllib2 import HTTPError, URLError
from oauth2.compatibility import urlencode
from zope.app.appsetup.product import getProductConfiguration
from zope.pluggableauth.interfaces import (
    IPrincipalInfo, IAuthenticatorPlugin, ICredentialsPlugin)


class BearerTokenAuthCredentialsPlugin(grok.GlobalUtility):
    grok.name('creds.bearer')
    grok.implements(ICredentialsPlugin)

    def extractCredentials(self, request):
        if not grok.IRESTLayer.providedBy(request):
            return None

        if request._auth:
            if request._auth.lower().startswith(u'bearer '):
                access_token = request._auth.split()[-1]
            return {'access_token': access_token}
        return None

    def challenge(self, request):
        if not grok.IRESTLayer.providedBy(request):
            return False
        request.response.setStatus(401)
        return True

    def logout(self, request):
        return False


class AccessTokenHolder(object):
    grok.implements(IPrincipalInfo)

    credentialsPlugin = None
    authenticatorPlugin = None

    def __repr__(self):
        return '<AccessTokenHolder "%s">' % self.id

    def __init__(self, token, infos):
        userid = infos['userid']
        client = infos['client']
        self.id = unicode(userid)
        self.title = u'Access token %r for %r (%r)' % (token, userid, client)
        self.description = u'OAuth2 access token provided for %r (%r)' % (
            userid, client)


class AuthenticateBearer(grok.GlobalUtility):
    grok.name('auth.bearer')
    grok.implements(IAuthenticatorPlugin)

    def __init__(self):
        config = getProductConfiguration('oauth2')
        self.verify_token = config.get('verify_token', False)

    def verify(self, token):
        params = {"access_token": token}
        try:
            response = urllib2.urlopen(self.verify_token, urlencode(params))
            token = json.load(response)
            return token
        except HTTPError as he:
            return None
        except URLError as e:
            return None
        else:
            return None

    def authenticateCredentials(self, credentials):
        """Return principal info if credentials can be authenticated
        """
        if not isinstance(credentials, dict):
            return None

        access_token = credentials.get('access_token')
        if access_token is None:
            return None

        infos = self.verify(access_token)
        if infos is not None:
            return AccessTokenHolder(access_token, infos)
        return None

    def principalInfo(self, id):
        return None
