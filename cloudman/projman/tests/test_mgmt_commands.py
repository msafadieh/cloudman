import os

from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from helmsman.api import HelmsManAPI, HMServiceContext, NamespaceExistsException
from helmsman.tests.client_mocker import ClientMocker

from projman import models as pm_models


class CommandsTestCase(TestCase):

    TEST_DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')
    INITIAL_HELMSMAN_DATA = os.path.join(
        TEST_DATA_PATH, 'helmsman_config.yaml')
    INITIAL_PROJECT_DATA = os.path.join(
        TEST_DATA_PATH, 'projman_config.yaml')

    def setUp(self):
        super().setUp()
        self.mock_client = ClientMocker(self)
        self.client.force_login(
            User.objects.get_or_create(username='admin', is_superuser=True)[0])

    def tearDown(self):
        self.client.logout()

    def test_projman_load_config_no_args(self):
        with self.assertRaisesRegex(CommandError, "required: config_file"):
            call_command('projman_load_config')

    def test_projman_load_config(self):
        call_command('helmsman_load_config', self.INITIAL_HELMSMAN_DATA)
        call_command('projman_load_config', self.INITIAL_PROJECT_DATA)
        project1 = pm_models.CMProject.objects.get(name='first')
        project2 = pm_models.CMProject.objects.get(name='second')
        self.assertEquals(project1.name, 'first')
        self.assertEquals(project1.owner.username, 'admin')
        self.assertEquals(project2.name, 'second')
        self.assertEquals(project2.owner.username, 'admin')
        admin = User.objects.filter(is_superuser=True).first()
        client = HelmsManAPI(HMServiceContext(user=admin))
        self.assertEquals(client.namespaces.get(project2.name).name, 'second')
        # Test error for default namespace
        with self.assertRaises(NamespaceExistsException):
            call_command("projman_create_project", "default")
        client.namespaces.delete(project1.name)
        client.namespaces.delete(project2.name)
