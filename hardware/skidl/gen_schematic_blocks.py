#!/usr/bin/env python3
"""SCH-DCS-003 Rev F — portfolio electrical schematic (IEEE/IEC symbols)."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import cairosvg

REPO = Path("/workspace/docs/hardware")
STORE_DOCS = Path("/cursor/stores/self/docs/hardware")
STORE_MEDIA = Path("/cursor/stores/self/media")
W, H = 1500, 820


def build_svg() -> str:
    a: list[str] = []

    def L(s: str = "") -> None:
        a.append(s)

    def j(x: float, y: float, r: float = 2.3) -> None:
        L(f'<circle class="dot" cx="{x}" cy="{y}" r="{r}"/>')

    def wire(d: str, cls: str = "w") -> None:
        L(f'<path class="{cls}" d="{d}"/>')

    def term(x: float, y: float) -> None:
        """Hollow terminal circle (connector pin)."""
        L(f'<circle cx="{x}" cy="{y}" r="4" fill="#fff" stroke="#0f172a" stroke-width="1.3"/>')

    L(
        f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<title>DCS SCH-DCS-003 Rev F</title>
<desc>Electrical schematic from CONNECTIONS.md. Real component symbols.</desc>
<defs>
<style><![CDATA[
  .bg {{ fill:#eceff3; }}
  .sheet {{ fill:#ffffff; stroke:#0f172a; stroke-width:1.2; }}
  .frame {{ fill:none; stroke:#0f172a; stroke-width:2; }}
  .w {{ fill:none; stroke:#0f172a; stroke-width:1.25; stroke-linecap:square; stroke-linejoin:miter; }}
  .wb {{ fill:none; stroke:#0f172a; stroke-width:1.5; }}
  .symf {{ fill:#ffffff; stroke:#0f172a; stroke-width:1.35; }}
  .dot {{ fill:#0f172a; }}
  .ref {{ font-family:"IBM Plex Mono",Consolas,"Courier New",monospace; font-size:11.5px; font-weight:700; fill:#075985; }}
  .val {{ font-family:"IBM Plex Sans",Helvetica,Arial,sans-serif; font-size:10.5px; fill:#1e293b; }}
  .pin {{ font-family:"IBM Plex Mono",Consolas,"Courier New",monospace; font-size:8.5px; fill:#334155; }}
  .net {{ font-family:"IBM Plex Mono",Consolas,"Courier New",monospace; font-size:9px; font-weight:600; fill:#075985; }}
  .note {{ font-family:"IBM Plex Sans",Helvetica,Arial,sans-serif; font-size:8.5px; fill:#64748b; }}
  .tb {{ font-family:"IBM Plex Sans",Helvetica,Arial,sans-serif; font-size:9.5px; fill:#0f172a; }}
  .tbb {{ font-family:"IBM Plex Sans",Helvetica,Arial,sans-serif; font-size:10px; font-weight:700; fill:#0f172a; }}
  .hdr {{ font-family:"IBM Plex Sans",Helvetica,Arial,sans-serif; font-size:12.5px; font-weight:700; fill:#0f172a; }}
]]></style>
<g id="pwr">
  <circle cx="0" cy="0" r="6" fill="#fff" stroke="#0f172a" stroke-width="1.25"/>
  <line x1="0" y1="-6" x2="0" y2="8" stroke="#0f172a" stroke-width="1.25"/>
</g>
<g id="gnd">
  <line x1="0" y1="0" x2="0" y2="4" stroke="#0f172a" stroke-width="1.25"/>
  <line x1="-8" y1="4" x2="8" y2="4" stroke="#0f172a" stroke-width="1.25"/>
  <line x1="-5" y1="7.5" x2="5" y2="7.5" stroke="#0f172a" stroke-width="1.25"/>
  <line x1="-2" y1="11" x2="2" y2="11" stroke="#0f172a" stroke-width="1.25"/>
</g>
</defs>
'''
    )

    L(f'<rect class="bg" width="{W}" height="{H}"/>')
    L(f'<rect class="frame" x="16" y="16" width="{W-32}" height="{H-32}"/>')
    L(f'<rect class="sheet" x="24" y="24" width="{W-48}" height="{H-48}"/>')
    L('<text class="hdr" x="38" y="46">DCS process loop &amp; ADC interface</text>')
    L(
        '<text class="note" x="38" y="59">CONNECTIONS.md rev D · SCH-DCS-003 rev F · IEEE/IEC symbols · unused pins omitted</text>'
    )

    # ===== PS1 — screw-terminal strip (4 circles), not a fat card =====
    # Layout: vertical stack of terminal circles with short stubs
    L('<g id="PS1">')
    L('<text class="ref" x="48" y="150">PS1</text>')
    L('<text class="val" x="48" y="162">Mean Well 24V DIN</text>')
    # four terminals: L, N, +V, -V arranged as 2+2
    # AC left column
    for i, (lab, yy) in enumerate([("L", 190), ("N", 220)]):
        term(70, yy)
        wire(f"M 50 {yy} H 66")
        L(f'<text class="pin" x="46" y="{yy+3}" text-anchor="end">{lab}</text>')
    # DC right column  
    for lab, yy in [("+V", 190), ("-V", 250)]:
        term(110, yy)
        wire(f"M 114 {yy} H 130")
        L(f'<text class="pin" x="92" y="{yy-6}">{lab}</text>')
    # body outline light bracket linking terminals (minimal, not a filled box)
    L('<path class="w" d="M 78 175 V 265 H 102 V 175" fill="none"/>')
    L('<text class="note" x="48" y="280">PSU_MW · AC silk TBD</text>')
    L("</g>")
    ps1_vp = (130, 190)
    ps1_vn = (130, 250)

    # ===== J1 — 2-pin terminal =====
    L('<g id="J1">')
    L('<text class="ref" x="210" y="150">J1</text>')
    L('<text class="val" x="210" y="162">Rosemount TT</text>')
    term(230, 190)
    term(230, 230)
    wire("M 214 190 H 226")
    wire("M 234 230 H 250")
    L('<text class="pin" x="238" y="186">+</text>')
    L('<text class="pin" x="238" y="244">-</text>')
    L('<text class="note" x="210" y="258">2-wire 4-20mA</text>')
    L("</g>")
    j1_p = (214, 190)
    j1_m = (250, 230)

    # ===== R1 vertical zig-zag =====
    rx = 330
    L('<g id="R1">')
    L(
        f'<path class="wb" d="M {rx} 230 V 242 l -10 7 20 11 -20 11 20 11 -20 11 10 7 V 340"/>'
    )
    L(f'<text class="ref" x="{rx+16}" y="278">R1</text>')
    L(f'<text class="val" x="{rx+16}" y="291">250R</text>')
    L(f'<text class="note" x="{rx+16}" y="303">0.1% RS250</text>')
    L("</g>")
    r_hi, r_lo = (rx, 230), (rx, 340)

    # ===== U2 ADS1115 — slim IC, pins outside =====
    u2x, u2y, u2w, u2h = 450, 145, 70, 140
    L('<g id="U2">')
    L(f'<rect class="symf" x="{u2x}" y="{u2y}" width="{u2w}" height="{u2h}"/>')
    # notch
    L(
        f'<path class="w" d="M {u2x+u2w/2-6} {u2y} A 6 6 0 0 0 {u2x+u2w/2+6} {u2y}" fill="#fff"/>'
    )
    for yy, name in [
        (u2y + 24, "AIN0"),
        (u2y + 50, "GND"),
        (u2y + 76, "ADDR"),
        (u2y + 110, "VDD"),
    ]:
        wire(f"M {u2x-12} {yy} H {u2x}")
        L(f'<text class="pin" x="{u2x+3}" y="{yy+3}">{name}</text>')
    for yy, name in [(u2y + 40, "SDA"), (u2y + 70, "SCL")]:
        wire(f"M {u2x+u2w} {yy} H {u2x+u2w+12}")
        L(f'<text class="pin" x="{u2x+u2w-3}" y="{yy+3}" text-anchor="end">{name}</text>')
    L(f'<text class="ref" x="{u2x}" y="{u2y-14}">U2</text>')
    L(f'<text class="val" x="{u2x}" y="{u2y-3}">ADS1115</text>')
    L(f'<text class="note" x="{u2x}" y="{u2y+u2h+11}">0x48 · PGA +/-6.144</text>')
    L("</g>")
    u2_ain0 = (u2x - 12, u2y + 24)
    u2_gnd = (u2x - 12, u2y + 50)
    u2_addr = (u2x - 12, u2y + 76)
    u2_vdd = (u2x - 12, u2y + 110)
    u2_sda = (u2x + u2w + 12, u2y + 40)
    u2_scl = (u2x + u2w + 12, u2y + 70)

    # ===== U3 LLC =====
    u3x, u3y, u3w, u3h = 660, 145, 80, 140
    L('<g id="U3">')
    L(f'<rect class="symf" x="{u3x}" y="{u3y}" width="{u3w}" height="{u3h}"/>')
    L(
        f'<line class="w" x1="{u3x+u3w/2}" y1="{u3y+10}" x2="{u3x+u3w/2}" y2="{u3y+u3h-10}" stroke-dasharray="2 2"/>'
    )
    L(f'<text class="pin" x="{u3x+3}" y="{u3y+12}">HV</text>')
    L(f'<text class="pin" x="{u3x+u3w-3}" y="{u3y+12}" text-anchor="end">LV</text>')
    for yy, name in [
        (u3y + 28, "B1"),
        (u3y + 52, "B2"),
        (u3y + 85, "HV"),
        (u3y + 115, "GND"),
    ]:
        wire(f"M {u3x-12} {yy} H {u3x}")
        L(f'<text class="pin" x="{u3x+3}" y="{yy+3}">{name}</text>')
    for yy, name in [
        (u3y + 28, "A1"),
        (u3y + 52, "A2"),
        (u3y + 85, "LV"),
        (u3y + 115, "GND"),
    ]:
        wire(f"M {u3x+u3w} {yy} H {u3x+u3w+12}")
        L(f'<text class="pin" x="{u3x+u3w-3}" y="{yy+3}" text-anchor="end">{name}</text>')
    L(f'<text class="ref" x="{u3x}" y="{u3y-14}">U3</text>')
    L(f'<text class="val" x="{u3x}" y="{u3y-3}">4ch LLC</text>')
    L(f'<text class="note" x="{u3x}" y="{u3y+u3h+11}">U_LLC · unused NC</text>')
    L("</g>")
    u3_b1 = (u3x - 12, u3y + 28)
    u3_b2 = (u3x - 12, u3y + 52)
    u3_hv = (u3x - 12, u3y + 85)
    u3_gndl = (u3x - 12, u3y + 115)
    u3_a1 = (u3x + u3w + 12, u3y + 28)
    u3_a2 = (u3x + u3w + 12, u3y + 52)
    u3_lv = (u3x + u3w + 12, u3y + 85)
    u3_gndr = (u3x + u3w + 12, u3y + 115)

    # ===== U1 Pi header as pin strip =====
    u1x, u1y, u1w, u1h = 920, 130, 64, 175
    L('<g id="U1">')
    L(f'<rect class="symf" x="{u1x}" y="{u1y}" width="{u1w}" height="{u1h}"/>')
    # pin circles on left edge suggesting header
    for yy, lab1, lab2 in [
        (u1y + 24, "GPIO2", "SDA p3"),
        (u1y + 50, "GPIO3", "SCL p5"),
        (u1y + 85, "3V3", "pin 1"),
        (u1y + 118, "5V", "pin 2/4"),
        (u1y + 150, "GND", "pin 6"),
    ]:
        wire(f"M {u1x-12} {yy} H {u1x}")
        term(u1x - 12, yy) if False else None
        L(f'<text class="pin" x="{u1x+3}" y="{yy-1}">{lab1}</text>')
        L(f'<text class="pin" x="{u1x+3}" y="{yy+9}">{lab2}</text>')
    L(f'<text class="ref" x="{u1x}" y="{u1y-14}">U1</text>')
    L(f'<text class="val" x="{u1x}" y="{u1y-3}">Pi 4</text>')
    L(f'<text class="note" x="{u1x}" y="{u1y+u1h+11}">U_PI · 5V pin TBD</text>')
    L("</g>")
    u1_sda = (u1x - 12, u1y + 24)
    u1_scl = (u1x - 12, u1y + 50)
    u1_3v3 = (u1x - 12, u1y + 85)
    u1_5v = (u1x - 12, u1y + 118)
    u1_gnd = (u1x - 12, u1y + 150)

    # ===== Wiring =====
    gnd_y = 480

    # +24V_LOOP
    wire(f"M {ps1_vp[0]} {ps1_vp[1]} H {j1_p[0]}")
    j(*ps1_vp)
    j(*j1_p)
    L(f'<text class="net" x="145" y="{ps1_vp[1]-8}">+24V_LOOP</text>')
    L(f'<use href="#pwr" x="160" y="{ps1_vp[1]-20}"/>')
    wire(f"M 160 {ps1_vp[1]-14} V {ps1_vp[1]}")
    j(160, ps1_vp[1])
    L(f'<text class="net" x="168" y="{ps1_vp[1]-22}">+24V</text>')

    # J1- to R1 high — need to route: J1- is at y=230, R1 high at 230
    wire(f"M {j1_m[0]} {j1_m[1]} H {rx}")
    j(*j1_m)
    j(*r_hi)
    L(f'<text class="net" x="260" y="{r_hi[1]-8}">NET_SHUNT_HIGH</text>')

    # Branch to AIN0
    wire(f"M {rx} {r_hi[1]} H 400 V {u2_ain0[1]} H {u2_ain0[0]}")
    j(400, r_hi[1])
    j(*u2_ain0)

    # R1 low to GND
    wire(f"M {r_lo[0]} {r_lo[1]} V {gnd_y}")
    j(rx, gnd_y)

    # GND rail
    wire(f"M 55 {gnd_y} H 1050", "wb")
    L(f'<text class="net" x="60" y="{gnd_y-7}">GND</text>')
    L(f'<use href="#gnd" x="{rx}" y="{gnd_y}"/>')
    L(f'<text class="note" x="{rx+14}" y="{gnd_y+16}">star @ shunt-low / brass bar</text>')

    # 0V_LOOP
    wire(f"M {ps1_vn[0]} {ps1_vn[1]} H 145 V {gnd_y}")
    j(145, gnd_y)
    L('<text class="net" x="150" y="300">0V_LOOP</text>')
    L('<text class="note" x="150" y="312">bonded to GND</text>')

    # U2 GND/ADDR
    wire(f"M {u2_gnd[0]} {u2_gnd[1]} H 430 V {gnd_y}")
    j(430, gnd_y)
    wire(f"M {u2_addr[0]} {u2_addr[1]} H 422 V {u2_gnd[1]}")
    j(422, u2_gnd[1])
    L(f'<text class="net" x="405" y="{u2_addr[1]-6}">GND</text>')

    # U3 / U1 GND
    wire(f"M {u3_gndl[0]} {u3_gndl[1]} H 640 V {gnd_y}")
    j(640, gnd_y)
    wire(f"M {u3_gndr[0]} {u3_gndr[1]} H 770 V {gnd_y}")
    j(770, gnd_y)
    wire(f"M {u1_gnd[0]} {u1_gnd[1]} H 900 V {gnd_y}")
    j(900, gnd_y)

    # I2C 5V
    wire(f"M {u2_sda[0]} {u2_sda[1]} H {u3_b1[0]}")
    j(*u2_sda)
    j(*u3_b1)
    L(f'<text class="net" x="545" y="{u2_sda[1]-7}">I2C_SDA_5V</text>')
    wire(f"M {u2_scl[0]} {u2_scl[1]} H {u3_b2[0]}")
    j(*u2_scl)
    j(*u3_b2)
    L(f'<text class="net" x="545" y="{u2_scl[1]-7}">I2C_SCL_5V</text>')

    # I2C 3V3
    wire(f"M {u3_a1[0]} {u3_a1[1]} H {u1_sda[0]}")
    j(*u3_a1)
    j(*u1_sda)
    L(f'<text class="net" x="780" y="{u3_a1[1]-7}">I2C_SDA_3V3</text>')
    wire(f"M {u3_a2[0]} {u3_a2[1]} H {u1_scl[0]}")
    j(*u3_a2)
    j(*u1_scl)
    L(f'<text class="net" x="780" y="{u3_a2[1]-7}">I2C_SCL_3V3</text>')

    # +3V3
    wire(f"M {u1_3v3[0]} {u1_3v3[1]} H {u3_lv[0]}")
    j(*u1_3v3)
    j(*u3_lv)
    L(f'<text class="net" x="800" y="{u1_3v3[1]-7}">+3V3_PI</text>')
    L(f'<use href="#pwr" x="840" y="{u1_3v3[1]-26}"/>')
    wire(f"M 840 {u1_3v3[1]-20} V {u1_3v3[1]}")
    j(840, u1_3v3[1])
    L(f'<text class="net" x="848" y="{u1_3v3[1]-28}">+3V3</text>')

    # +5V_ADS top rail
    rail_y = 110
    wire(f"M {u1_5v[0]} {u1_5v[1]} H 890 V {rail_y} H 410")
    j(890, rail_y)
    j(*u1_5v)
    L(f'<text class="net" x="600" y="{rail_y-7}">+5V_ADS</text>')
    L(f'<use href="#pwr" x="580" y="{rail_y-20}"/>')
    wire(f"M 580 {rail_y-14} V {rail_y}")
    j(580, rail_y)
    L(f'<text class="net" x="588" y="{rail_y-22}">+5V</text>')
    wire(f"M 640 {rail_y} V {u3_hv[1]} H {u3_hv[0]}")
    j(640, rail_y)
    j(*u3_hv)
    wire(f"M 410 {rail_y} V {u2_vdd[1]} H {u2_vdd[0]}")
    j(410, rail_y)
    j(*u2_vdd)

    # Legend + title block
    L(
        '''<g id="legend">
  <text class="tbb" x="38" y="540">Designators (CONNECTIONS.md)</text>
  <text class="tb" x="38" y="554">PS1=PSU_MW · J1=TT_RM · R1=RS250 · U2=U_ADS · U3=U_LLC · U1=U_PI</text>
  <text class="note" x="38" y="568">Omit Fluke / relay / software. No invented AIN1-3 or LLC unused ties. V=I*250R.</text>
</g>'''
    )

    tbx, tby = 1100, 520
    L(
        f'''<g id="tb">
  <rect class="symf" x="{tbx}" y="{tby}" width="360" height="150"/>
  <line class="w" x1="{tbx}" y1="{tby+28}" x2="{tbx+360}" y2="{tby+28}"/>
  <line class="w" x1="{tbx}" y1="{tby+56}" x2="{tbx+360}" y2="{tby+56}"/>
  <line class="w" x1="{tbx}" y1="{tby+88}" x2="{tbx+360}" y2="{tby+88}"/>
  <line class="w" x1="{tbx}" y1="{tby+118}" x2="{tbx+360}" y2="{tby+118}"/>
  <line class="w" x1="{tbx+170}" y1="{tby+56}" x2="{tbx+170}" y2="{tby+150}"/>
  <line class="w" x1="{tbx+260}" y1="{tby+56}" x2="{tbx+260}" y2="{tby+150}"/>
  <text class="tbb" x="{tbx+8}" y="{tby+18}">DCS — Distributed Control System (bench)</text>
  <text class="tb" x="{tbx+8}" y="{tby+46}">Loop · 250R shunt · ADS1115 · LLC · Pi 4</text>
  <text class="tbb" x="{tbx+8}" y="{tby+76}">SCH-DCS-003</text>
  <text class="tbb" x="{tbx+178}" y="{tby+76}">REV F</text>
  <text class="tb" x="{tbx+268}" y="{tby+76}">1 / 1</text>
  <text class="tb" x="{tbx+8}" y="{tby+108}">2026-09-28</text>
  <text class="tb" x="{tbx+178}" y="{tby+108}">NTS</text>
  <text class="tb" x="{tbx+268}" y="{tby+108}">A3L</text>
  <text class="note" x="{tbx+8}" y="{tby+138}">Truth: CONNECTIONS.md · not SKiDL auto-layout</text>
</g>'''
    )

    L("</svg>")
    return "\n".join(a)


def main() -> None:
    svg = build_svg()
    ET.fromstring(svg)
    REPO.mkdir(parents=True, exist_ok=True)
    STORE_DOCS.mkdir(parents=True, exist_ok=True)
    STORE_MEDIA.mkdir(parents=True, exist_ok=True)

    svg_path = REPO / "schematic-blocks.svg"
    pdf_path = REPO / "schematic-blocks.pdf"
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
