import evernote.edam.notestore.ttypes as NoteStoreTypes
from evernote.edam.type.ttypes import Note
from datetime import datetime, timedelta

class List(object):
	def __init__(self, client, authtoken):		
		self.client = client
		self.authtoken = authtoken

		filter = NoteStoreTypes.NoteFilter()
		filter.words = "notebook:TODO"
	
		self.notes = []
		self.tag_cache = {}
		self.notebook_guid = None

		offset = 0
		while True:
			noteList = self.client.findNotes(self.authtoken, filter, offset, 50)				
				
			self.notes += noteList.notes
			offset += len(noteList.notes)

			if len(self.notes) > 0:
				self.notebook_guid = self.notes[0].notebookGuid

			if (offset >= noteList.totalNotes):
				break

	def _decode_tag_guid(self, guids):
		map = {'1-day-todo': timedelta(days=1),
			   '3-day-todo': timedelta(days=3),
			   '1-week-todo': timedelta(weeks=1),
			   '1-month-todo': timedelta(weeks=4),
			  }
		for guid in guids:
			if self.tag_cache.has_key(guid):
				return self.tag_cache[guid]
		for guid in guids:			
			tag = self.client.getTag(self.authtoken, guid)
			if map.has_key(tag.name):
				self.tag_cache[guid] = map[tag.name]
				return self.tag_cache[guid]

	def task_expiration_date(self, note):
		return datetime.fromtimestamp(note.created / 1000) + self._decode_tag_guid(note.tagGuids)

	def tasks_by_expiration(self):		
		return sorted(self.notes, cmp=lambda x, y: cmp(self.task_expiration_date(x), self.task_expiration_date(y)))

	def delete_expired(self):
		deleted_count = 0
		for note in self.notes:
			if self.task_expiration_date(note) <= datetime.now():
				self.client.deleteNote(self.authtoken, note.guid)
				self.notes.remove(note)
				deleted_count += 1
		
		return deleted_count

	def add_1_day_task(self, description):
		self.notes.append(self.client.createNote(self.authtoken, 
												 Note(title=description, 
												 	  tagNames=["1-day-todo"], 
												 	  notebookGuid=self.notebook_guid)))

	def add_3_day_task(self, description):
		self.notes.append(self.client.createNote(self.authtoken, 
												 Note(title=description, 
												 	  tagNames=["3-day-todo"], 
												 	  notebookGuid=self.notebook_guid)))

	def add_1_week_task(self, description):
		self.notes.append(self.client.createNote(self.authtoken, 
												 Note(title=description, 
												 	  tagNames=["1-week-todo"], 
												 	  notebookGuid=self.notebook_guid)))

	def add_1_month_task(self, description):
		self.notes.append(self.client.createNote(self.authtoken, 
												 Note(title=description, 
												 	  tagNames=["1-month-todo"], 
												 	  notebookGuid=self.notebook_guid)))

