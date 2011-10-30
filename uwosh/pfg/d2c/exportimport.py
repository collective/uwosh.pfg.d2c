from Products.CMFCore.utils import getToolByName


def install(context):

    if not context.readDataFile('uwosh.pfg.d2c.txt'):
        return

    site = context.getSite()

    qi = getToolByName(site, 'portal_quickinstaller')
    if not qi.isProductInstalled('Products.PloneFormGen'):
        qi.installProduct('Products.PloneFormGen')

    types = getToolByName(site, 'portal_types')
    if 'FormFolder' in types.objectIds():
        folder = types['FormFolder']
        allowed_content_types = set(folder.allowed_content_types)
        allowed_content_types.add('FormSaveData2ContentAdapter')
        folder.allowed_content_types = tuple(allowed_content_types)
