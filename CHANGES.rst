Changelog for Cassette
======================

0.3.8 (2015-04-03)
------------------

- Add compatibility with Python 2.7.9

0.3.7 (2015-03-12)
------------------

- Add ability to report on unused cassette.

0.3.6 (2014-10-31)
------------------

- Fix NameError when using UL3CassetteHTTPConnection (thanks to @carolinevdh)
- Fix HTTP Response to use cStringIO, adding Unicode support (thanks to
  @carolinevdh)

0.3.5 (2014-08-28)
------------------

- Fix error closing HTTPConnections directly

0.3.4 (2014-08-27)
------------------

- Improve backward compatibility with 0.3.2

0.3.3 (2014-08-27)
------------------

- Added support for `requests`. Note that libraries are not neccessarily
  cross compatible-requests cached with `urllib2` may not work with `requests`
  and vice versa.

0.3.2 (2014-06-26)
------------------

- Handle absent headers with httplib (thanks to @blampe)

0.3.1 (2014-06-04)
------------------

- Add the ability to read from a directory instead of from a single file
  (thanks to @anthonysutardja)

0.3 (2014-03-18)
----------------

- Respect request headers in cassette name. Requires regenerating cassette
  files.

0.2 (2013-05-14)
----------------

- Get rid of urlopen mocking, mock only at ``httplib`` level to circumvent
  the problem with urlopen raising exceptions when getting non-2XX codes
- Clean up the docs, streamline their structure
- **This is a backward incompatible release**, you'll need to delete your
  YAML file.

0.1.13 (2013-05-13)
-------------------

- Fix binary file downloading (thanks to @twolfson)

0.1.12 (2013-04-26)
-------------------

- Add performance tests (courtesy of @twolfson)
- Cache the loaded file content to achieve significant performance improvements
  (thanks to @twolfson)

0.1.11 (2013-04-11)
-------------------

- Lazily load YAML file

0.1.11 (2013-04-11)
-------------------

- Started tracking changes
