from zope.app.component.hooks import getSite
from zope.component import getUtility
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from AccessControl.User import UnrestrictedUser as BaseUnrestrictedUser
from Products.CMFCore.permissions import ManagePortal
try:
    import json
except:
    import simplejson as json


class ManageD2CTypes(BrowserView):

    def _hasPermission(self):
        return getSecurityManager().checkPermission(ManagePortal, getSite())

    def hasPermission(self):
        return json.dumps({
            'hasPermission': self._hasPermission()
        })

    def addD2CType(self, name):
        if self.request.get("REQUEST_METHOD", 'GET') != 'POST':
            return json.dumps({'status': 'error', 'msg': 'Must be POST'})
        else:
            if not self._hasPermission():
                return json.dumps({'status': 'error', 'msg': 'Not permitted'})
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
        return json.dumps({'status': 'success', 'id': new_id, 'title': name})

    def deleteType(self, id):
        if self.request.get("REQUEST_METHOD", 'GET') != 'POST':
            return
        else:
            if not self._hasPermission():
                return json.dumps({'status': 'error', 'msg': 'Not permitted'})
        if id == 'FormSaveData2ContentEntry':
            return json.dumps({'status': 'error',
                               'msg': 'Cannot delete this type.'})
        catalog = getToolByName(self.context, 'portal_catalog')
        if len(catalog(portal_type=id)) > 0:
            return json.dumps({'status': 'error',
                               'msg': 'Can not delete this type because '
                                      'there are existing objects on the '
                                      'site right now.'})

        portal_types = getToolByName(self.context, 'portal_types')
        typ = portal_types[id]
        if typ.product != 'uwosh.pfg.d2c':
            return json.dumps({'status': 'failure'})
        portal_types.manage_delObjects([id])
        return json.dumps({'status': 'success', 'id': id})


_builtin_policies = {
    'simple_publication_workflow': 'simple-publication',
    'intranet_workflow': 'intranet',
    'plone_workflow': 'old-plone',
    'one_state_workflow': 'one-state'
}


class UnrestrictedUser(BaseUnrestrictedUser):
    """Unrestricted user that still has an id.
    """
    def getId(self):
        """Return the ID of the user.
        """
        return self.getUserName()


class PlacefulWorkflow(BrowserView):

    def _getAvailableWorkflows(self, placeful):
        pw = getToolByName(self.context, 'portal_workflow')
        config = placeful.getWorkflowPolicyConfig(self.context)
        policy_id = None
        if config:
            policy_id = config.getPolicyBelow()
            if policy_id:
                policy_id = policy_id.id
        workflows = []
        for workflow in pw.objectValues():
            workflowpid = _builtin_policies.get(workflow.id, workflow.id)
            workflows.append({
                'id': workflow.id,
                'title': workflow.title,
                'selected': workflowpid == policy_id
            })
        return json.dumps({
            'status': 'success',
            'workflows': workflows
        })

    def getAvailableWorkflows(self):
        placeful = getToolByName(self.context,
            'portal_placeful_workflow', None)
        if not placeful:
            return json.dumps({'status': 'error',
                               'msg': 'placeful workflow not installed'})
        return self.executeAsManager(self._getAvailableWorkflows, placeful)

    def setWorkflowPolicy(self, placeful, id):
        workflow_id = id
        if id in _builtin_policies:
            id = _builtin_policies[id]

        if not placeful.getWorkflowPolicyConfig(self.context):
            factory = self.context.manage_addProduct['CMFPlacefulWorkflow']
            factory.manage_addWorkflowPolicyConfig()

        types_tool = getToolByName(self.context, 'portal_types')
        # if policy not created yet, do it
        if id not in placeful.objectIds():
            wf_tool = getToolByName(self.context, 'portal_workflow')
            placeful.manage_addWorkflowPolicy(id)
            policy = placeful[id]
            policy.setDefaultChain((workflow_id, ))
            for ptype in types_tool.objectIds():
                chain = wf_tool.getChainForPortalType(ptype, managescreen=True)
                if chain:
                    policy.setChain(ptype, (workflow_id, ))
        else:
            policy = placeful.getWorkflowPolicyById(id)
        for typ in types_tool.objectValues():
            if typ.product == 'uwosh.pfg.d2c':
                chain = policy.getChainFor(typ.id)
                if chain != (workflow_id, ):
                    policy.setChain(typ.id, (workflow_id, ))

        config = placeful.getWorkflowPolicyConfig(self.context)
        config.setPolicyBelow(id)

    def assignWorkflowHere(self, id):
        if self.request.get("REQUEST_METHOD", 'GET') != 'POST':
            return json.dumps({'status': 'error',
                               'msg': 'Must be POST request.'})
        placeful = getToolByName(self.context,
            'portal_placeful_workflow', None)
        if not placeful:
            return json.dumps({'status': 'error',
                               'msg': 'placeful workflow not installed'})
        wf_tool = getToolByName(self.context, 'portal_workflow')
        if id not in wf_tool.objectIds():
            return json.dumps({'status': 'error',
                               'msg': 'Not a valid workflow.'})

        self.executeAsManager(self.setWorkflowPolicy, placeful, id)

        return json.dumps({'status': 'success'})

    def executeAsManager(self, function, *args, **kwargs):
        sm = getSecurityManager()
        try:
            try:
                tmp_user = UnrestrictedUser(
                  sm.getUser().getId(),
                   '', ['Manager'],
                   ''
                )

                # Act as user of the portal
                acl = getToolByName(self.context, 'acl_users')
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
