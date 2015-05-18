# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import pytest


cdn_manifest = pytest.mark.cdn_manifest


@pytest.fixture
def filename():
    return 'js/script.js'


@pytest.fixture
def checksum(filename):
    return '1234567890'


@pytest.fixture
def mock_get_checksum_for(monkeypatch, checksum):
    def mock_gcf(path):
        return checksum

    monkeypatch.setattr('flask_cdn._get_checksum_for', mock_gcf)


@pytest.fixture
def manifest_file():
    return b'''
afb9d1dccb6ae4b29df7a48dbd65fc4e  static/js/script.js
43483883da7b45f38d328a616d6163b2  static/js/plugins.js
7fde23188113df6aa5a0ef2dd875e597  static/css/style.css
9e25e8e29ef0ea358e9778082ffd97d8  static/libs/bootstrap3/js/bootstrap.min.js
93026945185532d3d6a1206a287decf6  static/libs/bootstrap3/js/bootstrap.js
3b31e1de93290779334c84c9b07c6eed  static/libs/bootstrap3/fonts/glyphicons-halflings-regular.svg
7c4cbe928205c888831ba76548563ca3  static/libs/bootstrap3/fonts/glyphicons-halflings-regular.woff
aa9c7490c2fd52cb96c729753cc4f2d5  static/libs/bootstrap3/fonts/glyphicons-halflings-regular.ttf
2469ccfe446daa49d5c1446732d1436d  static/libs/bootstrap3/fonts/glyphicons-halflings-regular.eot
4eadbf7d1721bb2729e398595bc7f0bc  static/libs/bootstrap3/css/bootstrap.min.css
cdec9434c15c405b002a7d535a052aca  static/libs/bootstrap3/css/bootstrap.css
383cb367e8784295f6244299c1b2e385  static/libs/bootstrap3/css/bootstrap-theme.css
6c5e32ffa6e869f2f3410167be7e7247  static/libs/bootstrap3/css/bootstrap-theme.min.css
57d592b195722ca55848f4cab6913535  static/libs/jquery2/jquery-2.0.3.min.js
'''


@pytest.fixture
def mock_download_manifest(monkeypatch, manifest_file):
    def mock_dm():
        return []

    monkeypatch.setattr('flask_cdn._download_manifest', mock_dm)


@cdn_manifest
def test_return_static_url_with_checksum(app, url_for, filename, checksum, mock_get_checksum_for):
    with app.test_request_context('/'):
        result = url_for('static', filename=filename)
        assert result.endswith('%s/static/%s?c=%s' % (app.config['CDN_DOMAIN'], filename, checksum))


def test_return_checksum_for_given_path():
    assert 0
