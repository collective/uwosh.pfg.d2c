from Products.CMFCore.utils import getToolByName

from logging import getLogger
from time import clock
from Acquisition import aq_base
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2Base as BTreeFolder
from folderutils import findObjects, timer, checkpointIterator
from transaction import get
from content.savedataadapter import FormSaveData2ContentAdapter
from Products.CMFCore.utils import getToolByName

logger = getLogger('uwosh.pfg.d2c:upgrades')


default_profile = 'profile-uwosh.pfg.d2c:default'

def upgrade_to_0_5(context):
    context.runImportStepFromProfile(default_profile, 'skins')

def upgrade_to_1_0(context, batch=1000, dryrun=False):
    """ find all btree-based folder below the context, potentially
        migrate them & provide some logging and statistics doing so """
    real = timer()          # real time
    lap = timer()           # real lap time (for intermediate commits)
    cpu = timer(clock)      # cpu time
    processed = 0
    def checkPoint():
        msg = 'intermediate commit (%d objects processed, last batch in %s)...'
        trx = get()
        trx.note('migrated %d btree-folders' % processed)
        trx.savepoint()
    cpi = checkpointIterator(checkPoint, batch)
    catalog = getToolByName(context, 'portal_catalog')
    for brain in catalog(portal_type='FormSaveData2ContentAdapter'):
	obj = brain.getObject()
	migrateD2C(obj)
	processed += 1
	cpi.next()

    checkPoint()                # commit last batch
    if dryrun:
        get().abort()           # abort on test-run...
    msg = 'processed %d object(s) in %s (%s cpu time).'
    msg = msg % (processed, real.next(), cpu.next())
    logger.info(msg)

def migrateD2C(folder):
    """ migrate existing data structure from a regular folder to a btree
        folder;  the folder needs to be btree-based already """
    folder = aq_base(folder)
    assert isinstance(folder, BTreeFolder)
    assert folder.getId()       # make sure the object is properly loaded
    has = folder.__dict__.has_key
    if has('_tree') and not has('_objects'):
        return False            # already migrated...
    folder._initBTrees()        # create _tree, _count, _mt_index
    for info in folder._objects:
        name = info['id']
        # _setOb will notify the ordering adapter itself,
        # so we don't need to care about storing order information here...
        folder._setOb(name, aq_base(getattr(folder, name)))
        delattr(folder, name)
    if has('_objects'):
        delattr(folder, '_objects')
    return True

def upgrade_to_1_1(context):
    pass

