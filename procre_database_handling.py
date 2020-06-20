import gid_pack.gid_ssentials as gis


def database_create_connect(triumvirate, overwrite=False, real_overwrite=False):
    if triumvirate[0].start_db() is False:
        print('yes')
        make_needed_tables(triumvirate)

    else: print('no')

def make_needed_tables(triumvirate):
    _key_word_dict = {'cre_boiler_tbl': ('boiler_tbl', 'project_creator_storage'),
                      'cre_template_storage_tbl': ('template_storage_tbl', 'project_creator_storage'),
                      'cre_template_type_tbl': ('template_type_tbl', 'project_creator_attributes'),
                      'cre_blueprint_tbl': ('blueprint_tbl', 'hidden_storage')
                      }
    with triumvirate[0].opendb() as conn:
        for keywords, value_tup in _key_word_dict.items():
            conn.execute(triumvirate[0].sql_input[keywords])
            triumvirate[0].insert_to_toc(value_tup[0], value_tup[1])
        conn.execute(triumvirate[0].sql_input['ins_template_type_tbl'], ('default', 'def', 'default template type, should not be overly used'))
        with open(gis.pathmaker('cwd', 'ressources', 'archive', 'template_blueprint.ini'), 'rb') as bluefile:
            blue_bin = bluefile.read()
            conn.execute(triumvirate[0].sql_input['ins_blueprint_tbl'], ('blueprint', blue_bin))
        return 'created tables and default types'
