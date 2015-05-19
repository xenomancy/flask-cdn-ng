# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import pytest

from flask_cdn import _get_checksum_for


cdn_manifest = pytest.mark.cdn_manifest


@pytest.fixture
def filename():
    return 'js/script.js'


@pytest.fixture
def checksum():
    return 'afb9d1dccb6ae4b29df7a48dbd65fc4e'


@pytest.fixture
def mock_get_checksum_for(monkeypatch, checksum):
    def mock_gcf(path, checksums):
        return checksum

    monkeypatch.setattr('flask_cdn._get_checksum_for', mock_gcf)


@pytest.fixture
def manifest_list(checksum, filename):
    return [
        ['7fde23188113df6aa5a0ef2dd875e597', 'static/css/style.css'],
        [checksum, 'static/%s' % filename],
    ]


@pytest.fixture
def mock_download_manifest(monkeypatch):
    def mock_dm(url):
        return []

    monkeypatch.setattr('flask_cdn._download_manifest', mock_dm)


@cdn_manifest
def test_return_static_url_with_checksum(app, url_for, filename, checksum, mock_get_checksum_for, mock_download_manifest):
    with app.test_request_context('/'):
        result = url_for('static', filename=filename)
        assert result.endswith('%s/static/%s?c=%s' % (app.config['CDN_DOMAIN'], filename, checksum))


def test_return_checksum_for_given_path(filename, checksum, manifest_list):
    result = _get_checksum_for('static/%s' % filename, manifest_list)

    assert result == checksum
