from zope.interface import implements
from zope.component.interfaces import ObjectEvent
from uwosh.pfg.d2c.interfaces import IFormSaveData2ContentEntryFinalizedEvent

class FormSaveData2ContentEntryFinalizedEvent(ObjectEvent):
   ""
   implements(IFormSaveData2ContentEntryFinalizedEvent)
