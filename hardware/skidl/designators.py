"""
Designator mapping: schematic refs ↔ CONNECTIONS.md logical names.

| Schematic | CONNECTIONS.md | Role |
|-----------|----------------|------|
| U1        | U_PI           | Raspberry Pi 4 Model B (GPIO subset as Conn stand-in) |
| U2        | U_ADS          | ADS1115 |
| U3        | U_LLC          | 4 Bi-Directional Level Shifters (Conn stand-in) |
| R1        | RS250          | 250 Ω shunt |
| PS1       | PSU_MW         | Mean Well DIN 24 V (Conn stand-in) |
| J1        | TT_RM          | Rosemount 2-wire TT terminals |
| J2        | (field/DIN)    | +24V_LOOP landing (optional DIN TB face) |
| J3        | (AC)           | AC L/N into PS1 (labels TODO in CONNECTIONS) |
| J4        | (PE/bar)       | PE / brass ground bar land |
| R2, D1, D2| (new OPTIONAL) | AIN0 series + clamp (not in CONNECTIONS permanent BOM) |
"""

MAPPING = {
    "U1": "U_PI",
    "U2": "U_ADS",
    "U3": "U_LLC",
    "R1": "RS250",
    "PS1": "PSU_MW",
    "J1": "TT_RM",
}
