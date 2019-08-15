"""
Test for autocomplete command
"""
from core.base_test.tns_test import TnsTest
from products.nativescript.tns import Tns


# noinspection PyMethodMayBeStatic
class AutocompleteTests(TnsTest):
    changed_to_enable = 'Restart your shell to enable command auto-completion.'
    changed_to_disable = 'Restart your shell to disable command auto-completion.'
    already_enabled = 'Autocompletion is already enabled.'
    enabled = 'Autocompletion is enabled.'
    disabled = 'Autocompletion is disabled.'

    def test_001_autocomplete_enable_and_disable(self):
        # Force enable autocomplete.
        Tns.exec_command(command='autocomplete enable')

        # Verify status
        result = Tns.exec_command(command='autocomplete status')
        assert self.enabled in result.output

        # Disable autocomplete.
        result = Tns.exec_command(command='autocomplete disable')
        assert self.changed_to_disable in result.output

        # Verify status
        result = Tns.exec_command(command='autocomplete status')
        assert self.disabled in result.output

        # Enable again
        result = Tns.exec_command(command='autocomplete enable')
        assert self.changed_to_enable in result.output

        # Enable once again
        result = Tns.exec_command(command='autocomplete enable')
        assert self.already_enabled in result.output

    def test_400_autocomplete_invalid_parameter(self):
        result = Tns.exec_command(command='autocomplete fake')
        assert "This command doesn't accept parameters." in result.output
        assert "Run 'tns autocomplete --help' for more information." in result.output
