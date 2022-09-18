#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from operator import or_
from typing import final
import dateutil.parser
import logging
import babel
import sys

from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from logging import Formatter, FileHandler
from datetime import datetime, date, timedelta
from flask_wtf import FlaskForm
from wtforms import validators
from sqlalchemy import func
from sqlalchemy import or_

from forms import *
from models import *



#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#




app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
migrate = Migrate(app, db)
db.init_app(app)
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database




#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
    date = dateutil.parser.parse(value)
  else:
    date = value

  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
# TODO: replace with real venues data.
#       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
# Retrieve data from the venues table
# ==============================CODE BLOCK ================


  now = datetime.now()
  today = now.strftime('%Y-%m-%d %H:%M:%S')

  sub = db.session.query(Show.venue_id, db.func.count(Show.start_time > today).label('show_count')).group_by(Show.venue_id).subquery()

  venue_details = db.session.query(Venue.name,Venue.city,Venue.state,sub).select_from(Venue).join(sub).all()





  data = []
  for v in venue_details:
    venue = {'id': v.venue_id, 'name': v.name, 'upcoming': v.show_count}
    city = v.city
    state = v.state
   

    if data == [] or city not in data:
      data.append({'city':city, 'state':state, 'venues': [venue]})
    else:
      for d in data:
        if d['city'] == city and d['state'] == state:
          d['venues'].append(venue)

  return render_template('pages/venues.html', areas=data);



