from pandas import read_excel

from model.mapping.group_views_model import get_nomenclatures_views
from model.mapping.mapping_model import get_nomenclatures_groups

FILE_PATH = "/home/syrnnik/Documents/Syrnnik/BandaWorks/Datastep/demo-backend/tests/[FOR TESTS] Classifier_ levelgroup enginerka test-cases.xlsx"
SHEET_NAME = "test-cases"
MODEL_ID = "local-syrnnik-new-dima-classifier"

noms_df = read_excel(FILE_PATH, sheet_name=SHEET_NAME)

noms_df['nomenclature'] = noms_df['Номенклатура поставщика']
noms_df['internal_group'] = get_nomenclatures_groups(noms_df, MODEL_ID)

noms_df = get_nomenclatures_views(noms_df)

noms_df.to_excel("./groups-and-views.xlsx", index=False)
