
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

    # ==========================================
    # DISTRIBUCIÓN F (Fisher-Snedecor)
    # ==========================================
    @staticmethod
    def f_pdf(x, df1, df2):
        """PDF de la distribución F"""
        if x <= 0: return 0
        try:
            from math import gamma
            num = math.sqrt(((df1 * x) ** df1) * (df2 ** df2) / ((df1 * x + df2) ** (df1 + df2)))
            den = x * (gamma(df1/2) * gamma(df2/2) / gamma((df1 + df2)/2))
            return num / den
        except:
            return 0.0

    @staticmethod
    def f_cdf(x, df1, df2):
        """CDF F (Aproximación por integración numérica)"""
        if x <= 0: return 0
        # Integración trapezoidal simple
        dt = 0.01
        area = 0.0
        t = 0.001
        while t < x:
            area += EstadisticaPura.f_pdf(t, df1, df2) * dt
            t += dt
        return min(max(area, 0), 1)

    @staticmethod
    def f_ppf(p, df1, df2):
        """F PPF (búsqueda binaria)"""
        if p <= 0: return 0
        if p >= 1: return float('inf')
        low, high = 0.001, 100
        for _ in range(100):
            mid = (low + high) / 2
            if EstadisticaPura.f_cdf(mid, df1, df2) < p:
                low = mid
            else:
                high = mid
        return mid

    # ==========================================
    # DISTRIBUCIONES MUESTRALES
    # ==========================================
    
    @staticmethod
    def media_muestral_sigma_conocida(x_bar, mu, sigma, n):
        """
        Media muestral cuando σ es conocida
        Retorna: z, prob_menor, prob_mayor
        """
        sigma_x_bar = sigma / math.sqrt(n)
        z = (x_bar - mu) / sigma_x_bar
        prob_menor = EstadisticaPura.normal_cdf(z, 0, 1)
        prob_mayor = 1 - prob_menor
        return {
            "z": z,
            "sigma_x_bar": sigma_x_bar,
            "prob_menor": prob_menor,
            "prob_mayor": prob_mayor,
            "formula": f"Z = (X̄ - μ) / (σ/√n) = ({x_bar} - {mu}) / ({sigma}/√{n}) = {z:.4f}"
        }
    
    @staticmethod
    def media_muestral_sigma_desconocida(x_bar, mu, s, n):
        """
        Media muestral cuando σ es desconocida (usa t-Student)
        Retorna: t, prob_menor, prob_mayor
        """
        s_x_bar = s / math.sqrt(n)
        t = (x_bar - mu) / s_x_bar
        df = n - 1
        prob_menor = EstadisticaPura.t_cdf(t, df)
        prob_mayor = 1 - prob_menor
        return {
            "t": t,
            "df": df,
            "s_x_bar": s_x_bar,
            "prob_menor": prob_menor,
            "prob_mayor": prob_mayor,
            "formula": f"t = (X̄ - μ) / (s/√n) = ({x_bar} - {mu}) / ({s}/√{n}) = {t:.4f}, gl = {df}"
        }
    
    @staticmethod
    def varianza_muestral(s2, sigma2, n):
        """
        Varianza muestral usando Chi-cuadrado
        """
        df = n - 1
        chi2 = (df * s2) / sigma2
        # Buscar probabilidades
        prob_menor = 0.0
        dt = 0.1
        t = 0.0
        while t < chi2:
            prob_menor += EstadisticaPura.chi2_pdf(t, df) * dt
            t += dt
        prob_menor = min(max(prob_menor, 0), 1)
        prob_mayor = 1 - prob_menor
        return {
            "chi2": chi2,
            "df": df,
            "prob_menor": prob_menor,
            "prob_mayor": prob_mayor,
            "formula": f"χ² = (n-1)S²/σ² = ({n}-1)×{s2}/{sigma2} = {chi2:.4f}, gl = {df}"
        }
    
    @staticmethod
    def proporcion_muestral(p_hat, p, n):
        """
        Proporción muestral (aproximación normal)
        Condición: np >= 5 y n(1-p) >= 5
        """
        se = math.sqrt(p * (1 - p) / n)
        z = (p_hat - p) / se
        prob_menor = EstadisticaPura.normal_cdf(z, 0, 1)
        prob_mayor = 1 - prob_menor
        condicion_ok = n * p >= 5 and n * (1 - p) >= 5
        return {
            "z": z,
            "se": se,
            "prob_menor": prob_menor,
            "prob_mayor": prob_mayor,
            "condicion_ok": condicion_ok,
            "formula": f"Z = (p̂ - p) / √(p(1-p)/n) = ({p_hat} - {p}) / {se:.4f} = {z:.4f}"
        }
    
    @staticmethod
    def diferencia_medias_sigma_conocida(x1_bar, x2_bar, mu1, mu2, sigma1, sigma2, n1, n2):
        """
        Diferencia de medias con σ conocidas
        """
        se = math.sqrt((sigma1**2 / n1) + (sigma2**2 / n2))
        z = ((x1_bar - x2_bar) - (mu1 - mu2)) / se
        prob_menor = EstadisticaPura.normal_cdf(z, 0, 1)
        prob_mayor = 1 - prob_menor
        return {
            "z": z,
            "se": se,
            "prob_menor": prob_menor,
            "prob_mayor": prob_mayor,
            "formula": f"Z = ((X̄₁-X̄₂) - (μ₁-μ₂)) / SE = {z:.4f}"
        }
    
    @staticmethod
    def diferencia_medias_pooled(x1_bar, x2_bar, s1, s2, n1, n2):
        """
        Diferencia de medias con varianzas desconocidas pero iguales (pooled)
        """
        sp2 = ((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2)
        sp = math.sqrt(sp2)
        se = sp * math.sqrt(1/n1 + 1/n2)
        t = (x1_bar - x2_bar) / se
        df = n1 + n2 - 2
        prob_menor = EstadisticaPura.t_cdf(t, df)
        prob_mayor = 1 - prob_menor
        return {
            "t": t,
            "df": df,
            "sp": sp,
            "se": se,
            "prob_menor": prob_menor,
            "prob_mayor": prob_mayor,
            "formula": f"t = (X̄₁-X̄₂) / (Sp√(1/n₁+1/n₂)) = {t:.4f}, Sp = {sp:.4f}, gl = {df}"
        }
    
    @staticmethod
    def diferencia_proporciones(p1_hat, p2_hat, n1, n2):
        """
        Diferencia de proporciones
        """
        p_combined = (p1_hat * n1 + p2_hat * n2) / (n1 + n2)
        se = math.sqrt(p_combined * (1 - p_combined) * (1/n1 + 1/n2))
        z = (p1_hat - p2_hat) / se if se > 0 else 0
        prob_menor = EstadisticaPura.normal_cdf(z, 0, 1)
        prob_mayor = 1 - prob_menor
        return {
            "z": z,
            "se": se,
            "p_combined": p_combined,
            "prob_menor": prob_menor,
            "prob_mayor": prob_mayor,
            "formula": f"Z = (p̂₁-p̂₂) / SE = ({p1_hat}-{p2_hat}) / {se:.4f} = {z:.4f}"
        }
    
    @staticmethod
    def razon_varianzas(s1_2, s2_2, n1, n2):
        """
        Razón de varianzas (distribución F)
        """
        f = s1_2 / s2_2 if s2_2 > 0 else 0
        df1 = n1 - 1
        df2 = n2 - 1
        prob_menor = EstadisticaPura.f_cdf(f, df1, df2)
        prob_mayor = 1 - prob_menor
        return {
            "f": f,
            "df1": df1,
            "df2": df2,
            "prob_menor": prob_menor,
            "prob_mayor": prob_mayor,
            "formula": f"F = S₁²/S₂² = {s1_2}/{s2_2} = {f:.4f}, gl = ({df1}, {df2})"
        }
    
    # ==========================================
    # INTERVALOS DE CONFIANZA
    # ==========================================
    @staticmethod
    def ic_media_sigma_conocida(x_bar, sigma, n, confianza=0.95):
        """Intervalo de confianza para la media (σ conocida)"""
        alpha = 1 - confianza
        z = EstadisticaPura.normal_ppf(1 - alpha/2)
        margin = z * sigma / math.sqrt(n)
        return {"lower": x_bar - margin, "upper": x_bar + margin, "margin": margin, "z": z}
    
    @staticmethod
    def ic_media_sigma_desconocida(x_bar, s, n, confianza=0.95):
        """Intervalo de confianza para la media (σ desconocida)"""
        alpha = 1 - confianza
        df = n - 1
        t = EstadisticaPura.t_ppf(1 - alpha/2, df)
        margin = t * s / math.sqrt(n)
        return {"lower": x_bar - margin, "upper": x_bar + margin, "margin": margin, "t": t, "df": df}
    
    @staticmethod
    def ic_proporcion(p_hat, n, confianza=0.95):
        """Intervalo de confianza para proporción"""
        alpha = 1 - confianza
        z = EstadisticaPura.normal_ppf(1 - alpha/2)
        se = math.sqrt(p_hat * (1 - p_hat) / n)
        margin = z * se
        return {"lower": max(0, p_hat - margin), "upper": min(1, p_hat + margin), "margin": margin, "z": z}
    
    @staticmethod
    def ic_varianza(s2, n, confianza=0.95):
        """Intervalo de confianza para varianza"""
        alpha = 1 - confianza
        df = n - 1
        chi2_lower = EstadisticaPura.chi2_ppf(1 - alpha/2, df)
        chi2_upper = EstadisticaPura.chi2_ppf(alpha/2, df)
        lower = df * s2 / chi2_lower
        upper = df * s2 / chi2_upper
        return {"lower": lower, "upper": upper, "df": df}

    # Gráficos Flet (desactivados - no compatibles con esta versión)
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
    def generar_chart_uniforme(a, b):
        """Genera gráfico para distribución uniforme continua"""
        if b <= a:
            b = a + 1  # Evitar división por cero
        height = 1 / (b - a)
        
        # Puntos para crear el rectángulo
        margin = (b - a) * 0.2
        data_points = [
            ft.LineChartDataPoint(a - margin, 0),
            ft.LineChartDataPoint(a, 0),
            ft.LineChartDataPoint(a, height),
            ft.LineChartDataPoint(b, height),
            ft.LineChartDataPoint(b, 0),
            ft.LineChartDataPoint(b + margin, 0),
        ]
        
        return ft.LineChart(
            data_series=[
                ft.LineChartData(
                    data_points=data_points,
                    color=ft.colors.AMBER,
                    stroke_width=3,
                    curved=False,
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
    def generar_chart_exponencial(lambd):
        """Genera gráfico para distribución exponencial"""
        data_points = []
        end = 5 / lambd if lambd > 0 else 5
        step = end / 50
        
        curr = 0
        while curr <= end:
            y = EstadisticaPura.exponential_pdf(curr, lambd)
            data_points.append(ft.LineChartDataPoint(curr, y))
            curr += step
        
        return ft.LineChart(
            data_series=[
                ft.LineChartData(
                    data_points=data_points,
                    color=ft.colors.PINK,
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
    def generar_grafico_dispatch(dist_id, params):
        if dist_id == "normal":
             return EstadisticaPura.generar_chart_normal(params[0], params[1])
        elif dist_id == "uniforme":
             return EstadisticaPura.generar_chart_uniforme(params[0], params[1])
        elif dist_id == "exponencial":
             return EstadisticaPura.generar_chart_exponencial(params[0])
        elif dist_id == "binomial":
             return EstadisticaPura.generar_chart_binomial(params[0], params[1])
        elif dist_id == "poisson":
             return EstadisticaPura.generar_chart_poisson(params[0])
        elif dist_id == "t_student":
             return EstadisticaPura.generar_chart_t(params[0])
        elif dist_id == "chi_cuadrado":
             return EstadisticaPura.generar_chart_chi2(params[0])
        else:
             return ft.Text("Gráfico no disponible", color="red")

