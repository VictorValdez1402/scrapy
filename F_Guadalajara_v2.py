#Cargamos las librerias necesarias

#Librerias para WebScraping.
from selenium import webdriver
import undetected_chromedriver as uc #Usamos undetected_chromedriver
from selenium.webdriver.chrome.service import Service #NUEVO
from selenium.common import exceptions

# Libraries for explicit waiting time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains  #vic

import re
import time
from datetime import date
import pandas as pd
import math
import numpy as np

#Librerias usadas en el método de David
import requests
from bs4 import BeautifulSoup as BSoup

import time
start_time = time.time()

def iniciar_navegador():
    ### Inicializamos el navegador
    s=Service('C:/Users/vanessa.mora/Desktop/WS Python/chromedriver-win64/chromedriver.exe')

    #Establecemos las opciones de navegación
    #options = webdriver.ChromeOptions()
    options = uc.ChromeOptions()    #vic 
    options.page_load_strategy = 'eager'
    options.binary_location = "C:/Users/vanessa.mora/Desktop/WS Python/chrome-win64/chrome.exe" #Este es el navegador Chrome destinado a pruebas de automatización
    options.add_argument('--start-maximized')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--blink-settings=imagesEnabled=false') #Asi evitamos que se carguen las imágenes
    #options.add_argument("--disable-popup-blocking")
    ##driver = uc.Chrome(service=s, options = options) #Nuevo
    options.add_argument("--disable-http2")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    

    options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe" #vic
    driver = uc.Chrome(options=options, version_main=145) #vic

    return driver #vic
driver = iniciar_navegador()  #vic
driver.set_page_load_timeout(60)

for intento in range(3):
    try:
        driver.get ("https://www.farmaciasguadalajara.com")  #vic
        break
    except:
        print("Error cargando paginas, reiniciando navegador")
        driver.quit()
        driver = iniciar_navegador()
        time.sleep(random.uniform(4,8))  #vic

if driver.window_handles:

    driver.execute_script("""    
    document.querySelectorAll('[role="dialog"]').forEach(function(e){
         e.remove();
    });
    document.querySelectorAll('.modal').forEach(function(e){
        e.remove();
    });
    document.body.classList.remove('modal-open');
    """)   #vic

farmacia = WebDriverWait(driver,20).until(
    EC.presence_of_element_located((By.CSS_SELECTOR,"a[href*='/farmacia']"))
)

time.sleep(5)

driver.execute_script(""" 
document.querySelectorAll('[role="dialog"]').forEach(e => e.remove());
document.querySelectorAll('.modal').forEach(e => e.remove());
document.body.classList.remove('modal-open');
""")

actions = ActionChains(driver)
actions.move_to_element(farmacia).perform()

time.sleep(2)

categorias = driver.find_elements(By.XPATH, "//a[contains(@href,'/farmacia/')]")

links = []

for c in categorias:
    link = c.get_attribute("href")

    if link:
        links.append(link)

print("Total categorias:", len(links))

for link in links:

    print("Entrando a:", link)

try:
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(link)

    import random #vic
    time.sleep(random.uniform(6,12))

except:
    print("Pagina tardo demasiado, continuando...")
    driver.execute_script("window.stop();")


############
#  Código para obtener categorías
url = 'https://www.farmaciasguadalajara.com/'
headers = {
           "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
           }

try:
    response = requests.get(url, headers=headers, timeout=15)
    response.status_code  #status_code
    html_source = response.text
except requests.exceptions.ReadTimeout:
    driver = iniciar_navegador()
    driver.get(url)
    html_source = driver.page_source



soup = BSoup(html_source, 'html.parser') #parse_only=SoupStrainer("a")
x = soup.find('ul', attrs={'role': 'menu', 'data-parent': 'header'})
if x:  #vic
    y = x.find_all('a', attrs={'role': "menuitem"})
else: #vic
    print("No se encontro el menu")  #vic
