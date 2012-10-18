import evernote.edam.notestore.NoteStore as NoteStore
import evernote.edam.userstore.UserStore as UserStore
import thrift.protocol.TBinaryProtocol as TBinaryProtocol
import thrift.transport.THttpClient as THttpClient

class EvernoteClient(object):

    def __init__(self, authtoken):
        self.authtoken = authtoken

        user_store_http_client = THttpClient.THttpClient("https://www.evernote.com/edam/user")
        user_store_protocol = TBinaryProtocol.TBinaryProtocol(user_store_http_client)
        self.user_store = UserStore.Client(user_store_protocol)

        note_store_url = self.user_store.getNoteStoreUrl(self.authtoken)
        note_store_http_client = THttpClient.THttpClient(note_store_url)
        note_store_protocol = TBinaryProtocol.TBinaryProtocol(note_store_http_client)

        self.note_store = NoteStore.Client(note_store_protocol)


