import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from scipy import stats
import flet as ft
import base64
import io
import tempfile
import os

matplotlib.use('Agg')

# ==========================================
# 1. LÓGICA DE NEGOCIO
# ==========================================
class EstadisticaLogic:
    
    # Configuración de parámetros por distribución
    DISTRIBUCIONES = {
        "normal": {"nombre": "Normal (Gaussiana)", "params": [("Media (μ)", "0"), ("Desviación (σ)", "1")]},
        "uniforme": {"nombre": "Uniforme", "params": [("a (mínimo)", "0"), ("b (máximo)", "1")]},
        "exponencial": {"nombre": "Exponencial", "params": [("Lambda (λ)", "1")]},
        "poisson": {"nombre": "Poisson", "params": [("Lambda (λ)", "3")]},
        "binomial": {"nombre": "Binomial", "params": [("n (ensayos)", "10"), ("p (probabilidad)", "0.5")]},
        "t_student": {"nombre": "t-Student", "params": [("Grados de libertad (ν)", "10")]},
        "chi_cuadrado": {"nombre": "Chi-Cuadrado (χ²)", "params": [("Grados de libertad (k)", "5")]},
    }

    @staticmethod
    def generar_grafico(dist_id, params):
        """Genera un gráfico de la distribución y retorna la ruta del archivo temporal"""
        try:
            # Configuración del gráfico con estilo oscuro
            plt.style.use('dark_background')
            fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
            fig.patch.set_facecolor('#161b22')
            ax.set_facecolor('#161b22')
            
            # Color del gráfico
            color_linea = '#5b9bd5'
            color_relleno = '#5b9bd5'
            
            titulo = ""
            subtitulo = ""
            
            if dist_id == "normal":
                media, desv = params
                x = np.linspace(media - 4*desv, media + 4*desv, 200)
                y = stats.norm.pdf(x, media, desv)
                ax.plot(x, y, color=color_linea, linewidth=2)
                ax.fill_between(x, y, alpha=0.3, color=color_relleno)
                titulo = "DISTRIBUCIÓN NORMAL"
                subtitulo = f"μ = {media}, σ = {desv}"
                
            elif dist_id == "uniforme":
                a, b = params
                margen = (b - a) * 0.2
                x = np.linspace(a - margen, b + margen, 200)
                y = stats.uniform.pdf(x, loc=a, scale=b - a)
                ax.plot(x, y, color=color_linea, linewidth=2)
                ax.fill_between(x, y, alpha=0.3, color=color_relleno)
                titulo = "DISTRIBUCIÓN UNIFORME"
                subtitulo = f"a = {a}, b = {b}"
                
            elif dist_id == "exponencial":
                lambd = params[0]
                x = np.linspace(0, 5/lambd, 200)
                y = stats.expon.pdf(x, scale=1/lambd)
                ax.plot(x, y, color=color_linea, linewidth=2)
                ax.fill_between(x, y, alpha=0.3, color=color_relleno)
                titulo = "DISTRIBUCIÓN EXPONENCIAL"
                subtitulo = f"λ = {lambd}"
                
            elif dist_id == "poisson":
                lambd = params[0]
                x = np.arange(0, int(lambd * 3) + 5)
                y = stats.poisson.pmf(x, mu=lambd)
                ax.bar(x, y, color=color_relleno, alpha=0.8, width=0.8)
                titulo = "DISTRIBUCIÓN POISSON"
                subtitulo = f"λ = {lambd}"
                
            elif dist_id == "binomial":
                n, p = int(params[0]), params[1]
                x = np.arange(0, n + 1)
                y = stats.binom.pmf(x, n=n, p=p)
                ax.bar(x, y, color=color_relleno, alpha=0.8, width=0.8)
                titulo = "DISTRIBUCIÓN BINOMIAL"
                subtitulo = f"n = {n}, p = {p}"
                
            elif dist_id == "t_student":
                df = params[0]
                x = np.linspace(-4, 4, 200)
                y = stats.t.pdf(x, df=df)
                ax.plot(x, y, color=color_linea, linewidth=2)
                ax.fill_between(x, y, alpha=0.3, color=color_relleno)
                titulo = "DISTRIBUCIÓN t-STUDENT"
                subtitulo = f"ν = {df}"
                
            elif dist_id == "chi_cuadrado":
                k = params[0]
                x = np.linspace(0, k * 3 + 10, 200)
                y = stats.chi2.pdf(x, df=k)
                ax.plot(x, y, color=color_linea, linewidth=2)
                ax.fill_between(x, y, alpha=0.3, color=color_relleno)
                titulo = "DISTRIBUCIÓN CHI-CUADRADO"
                subtitulo = f"k = {k}"
            
            # Estilo del gráfico
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#8b949e')
            ax.spines['bottom'].set_color('#8b949e')
            ax.tick_params(colors='#8b949e', labelsize=8)
            ax.set_xlabel(subtitulo, color='#8b949e', fontsize=10)
            
            plt.tight_layout()
            
            # Guardar a archivo temporal
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, f"dist_chart_{dist_id}.png")
            plt.savefig(temp_path, facecolor='#161b22', edgecolor='none', bbox_inches='tight')
            plt.close(fig)
            
            return temp_path, titulo
            
        except Exception as e:
            return None, f"Error: {e}"

    @staticmethod
    def calcular_probabilidad(dist_id, params, valor):
        """Calcula P(X <= valor) para la distribución dada"""
        try:
            if dist_id == "normal":
                media, desv = params
                z = (valor - media) / desv
                return stats.norm.cdf(z)
            elif dist_id == "uniforme":
                a, b = params
                return stats.uniform.cdf(valor, loc=a, scale=b - a)
            elif dist_id == "exponencial":
                lambd = params[0]
                return stats.expon.cdf(valor, scale=1/lambd)
            elif dist_id == "poisson":
                lambd = params[0]
                return stats.poisson.cdf(valor, mu=lambd)
            elif dist_id == "binomial":
                n, p = params
                return stats.binom.cdf(valor, n=int(n), p=p)
            elif dist_id == "t_student":
                df = params[0]
                return stats.t.cdf(valor, df=df)
            elif dist_id == "chi_cuadrado":
                k = params[0]
                return stats.chi2.cdf(valor, df=k)
        except Exception as e:
            return f"Error: {e}"
        return 0.0

    @staticmethod
    def calcular_dato(dist_id, params, probabilidad):
        """Calcula el valor X tal que P(X <= x) = probabilidad (inversa)"""
        try:
            if dist_id == "normal":
                media, desv = params
                z = stats.norm.ppf(probabilidad)
                return z * desv + media
            elif dist_id == "uniforme":
                a, b = params
                return stats.uniform.ppf(probabilidad, loc=a, scale=b - a)
            elif dist_id == "exponencial":
                lambd = params[0]
                return stats.expon.ppf(probabilidad, scale=1/lambd)
            elif dist_id == "poisson":
                lambd = params[0]
                return stats.poisson.ppf(probabilidad, mu=lambd)
            elif dist_id == "binomial":
                n, p = params
                return stats.binom.ppf(probabilidad, n=int(n), p=p)
            elif dist_id == "t_student":
                df = params[0]
                return stats.t.ppf(probabilidad, df=df)
            elif dist_id == "chi_cuadrado":
                k = params[0]
                return stats.chi2.ppf(probabilidad, df=k)
        except Exception as e:
            return f"Error: {e}"
        return 0.0

    @staticmethod
    def simular(dist_id, params, n):
        """Genera n valores aleatorios de la distribución"""
        try:
            if dist_id == "normal":
                media, desv = params
                return np.random.normal(media, desv, n)
            elif dist_id == "uniforme":
                a, b = params
                return np.random.uniform(a, b, n)
            elif dist_id == "exponencial":
                lambd = params[0]
                return np.random.exponential(1/lambd, n)
            elif dist_id == "poisson":
                lambd = params[0]
                return np.random.poisson(lambd, n)
            elif dist_id == "binomial":
                n_ensayos, p = params
                return np.random.binomial(int(n_ensayos), p, n)
            elif dist_id == "t_student":
                df = params[0]
                return np.random.standard_t(df, n)
            elif dist_id == "chi_cuadrado":
                k = params[0]
                return np.random.chisquare(k, n)
        except Exception as e:
            return [0.0]
        return [0.0]


