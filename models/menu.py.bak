# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# ----------------------------------------------------------------------------------------------------------------------
# Customize your APP title, subtitle and menus here
# ----------------------------------------------------------------------------------------------------------------------

response.logo = H5(A(IMG(_src=URL('static', 'img/favicon.png'), _class="logo"),  _class="navbar-brand-name", _href=URL('default', 'index'),
                  _id="index", **{'_data-target': "#index"}))

website = db((db.website.id > 0) & (db.website.is_enabled == True)).select(cache=(cache.ram, 60), cacheable=True).first()

PAGINATE = 20
response.meta.generator = myconf.get('app.generator')

if website:

    response.title = CAT(" | ", website.intitution)
    response.subtitle = website.name.replace('_',' ').upper()

    ## read more at http://dev.w3.org/html5/markup/meta.name.html
    response.meta.author = website.contact_email
    response.meta.description = website.description
    response.meta.keywords = ' '.join(["%s" % k.upper() for k in website.keywords])

    PAGINATE = website.paginate

else:

    response.title = CAT(' | ', request.application.replace('_', ' ').title().upper())
    response.subtitle = ''

    # ----------------------------------------------------------------------------------------------------------------------
    # read more at http://dev.w3.org/html5/markup/meta.name.html
    # ----------------------------------------------------------------------------------------------------------------------
    response.meta.author = myconf.get('app.author')
    response.meta.description = myconf.get('app.description')
    response.meta.keywords = myconf.get('app.keywords')

# ----------------------------------------------------------------------------------------------------------------------
# your http://google.com/analytics id
# ----------------------------------------------------------------------------------------------------------------------
response.google_analytics_id = None

# ----------------------------------------------------------------------------------------------------------------------
# this is the main application menu add/remove items as required
# ----------------------------------------------------------------------------------------------------------------------

PRODUCTION_MENU = True


# ----------------------------------------------------------------------------------------------------------------------
# provide shortcuts for development. remove in production
# ----------------------------------------------------------------------------------------------------------------------

response.menu = [("home", False, A(T('Home'), _href=URL("default", "index")+"#homepage", **{'_data-target': "#homepage"}))]
response.menu += [("services", False, A(T('Services'), _href=URL("default", "index")+"#services", **{'_data-target': "#services"}))]
response.menu += [("about", False, A(T('About'), _href=URL("default", "index")+"#about", **{'_data-target': "#about"}))]
response.menu += [("information", False, A(T('Contact us'), _href=URL("default", "index")+"#information", **{'_data-target': "#information"}))]

#########################################################################
## provide shortcuts for development. remove in production
#########################################################################

def _():
    # Menu del administrador
    if(auth.has_membership("Administrador")):
        response.menu += [(T("Administration"),False, URL("default", "dashboard"), [
            ("user_roles", False, A(CAT(XML('<ico class="glyphicon glyphicon-user"></ico> '), T("Users")), _href=URL("admin", "user_roles"), **{"_data-target": "#user_roles"})),
            ("website", False, A(CAT(XML('<ico class="glyphicon glyphicon-home"></ico> '), T("Website")), _href=URL("admin", "website", ), **{"_data-target": "#website"})),
            ("admin", False, A(CAT(XML('<ico class="glyphicon glyphicon-book"></ico> '), T("Resources")), _href=URL("resource", "admin"), **{"_data-target": "#admin"})),
            ("upload", False, A(CAT(XML('<ico class="glyphicon glyphicon-upload"></ico> '), T("Multiple Uploads")), _href=URL("resource", "upload_multiple"), **{"_data-target": "#upload_multiple"})),
            ("manage", False, A(CAT(XML('<ico class="glyphicon glyphicon-lock"></ico> '), T("Appadmin")), _href=URL("appadmin", 'index'), **{"_data-target": "#manage"})),
            ("category", False, A(CAT(XML('<ico class="glyphicon glyphicon-tags"></ico> '), T("Categories")), _href=URL("admin", "category"), **{"_data-target": "#category"})),
            ("scheduler_task", False, A(CAT(XML('<ico class="glyphicon glyphicon-tasks"></ico> '), T("Scheduler Task")), _href=URL("admin", "scheduler_task"), **{"_data-target": "#scheduler_task"})),
            ("rtype", False, A(CAT(XML('<ico class="glyphicon glyphicon-tag"></ico> '), T("Types")), _href=URL("admin", "table", args=["rtype"]), **{"_data-target": "#rtype"})),
            ("language", False, A(CAT(XML('<ico class="glyphicon glyphicon-flag"></ico> '), T("Language")), _href=URL("resource", "admin_table", args=["language"]), **{"_data-target": "#language"})),
            ]
            )]

    if(auth.user):
        other_menu = []

        other_menu.append(("dashboard", False, A(CAT(XML('<ico class="glyphicon glyphicon-home"></ico> '), T("Dashboard")), _href=URL("default", "dashboard"), **{"_data-target": "#dashboard"})))
        other_menu.append(("upload", False, A(CAT(XML('<ico class="glyphicon glyphicon-upload"></ico> '), T("Upload and edit")), _href=URL("resource", "edites"), **{"_data-target": "#edites"})))
        other_menu.append(("resources", False, A(CAT(XML('<ico class="glyphicon glyphicon-briefcase"></ico> '), T("My briefcase")), _href=URL("resource", "my_briefcase"), **{"_data-target": "#my_briefcase"})))

        if(auth.has_membership("Revisor")):
            other_menu.append(("revised", False, A(CAT(XML('<ico class="glyphicon glyphicon-book"></ico> '), T("To Revised")), _href=URL("resource", "revised"), **{"_data-target": "#revised"})))
            other_menu.append(("publisher", False, A(CAT(XML('<ico class="glyphicon glyphicon-edit"></ico> '), T("Publisher")), _href=URL("resource", "admin_table", args =["publisher"]), **{"_data-target": "#publisher"})))

        if(auth.has_membership("Publicador")):
            other_menu.append(("publish", False, A(CAT(XML('<ico class="glyphicon glyphicon-leaf"></ico> '), T("To Published")), _href=URL("resource", "publish"), **{"_data-target": "#publish"})))

        response.menu += [(T("Resource"),False, URL("default", "dashboard"), other_menu)]

if PRODUCTION_MENU:
    _()
