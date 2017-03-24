#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *

def retrieve_file_properties(name):
    """
    Metodo copiado por la dal de web2py, permite obtener los datos de los archivos
    upload
    """
    try:
        import os
        from pydal.helpers import regex
        m = regex.REGEX_UPLOAD_PATTERN.match(name)

        t = m.group('table')
        f = m.group('field')
        u = m.group('uuidkey')

        #path = os.path.join(request.folder,'uploads', "%s.%s" % (t, f), u[:2])
        full_path = os.path.join(current.request.folder,'nfs-uploads', "%s.%s" % (t, f), u[:2], name)
        return full_path
    except Exception, e:
        raise IOError

def paginator(paginate, count):
    """
    Web2py paginator
    """
    try:
        page = int(current.request.vars.p or 1)-1
    except ValueError:
        page = 0
    def __self_link(name, p):
        d = dict(current.request.vars, p=p+1)
        return A(name, _href=URL(args=current.request.args, vars=d), cid=current.request.cid)
    paginator = UL()
    if paginate and paginate < count:
        npages, reminder = divmod(count, paginate)
        if reminder:
            npages += 1
        NPAGES = 5  # window is 2*NPAGES
        if page > NPAGES + 1:
            paginator.append(LI(__self_link('<<', 0)))
        if page > NPAGES:
            paginator.append(LI(__self_link('<', page - 1)))
        pages = range(max(0, page - NPAGES), min(page + NPAGES, npages))
        for p in pages:
            if p == page:
                paginator.append(LI(A(p + 1, _onclick='return false'), _class='current'))
            else:
                paginator.append(LI(__self_link(p + 1, p)))
        if page < npages - NPAGES:
            paginator.append(LI(__self_link('>', page + 1)))
        if page < npages - NPAGES - 1:
            paginator.append(LI(__self_link('>>', npages - 1)))
    return paginator

def paginator_comments(paginate, count):
    """
    Web2py paginator
    """
    try:
        page = int(current.request.vars.p or 1)-1
    except ValueError:
        page = 0
    def __self_link(name, p):
        d = dict(p=p+1)
        return A(name, _href=URL(args=current.request.args, vars=d), cid=current.request.cid)
    paginator = UL()
    if paginate and paginate < count:
        npages, reminder = divmod(count, paginate)
        if reminder:
            npages += 1
        NPAGES = 5  # window is 2*NPAGES
        if page > NPAGES + 1:
            paginator.append(LI(__self_link('<<', 0)))
        if page > NPAGES:
            paginator.append(LI(__self_link('<', page - 1)))
        pages = range(max(0, page - NPAGES), min(page + NPAGES, npages))
        for p in pages:
            if p == page:
                paginator.append(LI(A(p + 1, _onclick='return false'), _class='current'))
            else:
                paginator.append(LI(__self_link(p + 1, p)))
        if page < npages - NPAGES:
            paginator.append(LI(__self_link('>', page + 1)))
        if page < npages - NPAGES - 1:
            paginator.append(LI(__self_link('>>', npages - 1)))
    return paginator

def getCategory(id, state_id):
    # busco los datos de los hijos en la db
    db = current.db

    menus = db(db.category.category == id).select(cache=(current.cache.ram, 60), cacheable=True)

    # declaro una lista Hijo
    menu_child = []
    # recorro la tabla de los hijos
    for menu in menus:
        menu_other = getCategory(menu.id, state_id)

        q=c=t=y=i=""

        if current.request.vars.q:
            q=current.request.vars.q

        if current.request.vars.c:
            c=current.request.vars.c

        if current.request.vars.t:
            t=current.request.vars.t

        if current.request.vars.y:
            y=current.request.vars.y

        if current.request.vars.i:
            i=current.request.vars.i

        attr = None

        if c == str(menu.id) and not attr:
            attr = "menu-active"

        count_category = db((db.resource.category == menu.id) & (db.resource.state == state_id)).count()

        # añado a la lista hijo cada uno de los registros encontrados
        menu_child.append(getMenu(menu.id, menu.name, menu.description, q, menu.id, t, y, i, menu_other, attr, count_category))

    return menu_child

def getType(id, state_id):
    # busco los datos de los hijos en la db
    db = current.db

    menus = db(db.rtype.id > 0).select(cache=(current.cache.ram, 60), cacheable=True)

    q=c=t=y=i=""

    if current.request.vars.q:
        q=current.request.vars.q

    if current.request.vars.c:
        c=current.request.vars.c

    if current.request.vars.t:
        t=current.request.vars.t

    if current.request.vars.y:
        y=current.request.vars.y
    
    if current.request.vars.i:
        i=current.request.vars.i

    # declaro una lista Hijo
    menu_child = []
    # recorro la tabla de los hijos
    for menu in menus:

        attr = None

        if t == str(menu.id) and not attr:
            attr = "menu-active"

        count_type = db((db.resource.rtype == menu.id) & (db.resource.state == state_id)).count()

        # añado a la lista hijo cada uno de los registros encontrados
        menu_child.append(getMenu(menu.id, menu.name, menu.description, q, c, menu.id, y, i, [], attr, count_type))

    return menu_child

def getYear(id, state_id):
    # busco los datos de los hijos en la db
    db = current.db

    menus = db((db.resource.id > 0) & (db.resource.state == state_id)).select(db.resource.year, distinct=True, orderby=~db.resource.year, cache=(current.cache.ram, 60), cacheable=True)

    q=c=t=y=i=""

    if current.request.vars.q:
        q=current.request.vars.q

    if current.request.vars.c:
        c=current.request.vars.c

    if current.request.vars.t:
        t=current.request.vars.t

    if current.request.vars.y:
        y=current.request.vars.y

    if current.request.vars.i:
        i=current.request.vars.i

    # declaro una lista Hijo
    menu_child = []
    # recorro la tabla de los hijos
    for menu in menus:

        attr = None

        if y == str(menu.year) and not attr:
            attr = "menu-active"

        count_type = db((db.resource.year == menu.year) & (db.resource.state == state_id)).count()

        # añado a la lista hijo cada uno de los registros encontrados
        menu_child.append(getMenu(menu.year, menu.year, None, q, c, t, menu.year, i, [], attr, count_type))

    return menu_child


def getMenu(id, name, title, q, c, t, y, i, menu_other, attr, count):
    """
    Get menu of formated
    """
    get_vars = {"q": q, "c": c, "t": t , "y": y, "i": i}
    if current.request.p:
        get_vars = {"q": q, "p": current.request.p, "c": c, "t": t, "i": i}
    return [name, False, A(CAT(name, SPAN(count, _class="badge", _style="position: relative; float: right;")), _class=attr, _title=title, _href=URL("resource", "search_component.load", vars=get_vars), cid=current.request.cid,**{'_data-toggle': "tooltip", '_data-placement': "top"}), menu_other]
