[日本語](README.md) | English

# Software

The programs that run on the Raspberry Pi of PHOTON GLASS.
This program is one sample implementation of PHOTON GLASS. It reads aloud text captured by the first-person camera (it recognises the text in the image and speaks it).
When you press the camera button, it takes a photo, reads the text in it using Google Cloud, and reads it aloud through the speaker.
For preparing the Raspberry Pi (from writing the OS to automatic start-up), see [`docs/SETUP_RASPBERRY_PI.en.md`](../docs/SETUP_RASPBERRY_PI.en.md).

> [!NOTE]
> The comments in the programs and the messages they display are in Japanese.

## Files
| File | Contents |
|---|---|
| `main_async.py` | Main program (**asynchronous version**). **Use this one day to day** |
| `main_seq.py` | Main program (**sequential version**). A version whose flow is easy to follow, for learning how it works |
| `sound/` | Sound effects (start-up, shutter, communicating, before and after reading aloud, errors) |
| `test/hw_test.py` | Hardware test after assembly (LED → buttons → speaker → camera) |
| `api_key.txt.example` | A sample of `api_key.txt`, the file for the API key (create `api_key.txt` yourself, and do not publish it) |
| `setup/setup_pi.sh` | A script that does the Raspberry Pi setup in one go (installing software, audio output, automatic start-up, changing the name, etc.). For how to use it, see ["13." in `docs/SETUP_RASPBERRY_PI.en.md`](../docs/SETUP_RASPBERRY_PI.en.md#13-doing-the-setup-with-a-single-script) |
| `setup/photonglass.service` | The setting that starts `main_async.py` automatically at power-on (used by `setup_pi.sh`) |
| `setup/photonglass-reset` | A command that restores the program to its original state if it stops working after you modify it (installed by `setup_pi.sh`; for how to install it by hand, see ["6." in `docs/SETUP_RASPBERRY_PI.en.md`](../docs/SETUP_RASPBERRY_PI.en.md#save-the-original-program-and-install-the-restore-command)) |
| `setup/photonglass-fixname`, `setup/photonglass-fixname.service` | If a number such as `-2` gets added to the name (`<hostname>.local`), changes it back to the original name automatically (installed by `setup_pi.sh`; for details, see ["14." in `docs/SETUP_RASPBERRY_PI.en.md`](../docs/SETUP_RASPBERRY_PI.en.md#14-preparing-multiple-units)) |
| `setup/add_wifi.sh` | A script that registers a Wi-Fi network (you can register it in advance, even when you are not there) |
| `check_setup.sh` | A script that checks how far the setup has got (it only looks and changes nothing) |

## Which one should I use?
**Use `main_async.py` day to day, and read `main_seq.py` when you want to know how it works.**
Both do the same thing (take a photo → read the text → create the speech → read it aloud). What differs is how they proceed through the processing.

### `main_seq.py` (sequential version): read this one first
To use a cooking analogy, it works like **"standing at the stove waiting for the water to boil, and only then doing the next task"**.

- It goes through taking the photo → reading the text → creating the speech → reading it aloud **one at a time, from top to bottom**, waiting for each step to finish before moving on.
- The program flows straight from top to bottom, so **it is easy to follow what happens in what order**.
- On the other hand, it does not respond to the buttons while it is processing. Once it starts reading aloud, you have to listen to the end.

### `main_async.py` (asynchronous version): use this one day to day
To use the cooking analogy, it works like **"chopping vegetables while the water heats up, and stopping right away when someone calls you"**.

- Even while it is waiting for a reply over the network, it **plays sound effects and keeps watch on the buttons at the same time** (it uses Python's `asyncio`).
- This makes it more convenient for the user in the following ways.
  - Press the **camera button** while it is reading aloud to stop the current reading and **take a new photo right away**
  - Press the **sub button** while it is reading aloud to **stop the reading**
  - A sound effect keeps playing while it is communicating, so you can hear that it is working on something
- Because it contains the machinery for doing things at the same time, the flow of the program is a little harder to follow.

### Summary of the differences
| | `main_seq.py` (sequential version) | `main_async.py` (asynchronous version) |
|---|---|---|
| Best for | Learning how it works, practising modifications | Everyday use |
| How it proceeds | One step at a time, in order | Does other things at the same time while waiting |
| Buttons during processing | No response | Can take a new photo or stop |
| Sound effect while communicating | Plays once | Repeats until communication finishes |
| During the 5-second start-up sound | Cannot be operated | Pressing a button stops it right away, and it is ready to use |
| Library used for communication | `requests` | `httpx` |

Suggested way to read them: first get the overall flow from `main_seq.py`, then compare it with `main_async.py` to see how to write the same flow so that things happen at the same time. This makes it easier to understand.

## How to run
1. Create an API key in Google Cloud, and enable the **Cloud Vision API** and the **Cloud Text-to-Speech API**.
   - It is safer to put an API restriction on the key (limiting it to these two APIs).
2. Do not write the key in the program; write it on a single line in a file called `api_key.txt`.
   - Copy `api_key.txt.example` in this folder, name the copy `api_key.txt`, and replace its contents with your key.
   - The program reads `api_key.txt` from the same folder as the program file itself. If the file is missing or empty, the LED lights red, the network error sound plays, the reason is displayed, and the program stops (it waits instead of exiting, so that the error sound does not play over and over when it is started automatically).
   - **Do not publish `api_key.txt` on GitHub or anywhere else.** Someone else could use it and you could be charged for it (in this repository, it is excluded from git by `.gitignore`).
3. Install the required libraries.
   ```bash
   sudo apt install -y python3-gpiozero python3-picamera2 python3-httpx python3-requests
   ```
4. Run it. The program looks for the sound effects and `api_key.txt` in the folder where the program file is, so it works whichever folder you run it from.
   ```bash
   python3 software/main_async.py
   ```

## What the LED colours mean
| Colour | State |
|---|---|
| Green | Waiting (you can press the button) |
| Yellow | Communicating |
| Blue | Reading aloud |
| Red | Error (a sound effect tells you which error: camera / network / no text found) |

On the 2026 boards, the RGB LED part was changed, so GPIO9 = red, GPIO11 = green and GPIO10 = blue (different from the original board).

## Data sent and files left behind
- When you press the camera button, the photo you take is sent to the Google Cloud Vision API, and the text read from it to the Google Cloud Text-to-Speech API, over the internet. If you use it where people may appear in the photos, read ["1. Principles and use" in the Charter (`CHARTER.en.md`)](../CHARTER.en.md#1-principles-and-use).
- The last photo taken (`image.jpg`) and the speech audio (`speech.wav`) are left in the folder where the program file is (`~/photonglass` on the Raspberry Pi). They are overwritten the next time you take a photo. `main_async.py` also takes one photo when it starts, to check the camera. In this repository, these two files are excluded from git by `.gitignore`.
- The API charges depend on how much you use them. For details, see the pricing page of each Google Cloud API.
