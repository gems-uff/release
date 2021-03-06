from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .model import Commit, Project

import re
from datetime import timedelta

from .const import RELEASE_TYPE_MAJOR, RELEASE_TYPE_MINOR, RELEASE_TYPE_DUPLICATED, RELEASE_TIME, START_DEVELOPMENT_TIME, DEVELOPMENT_LENGTH, RELEASE_TYPE_PATCH, RELEASE_TYPE_PRE, RELEASE_TYPE_UNKNOWN
from .model import CommitTracker
from .data import Tag
from .developer import ReleaseDeveloperRoleTracker
from .exception import CommitReleaseAlreadyAssigned, MisplacedTimeException

class ReleaseFactory():
    def __init__(self, project: Project, prefixes=None, ignored_suffixes=None, version_separator=None):
        self._project = project
        self._pre_release_cache = {}
        self.prefixes = prefixes
        self.ignored_suffixes = ignored_suffixes
        if not version_separator:
            self.version_separator = r"\."
        else:
            self.version_separator = version_separator

    def build(self, tag: Tag, orign_release: None):
        """ Build the release

        Parameters:
            tag (Tag): the tag to parse
            
        Returns:
            the release or None if the tag does not represent a release
        """
        release_info = self.get_release_info_from_tag(tag.name)
        if not release_info:
            return None
        
        (release_type, prefix, suffix, major, minor, patch) = release_info
        release_version = f"{major}.{minor}.{patch}"

        if release_version not in self._pre_release_cache:
            self._pre_release_cache[release_version] = []

        if orign_release: #TODO create duplicated release class
            release_type = RELEASE_TYPE_DUPLICATED

        release = Release(
            project=self._project, 
            tag=tag,
            release_type=release_type,
            prefix=prefix,
            suffix=suffix,
            major=major,
            minor=minor,
            patch=patch
        )

        if orign_release: 
            release.original = orign_release
            orign_release.aliases.append(release)

        if release.is_type(RELEASE_TYPE_PRE):
            self._pre_release_cache[release_version].append(release)
        else:
            for pre_release in self._pre_release_cache[release_version]:
                release.add_pre_release(pre_release)

        tag.release = release
        
        return release

    def get_release_info_from_tag(self, tagname):
        vsep = self.version_separator
        prefix_pattern_str = r"(?P<prefix>.*?)"
        suffix_pattern_str = r"[.-]?(?P<suffix>.*)"
        version_pattern_str = r"(?P<version>([0-9]+" + vsep + r"?){2,3})"
        
        pattern_str = f"{prefix_pattern_str}{version_pattern_str}{suffix_pattern_str}"
        pattern = re.compile(pattern_str)
        pattern_match = pattern.match(tagname)
        if not pattern_match:
            return False

        prefix = pattern_match.group("prefix")
        if self.prefixes and prefix not in self.prefixes:
            return False

        suffix = pattern_match.group("suffix")
        if self.ignored_suffixes:
            for ignored_suffix in self.ignored_suffixes:
                ignored_suffix_pattern_str = f"{ignored_suffix}$"
                ignored_suffix_pattern = re.compile(ignored_suffix_pattern_str)
                suffix = re.sub(ignored_suffix_pattern, "", suffix)

        version = pattern_match.group("version")

        semantic_pattern_str = r"(?P<major>[0-9]+)" + vsep + r"(?P<minor>[0-9]+)(" + vsep + r"(?P<patch>[0-9]+))?"
        semantic_pattern = re.compile(semantic_pattern_str)
        semantic_match = semantic_pattern.match(version)
        if not semantic_match:
            return False

        major = int(semantic_match.group("major"))
        minor = int(semantic_match.group("minor"))
        if semantic_match.group("patch"):
            patch = int(semantic_match.group("patch"))
        else:
            patch = 0

        if suffix:
            release_type = RELEASE_TYPE_PRE
        elif patch > 0:
            release_type = RELEASE_TYPE_PATCH
        elif minor > 0:
            release_type = RELEASE_TYPE_MINOR
        elif major > 0:
            release_type = RELEASE_TYPE_MAJOR
        else:
            release_type = RELEASE_TYPE_UNKNOWN

        return (
            release_type,
            prefix,
            suffix,
            major,
            minor,
            patch
        )


