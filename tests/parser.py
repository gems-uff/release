import json
import cProfile

from releasy.miner_git import GitVcs
from releasy.miner import TagReleaseMiner, PathCommitMiner, RangeCommitMiner, TimeCommitMiner, VersionReleaseMatcher, VersionReleaseSorter, TimeReleaseSorter

vcs = GitVcs("../../repos2/vuejs/vue")
#vcs = GitVcs("../../repos2/facebook/react")
#vcs = GitVcs("../../repos2/facebook/react")
#vcs = GitVcs("../../repos2/laravel/framework")
#vcs = GitVcs("../../repos2/facebook\jest")
# vcs = GitVcs("../../repos2/symfony/symfony")
# vcs = GitVcs("../../repos2/git/git")
# vcs = GitVcs("../../repos2/git/git")
vcs = GitVcs("../../repos2/electron/electron")


release_matcher = VersionReleaseMatcher()
time_release_sorter = TimeReleaseSorter()
version_release_sorter = VersionReleaseSorter()

time_release_miner = TagReleaseMiner(vcs, release_matcher, time_release_sorter)
time_release_set = time_release_miner.mine_releases()

version_release_miner = TagReleaseMiner(vcs, release_matcher, version_release_sorter)
version_release_set = version_release_miner.mine_releases()

path_miner = PathCommitMiner(vcs, time_release_set)
range_miner = RangeCommitMiner(vcs, version_release_set)
time_miner = TimeCommitMiner(vcs, version_release_set)

print(f" - parsing by path")
#cProfile.run("path_miner.mine_commits()")
#path_release_set = path_miner.mine_commits()
print(f" - parsing by time")
cProfile.run("time_miner.mine_commits()")
#time_release_set = time_miner.mine_commits()
print(f" - parsing by range")
#range_release_set = range_miner.mine_commits()
#cProfile.run("range_miner.mine_commits()")


# def print_commits(project):
#     for release in project.releases:
#         print(release.name)
#         for commit in release.commits:
#             print(" - %s" % commit.subject)


# def print_release_stat(project):
#     print("# releases: %d" % len(project.releases))
#     release: Release
#     for release in project.releases:
#         print(json.dumps({
#                             'release': str(release),
#                             'base': str(release.base_releases),
#                             # 'reachable': str(release.reachable_releases)
#                             # 'time': str(release.time),
#                             # 'typename': release.typename,
#                             # # 'churn': release.churn,
#                             # 'commits': release.commits.count(),
#                             # # 'commits.churn': release.commits.total('churn'),
#                             # # 'rework': release.commits.total('churn') - release.churn,
#                             # 'merges': release.commits.total('merges'),
#                             # 'developers': release.developers.count(),
#                             # 'authors': release.developers.authors.count(),
#                             # 'committers': release.developers.committers.count(),
#                             # 'main_developers': release.developers.authors.top(0.8).count(),
#                             # 'newcomers': release.developers.newcomers.count(),
#                             # 'length': str(release.length),
#                             # 'length_group': release.length_group,
#                             # 'length_groupname':release.length_groupname, 
#                             # 'base': str(release.base_releases)
#                         }, indent=2))
#     #print(project.commits.total('churn'), project.commits.count())
#     #print({ 'a':1})


# # releasy.model_git.RELEASY_FT_COMMIT_CHURN = 1

# # project = ProjectFactory.create(".", GitVcs())
# # project = ProjectFactory.create("../../repos/discourse.git", GitVcs())
# # miner = Miner(vcs=GitVcs("../../repos/sapos"))
# #miner = Miner(vcs=GitVcs("../../repos/git/git"), track_base_release=False)
# miner = Miner(vcs=GitVcs("../../repos/tensorflow/tensorflow"), track_base_release=False)

# #project = cProfile.run('miner.mine(skip_commits=True)')
# project = miner.mine(skip_commits=True)

# for tag in project.tags:
#     print(tag.name, tag.is_annotated)

# #project = miner.mine_releases()
# #project = miner.mine_commits()
# # project = ProjectFactory.create("../../repos/angular")
# # project = Project.create("local", "../repos/atom", GitVcs())
# # project = Project.create("local", "../repos/mongo", GitVcs())
# #project = Project.create("local", "../repos/old/puppet", GitVcs())
# # print_commits(project)
# #print_release_stat(project)
