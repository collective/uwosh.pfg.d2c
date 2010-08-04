import unittest

from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup


# When ZopeTestCase configures Zope, it will *not* auto-load products
# in Products/. Instead, we have to use a statement such as:
#   ztc.installProduct('SimpleAttachment')
# This does *not* apply to products in eggs and Python packages (i.e.
# not in the Products.*) namespace. For that, see below.
# All of Plone's products are already set up by PloneTestCase.

ztc.installProduct('PloneFormGen')

@onsetup
def setup_product():
    """Set up the package and its dependencies.

    """

    fiveconfigure.debug_mode = True
    import uwosh.pfg.d2c
    zcml.load_config('configure.zcml', uwosh.pfg.d2c)
    fiveconfigure.debug_mode = False

    ztc.installPackage('uwosh.pfg.d2c')

# The order here is important: We first call the (deferred) function
# which installs the products we need for this product. Then, we let
# PloneTestCase set up this product on installation.

setup_product()
ptc.setupPloneSite(products=['uwosh.pfg.d2c'])


#
# PFG throw redirect exceptions that make the test browser mad.
#
from zExceptions import Redirect
from zope.testbrowser.browser import SubmitControl
original_click = SubmitControl.click

def redirect_exception_handling_click(self):
    try:
        original_click(self)
    except Redirect, url:
        # for some reason this exception never catches
        self.browser.open(url)
    except:
        pass
    
SubmitControl.click = redirect_exception_handling_click

class FunctionalTestCase(ptc.FunctionalTestCase):
    """We use this class for functional integration tests that use
    doctest syntax. Again, we can put basic common utility or setup
    code in here.
    """

    def afterSetUp(self):
        # Use the fake mailhost
        roles = ('Member', 'Contributor')
        self.portal.portal_membership.addMember(
            'contributor', 'secret', roles, []
        )
        
    def beforeTearDown(self):
        pass

def test_suite():
    return unittest.TestSuite([

        ztc.FunctionalDocFileSuite(
            'browser.txt', package='uwosh.pfg.d2c',
            test_class=FunctionalTestCase)
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
