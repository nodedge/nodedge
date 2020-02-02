.. _conventions-ref:

.. currentmodule:: nodedge

*******************
Library conventions
*******************

The nodedge library uses a set of standard conventions for the way
that different types of standard information used by the library.

LTI system representation
=========================

Linear time invariant (LTI) systems are represented in nodedge in
state space, transfer function, or frequency response data (FRD) form.  Most
functions in the toolbox will operate on any of these data types and
functions for converting between compatible types is provided.

State space systems
-------------------
.. math::

  \frac{dx}{dt} &= A x + B u \\
  y &= C x + D u

where u is the input, y is the output, and x is the state.

Transfer functions
------------------

.. math::

  G(s) = \frac{\text{num}(s)}{\text{den}(s)}
       = \frac{a_0 s^m + a_1 s^{m-1} + \cdots + a_m}
              {b_0 s^n + b_1 s^{n-1} + \cdots + b_n},

where n is generally greater than or equal to m (for a proper transfer
function).
