
import math
import random
import flet as ft

# ==========================================
# 1. ESTADÍSTICA PURA (SIN SCIPY/NUMPY)
# ==========================================
class EstadisticaPura:
    """Implementación de funciones estadísticas usando solo math y random"""
    
    @staticmethod
    def normal_pdf(x, mu=0, sigma=1):
        """Función de Densidad de Probabilidad Normal"""
        exp_part = math.exp(-0.5 * ((x - mu) / sigma) ** 2)
        return (1 / (sigma * math.sqrt(2 * math.pi))) * exp_part

    @staticmethod
    def normal_cdf(x, mu=0, sigma=1):
        """Función de Distribución Acumulada Normal (aprox. usando erf)"""
        return 0.5 * (1 + math.erf((x - mu) / (sigma * math.sqrt(2))))
    
    @staticmethod
    def normal_ppf(p, mu=0, sigma=1):
        """Función Percentil Normal (Inversa CDF) - Aprox. Acklam"""
        # Algoritmo de Peter J. Acklam para la inversa de la normal estándar
        if p <= 0 or p >= 1:
            return 0.0 # Manejo básico de bordes
        
        # Coeficientes para la aproximación
        a1, a2, a3, a4, a5, a6 = -39.69683028665376, 220.9460984245205, -275.9285104469687, 138.3577518672690, -30.66479806614716, 2.506628277459239
        b1, b2, b3, b4, b5 = -54.47609879822406, 161.5858368580409, -155.6989798598866, 66.80131188771972, -13.28068155288572
        c1, c2, c3, c4, c5, c6 = -0.007784894002430293, -0.3223964580411365, -2.400758277161838, -2.549732539343734, 4.374664141464968, 2.938163982698783
        d1, d2, d3, d4 = 0.007784695709041462, 0.3224671290700398, 2.445134137142996, 3.754408661907416
        
        q = min(p, 1 - p)
        if q > 0.02425:
            # Región central
            u = q - 0.5
            r = u * u
            z = (((((a1 * r + a2) * r + a3) * r + a4) * r + a5) * r + a6) * u / (((((b1 * r + b2) * r + b3) * r + b4) * r + b5) * r + 1)
        else:
            # Regiones de cola
            r = math.sqrt(-2 * math.log(q))
            z = (((((c1 * r + c2) * r + c3) * r + c4) * r + c5) * r + c6) / ((((d1 * r + d2) * r + d3) * r + d4) * r + 1)
        
        if p < 0.5:
            z = -z # Si es la cola izquierda, invertimos
            
        return mu + sigma * z

    @staticmethod
    def t_pdf(x, df):
        """PDF t-Student"""
        # Gamma aproximado para evitar dependencias complejas si es necesario, 
        # pero math.gamma existe en Py3.11+. Asumimos Py3.11 disponible en build.
        try:
            from math import gamma
            term1 = gamma((df + 1) / 2) / (math.sqrt(df * math.pi) * gamma(df / 2))
            term2 = (1 + (x**2) / df) ** (-(df + 1) / 2)
            return term1 * term2
        except:
             return 0.0 # Fallback

    @staticmethod
    def t_cdf(x, df):
        """CDF t-Student (Aprox. simple para visualización)"""
        # Aproximación usando normal si df es grande, o integración numérica simple
        if df > 30:
            return EstadisticaPura.normal_cdf(x)
        # Integración numérica simple (Trapecios) desde un valor muy bajo
        t = -10.0
        dt = 0.1
        area = 0.0
        while t < x:
            area += EstadisticaPura.t_pdf(t, df) * dt
            t += dt
        return min(max(area, 0), 1)

    @staticmethod
    def t_ppf(p, df):
        """t-Student PPF (Aproximación basada en Normal)"""
        z = EstadisticaPura.normal_ppf(p)
        # Aproximación de Peizer-Pratt o similar para ajustar Z a T
        # Para APK simple, usamos Z como base y ajustamos ligeramente por grados de libertad
        if df > 30:
             return z
        return z * (df / (df - 2))**0.5 if df > 2 else z * 1.5 # Muy aproximado

    @staticmethod
    def chi2_pdf(x, k):
        """PDF Chi-Cuadrado"""
        if x <= 0: return 0.0
        try:
            from math import gamma
            num = (x ** (k/2 - 1)) * math.exp(-x/2)
            den = (2 ** (k/2)) * gamma(k/2)
            return num / den
        except:
            return 0.0

    @staticmethod
    def chi2_ppf(p, k):
        """Chi2 PPF (Aproximación Wilson-Hilferty)"""
        # Transforma Chi2 a Normal 
        if p <= 0: return 0.0
        z = EstadisticaPura.normal_ppf(p)
        return k * (1 - 2/(9*k) + z * math.sqrt(2/(9*k))) ** 3

    # Discretas
    @staticmethod
    def factorial(n):
        if n == 0: return 1
        res = 1
        for i in range(1, int(n) + 1):
            res *= i
        return res

    @staticmethod
    def combinations(n, k):
        return EstadisticaPura.factorial(n) / (EstadisticaPura.factorial(k) * EstadisticaPura.factorial(n - k))

    @staticmethod
    def binomial_pmf(k, n, p):
        if k < 0 or k > n: return 0
        comb = EstadisticaPura.combinations(n, k)
        return comb * (p ** k) * ((1 - p) ** (n - k))
    
    @staticmethod
    def poisson_pmf(k, lambd):
        if k < 0: return 0
        return (lambd ** k * math.exp(-lambd)) / EstadisticaPura.factorial(k)
    
    @staticmethod
    def exponential_pdf(x, lambd):
        if x < 0: return 0
        return lambd * math.exp(-lambd * x)

    @staticmethod
    def exponential_cdf(x, lambd):
        if x < 0: return 0
        return 1 - math.exp(-lambd * x)

    # Gráficos Flet
    @staticmethod
    def generar_chart_normal(mu, sigma):
        data_points = []
        # Rango: mu - 3sigma a mu + 3sigma
        start = mu - 4 * sigma
        end = mu + 4 * sigma
        step = (end - start) / 50
        
        curr = start
        while curr <= end:
            y = EstadisticaPura.normal_pdf(curr, mu, sigma)
            data_points.append(ft.LineChartDataPoint(curr, y))
            curr += step
            
        return ft.LineChart(
            data_series=[
                ft.LineChartData(
                    data_points=data_points,
                    color=ft.colors.CYAN,
                    stroke_width=3,
                    curved=True,
                    stroke_cap_round=True,
                )
            ],
            border=ft.Border(
                bottom=ft.BorderSide(2, ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE))
            ),
            left_axis=ft.ChartAxis(labels_size=0),
            bottom_axis=ft.ChartAxis(labels_interval=1),
            tooltip_bgcolor=ft.colors.with_opacity(0.8, ft.colors.blue_grey_900),
            min_y=0,
            expand=True
        )

    @staticmethod
    def generar_chart_t(df):
        data_points = []
        start = -4
        end = 4
        step = 0.2
        curr = start
        while curr <= end:
             y = EstadisticaPura.t_pdf(curr, df)
             data_points.append(ft.LineChartDataPoint(curr, y))
             curr += step
        
        return ft.LineChart(
             data_series=[
                ft.LineChartData(
                    data_points=data_points,
                    color=ft.colors.ORANGE,
                    stroke_width=3,
                    curved=True
                )
             ],
             min_y=0, expand=True
        )

    @staticmethod
    def generar_chart_chi2(k):
        data_points = []
        start = 0.1
        end = k * 2 + 5
        step = (end - start) / 50
        curr = start
        while curr <= end:
             y = EstadisticaPura.chi2_pdf(curr, k)
             # Limitar valores muy altos cerca de 0 para df < 2
             if y > 1.0: y = 1.0 
             data_points.append(ft.LineChartDataPoint(curr, y))
             curr += step
        
        return ft.LineChart(
             data_series=[
                ft.LineChartData(
                    data_points=data_points,
                    color=ft.colors.PURPLE,
                    stroke_width=3,
                    curved=True
                )
             ],
             min_y=0, expand=True
        )
    
    @staticmethod
    def generar_chart_binomial(n, p):
        data_points = []
        for k in range(int(n) + 1):
            y = EstadisticaPura.binomial_pmf(k, n, p)
            data_points.append(
                ft.BarChartRod(
                    from_y=0,
                    to_y=y,
                    width=20 if n < 15 else 10,
                    color=ft.colors.GREEN,
                    tooltip=f"k={k}, P={y:.4f}",
                    border_radius=4
                )
            )
        
        return ft.BarChart(
            bar_groups=[
                ft.BarChartGroup(x=i, bar_rods=[rod]) for i, rod in enumerate(data_points)
            ],
            border=ft.Border(
                bottom=ft.BorderSide(2, ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE))
            ),
            left_axis=ft.ChartAxis(labels_size=0),
            bottom_axis=ft.ChartAxis(labels_interval=1 if n < 20 else 5),
            expand=True
        )
    
    @staticmethod
    def generar_chart_poisson(lambd):
        data_points = []
        end = int(lambd * 3) + 2
        for k in range(end):
            y = EstadisticaPura.poisson_pmf(k, lambd)
            data_points.append(
                 ft.BarChartRod(
                    from_y=0,
                    to_y=y,
                    width=15,
                    color=ft.colors.INDIGO,
                    tooltip=f"k={k}, P={y:.4f}",
                    border_radius=4
                )
            )
        return ft.BarChart(
             bar_groups=[
                ft.BarChartGroup(x=i, bar_rods=[rod]) for i, rod in enumerate(data_points)
            ],
            expand=True
        )

    @staticmethod
    def generar_grafico_dispatch(dist_id, params):
        if dist_id == "normal":
             return EstadisticaPura.generar_chart_normal(params[0], params[1])
        elif dist_id == "binomial":
             return EstadisticaPura.generar_chart_binomial(params[0], params[1])
        elif dist_id == "poisson":
             return EstadisticaPura.generar_chart_poisson(params[0])
        elif dist_id == "t_student":
             return EstadisticaPura.generar_chart_t(params[0])
        elif dist_id == "chi_cuadrado":
             return EstadisticaPura.generar_chart_chi2(params[0])
        else:
             return ft.Text("Gráfico no disponible distribucion simple", color="red")
