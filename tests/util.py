# -*- coding: utf-8 -*-
import io

import pandas as pd
from urllib3.response import HTTPResponse

IRIS_DATASET_NAME = "iris.csv"

IRIS_DATA = (
    "SepalLengthCm,SepalWidthCm,PetalLengthCm,PetalWidthCm,Species\n"
    "5.1,3.5,1.4,0.2,Iris-setosa\n"
    "4.9,3.0,1.4,0.2,Iris-setosa\n"
    "4.7,3.2,1.3,0.2,Iris-setosa\n"
    "4.6,3.1,1.5,0.2,Iris-setosa\n"
)

IRIS_DATA_HEADERLESS = (
    "5.1,3.5,1.4,0.2,Iris-setosa\n"
    "4.9,3.0,1.4,0.2,Iris-setosa\n"
    "4.7,3.2,1.3,0.2,Iris-setosa\n"
    "4.6,3.1,1.5,0.2,Iris-setosa\n"
)

IRIS_DATA_ARRAY = [
    [5.1, 3.5, 1.4, 0.2, "Iris-setosa"],
    [4.9, 3.0, 1.4, 0.2, "Iris-setosa"],
    [4.7, 3.2, 1.3, 0.2, "Iris-setosa"],
    [4.6, 3.1, 1.5, 0.2, "Iris-setosa"],
]

IRIS_COLUMNS = [
    "SepalLengthCm",
    "SepalWidthCm",
    "PetalLengthCm",
    "PetalWidthCm",
    "Species",
]

IRIS_HEADERLESS_COLUMNS = ["col0", "col1", "col2", "col3", "col4"]

IRIS_FEATURETYPES = [
    "Numerical",
    "Numerical",
    "Numerical",
    "Numerical",
    "Categorical",
]

IRIS_FEATURETYPES_FILE = "Numerical\nNumerical\nNumerical\nNumerical\nCategorical\n"

IRIS_COLUMNS_FEATURETYPES = [
    {"featuretype": "Numerical", "name": "SepalLengthCm"},
    {"featuretype": "Numerical", "name": "SepalWidthCm"},
    {"featuretype": "Numerical", "name": "PetalLengthCm"},
    {"featuretype": "Numerical", "name": "PetalWidthCm"},
    {"featuretype": "Categorical", "name": "Species"},
]

IRIS_HEADERLESS_COLUMNS_FEATURETYPES = [
    {"featuretype": "Numerical", "name": "col0"},
    {"featuretype": "Numerical", "name": "col1"},
    {"featuretype": "Numerical", "name": "col2"},
    {"featuretype": "Numerical", "name": "col3"},
    {"featuretype": "Categorical", "name": "col4"},
]

IRIS_DATAFRAME = pd.DataFrame(IRIS_DATA_ARRAY, columns=IRIS_COLUMNS)

PNG_DATASET_NAME = "text.png"

PNG_DATA = open(f"tests/resources/{PNG_DATASET_NAME}", "rb").read()

FILE_NOT_FOUND_ERROR = FileNotFoundError("The specified dataset does not exist")

# PREDICT FILE
PREDICT_FILE = "predict-file.csv"

PREDICT_FILE_HEADER = open(f"tests/resources/{PREDICT_FILE}", "rb")

PREDICT_HEADERLESS = "predict-file-headerless.csv"

PREDICT_FILE_HEADERLESS = open(f"tests/resources/{PREDICT_HEADERLESS}", "rb")

PREDICT_COLUMNS = [
    "Lote",
    "Fazenda",
    "Cultura",
    "Armazem de envase",
    "Cor",
    "Agua",
    "Glicose",
    "Frutose",
    "Sacarore",
    "Maltose",
    "Gluconolactona",
    "Acido Gluconico",
    "Acidez",
    "Nitrogenio",
    "Cinzas",
    "PH",
    "Minerais",
    "Aminoacidos",
    "Indice de formol",
    "Condutividade eletrica",
    "Metais pesados",
    "Antibioticos",
    "Nivel de alcaloides",
    "RFClassifier_predict_proba_Altera__es_discrepantes",
    "RFClassifier_predict_proba_Levemente_Alterado",
    "RFClassifier_predict_proba_Normal",
    "RFClassifier_predict_class",
]

