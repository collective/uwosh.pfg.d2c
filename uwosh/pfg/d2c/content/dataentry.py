from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.ATContentTypes.content.base import registerATCT
from uwosh.pfg.d2c.config import PROJECTNAME
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from uwosh.pfg.d2c.interfaces import IFormSaveData2ContentEntry
from zope.interface import implements


class FormSaveData2ContentEntry(ATCTContent):
    implements(IFormSaveData2ContentEntry)
    
    schema = ATContentTypeSchema.copy()

    meta_type = portal_type = 'FormSaveData2ContentEntry'
    archetype_name = 'Save Data to Content Entry'
    
    security       = ClassSecurityInfo()

    
registerATCT(FormSaveData2ContentEntry, PROJECTNAME)
