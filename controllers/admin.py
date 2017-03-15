# -*- coding: utf-8 -*-
# intente algo como
@auth.requires_membership("Administrador")
def website():
    """
    Admin website
    """
    response.flash = T("Administrate website")
    response.title = T("Administrate website")+response.title

    selectable = lambda ids: db(db.website.id.belongs(ids)).delete()

    fields = [db.website.name, db.website.is_enabled, db.website.request_app]

    grid = SQLFORM.smartgrid(db.website, selectable=selectable, fields=fields, linked_tables=[], exportclasses=dict(json=False, csv_with_hidden_cols=False, csv=False, xml=False, html=False))

    heading=grid.elements('th')
    if heading:
           heading[0].append(INPUT(_type='checkbox', _onclick="jQuery('input[type=checkbox]').each(function(k){jQuery(this).attr('checked', 'checked');});"))
    return dict(grid=grid)

@auth.requires_membership("Administrador")
def user_roles():
    """
    Administrate users and users group
    """

    selectable = lambda ids: db(db.auth_user.id.belongs(ids)).delete()

    grid = SQLFORM.smartgrid(db.auth_user, selectable=selectable, linked_tables=['auth_membership'], ignore_rw=True, exportclasses=dict(json=False, csv_with_hidden_cols=False, csv=False, xml=False, html=False))

    heading=grid.elements('th')
    if heading:
           heading[0].append(INPUT(_type='checkbox', _onclick="jQuery('input[type=checkbox]').each(function(k){jQuery(this).attr('checked', 'checked');});"))

    response.flash = T("Administrate users")
    response.title = T("Administrate users")+response.title
    return dict(grid=grid)

@auth.requires_membership("Administrador")
def category():
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

@auth.requires_membership("Administrador")
def scheduler_task():
    """
    Administrate scheduler task
    """
    selectable = lambda ids: db_task(db_task.scheduler_task.id.belongs(ids)).delete()
    fields = [db_task.scheduler_task.id, db_task.scheduler_task.task_name, db_task.scheduler_task.status, db_task.scheduler_task.function_name]

    grid = SQLFORM.smartgrid(db_task.scheduler_task, selectable=selectable, linked_tables=[], fields=fields, exportclasses=dict(json=False, csv_with_hidden_cols=False, csv=False, xml=False, html=False))

    heading=grid.elements('th')
    if heading:
           heading[0].append(INPUT(_type='checkbox', _onclick="jQuery('input[type=checkbox]').each(function(k){jQuery(this).attr('checked', 'checked');});"))

    response.flash = T("Administrate scheduler task")
    response.title = T("Administrate scheduler task")+response.title
    return dict(grid=grid)

@cache.action()
def download():
    return response.download(request, db)
