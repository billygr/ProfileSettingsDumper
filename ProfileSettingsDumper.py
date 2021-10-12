"""
    ProfileSettingsDumper - A plugin for the Ultimaker Cura.
    It allows you to dump all profile settings of the current project
    into an INI-like file.

    Copyright (C) 2020 Vadim Kuznetsov <vimusov@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from collections import defaultdict
from configparser import ConfigParser
from datetime import datetime
from io import StringIO
from typing import Any, DefaultDict, Dict, List, Optional, Tuple

from cura.CuraApplication import CuraApplication
from cura.CuraVersion import CuraVersion
from cura.Settings import ExtruderStack, GlobalStack
from UM.Resources import Resources
from UM.Workspace.WorkspaceWriter import WorkspaceWriter


class Dumper:
    __VALUE_INDENT = ' ' * 4
    __MULTILINE_INDENT = __VALUE_INDENT * 2

    def __init__(self):
        self.__section = None  # type: Optional[str]
        self.__comments = []  # type: List[Tuple[str, Any]]
        self.__settings = dict()  # type: Dict[str, DefaultDict[str, List[str]]]

    def __format_value(self, name: str, value: str):
        value_indent = self.__VALUE_INDENT
        multiline_indent = self.__MULTILINE_INDENT
        header = '{value_indent}{name} = '.format(value_indent=value_indent, name=name)
        if ('\r' not in value) and ('\n' not in value):
            yield header + '{value}'.format(value=value)
            return
        yield header + '\\'
        for line in value.splitlines():
            if not line:
                continue
            yield '{multiline_indent}{line}'.format(multiline_indent=multiline_indent, line=line)

    def __format_settings(self):
        for name, comment in self.__comments:
            yield '; {name} = {comment!s}'.format(name=name, comment=comment)
        yield ''
        settings = self.__settings
        for section in sorted(settings):
            yield '[{section}]'.format(section=section)
            params = settings[section]  # type: DefaultDict[str, List[str]]
            for name in sorted(params):
                values = params[name]  # type: List[str]
                for value in values:
                    yield from self.__format_value(name, value)
            yield ''
        yield ''

    def add_comment(self, name: str, comment: Any):
        self.__comments.append((name, comment))

    def add_section(self, name: str):
        self.__section = name
        self.__settings.setdefault(name, defaultdict(list))

    def add_param(self, name: str, value: Any, unit: str):
        assert self.__section is not None
        pretty_value = '{value!s} {unit}'.format(value=value, unit=unit) if unit else str(value)
        self.__settings[self.__section][name].append(pretty_value)

    def save(self, stream: StringIO):
        stream.write('\n'.join(self.__format_settings()))


class ProfileSettingsDumper(WorkspaceWriter):
    @staticmethod
    def __dump_settings(dumper: Dumper, stack: ExtruderStack, key: str):
        name = stack.getProperty(key, 'label')
        value_type = stack.getProperty(key, 'type')
        if value_type == 'category':
            dumper.add_section(name)
            return
        raw_value = stack.getProperty(key, 'value')
        if value_type == 'float':
            value = '{raw_value:.4f}'.format(raw_value=raw_value).rstrip('0').rstrip('.')
        elif value_type == 'enum':
            choices = stack.getProperty(key, 'options')
            value = choices.get(raw_value, '<undefined>')
        else:
            value = raw_value
        dumper.add_param(name, value, stack.getProperty(key, 'unit'))

    def __dump_profile(self, dumper: Dumper, stack: ExtruderStack, key: str):
        self.__dump_settings(dumper, stack, key)
        for child in CuraApplication.getInstance().getGlobalContainerStack().getSettingDefinition(key).children:
            self.__dump_profile(dumper, stack, child.key)

    def __dump_machine(self, dumper: Dumper, stack: ExtruderStack, key: str):
        self.__dump_settings(dumper, stack, key)
        for child in stack.getSettingDefinition(key).children:
            self.__dump_machine(dumper, stack, child.key)

    def write(self, stream: StringIO, *unused_args, **unused_kwargs):
        machine = CuraApplication.getInstance().getMachineManager().activeMachine  # type: GlobalStack

        extruders = list(machine.extruders.values())
        extruder = extruders[0]  # type: ExtruderStack

        dumper = Dumper()
        dumper.add_comment('date', datetime.now().ctime())
        dumper.add_comment('version', CuraVersion)
        dumper.add_comment('quality', machine.quality.getMetaData().get('name', '[UNDEFINED QUALITY]'))
        dumper.add_comment('profile', machine.qualityChanges.getMetaData().get('name', '[UNDEFINED PROFILE]'))

        material_metadata = extruder.material.getMetaData()
        brand = material_metadata.get('brand', '[UNDEFINED BRAND]')
        material = material_metadata.get('material', '[UNDEFINED MATERIAL]')
        dumper.add_comment('filament', '{brand}/{material}'.format(brand=brand, material=material))

        machine_section = 'machine_settings'
        sections = {machine_section}
        excluded_sections = {'dual', 'general'}

        for file_path in Resources.getAllResourcesOfType(CuraApplication.ResourceTypes.SettingVisibilityPreset):
            try:
                with open(file_path, mode='rt') as preset_file:
                    parser = ConfigParser(interpolation=None, allow_no_value=True)
                    parser.read_file(preset_file)
                    sections.update(name for name in parser.sections() if name not in excluded_sections)
            except FileNotFoundError:
                pass

        for section in sections:
            self.__dump_profile(dumper, extruder, section)

        self.__dump_machine(dumper, extruder, machine_section)

        dumper.save(stream)
        return True
