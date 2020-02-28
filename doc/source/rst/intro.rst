************
Introduction
************

Welcome to the Nodedge User's Manual. This manual contains information
on using Nodedge software, including documentation for all
development modules in the package and examples illustrating their use.

Overview
========

Some differences from Simulink
==============================

Installation
============

`nodedge` package can be installed using pip or the
standard distutils/setuptools mechanisms.

To install using pip::

  pip install nodedge


Alternatively, to use setuptools, first `clone or download the source
<https://github.com/nodedge/nodedge>`_.
To install in your default python interpreter, use::

  git clone git@github.com:nodedge/nodedge.git
  cd nodedge
  python setup.py install --user

Getting started
===============

There are two different ways to use the package.  For the default interface, simply import the control package as follows::

    >>> import nodedge

