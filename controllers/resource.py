# -*- coding: utf-8 -*-
# intente algo como
def search():
    '''
    Buscar recursos
    '''
    response.title = T("Buscando") + response.title
    return dict()

def search_component():
    """
    Function index, resources search
    q -> Resorce query search
    c -> Resource category search
    t -> Resource type search
    y -> Resource year search
    i -> Resource id search
    """

    if request.cid:
        import app_tools

        state = db(db.state.name == "Publicar").select(db.state.id, cache=(cache.ram, 86400), cacheable=True).first()
        query = (db.resource.id > 0) & (db.resource.state == state.id)

        if "q" in request.vars:
            if request.vars.q:

                query_search = db.resource.title.contains(request.vars.q, all=True)
                query_search |= db.resource.identifier.contains(request.vars.q, all=False)

                query_search |= db.resource.author.like('%'+request.vars.q+'%')
                query_search |= db.resource.keyword.like('%'+request.vars.q+'%')

                query &= query_search

                response.flash = T("Searched: ")+'"'+request.vars.q+'"'

        if "c" in request.vars:
            try:
                if request.vars.c:
                    query &= db.resource.category == int(request.vars.c)
            except ValueError:
                response.flash = T("Value of the category not found")

        if "t" in request.vars:
            try:
                if request.vars.t:
                    query &= db.resource.rtype == int(request.vars.t)
            except ValueError:
                response.flash = T("Value of the type not found")

        if "y" in request.vars:
            if request.vars.y:
                query &= db.resource.year == request.vars.y

        if "i" in request.vars:
            if request.vars.i:
                query &= db.resource.id == request.vars.i

        limitby = None

        try:
            page = int(request.vars.p or 1)-1
        except ValueError:
            page = 0

        limitby=(page*PAGINATE, (page+1)*PAGINATE)

        resources = db(query).select(db.resource.ALL, orderby=db.resource.votes_user|~db.resource.downloads|~db.resource.visits, groupby=db.resource.id, limitby=limitby, cache=(cache.ram, 60), cacheable=True)
        count=db(query).count()

        categories = app_tools.getCategory(None, state.id)
        types = app_tools.getType(None, state.id)
        years = app_tools.getYear(None, state.id)

        return dict(categories=categories, types=types, years=years, resources=resources, count=count, paginator=app_tools.paginator(PAGINATE, count), paginate=PAGINATE)
    else:
        raise HTTP(403)

@auth.requires_membership("Publicador")
def publish():
    '''
    El revisor revisa los recursos en estado de revición, los rechaza o lo acepta
    '''

    reviews = None

    selectable = lambda ids: __unmatched_resource(ids, "Publicar")

    query = (db.resource.id > 0)
    left = (db.resource.on((db.resource.state == db.state.id) & (db.state.name == "Aceptar")))

    fields = [db.resource.id, db.resource.title, db.resource.rtype, db.resource.language, db.resource.category, db.resource.state, db.resource.year, db.resource.keyword, db.resource.author]

    grid = SQLFORM.grid(query, left=left, selectable=selectable, fields=fields, orderby=~db.resource.id, advanced_search=False, create=False, editable=False, deletable=False, selectable_submit_button=T('Publish'))

    heading=grid.elements('th')
    if heading:
        heading[0].append(INPUT(_type='checkbox', _onclick="$('input[type=checkbox]').each(function(k){$(this).attr('checked', 'checked');});"))

    response.title = T("Para Publicar") + response.title
    response.flash = T("Para Publicar")

    if ("view" in request.args):
        reviews = db((db.review.id > 0) & (db.review.resource == request.args(-1))).select(orderby=~db.review.created_on)

    return dict(grid=grid, reviews=reviews)

def __unmatched_resource(ids, state_name):
    '''
    Acepta los recursos seleccionados
    '''
    state = db(db.state.name == state_name).select(db.state.id, cache=(cache.ram, 86400), cacheable=True).first()
    for resource in db(db.resource.id.belongs(ids)).select():
        is_valid = db((db.resource.id != resource.id) & (resource.id == state.id) & (db.resource.title == resource.title) & (db.resource.year == resource.year)).isempty()
        if is_valid:
            resource.state = state.id
            resource.update_record()
        else:
            state = db(db.state.name == "Rechazar").select(db.state.id, cache=(cache.ram, 86400), cacheable=True).first()
            db.review.insert(resource=resource.id, note=T('El recurso ha sido rechazado porque ya existe un recurso para este título, año y tipo, en este estado'), success=False)
            resource.state = state.id
            resource.update_record()
    return True