# ==========================================
# 2. INTERFAZ GRÁFICA - MOBILE FIRST
# ==========================================

def main(page: ft.Page):
    page.title = "App Estadística"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.bgcolor = "#0d1117"
    
    # Colores del tema
    CARD_BG = "#161b22"
    ACCENT_GREEN = "#2dd4bf"
    TEXT_MUTED = "#8b949e"

    # ==========================================
    # PANTALLA 1: DISTRIBUCIONES
    # ==========================================
    
    def crear_card(content, pad=15):
        """Crea una card con estilo consistente"""
        return ft.Container(
            content=content,
            bgcolor=CARD_BG,
            border_radius=12,
            padding=pad,
            margin=ft.Margin(0, 0, 0, 12)
        )

    def crear_seccion_titulo(texto):
        """Crea un título de sección"""
        return ft.Text(
            texto,
            size=12,
            weight=ft.FontWeight.W_500,
            color=TEXT_MUTED
        )

    # --- Header ---
    header = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.BAR_CHART, color=ACCENT_GREEN, size=28),
            ft.Column([
                ft.Text("Cálculo de Distribuciones", size=20, weight=ft.FontWeight.BOLD),
                ft.Text("Probabilidades y simulaciones", size=12, color=TEXT_MUTED)
            ], spacing=2)
        ], spacing=12),
        padding=ft.Padding(20, 20, 20, 10)
    )

    # --- Sección Parámetros (dinámica) ---
    # Contenedor para los campos de parámetros que cambian según la distribución
    param_fields = []  # Lista para almacenar referencias a los TextFields
    
    # Usamos un Container cuyo content se reemplaza completamente
    seccion_parametros = ft.Container(
        bgcolor=CARD_BG,
        border_radius=12,
        padding=15,
        margin=ft.Margin(0, 0, 0, 12)
    )

    def crear_param_field(label, value):
        """Crea un campo de parámetro con estilo"""
        return ft.TextField(
            label=label,
            value=value,
            bgcolor="#1f2937",
            expand=True,
            height=55
        )

    # --- Sección Gráfico (dinámica) ---
    grafico_titulo = ft.Text("DISTRIBUCIÓN NORMAL", size=12, weight=ft.FontWeight.W_500, color=TEXT_MUTED)
    grafico_imagen = ft.Image(src="", width=600, height=250)
    
    seccion_grafico = ft.Container(
        content=ft.Column([
            grafico_titulo,
            ft.Container(height=8),
            grafico_imagen
        ]),
        bgcolor=CARD_BG,
        border_radius=12,
        padding=15,
        margin=ft.Margin(0, 0, 0, 12)
    )

    def actualizar_grafico(dist_id, params):
        """Actualiza el gráfico con la distribución y parámetros actuales"""
        try:
            ruta, titulo = EstadisticaLogic.generar_grafico(dist_id, params)
            if ruta:
                grafico_titulo.value = titulo
                grafico_imagen.src = ruta
                if page.controls:
                    page.update()
        except Exception as e:
            pass

    def actualizar_parametros(dist_id):
        """Actualiza los campos de parámetros según la distribución seleccionada"""
        nonlocal param_fields
        param_fields = []  # Limpiar y reasignar
        
        dist_info = EstadisticaLogic.DISTRIBUCIONES.get(dist_id, {})
        params_def = dist_info.get("params", [])
        

        fields = []
        params_valores = []
        for label, default_value in params_def:
            field = crear_param_field(label, default_value)
            param_fields.append(field)
            fields.append(field)
            params_valores.append(float(default_value))
        
        # Crear el contenido según cantidad de parámetros
        content_controls = [
            crear_seccion_titulo("PARÁMETROS"),
            ft.Container(height=8)
        ]
        
        if len(fields) == 1:
            content_controls.append(fields[0])
        elif len(fields) >= 2:
            content_controls.append(ft.Row(fields[:2], spacing=12))
            # Si hay más de 2, agregar filas adicionales
            for i in range(2, len(fields), 2):
                remaining = fields[i:i+2]
                if len(remaining) == 1:
                    content_controls.append(remaining[0])
                else:
                    content_controls.append(ft.Row(remaining, spacing=12))
        
        # Reemplazar el contenido completo del contenedor
        seccion_parametros.content = ft.Column(content_controls)
        
        # Actualizar gráfico con valores por defecto
        actualizar_grafico(dist_id, params_valores)
        
        if page.controls:  # Solo actualizar si la página ya tiene controles
            page.update()

    # Inicializar parámetros con distribución normal
    actualizar_parametros("normal")

    def on_dist_changed(e):
        """Handler que se llama cuando cambia la distribución seleccionada"""
        actualizar_parametros(e.control.value)

    def on_actualizar_grafico(e):
        """Handler para actualizar el gráfico manualmente con parámetros actuales"""
        try:
            dist_id = radio_distribucion.value
            params = [float(field.value) for field in param_fields]
            actualizar_grafico(dist_id, params)
        except:
            pass

    # --- Sección Distribución (usando RadioGroup que tiene eventos funcionando) ---
    radio_distribucion = ft.RadioGroup(
        value="normal",
        on_change=on_dist_changed,
        content=ft.Column([
            ft.Radio(value="normal", label="Normal (Gaussiana)"),
            ft.Radio(value="uniforme", label="Uniforme"),
            ft.Radio(value="exponencial", label="Exponencial"),
            ft.Radio(value="poisson", label="Poisson"),
            ft.Radio(value="binomial", label="Binomial"),
            ft.Radio(value="t_student", label="t-Student"),
            ft.Radio(value="chi_cuadrado", label="Chi-Cuadrado (χ²)"),
        ], spacing=2)
    )

    # Botón para actualizar gráfico con parámetros modificados
    btn_actualizar_grafico = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.REFRESH, color=ACCENT_GREEN, size=18),
            ft.Text("Actualizar Gráfico", size=12, color=ACCENT_GREEN)
        ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
        on_click=on_actualizar_grafico,
        padding=ft.Padding(12, 8, 12, 8),
        border_radius=8,
        border=ft.Border.all(1, ACCENT_GREEN)
    )

    seccion_distribucion = crear_card(
        ft.Column([
            crear_seccion_titulo("DISTRIBUCIÓN"),
            ft.Container(height=8),
            radio_distribucion
        ])
    )

    # --- Sección Operación (dinámica) ---
    input_valor = ft.TextField(
        label="Valor (x)",
        value="0",
        bgcolor="#1f2937",
        expand=True,
        height=55
    )
    
    input_n = ft.TextField(
        label="N (Simulación)",
        value="10",
        bgcolor="#1f2937",
        expand=True,
        height=55,
        visible=False
    )

    # Contenedor para campos dinámicos
    campos_dinamicos = ft.Container(
        content=ft.Row([input_valor], spacing=12),
        padding=ft.Padding(0, 10, 0, 0)
    )

    def on_operacion_change(e):
        """Cambia los campos visibles según la operación seleccionada"""
        op = e.control.value
        if op == "prob":
            input_valor.label = "Valor (x)"
            input_valor.visible = True
            input_n.visible = False
            campos_dinamicos.content = ft.Row([input_valor], spacing=12)
        elif op == "dato":
            input_valor.label = "Probabilidad (P)"
            input_valor.value = "0.5"
            input_valor.visible = True
            input_n.visible = False
            campos_dinamicos.content = ft.Row([input_valor], spacing=12)
        elif op == "sim":
            input_valor.visible = False
            input_n.visible = True
            campos_dinamicos.content = ft.Row([input_n], spacing=12)
        page.update()

    radio_operacion = ft.RadioGroup(
        content=ft.Column([
            ft.Radio(value="prob", label="Buscar Probabilidad"),
            ft.Radio(value="dato", label="Buscar Dato"),
            ft.Radio(value="sim", label="Simular"),
        ], spacing=4),
        value="prob",
        on_change=on_operacion_change
    )

    seccion_operacion = crear_card(
        ft.Column([
            crear_seccion_titulo("OPERACIÓN"),
            ft.Container(height=8),
            radio_operacion,
            campos_dinamicos
        ])
    )

    # --- Resultados ---
    resultado_container = ft.Container(visible=False)

    def mostrar_resultado_simple(texto):
        """Muestra resultado de probabilidad/dato"""
        resultado_container.content = crear_card(
            ft.Text(texto, size=16, weight=ft.FontWeight.BOLD, color=ACCENT_GREEN)
        )
        resultado_container.visible = True
        page.update()

    def mostrar_resultado_simulacion(datos):
        """Muestra resultados de simulación como chips"""
        # Limitar a 20 chips para no sobrecargar la UI
        datos_mostrar = datos[:20] if len(datos) > 20 else datos
        chips = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(f"{d:.4f}", size=12, color=ACCENT_GREEN),
                    bgcolor="#1a332e",
                    border_radius=6,
                    padding=ft.Padding(10, 6, 10, 6)
                ) for d in datos_mostrar
            ],
            wrap=True,
            spacing=8,
            run_spacing=8
        )
        extra_text = f" (mostrando 20 de {len(datos)})" if len(datos) > 20 else ""
        resultado_container.content = crear_card(
            ft.Column([
                ft.Text(f"Resultados de Simulación ({len(datos)}){extra_text}:", size=12, color=TEXT_MUTED),
                ft.Container(height=8),
                chips
            ])
        )
        resultado_container.visible = True
        page.update()

    # --- Botón Calcular ---
    def on_calcular(e):
        try:
            dist_id = radio_distribucion.value
            op = radio_operacion.value
            
            # Obtener valores de los parámetros
            params = [float(field.value) for field in param_fields]

            if op == "prob":
                val = float(input_valor.value)
                res = EstadisticaLogic.calcular_probabilidad(dist_id, params, val)
                if isinstance(res, str):
                    mostrar_resultado_simple(res)
                else:
                    mostrar_resultado_simple(f"P(X ≤ {val}) = {res:.6f}")
            elif op == "dato":
                prob = float(input_valor.value)
                res = EstadisticaLogic.calcular_dato(dist_id, params, prob)
                if isinstance(res, str):
                    mostrar_resultado_simple(res)
                else:
                    mostrar_resultado_simple(f"X = {res:.6f}")
            elif op == "sim":
                n = int(input_n.value)
                datos = EstadisticaLogic.simular(dist_id, params, n)
                mostrar_resultado_simulacion(list(datos))
        except Exception as ex:
            mostrar_resultado_simple(f"Error: {ex}")

    btn_calcular = ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.GRID_VIEW, color="#000000", size=20),
                ft.Text("Calcular", size=16, weight=ft.FontWeight.BOLD, color="#000000")
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8
        ),
        bgcolor=ACCENT_GREEN,
        border_radius=10,
        padding=ft.Padding(0, 14, 0, 14),
        margin=ft.Margin(0, 8, 0, 8),
        on_click=on_calcular
    )

    # --- Vista Distribuciones completa ---
    vista_distribuciones = ft.Container(
        content=ft.Column([
            header,
            ft.Container(
                content=ft.Column([
                    seccion_distribucion,
                    seccion_parametros,
                    btn_actualizar_grafico,
                    seccion_grafico,
                    seccion_operacion,
                    btn_calcular,
                    resultado_container
                ], scroll=ft.ScrollMode.AUTO, expand=True),
                padding=ft.Padding(16, 0, 16, 0),
                expand=True
            )
        ], expand=True),
        expand=True
    )

    # ==========================================
    # PANTALLA 2: TABLAS ESTADÍSTICAS
    # ==========================================
    
    # Estado para la búsqueda
    search_value_tablas = ft.TextField(
        label="",
        hint_text="Buscar valor (ej: 0.5)",
        prefix_icon=ft.Icons.SEARCH,
        bgcolor="#1f2937",
        border_color="#3b82f6",
        focused_border_color=ACCENT_GREEN,
        height=50
    )
    
    # Contenedor para la tabla seleccionada
    tabla_container = ft.Container(expand=True)
    
    def generar_tabla_z(highlight_z=None):
        """Genera la tabla Z (distribución normal estándar)"""
        columnas = [
            ft.DataColumn(ft.Text("Z", weight=ft.FontWeight.BOLD, color=TEXT_MUTED, size=12))
        ]
        for i in range(10):
            columnas.append(
                ft.DataColumn(ft.Text(f".0{i}", weight=ft.FontWeight.BOLD, color=TEXT_MUTED, size=12))
            )
        
        filas = []
        for z_int in range(0, 40):  # Z de 0.0 a 3.9
            z_base = z_int / 10
            celdas = []
            
            # Determinar si esta fila debe resaltarse
            highlight_row = False
            if highlight_z is not None:
                try:
                    hz = float(highlight_z)
                    if abs(z_base - (hz - (hz % 0.1))) < 0.01:
                        highlight_row = True
                except:
                    pass
            
            # Primera celda: valor Z base
            celdas.append(ft.DataCell(
                ft.Text(f"{z_base:.1f}", weight=ft.FontWeight.BOLD, 
                       color=ACCENT_GREEN if highlight_row else "#ffffff", size=12)
            ))
            
            # Celdas de valores
            for decimal in range(10):
                z = z_base + decimal / 100
                prob = stats.norm.cdf(z)
                
                # Verificar si esta celda específica debe resaltarse
                cell_highlight = False
                if highlight_z is not None:
                    try:
                        hz = float(highlight_z)
                        if abs(z - hz) < 0.001:
                            cell_highlight = True
                    except:
                        pass
                
                celdas.append(ft.DataCell(
                    ft.Text(f"{prob:.4f}", 
                           color=ACCENT_GREEN if cell_highlight else ("#c9d1d9" if not highlight_row else "#a5d6a7"),
                           weight=ft.FontWeight.BOLD if cell_highlight else ft.FontWeight.NORMAL,
                           size=12)
                ))
            
            filas.append(ft.DataRow(cells=celdas))
        
        return ft.DataTable(
            columns=columnas,
            rows=filas,
            border=ft.Border.all(1, "#30363d"),
            border_radius=8,
            vertical_lines=ft.BorderSide(1, "#30363d"),
            horizontal_lines=ft.BorderSide(1, "#30363d"),
            heading_row_color="#1f2937",
            data_row_color={"hovered": "#21262d"},
            column_spacing=20
        )
    
    def generar_tabla_t(highlight_df=None):
        """Genera la tabla t-Student con valores críticos"""
        # Niveles de significancia comunes (dos colas)
        alphas = [0.10, 0.05, 0.025, 0.01, 0.005]
        
        columnas = [
            ft.DataColumn(ft.Text("df", weight=ft.FontWeight.BOLD, color=TEXT_MUTED, size=12))
        ]
        for alpha in alphas:
            columnas.append(
                ft.DataColumn(ft.Text(f"α={alpha}", weight=ft.FontWeight.BOLD, color=TEXT_MUTED, size=11))
            )
        
        filas = []
        dfs = list(range(1, 31)) + [40, 50, 60, 80, 100, 120]
        
        for df in dfs:
            celdas = []
            
            # Determinar si esta fila debe resaltarse
            highlight_row = False
            if highlight_df is not None:
                try:
                    hdf = int(float(highlight_df))
                    if df == hdf:
                        highlight_row = True
                except:
                    pass
            
            celdas.append(ft.DataCell(
                ft.Text(str(df), weight=ft.FontWeight.BOLD, 
                       color=ACCENT_GREEN if highlight_row else "#ffffff", size=12)
            ))
            
            for alpha in alphas:
                # Valor crítico t para dos colas
                t_crit = stats.t.ppf(1 - alpha/2, df)
                celdas.append(ft.DataCell(
                    ft.Text(f"{t_crit:.4f}", 
                           color=ACCENT_GREEN if highlight_row else "#c9d1d9", size=12)
                ))
            
            filas.append(ft.DataRow(cells=celdas))
        
        return ft.DataTable(
            columns=columnas,
            rows=filas,
            border=ft.Border.all(1, "#30363d"),
            border_radius=8,
            vertical_lines=ft.BorderSide(1, "#30363d"),
            horizontal_lines=ft.BorderSide(1, "#30363d"),
            heading_row_color="#1f2937",
            data_row_color={"hovered": "#21262d"},
            column_spacing=25
        )
    
    def generar_tabla_chi2(highlight_df=None):
        """Genera la tabla Chi-cuadrado con valores críticos"""
        # Niveles de significancia comunes
        alphas = [0.995, 0.99, 0.975, 0.95, 0.90, 0.10, 0.05, 0.025, 0.01, 0.005]
        
        columnas = [
            ft.DataColumn(ft.Text("df", weight=ft.FontWeight.BOLD, color=TEXT_MUTED, size=12))
        ]
        for alpha in alphas:
            columnas.append(
                ft.DataColumn(ft.Text(f"{alpha}", weight=ft.FontWeight.BOLD, color=TEXT_MUTED, size=10))
            )
        
        filas = []
        dfs = list(range(1, 31))
        
        for df in dfs:
            celdas = []
            
            # Determinar si esta fila debe resaltarse
            highlight_row = False
            if highlight_df is not None:
                try:
                    hdf = int(float(highlight_df))
                    if df == hdf:
                        highlight_row = True
                except:
                    pass
            
            celdas.append(ft.DataCell(
                ft.Text(str(df), weight=ft.FontWeight.BOLD, 
                       color=ACCENT_GREEN if highlight_row else "#ffffff", size=12)
            ))
            
            for alpha in alphas:
                chi2_val = stats.chi2.ppf(alpha, df)
                celdas.append(ft.DataCell(
                    ft.Text(f"{chi2_val:.3f}", 
                           color=ACCENT_GREEN if highlight_row else "#c9d1d9", size=11)
                ))
            
            filas.append(ft.DataRow(cells=celdas))
        
        return ft.DataTable(
            columns=columnas,
            rows=filas,
            border=ft.Border.all(1, "#30363d"),
            border_radius=8,
            vertical_lines=ft.BorderSide(1, "#30363d"),
            horizontal_lines=ft.BorderSide(1, "#30363d"),
            heading_row_color="#1f2937",
            data_row_color={"hovered": "#21262d"},
            column_spacing=15
        )
    
    # Estado actual de la tabla seleccionada
    tabla_actual = {"tipo": "z"}
    
    def actualizar_tabla(e=None):
        """Actualiza la tabla con el valor de búsqueda"""
        valor_busqueda = search_value_tablas.value if search_value_tablas.value else None
        
        if tabla_actual["tipo"] == "z":
            tabla = generar_tabla_z(valor_busqueda)
        elif tabla_actual["tipo"] == "t":
            tabla = generar_tabla_t(valor_busqueda)
        else:
            tabla = generar_tabla_chi2(valor_busqueda)
        
        tabla_container.content = ft.Column([
            ft.Row([tabla], scroll=ft.ScrollMode.AUTO)
        ], scroll=ft.ScrollMode.AUTO, expand=True)
        
        if page.controls:
            page.update()
    
    def on_tab_change(e):
        """Cambia entre las diferentes tablas"""
        idx = e.control.selected_index
        if idx == 0:
            tabla_actual["tipo"] = "z"
            search_value_tablas.hint_text = "Buscar Z (ej: 0.5)"
        elif idx == 1:
            tabla_actual["tipo"] = "t"
            search_value_tablas.hint_text = "Buscar df (ej: 10)"
        else:
            tabla_actual["tipo"] = "chi2"
            search_value_tablas.hint_text = "Buscar df (ej: 5)"
        
        actualizar_tabla()
    
    # Conectar evento de búsqueda
    search_value_tablas.on_change = actualizar_tabla
    
    # Tabs para seleccionar tipo de tabla
    tabs_tablas = ft.TabBar(
        tabs=[
            ft.Tab(label="Tabla Z"),
            ft.Tab(label="Tabla T"),
            ft.Tab(label="Chi²"),
        ]
    )
    tabs_tablas.selected_index = 0
    tabs_tablas.on_change = on_tab_change
    
    # Inicializar tabla Z por defecto
    tabla_container.content = ft.Column([
        ft.Row([generar_tabla_z()], scroll=ft.ScrollMode.AUTO)
    ], scroll=ft.ScrollMode.AUTO, expand=True)
    
    vista_tablas = ft.Container(
        content=ft.Tabs(
            length=3,
            content=ft.Column([
                # Header
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.TABLE_CHART, color=ACCENT_GREEN, size=28),
                        ft.Column([
                            ft.Text("Tablas Estadísticas", size=20, weight=ft.FontWeight.BOLD),
                            ft.Text("Consulta valores críticos", size=12, color=TEXT_MUTED)
                        ], spacing=2)
                    ], spacing=12),
                    padding=ft.Padding(20, 20, 20, 10)
                ),
                # Tabs
                ft.Container(
                    content=tabs_tablas,
                    padding=ft.Padding(16, 0, 16, 0)
                ),
                # Campo de búsqueda
                ft.Container(
                    content=search_value_tablas,
                    padding=ft.Padding(16, 10, 16, 10)
                ),
                # Tabla
                ft.Container(
                    content=tabla_container,
                    padding=ft.Padding(16, 0, 16, 16),
                    expand=True
                )
            ], expand=True)
        ),
        expand=True
    )

    # ==========================================
    # PANTALLA 3: CALCULADORA (Placeholder)
    # ==========================================
    vista_calculadora = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CALCULATE, color=ACCENT_GREEN, size=28),
                    ft.Column([
                        ft.Text("Calculadora", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text("Operaciones rápidas", size=12, color=TEXT_MUTED)
                    ], spacing=2)
                ], spacing=12),
                padding=20
            ),
            ft.Container(
                content=ft.Text("Próximamente...", color=TEXT_MUTED),
                padding=20
            )
        ]),
        expand=True
    )

    # ==========================================
    # PANTALLA 4: AJUSTES (Placeholder)
    # ==========================================
    vista_ajustes = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.SETTINGS, color=ACCENT_GREEN, size=28),
                    ft.Column([
                        ft.Text("Ajustes", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text("Configuración", size=12, color=TEXT_MUTED)
                    ], spacing=2)
                ], spacing=12),
                padding=20
            ),
            ft.Container(
                content=ft.Text("Próximamente...", color=TEXT_MUTED),
                padding=20
            )
        ]),
        expand=True
    )

    # ==========================================
    # NAVEGACIÓN INFERIOR
    # ==========================================
    contenedor_principal = ft.Container(content=vista_distribuciones, expand=True)

    def on_nav_change(e):
        idx = e.control.selected_index
        if idx == 0:
            contenedor_principal.content = vista_distribuciones
        elif idx == 1:
            contenedor_principal.content = vista_tablas
        elif idx == 2:
            contenedor_principal.content = vista_calculadora
        elif idx == 3:
            contenedor_principal.content = vista_ajustes
        page.update()

    nav_bar = ft.NavigationBar(
        selected_index=0,
        bgcolor=CARD_BG,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.BAR_CHART_OUTLINED,
                selected_icon=ft.Icons.BAR_CHART,
                label="Distribuciones"
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.TABLE_CHART_OUTLINED,
                selected_icon=ft.Icons.TABLE_CHART,
                label="Tablas"
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.CALCULATE_OUTLINED,
                selected_icon=ft.Icons.CALCULATE,
                label="Calculadora"
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="Ajustes"
            ),
        ],
        on_change=on_nav_change
    )

    # ==========================================
    # LAYOUT PRINCIPAL
    # ==========================================
    page.add(
        ft.Column([
            contenedor_principal,
            nav_bar
        ], expand=True, spacing=0)
    )


if __name__ == "__main__":
    ft.run(main)