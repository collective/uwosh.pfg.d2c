"Custom event implementations."

from zope.interface import implements
from zope.component.interfaces import ObjectEvent
from uwosh.pfg.d2c.interfaces import IFormSaveData2ContentEntryFinalizedEvent

class FormSaveData2ContentEntryFinalizedEvent(ObjectEvent):
   """Useful for third-party code that wants to do something with data content entries as soon as they are created.
      Built-in zope/AT events either fire too early, or fire also upon subsequent content edits. This event is only
      fired once after each data entry is fully created, making it more useful for the purpose.
   """

   def __init__(self, object, referrer):
      self.object = object
      self.referrer = referrer

   implements(IFormSaveData2ContentEntryFinalizedEvent)