@auth.requires_membership("Revisor")
def revised():
    '''
    El revisor revisa los recursos en estado de revición, los rechaza o lo acepta
    '''
    reviews = None

    selectable = lambda ids: __unmatched_resource(ids, "Aceptar")

    query = (db.resource.category.belongs(auth.user.categories_review))
    left = (db.resource.on((db.resource.state == db.state.id) & (db.state.name == "Revisar")))

    fields = [db.resource.id, db.resource.title, db.resource.rtype, db.resource.language, db.resource.category, db.resource.state, db.resource.year, db.resource.keyword, db.resource.author]

    grid = SQLFORM.grid(query, left=left, selectable=selectable, fields=fields, orderby=~db.resource.id, advanced_search=False, create=False, editable=False, deletable=False, selectable_submit_button=T('Acept'))

    heading=grid.elements('th')
    if heading:
        heading[0].append(INPUT(_type='checkbox', _onclick="$('input[type=checkbox]').each(function(k){$(this).attr('checked', 'checked');});"))

    response.title = T("Para Revisar") + response.title
    response.flash = T("Para Revisar")

    if ("view" in request.args):
        reviews = db((db.review.id > 0) & (db.review.resource == request.args(-1))).select(orderby=~db.review.created_on)

    return dict(grid=grid, reviews=reviews)

@auth.requires_signature()
def review():
    '''
    Componente que implementa el proceso de revición
    '''
    resource = db.resource(request.args(-1))

    form = SQLFORM(db.review, formstyle='bootstrap3_stacked')
    opts = [OPTION(state.name, _value=state.id) for state in db((db.state.id > 0) & (db.state.name == "Rechazar") | (db.state.name == "Aceptar")).select(db.state.id, db.state.name, orderby=~db.state.id)]

    if ("Administrador" in auth.user_groups.values()) or ("Publicador" in auth.user_groups.values()):
        opts = [OPTION(state.name, _value=state.id) for state in db((db.state.id > 0) & (db.state.name == "Rechazar") | (db.state.name == "Publicar")).select(db.state.id, db.state.name, orderby=db.state.id)]

    form[0].insert(-1, INPUT(_type="hidden", _value=resource.id, _name="resource"))
    form[0].insert(-1, CAT(LABEL(T("Nuevo estado del recurso")), SELECT(*opts, _name="state", _value=T("Estado del Recurso"), _class="form-control")))

    if form.validate():
        is_valid = db((db.resource.id != resource.id) & (db.resource.state == form.vars.state) & (db.resource.title == resource.title) & (db.resource.year == resource.year)).isempty()

        if is_valid:
            db.review.insert(resource=form.vars.resource, note=form.vars.note, success=True)
            resource.state = form.vars.state
            resource.update_record()
            response.flash = T('Nueva revición agregada')
        else:
            state = db(db.state.name == "Rechazar").select(db.state.id).first()
            db.review.insert(resource=form.vars.resource, note=T('El recurso ha sido rechazado porque ya existe un recurso para este título, año y tipo'), success=False)
            resource.state = state.id
            resource.update_record()
            response.flash = T('El recurso ha sido rechazado porque ya existe un recurso para este título, año y tipo')
    elif form.errors:
        response.flash = T('El formulario tiene errores')

    import app_tools
    limitby = None
    PAGINATE = 5

    try:
        page = int(request.vars.p or 1)-1
    except ValueError:
        page = 0

    limitby=(page*PAGINATE, (page+1)*PAGINATE)

    query = (db.review.id > 0) & (db.review.resource == resource.id)

    reviews = db(query).select(orderby=~db.review.created_on, limitby=limitby)
    count=db(query).count()

    return dict(form=form, reviews=reviews, count=count, paginator=app_tools.paginator(PAGINATE, count), paginate=PAGINATE, resource=db.resource(request.args(-1)))

