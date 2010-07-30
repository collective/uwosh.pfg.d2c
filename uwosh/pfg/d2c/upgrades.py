from Products.CMFCore.utils import getToolByName

default_profile = 'profile-uwosh.pfg.d2c:default'

def upgrade_to_0_5(context):
    context.runImportStepFromProfile(default_profile, 'skins.xml')
