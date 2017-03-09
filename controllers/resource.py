# -*- coding: utf-8 -*-
# intente algo como
@auth.requires_login()
def my_briefcase():
    """
    Descargar todos los recursos que son de mi interés (a los que le di mi voto) en formato .zip
    """
    editable = False

    selectable = lambda ids: resource_quit(ids)

    if (auth.has_membership('Administrador') or auth.has_membership('Revisor')):
        editable = deletable = True

    query = db.resource.votes_user.contains(auth.user.id, all=True)
    left = db.resource.on((db.resource.state == db.state.id) & (db.state.name == "Publicado"))
    fields = [db.resource.id, db.resource.resource, db.resource.title,  db.resource.language, db.resource.category, db.resource.rtype, db.resource.year]

    grid = SQLFORM.grid(query, left=left, selectable=selectable, fields=fields, orderby=~db.resource.id, create=False, deletable=deletable, editable=editable, links_in_grid=False)

    heading=grid.elements('th')
    if heading:
           heading[0].append(INPUT(_type='checkbox', _onclick="jQuery('input[type=checkbox]').each(function(k){jQuery(this).attr('checked', 'checked');});"))

    response.title = T("My Briefcase") + response.title
    response.flash = T("My Briefcase")

    return dict(grid=grid)

@auth.requires_login()
def resource_quit(ids):
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

    for register in db((db.resource.votes_user.contains(auth.user.id, all=True)) & (db.resource.state == db.state.id) & (db.state.name == "Publicado")).select(db.resource.category, db.resource.title, db.resource.mime_type, db.resource.resource):
        fullpath = app_tools.retrieve_file_properties(register.resource)
        if register.mime_type == "epub+zip":
            files.write(fullpath, register.category.name+"/"+register.title+'.epub')
        else:
            files.write(fullpath, register.category.name+"/"+register.title+'.'+register.mime_type)

    files.close()
    response.headers['Content-Type'] = 'application/zip'
    response.headers['Content-Disposition'] = CAT('attachment=True; filename=', T('my_briefcase'), '.zip')
    out.seek(0)

    return response.stream(out, request=request)

@auth.requires_login()
@auth.requires(lambda:  to_review())
def revised():
    """
    """
    links=[]

    selectable = lambda ids: db(db.resource.id.belongs(ids)).delete()
    query = ((db.resource.state == 2) & (db.resource.category.belongs(auth.user.categories)))

    fields = [db.resource.id, db.resource.title,  db.resource.language, db.resource.category, db.resource.state]

    grid = SQLFORM.grid(query, selectable=selectable, fields=fields, orderby=~db.resource.id, create=False, links=links, links_in_grid=False)

    heading=grid.elements('th')
    if heading:
           heading[0].append(INPUT(_type='checkbox', _onclick="jQuery('input[type=checkbox]').each(function(k){jQuery(this).attr('checked', 'checked');});"))

    return dict(grid=grid)

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
            __extract(db.resource(request.args[-1]), request.vars.option)

    selectable = lambda ids: db(db.resource.id.belongs(ids)).delete()

    query = (db.resource.created_by == auth.user.id)
    left = (db.resource.on((db.resource.state == db.state.id) & ((db.state.name == "Edición") | (db.state.name == "Rechazado"))))
    fields = [db.resource.id, db.resource.resource, db.resource.title,  db.resource.language, db.resource.category, db.resource.rtype, db.resource.year]

    grid = SQLFORM.grid(query, left=left, selectable=selectable, fields=fields, links=links, orderby=~db.resource.id, create=False, links_in_grid=False)

    heading=grid.elements('th')
    if heading:
           heading[0].append(INPUT(_type='checkbox', _onclick="jQuery('input[type=checkbox]').each(function(k){jQuery(this).attr('checked', 'checked');});"))

    response.title = T("Editar") + response.title

    return dict(grid=grid)

def __extract(resource, option):
    '''
    Función auxiliar que permite extraer los metadatos o extraer imagen del cover de un recurso en edición
    '''

    import app_resource

    if  option == "coverpage":
        try:
            classResource = app_resource.resourceMetadata(resource.resource)
            resource.update_record(**classResource.coverpage())
            response.flash = T("Take image")
        except Exception, e:
            response.flash = T("Failed to take image")
    elif option == "metadata":
        try:
            classResource = app_resource.resourceMetadata(resource.resource)
            resource.update_record(**classResource.getMetadata())
            response.flash = T("Extract metadata")
        except Exception, e:
            response.flash = T("Failed to extract metadata")
    else:
        response.flash = T("Error option not found")

@auth.requires_membership("Revisors")
def table():
    """
    Administrate tables
    """
    table = request.args(0) or 'publisher'
    if not table in db.tables(): grid=None

    selectable = lambda ids: db(db[table].id.belongs(ids)).delete()

    grid = SQLFORM.smartgrid(db[table], args=request.args[:1], linked_tables=[], selectable=selectable)

    heading=grid.elements('th')
    if heading:
        heading[0].append(INPUT(_type='checkbox', _onclick="jQuery('input[type=checkbox]').each(function(k){jQuery(this).attr('checked', 'checked');});"))

    response.flash = T(table.replace("_", " "))

    return dict(grid=grid)

def is_public():
    """
    Validate that is public resource
    """
    resource = db((db.resource.id == request.args[-1]) & (db.resource.state == 3)).isempty()
    if resource:
        return False
    return True