@auth.requires_login()
def my_briefcase():
    """
    Descargar todos los recursos que son de mi interés (a los que le di mi voto) en formato .zip
    """
    def __resource_quit(ids):
        """
        Resource quit of the my briefcase
        """
        for id in ids:
            resource = db.resource(id)
            votes_user = resource.votes_user.remove(auth.user.id)
            if votes_user:
                resource.update_record(votes_user = votes_user)
            else:
                resource.update_record(votes_user = [])
        return True

    editable = False

    selectable = lambda ids: __resource_quit(ids)

    if (auth.has_membership('Administrador') or auth.has_membership('Revisor')):
        editable = deletable = True

    query = db.resource.votes_user.contains(auth.user.id, all=True)
    left = db.resource.on((db.resource.state == db.state.id) & (db.state.name == "Publicar"))
    fields = [db.resource.id, db.resource.resource, db.resource.title, db.resource.language, db.resource.category, db.resource.rtype, db.resource.year]

    grid = SQLFORM.grid(query, left=left, selectable=selectable, fields=fields, orderby=~db.resource.id, advanced_search=False, create=False, deletable=deletable, editable=editable, links_in_grid=False, selectable_submit_button=T('Unlike'))

    heading=grid.elements('th')
    if heading:
           heading[0].append(INPUT(_type='checkbox', _onclick="$('input[type=checkbox]').each(function(k){$(this).attr('checked', 'checked');});"))

    response.title = T("My Briefcase") + response.title
    response.flash = T("My Briefcase")

    return dict(grid=grid)

@auth.requires_login()
def multiple_downloads():
    """
    Creating zip for multiple download
    """
    import app_tools
    import zipfile
    from cStringIO import StringIO
    out = StringIO()
    files = zipfile.ZipFile(out, mode='w')

    for register in db((db.resource.votes_user.contains(auth.user.id, all=True)) & (db.resource.state == db.state.id) & (db.state.name == "Publicar")).select(db.resource.category, db.resource.title, db.resource.mime_type, db.resource.resource, db.resource.downloads, db.resource.modified_on, db.resource.id):
        fullpath = app_tools.retrieve_file_properties(register.resource)
        if register.mime_type == "epub+zip":
            files.write(fullpath, register.category.name+"/"+register.title+'.epub')
        else:
            files.write(fullpath, register.category.name+"/"+register.title+'.'+register.mime_type)
        
        resource = db.resource(register.id)

        resource.downloads = resource.downloads + 1
        resource.modified_on = resource.modified_on
        resource.update_record()

    files.close()
    response.headers['Content-Type'] = 'application/zip'
    response.headers['Content-Disposition'] = CAT('attachment=True; filename=', T('my_briefcase'), '.zip')
    out.seek(0)

    return response.stream(out, request=request)

def __resource_exist(form, resource_id):
    '''
    Función que valida que un recurso no esta publicado en el sistema titulo, año y tipo no pueden coincidir
    '''
    is_valid = db((db.resource.id != resource_id) & (db.resource.title == form.vars.title) & (db.resource.year == form.vars.year) & (db.resource.rtype == form.vars.rtype)).isempty()
    if not is_valid:
        form.errors.title = T("Existe un recurso con este título, para este año y tipo")
        form.errors.rtype = T("Existe un recurso con este tipo, para este año y título")
        form.errors.year = T("Existe un recurso con este año, para este título y tipo")
        return True
    return False

@auth.requires_login()
def edites():
    """
    Grid to edit resource in edition or rechazed state
    """

    links=[]

    if "edit" in request.args:

        links.append({'header': T('Extract'), 'body': lambda row: A(XML('<i class="glyphicon glyphicon-plus"></i> '), _class="btn btn-info btn-menu", _href=URL(args=request.args, vars=dict(option="metadata"), user_signature=True, hash_vars=False),**{'_data-toggle': "tooltip", '_title': T("Extract metadata file"), '_data-placement': "top"})})

        links.append({'header': T('Take coverpage'), 'body': lambda row: A(XML('<i class="glyphicon glyphicon-camera"></i> '), _class="btn btn-info btn-menu", _href=URL(args=request.args, vars=dict(option="coverpage"), user_signature=True, hash_vars=False), **{'_data-toggle': "tooltip", '_title': T("Take coverpage image"), '_data-placement': "top"})})

        if request.vars.option:
            __extract(db.resource(request.args(-1)), request.vars.option)

    selectable = lambda ids: db(db.resource.id.belongs(ids)).delete()

    query = (db.resource.created_by == auth.user.id)
    left = (db.resource.on((db.resource.state == db.state.id) & ((db.state.name == "Editar") | (db.state.name == "Rechazar"))))
    fields = [db.resource.id, db.resource.resource, db.resource.title, db.resource.state, db.resource.language, db.resource.category, db.resource.rtype, db.resource.year]

    grid = SQLFORM.grid(query, left=left, onvalidation=lambda form : __resource_exist(form, request.args(-1)), selectable=selectable, fields=fields, links=links, orderby=~db.resource.id, create=False, advanced_search=False, links_in_grid=False, selectable_submit_button=T('Delete'))

    heading=grid.elements('th')
    if heading:
           heading[0].append(INPUT(_type='checkbox', _onclick="$('input[type=checkbox]').each(function(k){$(this).attr('checked', 'checked');});"))

    response.title = T("Editar") + response.title
    response.flash = T("Editar")

    return dict(grid=grid)