c = 0
## c = len(y)
df = []
for i in range(0,c):

    z = y[i]
    Nombre = z.text.replace('\r','').replace('\n','').replace('\t','').strip()
    Id = z.get('id')
    list_var = Id.split('_')
    link = z.get('href')

    if link != 'javascript:void(0)':
        if len(list_var) == 2:
            div_id = list_var[1]
            cat_id = ''
            subcat_id = ''
        elif len(list_var) == 3:
            div_id = list_var[1]
            cat_id = list_var[2]
            subcat_id = ''
        elif len(list_var) == 4:
            div_id = list_var[1]
            cat_id = list_var[2]
            subcat_id = list_var[3] 
    
        dn = [Nombre, Id, div_id, cat_id, subcat_id, link]
        df.append(dn)
    else:
        continue

df_categorias = pd.DataFrame(df, columns=['Nombre', 'Id', 'div_id', 'cat_id', 'subcat_id', 'Link'])
df_categorias = df_categorias.merge(df_categorias[df_categorias.cat_id == ''][['Nombre','div_id']].rename(columns={'Nombre': 'División'}), on ='div_id', how = 'left')
df_categorias = df_categorias.merge(df_categorias[(df_categorias.cat_id != '') & (df_categorias.subcat_id == '')][['Nombre','cat_id']].rename(columns={'Nombre': 'Categoría'}), on ='cat_id', how = 'left').rename(columns={'Nombre': 'Subcategoría'})
df_categorias = df_categorias[['Id', 'División', 'Categoría', 'Subcategoría', 'div_id', 'cat_id', 'subcat_id', 'Link']]
df_categorias = df_categorias[(df_categorias.División != 'Sobre nosotros') & (df_categorias.División != 'Ayuda')]
#pd.DataFrame(df_categorias).to_excel('Categorias_G.xlsx')
################



# Definimos la función para extraer los atributos de los productos
def funcion_extraer(i, soup):
    # Otra url para ver productos https://www.farmaciasguadalajara.com/ProductDisplay?top_category5=&top_category4=&top_category3=&urlRequestType=Base&productId=3074457345616859180&catalogId=10052&top_category2=&categoryId=3074457345616680855&errorViewName=ProductDisplayErrorView&urlLangId=-24&langId=-24&top_category=3074457345616680768&parent_category_rn=3074457345616680781&storeId=10151
    z = x[i]
    link = z.find('div', attrs = {'class': 'product_name'}).a.get('href')
    product_id = z.find('div', attrs={'class': 'image'}).get('dataci_product')[2:]
    Internal_productId = z.find('div', attrs={'class': 'compare_target compare_target_hidden'}).input.get('value')
    #product_id = re.compile(r'-\d+$').findall(link)[0][1:]
    Marca = z.find('div', attrs = {'class': 'product_name'}).b.text
    descripcion = z.find('div', attrs = {'class': 'product_name'}).a.text
    precio_final = z.find('div', attrs = {'class': 'product_price'}).find('span', attrs = {'class': 'price'}).text.replace('\r','').replace('\n','').replace('\t','').replace('$','').replace(',','').strip()
    try: 
        precio_final = float(precio_final)
    except ValueError:
        precio_final = np.nan

    if z.find('div', attrs = {'class': 'product_price'}).find('span', attrs = {'class': 'old_price'})==None:
        precio_original = precio_final
    else:
        precio_original = float(z.find('div', attrs = {'class': 'product_price'}).find('span', attrs = {'class': 'old_price'}).text.replace('\r','').replace('\n','').replace('\t','').replace('$','').replace(',','').strip())
        
    dn = [product_id, Internal_productId, Marca, descripcion, link, precio_original, precio_final]
    return dn
#funcion_extraer(0, x)

