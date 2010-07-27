Introduction
============

uwosh.pfg.(d)ata(2)(c)ontent

This product provides a dynamic content type to store PloneFormGen form
data into. It leverages schemaextenders ability to dynamically add extra
fields on a content type so that you essentially get a persistent copy of
your form.

The product adds a "Save Data to Content Adapter" item to the "Add new.." drop
down for the PloneFormGen Form. Once enabled, when a user submits a form,
a new content item is created with that data and located in the adapter.