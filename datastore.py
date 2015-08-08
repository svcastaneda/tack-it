from google.appengine.ext import ndb
from google.appengine.ext import blobstore

# we need to link emails to Account kind in order to save data

class Account(ndb.Model):
  username = ndb.StringProperty()

class Tacs(ndb.Model):
  title = ndb.StringProperty()
  def delete(self):
      return '/delete?id=%s' % self.key.id()

class Note(ndb.Model):
  title = ndb.StringProperty()
  content = ndb.StringProperty()
  def delete(self):
      return '/delete?id=%s' % self.key.id()

class Image(ndb.Model):
  blobKey = ndb.PickleProperty()
  urlString = ndb.StringProperty()
  def deleteImage(self):
      return '/deleteImage?id=%s' % self.key.id()