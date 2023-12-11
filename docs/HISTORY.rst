Changelog
=========

2.0.2
-----
 - added mising interfaces attributes

2.0.1
-----
 - updated Buildout configuration

2.0.0
-----
 - migrated to Pyramid 2.0

1.8.1
-----
 - small templates updates

1.8.0
-----
 - added support for optional *factory* argument when using *form_and_handler* decorator
 - added optional *notify* argument to form *extract_data* method; you can set this argument
   to *False* when you don't want to generate extra events on a manual data extraction

1.7.4
-----
 - reverted doctest

1.7.3
-----
 - added support for Python 3.10 and 3.11
 - updated doctests

1.7.2
-----
 - cancelled doctest update

1.7.1
-----
 - updated get_forms method to only get inner forms which are really implementing inner forms
   interfaces; this can be useful to include inner viewlets which are not forms into a parent
   form

1.7.0
-----
 - added interfaces support for form content and form fields adapters
 - added form update events
 - added support for Python 3.10

1.6.5
-----
 - cancelled doctest update

1.6.4
-----
 - small updates in default AJAX form renderer
 - reified form edit permission getter

1.6.3
-----
 - changed test in AJAX add form to check changes against *None* instead of boolean *false*
   value to handle use case where created object is an empty container

1.6.2
-----
 - updated doctests for *zope.schema* package >= 6.1.1, where boolean schema fields are
   automatically set as required

1.6.1
-----
 - updated doctests

1.6.0
-----
 - added optional *ajax_require_csrf* argument to *ajax_form_config* decorator

1.5.0
-----
 - updated sequence widget behaviour to be able to extract data from single
   value using a separator
 - updated default AJAX renderer to merge outputs of inner forms renderers

1.4.3
-----
 - version mismatch

1.4.2
-----
 - added missing "context" argument to permission check
 - added missing widget factory for text lines list field
 - removed unused interface

1.4.1
-----
 - Gitlab-CI pylint test update

1.4.0
-----
 - removed support for Python < 3.7
 - updated Bytes schema field to FileWidget data converter

1.3.1
-----
 - updated Gitlab-CI configuration

1.3.0
-----
 - look for actions in finished state to get AJAX renderers
 - updated Gitlab-CI configuration
 - removed Travis-CI configuration

1.2.1
-----
 - interfaces description updates
 - code cleanup

1.2.0
-----
 - added support for inner sub-forms and tab-forms in groups manager

1.1.0
-----
 - small updates in forms API
 - use form's "finished_state" attribute to store executed action and changes
 - automatically use objects factories in add forms
 - updated "adapter_config" decorator arguments names
 - updated access to Pyramid's global registry
 - updated doctests

1.0.4
-----
 - included edge case fix to handle missing values which are not None but that work as None
   (merged from z3c.form)

1.0.3
-----
 - updated doctests using ZCA hook

1.0.2
-----
 - code refactoring to reduce duplications

1.0.1
-----
 - updated doctests

1.0.0
-----
 - initial release
