from datetime import datetime, timedelta
from evernote.edam.type.ttypes import Tag
from evernote.edam.type.ttypes import Notebook
from forget import todo 
from mock import Mock, patch, call
import time
import uuid

class TestTODOList(object):
    def setup_method(self, method):        

        self.mock_notestore_client = Mock()
        self.mock_notestore_client.findNotes.return_value.notes = []
        self.mock_notestore_client.findNotes.return_value.totalNotes = 0

        self.mock_authtoken = Mock()

        self.notefilter_patcher = patch("forget.todo.list.NoteStoreTypes.NoteFilter")
        self.note_patcher = patch("forget.todo.list.Note")

        self.mock_notefilter = self.notefilter_patcher.start()
        self.mock_note = self.note_patcher.start()

        self.todo_notebook = Notebook(name="TODO", guid=uuid.uuid4())
        self.mock_notestore_client.listNotebooks.return_value = [self.todo_notebook]


    def teardown_method(self, method):
        self.notefilter_patcher.stop()
        self.note_patcher.stop()

    def _patch_decode_expiration_tag_guid(self):
        tags = {'1dayguid': '1-day-todo', 
                '3dayguid': '3-day-todo', 
                '1weekguid':'1-week-todo', 
                '1monthguid': '1-month-todo'}

        self.mock_notestore_client.getTag.side_effect = lambda token, guid: Tag(name=tags[guid])

    def _build_created_timestamp(self, **kwargs):
        return int((datetime.now() - timedelta(**kwargs)).strftime('%s')) * 1000

    def _build_notes_list(self, count):
        return [Mock(created = int(time.time() * 1000)) for x in range(count)]

    def test_constructor(self):
        self.mock_notestore_client.findNotes.return_value = Mock(notes = self._build_notes_list(50), totalNotes = 10)

        list = todo.list.List(self.mock_notestore_client, self.mock_authtoken)
        self.mock_notefilter.assert_called_with()        
        assert self.mock_notefilter.return_value.notebookGuid == self.todo_notebook.guid
        self.mock_notestore_client.findNotes.assert_called_with(self.mock_authtoken,
                                                                self.mock_notefilter.return_value,
                                                                0, 50)

        assert list.notes == self.mock_notestore_client.findNotes.return_value.notes

    def test_constructor_saves_notebook_guid(self):        
        other_notebook = Notebook(name="Other", guid=uuid.uuid4())
        self.mock_notestore_client.listNotebooks.return_value = [other_notebook, self.todo_notebook]

        list = todo.list.List(self.mock_notestore_client, self.mock_authtoken)
        assert list.notebook_guid == self.todo_notebook.guid

    def test_constructor_multiple_batches(self):
        note_batches = [Mock(notes = self._build_notes_list(50), totalNotes = 60), 
                        Mock(notes = self._build_notes_list(10), totalNotes = 60)]
        self.mock_notestore_client.findNotes.side_effect = lambda *args: note_batches.pop(0)

        list = todo.list.List(self.mock_notestore_client, self.mock_authtoken)
        
        self.mock_notefilter.assert_called_with()                
        assert self.mock_notestore_client.findNotes.call_args_list ==\
            [call(self.mock_authtoken, self.mock_notefilter.return_value, 0, 50),
             call(self.mock_authtoken, self.mock_notefilter.return_value, 50, 50)]

    def test_decode_expiration_tag_guid_1_day(self):
        list = todo.list.List(self.mock_notestore_client, self.mock_authtoken)
        self.mock_notestore_client.getTag.return_value = Tag(name="1-day-todo")
        
        assert list._decode_expiration_tag_guid(['1dayguid']) == timedelta(days=1)
        
        self.mock_notestore_client.getTag.assert_called_once_with(self.mock_authtoken, '1dayguid')

    def test_decode_expiration_tag_guid_3_day(self):
        list = todo.list.List(self.mock_notestore_client, self.mock_authtoken)
        self.mock_notestore_client.getTag.return_value = Tag(name="3-day-todo")
        
        assert list._decode_expiration_tag_guid(['3dayguid']) == timedelta(days=3)
        
        self.mock_notestore_client.getTag.assert_called_once_with(self.mock_authtoken, '3dayguid')

    def test_decode_expiration_tag_guid_1_week(self):
        list = todo.list.List(self.mock_notestore_client, self.mock_authtoken)
        self.mock_notestore_client.getTag.return_value = Tag(name="1-week-todo")
        
        assert list._decode_expiration_tag_guid(['1weekguid']) == timedelta(weeks=1)
        
        self.mock_notestore_client.getTag.assert_called_once_with(self.mock_authtoken, '1weekguid')

    def test_decode_expiration_tag_guid_1_month(self):
        list = todo.list.List(self.mock_notestore_client, self.mock_authtoken)
        self.mock_notestore_client.getTag.return_value = Tag(name="1-month-todo")
        
        assert list._decode_expiration_tag_guid(['1monthguid']) == timedelta(weeks=4)
        
        self.mock_notestore_client.getTag.assert_called_once_with(self.mock_authtoken, '1monthguid')

    def test_decode_expiration_tag_guid_cache(self):
        list = todo.list.List(self.mock_notestore_client, self.mock_authtoken)
        self.mock_notestore_client.getTag.return_value = Tag(name="1-month-todo")
        
        assert list._decode_expiration_tag_guid(['1monthguid']) == timedelta(weeks=4)
        assert list._decode_expiration_tag_guid(['1monthguid']) == timedelta(weeks=4)
        
        self.mock_notestore_client.getTag.assert_called_once_with(self.mock_authtoken, '1monthguid')

    def test_decode_expiration_tag_guid_multi_tags(self):
        list = todo.list.List(self.mock_notestore_client, self.mock_authtoken)
        tags = [Tag(name="not-important"), Tag(name="1-month-todo")]
        self.mock_notestore_client.getTag.side_effect = lambda *args: tags.pop(0) 
        
        assert list._decode_expiration_tag_guid(['otherguid', '1monthguid']) == timedelta(weeks=4)
        
        assert self.mock_notestore_client.getTag.call_args_list ==\
            [call(self.mock_authtoken, 'otherguid'), call(self.mock_authtoken, '1monthguid')]


    def test_sorted_by_expiration(self):        
        notes = [Mock(tagGuids = ['1dayguid'], created = int(time.time() * 1000)),
                 Mock(tagGuids = ['3dayguid'], created = int(time.time() * 1000)),
                 Mock(tagGuids = ['1weekguid'], created = int(time.time() * 1000)),
                 Mock(tagGuids = ['1monthguid'], created = int(time.time() * 1000)),
                ]

        list = todo.list.List(self.mock_notestore_client, self.mock_authtoken)
        self._patch_decode_expiration_tag_guid()
        list.notes = notes
        assert list.tasks_by_expiration() == notes

    def test_sorting_1_day(self):
        notes = [Mock(tagGuids = ['1dayguid'], created = int(time.time() * 1000)),
                 Mock(tagGuids = ['1dayguid'], created = self._build_created_timestamp(hours=12))]

        list = todo.list.List(self.mock_notestore_client, self.mock_authtoken)
        self._patch_decode_expiration_tag_guid()
        list.notes = notes
        assert list.tasks_by_expiration() == [notes[1], notes[0]]

    def test_sorting_1_day_1_week(self):
        notes = [Mock(tagGuids = ['1dayguid'], created = int(time.time() * 1000)),
                 Mock(tagGuids = ['1weekguid'], created = self._build_created_timestamp(days=2))]

        list = todo.list.List(self.mock_notestore_client, self.mock_authtoken)
        self._patch_decode_expiration_tag_guid()
        list.notes = notes
        assert list.tasks_by_expiration() == notes

    def test_delete_expired(self):
        notes = [Mock(tagGuids = ['1dayguid'], created = self._build_created_timestamp(days=2), guid = "qwerty")]

        list = todo.list.List(self.mock_notestore_client, self.mock_authtoken)
        self._patch_decode_expiration_tag_guid()
        list.notes = notes
        list.delete_expired()

        self.mock_notestore_client.deleteNote.assert_called_with(self.mock_authtoken, "qwerty")
        assert list.notes == []

    def test_delete_2_expired(self):
        notes = [Mock(tagGuids = ['1dayguid'], created = self._build_created_timestamp(days=2), guid = "qwerty"),
                 Mock(tagGuids = ['1dayguid'], created = self._build_created_timestamp(days=2), guid = "asdfg")]

        list = todo.list.List(self.mock_notestore_client, self.mock_authtoken)
        self._patch_decode_expiration_tag_guid()
        list.notes = notes        
        list.delete_expired()

        assert self.mock_notestore_client.deleteNote.call_args_list ==\
            [call(self.mock_authtoken, "qwerty"), call(self.mock_authtoken, "asdfg")]
        assert list.notes == []

    def test_delete_2__only_1_expired(self):
        notes = [Mock(tagGuids = ['1dayguid'], created = self._build_created_timestamp(days=2), guid = "qwerty"),
                 Mock(tagGuids = ['1weekguid'], created = self._build_created_timestamp(days=2), guid = "asdfg")]

        list = todo.list.List(self.mock_notestore_client, self.mock_authtoken)
        self._patch_decode_expiration_tag_guid()
        list.notes = notes
        list.delete_expired()

        self.mock_notestore_client.deleteNote.assert_called_once_with(self.mock_authtoken, "qwerty")
        assert len(list.notes) == 1
        assert list.notes[0].guid == "asdfg"

    def test_delete_no_expired(self):
        notes = [Mock(tagGuids = ['1weekguid'], created = self._build_created_timestamp(days=2), guid = "qwerty"),
                 Mock(tagGuids = ['1weekguid'], created = self._build_created_timestamp(days=2), guid = "bhyggv"),
                 Mock(tagGuids = ['1weekguid'], created = self._build_created_timestamp(days=2), guid = "hvgvjv"),
                 Mock(tagGuids = ['1weekguid'], created = self._build_created_timestamp(days=2), guid = "hhycjbk")]

        list = todo.list.List(self.mock_notestore_client, self.mock_authtoken)
        self._patch_decode_expiration_tag_guid()
        list.notes = notes
        list.delete_expired()
        
        assert len(list.notes) == 4
        assert self.mock_notestore_client.deleteNote.call_args_list == []

    def test_delete_expired_returns_deleted_count(self):
        notes = [Mock(tagGuids = ['1dayguid'], created = self._build_created_timestamp(days=2), guid = "qwerty"),
                 Mock(tagGuids = ['1weekguid'], created = self._build_created_timestamp(days=2), guid = "asdfg")]

        list = todo.list.List(self.mock_notestore_client, self.mock_authtoken)
        self._patch_decode_expiration_tag_guid()
        list.notes = notes
        assert list.delete_expired() == 1

    def test_add_task_1_day(self):
        list = todo.list.List(self.mock_notestore_client, self.mock_authtoken)
        list.notebook_guid = uuid.uuid4()
        list.add_1_day_task("task description")

        self.mock_note.assert_called_with(title="task description", 
                                          tagNames=["1-day-todo"], 
                                          notebookGuid=list.notebook_guid)
        self.mock_notestore_client.createNote.assert_called_with(self.mock_authtoken, self.mock_note.return_value)
        assert list.notes == [self.mock_notestore_client.createNote.return_value]

        
    def test_add_task_3_day(self):
        list = todo.list.List(self.mock_notestore_client, self.mock_authtoken)
        list.notebook_guid = uuid.uuid4()
        list.add_3_day_task("task description")

        self.mock_note.assert_called_with(title="task description", 
                                          tagNames=["3-day-todo"], 
                                          notebookGuid=list.notebook_guid)
        self.mock_notestore_client.createNote.assert_called_with(self.mock_authtoken, self.mock_note.return_value)
        assert list.notes == [self.mock_notestore_client.createNote.return_value]

    def test_add_task_1_week(self):
        list = todo.list.List(self.mock_notestore_client, self.mock_authtoken)
        list.notebook_guid = uuid.uuid4()
        list.add_1_week_task("task description")

        self.mock_note.assert_called_with(title="task description", 
                                          tagNames=["1-week-todo"], 
                                          notebookGuid=list.notebook_guid)
        self.mock_notestore_client.createNote.assert_called_with(self.mock_authtoken, self.mock_note.return_value)
        assert list.notes == [self.mock_notestore_client.createNote.return_value]

    def test_add_task_1_month(self):
        list = todo.list.List(self.mock_notestore_client, self.mock_authtoken)
        list.notebook_guid = uuid.uuid4()
        list.add_1_month_task("task description")

        self.mock_note.assert_called_with(title="task description", 
                                          tagNames=["1-month-todo"], 
                                          notebookGuid=list.notebook_guid)
        self.mock_notestore_client.createNote.assert_called_with(self.mock_authtoken, self.mock_note.return_value)
        assert list.notes == [self.mock_notestore_client.createNote.return_value]

        







