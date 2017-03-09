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
        page = int(current.request.vars.page or 1)-1
    except ValueError:
        page = 0
    def __self_link(name, p):
        d = dict(current.request.vars, page=p+1)
        return A(name, _href=URL('default', 'index.html', args=current.request.args, vars=d))
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