def __extract(resource, option):
    '''
    Función auxiliar que permite extraer los metadatos o extraer imagen del cover de un recurso en edición
    '''

    if  option == "coverpage":
        try:
            classResource = app_resource.resourceMetadata(resource.resource)
            resource.coverpag = classResource.coverpage()['coverpag']
            resource.update_record()
            response.flash = T("Take image")
        except Exception, e:
            response.flash = T("Failed to take image")
    elif option == "metadata":
        try:
            classResource = app_resource.resourceMetadata(resource.resource)
            resource_metadata = classResource.getMetadata()
            resource.year_update = resource_metadata['year_update']
            resource.mime_type = resource_metadata['mime_type']
            resource.keyword = resource_metadata['keyword']
            resource.title = resource_metadata['title']
            resource.author = resource_metadata['author']
            resource.year = resource_metadata['year']
            resource.pages = resource_metadata['pages']
            resource.unit = resource_metadata['unit']
            resource.size = resource_metadata['size']
            resource.update_record()
            response.flash = T("Extract metadata")
        except Exception, e:
            response.flash = T("Failed to extract metadata")
    else:
        response.flash = T("Error option not found")

@auth.requires_membership("Administrador")
def admin_table():
    """
    Administrate tables
    """
    table = request.args(0) or 'auth_user'
    if not table in db.tables(): grid=None

    selectable = lambda ids: db(db[table].id.belongs(ids)).delete()

    grid = SQLFORM.smartgrid(db[table], args=request.args[:1], linked_tables=[], advanced_search=False, selectable=selectable, selectable_submit_button=T('Delete'))

    heading=grid.elements('th')
    if heading:
           heading[0].append(INPUT(_type='checkbox', _onclick="jQuery('input[type=checkbox]').each(function(k){jQuery(this).attr('checked', 'checked');});"))

    response.title = T(table.replace("_", " ").capitalize()) + response.title
    response.flash = T(table.replace("_", " ").capitalize())

    return dict(grid=grid)

@auth.requires_membership("Administrador")
def upload_multiple():
    """
    Function for upload multiples resources
    """

    form = SQLFORM(db.resource, fields=['rtype', "category", 'resource'], labels={'resource': T('Recurso'), 'rtype': T('Type'), 'category': T('Category')}, submit_button=T('Upload all'))

    response.title = T("Upload Multiple") + response.title
    response.flash = T("Upload multiple files")
    return dict(form=form)

