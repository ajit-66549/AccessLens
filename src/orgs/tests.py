from django.test import TestCase
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model

from .models import Organization, Membership

User = get_user_model()

# Create your tests here.
"""
    This test checks the database refuses to create two users with same username in the same organization.
"""
class OrganizationModelTest(TestCase):
    # test organization string
    def test_org_str(self):
        org = Organization.objects.create(
            name = "Org1",
            slug = "org1",
        )
        self.assertEqual(str(org), "Org1")
        
class MembershipModelTest(TestCase):
    # setup organization and user
    def setUp(self):
        self.org = Organization.objects.create(
            name = "Org1",
            slug = "org1",
        )
        self.user = User.objects.create_user(
            username="abc",
            email="abc@example.com",
            password="password123",
        )
        self.user2 = User.objects.create_user(
            username="abc",
            email="abc@example.com",
            password="password123",
        )
        
        # create membership between that user and organization
    def test_unique_user_org_membership(self):
        Membership.objects.create(
            user = self.user,
            organization = self.org,
        )
        with self.assertRaises(IntegrityError):
            # create a same membership between same user and same org, so raises Integrity error
            Membership.objects.create(
                user = self.user,
                organization = self.org,
            )