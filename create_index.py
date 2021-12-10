from os import path
import pandas as pd

municipios = ['Aguascalientes', 'Campeche', 'Centro', 'Chihuahua', 'Chilpancingo de los Bravo', 'Colima', 'Cuernavaca',
              'Culiacán', 'Durango', 'Guadalajara', 'Guanajuato', 'Hermosillo', 'La Paz', 'Mexicali', 'Monterrey',
              'Morelia', 'Mérida', 'Oaxaca de Juárez', 'Othón P. Blanco', 'Pachuca de Soto', 'Puebla', 'Querétaro',
              'Saltillo', 'San Luis Potosí', 'Tepic', 'Tlaxcala', 'Toluca', 'Tuxtla Gutiérrez', 'Victoria', 'Xalapa',
              'Zacatecas']



data_path = 'data'
municipio = municipios[0]

asc = pd.read_csv(path.join(data_path, municipio + '_ASCENDING_.csv')).iloc[:, 1].to_numpy()
dsc = pd.read_csv(path.join(data_path, municipio + '_DESCENDING_.csv')).iloc[:, 1].to_numpy()

changes = asc + dsc / 2



print('eof')
