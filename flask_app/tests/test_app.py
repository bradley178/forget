from mock import patch
from flask_app import app

class TestTODOList(object):
    def setup_method(self, method):        
        self.evernote_client_patcher = patch("flask_app.app.EvernoteClient")
        self.list_patcher = patch("flask_app.app.List")
        self.render_template_patcher = patch("flask_app.app.render_template")
        self.session_patcher = patch("flask_app.app.session")

        self.mock_client = self.evernote_client_patcher.start()
        self.mock_list = self.list_patcher.start()
        self.mock_render_template = self.render_template_patcher.start()
        self.mock_session = self.session_patcher.start()

    def teardown_method(self, method):
        self.evernote_client_patcher.stop()
        self.list_patcher.stop()
        self.render_template_patcher.stop()
        self.session_patcher.stop()

    def test_index(self):
        app.index()

        self.mock_render_template.assert_called_with("index.html", tasks=self.mock_list().tasks_by_expiration())

    def test_index_uses_token_from_session(self):
        app.index()

        self.mock_client.assert_called_with(app.EVERNOTE_URL, self.mock_session.get('evernote_token'))
