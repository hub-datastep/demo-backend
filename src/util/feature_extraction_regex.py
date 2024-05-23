# Определение регулярных выражений для разных категорий
regex_patterns = {
    "overall_size_mm_cm_m": r"(\d+)\s?(мм|см|м)",  # Общий размер в мм/см/м
    "nominal_bore_diameter": r"Ду-?(\d+)|DN=?(\d+)",  # Диаметр условного отверстия
    "diameter_inches": r"(\d+\/\d+\"|\d+\")",  # Диаметр (в дюймах)
    "rectangular_dimensions": r"(\d+)[xх](\d+)(?:[xх](\d+))?",  # Прямоугольные размеры
    "pressure_PN": r"[PР][Nn](\d+)",  # Давление (PN)
    "working_pressure_Ru": r"Ру\s?(\d+)",  # Рабочее давление (Ру)
    "maximum_temperature": r"[ТT][mMмМ][aAаА][xXкК][Сс]?\s*=?\s*(\d+)\s*[°\s]?[гГ]?[рР]?[CcСсoO]?",  # Максимальная температура
    "flow_volume": r"(\d+,\d+|\d+) - (\d+,\d+|\д+) л/час",  # Объем потока
    "power": r"(\д+)\s?(Вт|кВт)"  # Мощность
}