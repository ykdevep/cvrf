# -*- coding: utf-8 -*-
from gluon.scheduler import Scheduler
from datetime import timedelta as timed, datetime

db_task = DAL(myconf.take('db.uri_task'), pool_size=myconf.take('db.pool_size', cast=int), check_reserved=['common'])

def user_notifications():
    """
    User notifications by date of resource modification
    """

    website = db((db.website.id > 0) & (db.website.is_enabled == True)).select(cache=(cache.ram, 60), cacheable=True).first()

    if website:

        for user in db((db.auth_user.id > 0) & (db.auth_user.notification == True)).select(db.auth_user.email, db.auth_user.id):

            r =  UL()

            for resource in db((db.resource.state == 3) & (db.resource.modified_on == datetime.today())).select():
                r.append(LI(CAT(A(resource.title, _href=URL('resource', 'view', args=resource.id, scheme='http', host=website.request_app)))))

            if len(r) > 0 and user.email:
                mail.send(user.email,
                          'Notificación para usuarios',
                          ('<html>'+str(CAT(H1("Notificacion del sitio web"), website.name))+str(r)+str(H3("Atentamente."))+'</html>'))

def revisor_notifications():
    """
    Email notifications
    """

    website = db((db.website.id > 0) & (db.website.is_enabled == True)).select(cache=(cache.ram, 60), cacheable=True).first()

    if website:

        for user in db((db.auth_user.id == db.auth_membership.user_id) & (db.auth_membership.group_id == 2)).select(db.auth_user.categories, db.auth_user.email, db.auth_user.id):

            r =  UL()

            for resource in db((db.resource.state == 2) & (db.resource.category.belongs(user.categories))).select():
                r.append(LI(CAT(A(resource.title, _href=URL('resource', 'revised', scheme='http', host=website.request_app)))))

            if len(r) > 0 and user.email:
                mail.send(user.email,
                          'Notificación de revisión',
                          ('<html>'+str(CAT(H1("Notificacion del sitio web"), website.name))+str(r)+str(H3("Atentamente."))+'</html>'))

    db.commit()

def admin_notifications():
    """
    Email notifications
    """
    
    print db

    db.commit()

scheduler = Scheduler(db_task, dict(admin_notifications=admin_notifications, revisor_notifications=revisor_notifications, user_notifications=user_notifications))
