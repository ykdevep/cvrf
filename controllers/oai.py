# -*- coding: utf-8 -*-
# intente algo como
def index(): 
    '''
    '''
    resources = db(db.resource.id > 0).select()
    return dict(message="hello from oai.py", resources=resources)
