from datetime import datetime




from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
# shows = db.Table('shows', 
#   db.Column('venue_id', db.Integer, db.ForeignKey('venue.id')), 
#   db.Column('artist_id',  db.Integer, db.ForeignKey('artist.id')),
#   db.Column('start_time', db.DateTime, nullable=False))
class Show(db.Model):
  __tablename__ = 'show'
  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer,  db.ForeignKey('venue.id'))
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
  start_time = db.Column(db.DateTime, nullable=False)

  def __repr__(self):
    return f'<Show id : {self.id} artist_id : {self.artist_id} venue_id : {self.venue_id} start_time : {self.start_time}>'

class Venue(db.Model):
  __tablename__ = 'venue'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  genres = db.Column(db.ARRAY(db.String()))
  facebook_link = db.Column(db.String(120))
  website_link = db.Column(db.String(120))
  seeking_talent = db.Column(db.Boolean)
  seeking_description = db.Column(db.String(120))
  shows = db.relationship('Show', backref='venues', lazy='dynamic', cascade='all, delete-orphan')


  def __repr__(self):
    return f'<id: {self.id}, name: {self.name}, city:{self.city}, state: {self.state}, address: {self.address}, phone: {self.phone}, image_link: {self.image_link}, genres: {self.genres}, facebook_link: {self.facebook_link}, website_link: {self.website_link}, seeking_talent: {self.seeking_talent},  seeking_description: {self.seeking_description}'


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
  __tablename__ = 'artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  genres = db.Column(db.String(120))
  facebook_link = db.Column(db.String(120))
  website_link = db.Column(db.String(120))
  seeking_venue = db.Column(db.Boolean)
  seeking_description = db.Column(db.String(120))
  shows = db.relationship('Show', backref='artists', lazy='dynamic', cascade='all, delete-orphan')

  def __repr__(self):
    return f'<id: {self.id}, name: {self.name}, city:{self.city}, state: {self.state}, phone: {self.phone}, image_link: {self.image_link}, genres: {self.genres}, facebook_link: {self.facebook_link}, website_link: {self.website_link}, seeking_venue: {self.seeking_venue},  seeking_description: {self.seeking_description}'


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