@auth.requires_membership("Administrador")
def admin():
    """
    Administrate resources
    """

    links=[]
    selectable=orderby=fields=onvalidation=None

    if "review.resource" in request.args:
        selectable = lambda ids: db(db.review.id.belongs(ids)).delete()
        fields = [db.review.id, db.review.success, db.review.note]
        response.title = T("Administrate reviews") + response.title
        response.flash = T("Administrate reviews")
    else:
        response.flash = T("Administrate resources")

        if "edit" in request.args:
            onvalidation = lambda form : __resource_exist(form, request.args(-1))
            links.append({'header': T('Extract'), 'body': lambda row: A(XML('<i class="glyphicon glyphicon-plus"></i> '), _class="btn btn-info btn-menu", _href=URL(args=request.args, vars=dict(option="metadata"), user_signature=True, hash_vars=False),**{'_data-toggle': "tooltip", '_title': T("Extract metadata file"), '_data-placement': "top"})})

            links.append({'header': T('Take coverpage'), 'body': lambda row: A(XML('<i class="glyphicon glyphicon-camera"></i> '), _class="btn btn-info btn-menu", _href=URL(args=request.args, vars=dict(option="coverpage"), user_signature=True, hash_vars=False), **{'_data-toggle': "tooltip", '_title': T("Take coverpage image"), '_data-placement': "top"})})

            if request.vars.option:
                __extract(db.resource(request.args[-1]), request.vars.option)

        selectable = lambda ids: db(db.resource.id.belongs(ids)).delete()
        fields = [db.resource.id, db.resource.resource, db.resource.title, db.resource.publisher, db.resource.year, db.resource.rtype, db.resource.category, db.resource.state, db.resource.votes]
        orderby=~db.resource.id
        response.title = T("Administrate Resource") + response.title

    grid = SQLFORM.smartgrid(db.resource, fields=fields, onvalidation=onvalidation, create=False, links=links, selectable=selectable, linked_tables=['review'], links_in_grid=False, ignore_rw=True, orderby=orderby, selectable_submit_button=T('Delete'))

    heading=grid.elements('th')
    if heading:
        heading[0].append(INPUT(_type='checkbox', _onclick="jQuery('input[type=checkbox]').each(function(k){jQuery(this).attr('checked', 'checked');});"))

    return dict(grid=grid)

@auth.requires_signature()
def upload_file():
    """
    File upload handler for the ajax form of the plugin jquery-file-upload
    Return the response in JSON required by the plugin
    """
    try:
        import re
        from gluon.serializers import json

        resource_file = request.vars['files[]']
        resource_type = re.compile('^(\s|\.|-|\w|á|é|í|ó|ú|ñ|Á|É|Í|Ó|Ú|Ñ){1,40}\.(pdf|epub|png)$')
        filename = resource_file.filename

        if resource_type.match(filename):
            # Store file
            id = db.resource.insert(resource = db.resource.resource.store(resource_file, filename), title=filename)
            response.flash= CAT(T("I uploaded resource named "), filename)
            return response.json(json({"name": filename, "success": True, "url": URL('resource', 'edites', args=['edit', 'resource', id], user_signature=True)}))
        else:
            return response.json(json({"name": filename, "success": False, "message": T("Invalid file name")}))

    except Exception, e:
        response.flash= T("Failed uploading file")
        return response.json(json({"name": resource_file.filename, "success": False, "message": str(e)}))

@auth.requires_signature()
def admin_upload_file():
    """
    File upload handler for the ajax form of the plugin jquery-file-upload
    Return the response in JSON required by the plugin
    """
    try:
        import re
        from gluon.serializers import json

        resource_file = request.vars['files[]']
        resource_type = re.compile('^(\s|\.|-|\w|á|é|í|ó|ú|ñ|Á|É|Í|Ó|Ú|Ñ){1,40}\.(pdf|epub|png)$')
        filename = resource_file.filename

        if resource_type.match(filename):
            # Store file
            id = db.resource.insert(resource = db.resource.resource.store(request.vars['files[]'], request.vars['files[]'].filename), title=request.vars['files[]'].filename, category=request.vars['category'], rtype=request.vars['rtype'])
            response.flash= CAT(T("I uploaded resource named"), " ", request.vars['files[]'].filename)
            return response.json(json({True}))
        else:
            response.flash= CAT(T("Error filename"), " ", request.vars['files[]'].filename)
            return response.json(json({False}))
    except:
        response.flash= T("Failed uploading file")
        return response.json(json({False}))

def download_component():
    '''
    Función llamada por ajax que permite actualizar el número de descargas
    '''
    if not URL.verify(request, hmac_key=KEY): raise HTTP(403)
    import gluon.contrib.simplejson
    if request.ajax:
        resource = db.resource(request.vars.resource)
        if resource:
            resource.downloads = resource.downloads + 1
            resource.modified_on = resource.modified_on
            resource.update_record()
            response.headers['web2py-component-flash'] = T("Descargando...")
            return gluon.contrib.simplejson.dumps({'success': True, 'download': resource.downloads, 'resource': resource.id})
        else:
            response.headers['web2py-component-flash'] = T("Error en descarga, no se encontró recurso")
            return gluon.contrib.simplejson.dumps({'success': False})
    else:
        response.headers['web2py-component-flash'] = T("Error en descarga")
        return gluon.contrib.simplejson.dumps({'success': False})

