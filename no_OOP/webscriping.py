from pkg_resources import resource_listdir
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen

urls = ['https://es.wikipedia.org/wiki/Colombia',
'https://es.wikipedia.org/wiki/Inteligencia_artificial',
'https://es.wikipedia.org/wiki/Homo_sapiens',
'https://es.wikipedia.org/wiki/Capitalismo',
'https://es.wikipedia.org/wiki/Alan_Turing',
'https://es.wikipedia.org/wiki/Juda%C3%ADsmo',
'https://es.wikipedia.org/wiki/Salsa_(g%C3%A9nero_musical)',
'https://es.wikipedia.org/wiki/Divina_comedia',
'https://es.wikipedia.org/wiki/Holocausto',
'https://es.wikipedia.org/wiki/Asia',
'https://es.wikipedia.org/wiki/Odisea',
'https://es.wikipedia.org/wiki/Ludwig_van_Beethoven',
'https://es.wikipedia.org/wiki/Enrique_VIII_de_Inglaterra',
'https://es.wikipedia.org/wiki/Guerra_Fr%C3%ADa',
'https://es.wikipedia.org/wiki/Nevado_del_Ruiz',
'https://es.wikipedia.org/wiki/Nikola_Tesla',
'https://es.wikipedia.org/wiki/Julio_Garavito',
'https://es.wikipedia.org/wiki/Estados_Unidos',
'https://es.wikipedia.org/wiki/Juglar',
'https://es.wikipedia.org/wiki/Biblia',
'https://es.wikipedia.org/wiki/Cristianismo',
'https://es.wikipedia.org/wiki/Pueblos_germ%C3%A1nicos',
'https://es.wikipedia.org/wiki/Europa',
'https://es.wikipedia.org/wiki/Grecia',
'https://es.wikipedia.org/wiki/Democracia',
'https://es.wikipedia.org/wiki/Estado',
'https://es.wikipedia.org/wiki/Filosof%C3%ADa',
'https://es.wikipedia.org/wiki/Ciencia',
'https://es.wikipedia.org/wiki/Cultura',
'https://es.wikipedia.org/wiki/Per%C3%ADodo_helen%C3%ADstico',
'https://es.wikipedia.org/wiki/Babilonia_(ciudad)',
'https://es.wikipedia.org/wiki/Organizaci%C3%B3n_de_las_Naciones_Unidas',
'https://es.wikipedia.org/wiki/Segunda_Guerra_Mundial',
'https://es.wikipedia.org/wiki/Reino_Unido',
'https://es.wikipedia.org/wiki/Aeropuerto',
'https://es.wikipedia.org/wiki/Saxof%C3%B3n',
'https://es.wikipedia.org/wiki/Biodiversidad',
'https://es.wikipedia.org/wiki/Gastronom%C3%ADa_de_M%C3%A9xico',
'https://es.wikipedia.org/wiki/Valle',
'https://es.wikipedia.org/wiki/George_Patton',
'https://es.wikipedia.org/wiki/Cristo',
'https://es.wikipedia.org/wiki/Arte',
'https://es.wikipedia.org/wiki/Est%C3%A9tica',
'https://es.wikipedia.org/wiki/Sublime',
'https://es.wikipedia.org/wiki/Liberalismo',
'https://es.wikipedia.org/wiki/Ecologismo',
'https://es.wikipedia.org/wiki/Consumo',
'https://es.wikipedia.org/wiki/Energ%C3%ADa_nuclear',
'https://es.wikipedia.org/wiki/Revoluci%C3%B3n_Industrial',
'https://es.wikipedia.org/wiki/Henry_Ford',
'https://es.wikipedia.org/wiki/Jorge_Isaacs',
'https://es.wikipedia.org/wiki/Gabriel_Garc%C3%ADa_M%C3%A1rquez',
'https://es.wikipedia.org/wiki/Italia',
'https://es.wikipedia.org/wiki/Pizza',
'https://es.wikipedia.org/wiki/Antiguo_Egipto',
'https://es.wikipedia.org/wiki/%C3%81frica',
'https://es.wikipedia.org/wiki/Agricultura',
'https://es.wikipedia.org/wiki/Fruta',
'https://es.wikipedia.org/wiki/Real_Academia_Espa%C3%B1ola',
'https://es.wikipedia.org/wiki/Diccionario',
'https://es.wikipedia.org/wiki/Escritura',
'https://es.wikipedia.org/wiki/Rueda',
'https://es.wikipedia.org/wiki/Thomas_Alva_Edison',
'https://es.wikipedia.org/wiki/Finanzas',
'https://es.wikipedia.org/wiki/Libro']
f= open("data.txt","w+")
for url in urls:
  html = urlopen(url).read()
  soup = BeautifulSoup(html, features="html.parser")

  for script in soup(["script", "style"]):
      script.extract()    # rip it out

  text = soup.get_text()
  lines = (line.strip() for line in text.splitlines())
  chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
  text = '\n'.join(chunk for chunk in chunks if chunk)
  f.write(text)
  print(url)
f.close()