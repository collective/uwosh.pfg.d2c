from Products.CMFCore.utils import getToolByName
"""Implements a data content entry type for use by the save data adapter.
"""

from AccessControl import ClassSecurityInfo
from AccessControl.SecurityManagement import \
    newSecurityManager, getSecurityManager, setSecurityManager

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
    """
    Multi-purpose content type used by the
    save data adapter to store form submissions
    """

    implements(IFormSaveData2ContentEntry)

    schema = FormSaveData2ContentEntrySchema

    meta_type = portal_type = 'FormSaveData2ContentEntry'
    archetype_name = 'Save Data to Content Entry'

    security = ClassSecurityInfo()

    def getForm(self):
        adapter = self.getFormAdapter()
        if adapter is None:
            adapter = self.getParentNode()

        form = adapter.getParentNode()
        if getattr(form, 'portal_type', None) != 'FormFolder':
            form = None
        return form

    def getFormAdapter(self):
        uid = getattr(self, '_adapter_uid', None)
        if uid is None:
            return uid
        else:
            catalog = getToolByName(self, 'uid_catalog')
            res = catalog(UID=uid)
            if len(res) > 0:
                return res[0].getObject()
        adapter = self.getParentNode()
        if getattr(adapter, 'portal_type', None) != \
                            'FormSaveData2ContentAdapter':
            adapter = None
        return adapter

    def setFormAdapter(self, adapter):
        self._adapter_uid = adapter.UID()
        self._p_changed = 1

    security.declareProtected('View', 'Title')
    def Title(self):
        """
        generate custom title from the selected
        form field or the given TALES expression override
        """
        adapter = self.getFormAdapter()
        if not adapter:
            return self.getId()
        # If there's a TALES expression:
        if adapter.getRawDynamicTitle():
            # TALES expr evaluation may require permissions an anonymous user
            # does not have. So we set up a new security manager and pose as
            # an Owner.
            old_security_manager = getSecurityManager()
            user = self.getWrappedOwner()
            newSecurityManager(None, user)

            # Try evaluating it
            exprcontext = getExprContext(self, self)
            try:
                value = adapter.getDynamicTitle(
                    expression_context=exprcontext)
                setSecurityManager(old_security_manager)
                return value
            except Exception:
                # make sure original security manager is reinstated.
                setSecurityManager(old_security_manager)
                raise

        # Ok. No override, resort to using a selected field
        field = adapter.getTitleField()
        schema = self.Schema()
        if field in schema:
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
