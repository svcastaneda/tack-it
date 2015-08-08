from datastore import Note, Image
from google.appengine.api import users
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import blobstore
from google.appengine.api.images import get_serving_url
from google.appengine.ext import ndb
import logging
import jinja2
import os 
import webapp2
import cgi

jinja_environment = jinja2.Environment(loader=
    jinja2.FileSystemLoader(os.path.dirname(__file__)))


##### MAKE SURE WE ADD COMMENTS EVERYWHERE. k, thanks :D :D:D:D:D

#photoupload

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    logging.info("hi")
    upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
    blob_info = upload_files[0]
    userID = users.get_current_user().user_id()
    
    image = Image(parent = ndb.Key('image', userID), blobKey=blob_info.key(), urlString = get_serving_url(blob_info.key(), size=None, crop=False, secure_url=None))
    image.put()
    self.redirect('/my-dashboard')

# class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
#   def get(self, resource):
#     resource = str(urllib.unquote(resource))
#     blob_info = blobstore.BlobInfo.get(resource)
#     self.send_blob(blob_info)

class MainHandler(webapp2.RequestHandler): #handler for the homepage, use file home.html as file 
  def get(self):
    template_values = {}
    template_values['current_user'] = users.get_current_user()
    template_values['loginURL'] = users.create_login_url(dest_url='my-dashboard')
    template = jinja_environment.get_template('home.html')
    self.response.out.write(template.render(template_values))

class ExtrasHandler(webapp2.RequestHandler):
	def get(self):
	  template_values = {}
	  current_user = users.get_current_user()
	  if current_user == None:					# returns to homepage if no user logged in
	    template_values['loginURL'] = users.create_login_url(dest_url='my-dashboard')
	    template = jinja_environment.get_template('home.html')
	    self.response.out.write(template.render(template_values))
	  else:
	    template_values['name'] = users.get_current_user().nickname()
	    template_values['logout'] = users.create_logout_url('/')
	    template = jinja_environment.get_template('extra.html')
	    self.response.out.write(template.render(template_values))


# Adds a new note
class NewNoteHandler(webapp2.RequestHandler): 
   def get(self):
      template_values = {}
      
      current_user = users.get_current_user()
      logout = users.create_logout_url('/')
      name = users.get_current_user().nickname()
      
      title = self.request.get('title')
      content = self.request.get('content')
      
      upload_url = blobstore.create_upload_url('/upload')
      #direct to my dashboard
      
      #note = Note(title=title, content=content)
      #note.put()
      
      template_values = {
       'title': title,
       'content': content,
       'name' : name,
       'logout' : logout,
       'current_user' : current_user,
       'upload_url' : upload_url
      }
    
      template = jinja_environment.get_template('newtack.html')
      self.response.out.write(template.render(template_values))
      #self.redirect("/my-dashboard")
      

      
class AddNewNote(webapp2.RequestHandler): 
   def post(self):
       title = cgi.escape(self.request.get('title'))
       content = cgi.escape(self.request.get('content'))
       
       userID = users.get_current_user().user_id()
       
       note = Note(parent = ndb.Key('note',userID), title=title, content=content)
       note.put()
       
       self.redirect("/my-dashboard")
      
class DeleteHandler(webapp2.RequestHandler): 
  def get(self): 
      
      userID = users.get_current_user().user_id()
      
      note_id = int(self.request.get('id'))
      ndb.Key('note',userID,'Note',note_id).delete()
      
      self.redirect("/my-dashboard")
      
class DeleteImageHandler(webapp2.RequestHandler):
  def get(self):

      userID = users.get_current_user().user_id()

      image_id = int(self.request.get('id'))
      ndb.Key('image',userID,'Image',image_id).delete()

      self.redirect("/my-dashboard")
            
class DashboardHandler(webapp2.RequestHandler):
  def get(self):
    template_values = {}
    
    current_user = users.get_current_user()
    if current_user == None:					# returns to homepage if no user logged in
      template_values['loginURL'] = users.create_login_url(dest_url='my-dashboard')
      template = jinja_environment.get_template('home.html')
      self.response.out.write(template.render(template_values))
    else:
      name = users.get_current_user()
      logout = users.create_logout_url('/')
      userID = users.get_current_user().user_id()

      notes = Note.query(ancestor=ndb.Key('note', userID)).fetch()
      images = Image.query(ancestor=ndb.Key('image', userID)).fetch()
      
      # allURLs = []
      # for image in images:
      #     url = get_serving_url(image.blobKey, size=None, crop=False, secure_url=None)
      #     allURLs.append(url)
            
      template_values = {
       'notes': notes,
       'name' : name, 
       'current_user': current_user,
       'logout' : logout,
       'images' : images
      }
      
      template = jinja_environment.get_template('my-dashboard.html')
      self.response.out.write(template.render(template_values))
    
class DevPageHandler(webapp2.RequestHandler):
	def get(self):
	  template_values = {}
	  logout = users.create_logout_url('/')
	  template_values['logout'] = users.create_logout_url('/')
	  template = jinja_environment.get_template('developers.html')
	  self.response.out.write(template.render(template_values))
	        
routes = [

('/extra', ExtrasHandler),
('/my-dashboard', DashboardHandler),
('/newtack', NewNoteHandler),
('/addNote', AddNewNote),
('/delete', DeleteHandler),
('/deleteImage', DeleteImageHandler),
('/upload', UploadHandler),
('/', MainHandler),
('/developers', DevPageHandler),
]


app = webapp2.WSGIApplication(routes, debug=True) 