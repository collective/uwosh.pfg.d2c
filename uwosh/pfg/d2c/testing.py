# -*- coding: utf-8 -*-

from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing.bbb import PTC_FIXTURE
from plone.testing import z2

import Products.PloneFormGen
import plone.app.layout
import uwosh.pfg.d2c


class Fixture(PloneSandboxLayer):

    defaultBases = (PTC_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=Products.PloneFormGen)
        self.loadZCML(package=plone.app.layout)
        self.loadZCML(package=uwosh.pfg.d2c)
        z2.installProduct(app, 'Products.PloneFormGen')
        z2.installProduct(app, 'uwosh.pfg.d2c')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        self.applyProfile(portal, 'Products.PloneFormGen:default')
        self.applyProfile(portal, 'uwosh.pfg.d2c:default')
        setRoles(portal, TEST_USER_ID, ['Member', 'Manager'])


FIXTURE = Fixture()

D2C_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name='uwosh.pfg.d2c:Integration',
)
D2C_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE, z2.ZSERVER_FIXTURE),
    name='uwosh.pfg.d2c:Functional',
)
