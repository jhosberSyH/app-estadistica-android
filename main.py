import flet as ft
from statistics_logic import EstadisticaPura

# ==========================================
# 1. LÓGICA DE NEGOCIO (Wrapper)
# ==========================================
class EstadisticaLogic:
    
    # Configuración de parámetros por distribución
    DISTRIBUCIONES = {
        "normal": {"nombre": "Normal (Gaussiana)", "params": [("Media (μ)", "0"), ("Desviación (σ)", "1")]},
        "uniforme": {"nombre": "Uniforme Continua", "params": [("a (mínimo)", "0"), ("b (máximo)", "1")]},
        "exponencial": {"nombre": "Exponencial", "params": [("Lambda (λ)", "1")]},
        "poisson": {"nombre": "Poisson", "params": [("Lambda (λ)", "3")]},
        "binomial": {"nombre": "Binomial", "params": [("n (ensayos)", "10"), ("p (probabilidad)", "0.5")]},
        "t_student": {"nombre": "t-Student", "params": [("Grados de libertad (ν)", "10")]},
        "chi_cuadrado": {"nombre": "Chi-Cuadrado (χ²)", "params": [("Grados de libertad (k)", "5")]},
        "fisher_f": {"nombre": "Fisher F", "params": [("gl numerador (d₁)", "5"), ("gl denominador (d₂)", "10")]},
    }

    @staticmethod
    def generar_grafico(dist_id, params):
        """Genera el control gráfico Flet directamente"""
        try:
            chart = EstadisticaPura.generar_grafico_dispatch(dist_id, params)
            title = EstadisticaLogic.DISTRIBUCIONES[dist_id]["nombre"]
            return chart, title
        except Exception as e:
            return ft.Text(f"Error gráfico: {e}"), "Error"

    @staticmethod
    def calcular_probabilidad(dist_id, params, valor):
        """Calcula P(X <= valor)"""
        try:
            if dist_id == "normal":
                return EstadisticaPura.normal_cdf(valor, params[0], params[1])
            elif dist_id == "exponencial":
                return EstadisticaPura.exponential_cdf(valor, params[0])
            elif dist_id == "poisson":
                # Poisson CDF sumando PMFs (simple)
                lambd = params[0]
                k = int(valor)
                return sum(EstadisticaPura.poisson_pmf(i, lambd) for i in range(k + 1))
            elif dist_id == "binomial":
                n, p = params
                k = int(valor)
                return sum(EstadisticaPura.binomial_pmf(i, n, p) for i in range(k + 1))
            elif dist_id == "t_student":
                return EstadisticaPura.t_cdf(valor, params[0])
            elif dist_id == "chi_cuadrado":
                # Chi2 CDF via integration
                prob = 0.0
                dt = 0.1
                t = 0.0
                while t < valor:
                    prob += EstadisticaPura.chi2_pdf(t, params[0]) * dt
                    t += dt
                return min(max(prob, 0), 1)
            elif dist_id == "fisher_f":
                return EstadisticaPura.f_cdf(valor, params[0], params[1])
            # Chi2 y uniforme no implementados en simple pure logic full cdf yet for "calcular_probabilidad" exactly as scipy
            # Implementing basics
            return 0.0
        except Exception as e:
            return f"Error: {e}"

    @staticmethod
    def calcular_dato(dist_id, params, probabilidad):
        """Calcula el valor X tal que P(X <= x) = probabilidad"""
        try:
            if dist_id == "normal":
                return EstadisticaPura.normal_ppf(probabilidad, params[0], params[1])
            elif dist_id == "t_student":
                return EstadisticaPura.t_ppf(probabilidad, params[0])
            elif dist_id == "chi_cuadrado":
                return EstadisticaPura.chi2_ppf(probabilidad, params[0])
            elif dist_id == "fisher_f":
                return EstadisticaPura.f_ppf(probabilidad, params[0], params[1])
            return 0.0
        except Exception as e:
            return f"Error: {e}"

    @staticmethod
    def simular(dist_id, params, n):
        """Genera n valores aleatorios"""
        if n <= 0:
            return ["Error: N debe ser mayor que 0"]
        if n > 10000:
            n = 10000  # Limitar para evitar problemas de rendimiento
        
        results = []
        try:
            import random
            for _ in range(n):
                if dist_id == "normal":
                    results.append(random.gauss(params[0], params[1]))
                elif dist_id == "exponencial":
                    results.append(random.expovariate(params[0]))
                elif dist_id == "poisson":
                    # Simple poisson generator or use math logic
                    L = 2.71828 ** (-params[0])
                    k = 0
                    p = 1
                    while p > L:
                        k += 1
                        p *= random.random()
                    results.append(k - 1)
                elif dist_id == "uniforme":
                    results.append(random.uniform(params[0], params[1]))
                else:
                    results.append(0.0)
            return results
        except ValueError as e:
            return [f"Error de valor: {e}"]
        except Exception as e:
            return [f"Error: {e}"]


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

    # --- Sección Fórmula (reemplaza gráfico) ---
    formula_titulo = ft.Text("FÓRMULA", size=12, weight=ft.FontWeight.W_500, color=TEXT_MUTED)
    formula_texto = ft.Text("", size=14, color="#ffffff", selectable=True)
    formula_con_valores = ft.Text("", size=14, color=ACCENT_GREEN, weight=ft.FontWeight.BOLD, selectable=True)
    
    seccion_formula = ft.Container(
        content=ft.Column([
            formula_titulo,
            ft.Container(height=8),
            formula_texto,
            ft.Container(height=4),
            formula_con_valores
        ]),
        bgcolor=CARD_BG,
        border_radius=12,
        padding=15,
        margin=ft.Margin(0, 0, 0, 12),
        visible=False
    )

    # Fórmulas por distribución
    FORMULAS = {
        "normal": {
            "nombre": "Normal",
            "formula": "Z = (X - μ) / σ",
            "formula_fn": lambda x, mu, sigma: f"Z = ({x} - {mu}) / {sigma} = {(x - mu) / sigma:.4f}" if sigma != 0 else "Error: σ = 0"
        },
        "uniforme": {
            "nombre": "Uniforme",
            "formula": "P(X ≤ x) = (x - a) / (b - a)",
            "formula_fn": lambda x, a, b: f"P = ({x} - {a}) / ({b} - {a}) = {(x - a) / (b - a):.4f}" if b != a else "Error: a = b"
        },
        "exponencial": {
            "nombre": "Exponencial",
            "formula": "P(X ≤ x) = 1 - e^(-λx)",
            "formula_fn": lambda x, lambd: f"P = 1 - e^(-{lambd}×{x}) = {1 - 2.71828**(-lambd * x):.4f}"
        },
        "poisson": {
            "nombre": "Poisson",
            "formula": "P(X = k) = (λ^k × e^(-λ)) / k!",
            "formula_fn": lambda k, lambd: f"P = ({lambd}^{int(k)} × e^(-{lambd})) / {int(k)}!"
        },
        "binomial": {
            "nombre": "Binomial",
            "formula": "P(X = k) = C(n,k) × p^k × (1-p)^(n-k)",
            "formula_fn": lambda k, n, p: f"P = C({int(n)},{int(k)}) × {p}^{int(k)} × {1-p:.2f}^{int(n-k)}"
        },
        "t_student": {
            "nombre": "t-Student",
            "formula": "t = (X̄ - μ) / (s / √n)",
            "formula_fn": lambda t, df: f"t = {t:.4f}, df = {int(df)}"
        },
        "chi_cuadrado": {
            "nombre": "Chi-Cuadrado",
            "formula": "χ² = Σ((O - E)² / E)",
            "formula_fn": lambda x, k: f"χ² = {x:.4f}, k = {int(k)}"
        },
        "fisher_f": {
            "nombre": "Fisher F",
            "formula": "F = S₁²/S₂² = (Var₁/Var₂)",
            "formula_fn": lambda f, d1, d2: f"F = {f:.4f}, gl = ({int(d1)}, {int(d2)})"
        }
    }

    def mostrar_formula(dist_id, params, valor=None):
        """Muestra la fórmula de la distribución con los valores"""
        if dist_id in FORMULAS:
            info = FORMULAS[dist_id]
            formula_texto.value = f"{info['nombre']}: {info['formula']}"
            if valor is not None:
                try:
                    if dist_id == "normal":
                        formula_con_valores.value = info["formula_fn"](valor, params[0], params[1])
                    elif dist_id == "uniforme":
                        formula_con_valores.value = info["formula_fn"](valor, params[0], params[1])
                    elif dist_id == "exponencial":
                        formula_con_valores.value = info["formula_fn"](valor, params[0])
                    elif dist_id == "poisson":
                        formula_con_valores.value = info["formula_fn"](valor, params[0])
                    elif dist_id == "binomial":
                        formula_con_valores.value = info["formula_fn"](valor, params[0], params[1])
                    elif dist_id == "t_student":
                        formula_con_valores.value = info["formula_fn"](valor, params[0])
                    elif dist_id == "chi_cuadrado":
                        formula_con_valores.value = info["formula_fn"](valor, params[0])
                    elif dist_id == "fisher_f":
                        formula_con_valores.value = info["formula_fn"](valor, params[0], params[1])
                except Exception as ex:
                    formula_con_valores.value = f"Error: {ex}"
            else:
                formula_con_valores.value = ""
            seccion_formula.visible = True
        else:
            seccion_formula.visible = False


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
        
        # Mostrar fórmula de la distribución
        mostrar_formula(dist_id, params_valores)
        
        if page.controls:  # Solo actualizar si la página ya tiene controles
            page.update()

    # Inicializar parámetros con distribución normal
    actualizar_parametros("normal")

    def on_dist_changed(e):
        """Handler que se llama cuando cambia la distribución seleccionada"""
        actualizar_parametros(e.control.value)

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
            ft.Radio(value="fisher_f", label="Fisher F"),
        ], spacing=2)
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
        elif op == "media_muestral":
            input_valor.label = "Valor (X̄)"
            input_valor.visible = True
            input_n.label = "Tamaño muestra (n)"
            input_n.visible = True
            campos_dinamicos.content = ft.Row([input_valor, input_n], spacing=12)
        elif op == "sim":
            input_valor.visible = False
            input_n.label = "Cantidad (N)"
            input_n.visible = True
            campos_dinamicos.content = ft.Row([input_n], spacing=12)
        page.update()

    radio_operacion = ft.RadioGroup(
        content=ft.Column([
            ft.Radio(value="prob", label="Buscar Probabilidad"),
            ft.Radio(value="dato", label="Buscar Dato"),
            ft.Radio(value="media_muestral", label="Media Muestral (X̄)"),
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
                
                # Mostrar fórmula con valores
                mostrar_formula(dist_id, params, val)
                
                if isinstance(res, str):
                    mostrar_resultado_simple(res)
                else:
                    # Mostrar ambas probabilidades
                    prob_menor = res
                    prob_mayor = 1 - res
                    resultado_container.content = crear_card(
                        ft.Column([
                            ft.Text("📊 RESULTADOS", size=12, weight=ft.FontWeight.BOLD, color=ACCENT_GREEN),
                            ft.Container(height=8),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(f"P(X ≤ {val})", size=12, color=TEXT_MUTED),
                                    ft.Text(f"{prob_menor:.6f}", size=20, weight=ft.FontWeight.BOLD, color=ACCENT_GREEN)
                                ]),
                                bgcolor="#1f2937",
                                border_radius=8,
                                padding=12
                            ),
                            ft.Container(height=8),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(f"P(X > {val})", size=12, color=TEXT_MUTED),
                                    ft.Text(f"{prob_mayor:.6f}", size=20, weight=ft.FontWeight.BOLD, color="#f59e0b")
                                ]),
                                bgcolor="#1f2937",
                                border_radius=8,
                                padding=12
                            ),
                        ])
                    )
                    resultado_container.visible = True
                    page.update()
            elif op == "dato":
                prob = float(input_valor.value)
                res = EstadisticaLogic.calcular_dato(dist_id, params, prob)
                
                # Mostrar fórmula
                mostrar_formula(dist_id, params, res if not isinstance(res, str) else 0)
                
                if isinstance(res, str):
                    mostrar_resultado_simple(res)
                else:
                    resultado_container.content = crear_card(
                        ft.Column([
                            ft.Text("📊 RESULTADO", size=12, weight=ft.FontWeight.BOLD, color=ACCENT_GREEN),
                            ft.Container(height=8),
                            ft.Text(f"Para P = {prob}", size=12, color=TEXT_MUTED),
                            ft.Text(f"X = {res:.6f}", size=20, weight=ft.FontWeight.BOLD, color=ACCENT_GREEN),
                        ])
                    )
                    resultado_container.visible = True
                    page.update()
            elif op == "media_muestral":
                # Cálculo de media muestral usando Teorema Central del Límite
                x_bar = float(input_valor.value)
                n_muestra = int(input_n.value)
                
                if dist_id == "normal":
                    mu = params[0]
                    sigma = params[1]
                    # Error estándar de la media
                    sigma_x_bar = sigma / (n_muestra ** 0.5)
                    # Estandarizar
                    z = (x_bar - mu) / sigma_x_bar
                    # Calcular probabilidad
                    prob = EstadisticaLogic.calcular_probabilidad("normal", [0, 1], z)
                    
                    if isinstance(prob, str):
                        mostrar_resultado_simple(prob)
                    else:
                        prob_mayor = 1 - prob
                        resultado_container.content = crear_card(
                            ft.Column([
                                ft.Text("📊 MEDIA MUESTRAL (X̄)", size=12, weight=ft.FontWeight.BOLD, color=ACCENT_GREEN),
                                ft.Container(height=8),
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text("Fórmula:", size=10, color=TEXT_MUTED),
                                        ft.Text(f"σ_X̄ = σ/√n = {sigma}/√{n_muestra} = {sigma_x_bar:.4f}", size=12),
                                        ft.Text(f"Z = (X̄ - μ)/σ_X̄ = ({x_bar} - {mu})/{sigma_x_bar:.4f} = {z:.4f}", size=12),
                                    ]),
                                    bgcolor="#1f2937",
                                    border_radius=8,
                                    padding=12
                                ),
                                ft.Container(height=8),
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text(f"P(X̄ ≤ {x_bar})", size=12, color=TEXT_MUTED),
                                        ft.Text(f"{prob:.6f}", size=20, weight=ft.FontWeight.BOLD, color=ACCENT_GREEN)
                                    ]),
                                    bgcolor="#1f2937",
                                    border_radius=8,
                                    padding=12
                                ),
                                ft.Container(height=8),
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text(f"P(X̄ > {x_bar})", size=12, color=TEXT_MUTED),
                                        ft.Text(f"{prob_mayor:.6f}", size=20, weight=ft.FontWeight.BOLD, color="#f59e0b")
                                    ]),
                                    bgcolor="#1f2937",
                                    border_radius=8,
                                    padding=12
                                ),
                            ])
                        )
                        resultado_container.visible = True
                        page.update()
                else:
                    mostrar_resultado_simple("Media muestral solo disponible para Distribución Normal")
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
        on_click=on_calcular,
        ink=True,
        animate=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
        animate_scale=ft.Animation(100, ft.AnimationCurve.EASE_IN_OUT),
        on_hover=lambda e: setattr(e.control, 'scale', 1.02 if e.data == "true" else 1.0) or page.update()
    )

    # --- Vista Distribuciones completa ---
    vista_distribuciones = ft.Container(
        content=ft.Column([
            header,
            ft.Container(
                content=ft.Column([
                    seccion_distribucion,
                    seccion_parametros,
                    seccion_formula,
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
                prob = EstadisticaPura.normal_cdf(z, 0, 1)
                
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
                t_crit = EstadisticaPura.t_ppf(1 - alpha/2, df)
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
                chi2_val = EstadisticaPura.chi2_ppf(alpha, df)
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
    
    # Estado de tab seleccionado
    tab_seleccionado = {"valor": "z"}
    
    def crear_tab_btn(texto, valor):
        """Crea un botón de tab"""
        is_selected = tab_seleccionado["valor"] == valor
        return ft.Container(
            content=ft.Text(
                texto, 
                size=14, 
                weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL,
                color=ACCENT_GREEN if is_selected else TEXT_MUTED
            ),
            bgcolor="#1a332e" if is_selected else "transparent",
            border_radius=8,
            padding=ft.Padding(16, 10, 16, 10),
            on_click=lambda e, v=valor: on_tab_click(v),
            ink=True
        )
    
    tabs_row = ft.Row(spacing=8)
    
    def actualizar_tabs():
        """Actualiza la apariencia de los tabs"""
        tabs_row.controls = [
            crear_tab_btn("Tabla Z", "z"),
            crear_tab_btn("Tabla T", "t"),
            crear_tab_btn("Chi²", "chi2"),
        ]
    
    def on_tab_click(valor):
        """Cambia entre las diferentes tablas"""
        tab_seleccionado["valor"] = valor
        tabla_actual["tipo"] = valor
        
        if valor == "z":
            search_value_tablas.hint_text = "Buscar Z (ej: 0.5)"
        elif valor == "t":
            search_value_tablas.hint_text = "Buscar df (ej: 10)"
        else:
            search_value_tablas.hint_text = "Buscar df (ej: 5)"
        
        actualizar_tabs()
        actualizar_tabla()
        page.update()
    
    # Inicializar tabs
    actualizar_tabs()
    
    # Inicializar tabla Z por defecto
    tabla_container.content = ft.Column([
        ft.Row([generar_tabla_z()], scroll=ft.ScrollMode.AUTO)
    ], scroll=ft.ScrollMode.AUTO, expand=True)
    
    vista_tablas = ft.Container(
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
                content=tabs_row,
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
        ], expand=True),
        expand=True
    )

    # --- Calculadora: Lógica de estadísticas descriptivas ---
    def calcular_estadisticas_descriptivas(datos):
        """Calcula estadísticas descriptivas básicas"""
        if not datos:
            return {}
        
        n = len(datos)
        suma = sum(datos)
        media = suma / n
        
        # Ordenar para mediana
        ordenados = sorted(datos)
        if n % 2 == 0:
            mediana = (ordenados[n//2 - 1] + ordenados[n//2]) / 2
        else:
            mediana = ordenados[n//2]
        
        # Moda (valor más frecuente)
        frecuencias = {}
        for d in datos:
            frecuencias[d] = frecuencias.get(d, 0) + 1
        max_freq = max(frecuencias.values())
        modas = [k for k, v in frecuencias.items() if v == max_freq]
        moda = modas[0] if len(modas) == 1 else "Múltiple"
        
        # Varianza y desviación estándar
        varianza = sum((x - media) ** 2 for x in datos) / n
        desv_std = varianza ** 0.5
        
        # Varianza muestral (n-1)
        varianza_muestral = sum((x - media) ** 2 for x in datos) / (n - 1) if n > 1 else 0
        desv_std_muestral = varianza_muestral ** 0.5
        
        return {
            "n": n,
            "suma": suma,
            "media": media,
            "mediana": mediana,
            "moda": moda,
            "min": min(datos),
            "max": max(datos),
            "rango": max(datos) - min(datos),
            "varianza": varianza,
            "desv_std": desv_std,
            "varianza_m": varianza_muestral,
            "desv_std_m": desv_std_muestral
        }
    
    # Input de datos
    calc_input = ft.TextField(
        label="Datos (separados por comas o espacios)",
        hint_text="Ej: 1, 2, 3, 4, 5 o 1 2 3 4 5",
        bgcolor="#1f2937",
        border_color="#3b82f6",
        focused_border_color=ACCENT_GREEN,
        multiline=True,
        min_lines=2,
        max_lines=4
    )
    
    # Contenedor de resultados
    calc_resultados = ft.Container(visible=False)
    
    def crear_stat_card(titulo, valor, icono, color=ACCENT_GREEN):
        """Crea una tarjeta para mostrar una estadística"""
        return ft.Container(
            content=ft.Row([
                ft.Icon(icono, color=color, size=24),
                ft.Column([
                    ft.Text(titulo, size=11, color=TEXT_MUTED),
                    ft.Text(str(valor) if isinstance(valor, str) else f"{valor:.4f}", 
                            size=16, weight=ft.FontWeight.BOLD, color=color)
                ], spacing=2, expand=True)
            ], spacing=12),
            bgcolor="#1f2937",
            border_radius=10,
            padding=12
        )
    
    def on_calcular_stats(e):
        """Procesa los datos y muestra estadísticas"""
        try:
            texto = calc_input.value.strip()
            if not texto:
                calc_resultados.visible = False
                page.update()
                return
            
            # Parsear datos (comas o espacios)
            texto = texto.replace(",", " ")
            datos = [float(x.strip()) for x in texto.split() if x.strip()]
            
            if not datos:
                calc_resultados.visible = False
                page.update()
                return
            
            stats = calcular_estadisticas_descriptivas(datos)
            
            # Crear grid de resultados
            calc_resultados.content = ft.Column([
                ft.Text("📊 Resultados", size=14, weight=ft.FontWeight.BOLD, color=ACCENT_GREEN),
                ft.Container(height=8),
                ft.Row([
                    ft.Column([
                        crear_stat_card("Cantidad (n)", stats["n"], ft.Icons.NUMBERS),
                        crear_stat_card("Media (μ)", stats["media"], ft.Icons.SHOW_CHART),
                        crear_stat_card("Mediana", stats["mediana"], ft.Icons.ALIGN_VERTICAL_CENTER),
                        crear_stat_card("Moda", stats["moda"], ft.Icons.STAR),
                    ], spacing=8, expand=True),
                    ft.Column([
                        crear_stat_card("Suma (Σ)", stats["suma"], ft.Icons.ADD),
                        crear_stat_card("Desv. Std (σ)", stats["desv_std"], ft.Icons.STACKED_LINE_CHART),
                        crear_stat_card("Varianza (σ²)", stats["varianza"], ft.Icons.SQUARE),
                        crear_stat_card("Rango", stats["rango"], ft.Icons.SWAP_VERT),
                    ], spacing=8, expand=True),
                ], spacing=8),
                ft.Container(height=12),
                ft.Text("📐 Valores Extremos", size=12, weight=ft.FontWeight.W_500, color=TEXT_MUTED),
                ft.Container(height=4),
                ft.Row([
                    crear_stat_card("Mínimo", stats["min"], ft.Icons.ARROW_DOWNWARD, "#ef4444"),
                    crear_stat_card("Máximo", stats["max"], ft.Icons.ARROW_UPWARD, "#22c55e"),
                ], spacing=8),
                ft.Container(height=12),
                ft.Text("📏 Muestrales (n-1)", size=12, weight=ft.FontWeight.W_500, color=TEXT_MUTED),
                ft.Container(height=4),
                ft.Row([
                    crear_stat_card("Varianza (s²)", stats["varianza_m"], ft.Icons.SQUARE_OUTLINED),
                    crear_stat_card("Desv. Std (s)", stats["desv_std_m"], ft.Icons.STACKED_LINE_CHART),
                ], spacing=8),
            ], scroll=ft.ScrollMode.AUTO)
            
            calc_resultados.visible = True
            page.update()
            
        except Exception as ex:
            calc_resultados.content = ft.Text(f"Error: {ex}", color="#ef4444")
            calc_resultados.visible = True
            page.update()
    
    btn_calcular_stats = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.CALCULATE, color="#000000", size=20),
            ft.Text("Calcular Estadísticas", size=14, weight=ft.FontWeight.BOLD, color="#000000")
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
        bgcolor=ACCENT_GREEN,
        border_radius=10,
        padding=ft.Padding(0, 12, 0, 12),
        on_click=on_calcular_stats
    )
    
    vista_calculadora = ft.Container(
        content=ft.Column([
            # Header
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CALCULATE, color=ACCENT_GREEN, size=28),
                    ft.Column([
                        ft.Text("Calculadora Estadística", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text("Estadísticas descriptivas", size=12, color=TEXT_MUTED)
                    ], spacing=2)
                ], spacing=12),
                padding=ft.Padding(20, 20, 20, 10)
            ),
            # Contenido
            ft.Container(
                content=ft.Column([
                    crear_card(ft.Column([
                        crear_seccion_titulo("INGRESA TUS DATOS"),
                        ft.Container(height=8),
                        calc_input,
                        ft.Container(height=12),
                        btn_calcular_stats
                    ])),
                    calc_resultados
                ], scroll=ft.ScrollMode.AUTO, expand=True),
                padding=ft.Padding(16, 0, 16, 16),
                expand=True
            )
        ], expand=True),
        expand=True
    )

    # ==========================================
    # PANTALLA 4: DISTRIBUCIONES MUESTRALES
    # ==========================================
    
    # Campos de entrada para muestrales
    muestral_fields = {}
    muestral_resultado = ft.Container(visible=False)
    
    # Tipo de distribución muestral
    muestral_tipo = ft.RadioGroup(
        value="media_sigma_con",
        content=ft.Column([
            ft.Radio(value="media_sigma_con", label="Media (σ conocida)"),
            ft.Radio(value="media_sigma_des", label="Media (σ desconocida)"),
            ft.Radio(value="varianza", label="Varianza Muestral"),
            ft.Radio(value="proporcion", label="Proporción Muestral"),
            ft.Radio(value="dif_medias", label="Diferencia de Medias"),
            ft.Radio(value="dif_proporciones", label="Diferencia de Proporciones"),
            ft.Radio(value="razon_varianzas", label="Razón de Varianzas"),
        ], spacing=2)
    )
    
    # Contenedor dinámico para campos
    muestral_campos = ft.Container()
    
    # Campos por tipo
    def crear_campo(label, value="0"):
        return ft.TextField(label=label, value=value, bgcolor="#1f2937", expand=True, height=55)
    
    def actualizar_campos_muestrales(e=None):
        tipo = muestral_tipo.value
        campos = []
        
        if tipo == "media_sigma_con":
            campos = [
                ft.Row([crear_campo("X̄ (media muestral)", "70"), crear_campo("μ (media poblacional)", "70")], spacing=8),
                ft.Row([crear_campo("σ (desv. poblacional)", "5"), crear_campo("n (tamaño muestra)", "30")], spacing=8),
            ]
        elif tipo == "media_sigma_des":
            campos = [
                ft.Row([crear_campo("X̄ (media muestral)", "70"), crear_campo("μ (media poblacional)", "70")], spacing=8),
                ft.Row([crear_campo("s (desv. muestral)", "5"), crear_campo("n (tamaño muestra)", "30")], spacing=8),
            ]
        elif tipo == "varianza":
            campos = [
                ft.Row([crear_campo("S² (varianza muestral)", "25"), crear_campo("σ² (varianza poblacional)", "20")], spacing=8),
                crear_campo("n (tamaño muestra)", "30"),
            ]
        elif tipo == "proporcion":
            campos = [
                ft.Row([crear_campo("p̂ (proporción muestral)", "0.6"), crear_campo("p (proporción poblacional)", "0.5")], spacing=8),
                crear_campo("n (tamaño muestra)", "100"),
            ]
        elif tipo == "dif_medias":
            campos = [
                ft.Row([crear_campo("X̄₁", "75"), crear_campo("X̄₂", "70")], spacing=8),
                ft.Row([crear_campo("s₁", "8"), crear_campo("s₂", "7")], spacing=8),
                ft.Row([crear_campo("n₁", "30"), crear_campo("n₂", "35")], spacing=8),
            ]
        elif tipo == "dif_proporciones":
            campos = [
                ft.Row([crear_campo("p̂₁", "0.6"), crear_campo("p̂₂", "0.5")], spacing=8),
                ft.Row([crear_campo("n₁", "100"), crear_campo("n₂", "120")], spacing=8),
            ]
        elif tipo == "razon_varianzas":
            campos = [
                ft.Row([crear_campo("S₁²", "25"), crear_campo("S₂²", "20")], spacing=8),
                ft.Row([crear_campo("n₁", "30"), crear_campo("n₂", "35")], spacing=8),
            ]
        
        muestral_campos.content = ft.Column(campos, spacing=8)
        if page.controls:
            page.update()
    
    muestral_tipo.on_change = actualizar_campos_muestrales
    
    def calcular_muestral(e):
        try:
            tipo = muestral_tipo.value
            campos = muestral_campos.content.controls if muestral_campos.content else []
            
            # Extraer valores de los campos
            def get_val(row_idx, col_idx=0):
                if isinstance(campos[row_idx], ft.Row):
                    return float(campos[row_idx].controls[col_idx].value)
                return float(campos[row_idx].value)
            
            resultado = None
            
            if tipo == "media_sigma_con":
                x_bar = get_val(0, 0)
                mu = get_val(0, 1)
                sigma = get_val(1, 0)
                n = int(get_val(1, 1))
                resultado = EstadisticaPura.media_muestral_sigma_conocida(x_bar, mu, sigma, n)
                
            elif tipo == "media_sigma_des":
                x_bar = get_val(0, 0)
                mu = get_val(0, 1)
                s = get_val(1, 0)
                n = int(get_val(1, 1))
                resultado = EstadisticaPura.media_muestral_sigma_desconocida(x_bar, mu, s, n)
                
            elif tipo == "varianza":
                s2 = get_val(0, 0)
                sigma2 = get_val(0, 1)
                n = int(get_val(1))
                resultado = EstadisticaPura.varianza_muestral(s2, sigma2, n)
                
            elif tipo == "proporcion":
                p_hat = get_val(0, 0)
                p = get_val(0, 1)
                n = int(get_val(1))
                resultado = EstadisticaPura.proporcion_muestral(p_hat, p, n)
                
            elif tipo == "dif_medias":
                x1 = get_val(0, 0)
                x2 = get_val(0, 1)
                s1 = get_val(1, 0)
                s2 = get_val(1, 1)
                n1 = int(get_val(2, 0))
                n2 = int(get_val(2, 1))
                resultado = EstadisticaPura.diferencia_medias_pooled(x1, x2, s1, s2, n1, n2)
                
            elif tipo == "dif_proporciones":
                p1 = get_val(0, 0)
                p2 = get_val(0, 1)
                n1 = int(get_val(1, 0))
                n2 = int(get_val(1, 1))
                resultado = EstadisticaPura.diferencia_proporciones(p1, p2, n1, n2)
                
            elif tipo == "razon_varianzas":
                s1_2 = get_val(0, 0)
                s2_2 = get_val(0, 1)
                n1 = int(get_val(1, 0))
                n2 = int(get_val(1, 1))
                resultado = EstadisticaPura.razon_varianzas(s1_2, s2_2, n1, n2)
            
            if resultado:
                muestral_resultado.content = crear_card(
                    ft.Column([
                        ft.Text("📊 RESULTADO", size=12, weight=ft.FontWeight.BOLD, color=ACCENT_GREEN),
                        ft.Container(height=8),
                        ft.Container(
                            content=ft.Text(resultado.get("formula", ""), size=12, selectable=True),
                            bgcolor="#1f2937",
                            border_radius=8,
                            padding=12
                        ),
                        ft.Container(height=8),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("P(≤)", size=12, color=TEXT_MUTED),
                                ft.Text(f"{resultado.get('prob_menor', 0):.6f}", size=20, weight=ft.FontWeight.BOLD, color=ACCENT_GREEN)
                            ]),
                            bgcolor="#1f2937",
                            border_radius=8,
                            padding=12
                        ),
                        ft.Container(height=8),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("P(>)", size=12, color=TEXT_MUTED),
                                ft.Text(f"{resultado.get('prob_mayor', 0):.6f}", size=20, weight=ft.FontWeight.BOLD, color="#f59e0b")
                            ]),
                            bgcolor="#1f2937",
                            border_radius=8,
                            padding=12
                        ),
                    ])
                )
                muestral_resultado.visible = True
                page.update()
                
        except Exception as ex:
            muestral_resultado.content = crear_card(
                ft.Text(f"Error: {ex}", color="red", size=14)
            )
            muestral_resultado.visible = True
            page.update()
    
    btn_calcular_muestral = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.ANALYTICS, color="#000000", size=20),
            ft.Text("Calcular", size=16, weight=ft.FontWeight.BOLD, color="#000000")
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
        bgcolor=ACCENT_GREEN,
        border_radius=10,
        padding=ft.Padding(0, 14, 0, 14),
        margin=ft.Margin(0, 8, 0, 8),
        on_click=calcular_muestral,
        ink=True
    )
    
    # Inicializar campos
    actualizar_campos_muestrales()
    
    vista_muestrales = ft.Container(
        content=ft.Column([
            # Header
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.ANALYTICS, color=ACCENT_GREEN, size=28),
                    ft.Column([
                        ft.Text("Distribuciones Muestrales", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text("Inferencia estadística", size=12, color=TEXT_MUTED)
                    ], spacing=2)
                ], spacing=12),
                padding=ft.Padding(20, 20, 20, 10)
            ),
            # Contenido
            ft.Container(
                content=ft.Column([
                    crear_card(ft.Column([
                        crear_seccion_titulo("TIPO DE DISTRIBUCIÓN"),
                        ft.Container(height=8),
                        muestral_tipo
                    ])),
                    crear_card(ft.Column([
                        crear_seccion_titulo("PARÁMETROS"),
                        ft.Container(height=8),
                        muestral_campos
                    ])),
                    btn_calcular_muestral,
                    muestral_resultado
                ], scroll=ft.ScrollMode.AUTO, expand=True),
                padding=ft.Padding(16, 0, 16, 16),
                expand=True
            )
        ], expand=True),
        expand=True
    )

    # ==========================================
    # PANTALLA 5: AJUSTES
    # ==========================================
    
    # Estado de configuración
    app_config = {
        "decimales": 4
    }
    
    def on_decimales_change(e):
        """Cambia la precisión decimal"""
        app_config["decimales"] = int(e.control.value)
    
    decimales_dropdown = ft.Dropdown(
        value="4",
        options=[
            ft.dropdown.Option("2", "2 decimales"),
            ft.dropdown.Option("4", "4 decimales"),
            ft.dropdown.Option("6", "6 decimales"),
            ft.dropdown.Option("8", "8 decimales"),
        ],
        bgcolor="#1f2937",
        width=200
    )
    
    def crear_ajuste_item(icono, titulo, descripcion, control):
        """Crea un item de ajuste con icono, texto y control"""
        return ft.Container(
            content=ft.Row([
                ft.Icon(icono, color=ACCENT_GREEN, size=24),
                ft.Column([
                    ft.Text(titulo, size=14, weight=ft.FontWeight.W_500),
                    ft.Text(descripcion, size=11, color=TEXT_MUTED)
                ], spacing=2, expand=True),
                control
            ], spacing=16),
            bgcolor="#1f2937",
            border_radius=10,
            padding=16,
            margin=ft.Margin(0, 0, 0, 8)
        )
    
    vista_ajustes = ft.Container(
        content=ft.Column([
            # Header
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.SETTINGS, color=ACCENT_GREEN, size=28),
                    ft.Column([
                        ft.Text("Ajustes", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text("Personaliza la aplicación", size=12, color=TEXT_MUTED)
                    ], spacing=2)
                ], spacing=12),
                padding=ft.Padding(20, 20, 20, 10)
            ),
            # Contenido
            ft.Container(
                content=ft.Column([
                    # Sección Configuración
                    crear_card(ft.Column([
                        crear_seccion_titulo("CONFIGURACIÓN"),
                        ft.Container(height=12),
                        crear_ajuste_item(
                            ft.Icons.NUMBERS,
                            "Precisión Decimal",
                            "Cantidad de decimales en resultados",
                            decimales_dropdown
                        ),
                    ])),
                    # Sección Info
                    crear_card(ft.Column([
                        crear_seccion_titulo("INFORMACIÓN"),
                        ft.Container(height=12),
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.INFO_OUTLINE, color=TEXT_MUTED, size=20),
                                    ft.Text("App Estadística", size=14, weight=ft.FontWeight.W_500),
                                ], spacing=12),
                                ft.Container(height=8),
                                ft.Text("Versión 1.0.0", size=12, color=TEXT_MUTED),
                                ft.Text("Desarrollado con Flet & Python", size=12, color=TEXT_MUTED),
                                ft.Container(height=12),
                                ft.Text("Incluye:", size=12, color=TEXT_MUTED),
                                ft.Text("• 7 distribuciones de probabilidad", size=11, color=TEXT_MUTED),
                                ft.Text("• 7 distribuciones muestrales", size=11, color=TEXT_MUTED),
                                ft.Text("• Tablas Z, t-Student y Chi²", size=11, color=TEXT_MUTED),
                                ft.Text("• Calculadora de estadísticas descriptivas", size=11, color=TEXT_MUTED),
                            ]),
                            padding=ft.Padding(12, 12, 12, 12),
                            bgcolor="#1f2937",
                            border_radius=10
                        )
                    ])),
                    # Sección Desarrollador
                    crear_card(ft.Column([
                        crear_seccion_titulo("DESARROLLADOR"),
                        ft.Container(height=12),
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.PERSON, color=ACCENT_GREEN, size=24),
                                    ft.Text("Jhosber Ynojosa", size=16, weight=ft.FontWeight.BOLD),
                                ], spacing=12),
                                ft.Container(height=4),
                                ft.Text("Estudiante de Computación", size=12, color=TEXT_MUTED),
                            ]),
                            padding=ft.Padding(12, 12, 12, 12),
                            bgcolor="#1f2937",
                            border_radius=10
                        )
                    ])),
                ], scroll=ft.ScrollMode.AUTO, expand=True),
                padding=ft.Padding(16, 0, 16, 16),
                expand=True
            )
        ], expand=True),
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
            contenedor_principal.content = vista_muestrales
        elif idx == 4:
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
                icon=ft.Icons.ANALYTICS_OUTLINED,
                selected_icon=ft.Icons.ANALYTICS,
                label="Muestrales"
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