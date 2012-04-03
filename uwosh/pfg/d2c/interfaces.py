from zope.interface import Interface, Attribute
from zope.component.interfaces import IObjectEvent


class IFormSaveData2ContentEntry(Interface):
    def getValue(fieldid, default=None):
        """get the value of a field"""

    def setValue(fieldid, value):
        """set the value for a field"""

    def getForm():
        """get connected pfg form"""

    def getFormAdapter():
        """get the form adapter"""


class IFormSaveData2ContentAdapter(Interface):
    pass


class IFormSaveData2ContentEntryFinalizedEvent(IObjectEvent):
    "an event sent when the entry is completed"

    referrer = Attribute("the referring content object")


class ILayer(Interface):
    pass
