from mock import patch
from flask_app import app
import oauth2 as oauth
import pytest
from evernote.edam.error.ttypes import EDAMErrorCode, EDAMUserException

class TestFlaskApp(object):
    def setup_method(self, method):        
        self.evernote_client_patcher = patch("flask_app.app.EvernoteClient")
        self.list_patcher = patch("flask_app.app.List")
        self.render_template_patcher = patch("flask_app.app.render_template")
        self.session_patcher = patch("flask_app.app.session")

        self.mock_client = self.evernote_client_patcher.start()
        self.mock_list = self.list_patcher.start()
        self.mock_render_template = self.render_template_patcher.start()
        self.mock_session = self.session_patcher.start()

        self.context = app.app.test_request_context('/')
        self.context.push()

    def teardown_method(self, method):
        self.evernote_client_patcher.stop()
        self.list_patcher.stop()
        self.render_template_patcher.stop()
        self.session_patcher.stop()

        self.context.pop()

    def test_index(self):
        app.index()

        self.mock_render_template.assert_called_with("index.html", tasks=self.mock_list().tasks_by_expiration())

    def test_index_uses_token_from_session(self):
        app.index()

        self.mock_client.assert_called_with(app.EVERNOTE_URL, self.mock_session.get('evernote_token'))

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

            

        
