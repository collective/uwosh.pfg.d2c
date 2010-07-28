from zope.component import adapts
from zope.interface import implements
from archetypes.schemaextender.interfaces import ISchemaExtender
from Products.Archetypes.public import BooleanWidget
from interfaces import IFormSaveData2ContentEntry
from Acquisition import aq_parent, aq_inner
from Products.Archetypes.Field import TextField, StringField, DateTimeField, \
    FixedPointField, FileField, LinesField, IntegerField, ObjectField
from Products.PloneFormGen.content.fieldsBase import LinesVocabularyField, \
    StringVocabularyField
from Products.PloneFormGen.content.likertField import LikertField
from Products.PloneFormGen.content.fields import HtmlTextField, NRBooleanField, \
    PlainTextField
    
from archetypes.schemaextender.field import ExtensionField

from plone.memoize.instance import memoize

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

class XLikertField(ExtensionField, LikertField): 
    """
    override default methods which have bugs...
    """
    
    def get(self, instance, **kwargs):
        value = ObjectField.get(self, instance, **kwargs)
        if not value:
            return tuple()
        else:
            return value

    def set(self, instance, value, **kwargs):
        if type(value) in (str, unicode):
            value = [v.strip() for v in value.split(',')]
        ObjectField.set(self, instance, value, **kwargs)


class XHtmlTextField(ExtensionField, HtmlTextField): pass
class XNRBooleanField(ExtensionField, NRBooleanField): pass
    
extension_fields = [
    XTextField, XStringField, XDateTimeField, XFixedPointField, XFileField,
    XLinesField, XIntegerField, XLinesVocabularyField, XStringVocabularyField,
    XLikertField, XHtmlTextField, XNRBooleanField, XPlainTextField
]

extra_fields = [
    'widget', 'questionSet', 'answerSet', 'validators'
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

    @memoize
    def getFields(self):
        form = aq_parent(aq_parent(aq_inner(self.context)))
        obj_fields = form.fgFields()
        fields = []
        
        for field in obj_fields:
            klassname = 'X' + field.__class__.__name__
            if FIELDS.has_key(klassname):
                klass = FIELDS[klassname]
                newfield = klass(field.__name__, **field._properties)
                for key in extra_fields:
                    if hasattr(field, key):
                        setattr(newfield, key, getattr(field, key))
                        
                fields.append(newfield)
            
        return fields