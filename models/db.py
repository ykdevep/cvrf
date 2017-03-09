# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------
# This scaffolding model makes your app work on Google App Engine too
# File is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

if request.global_settings.web2py_version < "2.14.1":
    raise HTTP(500, "Requires web2py 2.13.3 or newer")

# -------------------------------------------------------------------------
# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# -------------------------------------------------------------------------
# request.requires_https()

# -------------------------------------------------------------------------
# app configuration made easy. Look inside private/appconfig.ini
# -------------------------------------------------------------------------
from gluon.contrib.appconfig import AppConfig

# -------------------------------------------------------------------------
# once in production, remove reload=True to gain full speed
# -------------------------------------------------------------------------
myconf = AppConfig(reload=True)

if not request.env.web2py_runtime_gae:
    # ---------------------------------------------------------------------
    # if NOT running on Google App Engine use SQLite or other DB
    # ---------------------------------------------------------------------
    db = DAL(myconf.get('db.uri'),
             pool_size=myconf.get('db.pool_size'),
             migrate_enabled=myconf.get('db.migrate'))
else:
    # ---------------------------------------------------------------------
    # connect to Google BigTable (optional 'google:datastore://namespace')
    # ---------------------------------------------------------------------
    db = DAL('google:datastore+ndb')
    # ---------------------------------------------------------------------
    # store sessions and tickets there
    # ---------------------------------------------------------------------
    session.connect(request, response, db=db)
    # ---------------------------------------------------------------------
    # or store session in Memcache, Redis, etc.
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
    # ---------------------------------------------------------------------

# -------------------------------------------------------------------------
# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
# -------------------------------------------------------------------------
response.generic_patterns = ['*'] if request.is_local else []
# -------------------------------------------------------------------------
# choose a style for forms
# -------------------------------------------------------------------------
response.formstyle = myconf.get('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.get('forms.separator') or ''

# -------------------------------------------------------------------------
# (optional) optimize handling of static files
# -------------------------------------------------------------------------
response.optimize_css = 'concat,minify,inline'
response.optimize_js = 'concat,minify,inline'

# -------------------------------------------------------------------------
# (optional) static assets folder versioning
# -------------------------------------------------------------------------
# response.static_version = '0.0.0'

# -------------------------------------------------------------------------
# Here is sample code if you need for
# - email capabilities
# - authentication (registration, login, logout, ... )
# - authorization (role based authorization)
# - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
# - old style crud actions
# (more options discussed in gluon/tools.py)
# -------------------------------------------------------------------------

from gluon.tools import Auth, Service, PluginManager

# host names must be a list of allowed host names (glob syntax allowed)
auth = Auth(db, host_names=myconf.get('host.names'))

def __category(row):
    """
    Gets categories format c/c1/c2
    """
    if(row.category == None):
        return row.name
    else:
        return __category(db.category(row.category))+'/'+ row.name

db.define_table('category',
    Field('name', 'string', length=50, requires=IS_NOT_EMPTY(), label=T('Name')),
    Field('description', 'text', label=T('Description')),
    Field('category', 'reference category', ondelete="SET NULL", writable=False, readable=False, default=None, label=T('Category')),
    format=lambda r: __category(r))

db.category._singular = T("Category")
db.category._plural = T("Categories")

db.define_table('rtype',
    Field('name', 'string', length=50, requires=IS_NOT_EMPTY(), label=T('Type'), comment=T("Type name")),
    Field('description', 'text', label=T('Description')),
    format='%(name)s')

db.rtype._singular = T("Type")
db.rtype._plural = T("Types")

auth.settings.extra_fields['auth_user'] = [
    Field('notification', "boolean", default=False, label=T("Email notification")),
    Field('categories', "list:reference category", default=[], readable=False, writable=False, label=T("Categories"), comment=T("List the ids of categories")),
    Field('types', "list:reference rtype", default=[], readable=False, writable=False, label=T("Types"), comment=T("List the ids of types"))]

service = Service()
plugins = PluginManager()

# -------------------------------------------------------------------------
# create all tables needed by auth if not custom tables
# -------------------------------------------------------------------------
auth.define_tables(username=True, signature=False)

#Active directory UPR
from gluon.contrib.login_methods.ldap_auth import ldap_auth

auth.settings.login_methods.append(ldap_auth(mode='ad', server=myconf.take('ad.server'), base_dn=myconf.take('ad.base_dn'), manage_user=True, user_firstname_attrib='cn:1', user_lastname_attrib='cn:2', user_mail_attrib='mail', db=db))

#Gmail auth
from gluon.contrib.login_methods.email_auth import email_auth
auth.settings.login_methods.append(
    email_auth("smtp.gmail.com:587", "@gmail.com "))

#Facebook id and key
'''
client_id = ""
client_secret = ""
auth_url = ""
token_url = ""

from gluon.contrib.login_methods.oauth20_account import OAuthAccount
auth.settings.login_form=OAuthAccount(client_id, client_secret, auth_url, token_url)
'''

db._common_fields.append(auth.signature)

# -------------------------------------------------------------------------
# configure email
# -------------------------------------------------------------------------
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.get('smtp.server')
mail.settings.sender = myconf.get('smtp.sender')
mail.settings.login = myconf.get('smtp.login')
mail.settings.tls = myconf.get('smtp.tls') or False
mail.settings.ssl = myconf.get('smtp.ssl') or False

# all we need is login
auth.settings.actions_disabled=['retrieve_username'] #,'register','profile', 'request_reset_password']

# you don't have to remember me
auth.settings.remember_me_form = True

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True
auth.settings.create_user_groups = None

#Define website configuration
db.define_table('website',
    Field('name', 'string', length=10, requires=IS_NOT_EMPTY(), label=T('Website name')),
    Field('intitution', 'string', length=250, requires=IS_NOT_EMPTY(), label=T('Intitution')),
    Field('description', 'text', requires=IS_NOT_EMPTY(), label=T('Description')),
    Field('is_enabled', 'boolean', default=False, label=T('Is enabled')),
    Field('paginate', 'integer', default=20, label=T('Search pagination'), comment=T("It was used in the search of resources and users")),
    Field('keywords', 'list:string', label=T("Keywords"), comment=T("Enter some keywords for this website.")),
    Field('contact_email', 'string', requires=IS_NOT_EMPTY(), label=T('Contact email'), comment=T("Webmaster email")),
    Field('request_app', default=request.env.http_host, update= request.env.http_host, writable=False, label=T("Request tenant")),
    format='%(name)s')

db.website._singular = T("Website")
db.website._plural = T("Websites")

def websiteInsertBefore(f):
    """
    Callback for updated is_enabled field in the table website
    """
    try:
        if f.has_key('is_enabled'):
            if f['is_enabled']:
                db(db.website.id > 0).update(is_enabled=False)
        return None
    except Exception, e:
        return True

db.website._before_insert.append(lambda f: websiteInsertBefore(f))

def websiteUpdateBefore(s, f):
    """
    Callback for updated is_enabled field in the table website
    """
    try:
        if f.has_key('is_enabled'):
            if f['is_enabled']:
                db(db.website.id > 0).update(is_enabled=False)
        return None
    except Exception, e:
        return True

db.website._before_update.append(lambda s,f: websiteUpdateBefore(s,f))