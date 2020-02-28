```eval_rst
.. _coding-standards:
```
# Coding Standards

These following rules and guidelines are used through the nodeeditor package:
* methods named ```doXY``` usually *do* certain tas and also take care off low level operations
* classes always contain methods in this order:
    * ```__init__```
    * python magic methods (i.e. ```__str__```), setters and getters 
    * ```initXY``` functions
    * listener functions
    * nodedge event functions
    * nodedge ```doXY``` and ```getXY``` helping functions 
    * Qt5 event functions
    * python magic methods (i.e. ```__str__```), setters and getters 
    * other functions
    * optionally overridden Qt ```paint``` method
    * ```serialize``` and ```deserialize``` methods at the end  
