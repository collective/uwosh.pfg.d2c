from zope.component import getUtility
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
try:
    import json
except:
    import simplejson as json


class AddD2CType(BrowserView):

    def __call__(self, name):
        if self.request.get("REQUEST_METHOD", 'GET') != 'POST':
            return
        portal_types = getToolByName(self.context, 'portal_types')
        data = portal_types.manage_copyObjects(['FormSaveData2ContentEntry'])
        res = portal_types.manage_pasteObjects(data)
        id = res[0]['new_id']
        normalizer = getUtility(IIDNormalizer)
        new_id = normalizer.normalize(name)

        count = 1
        while new_id in portal_types.objectIds():
            new_id = normalizer.normalize(name + str(count))
            count += 1

        portal_types.manage_renameObject(id, new_id)
        new_type = portal_types[new_id]
        new_type.title = name
        return json.dumps({'id': new_id, 'title': name})


class DeleteType(BrowserView):

    def __call__(self, id):
        if self.request.get("REQUEST_METHOD", 'GET') != 'POST':
            return
        if id == 'FormSaveData2ContentEntry':
            return json.dumps({'status': 'Cannot delete this type.'})
        catalog = getToolByName(self.context, 'portal_catalog')
        if len(catalog(portal_type=id)) > 0:
            return json.dumps({'status': 'Can not delete this type because '
                                         'there are existing objects on the '
                                         'site right now.'})

        portal_types = getToolByName(self.context, 'portal_types')
        typ = portal_types[id]
        if typ.product != 'uwosh.pfg.d2c':
            return json.dumps({'status': 'failure'})
        portal_types.manage_delObjects([id])
        return json.dumps({'status': 'success', 'id': id})
