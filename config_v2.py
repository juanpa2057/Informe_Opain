NIGHT_HOURS = [0, 1, 2, 3, 4, 5, 19, 20, 21, 22, 23]

# date format would be "YYYY-MM-DD"
# last baseline date must be the same
# date as start of study. Basically all
# dates must be mondays.
#BASELINE = ['2023-08-15', '2023-12-26']
STUDY = ['2023-11-11', '2024-01-01']
#PAST_WEEK = ['2023-12-18', '2023-12-26']

DATE_INTERVALS_TO_DISCARD = {
}

# variables that make up totalizer measurement
ENERGY_VAR_LABELS = ('ea-consumo-total-hora')
#POWER_VAR_LABELS = ('a', 'ilu-potencia-activa')


WHITELISTED_VAR_LABELS = (
    "ea-consumo-total-hora",
    "ea-control-sistema-hvac-dia",
    "ea-control-sistema-hvac-hora",
    "ea-oficinas-tablero-normal-dia",
    "ea-oficinas-tablero-normal-hora",
    "ea-oficinas-tablero-regulado-dia",
    "ea-oficinas-tablero-regulado-hora",
    "energia-total-consumia-dia",
    "potencia-activa-control-hvac",
    "potencia-activa-of-normal",
    "potencia-activa-tablero-regulado",

)


print("Study en config_v2.py:", STUDY)