class Release:
    """
    Software Release

    Attributes:
        name (str): release name
        description (str): release description
        time: release creation time
        commits: list of commits that belong exclusively to this release
        tag: tag that represents the release
        head: commit referred  by release.tag
        tails: list of commits where the release begin
        developers: list of developers
        length: release duration
    """

    def __init__(self, project: Project, tag, release_type=RELEASE_TYPE_UNKNOWN, prefix=None, suffix=None, major=None, minor=None, patch=None):
        self.project = project
        self._tag = tag
        self.type = release_type
        if not prefix: #TODO check for default arguments
            prefix = ""
        self.prefix = prefix
        if not suffix: #TODO check for default arguments
            suffix = ""
        self.suffix = suffix
        self.major = major
        self.minor = minor
        self.patch = patch
        self.version = f"{major}.{minor}.{patch}"
        self.feature_version = f"{major}.{minor}.x"
        self.base_releases = []
        self.reachable_releases = []
        self.tail_commits = []
        self.commits = []
        self.developers = ReleaseDeveloperRoleTracker()
        self.pre_releases = []
        self.aliases = []
        self.original = None # in case of duplicate return the original release
        
    @property
    def name(self):
        return self._tag.name
        
    @property
    def head_commit(self):
        return self._tag.commit

    @property
    def time(self):
        return self._tag.time

    @property
    def length(self):
        if self.tail_commits:
            length = self.time - self.tail_commits[0].author_time
        else:
            length = self.time - self.head_commit.author_time
        
        if length < timedelta(0):
            raise MisplacedTimeException(self)
        return length

    @property
    def description(self):
        return self._tag.message

    def __repr__(self):
        return self.name

    @property
    def typename(self):
        current = self.project.release_pattern.match(self.name)
        if current:
            if current.group('patch') != '0':
                return 'PATCH'
            elif current.group('minor') != '0':
                return 'MINOR'
            else:
                return 'MAJOR'
        else:
            return 'UNKNOWN'

    @property
    def length_group(self):
        if self.length < timedelta(hours=1):
            return 0 #'minutes'
        elif self.length < timedelta(days=1):
            return 1 #'hours'
        elif self.length < timedelta(days=7):
            return 2 #'days'
        elif self.length < timedelta(days=30):
            return 3 #'weeks'
        elif self.length < timedelta(days=365):
            return 4 #'months'
        else:
            return 5 #'years'

    @property
    def length_groupname(self):
        return {
            0: 'minutes',
            1: 'hours',
            2: 'days',
            3: 'weeks',
            4: 'months',
            5: 'years'
        }[self.length_group]
    
    @property
    def churn(self):
        if self.__commit_stats:
            return self.__commit_stats.churn

        self.__commit_stats = CommitStats()
        if self.base_releases:
            for base_release in self.base_releases:
                self.__commit_stats += self.head.diff_stats(base_release.head)
        else:
            self.__commit_stats = self.head.diff_stats()

        return self.__commit_stats.churn

    def is_type(self, release_type):
        if self.type & release_type == self.type:
            return True
        else:
            return False

    def is_duplicated(self):
        return self.is_type(RELEASE_TYPE_DUPLICATED)

    def get_time(self, of=RELEASE_TIME):
        switch = {
            RELEASE_TIME: lambda : self.time,
            START_DEVELOPMENT_TIME: lambda : self.time
        }

        try:
            return switch[of]()
        except:
            return -1

    def get_length(self, of=DEVELOPMENT_LENGTH):
        switch = {
            DEVELOPMENT_LENGTH: lambda : self.length,
        }

        try:
            return switch[of]()
        except:
            return timedelta(0)


    def is_patch(self) -> bool:
        return self.is_type(RELEASE_TYPE_PATCH)

    def is_pre_release(self) -> bool:
        return self.is_type(RELEASE_TYPE_PRE)

    def add_commit(self, commit: Commit, assign_commit_to_release=True):
        is_newcomer = False
        if assign_commit_to_release:
            if not commit.release:
                commit.release = self
                self.project.add_commit(commit)
                is_newcomer = self.project.developers.add_from_commit(commit)
            else:
                raise CommitReleaseAlreadyAssigned(commit, self)

        self.commits.append(commit)
        self.developers.add_from_commit(commit, is_newcomer)

    def add_commits_from_pre_releases(self):
        """ This method is necessary for lazy loading commits """
        for pre_release in self.pre_releases:
            for commit in pre_release.commits:
                self.add_commit(commit, False)
            for newcomer in pre_release.developers.newcomers:
                self.developers.force_newcomer(newcomer)
            self.tail_commits += pre_release.tail_commits
            self.tail_commits = sorted(self.tail_commits, key=lambda commit: commit.author_time)

    def add_pre_release(self, pre_release: Release):
        self.pre_releases.append(pre_release)
        self.commits.extend(pre_release.commits)
