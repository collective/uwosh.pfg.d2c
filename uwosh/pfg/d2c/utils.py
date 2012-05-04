from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from AccessControl.User import UnrestrictedUser as BaseUnrestrictedUser


class UnrestrictedUser(BaseUnrestrictedUser):
    """Unrestricted user that still has an id.
    """
    def getId(self):
        """Return the ID of the user.
        """
        return self.getUserName()


def executeAsManager(context, function, *args, **kwargs):
    sm = getSecurityManager()
    try:
        try:
            tmp_user = UnrestrictedUser(
              sm.getUser().getId(),
               '', ['Manager'],
               ''
            )

            # Act as user of the portal
            acl = getToolByName(context, 'acl_users')
            tmp_user = tmp_user.__of__(acl)
            newSecurityManager(None, tmp_user)

            # Call the function
            return function(*args, **kwargs)

        except:
            # If special exception handlers are needed, run them here
            raise
    finally:
        # Restore the old security manager
        setSecurityManager(sm)
