[日本語](SETUP_RASPBERRY_PI.md) | English

# Raspberry Pi setup

This guide prepares the Raspberry Pi for PHOTON GLASS, from installing the OS through the hardware test to starting the program automatically.
It assumes that you have finished the assembly (steps 1–4 of [`BUILD_GUIDE.en.md`](BUILD_GUIDE.en.md)).

> [!NOTE]
> The programs and scripts used in this guide (such as `hw_test.py` and `check_setup.sh`) display their messages in Japanese. Where this guide quotes a message, an English translation is given alongside it.

## What you need
- Raspberry Pi Zero 2 WH (with the main board mounted and the camera unit, speaker and power cable connected)
- microSD card (we use a SanDisk Ultra 32GB, bought from Yodobashi Camera)
- A PC (Mac) and a device for reading and writing microSD cards
- Wi-Fi (used to communicate with Google Cloud)
- A monitor, keyboard and mouse for the initial setup (["0. What you need" in `BUILD_GUIDE.en.md`](BUILD_GUIDE.en.md#0-what-you-need))
- A Google Cloud API key ("[7. Prepare the API key](#7-prepare-the-api-key)")

This page uses the following names.

| Item | Name used on this page |
|---|---|
| Username | `photonglass` |
| Hostname | `raspberrypi` (the Raspberry Pi Imager default; from the PC, connect to it as `raspberrypi.local`) |
| Where the program goes | `~/photonglass` (`/home/photonglass/photonglass`) |

Passwords and Wi-Fi names are written as placeholders such as `<password>`. Replace them with your own.
If you choose a different username or hostname, change the commands on this page to match.

## 1. Write the OS to the microSD card
1. Install [Raspberry Pi Imager](https://www.raspberrypi.com/software/) on your PC and start it.
2. Choose the following.
   - Device: Raspberry Pi Zero 2 W
   - OS: Raspberry Pi OS (32-bit) (with desktop; Bookworm or later)
   - Storage: the microSD card
3. In OS customisation (advanced settings), set the following, then write the card.
   - Hostname: `raspberrypi`
   - Username: `photonglass`, password: `<password>`
   - Wi-Fi: SSID `<Wi-Fi name>`, password `<Wi-Fi password>`, country `JP` (outside Japan, use your own country)

The screens and item names in Imager differ slightly between versions.

## 2. First boot and enabling SSH
1. Insert the microSD card into the Raspberry Pi.
2. Connect a monitor to the Raspberry Pi's mini HDMI port, and the keyboard and mouse to its USB port (the micro USB port that is not for power).
3. Connect the mobile battery with the power cable and press the battery's power button (["Mobile battery to use" in `enclosure/usb-power-cable/README.en.md`](../enclosure/usb-power-cable/README.en.md#mobile-battery-to-use)).
4. When the desktop appears, open "Raspberry Pi Configuration" from "Preferences" in the menu, and enable SSH under "Interfaces". The names and locations of menus may differ slightly depending on the version of the OS.
5. From a terminal on your PC, check that you can connect via SSH.
   ```bash
   ssh photonglass@raspberrypi.local
   ```
   The first time you connect, if you are asked `Are you sure you want to continue connecting`, type `yes`, then enter the password (nothing is shown on screen as you type it).

You can run the commands from here on either in a terminal on your PC connected via SSH, or in a terminal on the Raspberry Pi's desktop.
Once you can connect via SSH, you can disconnect the monitor, keyboard and mouse (all the remaining steps can be done over SSH).

### Settings to keep SSH stable
These settings prevent SSH from becoming slow to respond and prevent connections by the name `raspberrypi.local` from failing. They are the same settings that `setup_pi.sh` in "[13.](#13-doing-the-setup-with-a-single-script)" makes.
1. Turn off Wi-Fi power saving.
   ```bash
   sudo mkdir -p /etc/NetworkManager/conf.d
   ```
   ```bash
   printf '[connection]\n# 2 = Wi-Fi power saving off\nwifi.powersave = 2\n' | sudo tee /etc/NetworkManager/conf.d/99-photonglass-wifi-powersave.conf > /dev/null
   ```
   ```bash
   sudo iw dev wlan0 set power_save off
   ```
2. So that the name does not get a number added, as in `raspberrypi-2.local`, make the Raspberry Pi announce its name over Wi-Fi IPv4 only (avahi setting).
   ```bash
   sudo sed -i -e "s/^#*use-ipv6=.*/use-ipv6=no/" -e "s/^#*allow-interfaces=.*/allow-interfaces=wlan0/" /etc/avahi/avahi-daemon.conf
   ```

The last command in step 1 turns power saving off immediately. The other settings take effect after the reboot at the end of "3.".

## 3. Set up audio output (DAC)
Make the main board's audio output (DAC) usable on the Raspberry Pi.
1. Open the configuration file.
   ```bash
   sudo nano /boot/firmware/config.txt
   ```
2. Add the following line at the end of the file (required).
   ```
   dtoverlay=hifiberry-dac
   ```
3. (Recommended) Change the line that reads `dtoverlay=vc4-kms-v3d` as follows. This setting stops audio from being output over HDMI.
   ```
   dtoverlay=vc4-kms-v3d,noaudio
   ```
4. Save and close (in nano: Ctrl+O → Enter → Ctrl+X), then reboot.
   ```bash
   sudo reboot
   ```
5. After rebooting, check that the audio output is recognised.
   ```bash
   aplay -l
   ```
   It is OK if `hifiberry` (`snd_rpi_hifiberry_dac`) appears in the list.

The main programs (`main_async.py`, `main_seq.py`) and the hardware test (`test/hw_test.py`) send sound directly to the audio output of the main board. You do not need to choose the output device in the desktop's sound settings.

## 4. Install the required software
```bash
sudo apt update
```
```bash
sudo apt install -y python3-gpiozero python3-picamera2 python3-httpx python3-requests
```
The `aplay` command, which plays sounds, comes with Raspberry Pi OS.

## 5. About the camera
No additional settings are needed for the camera (no changes to `config.txt` either).
You will check that the camera is recognised in "[8. Run the hardware test](#8-run-the-hardware-test)".

## 6. Copy the program to the Raspberry Pi
If you do not yet have this repository on your PC, download it from the repository page on GitHub with "Code" → "Download ZIP" and extract it, or get it with the following command.
```bash
git clone https://github.com/photonglass/photonglass.git
```
In a terminal on your PC (Mac), move into this repository's folder (`photonglass` if you used `git clone`, `photonglass-main` if you used the ZIP), then run the commands below.
They copy the contents of the `software` folder to `~/photonglass` on the Raspberry Pi.
```bash
ssh photonglass@raspberrypi.local "mkdir -p ~/photonglass"
```
```bash
scp -r software/main_async.py software/main_seq.py software/sound software/test software/setup software/check_setup.sh photonglass@raspberrypi.local:photonglass/
```
After copying, the Raspberry Pi contains the following (`api_key.txt` is put in place in the next step).
```
~/photonglass/
├── main_async.py     本体プログラム（普段使う）
├── main_seq.py       本体プログラム（流れの読みやすい版）
├── sound/            効果音
├── test/hw_test.py   動作テスト
├── setup/            準備をまとめて行うスクリプト、photonglass-reset、photonglass-fixname（「6.」の最後・「13.」・「14.」で使う）
├── check_setup.sh    準備ができているかを確認するスクリプト
└── api_key.txt       Google Cloud の API キー
```
The Japanese notes in the tree above mean:
- `main_async.py`: the main program (for everyday use)
- `main_seq.py`: the main program (a version whose flow is easier to follow)
- `sound/`: sound effects
- `test/hw_test.py`: hardware test
- `setup/`: the script that does the setup in one go, `photonglass-reset` and `photonglass-fixname` (used at the end of "6." and in "13." and "14.")
- `check_setup.sh`: a script that checks whether the setup is complete
- `api_key.txt`: the Google Cloud API key

When you have modified the program, copy it again with the same `scp` command.

### Save the original program and install the restore command
Before you start modifying the program, save the program you have just copied as the "original state" and install `photonglass-reset`, a command that restores it. This is the same work that `setup_pi.sh` in "[13. Doing the setup with a single script](#13-doing-the-setup-with-a-single-script)" does. Run steps 1–4 below on the Raspberry Pi (connected via SSH).
1. Create the folder to save to.
   ```bash
   sudo mkdir -p /opt/photonglass/original
   ```
2. Save the programs and sound effects.
   ```bash
   sudo cp -r ~/photonglass/main_async.py ~/photonglass/main_seq.py ~/photonglass/sound /opt/photonglass/original/
   ```
3. Record the location of the program folder (used by `photonglass-reset`).
   ```bash
   echo "$HOME/photonglass" | sudo tee /opt/photonglass/app_dir
   ```
4. Install `photonglass-reset`.
   ```bash
   sudo install -m 755 ~/photonglass/setup/photonglass-reset /usr/local/bin/photonglass-reset
   ```

If the program stops working after you have modified it, run `photonglass-reset` to go back to the state saved here. The API key (`api_key.txt`) is kept as it is, and your modified version is kept in `~/photonglass/backup_<date-time>/`. If you use it before setting up automatic start in "10.", an error is shown at the final step, where it restarts the program, but the restore itself has been completed.

## 7. Prepare the API key
1. Create an API key in Google Cloud, and enable the **Cloud Vision API** and the **Cloud Text-to-Speech API**.
   - It is safer to put an API restriction on the key (limiting it to these two APIs).
   - If billing (a billing account) is not enabled for the project, you will get a network error.
2. On your PC, copy the sample file to create `api_key.txt`, and replace its contents with your key, on a single line.
   ```bash
   cp software/api_key.txt.example software/api_key.txt
   ```
3. Copy it to `~/photonglass` on the Raspberry Pi.
   ```bash
   scp software/api_key.txt photonglass@raspberrypi.local:photonglass/
   ```

The program reads `api_key.txt` from the same folder as the program file itself. If the file is missing or empty, at start-up the LED lights red, the network error sound plays, and the program stops.

> [!WARNING]
> Do not publish `api_key.txt` on GitHub or anywhere else. Someone else could use it and you could be charged for it (in this repository, it is excluded from git by `.gitignore`).

## 8. Run the hardware test
Use `hw_test.py` to check the LED → buttons → speaker → camera, one at a time (run it on the Raspberry Pi).
```bash
python3 ~/photonglass/test/hw_test.py
```

| Test | What to do and check |
|---|---|
| LED | Red, green and blue each light for 2 seconds; check that each really lights in that colour. Finally all three light together: OK if it looks whitish |
| Buttons | Press each of the five buttons (camera button, main, sub, UP, DOWN) once. When all have responded, it moves on to the next test (Ctrl+C to abort) |
| Speaker | Turn the volume (VR1) up a little and unplug any headphones. OK if the start-up sound plays. When you plug in headphones, the speaker should go silent: OK if you hear the sound in the headphones |
| Camera | If the camera is found, it takes one picture and saves it as `~/test.jpg` |

You can copy the photo to your PC to check it (run this on the PC).
```bash
scp photonglass@raspberrypi.local:test.jpg .
```
To run just one test, add `led`, `button`, `sound` or `camera` at the end (e.g. `python3 ~/photonglass/test/hw_test.py camera`).

If something goes wrong:
- It says "音声ボード（snd_rpi_hifiberry_dac）が見つかりません" (audio board (snd_rpi_hifiberry_dac) not found) → check that `config.txt` contains `dtoverlay=hifiberry-dac`, and reboot ("[3. Set up audio output (DAC)](#3-set-up-audio-output-dac)")
- It says "カメラが見つかりません" (camera not found) → check the orientation and insertion of the FFC cable, the HDMI cable and the camera board

## 9. Run the program
```bash
python3 ~/photonglass/main_async.py
```
When the start-up sound plays and the LED turns green, it is ready. Press the camera button and it takes a photo and reads the text aloud. To stop it, press Ctrl+C.
The program looks for the sound effects and `api_key.txt` in the folder where the program file is, so it works whichever folder you run it from.

| LED colour | State |
|---|---|
| Green | Waiting (you can press the button) |
| Yellow | Communicating |
| Blue | Reading aloud |
| Red | Error (a sound effect tells you which: camera, network, or no text found) |

For the differences between the two programs (`main_async.py` and `main_seq.py`), see [`software/README.en.md`](../software/README.en.md).

## 10. Start automatically at power-on (systemd)
1. Create the service configuration file.
   ```bash
   sudo nano /etc/systemd/system/photonglass.service
   ```
   Its contents are as follows.
   ```ini
   [Unit]
   Description=PHOTON GLASS (photonglass)
   Wants=network-online.target
   After=network-online.target sound.target

   [Service]
   User=photonglass
   WorkingDirectory=/home/photonglass/photonglass
   ExecStart=/usr/bin/python3 /home/photonglass/photonglass/main_async.py
   Environment=PYTHONUNBUFFERED=1
   # 止まってしまったら（エラーやカメラの抜けなど）、5秒後に自動で動かし直す
   Restart=always
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```
   (The Japanese comment means: "If it stops (because of an error, the camera coming loose, etc.), restart it automatically after 5 seconds.")
   These contents are the same as the file that `setup_pi.sh` in "[13. Doing the setup with a single script](#13-doing-the-setup-with-a-single-script)" installs (`software/setup/photonglass.service`). This step can also be done automatically with `setup_pi.sh`.
2. Enable and start the service.
   ```bash
   sudo systemctl daemon-reload
   ```
   ```bash
   sudo systemctl enable --now photonglass
   ```
   From now on, `main_async.py` starts automatically when you power on.

| To do this | Command |
|---|---|
| See whether it is running | `systemctl status photonglass` |
| Stop it | `sudo systemctl stop photonglass` |
| Start it | `sudo systemctl start photonglass` |
| Apply a modified program | `sudo systemctl restart photonglass` |
| Stop it from starting automatically | `sudo systemctl disable --now photonglass` |

While it is running automatically, that program is using the camera. Before you run `python3 main_async.py` yourself or use `hw_test.py`, stop it first with `sudo systemctl stop photonglass`. When you have finished, start it again with `sudo systemctl start photonglass`.

## 11. Troubleshooting

| Symptom | What to check |
|---|---|
| Cannot connect to `raspberrypi.local` from the PC | Whether the Raspberry Pi is powered on, and whether it is connected to the same Wi-Fi as the PC. Wait a little for it to finish starting up |
| SSH says `REMOTE HOST IDENTIFICATION HAS CHANGED` (e.g. after you have rewritten the OS) | Run `ssh-keygen -R raspberrypi.local` on the PC, then connect again |
| At start-up it lights red, plays the network error sound and stops (and then does not respond to the buttons) | Whether `~/photonglass/api_key.txt` exists and is not empty ("[7. Prepare the API key](#7-prepare-the-api-key)") |
| Pressing the button plays the network error sound | Whether it is connected to Wi-Fi, whether the API key is correct, and whether the Google Cloud APIs and billing are enabled |
| The camera error sound plays | The orientation and insertion of the FFC cable, the HDMI cable and the camera board (the camera test in "[8. Run the hardware test](#8-run-the-hardware-test)") |
| No sound from the speaker | Whether hifiberry appears in `aplay -l`, the volume (VR1), and whether headphones are plugged in |
| The camera error sound plays, and a little later the start-up sound plays | The camera stopped delivering photos during use, so the program restarted. A loose FFC cable (turn the power off before reseating it) or an insufficient power supply |
| SSH is slow to respond or sometimes cannot connect | Wi-Fi power saving is active. It is turned off by "[Settings to keep SSH stable](#settings-to-keep-ssh-stable)" in "2." or by `setup_pi.sh` in "[13.](#13-doing-the-setup-with-a-single-script)" |
| You cannot connect with `<hostname>.local`, and the name has become a numbered one such as `<hostname>-2.local` | The Raspberry Pi has decided that its name clashed with another. Wait about a minute after powering on (if `photonglass-fixname` is installed, the name is changed back). If that does not fix it, apply the avahi setting in "[Settings to keep SSH stable](#settings-to-keep-ssh-stable)" in "2." (for details, see "[14. Preparing multiple units](#14-preparing-multiple-units)") |
| You want to see the messages of the program running automatically | `journalctl -u photonglass -n 30` shows the recent messages. If you stop it with `sudo systemctl stop photonglass` and then run it with `python3 ~/photonglass/main_async.py`, the messages appear in the terminal |

## 12. Shutting down
```bash
sudo poweroff
```
Wait a little for the Raspberry Pi to shut down, then press the battery's power button to cut the power. Cutting the power abruptly can corrupt the microSD card.

## 13. Doing the setup with a single script
`setup_pi.sh` does all of the following in one go: "[Settings to keep SSH stable](#settings-to-keep-ssh-stable)" in "2.", "3. Set up audio output (DAC)", "4. Install the required software", "[Save the original program and install the restore command](#save-the-original-program-and-install-the-restore-command)" in "6.", and "10. Start automatically at power-on". It is safe to run it any number of times.
Copy `setup/` as well in "6. Copy the program to the Raspberry Pi", then run it on the Raspberry Pi.
```bash
sudo bash ~/photonglass/setup/setup_pi.sh photon01
```
`photon01` is the name (hostname) for this Raspberry Pi. If you leave it out, the name is not changed. When the script has finished, reboot with `sudo reboot`.

What `setup_pi.sh` does:
- Installs the required software (`python3-gpiozero`, `python3-picamera2`, `python3-httpx`, `python3-requests`, `alsa-utils`)
- Adds `dtoverlay=hifiberry-dac` to `config.txt` and turns off HDMI audio
- Turns off Wi-Fi power saving (to keep SSH from becoming slow or unable to connect) and connects automatically to registered Wi-Fi networks
- Stops the desktop from starting (because the Raspberry Pi Zero 2 W has little memory; this does not affect operation over SSH)
- Keeps the name from getting a number added (e.g. `photon01-2.local`), and if it still does, changes it back automatically (`photonglass-fixname`; see "[14.](#14-preparing-multiple-units)")
- Changes the name (when you give an argument)
- Sets `main_async.py` to start automatically at power-on (`photonglass.service`)
- Saves the current program as the "original state" and installs `photonglass-reset`, the command that restores it. If the program stops working after you have modified it, you can go back with `photonglass-reset` (your modified version is kept in `~/photonglass/backup_<date-time>/`)

You can check from your PC whether the setup is complete with `check_setup.sh` (it only looks and changes nothing; it does not display the API key or Wi-Fi passwords). If there are any `[NG]` lines, apply the fix written on that line.
```bash
ssh photonglass@photon01.local 'bash -s' < software/check_setup.sh
```

You can register the Wi-Fi of the place where you will use the device in advance, even if you are not there. You are asked for the password after you run the command (it is not left on screen or in the command history). The number is the priority: networks with larger numbers are connected to first.
```bash
sudo bash ~/photonglass/setup/add_wifi.sh "Wi-Fiの名前" 20
```
Replace `Wi-Fiの名前` ("Wi-Fi name") with the name (SSID) of the Wi-Fi network.

## 14. Preparing multiple units
Once the first unit is complete, you can prepare the rest quickly by duplicating its microSD card.
- **Change the name of each unit.** Every duplicated card starts up with the same name as the first unit. Start them one at a time, change the name with a command such as `sudo raspi-config nonint do_hostname photon02`, and reboot (if Raspberry Pis with the same name are running at the same time, you cannot tell which one you are connecting to).
- **If the name gets a number added.** Sometimes `photon02.local` cannot be found and the name becomes something like `photon02-2.local`. There are two causes.
  - The Raspberry Pi announces its name over more than one channel (such as IPv4 and IPv6) and concludes that its own announcements clash ("the name is taken"). This can be prevented by the avahi setting in "[Settings to keep SSH stable](#settings-to-keep-ssh-stable)" in "2." or in `setup_pi.sh`. If you have not made this setting yet, run the following and then reboot.
    ```bash
    sudo sed -i -e "s/^#*use-ipv6=.*/use-ipv6=no/" -e "s/^#*allow-interfaces=.*/allow-interfaces=wlan0/" /etc/avahi/avahi-daemon.conf
    ```
  - The Wi-Fi router sends the Raspberry Pi's "I am going to use this name" announcement straight back, and the Raspberry Pi mistakes it for a reply from another device. This tends to happen when many units are powered on at the same time, and the avahi setting cannot prevent it. `photonglass-fixname`, which `setup_pi.sh` installs, checks the name about 20 seconds after start-up and, if a number has been added, changes it back to the original name (after that, it keeps checking every minute). If you wait about a minute after powering on, you can connect with `photon02.local`. You can see what it did with `journalctl -u photonglass-fixname`. To install it without using `setup_pi.sh`, copy `setup/` and then run the following.
    ```bash
    sudo apt install -y avahi-utils
    ```
    ```bash
    sudo install -m 755 ~/photonglass/setup/photonglass-fixname /usr/local/bin/photonglass-fixname
    ```
    ```bash
    sudo install -m 644 ~/photonglass/setup/photonglass-fixname.service /etc/systemd/system/photonglass-fixname.service
    ```
    ```bash
    sudo systemctl daemon-reload && sudo systemctl enable --now photonglass-fixname
    ```
  If a unit cannot be found by name, look up its IP address, for example on the Wi-Fi router's admin page, and connect by IP address, as in `ssh photonglass@192.168.x.x`.
- **SSH warnings.** After you change the name or rewrite the card, your PC may show `REMOTE HOST IDENTIFICATION HAS CHANGED`. Run `ssh-keygen -R photon02.local`, then connect again.
- **API key and Wi-Fi passwords.** The duplicated cards also contain `api_key.txt` and the Wi-Fi passwords. Do not give the cards or image files to other people, or publish them.
