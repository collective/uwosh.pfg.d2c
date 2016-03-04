from urlparse import urlparse

from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ModifyPortalContent
from Products.Archetypes.public import BooleanField, BooleanWidget, \
    StringField, StringWidget, FileField, Schema, SelectionWidget
from Products.Archetypes.utils import DisplayList
from Products.ATContentTypes.content.base import registerATCT

from zope.interface import implements
from zope.event import notify

try:
    from Products.ATContentTypes.content.folder import \
        ATBTreeFolderSchema as ATFolderSchema
    from Products.ATContentTypes.content.folder import \
        ATBTreeFolder as ATFolder
except:
    from Products.ATContentTypes.content.folder import ATFolderSchema
    from Products.ATContentTypes.content.folder import ATFolder

# Problematic interfaces on Plone 3
toimplement = []
try:
    from plone.folder.interfaces import IOrderable
    toimplement.append(IOrderable)
except ImportError:
    pass
try:
    from plone.app.folder.folder import IATUnifiedFolder
    toimplement.append(IATUnifiedFolder)
except ImportError:
    pass

from Products.PloneFormGen.content.actionAdapter import FormActionAdapter
from Products.PloneFormGen.content.actionAdapter import FormAdapterSchema
from Products.PloneFormGen.interfaces import IPloneFormGenActionAdapter
from Products.PloneFormGen.config import EDIT_TALES_PERMISSION
from Products.Archetypes.event import ObjectInitializedEvent
from Products.ATContentTypes.interface import IATFolder
from Products.ATContentTypes.content.schemata import NextPreviousAwareSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.CMFCore.permissions import View
from Acquisition import aq_parent, aq_inner

from Products.TALESField import TALESString

try:
    from Products.DataGridField import DataGridField
except:
    class DataGridField:
        pass

from uwosh.pfg.d2c.config import PROJECTNAME
from uwosh.pfg.d2c import pfgMessageFactory as _
from uwosh.pfg.d2c.interfaces import IFormSaveData2ContentAdapter
from uwosh.pfg.d2c.events import FormSaveData2ContentEntryFinalizedEvent
from uwosh.pfg.d2c.utils import executeAsManager

FormSaveData2ContentAdapterSchema = ATFolderSchema.copy() + \
    NextPreviousAwareSchema.copy() + \
    FormAdapterSchema.copy() + Schema((
        BooleanField('avoidSecurityChecks',
            default=True,
            widget=BooleanWidget(
                label=_("label_savecontentadapter_avoidsecuritychecks",
                        default=u"Avoid Security Checks"),
                description=_('help_savecontentadapter_avoidsecuritychecks',
                              default=u"Avoid checking if the user has permission to create the content "
                                      u"data. You will almost always want this checked; otherwise, "
                                      u"anonymous users will most likely not be able to submit your "
                                      u"forms."
                              ),
            )
        ),
        StringField('titleField',
            searchable=False,
            required=False,
            vocabulary='fieldVocabulary',
            widget=SelectionWidget(
                label=_(u'label_savecontentadapter_title',
                        default="Title Field"),
                description=_('help_savecontentadapter_title',
                              default=u"Select a field to be used as the title of the entries. "
                                      u"You will have to reindex previous form results for you "
                                      u"to notice most changes. You can edit each form result to "
                                      u"force reindexing."
                             ),
            ),
            default='id'
        ),

        StringField("entryType",
            default="FormSaveData2ContentEntry",
            searchable=False,
            required=True,
            mutator='setEntryType',
            widget=SelectionWidget(
                label=_('label_savecontentadapter_entrytype',
                        default=u'Saved entry content type'
                        ),
                description=_('help_savecontentadapter_entrytype',
                              default=u"Portal type to use for the saved data. Leave as "
                                      u"default if you're unsure of what this does. "
                                      u"If you select a plone standard type, you must "
                                      u"make sure the field names are the same in order "
                                      u"for the data to store correctly."
                              ),
                format='radio',
                macro="d2c-adapter-selection",
            ),
            vocabulary='entry_types'
        ),

        TALESString('dynamicTitle',
            schemata='overrides',
            searchable=0,
            required=0,
            validators=('talesvalidator',),
            default='',
            write_permission=EDIT_TALES_PERMISSION,
            read_permission=ModifyPortalContent,
            isMetadata=True,  # just to hide from base view
            widget=StringWidget(label=_(u'label_dynamictitle_text',
                                        default=u"Dynamic title override"),
                description=_(u'help_dynamictitle_text',
                              default=u"A TALES expression that will be "
                                      u"evaluated to determine the title "
                                      u"for entry"),
                size=70,
            ),
        ),
        BooleanField('niceIds',
            default=False,
            widget=BooleanWidget(
                label=_('label_savecontentadapter_niceIds',
                        default=u"Nice Ids"),
                description=_("help_savecontentadapter_niceIds",
                              default=u"Generate nice ids from the title field. "
                                      u"If this is unchecked, the object id will be generated "
                                      u"from the date of creation. Respects avoid security "
                                      u"checks setting."
                            ),                
            )
        ),
    ))
