import cv2
import numpy as np
import scipy.stats as stats
import os
import pandas as pd
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

# ==================== CONFIGURACIÓN ====================
carpeta_base = r'Z:\RESULTADOS'
nombre_imagen = 'NoisseTrade.png'
archivo_excel = os.path.join(carpeta_base, 'ranking_estrategias.xlsx')

# FILTROS
CORR_MIN = 0.80
CORR_MAX = 1.00
ZSCORE_MIN = 0.5
ZSCORE_MAX = 2.80
ANCHO_MIN = 100
ANCHO_MAX = 300.0

# OPTIMIZACIÓN: Usar múltiples núcleos del CPU
NUM_WORKERS = max(1, multiprocessing.cpu_count() - 1)  # Dejar 1 núcleo libre

# =======================================================

def procesar_imagen(args):
    """
    Función para procesar una sola imagen (optimizada para paralelización)
    """
    ruta_imagen, activo, estrategia, nombre_carpeta = args
    
    try:
        # Leer imagen
        img = cv2.imread(ruta_imagen)
        if img is None:
            return None
        
        # PROCESAMIENTO (código optimizado)
        h, w = img.shape[:2]  # Más rápido que img.shape
        top, bottom = int(h*0.1), int(h*0.9)
        left, right = int(w*0.08), int(w*0.95)
        
        roi = img[top:bottom, left:right]
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # Máscaras (pre-calculadas como arrays)
        blue_lower = np.array([105, 150, 50], dtype=np.uint8)
        blue_upper = np.array([125, 255, 255], dtype=np.uint8)
        color_lower = np.array([0, 60, 60], dtype=np.uint8)
        color_upper = np.array([180, 255, 255], dtype=np.uint8)
        
        blue_mask = cv2.inRange(hsv_roi, blue_lower, blue_upper)
        full_color = cv2.inRange(hsv_roi, color_lower, color_upper)
        cloud_mask = cv2.bitwise_and(full_color, cv2.bitwise_not(blue_mask))

        # Búsqueda optimizada de intersección
        blue_cols = np.sum(blue_mask > 0, axis=0) > 1
        cloud_cols = np.sum(cloud_mask > 0, axis=0) > 5
        
        blue_indices = np.where(blue_cols)[0]
        cloud_indices = np.where(cloud_cols)[0]
        
        if len(blue_indices) == 0 or len(cloud_indices) == 0:
            return None

        x_start = max(blue_indices[0], cloud_indices[0]) + 5
        x_end = min(blue_indices[-1], cloud_indices[-1]) - 5
        
        if x_end <= x_start:
            return None

        # Muestreo de puntos (optimizado con linspace)
        puntos_x = np.linspace(x_start, x_end, 120, dtype=np.int32)
        altura = roi.shape[0]

        # Preallocate arrays (mucho más rápido)
        y_azul_list = []
        y_media_list = []
        y_std_list = []
        x_valid = []

        # Vectorización parcial del bucle
        for x in puntos_x:
            blue_pixels = np.where(blue_mask[:, x] == 255)[0]
            cloud_pixels = np.where(cloud_mask[:, x] == 255)[0]
            
            if len(blue_pixels) > 0 and len(cloud_pixels) > 5:
                x_valid.append(x)
                y_azul_list.append(altura - blue_pixels[0])  # np.min optimizado
                y_media_list.append(altura - np.mean(cloud_pixels))
                y_std_list.append(np.std(altura - cloud_pixels))

        if len(x_valid) < 2:
            return None

        # Convertir a arrays numpy (una sola vez)
        y_a = np.array(y_azul_list, dtype=np.float32)
        y_m = np.array(y_media_list, dtype=np.float32)
        y_s = np.array(y_std_list, dtype=np.float32)

        # CÁLCULO DE MÉTRICAS
        corr = np.corrcoef(y_a, y_m)[0, 1]  # Más rápido que pearsonr para este caso
        z_final = (y_a[-1] - y_m[-1]) / y_s[-1] if y_s[-1] != 0 else 0.0
        ancho_final = y_s[-1] * 4

        # SISTEMA DE PUNTUACIÓN (lookup tables son más rápidos)
        if corr >= 0.95:
            score_corr = 5
        elif corr >= 0.90:
            score_corr = 4
        elif corr >= 0.85:
            score_corr = 3
        elif corr >= 0.80:
            score_corr = 2
        else:
            score_corr = 1
        
        abs_z = abs(z_final - 1.5)
        if abs_z <= 0.3:
            score_zscore = 5
        elif abs_z <= 0.5:
            score_zscore = 4
        elif abs_z <= 0.8:
            score_zscore = 3
        elif abs_z <= 1.2:
            score_zscore = 2
        else:
            score_zscore = 1
        
        if 150 <= ancho_final <= 200:
            score_ancho = 5
        elif 130 <= ancho_final <= 220:
            score_ancho = 4
        elif 110 <= ancho_final <= 240:
            score_ancho = 3
        elif 100 <= ancho_final <= 260:
            score_ancho = 2
        else:
            score_ancho = 1
        
        score_final = (score_corr * 0.4 + score_zscore * 0.35 + score_ancho * 0.25)
        
        # Aplicar filtros
        aprobado = (CORR_MIN <= corr <= CORR_MAX and 
                   ZSCORE_MIN <= z_final <= ZSCORE_MAX and 
                   ANCHO_MIN <= ancho_final <= ANCHO_MAX)
        
        return {
            'Activo': activo,
            'Estrategia': estrategia,
            'Nombre Carpeta': nombre_carpeta,
            'Correlación': round(float(corr), 4),
            'Z-Score': round(float(z_final), 2),
            'Ancho Nube': round(float(ancho_final), 1),
            'Score Correlación': score_corr,
            'Score Z-Score': score_zscore,
            'Score Ancho': score_ancho,
            'Score Final': round(score_final, 2),
            'Aprobado': 'SÍ' if aprobado else 'NO',
            'Ruta': ruta_imagen
        }
    
    except Exception as e:
        print(f"⚠️  Error en {ruta_imagen}: {str(e)}")
        return None


