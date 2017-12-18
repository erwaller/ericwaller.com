import os
import logging
import urllib
from urlparse import urlparse, urlunparse

from flask import (Flask,
                   flash,
                   render_template,
                   request,
                   redirect,
                   session,
                   url_for)
import requests


app = Flask(__name__)
app.debug = os.environ.get("APP_ENV") == "dev"
app.secret_key = os.environ.get("APP_SECRET_KEY")


CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
AUTHORIZE_URL = "https://seatgeek.com/oauth2"
API_BASE = "https://api.seatgeek.com/2"
SCOPES = "email,readwrite"


class SGAccessTokenAuth(requests.auth.AuthBase):

    def __init__(self, access_token=None):
        self.access_token = access_token

    def __call__(self, r):
        r.headers["Authorization"] = "token {}".format(self.access_token)
        return r


@app.before_request
def redirect_www_ssl():
    """Redirect www requests to non-www and non-ssl to ssl."""
    urlparts = urlparse(request.url)
    urlparts_list = list(urlparts)
    should_redirect = False

    if urlparts.netloc == 'www.ericwaller.com':
        urlparts_list[1] = 'ericwaller.com'
        should_redirect = True

    # if os.environ.get("APP_ENV") == 'prod' and urlparts.scheme == 'http':
    #     urlparts_list[0] = 'https'
    #     should_redirect = True

    if should_redirect:
        return redirect(urlunparse(urlparts_list), code=301)


@app.route("/")
def index():
    user = None
    if "access_token" in session:
        with requests.Session() as s:
            s.auth = SGAccessTokenAuth(access_token=session["access_token"])
            r = s.get(API_BASE + "/me")
            app.logger.info(r.json())
            user = r.json()
    return render_template("index.html", user=user)


@app.route("/api/connect")
def oauth_connect():
    redirect_uri = url_for("oauth_callback", _external=True)
    params = dict(client_id=CLIENT_ID, scope=SCOPES, redirect_uri=redirect_uri)
    return redirect(AUTHORIZE_URL + "?" + urllib.urlencode(params))


@app.route("/api/callback")
def oauth_callback():
    # Success args: code, state
    code = request.args.get("code")

    if code:
        app.logger.info("OAuth success, code:%s", code)

        params = dict(code=code, grant_type="authorization_code")
        r = requests.get(API_BASE + "/oauth/access_token", params=params, auth=(CLIENT_ID, CLIENT_SECRET))

        if r.status_code == requests.codes.ok:
            resp = r.json()

            app.logger.info("OAuth retrieved access_token:%s", resp["access_token"])
            session["access_token"] = resp["access_token"]

            flash("You connected with SeatGeek!")
            return redirect(url_for("index"))

    # Error args: error_reason, error, error_description, state
    error = request.args.get("error")
    error_reason = request.args.get("error_reason")
    error_description = request.args.get("error_description")
    app.logger.info("OAuth error, error:%s error_reason:%s", error, error_reason)

    flash("You didn't connect with SeatGeek...")
    return redirect(url_for("index"))


@app.route("/keybase.txt")
def keybase():
    return render_template("keybase.txt"), 200, {'Content-Type': 'text/plain'}


if __name__ == "__main__":
    app.logger.addHandler(logging.StreamHandler())
    app.logger.setLevel(logging.INFO)

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
