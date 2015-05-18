# -*- coding: utf-8 -*-

import pytest

from itertools import chain

from flask import Flask
from flask.ext.cdn import CDN


def pytest_generate_tests(metafunc):
    if hasattr(metafunc.function, 'cdn_manifest'):
        metafunc.parametrize('app', ['cdn_manifest'], indirect=True)


def config():
    return {
        'TESTING': True,
        'SECRET_KEY': 'secret',
        'CDN_DOMAIN': 'mycdnname.cloudfront.net',
    }


def cdnmanifest(config):
    cdn_manifest = {
        'CDN_MANIFEST': True,
        'CDN_TIMESTAMP': False,
        'CDN_MANIFEST_URL': 'http://localhost:5000/MANIFEST',
    }
    return {key: value for (key, value) in chain(config.items(), cdn_manifest.items())}


def create_app(config):
    app = Flask(__name__)

    # config
    for key, value in config.items():
        app.config[key] = value

    CDN(app)

    return app


@pytest.fixture
def app(request):
    if getattr(request, 'param', '') == 'cdn_manifest':
        app = create_app(cdnmanifest(config()))
    else:
        app = create_app(config())

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)

    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def url_for(app):
    return app.jinja_env.globals['url_for']
