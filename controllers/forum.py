# -*- coding: utf-8 -*-
# intente algo como
@auth.requires_membership("Editor")
def admin_forum():
    """
    Admin website
    """
    response.flash = T("Administrate forum")
    response.title = T("Administrate forum")+response.title

    selectable = lambda ids: db(db.forum.id.belongs(ids)).delete()

    grid = SQLFORM.smartgrid(db.forum, selectable=selectable, selectable_submit_button=T('Delete'))

    heading=grid.elements('th')
    if heading:
           heading[0].append(INPUT(_type='checkbox', _onclick="$('input[type=checkbox]').each(function(k){$(this).attr('checked', 'checked');});"))
    return dict(grid=grid)

def index():
    '''
    Foro debate
    '''
    response.title = T("Foro") + response.title
    return dict()

def entries():
    '''
    Entradas del foro
    '''
    if request.cid:
        count = db(db.forum.id > 0).count()
        limitby = None

        try:
            page = int(request.vars.p or 1)-1
        except ValueError:
            page = 0

        import app_tools

        limitby = (page*PAGINATE, (page+1)*PAGINATE)
        entries = db(db.forum.id > 0).select(orderby=db.forum.created_on, limitby=limitby)
        return dict(entries=entries, paginator=app_tools.paginator(PAGINATE, count), count=count)
    else:
        raise HTTP(403)

def comments():
    '''
    Componente para los comentarios del forum
    '''
    if request.cid:
        entry = db.forum(request.args(-1))
        form = SQLFORM(db.forum_comment, submit_button=T('Comment'))

        response.flash = T("Commets")

        try:
            page = int(request.vars.p or 1)-1
        except ValueError:
            page = 0

        import app_tools

        PAGINATE = 10
        count = db(db.forum_comment.forum == entry.id).count()

        if form.validate():
            db.forum_comment.insert(text=request.vars.text, forum=entry.id)
            response.flash = T('Added comment')

            page, reminder = divmod(count, PAGINATE)
            request.vars.p = page + 1

        limitby = (page*PAGINATE, (page+1)*PAGINATE)

        comments = db(db.forum_comment.forum == entry.id).select(orderby=db.forum_comment.created_on, limitby=limitby)

        return dict(form=form, paginator=app_tools.paginator_comments(PAGINATE, count), count=count, entry=entry, comments=comments)
    else:
        raise HTTP(403)

def comment_count():
    if request.cid:
        count = 0
        if request.args(-1):
            count = db((db.forum_comment.id > 0) & (db.forum_comment.forum == request.args(-1))).count()
    return dict(count=count)

@cache.action()
def download():
    """
    Download upload field
    """
    return response.download(request, db)
