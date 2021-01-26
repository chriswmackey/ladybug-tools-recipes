from typing import Dict, List
from queenbee_dsl.dag import Inputs, DAG, task, Outputs
from dataclasses import dataclass
from pollination_dragonfly_energy.translate import ModelToHoneybee
from pollination_honeybee_energy.settings import SimParDefault
from pollination_honeybee_energy.simulate import SimulateModel
from pollination_honeybee_energy.result import EnergyUseIntensity


@dataclass
class DragonflyAnnualEnergyUseEntryPoint(DAG):
    """Dragonfly annual energy use entry point."""

    # inputs
    model = Inputs.file(
        description='A Dragonfly model in JSON file format.',
        extensions=['json', 'dfjson'],
    )

    epw = Inputs.file(
        description='EPW weather file to be used for the annual energy simulation.',
        extensions=['epw']
    )

    ddy = Inputs.file(
        description='A DDY file with design days to be used for the initial '
        'sizing calculation.', extensions=['ddy']
    )

    obj_per_model = Inputs.str(
        description='Text to describe how the input Model should be divided for '
        'parallel simulation. Choose from: District, Building, Story.', default='Story',
        spec={'type': 'string', 'enum': ['District', 'Building', 'Story']}
    )

    use_multiplier = Inputs.str(
        description='A switch to note whether the multipliers on each Building story '
        'should be passed along to the generated Honeybee Room objects or if full '
        'geometry objects should be written for each story of each dragonfly building.',
        default='full-geometry',
        spec={'type': 'string', 'enum': ['full-geometry', 'multiplier']}
    )

    shade_dist = Inputs.float(
        description='A number to note the distance beyond which other buildings shade '
        'should be excluded from a given Honeybee Model. This number should always be '
        'in meters regardless of the input Dragonfly model units. If 0, shade from all '
        'neighboring buildings will be excluded from the resulting models.', default=50
    )

    filter_des_days = Inputs.str(
        description='A switch for whether the ddy-file should be filtered to only '
        'include 99.6 and 0.4 design days', default='filter-des-days',
        spec={'type': 'string', 'enum': ['filter-des-days', 'all-des-days']}
    )

    units = Inputs.str(
        description='A switch to indicate whether the data in the final EUI file '
        'should be in SI (kWh/m2) or IP (kBtu/ft2). Valid values are "si" and "ip".',
        default='si', spec={'type': 'string', 'enum': ['si', 'ip']}
    )

    # tasks
    @task(template=ModelToHoneybee)
    def convert_to_honeybee(
        self, model=model, obj_per_model=obj_per_model,
        use_multiplier=use_multiplier, shade_dist=shade_dist
    ) -> List[Dict]:
        return [
            {
                'from': ModelToHoneybee()._outputs.output_folder,
                'to': 'models'
            },
            {
                'from': ModelToHoneybee()._outputs.hbjson_list,
                'description': 'Information about exported HBJSONs.'
            }
            ]

    @task(template=SimParDefault)
    def create_sim_par(self, ddy=ddy, filter_des_days=filter_des_days) -> List[Dict]:
        return [
            {'from': SimParDefault()._outputs.sim_par_json,
             'to': 'simulation_parameter.json'}
            ]

    @task(
        template=SimulateModel,
        needs=[create_sim_par, convert_to_honeybee],
        loop=convert_to_honeybee._outputs.hbjson_list,
        sub_folder='results',  # create a subfolder for results
        sub_paths={'model': '{{item.path}}'}  # sub_path for sim_par arg
    )
    def run_simulation(
        self, model=convert_to_honeybee._outputs.output_folder, epw=epw,
        sim_par=create_sim_par._outputs.sim_par_json
    ) -> List[Dict]:
        return [
            {'from': SimulateModel()._outputs.osm, 'to': 'osm/{{item.id}}.osm'},
            {'from': SimulateModel()._outputs.idf, 'to': 'idf/{{item.id}}.idf'},
            {'from': SimulateModel()._outputs.sql, 'to': 'sql/{{item.id}}.sql'},
            {'from': SimulateModel()._outputs.zsz, 'to': 'zsz/{{item.id}}_zsz.csv'},
            {'from': SimulateModel()._outputs.html, 'to': 'html/{{item.id}}.htm'},
            {'from': SimulateModel()._outputs.err, 'to': 'err/{{item.id}}.err'}
            ]

    @task(template=EnergyUseIntensity, needs=[run_simulation])
    def compute_eui(
        self, result_folder='results/sql', units=units
    ) -> List[Dict]:
        return [
            {'from': EnergyUseIntensity()._outputs.eui_json,
             'to': 'eui.json'}
            ]

    # outputs
    eui = Outputs.file(
        source='eui.json', description='A JSON containing energy use intensity '
        'information across the total model floor area. Values are either kWh/m2 '
        'or kBtu/ft2 depending upon the units input.'
    )

    hbjson = Outputs.folder(
        source='models',
        description='Folder containing the HBJSON models used for simulation.'
    )

    osm = Outputs.folder(
        source='results/osm', description='Folder containing the OpenStudio model.'
    )

    idf = Outputs.folder(
        source='results/idf', description='Folder containing the IDF models.'
    )

    sql = Outputs.folder(
        source='results/sql',
        description='Folder containing the result SQL files output by the simulation.'
    )

    zsz = Outputs.folder(
        source='results/zsz', description='Folder containing the CSV files with '
        'the zone loads over the design day.'
    )

    html = Outputs.folder(
        source='results/html',
        description='Folder containing the result HTML pages with summary reports.'
    )

    err = Outputs.folder(
        source='results/err',
        description='Folder containing the error reports output by the simulation.'
    )
