Changelog for Cassette
======================

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
