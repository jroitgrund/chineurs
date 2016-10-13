"""Entry point for chineurs server"""
import urllib

from flask import Flask, redirect, render_template, request, url_for

from chineurs import facebook_authentication, group_feed, settings, timestamp


APP = Flask(__name__)


@APP.route("/authenticate/<group_id>")
def authenticate(group_id):
    """Authenticates the user with Facebook and
        redirects to the scraping route"""
    uri = (
        'https://www.facebook.com/v2.8/dialog/oauth?'
        'client_id=%s&redirect_uri=%s' % (
            facebook_authentication.APP_ID,
            urllib.parse.quote(get_redirect_uri(group_id))))
    return redirect(uri)


@APP.route("/chine")
def chine():
    """Gets all the new videos for a group and posts them
       to a YouTube channel"""
    earliest_timestamp = timestamp.get_last_timestamp()
    timestamp.write_last_timestamp()
    group_id = request.args.get('group_id')
    access_token = facebook_authentication.get_access_token(
        request.args.get('code'), get_redirect_uri(group_id))
    return render_template(
        'index.html', urls=group_feed.get_youtube_links(
            group_id, access_token, earliest_timestamp))


def get_redirect_uri(group_id):
    """Returns the redirect_url parameter for requests to the FB API"""
    return '%s%s?group_id=%s' % (
        settings.REDIRECT_URI, url_for('chine'), group_id)
