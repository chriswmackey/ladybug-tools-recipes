from .entry import DragonflyAnnualEnergyUseEntryPoint

__queenbee__ = {
    'name': 'dragonfly-annual-energy-use',
    'entry_point': DragonflyAnnualEnergyUseEntryPoint,
    'description': 'Run an annual energy simulation and compute energy use intensity for a Dragonfly model.',
    'icon': 'https://raw.githubusercontent.com/ladybug-tools/artwork/master/icons_components/honeybee/png/annualloads.png',
    'tag': '0.2.0',  # tag for dragonfly-energy plugin
    'app_version': '3.1.0',  # tag for version of Openstudio
    'keywords': ['dragonfly', 'energyplus', 'openstudio', 'ladybug-tools', 'energy'],
    'maintainers': [
        {'name': 'chris', 'email': 'chris@ladybug.tools'}
    ],
    'license': {
        'name': 'PolyForm Shield License 1.0.0',
        'url': 'https://polyformproject.org/wp-content/uploads/2020/06/PolyForm-Shield-1.0.0.txt'
    }
}
