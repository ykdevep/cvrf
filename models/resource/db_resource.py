# -*- coding: utf-8 -*-
import app_resource.py

db.define_table('state',
    Field('name', 'string', length=15, requires=IS_NOT_EMPTY(), label=T('State'), comment=T("State name")),
    Field('description', 'text', label=T('Description'), comment=T("Description")),
    format='%(name)s')

db.state._singular = T("State")
db.state._plural = T("States")

db.define_table('language',
    Field('name', 'string', length=25, requires=IS_NOT_EMPTY(), label=T('Language'), comment=T("Language name")),
    format='%(name)s')

db.language._singular = T("Language")
db.language._plural = T("Languages")

db.define_table('publisher',
    Field('name', 'string', length=50, requires=IS_NOT_EMPTY(), label=T('Publisher'), comment=T("Publisher name")),
    format='%(name)s')

db.publisher._singular = T("Publisher")
db.publisher._plural = T("Publishers")

db.define_table('resource',
    Field('resource', 'upload', autodelete=True, uploadseparate = True, uploadfolder=os.path.join(request.folder,'nfs-uploads'), label=T('Resource')),
    Field('coverpag', 'upload', autodelete=True, uploadseparate = True, uploadfolder=os.path.join(request.folder,'nfs-uploads'), label=T('Coverpage')),
    Field('title', 'string', label=T('Resource title'), comment=T('Resource title (*)')),
    Field('description', 'text', default=P(T('Enter description...')), label=T('Description'), comment=T('Resource description')),
    Field('keyword', 'list:string', default=[T('Keywords')], label=T('Keywords'), comment=T('Resource keywords')),
    Field('author', 'list:string', default=[T("Authors")], label=T('Authors'), comment=T('Resource authors')),
    Field('language', 'reference language', ondelete="SET NULL", label=T('Language'), comment=T('Resource language')),
    Field('publisher','reference publisher', ondelete="SET NULL", label=T('Publisher'), comment=T("Resource publisher")),
    Field('state', 'reference state', ondelete="SET NULL", label=T('State'), comment=T('Resource state')),
    Field('rtype', 'reference rtype', ondelete="SET NULL", label=T('Type'), comment=T('Resource type')),
    Field('category', 'reference category', ondelete="SET NULL", label=T('Category'), comment=T('Resource category')),
    Field('year', 'string', default=str(request.now.year), label=T('Year'), comment=T("Resource year")),
    Field('identifier', 'string', label=T('Identifier'), comment=T('Resource identifier (isbn, issn)')),
    Field('year_update', 'string', default=str(request.now.year), readable=False, writable=False, label=T('Year Update')),
    Field('size', 'double', default=0.0, readable=False, writable=False, label=T('Size')),
    Field('unit', 'string', default = "Mib", readable=False, writable=False,  label=T('Unit')),
    Field('mime_type', 'string', default="pdf", readable=False, writable=False,  label=T('Mime Type')),
    Field('pages', 'integer', default=0, readable=False, writable=False, label=T('Pages')),
    Field('downloads', 'integer', default=0, readable=False, writable=False, label=T('Downloads')),
    Field('visits', 'integer', default=0, readable=False, writable=False,  label=T('Visits')),
    Field('votes_user', 'list:integer', default=[], label=T('Ids user'), writable=False, readable=False),
    Field('votes', 'integer', writable=False, readable=False, default=[], label=T('Votes'), compute = lambda r: len(r.votes_user)),
    format='%(title)s')

db.resource.resource.requires = [IS_UPLOAD_FILENAME(filename='^(\s|\.|-|\w|á|é|í|ó|ú|ñ|Á|É|Í|Ó|Ú|Ñ){1,40}$', extension='^(pdf|epub|png)$', case=0)]
db.resource.resource.comment = T("Filename length (40), alphanumeric characters and format (pdf, epub or png)")
db.resource.coverpag.comment = T("Image format (png) and  (120x160)")
db.resource.resource.represent = lambda value, register: A(T('Click here for download'), _href=URL('resource', 'downloads', args=[register.id, value]))

db.resource.resource.authorization = lambda registro: auth.is_logged_in()

