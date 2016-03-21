import logging
import os

from pelican import signals

logger = logging.getLogger(__name__)


class FolderCat(object):

    @staticmethod
    def is_leaf_dir(dir):
        assert os.path.isdir(dir)

        ls = os.listdir(dir)
        for sub_dir in ls:
            sub_dir_absp = os.path.join(dir, sub_dir)
            if os.path.isdir(sub_dir_absp):
                return False

        return True

    def __init__(self, pelican_cats, dir, exc_dirs):
        self.entries = []
        self.is_leaf = self.is_leaf_dir(dir)
        self.name = os.path.basename(dir)
        self.count = None
        self.url = None

        if os.path.basename(dir) in exc_dirs:
            self.excluded = True
        else:
            self.excluded = False

        ls = os.listdir(dir)

        if self.is_leaf:
            for peli_cat, peli_arts in pelican_cats:
                if self.name == peli_cat:
                    self.entries = peli_arts
                    self.url = peli_cat.url
                    self.count = len(peli_arts)
                    break
        else:
            for sub_dir in ls:
                sub_dir_absp = os.path.join(dir, sub_dir)
                if os.path.isdir(sub_dir_absp):
                    fc = FolderCat(pelican_cats, sub_dir_absp, exc_dirs)
                    if fc.excluded is False:
                        self.entries.append(fc)

    def IsLeaf(self):
        return self.is_leaf_dir

    def GetName(self):
        return self.name

    def GetUrl(self):
        return self.url

    def GetEntries(self):
        return self.entries

    def TestPrintSelf(self, depth=0):
        for i in range(depth):
            print '\t',
        print self.name

        if self.is_leaf:
            for fl in self.entries:
                for i in range(depth + 1):
                    print '\t',
                print fl
        else:
            for sub in self.entries:
                sub.TestPrintSelf(depth + 1)


def create_subcategories_by_folder(generator):
    logger.debug('enter subfolderascat plugin')

    content_dir = generator.settings.get('PATH')
    fc = FolderCat(generator.categories, content_dir, ['pages'])

    if __debug__:
        fc.TestPrintSelf()

    generator.foldercat = fc
    generator._update_context(['foldercat'])

    logger.debug('exit subfolderascat plugin')


def register():
    signals.article_generator_finalized.connect(create_subcategories_by_folder)
