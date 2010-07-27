from zope.component import adapts
from zope.interface import implements
from archetypes.schemaextender.interfaces import ISchemaExtender
from Products.Archetypes.public import BooleanWidget
from interfaces import IFormSaveData2ContentEntry
from Acquisition import aq_parent, aq_inner
from Products.Archetypes.Field import TextField, StringField, DateTimeField, \
    FixedPointField, FileField, LinesField, IntegerField
from Products.PloneFormGen.content.fieldsBase import LinesVocabularyField, \
    StringVocabularyField
from Products.PloneFormGen.content.likertField import LikertField
from Products.PloneFormGen.content.fields import HtmlTextField, NRBooleanField, \
    PlainTextField
    
from archetypes.schemaextender.field import ExtensionField

class XPlainTextField(ExtensionField, PlainTextField): pass
class XTextField(ExtensionField, TextField): pass
class XStringField(ExtensionField, StringField): pass
class XDateTimeField(ExtensionField, DateTimeField): pass        
class XFixedPointField(ExtensionField, FixedPointField): pass
class XFileField(ExtensionField, FileField): pass
class XLinesField(ExtensionField, LinesField): pass
class XIntegerField(ExtensionField, IntegerField): pass

class XLinesVocabularyField(ExtensionField, LinesVocabularyField): pass
class XStringVocabularyField(ExtensionField, StringVocabularyField): pass

class XLikertField(ExtensionField, LikertField): pass

class XHtmlTextField(ExtensionField, HtmlTextField): pass
class XNRBooleanField(ExtensionField, NRBooleanField): pass
    
extension_fields = [
    XTextField, XStringField, XDateTimeField, XFixedPointField, XFileField,
    XLinesField, XIntegerField, XLinesVocabularyField, XStringVocabularyField,
    XLikertField, XHtmlTextField, XNRBooleanField, XPlainTextField
]

FIELDS = {}

for klass in extension_fields:
    FIELDS[klass.__name__] = klass

class ContentEntryExtender(object):
    """
    We use this because it's a nice way to dynamically add fields
    to content.
    """
    adapts(IFormSaveData2ContentEntry)
    implements(ISchemaExtender)

    def __init__(self, context):
        self.context = context

    def getFields(self):
        form = aq_parent(aq_parent(aq_inner(self.context)))
        orig_fields = form.fgFields()
        fields = []
        
        for field in orig_fields:
            klassname = 'X' + field.__class__.__name__
            if FIELDS.has_key(klassname):
                klass = FIELDS[klassname]
                fields.append(klass(field.__name__, **field._properties))
            
        return fields