def visit_component():
    '''
    Función llamada por ajax que permite actualizar el número de visitas
    '''
    if not URL.verify(request, hmac_key=KEY): raise HTTP(403)
    import gluon.contrib.simplejson
    if request.ajax:
        resource = db.resource(request.vars.resource)
        if resource:
            resource.visits = resource.visits + 1
            resource.modified_on = resource.modified_on
            resource.update_record()
            return gluon.contrib.simplejson.dumps({'success': True, 'visit': resource.visits, 'resource': resource.id})
        else:
            response.headers['web2py-component-flash'] = T("Error no se encontró recurso")
            return gluon.contrib.simplejson.dumps({'success': False})
    else:
        response.headers['web2py-component-flash'] = T("Error en visita")
        return gluon.contrib.simplejson.dumps({'success': False})

@auth.requires_signature()
def like_component():
    '''
    Función llamada por ajax que permite actualizar el número de descargas
    '''
    import gluon.contrib.simplejson
    if request.ajax:
        resource = db.resource(request.vars.resource)
        if resource:
            if auth.user.id in resource.votes_user:
                resource.votes_user.remove(auth.user.id)
                response.headers['web2py-component-flash'] = T("Unlike")
            else:
                resource.votes_user.append(auth.user.id)
                response.headers['web2py-component-flash'] = T("Like")

            resource.modified_on = resource.modified_on
            resource.votes = len(resource.votes_user)
            resource.update_record()

            return gluon.contrib.simplejson.dumps({'success': True, 'votes': resource.votes, 'resource': resource.id})
        else:
            response.headers['web2py-component-flash'] = T("Error no se encontró recurso")
            return gluon.contrib.simplejson.dumps({'success': False})
    else:
        response.headers['web2py-component-flash'] = T("Error en la votación")
        return gluon.contrib.simplejson.dumps({'success': False})

def get_informations():
    '''
    Función llamada por ajax que permite actualizar la cantidad de recursos publicados y usuarios del sistema
    '''
    if not URL.verify(request, hmac_key=KEY): raise HTTP(403)
    import gluon.contrib.simplejson
    if request.ajax:
        state_id = db(db.state.name == "Publicar").select(db.state.id, cache=(cache.ram, 86400)).first()
        count_resources = db(db.resource.state == state_id).count(cache=(cache.ram, 5))
        count_users = db(db.auth_user.id > 0).count(cache=(cache.ram, 5))

        count_downloads = vv = db((db.resource.state == state_id) & (db.resource.downloads > 0)).select(db.resource.downloads.sum(), cache=(cache.ram, 5)).first()[db.resource.downloads.sum()]

        return gluon.contrib.simplejson.dumps({'resources': count_resources, 'users': count_users, 'downloads': count_downloads})
    else:
        return gluon.contrib.simplejson.dumps({'resources': 0, 'users': 0, 'downloads': 0})


def title_selection():
    '''
    Búsqueda rápida
    '''
    if not URL.verify(request, hmac_key=KEY): raise HTTP(403)

    if not request.vars.q:
        return ''

    pattern = request.vars.q + '%'
    state = db(db.state.name == "Publicar").select(db.state.id, cache=(cache.ram, 86400)).first()
    query = db.resource.state == state.id

    query &= db.resource.title.like(pattern)

    q=c=t=y=i=""

    if request.vars.q:
        q=request.vars.q

    if request.vars.c:
        query &= db.resource.category == int(request.vars.c)
        c=request.vars.c

    if request.vars.t:
        query &= db.resource.rtype == int(request.vars.t)
        t=request.vars.t

    if request.vars.y:
        query &= db.resource.year == int(request.vars.y)
        y=request.vars.y

    selections = [registro for registro in
                     db(query).select(db.resource.id, db.resource.title, limitby=(0,5))]
    return ''.join([LI(A(k.title, _href=URL('resource', 'search_component.load', vars=dict(q=q, c=c, t=t, y=y, i=k.id)), **{"_data-w2p_disable_with": "default", "_data-w2p_method": "GET", "_data-w2p_target": request.vars.cid})).xml() for k in selections])

@cache.action()
def download():
    """
    Download upload field
    """
    return response.download(request, db)
