import configparser
from configparser import ExtendedInterpolation
import os
import gid_pack.gid_ssentials as gis

import time

# region [Class] GiLoadedTemplate
# Bug: nameing underscores split names.
#TODO: rework naming and renaming of main folder
class GiLoadedTemplate:
    def __init__(self, in_template: str, in_project_name: str, object_triumvirate_list):
        self.db_instance = object_triumvirate_list[0]
        self.solid_config = object_triumvirate_list[1]
        self.user_config = object_triumvirate_list[2]
        self.template_handle = configparser.ConfigParser(interpolation=ExtendedInterpolation())
        self.template_handle.optionxform = lambda option: option
        self.temp_folder_name = gis.pathmaker('cwd', self.solid_config.main_settings['temp_folder'])
        self.project_name = in_project_name
        self.var_replace_dict = {'_pct_PROJECT_NAME_pct_': self.project_name}
        self.temp_file_path = gis.pathmaker('cwd', self.temp_folder_name, 'temp_' + self.project_name + '.ini')
        self.template_full_path = gis.pathmaker('cwd', gis.pathmaker('cwd', self.solid_config.main_settings['template_folder']), in_template)
        self.output_path = gis.pathmaker(self.user_config.from_user['output_location'])
        self.temp_process_template()
        self.project_main_folder = gis.pathmaker(self.read_template(in_section='folder', in_key='main_folder'))

    def check_if_already_exist(self):
        return os.path.exists(gis.pathmaker(self.output_path, self.project_main_folder))

    def read_template(self, in_section=None, in_key=None):
        """Generic function to read .ini file."""
        self.template_handle.read(self.temp_file_path)
        if in_section is None and in_key is None:
            _output = self.template_handle.sections()
        elif in_section is not None and in_key is None:
            _output = self.template_handle.items(in_section)
        elif in_section is not None and in_key is not None:
            _output = self.template_handle[in_section][in_key]
        return _output

    def temp_process_template(self):
        """reads template, replaces variables and writes temp template."""

        with open(self.template_full_path, 'r') as _template_file:
            _template_holder = _template_file.read()
            _template_holder = _template_holder.replace('_pct_PROJECT_NAME_pct_', self.project_name)
        with open(self.temp_file_path, 'w') as temp_template_file:
            temp_template_file.write(_template_holder)


    def create_folder(self):
        os.makedirs(gis.pathmaker(self.output_path, self.project_main_folder))
        for _key, value in self.read_template(in_section='folder'):
            if _key not in ['main_folder', 'project_name', 'project_type']:
                os.makedirs(gis.pathmaker(self.output_path, value))

    def create_dummies(self):
        if self.read_template(in_section='dummies') != {}:

            for _key, value in self.read_template(in_section='dummies'):
                if _key not in ['main_folder', 'project_name', 'project_type']:
                    with open(gis.pathmaker(self.output_path, value), 'w') as dummy_file:
                        dummy_file.write('This is a dummy file!\n\n')

        else:
            print('no dummies to make')


    def create_boilers(self):
        if self.read_template(in_section='boilers') != {}:

            for _key, value in self.read_template(in_section='boilers'):

                if _key not in ['main_folder', 'project_name', 'project_type']:
                    with self.db_instance.opendb() as conn:
                        conn.execute(self.db_instance.sql_query['sel_boiler'], (_key,))
                        _temp_boiler_file = conn.fetchone()

                    if self.read_template(in_section='renames', in_key=_key) != '':

                        _repl_key = _key.replace('__', '.')
                        _n_name = value.replace(_repl_key, self.read_template(in_section='renames', in_key=_key))
                    else:

                        _n_name = value
                    with open(gis.pathmaker(self.output_path, _n_name), 'wb') as boiler_file:
                        boiler_file.write(_temp_boiler_file[0])

        else:
            print('no boilers to make')

    def rename_main_folder_at_end(self):
        old_path = gis.pathmaker(self.output_path, self.project_main_folder)
        _is_split = self.project_main_folder.split('_', 2)

        _new_name = f'[{_is_split[0]}_{_is_split[1]}]_{_is_split[2]}'
        new_path = gis.pathmaker(self.output_path, _new_name)
        os.rename(old_path, new_path)

    def cleanup_temp_files(self):
        os.remove(self.temp_file_path)

    def create_whole_project(self):
        self.create_folder()
        time.sleep(3)
        self.create_dummies()
        time.sleep(3)
        self.create_boilers()
        time.sleep(3)
        self.cleanup_temp_files()
        time.sleep(3)
        self.rename_main_folder_at_end()

        return f'{self.project_main_folder} Project created in {self.output_path}'

    def __repr__(self):
        _template = gis.pathmaker(self.template_full_path, st_revsplit='split_getname')
        return f"GiLoadedTemplate '{_template}', '{self.output_path}', '{self.project_name}', '{self.temp_folder_name}'"

    def __str__(self):
        _template = gis.pathmaker(self.template_full_path, st_revsplit='split_getname')
        with open(self.temp_file_path, 'r') as temp_template_file:
            full_template = temp_template_file.read()
        return f"'{self.project_name}' from template '{_template}':\n\n\t'{full_template}'"

# endregion [Class] GiLoadedTemplate
