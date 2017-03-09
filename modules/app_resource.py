#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *

from pydal.helpers import regex

import os, datetime, magic
from wand.image import Image
from pyPdf import PdfFileReader
#from epubzilla.epubzilla import Epub

CONST_IMAGE_WIDTH = 120
CONST_IMAGE_HEIGTH = 160
CONST_IMAGE_FORMAT = "png"

class resourceMetadata(object):
    """
    Class for extract metadata and created coverpage
    """
    def __init__(self, resource):
        """
        Init class width resource and coverpage dir
        """
        self.resource = resource
        self.coverpag = resource.replace(".resource", ".coverpag").replace(".pdf", ".png").replace(".epub", ".png")
        self.coverpag_path = self.retrieve_file_properties(self.coverpag)
        self.resource_path = self.retrieve_file_properties(self.resource)['full_path']
        self.pdf_toread = None
        self.pdf_info = None
        self.epub_info = None
        self.mimeType = self.mimeType()

    def retrieve_file_properties(self, name, path=None):
        """
        Metodo copiado por la dal de web2py, permite obtener los datos de los archivos
        upload
        """
        try:
            m = regex.REGEX_UPLOAD_PATTERN.match(name)

            t = m.group('table')
            f = m.group('field')
            u = m.group('uuidkey')

            path = os.path.join(current.request.folder,'nfs-uploads', "%s.%s" % (t, f), u[:2])
            full_path = os.path.join(current.request.folder,'nfs-uploads', "%s.%s" % (t, f), u[:2], name)
            return dict(path=path, full_path=full_path)
        except Exception, e:
            raise IOError

    def mimeType(self):
        mime = "pdf"
        try:
            mo = magic.open(magic.MIME_TYPE)
            mo.load()
            mime = mo.file(self.resource_path).split('/')[-1]
        except Exception, e:
            return None
        finally:
            return mime

    def getTitle(self):

        try:
            if self.mimeType == "epub+zip":
                title = self.epub_info.title
            elif self.mimeType == "pdf":
                title = str(self.pdf_info.title)
            else:
                title = None
        except Exception, e:
            return None
        finally:
            return title

    def getAuthors(self):

        try:
            if self.mimeType == "epub+zip":
                authors = str(self.epub_info.author).split(',')
            elif self.mimeType == "pdf":
                authors = str(self.pdf_info.author).split(',')
            else:
                authors = []
        except Exception, e:
            return []
        finally:
            return authors

    def getKeywords(self):
        keyword = []
        try:
            keyword = (str(self.pdf_info['/Keywords']).replace(';',',')).split(",")
        except Exception, e:
            return []
        finally:
            return keyword

    def getDateCreate(self):
        year = str(datetime.date.today())
        year = year[0]+year[1]+year[2]+year[3]
        try:
            year = str(self.pdf_info['/CreationDate'])
            year = year[2]+year[3]+year[4]+year[5]
        except Exception, e:
            return year
        finally:
            return year

    def getDateUpdate(self):
        year = str(datetime.date.today())
        year = year[0]+year[1]+year[2]+year[3]
        try:
            modDate = str(self.pdf_info['/ModDate'])
            if modDate!=None:
                year = modDate[2]+modDate[3]+modDate[4]+modDate[5]
            year = year[2]+year[3]+year[4]+year[5]
        except Exception, e:
            return year
        finally:
            return year

    def getDate(self):
        year = str(datetime.date.today())
        year = year[0]+year[1]+year[2]+year[3]
        try:
            return year
        except Exception, e:
            return year

    def best_unit_size(self, bytes_size):
        """Get a size in bytes & convert it to the best IEC prefix for readability."""
        for exp in range(0, 90 , 10):
            bu_size = abs(bytes_size) / pow(2.0, exp)
            if int(bu_size) < 2 ** 10:
                unit = {0:"bytes", 10:"KiB", 20:"MiB", 30:"GiB", 40:"TiB", 50:"PiB", 60:"EiB", 70:"ZiB", 80:"YiB"}[exp]
                break
        return {"s":bu_size, "u":unit, "b":bytes_size}

    def getSize(self):
        size = {'s':0.0, 'u':"bytes"}
        try:
            size = self.best_unit_size(os.path.getsize(self.resource_path))
        except Exception, e:
            return size
        finally:
            return float(size['s']), str(size['u'])

    def getPages(self):
        pages = 0
        try:
            pages = self.pdf_toread.getNumPages()
        except Exception, e:
            return int(pages)
        finally:
            return int(pages)

    def getMetadata(self):
        """
        Extract metadata, size and mimeType of resource
        """
        try:
            size, unit = self.getSize()
            if self.mimeType == "pdf":

                self.pdf_toread = PdfFileReader(open(self.resource_path, "r"))
                self.pdf_info = self.pdf_toread.getDocumentInfo()

                return {'size': size, 'unit': unit, 'mime_type': self.mimeType, 'pages':self.getPages(), 'title':self.getTitle(), 'author':self.getAuthors(), 'year': self.getDateCreate(), 'year_update': self.getDateUpdate(), 'keyword':self.getKeywords()}

            if self.mimeType == "epub+zip":

                self.epub_info = Epub.from_file(self.resource_path)
                epub = {'size': size, 'unit': unit, 'mime_type': self.mimeType, 'pages': 0, 'title':self.getTitle(), 'author':self.getAuthors(), 'year': "", 'year_update': "", 'keyword': ""}
                db = current.db

                for element in self.epub_info.metadata:

                    if element.tag.localname == "description":
                        epub["description"] = element.tag.text
                    elif element.tag.localname == "identifier":
                        epub["identifier"] = element.tag.text
                    elif element.tag.localname == "subject":
                        epub["keyword"] = element.tag.text.split(' ')
                    elif element.tag.localname == "publisher":
                        query = db(db.publisher.name == str(element.tag.text))
                        if query.isempty():
                           id = db.publisher.insert(name=element.tag.text)
                           epub["publisher"] = id
                        else:
                            publisher = query.select().first()
                            epub["publisher"] = publisher.id
                    elif element.tag.localname == "date":
                        if not epub["year"]:
                            epub["year"] = element.tag.text.split("-")[0]
                        else:
                            epub["year_update"] =  element.tag.text.split("-")[0]
                return epub

            else:
                return {'size': size, 'unit': unit, 'mime_type': self.mimeType, 'pages':0, 'title': "", 'author': "", 'year': "", 'year_update': "", 'keyword': ""}
        except Exception, e:
            return {'size': size, 'unit': unit, 'mime_type': self.mimeType, 'pages':0, 'title': "", 'author': "", 'year': "", 'year_update': "", 'keyword': ""}

    def imageCreate(self, coverpage_path_full, path_coverpage):
        """
        Take image from pdf, png or epub files
        """
        if not os.path.exists(path_coverpage):
            os.makedirs(path_coverpage)
        if os.path.exists(self.resource_path) and not os.path.exists(coverpage_path_full):

            if ((self.mimeType == "pdf") or (self.mimeType == "png")):
                 with Image(filename = self.resource_path+'[0]') as img:
                    img.format = CONST_IMAGE_FORMAT
                    img.resize(CONST_IMAGE_WIDTH, CONST_IMAGE_HEIGTH)
                    img.save(filename = coverpage_path_full)

            elif self.mimeType == "epub+zip":

                self.epub_info = Epub.from_file(self.resource_path)

                # Find the best implementation available on this platform
                try:
                    from cStringIO import StringIO
                except:
                    from StringIO import StringIO

                # Initialize a read buffer
                cover = StringIO(self.epub_info.cover.get_file())
                with Image(file=cover) as img:
                    img.format = CONST_IMAGE_FORMAT
                    img.resize(CONST_IMAGE_WIDTH, CONST_IMAGE_HEIGTH)
                    img.save(filename = coverpage_path_full)

        return True

    def coverpage(self):
        try:
            if not os.path.exists(self.coverpag_path['full_path']):
                self.imageCreate(self.coverpag_path['full_path'], self.coverpag_path['path'])
            return {'coverpag': self.coverpag}
        except Exception, e:
            return {'coverpag': self.coverpag}
