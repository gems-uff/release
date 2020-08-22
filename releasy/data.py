# Releasy Abstract data model
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .miner import AbstractReleaseMiner
    from typing import List

   
class Tag:
    """Tag

    Attributes:
        name: tag name
        commit: tagged commit
        time: tag time
        message (str): tag message - annotated tags only
    """

    def __init__(self, name, commit, time=None, message=None):
        self.name = name
        self.commit = commit
        self.release = None
        self.time = None
        self.message = None
        if time: # annotated tag
            self.is_annotated = True
            self.time = time
            self.message = message
        else:
            self.is_annotated = False
            if commit:
                self.time = commit.committer_time
                self.message = commit.message
    
    def __repr__(self):
        return self.name


class Release:
    """A single software release 
    
    :name: the release name
    :time: the release date
    :head: the last commit of the release
    """

    def __init__(self, name, commit, time, description):
        self.name = name
        self.head = commit
        self.time = time
        self.description = description

    def __repr__(self):
        return self.name


class TagRelease(Release):
    """ A release represented by a tag """

    def __init__(self, tag: Tag):
        super().__init__(tag.name, tag.commit, tag.time, None) #TODO add description
        self.tag = tag


class Commit:
    """
    Commit

    Attributes:
        hashcode: commit id
        message: commit message
        subject: first line from commit message
        committer: contributor responsible for the commit
        author: contributor responsible for the code
        time: commit time
        author_time: author time
        release: associated release
    """
    def __init__(self, hashcode, parents=None, message=None, 
                 author=None, author_time=None, 
                 committer=None, committer_time=None):
        self.id = hashcode
        self.hashcode = hashcode
        self.parents = parents
        self.message = message
        self.author = author
        self.author_time = author_time
        self.committer = committer
        self.committer_time = committer_time
        self.release = None

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return hash(self) == hash(other)

    def has_release(self) -> bool:
        return self.release != None

    def __repr__(self):
        return str(self.hashcode)


class Vcs:
    """
    Version Control Repository

    Attributes:
        __commit_dict: internal dictionary of commits
    """
    def __init__(self, path):
        self.path = path
        self._tags = []

    def tags(self) -> List[Tag]:
        """ Return repository tags """
        return self._tags

    def commits(self) -> List[Commit]:
        pass


class ReleaseSet:
    """ An easy form to retrieve releases """
    def __init__(self):
        self.index = {}
        self.releases : List[ReleaseData] = []

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.releases[key]
        elif isinstance(key, str):
            return self.releases[self.index[key]]
        else: 
            raise TypeError()

    def add(self, release: Release, commits: List[Commit]):
        data = ReleaseData(release, commits)
        self.releases.append(data)
        self.index[release.name] = len(self.releases)-1

    def __len__(self):
      return len(self.releases)


class ReleaseData:
    """ Connect release and commits """
    def __init__(self, release: Release = None, commits: List[Commit] = None):
        self.release = release
        self.commits = commits

    def __getattr__(self, name):
        if name in dir(self.release):
            return getattr(self.release, name)
        else:
            raise AttributeError


class Project:
    def __init__(self, vcs: Vcs, releases: ReleaseSet):
        self.vcs = vcs
        self.releases = releases


        

    