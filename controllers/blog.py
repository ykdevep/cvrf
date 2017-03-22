# -*- coding: utf-8 -*-
# intente algo como
@auth.requires_membership("Editor")
def admin_news():
    """
    Admin website
    """
    response.flash = T("Administrate news")
    response.title = T("Administrate news")+response.title

    selectable = lambda ids: db(db.news.id.belongs(ids)).delete()

    grid = SQLFORM.smartgrid(db.news, selectable=selectable, linked_tables=[], selectable_submit_button=T('Delete'))

    heading=grid.elements('th')
    if heading:
           heading[0].append(INPUT(_type='checkbox', _onclick="$('input[type=checkbox]').each(function(k){$(this).attr('checked', 'checked');});"))
    return dict(grid=grid)

def index():
    '''
    Buscar noticias
    '''
    response.title = T("News") + response.title
    return dict()


def news():
    '''
    Componente que implementa la búsqueda de noticias
    '''
    if request.cid:
        import app_tools
        import datetime

        form=FORM(DIV(CAT(INPUT(_type='text', _name="search", _value=request.vars.search, _id="search", _class="form-control", _placeholder=T("Search")), CAT(SPAN(INPUT(_type='submit', _value=T("Search"), _class="btn btn-default"), _class="input-group-btn")),), _class="input-group"), _action=URL('blog', 'news.load'), _class="", _method='get')

        try:
            page = int(request.vars.p or 1)-1
        except ValueError:
            page = 0

        limitby = (page*PAGINATE, (page+1)*PAGINATE)
        query = ((db.news.id > 0) & (db.news.published_on <= datetime.date.today()) & (db.news.is_enabled == True))

        years_part = db.news.published_on.year()

        years = db(query).select(years_part, groupby=db.news.published_on.year(), distinct=True, orderby=~db.news.published_on)

        if 'y' in request.vars:
            query &= (db.news.published_on.year() == request.vars.y)

        if request.vars.search:
            query &= db.news.title.contains((request.vars.search.strip()).split(), all=True)

        count = db(query).count()
        news = db(query).select(orderby =~db.news.published_on, limitby=limitby)

        response.flash = T('News')
        return dict(news=news, form=form, paginator=app_tools.paginator(PAGINATE, count), count=count, years=years, years_part=years_part)
    else:
        raise HTTP(403)

def visit_component():
    '''
    Función llamada por ajax que permite actualizar el número de visitas
    '''
    if not URL.verify(request, hmac_key=KEY): raise HTTP(403)
    import gluon.contrib.simplejson
    if request.ajax:
        news = db.news(request.vars.new_id)
        if news:
            news.rank = news.rank + 1
            news.modified_on = news.modified_on
            news.update_record()
            return gluon.contrib.simplejson.dumps({'success': True, 'visit': news.rank, 'new_id': news.id})
        else:
            response.headers['web2py-component-flash'] = T("Error no se encontró recurso")
            return gluon.contrib.simplejson.dumps({'success': False})
    else:
        response.headers['web2py-component-flash'] = T("Error en visita")
        return gluon.contrib.simplejson.dumps({'success': False})


def feed():
    '''
    Feed of the news of blog
    '''
    if website:
        import datetime
        entries = db((db.news.id > 0) & (db.news.published_on <= datetime.date.today()) & (db.news.is_enabled == True)).select(orderby=~db.news.published_on)
        return dict(title=T('%s latest news', website.name),
                    link=URL(scheme=True, host=website.request_app),
                    description=website.description,
                    entries=[
                      dict(title=entry.title,
                      link=URL("blog", "index.html", scheme=True, host=website.request_app),
                      created_on = entry.created_on,
                      description=entry.text) for entry in entries
                    ])
    else:
        return dict(title=T('News not found'))

@cache.action()
def download():
    """
    Download upload field
    """
    return response.download(request, db)
