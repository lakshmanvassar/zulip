from __future__ import absolute_import

import requests
import json

from typing import Optional, Text

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.utils.translation import ugettext as _

from zerver.lib.push_notifications import add_push_device_token, \
    b64_to_hex, remove_push_device_token
from zerver.lib.request import has_request_variables, REQ, JsonableError
from zerver.lib.response import json_success, json_error
from zerver.lib.validator import check_string, check_list, check_bool
from zerver.models import PushDeviceToken, UserProfile

def validate_token(token_str, kind):
    # type: (bytes, int) -> None
    if token_str == '' or len(token_str) > 4096:
        raise JsonableError(_('Empty or invalid length token'))
    if kind == PushDeviceToken.APNS:
        # Validate that we can actually decode the token.
        try:
            b64_to_hex(token_str)
        except Exception:
            raise JsonableError(_('Invalid APNS token'))

@has_request_variables
def add_apns_device_token(request, user_profile, token=REQ(),
                          appid=REQ(default=settings.ZULIP_IOS_APP_ID)):
    # type: (HttpRequest, UserProfile, bytes, str) -> HttpResponse
    validate_token(token, PushDeviceToken.APNS)
    add_push_device_token(user_profile, token, PushDeviceToken.APNS, ios_app_id=appid)
    return json_success()

@has_request_variables
def add_android_reg_id(request, user_profile, token=REQ()):
    # type: (HttpRequest, UserProfile, bytes) -> HttpResponse
    validate_token(token, PushDeviceToken.GCM)
    add_push_device_token(user_profile, token, PushDeviceToken.GCM)
    return json_success()

@has_request_variables
def remove_apns_device_token(request, user_profile, token=REQ()):
    # type: (HttpRequest, UserProfile, bytes) -> HttpResponse
    validate_token(token, PushDeviceToken.APNS)
    remove_push_device_token(user_profile, token, PushDeviceToken.APNS)
    return json_success()

@has_request_variables
def remove_android_reg_id(request, user_profile, token=REQ()):
    # type: (HttpRequest, UserProfile, bytes) -> HttpResponse
    validate_token(token, PushDeviceToken.GCM)
    remove_push_device_token(user_profile, token, PushDeviceToken.GCM)
    return json_success()