def add_vote():
    """
    Add vote of auth user
    """
    resource = db.resource(request.args(0))

    if resource:
        votes_user = resource.votes_user
        form = FORM(INPUT(_type='submit'))

        if form.validate():
            if auth.user.id in resource.votes_user:
                votes_user.remove(auth.user.id)
                response.flash = T("Remove star")
            else:
                votes_user.append(auth.user.id)
                response.flash = T("Give star")
            resource.update_record(votes_user=resource.votes_user, modified_on=resource.modified_on)

        return dict(form=form, vote_by_my=(auth.user.id in resource.votes_user), votes = len(resource.votes_user))
    else:
        return dict(form=None, vote_by_my=None, votes=None)

def vote():
    """
    Gets votes
    """
    resource = db.resource(request.args(0))
    if resource:
        votes = len(resource.votes_user)
    else:
        votes = None
    return dict(votes=votes)

def add_comment():
    """
    Add comment to resource
    """

    form=SQLFORM(db.comment, submit_button=T('Comment'))
    if form.validate():
        db.comment.insert(body=request.vars.body, resource=request.args(0))
        response.flash = T('Add comment')
    return dict(form=form, comments=db(db.comment.resource == request.args(0)).select())

def comment():
    """
    Get comments
    """
    return dict(comments=db(db.comment.resource == request.args(0)).select())

def view():
    """
    View resource by id
    """
    resource = db.resource(request.args(0))

    if resource:
        if resource.state != 3:
            return dict(resource = None)

        resource.update_record(visits = int(resource.visits)+1, modified_on=resource.modified_on)

    response.title = CAT(T('View').upper(), " | ", website.intitution)

    return dict(resource=resource)

@cache.action()
def downloads():
    """
    Updating downloads of resource
    """
    resource = db.resource(request.args(0))
    if resource:
        resource.update_record(downloads = resource.downloads + 1, modified_on=resource.modified_on)
    return response.download(request, db)


@auth.requires_membership("Administrador")
def admin_table():
    """
    Administrate tables
    """
    table = request.args(0) or 'auth_user'
    if not table in db.tables(): grid=None

    selectable = lambda ids: db(db[table].id.belongs(ids)).delete()

    grid = SQLFORM.smartgrid(db[table], args=request.args[:1], linked_tables=[], selectable=selectable)

    heading=grid.elements('th')
    if heading:
           heading[0].append(INPUT(_type='checkbox', _onclick="jQuery('input[type=checkbox]').each(function(k){jQuery(this).attr('checked', 'checked');});"))

    response.title = T(table.replace("_", " ").capitalize()) + response.title
    response.flash = T(table.replace("_", " ").capitalize())

    return dict(grid=grid)

@auth.requires_membership("Administrador")
def admin_category():
    """
    Administrate categories
    """
    selectable = lambda ids: db(db.category.id.belongs(ids)).delete()

    fields = [db.category.id, db.category.name]
    grid = SQLFORM.smartgrid(db.category, fields=fields, selectable=selectable, linked_tables=['category'])

    heading=grid.elements('th')
    if heading:
           heading[0].append(INPUT(_type='checkbox', _onclick="jQuery('input[type=checkbox]').each(function(k){jQuery(this).attr('checked', 'checked');});"))

    response.title = T("Administrate categories") + response.title
    response.flash = T("Administrate categories")
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
    selectable=orderby=fields=None

    if not "comment.resource" in request.args:

        response.flash = T("Administrate resources")

        if "edit" in request.args:
            links.append({'header': T('Extract'), 'body': lambda row: A(XML('<i class="glyphicon glyphicon-plus"></i> '), _class="btn btn-info btn-menu", _href=URL(args=request.args, vars=dict(option="metadata"), user_signature=True, hash_vars=False),**{'_data-toggle': "tooltip", '_title': T("Extract metadata file"), '_data-placement': "top"})})

            links.append({'header': T('Take coverpage'), 'body': lambda row: A(XML('<i class="glyphicon glyphicon-camera"></i> '), _class="btn btn-info btn-menu", _href=URL(args=request.args, vars=dict(option="coverpage"), user_signature=True, hash_vars=False), **{'_data-toggle': "tooltip", '_title': T("Take coverpage image"), '_data-placement': "top"})})

            if request.vars.option:
                __extract(db.resource(request.args[-1]), request.vars.option)

        selectable = lambda ids: db(db.resource.id.belongs(ids)).delete()
        fields = [db.resource.id, db.resource.resource, db.resource.title, db.resource.publisher, db.resource.rtype, db.resource.category, db.resource.state, db.resource.votes]
        orderby=~db.resource.id
        response.title = T("Administrate Resource") + response.title

    else:
        selectable = lambda ids: db(db.comment.id.belongs(ids)).delete()
        fields = [db.comment.id, db.comment.body, db.comment.resource]
        response.title = T("Administrate comments") + response.title
        response.flash = T("Administrate comments")

    grid = SQLFORM.smartgrid(db.resource, fields=fields, links=links, selectable=selectable, linked_tables=['comment'], links_in_grid=False, ignore_rw=True, orderby=orderby)

    heading=grid.elements('th')
    if heading:
        heading[0].append(INPUT(_type='checkbox', _onclick="jQuery('input[type=checkbox]').each(function(k){jQuery(this).attr('checked', 'checked');});"))

    return dict(grid=grid)

@auth.requires_login()
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
            return response.json(json({"name": filename, "success": True}))
        else:
            return response.json(json({"name": filename, "success": False, "message": T("Invalid file name")}))

    except Exception, e:
        response.flash= T("Failed uploading file")
        return response.json(json({"name": resource_file.filename, "success": False, "message": str(e)}))

@auth.requires_membership("Administrador")
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
