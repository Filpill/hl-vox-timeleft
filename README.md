# Counter-Strike Pomodoro Timer

Python `dearpygui` application to manage your time -- now with Half-Life sky textures and sounds!

> https://youtube.com/shorts/OZr_s5ugzXM

<p align="center">
  <img src="https://raw.githubusercontent.com/Filpill/hl-vox-timeleft/refs/heads/main/assets/img/model/t-squad.png" alt="T Squad" height="220"/>
  <img src="https://raw.githubusercontent.com/Filpill/hl-vox-timeleft/refs/heads/main/assets/gif/hl-timer1.gif" alt="HL Timer" height="300"/>
  <img src="https://raw.githubusercontent.com/Filpill/hl-vox-timeleft/refs/heads/main/assets/img/model/ct-squad.png" alt="CT Squad" height="220"/>
</p>                                                                                                                        

### File Directory
Types of files stored in this project
<div align = center>
  
| Directory  | Description |
| :------------- | :------------- |
| **assets/**         | Store for application half-life assets |
| **assets/fonts/**   | Storing fonts for GUI |
| **assets/gif/**     | Storing animations for application showcase |
| **assets/img/**     | Storing images of half-life assets |
| **assets/sounds/**  | Storing sounds of half-life assets |
| **sandbox/**        | Testbed for GUI application features  |
  
</div>

### System Requirements
Sub-shell responsible for playing sounds effects and requires `ffmpeg` to be installed on users machine in run Python application:

***e.g. Arch install:***
```bash
sudo pacman -S ffmpeg
```

### Python Virtual Environment

Python environment is created using the **uv** package manager and the following files specify dependancies:

<div align = center>

| File | Description |
| :------------- | :------------- |
| **pyproject.toml** | Keep track of key library dependencies |
| **uv.lock** | Precisely captures all python package versions |
| **requirements.txt** | Default python requirements file compiled from pyproject.toml |

</div>

To create a virtual environment:
```bash
uv venv --python 3.12
```

To activate virtual environment: 
```bash                                  
source .venv/bin/activate                
```                                      

To add packages to pyproject.toml:
```bash                                  
uv add <package-name>
```

To compile package to requirements.txt:
```bash
uv pip compile pyproject.toml > requirements.txt
```

To install python library requirements:
```bash
uv sync
```
