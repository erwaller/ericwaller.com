import os
from urlparse import urlparse, urlunparse

from flask import Flask
from flask import (Flask,
                   render_template,
                   request,
                   redirect)


app = Flask(__name__)
app.debug = os.environ.get("APP_ENV") == "dev"

@app.before_request
def redirect_www():
    """Redirect non-www requests to www."""
    urlparts = urlparse(request.url)
    if urlparts.netloc == 'www.ericwaller.com':
        urlparts_list = list(urlparts)
        urlparts_list[1] = 'ericwaller.com'
        return redirect(urlunparse(urlparts_list), code=301)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
