"""
Gitee Authentication

"""

import httplib2
from django.conf import settings
from django.core.mail import send_mail
from oauth2client.client import OAuth2WebServerFlow

from helios_auth import utils

# some parameters to indicate that status updating is not possible
STATUS_UPDATES = False

# display tweaks
LOGIN_MESSAGE = "Log in with Gitee"

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
  request.session['gitee_redirect_uri'] = redirect_url
  return flow.step1_get_authorize_url().replace("&access_type=offline", "")

def get_user_info_after_auth(request):
  redirect_uri = request.session['gitee_redirect_uri']
  del request.session['gitee_redirect_uri']
  flow = get_flow(redirect_uri)
  if 'code' not in request.GET:
    return None
  code = request.GET['code']
  credentials = flow.step2_exchange(code)

  http = httplib2.Http(".cache")
  http = credentials.authorize(http)
  (_, content) = http.request("https://gitee.com/api/v5/user", "GET")
  response = utils.from_json(content.decode('utf-8'))
  user_id = response['login']
  user_name = response['name']

  (_, content) = http.request("https://gitee.com/api/v5/emails", "GET")
  response = utils.from_json(content.decode('utf-8'))
  user_email = None
  for email in response:
    if email['scope'][0] == "primary" and email['scope'][1] == "committed":
      user_email = email['email']
      break
  if not user_email:
    raise Exception("email address with Gitee not find")

  return {
    'type': 'gitee',
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
