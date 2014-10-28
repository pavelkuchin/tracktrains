from django.core.management import call_command
from django.test import TestCase

class CommandsTestCase(TestCase):
    def test_job_bytrainway(self):
        " Test my custom command."

        args = []
        opts = {}
        call_command('job_bytrainway', *args, **opts)

        # TODO write some tests here
