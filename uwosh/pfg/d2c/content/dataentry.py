"""Implements a data content entry type for use by the save data adapter.
"""

from AccessControl import ClassSecurityInfo
from AccessControl.SecurityManagement import newSecurityManager, getSecurityManager, setSecurityManager

from Products.ATContentTypes.content.base import registerATCT
from uwosh.pfg.d2c.config import PROJECTNAME
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from uwosh.pfg.d2c.interfaces import IFormSaveData2ContentEntry
from zope.interface import implements

from Products.CMFCore.Expression import getExprContext

FormSaveData2ContentEntrySchema = ATContentTypeSchema.copy()
FormSaveData2ContentEntrySchema.delField('title')
FormSaveData2ContentEntrySchema.delField('description')

class FormSaveData2ContentEntry(ATCTContent):
    "Multi-purpose content type used by the save data adapter to store form submissions"

    implements(IFormSaveData2ContentEntry)
    
    schema = FormSaveData2ContentEntrySchema

    meta_type = portal_type = 'FormSaveData2ContentEntry'
    archetype_name = 'Save Data to Content Entry'
    
    security       = ClassSecurityInfo()

    security.declareProtected('View', 'Title')    
    def Title(self):
        "generate custom title from the selected form field or the given TALES expression override"
        
        # If there's a TALES expression:
        if self.getParentNode().getRawDynamicTitle():
        
            # TALES expr evaluation may require permissions an anonymous user does not have.
            # So we set up a new security manager and pose as an Owner.
            old_security_manager = getSecurityManager()
            user = self.getWrappedOwner()
            newSecurityManager(None, user)

            # Try evaluating it
            exprcontext = getExprContext(self,self)
            try:        
                value = self.getParentNode().getDynamicTitle(expression_context=exprcontext)
                setSecurityManager(old_security_manager)
                return value
            except Exception, e:
                # make sure original security manager is reinstated.
                setSecurityManager(old_security_manager)
                raise            

        # Ok. No override, resort to using a selected field
        field = self.getParentNode().getTitleField()
        schema = self.Schema()
        if schema.has_key(field):
            value = schema.get(field).get(self)
            try:
                if not isinstance(value, basestring):
                    # not of string type so convert it
                    # This may not always work but might prevent some errors.
                    value = str(value)
            except:
                pass
            
            return value
        else:
            return self.getId()
        
    security.declareProtected('View', 'getValue')
    def getValue(self, field):
        """
        somewhat a replacement for the get generated methods.
        """
        schema = self.Schema()
        field = schema.get(field)
        return field.get(self)
        
    
registerATCT(FormSaveData2ContentEntry, PROJECTNAME)
