
from apps.codes.models import CodeModel

class CodeModelResources:
    def __init__(self, code="", requirements=[], files=[]):
        self.code=code
        self.requirements=requirements
        self.files=files
    def merge_with(self, a):
        if isinstance(a, list):
            for item in a:
                self.merge_with(item)
        if isinstance(a, self.__class__):
            # append code
            self.add_code(a.code)
            # append requirements
            self.add_requirements(a.requirements)
            self.add_files(a.files)
    def add_code(self, c, append=True):
        if len(c):
            if append:
                self.code="\n".join([self.code, c])
            else:
                self.code="\n".join([c, self.code])
    def has_requirements(self, requirements):
        if isinstance(requirements, list):
            return all([self.has_requirements(req) for req in requirements])
        return requirements in self.requirements
    def add_requirements(self,requirements):
        for req in requirements:
            if not self.has_requirements(req):
                self.requirements.append(req)
    def has_files(self,files):
        if isinstance(files, list):
            return all([self.has_files(f) for f in files])
        return files in self.files
    def add_files(self, files):
        for f in files:
            if not self.has_files(f):
                self.files.append(f)
    def __getitem__(self, i):
        if i==0:
            return self.code
        if i==1:
            return self.requirements
        if i==2:
            return self.files
    @staticmethod
    def from_codemodel(cm=None):
        if cm is None:
            return CodeModelResources()
        if isinstance(cm, list):
            a=CodeModelResources()
            for codemodel in cm:
                a.merge_with(CodeModelResources.from_codemodel(codemodel))
            return a
        return CodeModelResources(cm.get_code(), cm.get_requirements(), cm.get_filenames())
