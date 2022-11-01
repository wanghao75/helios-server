"""
email Authentication

"""

import httplib2
import requests
from django.conf import settings
from django.core.mail import send_mail
from oauth2client.client import OAuth2WebServerFlow

from helios_auth import utils

# some parameters to indicate that status updating is not possible
STATUS_UPDATES = False

# display tweaks
LOGIN_MESSAGE = "Log in with Email"


def get_flow(redirect_url=None):
  return OAuth2WebServerFlow(
    client_id=settings.GITEE_CLIENT_ID,
    client_secret=settings.GITEE_CLIENT_SECRET,
    scope=['user_info'],
    auth_uri="https://gitee.com/oauth/authorize",
    token_uri="https://gitee.com/oauth/token",
    redirect_uri=redirect_url,
  )


def get_auth_url(request, redirect_url):
  flow = get_flow(redirect_url)
  request.session['email_redirect_uri'] = redirect_url
  return "https://email-auth.test.osinfra.cn/auth/code"


def get_user_info_after_auth(request):
  # after auth, use token to get userinfo
  code = request.session.get('code')
  params2 = {
    "code": code,
    "grant_type": "authorization_code",
    "redirect_uri": "https://helios-voting.osinfra.cn/auth/after",
  }

  r = requests.get(url="https://email-auth.test.osinfra.cn/auth/access", params=params2)
  if r.status_code != 200:
    return None

  access_token = r.json().get("data").get("token")
  refresh_token = r.json().get("data").get("refresh_token")
  redirect_uri = r.json().get("data").get("redirect_uri")

  data = {"token": access_token}
  content = requests.get(url="https://email-auth.test.osinfra.cn/auth/resource", params=data)
  response = content.json()
  status = response["status_code"]
  if status != 200:
    if status != 403:
      return None
    else:
      # 重刷token
      data2 = {"grant_type": "refresh_token", "email": request.session.get("email"), "refresh_token": refresh_token}
      r2 = requests.put(url="https://email-auth.test.osinfra.cn/auth/refresh", data=data2)
      if r2.status_code != 200:
        return None
      data3 = {"token": access_token}
      content2 = requests.get(url="https://email-auth.test.osinfra.cn/auth/resource", data=data3)
      response2 = content2.json()
      user_email = response2["data"]["email"]
      user_name = response2["data"]["name"]
      user_id = response2["data"]["name"]
      return {
        'type': 'email',
        'user_id': user_id,
        'name': '%s (%s)' % (user_id, user_name),
        'info': {'email': user_email},
        'token': {},
      }

  user_email = response.get("data").get("email")
  user_name = response.get("data").get("name")
  user_id = response.get("data").get("name")

  return {
    'type': 'email',
    'user_id': user_id,
    'name': '%s (%s)' % (user_id, user_name),
    'info': {'email': user_email},
    'token': {},
  }


def do_logout(user):
  return None


def update_status(token, message):
  pass


def send_message(user_id, name, user_info, subject, body):
  send_mail(
    subject,
    body,
    settings.SERVER_EMAIL,
    ["%s <%s>" % (user_id, user_info['email'])],
    fail_silently=False,
  )


def check_constraint(eligibility, user_info):
  pass


#
# Election Creation
#
def can_create_election(user_id, user_info):
  return True
