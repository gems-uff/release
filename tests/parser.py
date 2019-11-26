import json
import cProfile

from releasy.miner.vcs.git import GitVcs
from releasy.miner.vcs.miner import Miner

from releasy.model import Project, Tag, Commit
from releasy.release import Release

def print_commits(project):
    for release in project.releases:
        print(release.name)
        for commit in release.commits:
            print(" - %s" % commit.subject)


def print_release_stat(project):
    print("# releases: %d" % len(project.releases))
    release: Release
    for release in project.releases:
        print(json.dumps({
                            'release': str(release),
                            'base': str(release.base_releases),
                            # 'reachable': str(release.reachable_releases)
                            # 'time': str(release.time),
                            # 'typename': release.typename,
                            # # 'churn': release.churn,
                            # 'commits': release.commits.count(),
                            # # 'commits.churn': release.commits.total('churn'),
                            # # 'rework': release.commits.total('churn') - release.churn,
                            # 'merges': release.commits.total('merges'),
                            # 'developers': release.developers.count(),
                            # 'authors': release.developers.authors.count(),
                            # 'committers': release.developers.committers.count(),
                            # 'main_developers': release.developers.authors.top(0.8).count(),
                            # 'newcomers': release.developers.newcomers.count(),
                            # 'length': str(release.length),
                            # 'length_group': release.length_group,
                            # 'length_groupname':release.length_groupname, 
                            # 'base': str(release.base_releases)
                        }, indent=2))
    #print(project.commits.total('churn'), project.commits.count())
    #print({ 'a':1})


# releasy.model_git.RELEASY_FT_COMMIT_CHURN = 1

# project = ProjectFactory.create(".", GitVcs())
# project = ProjectFactory.create("../../repos/discourse.git", GitVcs())
# miner = Miner(vcs=GitVcs("../../repos/sapos"))
miner = Miner(vcs=GitVcs("../../repos/git/git"), track_base_release=False)
cProfile.run('miner.mine_commits()')

#project = miner.mine_releases()
#project = miner.mine_commits()
# project = ProjectFactory.create("../../repos/angular")
# project = Project.create("local", "../repos/atom", GitVcs())
# project = Project.create("local", "../repos/mongo", GitVcs())
#project = Project.create("local", "../repos/old/puppet", GitVcs())
# print_commits(project)
#print_release_stat(project)
