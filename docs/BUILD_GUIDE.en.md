[日本語](BUILD_GUIDE.md) | English

# PHOTON GLASS build guide

This page sets out the order of the work when you build PHOTON GLASS from scratch.
For details of each step, see the linked documents.

## Overview

| Step | Task | Details |
|---|---|---|
| 0 | Gather what you need | "[0. What you need](#0-what-you-need)" on this page |
| 1 | Order the boards | [`hardware/JLCPCB_ORDERING.en.md`](../hardware/JLCPCB_ORDERING.en.md) |
| 2 | Hand-solder the remaining parts | ["Parts not to be assembled (hand-soldered)" in `hardware/JLCPCB_ORDERING.en.md`](../hardware/JLCPCB_ORDERING.en.md#parts-not-to-be-assembled-hand-soldered) |
| 3 | Print the enclosures | Main body: ["Print settings" in `enclosure/main-body/README.en.md`](../enclosure/main-body/README.en.md#print-settings); camera unit: ["Print settings" in `enclosure/camera-unit/README.en.md`](../enclosure/camera-unit/README.en.md#print-settings) |
| 4 | Assemble | "[4. Assemble](#4-assemble)" on this page |
| 5 | Set up the Raspberry Pi | Steps 1–7 of [`SETUP_RASPBERRY_PI.en.md`](SETUP_RASPBERRY_PI.en.md) |
| 6 | Hardware test (hw_test) | ["8. Run the hardware test" in `SETUP_RASPBERRY_PI.en.md`](SETUP_RASPBERRY_PI.en.md#8-run-the-hardware-test) |
| 7 | Run the program | ["9. Run the program" in `SETUP_RASPBERRY_PI.en.md`](SETUP_RASPBERRY_PI.en.md#9-run-the-program) |

## 0. What you need

### Parts for the boards, enclosures and power cable
See the parts list in each document.
- Boards (parts assembled by JLCPCB and parts you solder by hand): [`hardware/JLCPCB_ORDERING.en.md`](../hardware/JLCPCB_ORDERING.en.md). Details of every part are in [`parts_list.en.md`](parts_list.en.md)
- Main body enclosure (screws): ["Required parts" in `enclosure/main-body/README.en.md`](../enclosure/main-body/README.en.md#required-parts)
- Camera unit (camera, screws, cable ties): ["Required parts" in `enclosure/camera-unit/README.en.md`](../enclosure/camera-unit/README.en.md#required-parts)
- Power cable (USB plug, wires, connector, etc.): ["Parts" in `enclosure/usb-power-cable/README.en.md`](../enclosure/usb-power-cable/README.en.md#parts)
- 3D printer filament (PETG): ["Print settings" in `enclosure/main-body/README.en.md`](../enclosure/main-body/README.en.md#print-settings) (about 65–75 g per main body), ["Print settings" in `enclosure/camera-unit/README.en.md`](../enclosure/camera-unit/README.en.md#print-settings)

### Other things you need

| Item | Model, etc. | Used for |
|---|---|---|
| Raspberry Pi Zero 2 WH | With the pin header already fitted | Plugs into the 40-pin socket on the main board |
| microSD card | SanDisk Ultra 32GB | Holds the Raspberry Pi OS |
| FFC cable | Würth Elektronik 6876 series 687622100002 (100 mm, 0.5 mm pitch) | Connects the main board and the Raspberry Pi |
| HDMI cable | CAC-HD14US07BK (0.7 m) | Connects the main board and the camera unit (camera board) |
| Speaker | MSI28-12R (Akizuki Denshi) | Connects to the `SPK` connector on the main board |
| Mobile battery | cheero Canvas 3200mAh IoT機器対応 (for IoT devices) CHE-061-BK-IOT2 | Power supply (["Mobile battery to use" in `enclosure/usb-power-cable/README.en.md`](../enclosure/usb-power-cable/README.en.md#mobile-battery-to-use)) |
| Glasses | — | The camera unit is attached to them |

For the initial setup of the Raspberry Pi, you will also use the following.
- A monitor, and a mini HDMI to HDMI cable (or adapter). The video output of the Raspberry Pi Zero 2 W is a mini HDMI port.
- A keyboard and mouse, and a micro USB (male) to USB-A (female) adapter cable (OTG cable). The Raspberry Pi Zero 2 W has only one micro USB port for data, so to connect both a keyboard and a mouse, use a USB hub, or a wireless keyboard and mouse that share a single receiver. During development we used the AFSSLCBL L-shaped micro USB cable and the USB-4AF203AS USB-A female connector.

## 1. Order the boards
Order the main board and the camera board from JLCPCB with "PCB fabrication + parts assembly".
- Instructions: steps 1–5 of [`hardware/JLCPCB_ORDERING.en.md`](../hardware/JLCPCB_ORDERING.en.md)
- Part details (differences from the original parts, datasheets): [`parts_list.en.md`](parts_list.en.md)

## 2. Hand-solder the remaining parts
When the main board arrives, solder on the parts that you did not have assembled.
- Parts to fit: ["Parts not to be assembled (hand-soldered)" in `hardware/JLCPCB_ORDERING.en.md`](../hardware/JLCPCB_ORDERING.en.md#parts-not-to-be-assembled-hand-soldered)
- If you did not have the 40-pin socket (`U$1`) assembled, fit it as well (["3. Checking the parts (BOM screen)" in `hardware/JLCPCB_ORDERING.en.md`](../hardware/JLCPCB_ORDERING.en.md#3-checking-the-parts-bom-screen)).
- Orientation of the speaker connector: [`hardware/main-board/images/speaker_connector_orientation.png`](../hardware/main-board/images/speaker_connector_orientation.png)

## 3. Print the enclosures
- Main body: ["Print settings" in `enclosure/main-body/README.en.md`](../enclosure/main-body/README.en.md#print-settings)
- Camera unit: ["Print settings" in `enclosure/camera-unit/README.en.md`](../enclosure/camera-unit/README.en.md#print-settings)
- Cover for the USB plug of the power cable: ["1. Print the cover" in `enclosure/usb-power-cable/README.en.md`](../enclosure/usb-power-cable/README.en.md#1-print-the-cover)

## 4. Assemble
- Main body: ["Assembly" in `enclosure/main-body/README.en.md`](../enclosure/main-body/README.en.md#assembly) (fix the body back to the body front with four screws)
- Camera unit: ["Assembly" in `enclosure/camera-unit/README.en.md`](../enclosure/camera-unit/README.en.md#assembly) (from connecting the camera and the camera board through to attaching the unit to the glasses)
- Power cable: ["How to make it" in `enclosure/usb-power-cable/README.en.md`](../enclosure/usb-power-cable/README.en.md#how-to-make-it) (always carry it through to the last step, "6. Check")

### Where to connect

| What to connect | Main board side | Other end | Notes |
|---|---|---|---|
| Raspberry Pi Zero 2 WH | 40-pin socket (`U$1`) | The Raspberry Pi's pin header | |
| FFC cable | `CN2` (camera connector) | The Raspberry Pi's camera connector | If the orientation or insertion is wrong, the camera will not be found (check with the [hardware test](SETUP_RASPBERRY_PI.en.md#8-run-the-hardware-test)) |
| HDMI cable | `CN3` (HDMI) | `CN1` (HDMI) on the camera board | This connector is for the camera board, not for a monitor |
| Speaker | `SPK` (2-pin) | Speaker | Connector orientation: [`speaker_connector_orientation.png`](../hardware/main-board/images/speaker_connector_orientation.png) |
| Power cable | `5V` (2-pin) | Mobile battery | Reversing + and − will destroy the Raspberry Pi. Always carry out "[6. Check](../enclosure/usb-power-cable/README.en.md#6-check-before-connecting-to-the-board-required)" before connecting |

## 5. Set up the Raspberry Pi
This covers everything from writing the OS to setting up the audio output (DAC), copying the program and preparing the API key.
- Instructions: steps 1–7 of [`SETUP_RASPBERRY_PI.en.md`](SETUP_RASPBERRY_PI.en.md)

## 6. Hardware test (hw_test)
Check that what you have assembled works, in the order LED → buttons → speaker → camera.
- Instructions: ["8. Run the hardware test" in `SETUP_RASPBERRY_PI.en.md`](SETUP_RASPBERRY_PI.en.md#8-run-the-hardware-test)

## 7. Run the program
- Instructions: ["9. Run the program" in `SETUP_RASPBERRY_PI.en.md`](SETUP_RASPBERRY_PI.en.md#9-run-the-program)
- Make it start automatically at power-on: ["10. Start automatically at power-on (systemd)" in `SETUP_RASPBERRY_PI.en.md`](SETUP_RASPBERRY_PI.en.md#10-start-automatically-at-power-on-systemd)
- Differences between the two programs (`main_async.py` and `main_seq.py`): [`software/README.en.md`](../software/README.en.md)

## Changing the design
- Boards: ["Opening the files" in `hardware/README.en.md`](../hardware/README.en.md#opening-the-files), notes on the KiCad version ([main board](../hardware/main-board/kicad/README.en.md), [camera board](../hardware/camera-board/kicad/README.en.md))
- Main body enclosure: ["Changing the design" in `enclosure/main-body/README.en.md`](../enclosure/main-body/README.en.md#changing-the-design)
- Camera unit enclosure: ["Changing the design" in `enclosure/camera-unit/README.en.md`](../enclosure/camera-unit/README.en.md#changing-the-design)
- Power cable cover: ["Files" in `enclosure/usb-power-cable/README.en.md`](../enclosure/usb-power-cable/README.en.md#files)
- Program: [`software/README.en.md`](../software/README.en.md)
