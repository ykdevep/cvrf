# -*- coding: utf-8 -*-
db.define_table('news',
   Field('title', 'string', label=T('Title')),
   Field('image', 'upload', uploadseparate = True, autodelete=True, default="", label=T('Image news'), comment=T("Image type ")),
   Field('published_on', 'date', default=request.now, label=T("Published on")),
   Field('rank', 'integer', writable=False, readable=False, default=0, label=T('Rank')),
   Field('is_enabled', 'boolean', default=True, label=T('Is enabled')),
   Field('abstract','text', label=T('New abstract')),
   Field('text','text', label=T('Content')),
   format='%(title)s')

db.news._singular = T("New")
db.news._plural = T("News")

db.news.image.represent = lambda value, register: __image_news(value)
db.news.text.represent = lambda value, register: XML(value)
db.news.abstract.default = T('Resumen de la Noticia')
db.news.text.default = P(T('Texto del primer parrafo de la noticia visible'))

db.news.title.requires = IS_NOT_EMPTY()
db.news.published_on.requires = IS_DATE()
db.news.text.requires = IS_NOT_EMPTY()
db.news.image.requires = [IS_EMPTY_OR(IS_IMAGE(extensions=('png', 'jpg', 'jpeg'), error_message=T('Image news format (png, jpeg, jpg)')))]

def __image_news(value):
    '''
    Auxiliary methods of represent image
    '''
    if value:
        return A(T('Click here for download or url copy'), _href=URL('blog', 'download', args=[value]))
    return A(T('Image not found'))
