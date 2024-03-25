from datetime import datetime

from mongoengine import Document, StringField, FileField, IntField, DateTimeField, ReferenceField


class Directory(Document):
    dir_name = StringField(required=True)
    owner_id = IntField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    owner=StringField(requires=True)

    meta = {"collection": "directory"}


class File(Document):
    file_name = StringField(required=True)
    content_type = StringField(required=True)
    file_content = FileField()
    owner_id = IntField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    owner=StringField(requires=True)


    parent = ReferenceField(Directory)

    meta = {"collection": "file"}
