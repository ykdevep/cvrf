# -*- coding: utf-8 -*-
# intente algo como

def index():
    '''
    Función que permite agregar un typo de recurso para recolectar metadatos
    '''

    response.title = T("Agregar Revista")+response.title

    form = SQLFORM(db.rtype, submit_button=T('Add'))

    if form.process().accepted:
        response.flash = T("Revista agregada")
    elif form.errors:
        response.flash = T("El formulario tiene errores")
    else:
        response.flash = T("Agregar Revista")

    return dict(form=form)
