from AccessControl import ClassSecurityInfo

from Products.Archetypes.public import *
from Products.ATContentTypes.content.base import registerATCT
from Products.PloneFormGen.content.actionAdapter import FormActionAdapter, FormAdapterSchema
from uwosh.pfg.d2c.config import PROJECTNAME
try:
    from Products.ATContentTypes.content.folder import ATBTreeFolderSchema as ATFolderSchema, ATBTreeFolder as ATFolder
except:
    from Products.ATContentTypes.content.folder import ATFolderSchema, ATFolder

from uwosh.pfg.d2c.interfaces import IFormSaveData2ContentAdapter
from zope.interface import implements
from Products.Archetypes.Field import FileField
from Products.Archetypes.Field import ObjectField
from Products.CMFCore.utils import getToolByName
from Products.PloneFormGen.interfaces import IPloneFormGenActionAdapter
from Products.Archetypes.utils import DisplayList

from uwosh.pfg.d2c import pfgMessageFactory as _

try:
    from Products.DataGridField import DataGridField
except:
    class DataGridField:
        pass

FormSaveData2ContentAdapterSchema = ATFolderSchema.copy() + FormAdapterSchema.copy() + \
    Schema((
        BooleanField('avoidSecurityChecks',
            i18n_domain="uwosh.pfg.d2c",
            label_msgid="label_savecontentadapter_avoidsecuritychecks",
            description_msgid="help_savecontentadapter_avoidsecuritychecks",

            default=True,
            widget=BooleanWidget(label="Avoid Security Checks",
                description="""
                Avoid checking if the user has permission to create the content
                data. You will almost always want this checked; otherwise,
                anonymous users will most likely not be able to submit your
                forms.
                """,)
        ),
        StringField('titleField',
            i18n_domain="uwosh.pfg.d2c",
            label_msgid="label_savecontentadapter_title",
            description_msgid="help_savecontentadapter_title",
            searchable=False,
            required=False,
            vocabulary='fieldVocabulary',
            widget=SelectionWidget(
                label='Title Field',
                description="""
                    Select a field to be used as the title of the entries.
                    You will have to reindex previous form results for you
                    to notice most changes. You can edit each form result to 
                    force reindexing.
                """
            ),
            default='id'
        ),
   
        StringField("entryType",
            i18n_domain="uwosh.pfg.d2c",
            label_msgid="label_savecontentadapter_entrytype",
            description_msgid="help_savecontentadapter_entrytype",
            default="FormSaveData2ContentEntry",
            searchable = False,
            mutator='setEntryType',
            required = False,
            widget = SelectionWidget(
               label = 'Saved entry content type',
               description = """Portal type to use for the saved data. Leave as default if you're unsure of what this does."""
                             """If you select a plone standard type, you must make sure the field names are the same in order for the data to store correctly."""
            ),
            vocabulary = 'entry_types'
        ),
    ))

class FormSaveData2ContentAdapter(ATFolder, FormActionAdapter):
    """A form action adapter that will save form input data and 
       return it in csv- or tab-delimited format."""

    implements(IFormSaveData2ContentAdapter, IPloneFormGenActionAdapter)
    schema = FormSaveData2ContentAdapterSchema

    meta_type = portal_type = 'FormSaveData2ContentAdapter'
    archetype_name = 'Save Data to Content Adapter'

    security = ClassSecurityInfo()
    
    def entry_types(self):
        pt = getToolByName(self, 'portal_types')
        derived_types = {}
        for fti in pt.listTypeInfo():
            if fti.getProperty('product') == 'uwosh.pfg.d2c':
               derived_types[fti.getId()] = fti.getProperty('title')
        if "FormSaveData2ContentAdapter" in derived_types: 
            del derived_types["FormSaveData2ContentAdapter"]
        
        return DisplayList(derived_types.items())

    def setEntryType(self, entry_type):
        pt = getToolByName(self, 'portal_types')
        type_info = pt.getTypeInfo(self.portal_type)
        if entry_type not in type_info.allowed_content_types:
            type_info.allowed_content_types = tuple(set(type_info.allowed_content_types) | set([entry_type]))

        field = self.getField('entryType')
        field.set(self, entry_type)


    def createEntry(self):
        id = self.generateUniqueId()
        entrytype = self.getEntryType() or "FormSaveData2ContentEntry"

        if self.getAvoidSecurityChecks():
            pt = getToolByName(self, 'portal_types')
            type_info = pt.getTypeInfo(entrytype)
            ob = type_info._constructInstance(self, id)
            # CMFCore compatibility
            if hasattr(type_info, '_finishConstruction'):
                return type_info._finishConstruction(ob)
            else:
                return ob
        else:
            self.invokeFactory(entrytype, id)
            return self[id]
    
    def onSuccess(self, fields, REQUEST=None, loopstop=False):
        """
        magic done here...
        """

        obj = self.createEntry()
        
        for field in self.fgFields():
            name = field.getName()
            value = REQUEST.form.get(name)
            
            if field.__class__ == DataGridField:
                # clean up datagrid field for issues...
                if type(value) in (tuple, set, list):
                    newval = []
                    for values in value:
                        values = dict(values)
                        if values.get('orderindex_', None) == 'template_row_marker':
                            del values['orderindex_']
                            
                        newval.append(values)
                    value = newval
            
            if field.__class__ == FileField:
                name += '_file'
                if value.filename:
                    field.set(obj, value)
            else:
                field.set(obj, value)
                
        obj.reindexObject()
        
    def fieldVocabulary(self):
        return [field.getName() for field in self.fgFields()]
        
registerATCT(FormSaveData2ContentAdapter, PROJECTNAME)
