.. ConfigValidator documentation master file, created by
   sphinx-quickstart on Fri Jul 10 23:06:45 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ConfigValidator's documentation!
===========================================


ConfigValidator is an python module to Validate ini File user input.
After validation you will get are well-defined python dict with the validated user inputs.

To achieve this, you will need an config dict, which is part of your source code. 
Furthermore you need an ini file, which is given to the program at runtime. 
This inputs to ConfigValidator will lead in an well-defined python dict, which can then be used in your program.


Features
--------

* Expandable with custom validators.

* Expandable with custom parsers for options.

* Expandable with custom parsers for sections.

* Validators may be used independently.


Installation
------------

You can install, upgrade, uninstall ConfigValidator with these commands::

  $ pip install configvalidator
  $ pip install --upgrade configvalidator
  $ pip uninstall configvalidator


Example usage
-------------

import ConfigValidator
::

  from configvalidator import ConfigValidator

Now you need to define the config dict for ConfigValidator.
::

  cp = ConfigParser()
  cp.read("user_input.ini")

  cv = ConfigValidator(cp=cp)
  data = cv.parse(config_dict=config_dict)

You can now use the data object like a normal python dict.

It contains all the validated user inputs as specified in the config dict.

For more examples, please open the example directory.
