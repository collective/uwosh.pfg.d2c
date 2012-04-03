Introduction
============

uwosh.pfg.(d)ata(2)(c)ontent

This product provides a dynamic content type to store PloneFormGen form
data into. It leverages schemaextenders ability to dynamically add extra
fields on a content type so that you essentially get a persistent copy of
your form.

The product adds a "Save Data to Content Adapter" item to the "Add
new.." drop down for the PloneFormGen Form. Once enabled, when a user
submits a form, a new content item is created with that data and
located in the adapter.


Saving Content
--------------
Upon save data adapter creation, user can choose to use any content type
that has 'uwosh.pfg.d2c' configured as the 'product' in the FTI, to store
the form submission. 

So besides the original FormSaveData2ContentEntry, its clone types can
also be used to store form data - whether added to types tool via code,
genericsetup profile or by manually copying the FormSaveData2ContentEntry
FTI in portal_types tool (and then renaming it appropriately).

The type names can be translated simply by adding them to
plone.po in the language-specific locale/LC_MESSAGES subdirectory.


Upgrading to 2.0
----------------

You must run the upgrade step in the add/remove product control panel
in order for you to successfully upgrade to 2.0 otherwise, your
data adapter will not display it's contents properly.


Warning
-------

Don't forget to enable the adapter after it is added to the form!


Placeful Workflows
------------------

It is often very useful to assign a placeful workflow onto a 
save data content type. Normally, this is rather cumbersome to
do; however, d2c now provides a nice widget to make this sort
of action automatic(automatically create missing workflow policy).


Compatibility
-------------

Compatible with versions of PloneFormGen >= 1.2.2 and Plone 3.x ->
4.x.

Version 1.0 derives the new D2C saved data adapter from the BTree
folder class.  This allows Plone 3.x sites to handle larger numbers of
content items inside the D2C objects.  There is an upgrade step that
allows pre-1.0 D2C objects to get migrated to BTree storage.  Version
1.0 also works with Plone 4.  However, if you have a Plone 3.x site
that uses pre-1.0 D2C and you upgrade to Plone 4 and only then upgrade
to 1.0+ D2C, the upgrade step that migrates D2C storage to BTree
storage may not work.  We recommend that you first upgrade to 1.0+ D2C
*then* upgrade to Plone 4.


D2C Form Images
---------------

Since D2C 2.1, there has been the ability for PFG file fields to behave
like plone image fields with scales. Just select the 'Is Image' checkbox
in the PFG file field settings.

To access scales for an image, you must construct a url like::

    http://site.com/path/to/object/image_fieldid_scalename

Example::

    http://site.com/path/to/object/image_myimage_large

or for original

    http://site.com/path/to/object/image_myimage


Upgrade old should-be d2c images
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, make sure you select that the field is an image in the corresponding
ploneformgen form.

Then, go to the zmi, portal_setup, upgrades tab, select `uwosh.pfg.d2c:default`,
click to show old and select the image-scales upgrade to run.


Windows
~~~~~~~

In order for this to work, you'll need to disable the schemaextender cache::

  archetypes.schemaextender\archetypes\schemaextender\extender.py line 113
  disable CACHE_ENABLED
  

Finding created d2c object on request
-------------------------------------
Sometimes you need to know what object you just created was to
redirect or perhaps do extra processing. D2C sets values on the request
environ so you can get that information::

    REQUEST.environ['d2c-obj-created-url']
    REQUEST.environ['d2c-obj-created-uid']


Content object methods
----------------------

getValue(fieldid, default=None)
    get the value of a field
setValue(fieldid, value)
    set the value for a field
getForm()
    get connected pfg form
getFormAdapter()
    get connected pfg content adapter
