"""
    This file is part of ProfileSettingsDumper.

    ProfileSettingsDumper is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ProfileSettingsDumper is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with ProfileSettingsDumper. If not, see <https://www.gnu.org/licenses/>.
"""

from . import ProfileSettingsDumper


def getMetaData():
    return {
        'workspace_writer': {
            'output': [
                {
                    'description': 'Profile settings dumps',
                    'mime_type': 'text/plain',
                    'extension': 'dump',
                    'mode': ProfileSettingsDumper.ProfileSettingsDumper.OutputMode.TextMode,
                },
            ],
        },
    }


def register(app):
    return {'workspace_writer': ProfileSettingsDumper.ProfileSettingsDumper()}
