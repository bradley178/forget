from evernote.edam.error.ttypes import EDAMErrorCode, EDAMUserException
from flask.ext.testing import TestCase
from flask_app import app
from mock import patch
import oauth2 as oauth
import pytest

class TestFlaskApp(TestCase):
    def setup_method(self, method):
        app.app.secret_key = "TEST_APP_SECRET_KEY"

        self.evernote_client_patcher = patch("flask_app.app.EvernoteClient")
        self.list_patcher = patch("flask_app.app.List")                

        self.mock_client = self.evernote_client_patcher.start()
        self.mock_list = self.list_patcher.start() 
        
    def teardown_method(self, method):
        self.evernote_client_patcher.stop()
        self.list_patcher.stop()
        
    def create_app(self):        
        app.app.config['TESTING'] = True
        return app.app

    def test_index(self):
        self.assert200(self.client.get("/"))
        self.mock_list().tasks_by_expiration.assert_called_with()        

    def test_index_uses_token_from_session(self):
        with patch("flask_app.app.session") as session:        
            self.assert200(self.client.get("/"))        
            self.mock_client.assert_called_with(app.EVERNOTE_URL, session.get('evernote_token'))

    def test_add_task(self):
        self.assert200(self.client.post("/add"))

class TestAuth(object):
    def setup_method(self, method):
        app.app.secret_key = "TEST_APP_SECRET_KEY"
        self.context = app.app.test_request_context('/')
        self.context.push()

    def teardown_method(self, method):
        self.context.pop()

    def test_get_oauth_client_includes_key_and_secret(self):
        app.EVERNOTE_CONSUMER_KEY = "test_key"
        app.EVERNOTE_CONSUMER_SECRET = "test_secret"
        client = app.get_oauth_client()

        assert client.consumer.key == "test_key"
        assert client.consumer.secret == "test_secret"

    def test_get_oauth_client_includes_token(self):
        token = oauth.Token("test_token_string", "test_token_secret")
        client = app.get_oauth_client(token)

        assert client.token == token
    
    def test_require_auth_returns_wrapped_function(self):
        assert "test_return_value" == app.require_evernote_auth(lambda: "test_return_value")()

    def test_require_auth_redirects(self):
        def raise_exception():
            raise EDAMUserException(errorCode=EDAMErrorCode.DATA_REQUIRED)

        with app.app.test_request_context('/'):
            assert 302 == app.require_evernote_auth(raise_exception)().status_code

    def test_require_auth_reraises_other_exceptions(self):
        error = EDAMUserException()
        def raise_exception():
            raise error

        with pytest.raises(EDAMUserException) as e:            
            app.require_evernote_auth(raise_exception)().status_code
        assert e.value == error

    def test_start_auth(self):
        with patch("flask_app.app.get_oauth_client") as client:
            client().request.return_value = ({'status': '200'}, "oauth_token=123&oauth_token_secret=xyz")
            assert 302 == app.start_auth().status_code

            assert app.session['oauth_token'] == '123'
            assert app.session['oauth_token_secret'] == 'xyz'

    def test_start_auth_bad_response(self):
        with patch("flask_app.app.get_oauth_client") as client:
            with pytest.raises(Exception):
                client().request.return_value = ({'status': None}, None)
                app.start_auth()

    def test_finish_auth(self):
        app.session['oauth_token'] = 'test_oauth_token'
        app.session['oauth_token_secret'] = 'test_oauth_token_secret'

        with patch("flask_app.app.get_oauth_client") as client:
            client().request.return_value = ({'status': '200'}, "oauth_token=qwerty")
            assert 302 == app.finish_auth().status_code

            assert app.session['evernote_token'] == 'qwerty'

    def test_finish_auth_bad_response(self):
        app.session['oauth_token'] = 'test_oauth_token'
        app.session['oauth_token_secret'] = 'test_oauth_token_secret'

        with patch("flask_app.app.get_oauth_client") as client:
            with pytest.raises(Exception):
                client().request.return_value = ({'status': None}, None)
                app.finish_auth()

            

        
