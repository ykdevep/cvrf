# -*- coding: utf-8 -*-
db.define_table('forum',
   Field('title', 'string', label=T('Title')),
   Field('description', 'text', label=T('Description')),
   Field('is_enabled', 'boolean', default=True, label=T('Is enabled')),
   format='%(title)s')

db.forum.title.requires = [IS_NOT_EMPTY()]
db.forum.description.requires = [IS_NOT_EMPTY()]

db.forum._singular = T("Forum")
db.forum._plural = T("Forums")

db.define_table('forum_comment',
   Field('text','text', default=T("Enter comment..."), label=""),
   Field('forum', 'reference forum', readable=False, writable=False),
   Field('forum_comment', 'reference forum_comment', readable=False, writable=False),
   format='%(id)s')

db.forum_comment.text.requires = [IS_NOT_EMPTY()]
db.forum_comment.text.represent = lambda value, register: XML(value)

db.forum_comment._singular = T("Comment")
db.forum_comment._plural = T("Comments")

def foroCommentInsert(f,id):
    try:
        if f.has_key("forum"):
            import datetime
            forum = db.forum(f["forum"])
            forum.update_record(update_on=datetime.datetime.today())
        return None
    except Exception, e:
        return None

db.forum_comment._after_insert.append(lambda f,id: foroCommentInsert(f,id))
