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


_builtin_policies = {
    'simple_publication_workflow': 'simple-publication',
    'intranet_workflow': 'intranet',
    'plone_workflow': 'old-plone',
    'one_state_workflow': 'one-state'
}


class PlacefulWorkflow(BrowserView):

    def getAvailableWorkflows(self):
        placeful = getToolByName(self.context,
            'portal_placeful_workflow', None)
        if not placeful:
            return json.dumps({'status': 'placeful workflow not installed'})
        pw = getToolByName(self.context, 'portal_workflow')
        config = placeful.getWorkflowPolicyConfig(self.context)
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

    def assignWorkflowHere(self, id):
        if self.request.get("REQUEST_METHOD", 'GET') != 'POST':
            return
        placeful = getToolByName(self.context,
            'portal_placeful_workflow', None)
        if not placeful:
            return json.dumps({'status': 'placeful workflow not installed'})

        workflow_id = id
        if id in _builtin_policies:
            id = _builtin_policies[id]

        # if policy not created yet, do it
        if id not in placeful.objectIds():
            wf_tool = getToolByName(self.context, 'portal_workflow')
            placeful.manage_addWorkflowPolicy(id)
            policy = placeful[id]
            types_tool = getToolByName(self.context, 'portal_types')
            policy.setDefaultChain((workflow_id, ))
            for ptype in types_tool.objectIds():
                chain = wf_tool.getChainForPortalType(ptype, managescreen=True)
                if chain:
                    policy.setChain(ptype, (workflow_id, ))
        else:
            policy = placeful.getWorkflowPolicyById(id)
        chain = policy.getChainFor('FormSaveData2ContentEntry')
        if chain != (workflow_id, ):
            policy.setChain('FormSaveData2ContentEntry', (workflow_id, ))
        chain = policy.getChainFor('FormSaveData2ContentAdapter')
        if chain != (workflow_id, ):
            policy.setChain('FormSaveData2ContentAdapter', (workflow_id, ))

        config = placeful.getWorkflowPolicyConfig(self.context)
        config.setPolicyBelow(id)
        return json.dumps({'status': 'success'})
