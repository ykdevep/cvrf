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

@cache.action()
def download():
    """
    Download upload field
    """
    return response.download(request, db)
