# TODO: popup when done creating folders and stuff


# region [Imports]

import os
import gid_pack.gid_ssentials as gis
import gid_pack.gid_qt as giq
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox, QTreeWidgetItem

import procre_database_handling as dh
import procre_template_reading as ptr
import procre_template_writing as ptw
import ui_conf_dialog as confgui
import ui_project_creator as basegui
import ui_Project_creator_style_rc
from ui_conf_dialog import Ui_Dialog as Form

# endregion [Imports]


def conspire_the_triumvirate(location='default', in_pragma=None):

    solid_pompey = gis.GiSolidConfig(location)
    user_crassus = gis.GiUserConfig(location)
    db_caesar = gis.GiDataBase(in_config_loc=location, in_pragma=in_pragma)
    return (db_caesar, solid_pompey, user_crassus)


class ProjectCreatorMainGUI(basegui.Ui_MainWindow):

    def __init__(self, MainWindow):
        super().setupUi(MainWindow)
        super().retranslateUi(MainWindow)

        self.triumvirate = conspire_the_triumvirate()
        self.db_tv = self.triumvirate[0]
        self.sc_tv = self.triumvirate[1]
        self.uc_tv = self.triumvirate[2]
        self.feedback(dh.database_create_connect(self.triumvirate))
        self.boiler_handler = ptw.BoilerHandler(self.triumvirate)
        self.popuper = giq.LittlePopuper()
        self.update_all()
        self.actions_section()
        self.line_empty_check()
        self.folder_icon = self.make_Icons(":/icon/ressources/icons/Folder_Classic_Yellow.ico", 1000, 1000)
        self.dummy_icon = self.make_Icons(":/icon/ressources/icons/Burn.ico", 100, 100)
        self.boiler_icon = self.make_Icons(":/icon/ressources/icons/Gear.ico", 100, 100)
        self.template_main_folder_created = False
        self.f_list = []
        self.d_list = []
        self.b_list = []

    def update_all(self):
        self.update_template_select_combo()
        self.update_template_type_combo()
        self.update_boiler_combo()

    def update_template_select_combo(self):
        giq.fill_combo_from_db(self.triumvirate, 'template_storage_tbl', 'template_storage_name', self.templateselect_combo)
        return 'templateselect_combo updated!'

    def update_template_type_combo(self):
        giq.fill_combo_from_db(self.triumvirate, 'template_type_tbl', 'template_type_name', self.newtemplate_type_combo)
        return 'template_type_combo updated!'

    def update_boiler_combo(self):
        giq.fill_combo_from_db(self.triumvirate, 'boiler_tbl', 'boiler_name', self.add_boiler_select_combo)
        return 'template_type_combo updated!'

    def line_empty_check(self):
        # region disable when lines empty
        self.newtemplate_name_lineinput.textChanged.connect(self.check_addmainfolder_button)
        self.newtemplate_shortname_lineinput.textChanged.connect(self.check_addmainfolder_button)

        self.foldername_lineinput.textChanged.connect(self.check_addfolder_button)

        self.dummyname_lineinput.textChanged.connect(self.check_adddummy_button)
        self.dummyextension_lineinput.textChanged.connect(self.check_adddummy_button)

        self.newtype_name_lineinput.textChanged.connect(self.check_newtype_button)
        self.newtype_shortname_lineinput.textChanged.connect(self.check_newtype_button)

        self.newboiler_filepath_lineinput.textChanged.connect(self.check_newboiler_button)

        self.projectname_lineinput.textChanged.connect(self.check_newproject_button)
        # endregion disable when lines empty

        # region button checks
    def check_addmainfolder_button(self):
        if self.template_main_folder_created is False:
            giq.enable_button(self.add_mainfolder_button, self.newtemplate_name_lineinput.text(), self.newtemplate_shortname_lineinput.text())

    def check_addfolder_button(self):
        giq.enable_button(self.addfolder_button, self.foldername_lineinput.text())

    def check_adddummy_button(self):
        giq.enable_button(self.adddummy_button, self.dummyname_lineinput.text(), self.dummyextension_lineinput.text())

    def check_addboiler_button(self):
        giq.enable_button(self.addboiler_button, self.boilername_lineinput.text(), self.boilerextension_lineinput.text())

    def check_newtype_button(self):
        giq.enable_button(self.create_newtype_button, self.newtype_name_lineinput.text(), self.newtype_shortname_lineinput.text())

    def check_newboiler_button(self):
        giq.enable_button(self.newboiler_createboiler_button, self.newboiler_filepath_lineinput.text())

    def check_newproject_button(self):
        giq.enable_button(self.createproject_button, self.projectname_lineinput.text())
        # endregion button checks



    def actions_section(self):
        # region actions
        self.create_newtype_button.pressed.connect(self.create_newtype_validator)
        self.newboiler_createboiler_button.pressed.connect(self.create_newboiler_validator)
        self.newboiler_selectfile_toolbutton.pressed.connect(self.boiler_filedialog)
        self.actionclear_DB_and_overwrite.triggered.connect(self.whole_db_drop_ask_I)
        self.add_mainfolder_button.pressed.connect(self.set_template_main_folder)
        self.addfolder_button.pressed.connect(self.template_add_folder_to_tree)
        self.delete_template_item.pressed.connect(self.delete_tree_item)
        self.newboiler_createfromfolder_checkbox.stateChanged.connect(self.newboiler_filepath_lineinput.clear)
        self.template_clear_all_button.pressed.connect(self.make_sure_clear_tree)
        self.delete_mode_checkbox.toggled.connect(self.check_deletebox)
        self.delete_template_checkbox.toggled.connect(self.fill_delete_combo)
        self.delete_type_checkbox.toggled.connect(self.fill_delete_combo)
        self.delete_boiler_checkbox.toggled.connect(self.fill_delete_combo)
        self.pushButton.pressed.connect(self.make_sure_delete)
        self.addboiler_button.pressed.connect(self.boiler_to_tree)
        self.adddummy_button.pressed.connect(self.dummy_to_tree)
        self.writetemplate_button.pressed.connect(self.parse_the_tree)
        self.createproject_button.pressed.connect(self.build_the_project_ask)
        self.actionconfigurator.triggered.connect(self.open_configurator)
        # endregion actions

    def open_configurator(self):
        dialog = QtWidgets.QDialog()
        dialog.ui = Form()
        dialog.ui.setupUi(dialog)
        dialog.exec_()

    def get_blueprint(self):
        with self.db_tv.opendb() as conn:
            conn.execute("SELECT * FROM blueprint_tbl")
            blueprint = conn.fetchone()
        with open(gis.pathmaker('cwd', self.sc_tv.main_settings['template_folder'], 'template_' + blueprint[1] + '.ini'), 'wb') as bluebinfile:
            bluebinfile.write(blueprint[2])

    def get_all_templates(self):

        with self.db_tv.opendb() as conn:
            conn.execute("SELECT template_storage_name, template_data FROM template_storage_tbl")
            _templates_tup = conn.fetchall()
        for templates in _templates_tup:
            with open(gis.pathmaker('cwd', self.sc_tv.main_settings['template_folder'], templates[0] + '.ini'), 'wb') as binfile:
                binfile.write(templates[1])

    def build_the_project_ask(self):
        self.popuper.warning_dialog('Do you really want to create this Project', '', self.build_the_project)

    def build_the_project(self):
        self.get_all_templates()
        _main_name = self.projectname_lineinput.text()
        _project_template = self.templateselect_combo.currentText() + '.ini'
        project = ptr.GiLoadedTemplate(_project_template, _main_name, self.triumvirate)
        if project.check_if_already_exist() is True:
            self.popuper.error_dialog('Project already exists','Projects need unique names, the prefix is disregarded for this')
        else:
            project.create_whole_project()
            self.feedback('new Project created')
            self.remove_files_again()


    def remove_files_again(self):
        _f_list = os.listdir(gis.pathmaker('cwd', self.sc_tv.main_settings['template_folder']))
        for files in _f_list:
            os.remove(gis.pathmaker('cwd', self.sc_tv.main_settings['template_folder'], files))
        print('files removed')


    def make_sure_clear_tree(self):
        self.popuper.warning_dialog('Do you really want to clear the Tree?', 'this cannot be reversed', self.clear_whole_tree)


    def parse_the_tree(self):
        self.get_blueprint()
        tree_iterator = QtWidgets.QTreeWidgetItemIterator(self.createtemplate_treewidget)
        while tree_iterator.value():
            item = tree_iterator.value()
            _parent = item.parent()

            if _parent is not None:
                if _parent.text(0) == self.cur_crafter.template_full_name:
                    _parent_name = 'main_folder'
                else:
                    _parent_name = _parent.text(0)
                if item.text(1) == 'folder':
                    self.cur_crafter.add_folder(_parent_name, item.text(0))
                elif item.text(1) == 'dummy':
                    _name = item.text(0).split('__')
                    self.cur_crafter.add_dummy(_parent_name, _name[0], _name[1])
                elif item.text(1) == 'boiler':
                    if '--' in item.text(0):
                        _t_name = item.text(0).split('--')
                    else:
                        _t_name = ['', item.text(0)]
                    _f_name = _t_name[1].split('__')
                    _name = _f_name[0].replace('[', '')
                    _ext = _f_name[1].replace(']', '')
                    _o_name = f'{_name}__{_ext}'
                    _n_name = _t_name[0]

                    self.cur_crafter.add_boiler(_parent_name, _name, _ext)
                    self.cur_crafter.add_rename(_o_name, _n_name)

            tree_iterator += 1
        self.createtemplate_treewidget.clear()
        self.newtemplate_name_lineinput.clear()
        self.newtemplate_shortname_lineinput.clear()
        self.display_template_mainfolder_lineedit.clear()
        self.template_main_folder_created = False

        self.create_the_template()

    def create_the_template(self):
        self.cur_crafter.create_ini()
        if self.writetemplate_onlylocal_check.isChecked() is False:
            self.cur_crafter.save_to_db()
        self.cur_crafter.clear_dicts()
        self.update_all()
        self.feedback('new template created')

    def dummy_to_tree(self):
        _ext = self.dummyextension_lineinput.text()
        _name = self.dummyname_lineinput.text() + '__' + _ext
        _parent = self.createtemplate_treewidget.currentItem()
        if _parent is None:
            self.popuper.error_dialog('you need to select a parent folder','')
        else:

            if _name in self.d_list:
                self.popuper.error_dialog('Boiler already exists', '')
            else:
                _type = 'dummy'
                self.set_tree_item(_name, _type, _parent)



    def boiler_to_tree(self):
        _rename_name = self.boiler_rename_line_edit.text()
        _saved_name = self.add_boiler_select_combo.currentText()
        _name = f'{_rename_name}--[{_saved_name}]' if _rename_name != '' else _saved_name
        _parent = self.createtemplate_treewidget.currentItem()
        if _parent is None:
            self.popuper.error_dialog('you need to select a parent folder','')
        else:

            if _rename_name != '' and _rename_name in self.b_list:
                self.popuper.error_dialog('Boiler already exists', '')
            elif _rename_name == '' and _saved_name in self.b_list:
                self.popuper.error_dialog('Boiler already exists', '')
            else:
                _type = 'boiler'
                self.set_tree_item(_name, _type, _parent)



    def make_sure_delete(self):
        _message ='Do you really want to delete this item from the db?\n This cannot be reversed!'
        _detail_message = ''
        self.popuper.warning_dialog(_message, _detail_message, self.delete_item)

    def delete_item(self):
        _item = self.comboBox.currentText()
        if self.delete_template_checkbox.isChecked():
            _q_var = ('template_storage_tbl', 'template_storage_name')
        elif self.delete_type_checkbox.isChecked():
            _q_var = ('template_type_tbl', 'template_type_name')
        elif self.delete_boiler_checkbox.isChecked():
            _q_var = ('boiler_tbl', 'boiler_name')
        _sql = f"DELETE FROM {_q_var[0]} WHERE {_q_var[1]} = '{_item}'"
        with self.db_tv.opendb() as conn:
            conn.execute(_sql)
        self.feedback(f"deleted item {_item} form db")
        self.check_deletebox()
        self.fill_delete_combo()
        self.update_all()

    def fill_delete_combo(self):
        self.comboBox.clear()
        self.comboBox.setEnabled(False)
        self.pushButton.setEnabled(False)
        if self.delete_template_checkbox.isChecked():
            _q_var = 'template'
        elif self.delete_type_checkbox.isChecked():
            _q_var = 'template_type'
        elif self.delete_boiler_checkbox.isChecked():
            _q_var = 'boiler'

        _items = self.get_item_from_db(_q_var)
        for item in _items:
            self.comboBox.addItem(item[0])
        if self.comboBox.count() != 0:
            self.comboBox.setEnabled(True)
            self.pushButton.setEnabled(True)

    def get_item_from_db(self, in_type):
        if in_type == 'template':
            _sql_vars = ('template_storage_tbl', 'template_storage_name', 'template_storage_short_name')
        elif in_type == 'template_type':
            _sql_vars = ('template_type_tbl', 'template_type_name', 'template_type_short_name')
        elif in_type == 'boiler':
            _sql_vars = ('boiler_tbl', 'boiler_name', 'not_provided')
        _sql = f"SELECT {_sql_vars[1]}, {_sql_vars[2]} FROM {_sql_vars[0]}"
        _sql = _sql.replace(', not_provided', '')
        with self.db_tv.opendb() as conn:
            conn.execute(_sql)
            _output = conn.fetchall()

        return _output

    def check_deletebox(self):

        self.comboBox.setEnabled(False)
        self.pushButton.setEnabled(False)
        self.delete_template_checkbox.setEnabled(False)
        self.delete_type_checkbox.setEnabled(False)
        self.delete_boiler_checkbox.setEnabled(False)
        if self.delete_mode_checkbox.isChecked():


            _available_templates =  self.get_item_from_db('template')
            _available_types = self.get_item_from_db('template_type')
            _available_boilers = self.get_item_from_db('boiler')

            if _available_templates != []:
                self.delete_template_checkbox.setEnabled(True)
                self.pushButton.setEnabled(True)
                self.comboBox.setEnabled(True)
            if _available_types != []:
                self.delete_type_checkbox.setEnabled(True)
                self.pushButton.setEnabled(True)
                self.comboBox.setEnabled(True)
            if _available_boilers != []:
                self.delete_boiler_checkbox.setEnabled(True)
                self.pushButton.setEnabled(True)
                self.comboBox.setEnabled(True)


    def clear_whole_tree(self):
        self.createtemplate_treewidget.clear()
        self.display_template_mainfolder_lineedit.clear()
        self.add_mainfolder_button.setEnabled(True)
        self.newtemplate_type_combo.setEnabled(True)
        self.writetemplate_button.setEnabled(False)
        self.update_all()


    def delete_tree_item(self):
        _item = self.createtemplate_treewidget.currentItem()
        if _item.text(0) == self.cur_crafter.template_full_name:
            self.popuper.error_dialog('you cannot delete the main folder in a template this way',
                                      'To delete the main folder you have to clear the whole template with the clear all button')
        else:
            _name = _item.text(0)
            _item.parent().removeChild(_item)
            if _item.text(1) == 'folder':
                self.f_list.remove(_name)
            elif _item.text(1) == 'dummy':
                self.d_list.remove(_name)
            elif _item.text(1) == 'boiler':
                self.b_list.remove(_name)
            self.feedback(f'{_name} is removed from the template')
            self.update_all()

    def template_add_folder_to_tree(self):

        _name = self.foldername_lineinput.text()
        _parent = self.createtemplate_treewidget.currentItem()
        if _parent is None:
            self.popuper.error_dialog('you need to select a parent folder')
        else:

            if _name in self.f_list:
                self.popuper.error_dialog('folder with this name already exist')
            else:
                _type = 'folder'
                self.set_tree_item(_name, _type, _parent)
                self.update_all()

    def set_template_main_folder(self):
        _template_name = self.newtemplate_name_lineinput.text()
        _template_short = self.newtemplate_shortname_lineinput.text()
        _template_type = self.newtemplate_type_combo.currentText()

        if self.is_it_unique('template', _template_name, _template_short) is False:
            self.popuper.error_dialog('Template Name or Template Short Name already EXISTS!', 'Please choose a different Name and/or Short Name.\nExistence is checked over all types.',)
        else:
            self.cur_crafter = ptw.GiTemplateCrafter(_template_name, _template_type, _template_short, self.triumvirate)
            self.display_template_mainfolder_lineedit.setText(self.cur_crafter.template_full_name)

            b_item = self.set_tree_item(self.cur_crafter.template_full_name, in_type='folder', in_parent=self.createtemplate_treewidget, accept_top=True)
            self.update_all()
            self.writetemplate_button.setEnabled(True)


    def set_tree_item(self, in_name, in_type, in_parent, accept_top=False):
        _name = str(in_name)
        if accept_top is False and in_parent == '':
            _parent = self.cur_crafter.template_full_name
        elif accept_top is False and in_parent == self.createtemplate_treewidget:
            _parent = self.cur_crafter.template_full_name
        else:
            _parent = in_parent

        _name = QTreeWidgetItem(_parent)
        if in_type == 'folder':
            _name.setIcon(0, self.folder_icon)
            self.f_list.append(in_name)
        elif in_type == 'dummy':
            _name.setIcon(0, self.dummy_icon)
            self.d_list.append(in_name)
        elif in_type == 'boiler':
            _name.setIcon(0, self.boiler_icon)
            self.b_list.append(in_name)

        _name.setText(0, in_name)
        _name.setText(1, in_type)
        _name.setFirstColumnSpanned(True)
        _name.setExpanded(True)
        if accept_top is True:
            self.template_main_folder_created = True
            self.add_mainfolder_button.setEnabled(False)
            self.newtemplate_type_combo.setEnabled(False)



        return _name

    def make_Icons(self, in_path, in_size_1, in_size_2):
        Icon = QtGui.QIcon()
        Icon.addFile(in_path, size=QtCore.QSize(in_size_1, in_size_2), state=QIcon.On)
        return Icon

    def is_it_unique(self, in_type, in_name, in_secondary):

        _type_dict = dict(template="SELECT template_storage_name, template_storage_short_name FROM template_storage_tbl",
                          template_type="SELECT template_type_name, template_type_short_name FROM template_type_tbl",
                          boiler="SELECT boiler_name, boiler_data FROM boiler_tbl")

        for key, value in _type_dict.items():
            if in_type == key:
                _sql = value
        _check_dup_sum = 0
        with self.db_tv.opendb() as conn:
            conn.execute(_sql)
            for rows in conn.fetchall():
                if in_name == rows[0]:
                    _check_dup_sum += 1
                if in_secondary == rows[1]:
                    _check_dup_sum += 1
        if _check_dup_sum == 0:
            _output = True
        else:
            _output = False
        return _output

    def whole_db_drop_ask_I(self):
        _message ='Do you really want to DELETE the whole DB and create a new one from scratch?'
        _detail_message = 'This action will destroy all inputs, types, templates, and everything'
        self.popuper.warning_dialog(_message, _detail_message, self.whole_db_drop_ask_II)

    def whole_db_drop_ask_II(self):
        _message ='Are you REALLY SURE, an backup of the old DB will be attempted but could fail?'
        _path = gis.pathmaker(self.db_tv.db_archive_loc, st_revsplit='rev')
        _detail_message = f"if the backup succeds you can find it in [{_path}]"
        self.popuper.warning_dialog(_message, _detail_message, self.drop_whole_db)

    def drop_whole_db(self):
        dh.database_create_connect(self.triumvirate, overwrite=True, real_overwrite=True)
        self.feedback('database dropped and new created')

        self.update_all()

    def feedback(self, in_message):
        self.action_feedback_lineoutput.setText(in_message)

    def boiler_filedialog(self):
        if self.newboiler_createfromfolder_checkbox.isChecked() is True:
            giq.as_filedialog(in_type='directory', in_title='Open folder', in_dir=None, in_filter_name=None, in_ext=None, in_output_object=self.newboiler_filepath_lineinput.setText)
        if self.newboiler_createfromfolder_checkbox.isChecked() is False:
            giq.as_filedialog(in_title='Open as Boiler File', in_dir=None, in_filter_name=None, in_ext=None, in_output_object=self.newboiler_filepath_lineinput.setText)


    def create_newtype_validator(self):
        _name = self.newtype_name_lineinput.text()
        _short_name = self.newtype_shortname_lineinput.text()
        _comment = self.newtype_comments_lineinput.text()
        self.feedback(ptw.add_new_type(self.triumvirate, _name, _short_name, _comment))
        self.update_all()


    def create_newboiler_validator(self):
        _path = gis.pathmaker(self.newboiler_filepath_lineinput.text())
        if os.path.exists(_path) is False:
            self.popuper.error_dialog('file not found', 'there is no file/folder at the path you specified!')
        elif self.newboiler_createfromfolder_checkbox.isChecked() is True:
            self.feedback(self.boiler_handler.get_all_boiler_in_folder(_path))
            self.newboiler_filepath_lineinput.clear()
        else:
            self.feedback(self.boiler_handler.add_boiler(_path))
            self.newboiler_filepath_lineinput.clear()
        self.update_all()




if __name__ == "__main__":
    import sys
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = ProjectCreatorMainGUI(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