PREDICT_FEATURETYPES = [
    "Categorical",
    "Categorical",
    "Categorical",
    "Categorical",
    "Categorical",
    "Categorical",
    "DateTime",
    "DateTime",
    "DateTime",
    "DateTime",
    "Categorical",
    "Categorical",
    "DateTime",
    "Categorical",
    "Categorical",
    "DateTime",
    "DateTime",
    "Categorical",
    "DateTime",
    "DateTime",
    "Categorical",
    "Categorical",
    "Categorical",
    "Categorical",
    "Categorical",
    "DateTime",
    "Categorical",
]

PREDICT_FILE_COLUMNS = [
    {'name': 'Lote', 'featuretype': 'Categorical'},
    {'name': 'Fazenda', 'featuretype': 'Categorical'},
    {'name': 'Cultura', 'featuretype': 'Categorical'},
    {'name': 'Armazem de envase', 'featuretype': 'Categorical'},
    {'name': 'Cor', 'featuretype': 'Categorical'},
    {'name': 'Agua', 'featuretype': 'Categorical'},
    {'name': 'Glicose', 'featuretype': 'DateTime'},
    {'name': 'Frutose', 'featuretype': 'DateTime'},
    {'name': 'Sacarore', 'featuretype': 'DateTime'},
    {'name': 'Maltose', 'featuretype': 'DateTime'},
    {'name': 'Gluconolactona', 'featuretype': 'Categorical'},
    {'name': 'Acido Gluconico', 'featuretype': 'Categorical'},
    {'name': 'Acidez', 'featuretype': 'DateTime'},
    {'name': 'Nitrogenio', 'featuretype': 'Categorical'},
    {'name': 'Cinzas', 'featuretype': 'Categorical'},
    {'name': 'PH', 'featuretype': 'DateTime'},
    {'name': 'Minerais', 'featuretype': 'DateTime'},
    {'name': 'Aminoacidos', 'featuretype': 'Categorical'},
    {'name': 'Indice de formol', 'featuretype': 'DateTime'},
    {'name': 'Condutividade eletrica', 'featuretype': 'DateTime'},
    {'name': 'Metais pesados', 'featuretype': 'Categorical'},
    {'name': 'Antibioticos', 'featuretype': 'Categorical'},
    {'name': 'Nivel de alcaloides', 'featuretype': 'Categorical'},
    {'name': 'RFClassifier_predict_proba_Altera__es_discrepantes', 'featuretype': 'Categorical'},
    {'name': 'RFClassifier_predict_proba_Levemente_Alterado', 'featuretype': 'Categorical'},
    {'name': 'RFClassifier_predict_proba_Normal', 'featuretype': 'DateTime'},
    {'name': 'RFClassifier_predict_class', 'featuretype': 'Categorical'},
]

PREDICT_FILE_COLUMNS_HEADERLESS = [
    {'name': 'col0', 'featuretype': 'Categorical'},
    {'name': 'col1', 'featuretype': 'Categorical'},
    {'name': 'col2', 'featuretype': 'Categorical'},
    {'name': 'col3', 'featuretype': 'Categorical'},
    {'name': 'col4', 'featuretype': 'Categorical'},
    {'name': 'col5', 'featuretype': 'Categorical'},
    {'name': 'col6', 'featuretype': 'DateTime'},
    {'name': 'col7', 'featuretype': 'DateTime'},
    {'name': 'col8', 'featuretype': 'DateTime'},
    {'name': 'col9', 'featuretype': 'DateTime'},
    {'name': 'col10', 'featuretype': 'Categorical'},
    {'name': 'col11', 'featuretype': 'Categorical'},
    {'name': 'col12', 'featuretype': 'DateTime'},
    {'name': 'col13', 'featuretype': 'Categorical'},
    {'name': 'col14', 'featuretype': 'Categorical'},
    {'name': 'col15', 'featuretype': 'DateTime'},
    {'name': 'col16', 'featuretype': 'DateTime'},
    {'name': 'col17', 'featuretype': 'Categorical'},
    {'name': 'col18', 'featuretype': 'DateTime'},
    {'name': 'col19', 'featuretype': 'DateTime'},
    {'name': 'col20', 'featuretype': 'Categorical'},
    {'name': 'col21', 'featuretype': 'Categorical'},
    {'name': 'col22', 'featuretype': 'Categorical'},
    {'name': 'col23', 'featuretype': 'Categorical'},
    {'name': 'col24', 'featuretype': 'Categorical'},
    {'name': 'col25', 'featuretype': 'DateTime'},
    {'name': 'col26', 'featuretype': 'Categorical'},
]

