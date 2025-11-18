import requests

try:
    # Probar la API de productos
    response = requests.get('http://127.0.0.1:8000/api/shop/products/')
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")

    if response.status_code == 200:
        try:
            data = response.json()
            print("\n=== API de Productos ===")
            if 'results' in data:
                products = data['results']
                print(f"Total de productos: {len(products)}")
                if products:
                    product = products[0]
                    print(f"\nProducto de ejemplo:")
                    print(f"  ID: {product.get('id')}")
                    print(f"  Nombre: {product.get('name')}")
                    print(f"  Imagen principal: {product.get('main_image_url')}")
                    print(f"  Todas las imágenes: {len(product.get('all_image_urls', []))} imágenes")
                    print(f"  Tiene imagen válida: {product.get('has_valid_image')}")

                    if product.get('images'):
                        print(f"  Imágenes detalladas: {len(product.get('images'))} imágenes")
                        for i, img in enumerate(product.get('images', [])[:3]):  # Mostrar hasta 3
                            print(f"    [{i+1}] Orden {img['order']}: {img['image_url'][:50]}... (Principal: {img['is_main']})")
            else:
                print("Respuesta no paginada")
                if isinstance(data, list) and data:
                    product = data[0]
                    print(f"Producto: {product.get('name')}")
        except Exception as e:
            print(f"Error al parsear JSON: {e}")
            print(f"Contenido: {response.text[:500]}")
    else:
        print(f"Error: {response.status_code}")
        print(f"Contenido: {response.text[:500]}")

    # Probar la API de imágenes de productos
    print("\n=== API de Imágenes de Productos ===")
    response2 = requests.get('http://127.0.0.1:8000/api/shop/product-images/')
    print(f"Status Code: {response2.status_code}")
    if response2.status_code == 200:
        try:
            data2 = response2.json()
            if 'results' in data2:
                images = data2['results']
                print(f"Total de imágenes: {len(images)}")
                if images:
                    img = images[0]
                    print(f"Imagen de ejemplo: {img.get('image_url')[:50]}... (Producto ID: {img.get('product')}, Orden: {img.get('order')}, Principal: {img.get('is_main')})")
        except Exception as e:
            print(f"Error al parsear JSON: {e}")

except Exception as e:
    print(f'Error de conexión: {e}')