# ===============================CODE BLOCK===============


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term')
  get_venues = db.session.query(Venue).filter(or_(Venue.name.ilike(f'%{search_term}%'), Venue.city.ilike(f'%{search_term}%'), Venue.state.ilike(f'%{search_term}%'))).all()


  venue_data = []
  for get_venue in get_venues:
    # if search_term in get_venues_name:

    now = datetime.now()
    today = now.strftime('%Y-%m-%d %H:%M:%S')

    num_upcoming_shows = db.session.query(Show).filter_by(venue_id=get_venue.id).filter(Show.start_time > today).count()

    venue_data.append({
      'id': get_venue.id,
      'name': get_venue.name,
      'num_upcoming_shows': num_upcoming_shows
    })

  response = {
    'count': len(venue_data),
    'data': venue_data
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  # ==================CODE BLOCK================

  venue_details = db.session.query(Venue).filter(Venue.id==venue_id).all()

  now = datetime.now()
  today = now.strftime('%Y-%m-%d %H:%M:%S')


  upcoming_shows = []
  upcoming_shows_all = db.session.query(Show, Artist).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time > today).all()
    
  upcoming_shows_count = db.session.query(Show).filter_by(venue_id=venue_id).filter(Show.start_time > today).count()

  for u in upcoming_shows_all:
    upcoming_shows.append({
      'artist_id': u[1].id,
      'artist_name': u[1].name,
      'artist_image_link': u[1].image_link,
      'start_time': u[0].start_time
    })



  past_shows = []

  past_shows_all = db.session.query(Show, Artist).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time < today).all()

  past_shows_count = db.session.query(Show).filter_by(venue_id=venue_id).filter(Show.start_time < today).count()

  for p in past_shows_all:
    past_shows.append({
      'artist_id': p[1].id,
      'artist_name': p[1].name,
      'artist_image_link': p[1].image_link,
      'start_time': p[0].start_time
    })


  data = {
      'id': venue_details[0].id,
      'name': venue_details[0].name,
      'genres': venue_details[0].genres,
      'address': venue_details[0].address,
      'city': venue_details[0].city,
      'state': venue_details[0].state,
      'phone': venue_details[0].phone,
      'website': venue_details[0].website_link,
      'facebook_link': venue_details[0].facebook_link,
      'seeking_talent': venue_details[0].seeking_talent,
      'seeking_description': venue_details[0].seeking_description,
      'image_link': venue_details[0].image_link,
      'past_shows': past_shows,
      'upcoming_shows': upcoming_shows,
      'past_shows_count': past_shows_count,
      'upcoming_shows_count': upcoming_shows_count
  }
 
  data = list(filter(lambda d: d['id'] == venue_id, [data]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm()
  error = False

  try:
    name = form.name.data
    city = form.city.data 
    state = form.state.data
    address = form.address.data
    phone = form.phone.data
    genres = request.form.getlist('genres')
    facebook_link = form.facebook_link.data
    image_link = form.image_link.data
    website_link = form.website_link.data
    seeking_talent = form.seeking_talent.data
    seeking_description = form.seeking_description.data

    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, image_link=image_link, facebook_link=facebook_link, genres=genres, website_link=website_link, seeking_talent=seeking_talent, seeking_description=seeking_description)

    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue: ' + form.name.data + ' could not be listed.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter_by(id=venue_id).delete()
    
    db.session.commit()

  except:
    db.session.rollback()

  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  data = Artist.query.with_entities(Artist.id, Artist.name).all()


  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term')
  get_artists = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
  now = datetime.now()
  today = now.strftime('%Y-%m-%d %H:%M:%S')
  
  artist_data = []
  
  for get_artist in get_artists:
    now = datetime.now()
    today = now.strftime('%Y-%m-%d %H:%M:%S')

    num_upcoming_shows = db.session.query(Show).filter_by(artist_id=get_artist.id).filter(Show.start_time > today).count()
    
    artist_data.append({
      'id':get_artist.id,
      'name':get_artist.name,
      'num_upcoming_shows': num_upcoming_shows
    })

  response = {
    'count':len(artist_data),
    'data': artist_data
  }


  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist_details = db.session.query(Artist).filter(Artist.id==artist_id).all()

  now = datetime.now()
  today = now.strftime('%Y-%m-%d %H:%M:%S')


  upcoming_shows = []
  upcoming_shows_all = db.session.query(Show, Venue).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time > today).all()
    
  upcoming_shows_count = db.session.query(Show).filter_by(artist_id=artist_id).filter(Show.start_time > today).count()

  for u in upcoming_shows_all:
    upcoming_shows.append({
      'venue_id': u[1].id,
      'venue_name': u[1].name,
      'venue_image_link': u[1].image_link,
      'start_time': u[0].start_time
    })



  past_shows = []

  past_shows_all = db.session.query(Show, Venue).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time < today).all()

  past_shows_count = db.session.query(Show).filter_by(artist_id=artist_id).filter(Show.start_time < today).count()

  for p in past_shows_all:
    past_shows.append({
      'venue_id': p[1].id,
      'venue_name': p[1].name,
      'venue_image_link': p[1].image_link,
      'start_time': p[0].start_time
    })


  data = {
      'id': artist_details[0].id,
      'name': artist_details[0].name,
      'genres': artist_details[0].genres,
      'city': artist_details[0].city,
      'state': artist_details[0].state,
      'phone': artist_details[0].phone,
      'website': artist_details[0].website_link,
      'facebook_link': artist_details[0].facebook_link,
      'seeking_venue': artist_details[0].seeking_venue,
      'seeking_description': artist_details[0].seeking_description,
      'image_link': artist_details[0].image_link,
      'past_shows': past_shows,
      'upcoming_shows': upcoming_shows,
      'past_shows_count': past_shows_count,
      'upcoming_shows_count': upcoming_shows_count
  }
 
  data = list(filter(lambda d: d['id'] == artist_id, [data]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  artist = db.session.query(Artist).filter_by(id=artist_id).all()

  # # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
# =============CODE BLOCK  ==============
  form = ArtistForm()
  try:
    artist = Artist.query.get(artist_id)

    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = form.facebook_link.data
    artist.image_link = form.image_link.data
    artist.website_link = form.website_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data

    db.session.commit()
    flash('Artist Updated Successfully')
  except:
    db.session.rollback()
  finally:
    db.session.close()
    


  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = db.session.query(Venue).filter_by(id=venue_id).all()

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm
  try:  
    venue = Venue.query.get(venue_id)

    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = form.facebook_link.data
    venue.image_link = form.image_link.data
    venue.website_link = form.website_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data

    db.session.commit()
    flash('Venue Updated Successfully')
  except:
    db.session.rollback()
  finally:
    db.session.close()
  
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm()
  error = False
  
  try:
    name = form.name.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data
    genres = request.form.getlist('genres')
    facebook_link = form.facebook_link.data
    image_link = form.image_link.data
    website_link = form.website_link.data
    seeking_venue = form.seeking_venue.data
    seeking_description = form.seeking_description.data

    artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link,website_link=website_link, seeking_venue=seeking_venue, seeking_description=seeking_description)

    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + request.form['name']+ ' could not be listed.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.

  show_details = db.session.query(Show.venue_id, Venue.name, Show.artist_id, Artist.name.label('artistname'), Artist.image_link, Show.start_time).select_from(Venue).join(Show).join(Artist).all()

  data = []
  for d in show_details:
    data.append({
      'venue_id': d.venue_id,
      'venue_name': d.name,
      'artist_id': d.artist_id,
      'artist_name': d.artistname,
      'artist_image_link': d.image_link,
      'start_time': d.start_time
    })
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm()
  error = False
  try:

    venue_id = form.venue_id.data
    artist_id = form.artist_id.data
    start_time = form.start_time.data

    show = Show(venue_id=venue_id, artist_id=artist_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()

  if error:
    flash('An error occurred. Show could not be listed.')
  else:
    flash('Show was successfully listed!')
  return render_template('pages/home.html')
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
