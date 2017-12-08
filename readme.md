# CS6460 Project Layout

## api
This directory contains the actual backend service. This is a Flask application
written in Python 3.6. It uses PeeWee ORM for managing the database and relational models.
TextBlob is used for NLP. Everything else is hand-rolled for speed and simplicity.

The layout is fairly straight forward. The entry point is standard for Flask apps and is 
location in app.py. This file sets up the database connection and defines all of our routes.
Had this been a larger backend, the routes would have been segregated but I kept
the routine simple by only exposing three REST endpoints.

The resources package contains all of the data models that are managed by the ORM. 

- Courses: Maps course name to Piazza id. The ID is what you see in the URL, also called 
the network id. The id for CS6460 is j6azklk4gaf4v9.
- Stats: Holds all the statistics for a student's online engagement. As you can see,
there is nothing directly identifying students and most of the content is simply
calculated or aggregate in nature.
- Scrape: This module performs the important task of actually scraping the data from
Piazza and processing into into a Stats model. The PiazzaPost model is an intermediate
form that is used for passing structure data between the parser and the NLP processor.
-User: Maps a user to their authentication secret and the courses that they are enrolled in.
This too is light on identifiable data and only stores the Piazza student ID and a
random secret that has no derivation from the user identity.

The common lib holds all the modules that are not specific to web requests. This
includes the low-level database, datetime handlers, and of course the NLP. The NLP
modules does most of the interesting calculations. The CSS gradient stuff is all
handled in the util module.

Overall, I'm very proud of this module. It is well tested and well documented. There
will of course be things I'd like to refactor but those are more stylistic changes
that fundamental transgressions.

## api_test
This is the unit test suite in which we achieved 91% code coverage. Emphasis was
placed on accuracy of the date methods and Piazza content extraction as these are
critical components. The actual Piazza scraping is not tested as that is a 3rd
party library. I've mocked this service out were appropriate to facilitate regression
testing. Also, because I'm nice person I've built in a random throttle so this service
does not knock Piazza over during our scrape sessions.

Unit testing uses the Python unittest package and there isn't much more to it.

## chrome