finalizeATCTSchema(FormAdapterSchema)


class FormSaveData2ContentAdapter(ATFolder, FormActionAdapter):
    """PFG save data adapter that saves form data to content objects"""

    implements(IFormSaveData2ContentAdapter,
               IPloneFormGenActionAdapter,
               IATFolder,
               *toimplement)
    schema = FormSaveData2ContentAdapterSchema

    meta_type = portal_type = 'FormSaveData2ContentAdapter'
    archetype_name = 'Save Data to Content Adapter'

    security = ClassSecurityInfo()

    _ordering = u''

    security.declareProtected(View, 'getNextPreviousParentValue')
    def getNextPreviousParentValue(self):
        """ If the parent node is also an IATFolder and has next/previous
            navigation enabled, then let this folder have it enabled by
            default as well """
        parent = self.getParentNode()
        if IATFolder.providedBy(parent):
            return parent.getNextPreviousEnabled()
        else:
            return False

    # get a vocabulary of available FTI clones of FormSaveData2ContentEntry
    def entry_types(self):
        pt = getToolByName(self, 'portal_types')
        derived_types = {}
        for fti in pt.listTypeInfo():
            # first item always "FormSaveData2ContentEntry"
            if fti.getId()=='FormSaveData2ContentEntry':
                first = fti
            elif fti.getProperty('product') == 'uwosh.pfg.d2c':
                derived_types[fti.getId()] = fti.getProperty('title')
        if "FormSaveData2ContentAdapter" in derived_types:
            del derived_types["FormSaveData2ContentAdapter"]
        return DisplayList([(first.getId(), _(first.getProperty('title')))] + \
                                    [(t[0], _(t[1])) for t in derived_types.items()])

    # add the selected entry type to allowed types if it isn't
    def setEntryType(self, entry_type):
        pt = getToolByName(self, 'portal_types')
        type_info = pt.getTypeInfo(self.portal_type)
        if entry_type not in type_info.allowed_content_types:
            type_info.allowed_content_types = \
                tuple(set(type_info.allowed_content_types) | set([entry_type]))

        field = self.getField('entryType')
        field.set(self, entry_type)

    def _createEntry(self):
        "create an entry of the chosen type"
        id = self.generateUniqueId()
        entrytype = self.getEntryType() or "FormSaveData2ContentEntry"

        if self.getAvoidSecurityChecks():
            pt = getToolByName(self, 'portal_types')
            type_info = pt.getTypeInfo(entrytype)
            if not type_info:
                type_info = pt.getTypeInfo('FormSaveData2ContentEntry')
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
        Triggered on successful form submission. Creates a data content entry,
        adds form contents to it, reindexes and sends an event to notify
        subscribers of the new entry.
        """

        obj = self._createEntry()
        obj.setFormAdapter(self)
        form = aq_parent(aq_inner(self))

        for field in self.fgFields():
            widget_macro = getattr(getattr(field, 'widget', None), 'macro', None)
            name = field.getName()
            value = REQUEST.form.get(name)

            if field.__class__ == DataGridField:
                # clean up datagrid field for issues...
                if type(value) in (tuple, set, list):
                    newval = []
                    for values in value:
                        values = dict(values)
                        if values.get('orderindex_', None) == \
                                'template_row_marker':
                            del values['orderindex_']

                        newval.append(values)
                    value = newval
            elif widget_macro == 'donationfield_widget':
                # need to get the value from different request variables
                value = REQUEST.form.get('%s_level' % name)
                if not value:
                    value = REQUEST.form.get('%s_amount' % name)

            if field.__class__ == FileField:
                field = obj.getField(name)
                name += '_file'
                value = REQUEST.form.get(name)
                if hasattr(value, 'filename') and value.filename:
                    field.set(obj, value)
            else:
                field.set(obj, value)

        # rename id now...
        if self.getNiceIds():
            if self.getAvoidSecurityChecks():
                executeAsManager(self, obj._renameAfterCreation,
                    check_auto_id=False)
            else:
                obj._renameAfterCreation(check_auto_id=False)

        obj.reindexObject()
        notify(ObjectInitializedEvent(obj))

        # dispatch the event for others to use, with referrer
        last_referer = REQUEST.form.get('last_referer', None)
        parsed = urlparse(last_referer)
        pth = getattr(parsed, 'path', parsed[2])
        referrer = self.restrictedTraverse(pth.strip('/').split('/'), None)
        evt = FormSaveData2ContentEntryFinalizedEvent(obj, referrer)
        notify(evt)

        # set values on request so others can know what object was
        # just created
        REQUEST.environ['d2c-obj-created-url'] = obj.absolute_url()
        REQUEST.environ['d2c-obj-created-uid'] = obj.UID()

    # An utility that provides a list of all form field names.
    def fieldVocabulary(self):
        return [field.getName() for field in self.fgFields()]

registerATCT(FormSaveData2ContentAdapter, PROJECTNAME)
