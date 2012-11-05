from forget.evernote_client import EvernoteClient
from mock import patch

class TestEvernoteAuth(object):
    def setup_method(self, method):
        self.note_store_patcher = patch("forget.evernote_client.NoteStore")
        self.user_store_patcher = patch("forget.evernote_client.UserStore")
        self.binary_protocol_patcher = patch("forget.evernote_client.TBinaryProtocol")
        self.http_client_patcher = patch("forget.evernote_client.THttpClient")

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
        assert EvernoteClient("test url", "test token")        

