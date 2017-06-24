import os
from urlparse import urlparse, urlunparse

from flask import (Flask,
                   render_template,
                   request,
                   redirect)


app = Flask(__name__)
app.debug = os.environ.get("APP_ENV") == "dev"


@app.before_request
def redirect_www_ssl():
    """Redirect www requests to non-www and non-ssl to ssl."""
    urlparts = urlparse(request.url)
    urlparts_list = list(urlparts)
    should_redirect = False

    if urlparts.netloc == 'www.ericwaller.com':
        urlparts_list[1] = 'ericwaller.com'
        should_redirect = True

    if os.environ.get("APP_ENV") == 'prod' and urlparts.scheme == 'http':
        urlparts_list[0] = 'https'
        should_redirect = True

    if should_redirect:
        return redirect(urlunparse(urlparts_list), code=301)


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
