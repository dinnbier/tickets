# Automatización de Tickets de Mercadona para Análisis en Hoja de Cálculo

En este artículo explico cómo he conseguido automatizar el proceso de gestión de los tickets de Mercadona que recibo en mi correo electrónico. Utilizando dos flujos de información principales y herramientas como Google Apps Script y Python, he podido transformar estos tickets en datos estructurados dentro de una hoja de cálculo para su estudio.

## Flujo de Trabajo

El proceso consta de dos fases principales:

1. Guardado automático de los tickets en formato PDF en Google Drive desde Gmail.

2. Extracción de datos de los tickets PDF y creación de hojas de cálculo con los datos relevantes.

## Fase 1: Guardado Automático de Tickets en Google Drive



En esta primera fase, he utilizado Google Apps Script para acceder a mi cuenta de Gmail y almacenar automáticamente los archivos PDF de los tickets en una carpeta específica de Google Drive. A continuación se muestra el código en JavaScript que se ejecuta en Google Apps Script para lograr este objetivo.
Los scripts de Google Apps se pueden ejecutar empleando temporizadores. El temporizador que he asociado en este caso se ejecuta cada 15 min, de modo que transcurrido ese tiempo tendremos todos los tickets de mercadona en la carpeta de Drive.

El script tickets_app_script.js se ejecuta en Google Apps Script y se encarga de:

- Buscar correos electrónicos con remitente ticket_digital@mail.mercadona.com que incluyan archivos PDF adjuntos.
- Guardar los archivos PDF en la carpeta de Google Drive especificada mediante folderId.
- Registrar los correos procesados para evitar duplicados.

## Fase 2: Extracción de Información desde los PDFs
Una vez almacenados los archivos PDF en Google Drive, el siguiente paso consiste en extraer la información de los tickets y guardarla en una hoja de cálculo. He utilizado Python junto con la biblioteca pdfplumber para leer los PDFs y pandas para estructurar los datos en hojas de cálculo.

El script de python es "tickets.py"

Como resultado de este scriot se generan dos archivos: totales_tickets.xlsx y productos.xlsx que contienen:

totales_tickets.xlsx: todos los tickets con el importe total y la fecha

productos.xlsx: todas las líneas de todos los tickets con su categoría y subcategoría, importe y en el caso de productos a granel importe total e importe por peso. 

Las categorías de los archivos deben actualizarse de forma manual, pero he creado ya un archivo categorias.csv que contiene muchos artículos categorizados. Para categorizar de forma efectiva y seguir alguna pauta he tomado como referencia la web de mercadona donde los productos siguen una estructura y organización que entiendo que un equipo con conocimiento y dedicación ha pensado mejor de lo que puedo hacerlo yo. 

