from Products.Archetypes.Widget import StringWidget
from Products.Archetypes.Registry import registerWidget


class DonationWidget(StringWidget):
    _properties = StringWidget._properties.copy()
    _properties.update({
        'macro' : 'donationfield_widget'
    })

    def process_form(self, instance, field, form, empty_marker=None, emptyReturnsMarker=False):
        name = field.getName()
        value = form.get('%s_level' % name)
        if not value:
            value = form.get('%s_amount' % name)
        return value, {}
        
registerWidget(DonationWidget, title='Donation Widget')
