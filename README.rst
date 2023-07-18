Track Generator
===============

Simple generator to create tracks (ground textures for vehicle simulations)
from a parametric description (XML).

For example, the following parametric description of a track in XML will lead
to the corresponding result:

**Track definition file (XML):**

.. literalinclude:: examples/track_files/reference_track_example.xml
   :language: XML
   :encoding: UTF-8
   :linenos:

**Output (SVG, optional PNG):**

![track output example](doc/source/_static/img/svg/reference_track_example.svg)

Installation
============

    pip install track-generator

Usage
=====

Generate track
--------------

    track_generator generate_track <TRACK_DEFINITION_FILE>

Generate track live
--------------

    track_generator generate_track_live <TRACK_DEFINITION_FILE>

Examples
========

TODO

Documentation
=============

TODO