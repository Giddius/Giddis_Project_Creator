import configparser
import os
import gid_pack.gid_ssentials as gis


def add_new_type(triumvirate, in_type_name: str, in_type_short_name: str, in_type_comment: str):
    new_type = (in_type_name, in_type_short_name, in_type_comment)
    with triumvirate[0].opendb() as conn:
        conn.execute(triumvirate[0].sql_input['ins_template_type_tbl'], new_type)
        return f'{in_type_name} added as new type!'

# region [Class] v


class GiTemplateCrafter:

    def __init__(self, in_template_name: str, in_template_type: str, in_template_short_name: str, triumvirate):
        self.template_handle = configparser.ConfigParser()
        self.db_instance = triumvirate[0]
        self.solid_config = triumvirate[1]
        self.user_config = triumvirate[2]
        self.template_name = in_template_name
        self.template_short_name = in_template_short_name
        self.template_type = in_template_type
        self.prefix = self.get_prefix_data()
        self.template_folder_path = gis.pathmaker('cwd', self.solid_config.main_settings['template_folder'])
        self.template_blueprint = gis.pathmaker(self.template_folder_path, 'template_blueprint.ini')
        self.folder_dict = {}
        self.dummies_dict = {}
        self.boilers_dict = {}
        self.binary_boiler_dict = {}
        self.rename_dict = {}
        self.template_full_name = gis.underscore_maker(self.prefix, self.template_short_name, self.template_name)

    def get_prefix_data(self):
        with self.db_instance.opendb() as conn:
            conn.execute("SELECT template_type_short_name, template_type_name FROM template_type_tbl WHERE template_type_name = ?", (self.template_type,))
            _temp_prefix_main = []
            for rows in conn.fetchall():
                _temp_prefix_main.append(rows[0])

            prefix_main = _temp_prefix_main[0]

        return str(prefix_main)

    def add_folder(self, in_parent_folder, in_name):
        _folder = '${' + in_parent_folder + '}\\' + in_name
        self.folder_dict[in_name] = _folder

    def add_dummy(self, in_folder, in_name, in_extension):
        _dummie = '${folder:' + in_folder + '}\\' + in_name + '.' + in_extension
        self.dummies_dict[in_name + '__' + in_extension] = _dummie

    def add_boiler(self, in_folder, in_name, in_extension):
        _boiler = '${folder:' + in_folder + '}\\' + in_name + '.' + in_extension
        self.boilers_dict[in_name + '__' + in_extension] = _boiler

    def add_rename(self, original_name, new_name):
        self.rename_dict[original_name] = new_name

    def remove_from_dict(self, in_type, in_name, in_extension=None):

        if in_type == 'folder':
            _key = in_name
            del self.folder_dict[_key]


        elif in_type == 'boiler':
            _key = in_name + '__' + in_extension
            del self.boilers_dict[_key]

        elif in_type == 'dummy':
            _key = in_name + '__' + in_extension
            del self.dummies_dict[_key]

        return _key

    def create_ini(self):
        with open(self.template_blueprint, 'r') as blueprint_file:
            blueprint = blueprint_file.read()
        blueprint = blueprint.replace('_pct_PREFIX_pct_', self.prefix + '_' + self.template_short_name)
        blueprint = blueprint.replace('_pct_PROJECT_TYPE_pct_', self.template_type)
        with open(gis.pathmaker(self.template_folder_path, self.template_full_name + '.ini'), 'w') as new_template:
            new_template.write(f'{blueprint}\n\n')
        with open(gis.pathmaker(self.template_folder_path, self.template_full_name + '.ini'), 'a') as append_template:
            append_template.write('[folder]\n')
            for key, value in self.folder_dict.items():
                append_template.write(f'{key}: {value}\n')
            append_template.write('\n[dummies]\n')
            for key, value in self.dummies_dict.items():
                append_template.write(f'{key}: {value}\n')
            append_template.write('\n[boilers]\n')
            for key, value in self.boilers_dict.items():
                append_template.write(f'{key}: {value}\n')
            append_template.write('\n[renames]\n')
            for key, value in self.rename_dict.items():
                append_template.write(f'{key}: {value}\n')

    def save_to_db(self):
        with open(gis.pathmaker(self.template_folder_path, self.template_full_name + '.ini'), 'rb') as binary_template_file:
            binary_template = binary_template_file.read()
        new_template = (self.template_full_name, self.template_short_name, binary_template, self.template_type)
        with self.db_instance.opendb() as conn:
            conn.execute(self.db_instance.sql_input['ins_template_storage_tbl'], new_template)
            return f'template {self.template_full_name} saved to db!'

    def clear_dicts(self):
        self.folder_dict = {}
        self.dummies_dict = {}
        self.boilers_dict = {}
        self.binary_boiler_dict = {}

# endregion [Class] GiTemplateCrafter


# region [Class] BoilerWriter

class BoilerHandler:
    def __init__(self, triumvirate):
        self.db_instance = triumvirate[0]
        self.solid_config = triumvirate[1]
        self.user_config = triumvirate[2]
        self.boiler_folder_path = gis.pathmaker('cwd', self.solid_config.main_settings['boiler_folder'])
        self.boiler_dict = {}

    def get_all_boiler_in_folder(self, in_file_path=None):
        file_path = self.boiler_folder_path if in_file_path is None else in_file_path
        temp_list = []
        for root, dir, files in os.walk(file_path):
            for f in files:
                _temp_path = gis.pathmaker(root, f)
                if '.' in _temp_path:
                    temp_list.append(_temp_path)
        for files in temp_list:
            if '.' in files:
                with open(files, 'rb') as binary_boiler:
                    binary_data = binary_boiler.read()
                    file_name = gis.splitter(files, out_part='file')
                    file_name = file_name.replace('.', '__')
                    self.boiler_dict[file_name] = binary_data
        if self.boiler_dict != {}:
            _out = self.boilers_to_db()
        else:
            _out = 'no, boilers'
        return _out

    def add_boiler(self, in_file_path: str):
        file_name = gis.pathmaker(in_file_path, st_revsplit='split_getname')
        with open(gis.pathmaker(in_file_path), 'rb') as binary_boiler:
            binary_data = binary_boiler.read()
            file_name = file_name.replace('.', '__')
            self.boiler_dict[file_name] = binary_data
        _out = self.boilers_to_db()
        return _out

    def boilers_to_db(self):
        _outp = []
        with self.db_instance.opendb() as conn:
            for key, value in self.boiler_dict.items():
                conn.execute(self.db_instance.sql_input['ins_boiler_tbl'], (key, value))
                _outp.append(key)
        return f'{_outp} boiler inputed into db!'

# endregion [Class] BoilerWriter
