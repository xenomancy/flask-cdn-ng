import unittest
import os

from flask import Flask, render_template_string

from flask.ext.cdn import CDN


class DefaultsTest(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.testing = True

        CDN(self.app)

    def test_domain_default(self):
        """ Tests CDN_DOMAIN default value is correctly set. """
        self.assertEquals(self.app.config['CDN_DOMAIN'], None)

    def test_debug_default(self):
        """ Tests CDN_DEBUG default value is correctly set. """
        self.assertEquals(self.app.config['CDN_DEBUG'], False)

    def test_https_default(self):
        """ Tests CDN_HTTPS default value is correctly set. """
        self.assertEquals(self.app.config['CDN_HTTPS'], False)

    def test_timestamp_default(self):
        """ Tests CDN_TIMESTAMP default value is correctly set. """
        self.assertEquals(self.app.config['CDN_TIMESTAMP'], True)


class UrlTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.testing = True

        self.app.config['CDN_DOMAIN'] = 'mycdnname.cloudfront.net'
        self.app.config['CDN_TIMESTAMP'] = False

        @self.app.route('/<url_for_string>')
        def a(url_for_string):
            return render_template_string(url_for_string)

        @self.app.route('/')
        def b():
            return render_template_string("{{ url_for('b') }}")

    def client_get(self, ufs):
        CDN(self.app)
        client = self.app.test_client()
        return client.get('/%s' % ufs)

    def test_url_for(self):
        """ Tests static endpoint correctly affects generated URLs. """
        # non static endpoint url_for in template
        self.assertEquals(self.client_get('').data, '/')

        # static endpoint url_for in template
        ufs = "{{ url_for('static', filename='bah.js') }}"
        exp = 'http://mycdnname.cloudfront.net/static/bah.js'
        self.assertEquals(self.client_get(ufs).data, exp)

    def test_url_for_debug(self):
        """ Tests CDN_DEBUG correctly affects generated URLs. """
        self.app.debug = True
        ufs = "{{ url_for('static', filename='bah.js') }}"

        self.app.config['CDN_DEBUG'] = True
        exp = 'http://mycdnname.cloudfront.net/static/bah.js'
        self.assertEquals(self.client_get(ufs).data, exp)

        self.app.config['CDN_DEBUG'] = False
        exp = '/static/bah.js'
        self.assertEquals(self.client_get(ufs).data, exp)

    def test_url_for_https(self):
        """ Tests CDN_HTTPS correctly affects generated URLs. """
        ufs = "{{ url_for('static', filename='bah.js') }}"

        self.app.config['CDN_HTTPS'] = True
        exp = 'https://mycdnname.cloudfront.net/static/bah.js'
        self.assertEquals(self.client_get(ufs).data, exp)

        self.app.config['CDN_HTTPS'] = False
        exp = 'http://mycdnname.cloudfront.net/static/bah.js'
        self.assertEquals(self.client_get(ufs).data, exp)

    def test_url_for_timestamp(self):
        """ Tests CDN_TIMESTAMP correctly affects generated URLs. """
        ufs = "{{ url_for('static', filename='bah.js') }}"

        self.app.config['CDN_TIMESTAMP'] = True
        path = os.path.join(self.app.static_folder, 'bah.js')
        ts = int(os.path.getmtime(path))
        exp = 'http://mycdnname.cloudfront.net/static/bah.js?t={}'.format(ts)
        self.assertEquals(self.client_get(ufs).data, exp)

        self.app.config['CDN_TIMESTAMP'] = False
        exp = 'http://mycdnname.cloudfront.net/static/bah.js'
        self.assertEquals(self.client_get(ufs).data, exp)


if __name__ == '__main__':
    unittest.main()
