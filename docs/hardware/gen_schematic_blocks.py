#!/usr/bin/env python3
"""Generate SCH-DCS-003 Rev H — polished IEEE/IEC electrical schematic (no KiCad)."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import cairosvg

HERE = Path(__file__).resolve().parent
STORE_DOCS = Path("/cursor/stores/self/docs/hardware")
STORE_MEDIA = Path("/cursor/stores/self/media")
W, H = 1480, 780

# Shared +24 horizontal rail Y — PS1 +V, F1, J1 + all on this line
Y24 = 200


def build_svg() -> str:
    a: list[str] = []

    def L(s: str = "") -> None:
        a.append(s)

    def j(x: float, y: float, r: float = 2.25) -> None:
        L(f'<circle class="dot" cx="{x}" cy="{y}" r="{r}"/>')

    def wire(d: str, cls: str = "w") -> None:
        L(f'<path class="{cls}" d="{d}"/>')

    def term(x: float, y: float) -> None:
        L(f'<circle cx="{x}" cy="{y}" r="3.8" fill="#fff" stroke="#0f172a" stroke-width="1.25"/>')

    L(
        f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<title>DCS SCH-DCS-003 Rev H</title>
<desc>Electrical schematic from CONNECTIONS.md rev E. F1 in +24 feed.</desc>
<defs>
<style><![CDATA[
  .bg {{ fill:#e8ecf0; }}
  .sheet {{ fill:#ffffff; stroke:#0f172a; stroke-width:1.15; }}
  .frame {{ fill:none; stroke:#0f172a; stroke-width:2; }}
  .w {{ fill:none; stroke:#0f172a; stroke-width:1.2; stroke-linecap:square; stroke-linejoin:miter; }}
  .wb {{ fill:none; stroke:#0f172a; stroke-width:1.45; }}
  .symf {{ fill:#ffffff; stroke:#0f172a; stroke-width:1.3; }}
  .dot {{ fill:#0f172a; }}
  .ref {{ font-family:"IBM Plex Mono",Consolas,"Courier New",monospace; font-size:11px; font-weight:700; fill:#075985; }}
  .val {{ font-family:"IBM Plex Sans",Helvetica,Arial,sans-serif; font-size:10px; fill:#1e293b; }}
  .pin {{ font-family:"IBM Plex Mono",Consolas,"Courier New",monospace; font-size:8px; fill:#334155; }}
  .net {{ font-family:"IBM Plex Mono",Consolas,"Courier New",monospace; font-size:8.5px; font-weight:600; fill:#075985; }}
  .note {{ font-family:"IBM Plex Sans",Helvetica,Arial,sans-serif; font-size:8px; fill:#64748b; }}
  .tb {{ font-family:"IBM Plex Sans",Helvetica,Arial,sans-serif; font-size:9px; fill:#0f172a; }}
  .tbb {{ font-family:"IBM Plex Sans",Helvetica,Arial,sans-serif; font-size:9.5px; font-weight:700; fill:#0f172a; }}
  .hdr {{ font-family:"IBM Plex Sans",Helvetica,Arial,sans-serif; font-size:12px; font-weight:700; fill:#0f172a; }}
]]></style>
<g id="pwr">
  <circle cx="0" cy="0" r="5.5" fill="#fff" stroke="#0f172a" stroke-width="1.2"/>
  <line x1="0" y1="-5.5" x2="0" y2="7" stroke="#0f172a" stroke-width="1.2"/>
</g>
<g id="gnd">
  <line x1="0" y1="0" x2="0" y2="4" stroke="#0f172a" stroke-width="1.2"/>
  <line x1="-7.5" y1="4" x2="7.5" y2="4" stroke="#0f172a" stroke-width="1.2"/>
  <line x1="-4.5" y1="7" x2="4.5" y2="7" stroke="#0f172a" stroke-width="1.2"/>
  <line x1="-1.8" y1="10" x2="1.8" y2="10" stroke="#0f172a" stroke-width="1.2"/>
</g>
</defs>
'''
    )

    L(f'<rect class="bg" width="{W}" height="{H}"/>')
    L(f'<rect class="frame" x="14" y="14" width="{W-28}" height="{H-28}"/>')
    L(f'<rect class="sheet" x="22" y="22" width="{W-44}" height="{H-44}"/>')
    L('<text class="hdr" x="36" y="44">DCS process loop &amp; ADC interface</text>')
    L(
        '<text class="note" x="36" y="57">CONNECTIONS.md rev E · SCH-DCS-003 rev H · unused pins omitted · F1 amp rating TBD</text>'
    )

    # ---------- PS1 ----------
    L('<g id="PS1">')
    L('<text class="ref" x="36" y="118">PS1</text>')
    L('<text class="val" x="36" y="130">Mean Well 24V</text>')
    for lab, yy in [("L", Y24), ("N", Y24 + 28)]:
        term(58, yy)
        wire(f"M 42 {yy} H 54")
        L(f'<text class="pin" x="38" y="{yy+3}" text-anchor="end">{lab}</text>')
    term(96, Y24)  # +V on +24 line
    term(96, Y24 + 55)  # -V
    wire(f"M 100 {Y24} H 112")
    wire(f"M 100 {Y24+55} H 112")
    L(f'<text class="pin" x="78" y="{Y24-7}">+V</text>')
    L(f'<text class="pin" x="78" y="{Y24+52}">-V</text>')
    L(f'<path class="w" d="M 66 {Y24-18} V {Y24+70} H 88 V {Y24-18}" fill="none"/>')
    L(f'<text class="note" x="36" y="{Y24+88}">PSU_MW</text>')
    L("</g>")
    ps1_vp = (112, Y24)
    ps1_vn = (112, Y24 + 55)

    # ---------- F1 on +24 line ----------
    # Clear gap: PS1 out 112 → fuse 140–200 → out to J1
    fx0, fx1 = 140, 205
    L('<g id="F1">')
    L(f'<text class="ref" x="{fx0+8}" y="{Y24-42}">F1</text>')
    L(f'<text class="val" x="{fx0+8}" y="{Y24-30}">PT 4-HESI</text>')
    L(f'<text class="note" x="{fx0+8}" y="{Y24-18}">5x20 amp TBD</text>')
    wire(f"M {fx0} {Y24} H {fx0+12}")
    wire(f"M {fx1-12} {Y24} H {fx1}")
    L(f'<rect class="symf" x="{fx0+12}" y="{Y24-9}" width="{fx1-fx0-24}" height="18"/>')
    L(
        f'<path class="wb" d="M {fx0+18} {Y24} H {fx0+24} Q {fx0+32} {Y24-6} {fx0+40} {Y24} Q {fx0+48} {Y24+6} {fx0+56} {Y24} H {fx1-18}"/>'
    )
    L("</g>")
    f1_in, f1_out = (fx0, Y24), (fx1, Y24)

    # ---------- J1 ----------
    jx = 250
    L('<g id="J1">')
    L(f'<text class="ref" x="{jx}" y="{Y24-42}">J1</text>')
    L(f'<text class="val" x="{jx}" y="{Y24-30}">Rosemount</text>')
    L(f'<text class="note" x="{jx}" y="{Y24-18}">4-20mA TT</text>')
    term(jx + 18, Y24)  # +
    term(jx + 18, Y24 + 36)  # -
    wire(f"M {jx+4} {Y24} H {jx+14}")
    wire(f"M {jx+22} {Y24+36} H {jx+40}")
    L(f'<text class="pin" x="{jx+24}" y="{Y24-6}">+</text>')
    L(f'<text class="pin" x="{jx+24}" y="{Y24+48}">-</text>')
    L("</g>")
    j1_p = (jx + 4, Y24)
    j1_m = (jx + 40, Y24 + 36)

    # ---------- R1 vertical ----------
    rx = 360
    L('<g id="R1">')
    L(f'<path class="wb" d="M {rx} {Y24+36} V {Y24+48} l -9 6 18 10 -18 10 18 10 -18 10 9 6 V {Y24+140}"/>')
    L(f'<text class="ref" x="{rx+14}" y="{Y24+85}">R1</text>')
    L(f'<text class="val" x="{rx+14}" y="{Y24+97}">250R</text>')
    L(f'<text class="note" x="{rx+14}" y="{Y24+109}">0.1%</text>')
    L("</g>")
    r_hi, r_lo = (rx, Y24 + 36), (rx, Y24 + 140)

    # ---------- U2 ----------
    u2x, u2y, u2w, u2h = 470, 140, 68, 130
    L('<g id="U2">')
    L(f'<rect class="symf" x="{u2x}" y="{u2y}" width="{u2w}" height="{u2h}"/>')
    L(f'<path class="w" d="M {u2x+u2w/2-5} {u2y} A 5 5 0 0 0 {u2x+u2w/2+5} {u2y}" fill="#fff"/>')
    L(f'<text class="ref" x="{u2x}" y="{u2y-12}">U2</text>')
    L(f'<text class="val" x="{u2x}" y="{u2y-2}">ADS1115</text>')
    for yy, name in [(u2y + 22, "AIN0"), (u2y + 48, "GND"), (u2y + 72, "ADDR"), (u2y + 105, "VDD")]:
        wire(f"M {u2x-11} {yy} H {u2x}")
        L(f'<text class="pin" x="{u2x+3}" y="{yy+2.5}">{name}</text>')
    for yy, name in [(u2y + 36, "SDA"), (u2y + 64, "SCL")]:
        wire(f"M {u2x+u2w} {yy} H {u2x+u2w+11}")
        L(f'<text class="pin" x="{u2x+u2w-3}" y="{yy+2.5}" text-anchor="end">{name}</text>')
    L(f'<text class="note" x="{u2x}" y="{u2y+u2h+10}">0x48 PGA+/-6.144</text>')
    L("</g>")
    u2_ain0 = (u2x - 11, u2y + 22)
    u2_gnd = (u2x - 11, u2y + 48)
    u2_addr = (u2x - 11, u2y + 72)
    u2_vdd = (u2x - 11, u2y + 105)
    u2_sda = (u2x + u2w + 11, u2y + 36)
    u2_scl = (u2x + u2w + 11, u2y + 64)

    # ---------- U3 ----------
    u3x, u3y, u3w, u3h = 680, 140, 78, 130
    L('<g id="U3">')
    L(f'<rect class="symf" x="{u3x}" y="{u3y}" width="{u3w}" height="{u3h}"/>')
    L(f'<line class="w" x1="{u3x+u3w/2}" y1="{u3y+8}" x2="{u3x+u3w/2}" y2="{u3y+u3h-8}" stroke-dasharray="2 2"/>')
    L(f'<text class="ref" x="{u3x}" y="{u3y-12}">U3</text>')
    L(f'<text class="val" x="{u3x}" y="{u3y-2}">4ch LLC</text>')
    L(f'<text class="pin" x="{u3x+3}" y="{u3y+11}">HV</text>')
    L(f'<text class="pin" x="{u3x+u3w-3}" y="{u3y+11}" text-anchor="end">LV</text>')
    for yy, name in [(u3y + 26, "B1"), (u3y + 50, "B2"), (u3y + 80, "HV"), (u3y + 108, "GND")]:
        wire(f"M {u3x-11} {yy} H {u3x}")
        L(f'<text class="pin" x="{u3x+3}" y="{yy+2.5}">{name}</text>')
    for yy, name in [(u3y + 26, "A1"), (u3y + 50, "A2"), (u3y + 80, "LV"), (u3y + 108, "GND")]:
        wire(f"M {u3x+u3w} {yy} H {u3x+u3w+11}")
        L(f'<text class="pin" x="{u3x+u3w-3}" y="{yy+2.5}" text-anchor="end">{name}</text>')
    L(f'<text class="note" x="{u3x}" y="{u3y+u3h+10}">unused NC</text>')
    L("</g>")
    u3_b1 = (u3x - 11, u3y + 26)
    u3_b2 = (u3x - 11, u3y + 50)
    u3_hv = (u3x - 11, u3y + 80)
    u3_gndl = (u3x - 11, u3y + 108)
    u3_a1 = (u3x + u3w + 11, u3y + 26)
    u3_a2 = (u3x + u3w + 11, u3y + 50)
    u3_lv = (u3x + u3w + 11, u3y + 80)
    u3_gndr = (u3x + u3w + 11, u3y + 108)

    # ---------- U1 ----------
    u1x, u1y, u1w, u1h = 920, 125, 62, 160
    L('<g id="U1">')
    L(f'<rect class="symf" x="{u1x}" y="{u1y}" width="{u1w}" height="{u1h}"/>')
    L(f'<text class="ref" x="{u1x}" y="{u1y-12}">U1</text>')
    L(f'<text class="val" x="{u1x}" y="{u1y-2}">Pi 4</text>')
    pins = [
        (u1y + 22, "GPIO2", "SDA p3"),
        (u1y + 48, "GPIO3", "SCL p5"),
        (u1y + 80, "3V3", "pin 1"),
        (u1y + 110, "5V", "pin 2/4"),
        (u1y + 140, "GND", "pin 6"),
    ]
    for yy, a1, a2 in pins:
        wire(f"M {u1x-11} {yy} H {u1x}")
        L(f'<text class="pin" x="{u1x+3}" y="{yy-1}">{a1}</text>')
        L(f'<text class="pin" x="{u1x+3}" y="{yy+9}">{a2}</text>')
    L(f'<text class="note" x="{u1x}" y="{u1y+u1h+10}">5V pin TBD</text>')
    L("</g>")
    u1_sda = (u1x - 11, u1y + 22)
    u1_scl = (u1x - 11, u1y + 48)
    u1_3v3 = (u1x - 11, u1y + 80)
    u1_5v = (u1x - 11, u1y + 110)
    u1_gnd = (u1x - 11, u1y + 140)

    # ========== WIRING ==========
    gnd_y = 450

    # +24 straight: PS1 → F1 → J1
    wire(f"M {ps1_vp[0]} {Y24} H {f1_in[0]}")
    j(*ps1_vp)
    j(*f1_in)
    # label ABOVE the gap between PS1 and F1, clear of F1 refs
    L(f'<text class="net" x="118" y="{Y24+14}">+24V_PSU</text>')

    wire(f"M {f1_out[0]} {Y24} H {j1_p[0]}")
    j(*f1_out)
    j(*j1_p)
    L(f'<text class="net" x="212" y="{Y24+14}">+24V_LOOP</text>')
    # power flag above J1+, not overlapping F1
    L(f'<use href="#pwr" x="232" y="{Y24-28}"/>')
    wire(f"M 232 {Y24-22} V {Y24}")
    j(232, Y24)
    L(f'<text class="net" x="240" y="{Y24-30}">+24V</text>')

    # J1- → R1 high (same y)
    wire(f"M {j1_m[0]} {j1_m[1]} H {rx}")
    j(*j1_m)
    j(*r_hi)
    L(f'<text class="net" x="292" y="{r_hi[1]-8}">NET_SHUNT_HIGH</text>')

    # Branch to AIN0 — orthogonal, no kink
    wire(f"M {rx} {r_hi[1]} H 420 V {u2_ain0[1]} H {u2_ain0[0]}")
    j(420, r_hi[1])
    j(*u2_ain0)

    # R1 low → GND
    wire(f"M {r_lo[0]} {r_lo[1]} V {gnd_y}")
    j(rx, gnd_y)

    # GND rail
    wire(f"M 50 {gnd_y} H 1080", "wb")
    L(f'<text class="net" x="54" y="{gnd_y-7}">GND</text>')
    L(f'<use href="#gnd" x="{rx}" y="{gnd_y}"/>')
    L(f'<text class="note" x="{rx+12}" y="{gnd_y+14}">star @ shunt-low / brass bar</text>')

    # 0V_LOOP
    wire(f"M {ps1_vn[0]} {ps1_vn[1]} H 128 V {gnd_y}")
    j(128, gnd_y)
    L(f'<text class="net" x="132" y="{ps1_vn[1]+14}">0V_LOOP</text>')

    # U2 GND — stub left then down; ADDR ties to same vertical (label clear of body)
    wire(f"M {u2_gnd[0]} {u2_gnd[1]} H 448 V {gnd_y}")
    j(448, gnd_y)
    wire(f"M {u2_addr[0]} {u2_addr[1]} H 440 V {u2_gnd[1]}")
    j(440, u2_gnd[1])
    L(f'<text class="net" x="412" y="{u2_gnd[1]-6}">GND</text>')

    # U3 / U1 GND
    wire(f"M {u3_gndl[0]} {u3_gndl[1]} H 660 V {gnd_y}")
    j(660, gnd_y)
    wire(f"M {u3_gndr[0]} {u3_gndr[1]} H 790 V {gnd_y}")
    j(790, gnd_y)
    wire(f"M {u1_gnd[0]} {u1_gnd[1]} H 900 V {gnd_y}")
    j(900, gnd_y)

    # I2C 5V
    wire(f"M {u2_sda[0]} {u2_sda[1]} H {u3_b1[0]}")
    j(*u2_sda)
    j(*u3_b1)
    L(f'<text class="net" x="560" y="{u2_sda[1]-7}">I2C_SDA_5V</text>')
    wire(f"M {u2_scl[0]} {u2_scl[1]} H {u3_b2[0]}")
    j(*u2_scl)
    j(*u3_b2)
    L(f'<text class="net" x="560" y="{u2_scl[1]-7}">I2C_SCL_5V</text>')

    # I2C 3V3
    wire(f"M {u3_a1[0]} {u3_a1[1]} H {u1_sda[0]}")
    j(*u3_a1)
    j(*u1_sda)
    L(f'<text class="net" x="800" y="{u3_a1[1]-7}">I2C_SDA_3V3</text>')
    wire(f"M {u3_a2[0]} {u3_a2[1]} H {u1_scl[0]}")
    j(*u3_a2)
    j(*u1_scl)
    L(f'<text class="net" x="800" y="{u3_a2[1]-7}">I2C_SCL_3V3</text>')

    # +3V3
    wire(f"M {u1_3v3[0]} {u1_3v3[1]} H {u3_lv[0]}")
    j(*u1_3v3)
    j(*u3_lv)
    L(f'<text class="net" x="820" y="{u1_3v3[1]-7}">+3V3_PI</text>')
    L(f'<use href="#pwr" x="860" y="{u1_3v3[1]-24}"/>')
    wire(f"M 860 {u1_3v3[1]-18} V {u1_3v3[1]}")
    j(860, u1_3v3[1])
    L(f'<text class="net" x="868" y="{u1_3v3[1]-26}">+3V3</text>')

    # +5V_ADS top rail
    rail_y = 100
    wire(f"M {u1_5v[0]} {u1_5v[1]} H 900 V {rail_y} H 440")
    j(900, rail_y)
    j(*u1_5v)
    L(f'<text class="net" x="620" y="{rail_y-6}">+5V_ADS</text>')
    L(f'<use href="#pwr" x="600" y="{rail_y-18}"/>')
    wire(f"M 600 {rail_y-12} V {rail_y}")
    j(600, rail_y)
    L(f'<text class="net" x="608" y="{rail_y-20}">+5V</text>')
    wire(f"M 660 {rail_y} V {u3_hv[1]} H {u3_hv[0]}")
    j(660, rail_y)
    j(*u3_hv)
    wire(f"M 440 {rail_y} V {u2_vdd[1]} H {u2_vdd[0]}")
    j(440, rail_y)
    j(*u2_vdd)

    # Legend + title
    L(
        '''<g id="legend">
  <text class="tbb" x="36" y="510">Designators</text>
  <text class="tb" x="36" y="524">PS1=PSU_MW · F1=FU_HESI · J1=TT_RM · R1=RS250 · U2=U_ADS · U3=U_LLC · U1=U_PI</text>
  <text class="note" x="36" y="538">+24V_PSU → F1 → +24V_LOOP → Rosemount. Fuse amp TBD. No Fluke/relay/software on sheet.</text>
</g>'''
    )
    tbx, tby = 1080, 490
    L(
        f'''<g id="tb">
  <rect class="symf" x="{tbx}" y="{tby}" width="360" height="140"/>
  <line class="w" x1="{tbx}" y1="{tby+26}" x2="{tbx+360}" y2="{tby+26}"/>
  <line class="w" x1="{tbx}" y1="{tby+52}" x2="{tbx+360}" y2="{tby+52}"/>
  <line class="w" x1="{tbx}" y1="{tby+82}" x2="{tbx+360}" y2="{tby+82}"/>
  <line class="w" x1="{tbx}" y1="{tby+110}" x2="{tbx+360}" y2="{tby+110}"/>
  <line class="w" x1="{tbx+170}" y1="{tby+52}" x2="{tbx+170}" y2="{tby+140}"/>
  <line class="w" x1="{tbx+255}" y1="{tby+52}" x2="{tbx+255}" y2="{tby+140}"/>
  <text class="tbb" x="{tbx+8}" y="{tby+17}">DCS — Distributed Control System (bench)</text>
  <text class="tb" x="{tbx+8}" y="{tby+42}">PS1 · F1 · loop · 250R · ADS1115 · LLC · Pi 4</text>
  <text class="tbb" x="{tbx+8}" y="{tby+72}">SCH-DCS-003</text>
  <text class="tbb" x="{tbx+178}" y="{tby+72}">REV H</text>
  <text class="tb" x="{tbx+263}" y="{tby+72}">1 / 1</text>
  <text class="tb" x="{tbx+8}" y="{tby+100}">2026-09-28</text>
  <text class="tb" x="{tbx+178}" y="{tby+100}">NTS</text>
  <text class="tb" x="{tbx+263}" y="{tby+100}">A3L</text>
  <text class="note" x="{tbx+8}" y="{tby+128}">Truth: CONNECTIONS.md · hand-drawn SVG (no KiCad)</text>
</g>'''
    )
    L("</svg>")
    return "\n".join(a)


def main() -> None:
    svg = build_svg()
    ET.fromstring(svg)
    STORE_DOCS.mkdir(parents=True, exist_ok=True)
    STORE_MEDIA.mkdir(parents=True, exist_ok=True)
    svg_path = HERE / "schematic-blocks.svg"
    pdf_path = HERE / "schematic-blocks.pdf"
    png_path = STORE_MEDIA / "schematic-blocks-preview.png"
    svg_path.write_text(svg, encoding="utf-8")
    data = svg.encode("utf-8")
    cairosvg.svg2pdf(bytestring=data, write_to=str(pdf_path))
    cairosvg.svg2png(bytestring=data, write_to=str(png_path), output_width=2200)
    (STORE_DOCS / "schematic-blocks.svg").write_text(svg, encoding="utf-8")
    (STORE_DOCS / "schematic-blocks.pdf").write_bytes(pdf_path.read_bytes())
    print("OK", svg_path.stat().st_size, pdf_path.stat().st_size, png_path.stat().st_size)


if __name__ == "__main__":
    main()
