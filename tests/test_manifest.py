# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import six
import pytest

from flask_cdn import _get_checksum_for, _download_manifest, CDNManifestUrlError, CDNFileNotFoundInManifest


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


def test_raise_exception_when_checksum_not_found(manifest_list):
    with pytest.raises(CDNFileNotFoundInManifest) as excinfo:
        _get_checksum_for('nesmyslna/cesta.txt', manifest_list)

    assert 'nesmyslna/cesta.txt not found in manifest' in str(excinfo.value)


@cdn_manifest
def test_download_mainifest_return_checksums_and_filenames_list(server):
    result = tuple(_download_manifest(server + '/static/MANIFEST'))

    assert all(map(lambda i: isinstance(i[0], six.text_type) and isinstance(i[1], six.text_type), result))
    assert all(map(lambda i: len(i[0]) == 32 and len(i[1]) > 0, result))


@cdn_manifest
def test_download_manifest_raise_error_when_bad_url_is_given(server):
    with pytest.raises(CDNManifestUrlError) as excinfo:
        _download_manifest(server + '/hokus/pokus/fokus')

    assert '404' in str(excinfo.value)
