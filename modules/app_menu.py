#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *

def getCategory(id):
    # busco los datos de los hijos en la db
    db = current.db

    menus = db(db.category.category == id).select(cache=(current.cache.ram, 600), cacheable=True)

    # declaro una lista Hijo
    menu_child = []
    # recorro la tabla de los hijos
    for menu in menus:
        menu_other = getCategory(menu.id)

        q=c=t=""

        if current.request.vars.q:
            q=current.request.vars.q

        if current.request.vars.c:
            c=current.request.vars.c

        if current.request.vars.t:
            t=current.request.vars.t

        attr = None

        if c == str(menu.id) and not attr:
            attr = "menu-active"

        count_category = db((db.resource.category == menu.id) & (db.resource.state == 3)).count()

        # añado a la lista hijo cada uno de los registros encontrados
        menu_child.append(getMenu(menu.id, menu.name, menu.description, q, menu.id, t, menu_other, attr, count_category))

    return menu_child

def getType(id):
    # busco los datos de los hijos en la db
    db = current.db

    menus = db(db.rtype.id > 0).select(cache=(current.cache.ram, 600), cacheable=True)

    q=c=t=""

    if current.request.vars.q:
        q=current.request.vars.q

    if current.request.vars.c:
        c=current.request.vars.c

    if current.request.vars.t:
        t=current.request.vars.t

    # declaro una lista Hijo
    menu_child = []
    # recorro la tabla de los hijos
    for menu in menus:

        attr = None

        if t == str(menu.id) and not attr:
            attr = "menu-active"

        count_type = db((db.resource.rtype == menu.id) & (db.resource.state == 3)).count()

        # añado a la lista hijo cada uno de los registros encontrados
        menu_child.append(getMenu(menu.id, menu.name, menu.description, q, c, menu.id, [], attr, count_type))

    return menu_child

def getMenu(id, name, title, q, c, t, menu_other, attr, count):
    """
    Get menu of formated
    """
    get_vars = {"q": q, "c": c, "t": t}
    if current.request.page:
        get_vars = {"q": q, "page": current.request.page, "c": c, "t": t}
    return [name, False, A(CAT(name, SPAN(count, _class="badge", _style="float: right;")), _class=attr, _title=title, _href=URL("default", "index.html", vars=get_vars), **{'_data-toggle': "tooltip", '_data-placement': "right"}), menu_other]
