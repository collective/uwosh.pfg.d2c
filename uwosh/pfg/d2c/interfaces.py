from zope.interface import Interface, Attribute
from zope.component.interfaces import IObjectEvent

from uwosh.pfg.d2c import pfgMessageFactory as _


class IFormSaveData2ContentEntry(Interface):
    pass

    
class IFormSaveData2ContentAdapter(Interface):
    pass


class IFormSaveData2ContentEntryFinalizedEvent(IObjectEvent):
    "an event sent when the entry is completed"

    referrer = Attribute("the referring content object")