def main():
    print("="*80)
    print(f"🔍 ANÁLISIS COMPLETO DE ESTRATEGIAS - GENERACIÓN DE RANKING (OPTIMIZADO)")
    print("="*80)
    print(f"📁 Carpeta base: {carpeta_base}")
    print(f"📊 Buscando: {nombre_imagen}")
    print(f"⚡ Procesadores: {NUM_WORKERS} núcleos")
    print("-"*80)
    print("CRITERIOS DE FILTRADO:")
    print(f"  • Correlación:    [{CORR_MIN:.2%} - {CORR_MAX:.2%}]")
    print(f"  • Z-Score Final:  [{ZSCORE_MIN:.2f} - {ZSCORE_MAX:.2f}] SD")
    print(f"  • Ancho Nube:     [{ANCHO_MIN:.1f} - {ANCHO_MAX:.1f}] px")
    print("="*80)
    print()

    # Verificar carpeta base
    if not os.path.exists(carpeta_base):
        print(f"❌ Error: No se encuentra la carpeta '{carpeta_base}'")
        return

    # DETECTAR ESTRUCTURA
    print("🔍 Detectando estructura y recolectando imágenes...")
    tiempo_inicio = datetime.now()
    
    carpetas_nivel1 = [d for d in os.listdir(carpeta_base) 
                       if os.path.isdir(os.path.join(carpeta_base, d))]

    if not carpetas_nivel1:
        print(f"❌ No se encontraron carpetas en '{carpeta_base}'")
        return

    # Detectar estructura
    muestra = carpetas_nivel1[0]
    ruta_muestra = os.path.join(carpeta_base, muestra)
    imagen_en_nivel1 = os.path.exists(os.path.join(ruta_muestra, nombre_imagen))

    # Recolectar todas las tareas
    tareas = []
    
    if imagen_en_nivel1:
        print("✓ Estructura PLANA detectada\n")
        for carpeta in carpetas_nivel1:
            ruta_imagen = os.path.join(carpeta_base, carpeta, nombre_imagen)
            if os.path.exists(ruta_imagen):
                partes = carpeta.split()
                activo = partes[0] if len(partes) >= 2 else carpeta
                estrategia = partes[1] if len(partes) >= 2 else "001"
                tareas.append((ruta_imagen, activo, estrategia, carpeta))
    else:
        print("✓ Estructura JERÁRQUICA detectada\n")
        for activo in carpetas_nivel1:
            ruta_activo = os.path.join(carpeta_base, activo)
            estrategias = [d for d in os.listdir(ruta_activo) 
                          if os.path.isdir(os.path.join(ruta_activo, d))]
            
            for estrategia in estrategias:
                ruta_imagen = os.path.join(ruta_activo, estrategia, nombre_imagen)
                if os.path.exists(ruta_imagen):
                    tareas.append((ruta_imagen, activo, estrategia, None))

    total_imagenes = len(tareas)
    print(f"📊 Total de imágenes encontradas: {total_imagenes}")
    
    if total_imagenes == 0:
        print("❌ No se encontraron imágenes para procesar")
        return
    
    print(f"⚡ Procesando en paralelo con {NUM_WORKERS} workers...\n")

    # PROCESAMIENTO PARALELO
    resultados = []
    imagenes_aprobadas = 0
    procesadas = 0
    
    # Usar ProcessPoolExecutor para paralelización
    with ProcessPoolExecutor(max_workers=NUM_WORKERS) as executor:
        # Enviar todas las tareas
        futures = {executor.submit(procesar_imagen, tarea): tarea for tarea in tareas}
        
        # Procesar resultados a medida que se completan
        for future in as_completed(futures):
            procesadas += 1
            resultado = future.result()
            
            if resultado is not None:
                resultados.append(resultado)
                if resultado['Aprobado'] == 'SÍ':
                    imagenes_aprobadas += 1
                    print(f"✅ [{procesadas}/{total_imagenes}] {resultado['Activo']} - {resultado['Estrategia']}: {resultado['Score Final']:.1f}/5 ⭐")
                else:
                    print(f"❌ [{procesadas}/{total_imagenes}] {resultado['Activo']} - {resultado['Estrategia']}: {resultado['Score Final']:.1f}/5")
            else:
                print(f"⚠️  [{procesadas}/{total_imagenes}] Imagen sin datos válidos")

    tiempo_proceso = (datetime.now() - tiempo_inicio).total_seconds()
    
    # GENERAR EXCEL
    print()
    print("="*80)
    print("📊 GENERANDO EXCEL...")
    print("="*80)

    if len(resultados) == 0:
        print("❌ No se generaron resultados válidos")
        return

    # Crear DataFrame
    df = pd.DataFrame(resultados)
    df = df.sort_values('Score Final', ascending=False, ignore_index=True)

    # Crear Excel con todas las hojas
    with pd.ExcelWriter(archivo_excel, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Ranking Completo', index=False)
        
        df_aprobados = df[df['Aprobado'] == 'SÍ']
        if len(df_aprobados) > 0:
            df_aprobados.to_excel(writer, sheet_name='Solo Aprobados', index=False)
        
        stats_activo = df.groupby('Activo').agg({
            'Score Final': ['mean', 'max', 'min', 'count'],
            'Aprobado': lambda x: (x == 'SÍ').sum()
        }).round(2)
        stats_activo.columns = ['Score Promedio', 'Score Máximo', 'Score Mínimo', 
                                'Total Estrategias', 'Aprobadas']
        stats_activo.to_excel(writer, sheet_name='Estadísticas por Activo')
        
        df_top20 = df.head(20)
        df_top20.to_excel(writer, sheet_name='Top 20', index=False)

    print(f"✅ Excel generado: {archivo_excel}")
    print()

    # RESUMEN FINAL
    print("="*80)
    print("📊 RESUMEN GENERAL")
    print("="*80)
    print(f"📸 Imágenes encontradas:      {total_imagenes}")
    print(f"🔍 Imágenes analizadas:       {len(resultados)}")
    print(f"✅ Imágenes aprobadas:        {imagenes_aprobadas} ({imagenes_aprobadas/len(resultados)*100:.1f}%)")
    print(f"❌ Imágenes rechazadas:       {len(resultados) - imagenes_aprobadas}")
    print(f"⚡ Tiempo de procesamiento:   {tiempo_proceso:.2f} segundos")
    print(f"⚡ Velocidad:                  {total_imagenes/tiempo_proceso:.1f} imágenes/seg")
    print("="*80)

    if len(resultados) > 0:
        print()
        print("🏆 TOP 10 MEJORES ESTRATEGIAS:")
        print("-"*80)
        for i in range(min(10, len(df))):
            row = df.iloc[i]
            estrellas = "⭐" * int(row['Score Final'])
            print(f"{i+1:2d}. {row['Activo']:15s} | {row['Estrategia']:20s} | {row['Score Final']:.2f}/5 {estrellas}")
            print(f"     Corr: {row['Correlación']:.2%} | Z: {row['Z-Score']:.2f} | Ancho: {row['Ancho Nube']:.1f}px")

    print()
    print(f"✓ Análisis completado. Revisa el archivo: {archivo_excel}")


if __name__ == '__main__':
    main()