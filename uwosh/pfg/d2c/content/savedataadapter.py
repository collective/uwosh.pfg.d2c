from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import *
from Products.ATContentTypes.content.base import registerATCT
from Products.PloneFormGen.content.actionAdapter import FormActionAdapter, FormAdapterSchema
from uwosh.pfg.d2c.config import PROJECTNAME
from Products.ATContentTypes.content.folder import ATFolderSchema, ATFolder
from uwosh.pfg.d2c.interfaces import IFormSaveData2ContentAdapter
from zope.interface import implements
from Products.Archetypes.Field import FileField

class FormSaveData2ContentAdapter(ATFolder, FormActionAdapter):
    """A form action adapter that will save form input data and 
       return it in csv- or tab-delimited format."""

    implements(IFormSaveData2ContentAdapter)
    schema = ATFolderSchema.copy() + FormAdapterSchema.copy()

    meta_type = portal_type = 'FormSaveData2ContentAdapter'
    archetype_name = 'Save Data to Content Adapter'

    security       = ClassSecurityInfo()
    
    def onSuccess(self, fields, REQUEST=None, loopstop=False):
        """
        magic done here...
        """
        
        id = self.invokeFactory("FormSaveData2ContentEntry", self.generateUniqueId())
        obj = self[id]
        
        for field in self.fgFields():
            name = field.getName()
            if isinstance(field, FileField):
                name += '_file'
            field.set(obj, REQUEST.form.get(name))
        
        
registerATCT(FormSaveData2ContentAdapter, PROJECTNAME)
