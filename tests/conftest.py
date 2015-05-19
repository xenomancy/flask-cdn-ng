# -*- coding: utf-8 -*-

import os
import socket
import sys
import time

import six
import pytest

from itertools import chain
from multiprocessing import Process

from flask import Flask
from flask.ext.cdn import CDN

from six.moves.urllib.request import urlopen
from six.moves.urllib.parse import urljoin


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
        'CDN_MANIFEST_URL': 'http://localhost:5555/MANIFEST',
    }
    return {key: value for (key, value) in chain(config.items(), cdn_manifest.items())}


def create_app(config):
    app = Flask(__name__)

    # config
    for key, value in config.items():
        app.config[key] = value

    CDN(app)

    @app.route('/')
    def index():
        return 'INDEX'

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


@six.python_2_unicode_compatible
class Server(object):

    def __init__(self, application):
        self.application = application
        self.schema = 'http'
        self.host = 'localhost'
        self.port = self._get_free_port()

        self.start()

    def _run(self, host, port):
        # close all outputs
        sys.stdout.close()
        sys.stdout = open(os.devnull)
        sys.stderr.close()
        sys.stderr = sys.stdout

        self.application.run(host=host, port=port)

    def _get_free_port(self, base_port=5555):
        for i in range(50000):
            port = base_port + i
            try:
                test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                test_socket.bind((self.host, port))
                test_socket.close()
                break
            except IOError:
                pass

        return port

    def is_alive(self, max_retries=5):
        '''
        Return True if server in child process respond.
        max_retries -- number of tries
        '''
        for i in range(max_retries):
            try:
                urlopen(self.url)
                return True
            except IOError:
                time.sleep(2 ** i)

        return False

    def start(self):
        self.p = Process(target=self._run,
                         kwargs={'host': self.host, 'port': self.port})

        self.p.start()

        if not self.is_alive():
            # TODO: raise exception or log some message
            self.stop()

    def stop(self):
        self.p.terminate()
        self.p.join()

    def restart(self):
        self.stop()
        self.start()

    @property
    def url(self):
        return '%s://%s:%d' % (self.schema, self.host, self.port)

    def __add__(self, other):
        return urljoin(str(self), other)

    def __str__(self):
        return self.url

    def __repr__(self):
        return '<LiveServer listening at %s>' % self.url


@pytest.fixture
def server(request, app):
    server = Server(application=app)

    request.addfinalizer(server.stop)

    return server