df = []
j=0
aux_time = time.time()
#cat = df_categorias[df_categorias.subcat_id!=''].subcat_id.reset_index().iloc[110,1]
for cat in df_categorias[df_categorias.subcat_id!=''].subcat_id:
#for cat in df_categorias[df_categorias.subcat_id =='3074457345616680809'].subcat_id:

    if((time.time()-aux_time)/60>10):
        driver.close()
        driver = iniciar_navegador()
        aux_time = time.time()

    j+=1
    url_cat = df_categorias[df_categorias.subcat_id == cat].Link.iloc[0]
    try:
        driver.get(url_cat)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "product"))
        )
    except exceptions.TimeoutException:
        driver.delete_network_conditions()
        driver.delete_all_cookies()
        driver.get(url_cat)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "product"))
        )
    html_source = driver.page_source
    soup = BSoup(html_source, 'html.parser')
    n_productos = int(soup.find('b', attrs={'class': 'fgplppagintotalCount'}).text)

    resultados = 50
    p=0
    while p<math.ceil(n_productos/resultados):
    #for i in range(1,pags+1): #Modificamos el inicio para ejecutar desde la pagina donde se detuvo el script.
        url = 'https://www.farmaciasguadalajara.com/ProductListingView?categoryId='+cat+'&storeId=10151&beginIndex='+str(resultados*p)+'&x_listOnly=true&&catalogId=10052&pageSize='+str(resultados)
        
        try:
            driver.get(url)
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "product"))
            )
        except exceptions.TimeoutException:
            driver.delete_network_conditions
            driver.delete_all_cookies
            driver.get(url)
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "product"))
            )
        
        html_source = driver.page_source
        soup = BSoup(html_source, 'html.parser')
        x = soup.find_all('div', attrs={'class': 'product'})

        # Atributos Artículos
        n = len(x)
        for i in range(0,n):
            dn = funcion_extraer(i,x)
            dn = dn + df_categorias[df_categorias.subcat_id ==cat][['División', 'Categoría', 'Subcategoría']].iloc[0].to_list()
            #dn = dn + list([str(p), str(i)])
            df.append(dn)
        
        print(str(p+1) + ' de ' + str(math.ceil(n_productos/resultados))) # Núumero de página
        p = p+1

    driver.delete_all_cookies
    print(cat + ' '+ str(j) + ' de ' + str(len(df_categorias[df_categorias.subcat_id!=''].subcat_id))) # Número de categoría


df_Farmacia = pd.DataFrame(df, columns=['id', 'Internal_productId', 'Marca', 'Descripción', 'Link', 'Precio Original', 'Precio Final', 'División', 'Categoría', 'Subcategoría'])
df_Farmacia['Fecha']=date.today()


df_SKUs = pd.read_excel("C:/Users/vanessa.mora/OneDrive - UNIFAR S.A. de C.V/Carpeta Compartida Webscrapping Precios/Precios/SKUS_FGuadalajara.xlsx",dtype='str')
productos_buscar_SKU = df_Farmacia[pd.isna(df_Farmacia.merge(df_SKUs, how='left').SKU ) == True].reset_index()



### Obtener SKUs
SKUs = []
for j in range(0,len(productos_buscar_SKU.Internal_productId)):
    p_id = productos_buscar_SKU.Internal_productId[j]
    url = 'https://www.farmaciasguadalajara.com/ProductDisplay?urlRequestType=Base&catalogId=10052&storeId=10151&productId='+p_id
    driver.get(url)
    html_source = driver.page_source
    soup = BSoup(html_source, 'html.parser')
    if soup.find('div', attrs={'class': 'shopperActions add-to-cart-pdp-list addcartbtnwrap'})!=None:
        x = soup.find('div', attrs={'class': 'shopperActions add-to-cart-pdp-list addcartbtnwrap'}).find('input', attrs={'id': 'descriptiveAttrbutes'}).get('value')
        if x != '{skus: []}':
            SKU = re.compile('cup\': \'\\d+\'').findall(x)[0][7:-1]
            id = soup.find('meta', attrs={'name': 'pageIdentifier'}).get('content').replace('P','')
            dn = [p_id, id, SKU]
            SKUs.append(dn)

    print(str(j+1) + ' de ' + str(len(productos_buscar_SKU.Internal_productId)))

add_df_SKUs = pd.DataFrame(SKUs,columns=['Internal_productId','id', 'SKU'])
df_SKUs = df_SKUs._append(add_df_SKUs, ignore_index = True)
df_SKUs = df_SKUs.drop_duplicates()

df_SKUs.to_excel("C:/Users/vanessa.mora/OneDrive - UNIFAR S.A. de C.V/Carpeta Compartida Webscrapping Precios/Precios/"+"SKUS_FGuadalajara.xlsx", index=False)

df_Farmacia = df_Farmacia.merge(df_SKUs, how='left')


df_Farmacia.to_excel("C:/Users/vanessa.mora/OneDrive - UNIFAR S.A. de C.V/SalidasWebScraping/"+"FGuadalajara_"+str(date.today())+".xlsx", index=False)
driver.close()
finish_time = time.time()

(finish_time-start_time)/60
tiempo_ejecución = 57.10995355844498 # Ejecución en casa


