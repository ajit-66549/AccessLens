from django.test import TestCase
from django.db.utils import IntegrityError

from .models import Project
from orgs.models import Organization

# Create your tests here.
"""
    This test checks the database refuses to save two project with same key in same organization.
"""
class ProjectModelsTest(TestCase):
    # setup one organization
    def setUp(self):
        self.org = Organization.objects.create(name="Org1", slug="org1")
        
    # test string representation
    def test_str(self):
        project = Project.objects.create(
            organization = self.org,
            key = "Project1",
            name = "project1",
            description = "Test Unique Constraints",
        )
        self.assertEqual(str(project), "org1:Project1")
        
    # create one project in that organization
    def test_unique_key_per_org(self):
        project = Project.objects.create(
            organization = self.org,
            key = "Project1",
            name = "project1",
            description = "Test",
        )
        with self.assertRaises(IntegrityError):
            # create another project with the same key in the same org, so assertRaises must raise an integrity error
            Project.objects.create(
                organization=self.org,
                key="Project1",
                name="Duplicate Key",
            )