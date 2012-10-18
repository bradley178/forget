from forget.evernote_auth import EvernoteAuth
from mock import patch

class TestEvernoteAuth(object):
    def setup_method(self, method):
        self.note_store_patcher = patch("forget.evernote_auth.NoteStore")
        self.user_store_patcher = patch("forget.evernote_auth.UserStore")
        self.binary_protocol_patcher = patch("forget.evernote_auth.TBinaryProtocol")
        self.http_client_patcher = patch("forget.evernote_auth.THttpClient")

        self.mock_note_store = self.note_store_patcher.start()
        self.mock_user_store = self.user_store_patcher.start()
        self.mock_binary_protocol = self.binary_protocol_patcher.start()
        self.mock_http_client = self.http_client_patcher.start()

    def teardown_method(self, method):        
        self.note_store_patcher.stop()
        self.user_store_patcher.stop()
        self.binary_protocol_patcher.stop()
        self.http_client_patcher.stop()

    def test_constructor(self):
        EvernoteAuth()        

