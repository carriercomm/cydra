# -*- coding: utf-8 -*-
#
# Copyright 2013 Manuel Stocker <mensi@mensi.ch>
#
# This file is part of Cydra.
#
# Cydra is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Cydra is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Cydra.  If not, see http://www.gnu.org/licenses
import os.path
from cydra.test.fixtures import *
from cydra.test.fixtures.common import FixtureWithTempPath
from cydra.test import getConfiguredTestCase
from cydraplugins.trac import TracEnvironments

class TracFixture(FixtureWithTempPath):
    """Configure Cydra for trac"""

    def setUp(self, configDict):
        super(TracFixture, self).setUp(configDict)
        configDict.setdefault('components', {}).setdefault('cydraplugins.trac.TracEnvironments', {})['base'] = self.path

def parameterized(name, fixture):
    class TestTrac(getConfiguredTestCase(fixture)):
        def test_create(self):
            tracenvs = TracEnvironments(self.cydra)
            self.assertTrue(tracenvs, "Unable to get TracEnvironments instance")

            guestuser = self.cydra.get_user(userid='*')
            project = self.cydra.datasource.create_project('tractest', guestuser)
            self.assertTrue(project, "Unable to create project")
            self.assertFalse(tracenvs.has_env(project), "Freshly created project should not have a trac env")

            self.assertTrue(tracenvs.create(project), "Unable to create trac env")
            self.assertTrue(tracenvs.has_env(project), "has_env should return true after env creation")

        def test_autodelete_on_project_deletion(self):
            tracenvs = TracEnvironments(self.cydra)
            guestuser = self.cydra.get_user(userid='*')
            project = self.cydra.datasource.create_project('tractest', guestuser)
            self.assertTrue(tracenvs.create(project), "Unable to create trac env")

            project.delete()
            self.assertFalse(tracenvs.has_env(project), "environment not properly removed on project deletion")

        def test_repository_registration(self):
            tracenvs = TracEnvironments(self.cydra)
            guestuser = self.cydra.get_user(userid='*')
            project = self.cydra.datasource.create_project('tractest', guestuser)
            self.assertTrue(tracenvs.create(project), "Unable to create trac env")

            gitrepo = project.get_repository_type('git').create_repository(project, "gitrepo")
            self.assertTrue(gitrepo, "Unable to create git repository")

            hgrepo = project.get_repository_type('hg').create_repository(project, "hgrepo")
            self.assertTrue(hgrepo, "Unable to create hg repository")

            self.assertTrue(tracenvs.register_repository(gitrepo), "Unable to register git repository")
            self.assertTrue(tracenvs.register_repository(hgrepo), "Unable to register hg repository")
            self.assertFalse(tracenvs.register_repository(gitrepo), "Duplicate registration for git repository possible")
            self.assertFalse(tracenvs.register_repository(hgrepo), "Duplicate registration for hg repository possible")

            self.assertTrue(tracenvs.is_repository_registered(gitrepo), "Is registered did not return true for gitrepo")
            self.assertTrue(tracenvs.is_repository_registered(hgrepo), "Is registered did not return true for hgrepo")

            gitrepo.delete()
            self.assertFalse(tracenvs.is_repository_registered(gitrepo), "Git repo still registered after repository deletion")
            self.assertTrue(tracenvs.is_repository_registered(hgrepo), "Is registered did not return true for hgrepo")

            project.delete()
            self.assertFalse(tracenvs.is_repository_registered(hgrepo), "Hg repo still registered after project deletion")

    TestTrac.__name__ = name
    return TestTrac

TestTrac_File = parameterized("TestTrac_File", TracFixture(FullWithFileDS))