db.resource.coverpag.requires = IS_EMPTY_OR(IS_IMAGE(extensions=('png'), maxsize=(120, 160)))

db.resource.title.requires = [IS_NOT_EMPTY(), IS_NOT_IN_DB(db, 'resource.title')]
db.resource.description.requires = [IS_NOT_EMPTY()]

db.resource.description.represent = lambda value, register: XML(value)

db.resource.language.default = lambda : db(db.language).select().first().id or None
db.resource.publisher.default = lambda : db(db.publisher).select().first().id or None
db.resource.state.default = lambda : db(db.state).select().first().id or None
db.resource.rtype.default = lambda : db(db.rtype).select().first().id or None
db.resource.category.default = lambda : db(db.category).select().first().id or None

subconjunto=db((db.state.name != "Publicado") & (db.state.name != "Rechazado") & (db.state.name != "Aceptado"))

if ("Administrador" in auth.user_groups.values()) or ("Publicador" in auth.user_groups.values()):
    subconjunto=db(db.state.id>0)
elif ("Revisor" in auth.user_groups.values()):
    subconjunto=db((db.state.name != "Publicado"))

db.resource.state.requires = IS_IN_DB(subconjunto, 'state.id', '%(name)s')

db.resource._singular = T("Resource")
db.resource._plural = T("Resources")

def resourceInsertBefore(f):
    """
    Callback for extract metadata file, create coverpage and update f dict
    """
    try:
        classResource = app_resource.resourceMetadata(f['resource'])
        coverpage = classResource.coverpage()
        f['coverpag'] = coverpage['coverpag']
        m = classResource.getMetadata()

        f['year_update'] = m['year_update']
        f['mime_type'] = m['mime_type']
        f['keyword'] = m['keyword']
        f['author'] = m['author']
        f['year'] = m['year']
        f['pages'] = m['pages']
        f['unit'] = m['unit']
        f['size'] = m['size']
        f['votes_user'] = [auth.user.id]

        if f.has_key('title'):
            if not f['title'] and m['title']:
                f['title'] = m['title']
        return None
    except Exception, e:
        return True

db.resource._before_insert.append(lambda f: resourceInsertBefore(f))

def resourceUpdateBefore(s, f):
    """
    Callback for extract metadata file, create coverpage and update f dict
    """
    try:
        resource = s.select().first()

        if f.has_key('resource'):
            if f['resource'] != resource.resource:

                classResource = app_resource.resourceMetadata(f['resource'], f['coverpag'])
                coverpage = classResource.coverpage()
                f['coverpag'] = coverpage['coverpag']
                m = classResource.getMetadata()
                f['year_update'] = m['year_update']
                f['mime_type'] = m['mime_type']
                f['keyword'] = m['keyword']
                f['author'] = m['author']
                f['year'] = m['year']
                f['pages'] = m['pages']
                f['unit'] = m['unit']
                f['size'] = m['size']
                f['title'] = m['title']

        return None
    except Exception, e:
        return True

db.resource._before_update.append(lambda s,f: resourceUpdateBefore(s,f))
db.resource.resource.authorize = lambda record:auth.is_logged_in()


db.define_table('review',
   Field('resource', 'reference resource', writable=False, readable=False, label=T("Resource")),
   Field('success', 'boolean', default=False, label=T("Success")),
   Field('note', 'text', default=T("Enter note of resource"), label=T("Note")),
   format='%(id)s')

db.review.note.represent = lambda value, register: XML(value)
db.review.note.requires = [IS_NOT_EMPTY()]

db.review._singular = T("Review")
db.review._plural = T("Revisions")

db.define_table('comment',
   Field('resource', 'reference resource', writable=False, readable=False, label=T("Resource")),
   Field('body','text', default=P(T("Enter comment...")), label=T('')),
   format='%(id)s')

db.comment.created_on.writable=db.comment.created_on.readable=False
db.comment.created_by.writable=db.comment.created_by.readable=False

db.comment.body.represent = lambda value, register : XML(value, sanitize=True, permitted_tags=['a', 'b', 'blockquote', 'br/', 'i', 'li', 'ol', 'ul', 'p', 'cite', 'code', 'pre'], allowed_attributes={'a':['href', 'title'], 'blockquote':['type']})
