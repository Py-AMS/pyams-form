==================
PyAMS_form package
==================

.. contents::


What is PyAMS?
==============

PyAMS (Pyramid Application Management Suite) is a small suite of packages written for applications
and content management with the Pyramid framework.

**PyAMS** is actually mainly used to manage web sites through content management applications (CMS,
see PyAMS_content package), but many features are generic and can be used inside any kind of web
application.

All PyAMS documentation is available on `ReadTheDocs <https://pyams.readthedocs.io>`_; source code
is available on `Gitlab <https://gitlab.com/pyams>`_ and pushed to `Github
<https://github.com/py-ams>`_. Complete doctests are available in the *doctests* folder.


What is PyAMS_form?
===================

PyAMS_form is a fork of `z3c.form <https///github.com/zopefoundation/z3c.form>`_ package;
it provides the same features to generate HTML forms based on schema interfaces, but adapted to
the Pyramid framework for use with Chameleon templates.

It is also adding a few features, with custom form-related viewlets managers and AJAX forms.

** Package API is also converted to common Python standards, using snake_case for variables and
methods.
