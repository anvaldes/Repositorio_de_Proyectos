import QuantLib as ql
import numpy as np
import math

def create_calendar_chile(start_year,n_years):
    Chile = ql.WeekendsOnly()
    days = [1,14,15,1,21,26,2,16,15,18,19,9,27,1,19,8,17,25,31]
    months = [1,4,4,5,5,6,8,9,9,10,10,11,12,12,12,12]
    name = ['Año Nuevo','Viernes Santo','Sabado Santo','Dia del Trabajo','Dia de las Glorias Navales','San Pedro y San Pablo','Elecciones Primarias','Dia de la Virgen del Carmen','Asuncion de la Virgen','Independencia Nacional','Glorias del Ejercito','Encuentro de dos mundos','Día de las Iglesias Evangélicas y Protestantes','Día de todos los Santos','Elecciones Presidenciales y Parlamentarias','Inmaculada Concepción','Segunda vuelta Presidenciales','Navidad','Feriado Bancario']
    for i in range(n_years+1):
        for x,y in zip(days,months):
            date = ql.Date(x,y,start_year+i)
            Chile.addHoliday(date)
    return Chile

class SwapValuationAndXVA:

    def __init__(self, effective_date, largo_paso=ql.Period(30, ql.Days), dfs_ois=[], dfs_libor3m=[], dfs_libor6m=[], dfs_collusd_clp=[],
                 dfs_icp=[], dfs_collusd_uf=[], dfs_uf=[], uf_to_clp=[]):

        self.effective_date = effective_date
        self.largo_paso = largo_paso
        self.curvas_ois = self.dfs_to_objetos_curva(dfs_ois)
        self.curvas_libor3m = self.dfs_to_objetos_curva(dfs_libor3m)
        self.curvas_libor6m = self.dfs_to_objetos_curva(dfs_libor6m)
        self.curvas_collusd_clp = self.dfs_to_objetos_curva(dfs_collusd_clp)
        self.curvas_icp = self.dfs_to_objetos_curva(dfs_icp)
        self.curvas_collusd_uf = self.dfs_to_objetos_curva(dfs_collusd_uf)
        self.curvas_uf = self.dfs_to_objetos_curva(dfs_uf)
        self.uf_to_clp = uf_to_clp

        self.calendar_chile = create_calendar_chile(2019, 100)
        self.calendar_usa = ql.TARGET()

        ##calendar, convention, terminationDateConvention, datagen, endOfMonth
        self.convenciones = {"US Dollar Overnight Swap": [self.calendar_usa, ql.ModifiedFollowing, ql.ModifiedFollowing,
                                                          ql.DateGeneration.Backward, True],
                             "CLP Fixed x Camara Swap": [self.calendar_chile, ql.ModifiedFollowing,
                                                         ql.ModifiedFollowing, ql.DateGeneration.Backward, True],
                             "Cross UF/ICP": [self.calendar_chile, ql.ModifiedFollowing, ql.ModifiedFollowing,
                                              ql.DateGeneration.Backward, True],
                             "CLP 6m vs USD 6m Basis Swap": [self.calendar_chile, ql.ModifiedFollowing,
                                                             ql.ModifiedFollowing, ql.DateGeneration.Backward, True]}

    def dfs_to_objetos_curva(self, dfs):
        objetos_curva = {}
        for i in range(len(dfs)):
            n_periodos = len(dfs[i])
            for t in range(n_periodos - 1):
                dates_utilizar = [self.effective_date + (k + t) * self.largo_paso for k in range(n_periodos - t)]
                dfs_utilizar = dfs[i][t]
                objetos_curva[(i, t)] = ql.DiscountCurve(dates_utilizar, dfs_utilizar, ql.Actual360())
        return objetos_curva

    def payment_dates(self, effectiveDate, terminationDate, frequency, calendar, convention, terminationDateConvention,
                      datagen, endOfMonth):
        schedule = ql.Schedule(effectiveDate, terminationDate, frequency, calendar, convention,
                               terminationDateConvention, datagen, endOfMonth)
        return [fecha for fecha in schedule]

    def fechas_dsps_periodo(self, t, termination_date, fechas):
        fecha_actual = self.effective_date + t * self.largo_paso
        return [fecha for fecha in fechas if fecha_actual <= fecha <= termination_date]

    def numero_instantes_valorizar(self, termination_date):
        # considera el numero de todos los instantes donde se valoriza, desde el día 0, hasta el primer día donde el swap ya haya terminado
        # cada instante tiene largo_paso tiempo de diferencia
        return math.ceil((termination_date - self.effective_date) / (
                    (self.effective_date + self.largo_paso) - self.effective_date)) + 1

    # Se asume que las fechas comienzan desde el día que se hace efectivo el contrato y siempre el primer factor de descuento de cada lista dfs es 1
    def OISPricer(self, notional, fixed_rate, dates, dfs, recibo_fija=True, day_count=ql.Actual360()):
        leg1 = np.dot(np.array(dfs[1:]), np.array(
            [fixed_rate * day_count.yearFraction(dates[i], dates[i + 1]) for i in range(len(dates) - 1)]))
        leg2 = np.dot(np.array(dfs[1:]), np.array([(dfs[i] / dfs[i + 1]) - 1 for i in range(len(dates) - 1)]))
        if recibo_fija:
            return notional * (leg1 - leg2)
        if not recibo_fija:
            return (-1) * notional * (leg1 - leg2)

    def value_US_Dollar_Overnight_Swap(self, notional, fixed_rate, termination_date,
                                       frequency, recibo_fija=True, day_count=ql.Actual360()):
        a, b, c, d, e = self.convenciones["US Dollar Overnight Swap"]
        fechas_de_pagos = self.payment_dates(self.effective_date, termination_date, frequency, a, b, c, d, e)
        numero_simulaciones = len(self.curvas_icp)
        numero_instantes_valorizar = self.numero_instantes_valorizar(termination_date)
        valorizaciones_swap = []

        for i in range(numero_simulaciones):
            valorizaciones_simulacion = []
            for t in range(numero_instantes_valorizar - 1):
                dates = self.fechas_dsps_periodo(t, termination_date, fechas_de_pagos)
                curve = self.curvas_ois[(i, t)]
                dfs = [curve.discount(j) for j in dates]
                valorizaciones_simulacion.append(
                    self.OISPricer(notional, fixed_rate, dates, dfs, recibo_fija, day_count))
            valorizaciones_simulacion.append(0)
            valorizaciones_swap.append(valorizaciones_simulacion)
        return valorizaciones_swap

    # Se asume que las fechas comienzan desde el día que se hace efectivo el contrato y siempre el primer factor de descuento de cada lista dfs es 1
    def ICPPricer(self, notional, fixed_rate, dates, dfs, recibo_fija=True, day_count=ql.Actual360()):
        leg1 = np.dot(np.array(dfs[1:]), np.array(
            [fixed_rate * day_count.yearFraction(dates[i], dates[i + 1]) for i in range(len(dates) - 1)]))
        leg2 = np.dot(np.array(dfs[1:]), np.array([(dfs[i] / dfs[i + 1]) - 1 for i in range(len(dates) - 1)]))
        if recibo_fija:
            return notional * (leg1 - leg2)
        elif not recibo_fija:
            return (-1) * notional * (leg1 - leg2)

    def value_CLP_Fixed_x_Camara_Swap(self, notional, fixed_rate, termination_date,
                                      frequency, recibo_fija=True, day_count=ql.Actual360()):

        a, b, c, d, e = self.convenciones["CLP Fixed x Camara Swap"]
        fechas_de_pagos = self.payment_dates(self.effective_date, termination_date, frequency, a, b, c, d, e)
        numero_simulaciones = len(self.curvas_icp)
        numero_instantes_valorizar = self.numero_instantes_valorizar(termination_date)
        valorizaciones_swap = []

        for i in range(numero_simulaciones):
            valorizaciones_simulacion = []
            for t in range(numero_instantes_valorizar - 1):
                dates = self.fechas_dsps_periodo(t, termination_date, fechas_de_pagos)
                curve = self.curvas_icp[(i, t)]
                dfs = [curve.discount(j) for j in dates]
                valorizaciones_simulacion.append(
                    self.ICPPricer(notional, fixed_rate, dates, dfs, recibo_fija, day_count))
            valorizaciones_simulacion.append(0)
            valorizaciones_swap.append(valorizaciones_simulacion)
        return valorizaciones_swap

    def CrossUfClpPricer(self, notional_clp, fixed_rate_clp, fixed_rate_uf, dates, dfs_clp, dfs_uf, uf_to_clp,
                         recibo_clp=True, day_count=ql.Actual360()):
        notional_uf = notional_clp / uf_to_clp
        leg1 = np.dot(np.array(dfs_clp[1:]), np.array(
            [fixed_rate_clp * day_count.yearFraction(dates[i], dates[i + 1]) for i in range(len(dates) - 1)]))
        leg2 = np.dot(np.array(dfs_uf[1:]),
                      np.array([fixed_rate_uf * (dates[i + 1] - dates[i]) / 360 for i in range(len(dates) - 1)]))
        pago_final = (notional_uf * dfs_uf[-1] * uf_to_clp - notional_clp * dfs_clp[-1])
        if recibo_clp:
            return notional_clp * leg1 - (notional_uf * leg2 + pago_final)
        elif not recibo_clp:
            return (-1) * (notional_clp * leg1 - (notional_uf * leg2 + pago_final))

    def value_Cross_UF_ICP(self, notional_clp, fixed_rate_clp, fixed_rate_uf, termination_date, frequency,
                           recibo_clp=True, day_count=ql.Actual360()):

        a, b, c, d, e = self.convenciones["Cross UF/ICP"]
        fechas_de_pagos = self.payment_dates(self.effective_date, termination_date, frequency, a, b, c, d, e)
        numero_simulaciones = len(self.curvas_collusd_uf)
        numero_instantes_valorizar = self.numero_instantes_valorizar(termination_date)
        valorizaciones_swap = []

        for i in range(numero_simulaciones):
            valorizaciones_simulacion = []
            for t in range(numero_instantes_valorizar - 1):
                dates = self.fechas_dsps_periodo(t, termination_date, fechas_de_pagos)
                curve_clp = self.curvas_collusd_clp[(i, t)]
                curve_uf = self.curvas_collusd_uf[(i, t)]
                dfs_clp = [curve_clp.discount(j) for j in dates]
                dfs_uf = [curve_uf.discount(j) for j in dates]
                valorizaciones_simulacion.append(self.CrossUfClpPricer(notional_clp, fixed_rate_clp, fixed_rate_uf,
                                                                       dates, dfs_clp, dfs_uf, self.uf_to_clp[i][t], recibo_clp,
                                                                       day_count))
            valorizaciones_simulacion.append(0)
            valorizaciones_swap.append(valorizaciones_simulacion)
        return valorizaciones_swap