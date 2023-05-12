Simple Django frontend deployed to AWS Elastic Beanstalk, for creating and managing feeds of "reruns" (rebroadcasted entries from existing RSS and Atom feeds).

The basic motivation for this project is to have old entries from various feeds intermittently show up in my feed reader, like this:

![Screenshot from Feedly](https://github.com/hannahlog/reruns-django-site/blob/main/screenshots/as_seen_in_feedly.png?raw=True)

The actual processing of RSS and Atom feed files is handled by [rss-reruns](https://github.com/hannahlog/rss-reruns), while this project hosts and stores generated feeds; schedules feed updates as periodic tasks; and provides a simple interface for multiple users to create and manage feeds of reruns.

(For my own personal use, I *could* have just used a persistent scheduler on my own laptop (or on a single EC2 instance) to periodically process the feeds and upload the updated files to S3. Instead, I used this project as an excuse to try Django and experience more of the AWS ecosystem.)

## Brief technical details

* Django application on Elastic Beanstalk, backed by an AWS PostgreSQL database

* Feed updates are carried out as [Celery](https://docs.celeryq.dev/en/stable/index.html) tasks, with scheduling of feed updates through [Celery Beat](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html); each feed has a corresponding Periodic Task model instance, stored in the database through Django's ORM

* Redis message broker for communication between Celery workers and Celery Beat

* Celery workers and Celery Beat are daemonized through supervisord

* User-supplied feed files and the resulting generated feeds are hosted on Amazon S3 (the project's MEDIA storage backend)

* The site's few static assets are stored separately on S3

## Miscellaneous details

* Each RerunsFeed has two FeedFiles: a full version of the XML file with `reruns` metadata included (e.g. elements indicating whether an entry has been rebroadcasted yet), and a condensed version, with all `reruns` elements stripped, and containing only the recently-rebroadcasted entries. The former is for this project's own internal use, while the latter is for feed readers to check for updates.

* When creating a RerunsFeed, the original feed can be given by either a URL or a file upload.

* The schedule for a feed's updates currently only accepts interval schedules given as a (positive) integer number of Minutes, Hours, or Days. [(Crontab Schedules are planned to be allowed in future.)](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html#crontab-schedules)

* A feed's update schedule can be edited at any time.

* Each user has a timezone setting they can adjust at any time (via a custom User model with a timezone field). When logged in, all datetimes on the site are displayed in the user's specified timezone

* When newly creating a feed _or_ when changing a feed's update schedule, an initial datetime must be supplied for when to begin the schedule. A custom multiwidget allows manually specifying any timezone along with the date and time, but the form will be initialized with the user's own timezone setting

* Open registration is currently not enabled because I don't want to potentially deal with bots trying to register (though I do have invitations enabled.) Since the forms are not visible without being logged in, here are a few example screenshots:

| Screenshot | Caption |
| ------------- | ------------- |
| !['Add Feed' form, with various fields](https://github.com/hannahlog/reruns-django-site/blob/main/screenshots/add_feed.png?raw=True) |  Adding a feed, giving the starting datetime in `UTC`. |
| !['Edit Feed' form](https://github.com/hannahlog/reruns-django-site/blob/main/screenshots/edit_feed.png?raw=True)  | Editing the feed once I've changed my user timezone to `US/Eastern`—the form is initialized with the prior datetime setting, but converted to `US/Eastern`.  |

(These forms admittedly aren't pretty, but they are ergonomic enough for my purposes.)
