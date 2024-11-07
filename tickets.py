import pdfplumber
import pandas as pd
import re
import os

# Cargar la tabla de categorías desde un archivo CSV con la nueva columna "Subcategoría"
tabla_categorias = pd.read_csv('categorias.csv', sep=';', encoding='utf-8')

# Función para obtener categoría y subcategoría desde la tabla CSV
def obtener_categoria_y_subcategoria(producto, tabla):
    for _, row in tabla.iterrows():
        if row['Producto'].upper() in producto.upper():
            return row['Categoría'], row['Subcategoría']
    return "Otros", "Sin subcategoría"  # Si no coincide, asigna 'Otros' y 'Sin subcategoría'

# Función para extraer información de productos normales
def extract_product(line):
    pattern = r'^(\d+)\s+([\w\sÁÉÍÓÚáéíóúÑñ.,/%()&+-]+)\s+(\d+,\d{2})(?:\s+(\d+,\d{2}))?$'
    match = re.match(pattern, line)
    
    if match:
        quantity = match.group(1)
        description = match.group(2).strip()

        if quantity != '1':
            total_price_str = match.group(4) if match.group(4) else match.group(3)
            total_price = float(total_price_str.replace(',', '.'))
            quantity_num = int(quantity)
            unit_price = total_price / quantity_num if quantity_num > 0 else 0.0
            unit_price_str = "{:.2f}".format(unit_price).replace('.', ',')
            if description.endswith(unit_price_str):
                description = description[:-(len(unit_price_str) + 1)]  
        else:
            unit_price = ''
            total_price_str = match.group(4) if match.group(4) else match.group(3)
            total_price = float(total_price_str.replace(',', '.'))

        # Obtener la categoría y subcategoría para el producto
        categoria, subcategoria = obtener_categoria_y_subcategoria(description, tabla_categorias)
        
        return {
            "Unidades": quantity,
            "Descripción": description,
            "Precio por unidad": f"{unit_price:.2f}" if unit_price != '' else '',
            "Precio por kg": '',
            "Importe": f"{total_price_str}",
            "Peso": '',
            "Categoría": categoria,
            "Subcategoría": subcategoria
        }
    
    return None

# Función para extraer información de productos a granel
def extract_bulk_product(description_line, weight_price_line):
    # Expresión regular para la primera línea (cantidad y descripción)
    quantity_description_pattern = r'^(\d+)\s+([\w\sÁÉÍÓÚáéíóúÑñ.,/%()&+-]+)$'
    description_match = re.match(quantity_description_pattern, description_line)
    
    if description_match:
        quantity = description_match.group(1)
        description = description_match.group(2).strip()
        
        # Obtener la categoría y subcategoría para el producto
        categoria, subcategoria = obtener_categoria_y_subcategoria(description, tabla_categorias)
        
        # Expresión regular para la segunda línea (peso, precio por kg, e importe)
        weight_price_pattern = r'^(\d+,\d{3})\s+kg\s+(\d+,\d{2})\s+€\/kg\s+(\d+,\d{2})$'
        weight_price_match = re.match(weight_price_pattern, weight_price_line)
        
        if weight_price_match:
            weight = weight_price_match.group(1)
            price_per_kg = weight_price_match.group(2)
            total_price = weight_price_match.group(3)
            
            return {
                "Unidades": quantity,
                "Descripción": description,
                "Precio por unidad": '',
                "Precio por kg": f"{price_per_kg}",
                "Importe": f"{total_price}",
                "Peso": f"{weight}",
                "Categoría": categoria,
                "Subcategoría": subcategoria
            }
    
    return None

# Función para procesar un archivo PDF
def process_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
            
    # Extraer la fecha
    date_match = re.search(r'\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}', text)
    date = date_match.group() if date_match else "Fecha no encontrada"
    
    # Dividir el texto en líneas
    product_lines = text.split('\n')
    products = []
    
    i = 0
    while i < len(product_lines):
        line = product_lines[i].strip()

        # Intentar extraer un producto normal
        product_info = extract_product(line)
        
        if product_info:
            # Añadir la fecha al producto extraído
            product_info["Fecha"] = date
            products.append(product_info)
        else:
            # Comprobar si es la primera línea de un producto a granel
            if re.match(r'^\d+\s+[\w\sÁÉÍÓÚáéíóúÑñ.,/%()&+-]+$', line):
                if i + 1 < len(product_lines):
                    next_line = product_lines[i + 1].strip()
                    if re.match(r'^\d+,\d{3}\s+kg\s+\d+,\d{2}\s+€\/kg\s+\d+,\d{2}$', next_line):
                        bulk_product = extract_bulk_product(line, next_line)
                        if bulk_product:
                            bulk_product["Fecha"] = date
                            products.append(bulk_product)
                        i += 1  # Saltar la segunda línea (peso, precio por kg)
        
        i += 1
    
    # Extraer el total del ticket
    total_match = re.search(r'TOTAL\s+€?\s*(\d+,\d{2})', text)
    total = total_match.group(1) if total_match else "Total no encontrado"
    
    return products, total

# Función para procesar todos los PDFs en una carpeta
def process_all_pdfs(folder_path):
    all_products = []
    all_totals = []
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            file_path = os.path.join(folder_path, filename)
            products, total = process_pdf(file_path)
            
            # Extender productos y agregar total del archivo
            all_products.extend(products)
            all_totals.append({"Fecha": products[0]["Fecha"], "Total": total, "Archivo": filename})
    
    # Guardar los productos y los totales en archivos Excel
    products_df = pd.DataFrame(all_products)
    totals_df = pd.DataFrame(all_totals)
    
    products_df.to_excel('productos.xlsx', index=False)
    totals_df.to_excel('totales_tickets.xlsx', index=False)

# Llamada al procesamiento de todos los archivos PDF en la carpeta
process_all_pdfs('./pdf/')
