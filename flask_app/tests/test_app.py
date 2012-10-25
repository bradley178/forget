from mock import Mock, patch, call
from flask_app import app

class TestTODOList(object):
    def setup_method(self, method):        
        self.evernote_client_patcher = patch("flask_app.app.EvernoteClient")
        self.list_patcher = patch("flask_app.app.List")
        self.render_template_patcher = patch("flask_app.app.render_template")

        self.evernote_client_patcher.start()
        self.mock_list = self.list_patcher.start()
        self.mock_render_template = self.render_template_patcher.start()

    def teardown_method(self, method):
        self.evernote_client_patcher.stop()
        self.list_patcher.stop()
        self.render_template_patcher.stop()

    def test_index(self):
        app.index()

        self.mock_render_template.assert_called_with("index.html", tasks=self.mock_list().tasks_by_expiration())