PREDICT_COLUMNS_HEADERLESS = [
    "col0",
    "col1",
    "col2",
    "col3",
    "col4",
    "col5",
    "col6",
    "col7",
    "col8",
    "col9",
    "col10",
    "col11",
    "col12",
    "col13",
    "col14",
    "col15",
    "col16",
    "col17",
    "col18",
    "col19",
    "col20",
    "col21",
    "col22",
    "col23",
    "col24",
    "col25",
    "col26",
]

PREDICT_FILE_DATA = [
    ['ID_6488',"Jardim d'Oeste",'Girassol','Avohai','Branco',"24,268","28,02","38,43","1,35","7,3","0,14","0,22","26,85","0,04","0,2117","3,9","1,3057","0,420784207","8,08","282,8","0,083158128","5,32e-05","210,58571579",'0','0','1','Normal'],
    ['ID_5923',"Jardim d'Oeste",'Girassol','Benemel','Âmbar extra claro','17,505','33,17','38,06','2,97','7,61','0,13','0,26','25,14','0,05','0,0978','3,8','1,1075','0,429064465','2,78','924,51','0,000103015','5,66e-05','87,95395221399998','0','0','1','Normal'],
    ['ID_5320',"Jardim d'Oeste",'Girassol','Mel e Cia','Âmbar extra claro','19,966','28,51','43,34','1,53','6,04','0,15','0,24','15,25','0,03','0,3365','3,6','1,3847','0,37420626','5,46','1172,07','9,62e-05','5,35e-05','140,962235726','0','0','1','Normal'],
    ['ID_183',"Jardim d'Oeste",'Girassol','Só Mel','Âmbar extra claro','25,144','28,26','38,21','1,09','6,67','0,31','0,22','29,63','0,05','0,2003','4,3','1,3516','0,408228646','1,84','1261,98','0,04223076','5,86e-05','478,28878503','0,2','0,8','0','Levemente Alterado'],
    ['ID_1281','Mangueirinha','Eucalipto','Avohai','Âmbar','22,062','33,21','34,58','2,48','7,25','0,15','0,37','36,8','0,04','0,4366','4,1','1,21','0,061603378','3,29','910,32','0,105298721','0,03869822','183,75845638','0','0','1','Normal'],
    ['ID_6689','Mangueirinha','Eucalipto','Avohai','Âmbar','16,504','34,03','39,65','0,63','8,53','0,13','0,38','34,12','0,04','0,4622','3,5','1,5412','0,2682812','8,07','313,8','0,088046702','0,038668998','114,258990033','0','0','1','Normal'],
    ['ID_9159','Mangueirinha','Eucalipto','Benemel','Âmbar','25,955','28,53','37,2','1,48','6,08','0,29','0,4','37,11','0,04','0,023','4,3','0,9773','0,352995272','11,78','265,37','9,9e-05','0,034730791','502,4476453','0,2','0,8','0','Levemente Alterado'],
    ['ID_4575','Mangueirinha','Eucalipto','Mel e Cia','Âmbar','29,628','29,95','32,05','1,41','6,32','0,26','0,48','16,49','0,04','0,221','3,7','0,8993','0,156104334','8,97','335,69','0,000112067','0,037726252','516,25083409','0','0','1','Normal'],
    ['ID_5995','Mangueirinha','Eucalipto','Só Mel','Âmbar claro','16,848','34,17','41,66','0,37','6,29','0,15','0,41','30,34','0,05','0,3443','3,6','1,2142','0,251900946','6,75','605,27','0,039102347','0,033876106','141,03050169','0','0','1','Normal'],
    ['ID_5558','Mangueirinha','Floresta','Avohai','Âmbar claro','26,354','26,23','38,22','1,04','7,61','0,24','0,27','13,25','0,05','0,3355','4,3','1,5636','0,283045619','8,2','342,02','0,094240348','0,034382335','419,4616270900001','0,3','0,6','0,1','Levemente Alterado'],
    ['ID_8887','Mangueirinha','Floresta','Benemel','Âmbar claro','21,695','30,65','39,47','0,22','7,38','0,12','0,38','18,4','0,03','0,1036','3,6','1,4206','0,211011309','6,06','784,95','0,0001007','0,032706972','144,70284354199998','0','0','1','Normal'],
    ['ID_7706','Mangueirinha','Floresta','Mel e Cia','Âmbar claro','23,114','32,43','36,64','1,16','6,03','0,09','0,32','25,8','0,04','0,7407','4,3','2,0632','0,295303862','3,05','282,36','9,29e-05','0,039794193','185,07742382','0','0','1','Normal'],
    ['ID_2000','Mangueirinha','Floresta','Só Mel','Âmbar claro','22,301','28,61','39,74','1,64','7,17','0,12','0,38','18,11','0,04','0,3821','4,1','1,2793','0,153209661','2,59','328,04','0,042854434','0,036675626','177,06612285','0','0','1','Normal'],
    ['ID_1235','Morro da Colméia','Urze','Avohai','Escuro','21,284','29,62','39,6','1,82','7,23','0,16','0,15','23,04','0,04','0,4627','4,0','1,5257','0,298164624','3,04','1083,52','0,096544125','5,22e-05','158,64731693999997','0','0','1','Normal'],
    ['ID_5361','Morro da Colméia','Urze','Benemel','Escuro','28,931','26,97','36,44','0,74','6,44','0,23','0,15','21,66','0,03','0,3797','3,3','1,5508','0,329418586','6,19','361,36','8,6e-05','4,61e-05','557,6605173700001','0,1','0','0,9','Normal'],
    ['ID_5652','Morro da Colméia','Urze','Só Mel','Escuro','26,731','24,89','38,69','1,91','7,32','0,24','0,16','24,65','0,03','0,3713','4,9','1,4519','0,302534148','14,12','970,79','0,036208923','4,7e-05','542,3354282500001','0,6','0,3','0,1','Alterações discrepantes'],
    ['ID_1208','Vereda Tropical','Flor de Laranjeira','Avohai','Âmbar extra claro','19,77','32,68','39,31','0,79','7,06','0,15','0,23','25,44','0,04','0,3684','4,4','1,6874','0,15271364','2,85','335,36','0,100138126','4,63e-05','178,01967715','0','0','1','Normal'],
    ['ID_2658','Vereda Tropical','Flor de Laranjeira','Benemel','Âmbar extra claro','20,879','28,92','41,39','0,46','7,94','0,13','0,25','26,5','0,04','0,3961','3,9','1,6969','0,161944349','7,32','592,97','9,36e-05','3,89e-05','147,1651059','0','0','1','Normal'],
    ['ID_4587','Vereda Tropical','Flor de Laranjeira','Mel e Cia','Âmbar extra claro','24,574','31,31','34,31','1,85','7,58','0,15','0,24','19,82','0,04','0,2099','3,6','1,2139','0,14762365','10,28','778,94','0,000114039','5,82e-05','202,3104805','0','0','1','Normal'],
    ['ID_4322','Vereda Tropical','Flor de Laranjeira','Só Mel','Âmbar extra claro','16,217','33,22','41,88','0,49','7,75','0,12','0,3','38,16','0,04','0,3358','4,3','1,4723','0,14732846','14,68','408,51','0,047399185','3,54e-05','112,440138617','0','0','1','Normal'],
    ['ID_7029','Vereda Tropical','Flores Silvestres','Avohai','Âmbar','15,707','35,13','38,01','3,13','7,25','0,14','0,68','24,11','0,04','0,1695','4,1','1,2131','0,084777659','7,41','831,59','0,08443157','3,78e-05','90,97855639499998','0','0','1','Normal'],
    ['ID_6319','Vereda Tropical','Flores Silvestres','Mel e Cia','Âmbar claro','23,108','30,44','33,75','4,22','7,88','0,11','0,44','14,7','0,04','0,4703','4,2','1,7916','0,167009392','7,63','829,15','8,85e-05','5,3e-05','155,58609625','0','0','1','Normal'],
    ['ID_331','Vereda Tropical','Flores Silvestres','Só Mel','Âmbar claro','21,311','26,28','41,18','2,23','8,1','0,11','0,64','15,73','0,04','0,0202','3,9','1,0015','0,262493016','11,69','1322,42','0,038438893','5,81e-05','101,45547218599998','0','0','1','Normal'],
]


def get_dataset_side_effect(name: str):
    """
    Returns a mock object when accessing bucket objects.

    Parameters
    ----------
    name : str

    Returns
    -------
    HTTPResponse
    """
    if name.endswith(".csv"):
        body = IRIS_DATA.encode()
    else:
        body = PNG_DATA
    return HTTPResponse(body=io.BytesIO(body), preload_content=False)
  