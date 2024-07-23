# Dora pipeline Robots

Reachy1 is an open-source, humanoid robot designed by Pollen Robotics for research and development purposes. It features
modular and customizable components, allowing for flexible experimentation in robotics and AI. With its expressive face
and dexterous arms, Reachy1 can interact naturally with its environment. It supports various programming languages and
tools, making it accessible for a wide range of applications in academia and industry.

## Installation

Dataflow-oriented robotic application (Dora) is a framework that makes creation of robotic applications fast and simple.
See [Dora repository](https://github.com/dora-rs/dora).

**Please read the instructions carefully before installing the required software and environment to run the robot.**

You must install Dora before attempting to run theAloha Robot pipeline. Here are the steps to install Dora:

- Install Rust by following the instructions at [Rustup](https://rustup.rs/). (You may need to install Visual Studio C++
  build tools on Windows.)
- Install Dora by running the following command:

```bash
cargo install dora-cli
```

Now you're ready to run Rust dataflow applications! We decided to only make Python dataflow for Aloha Robot, so
you may need to setup your Python environment:

- Install Python 3.12 or later by following the instructions at [Python](https://www.python.org/downloads/).
- Clone this repository by running the following command:

```bash
git clone https://github.com/dora-rs/dora-lerobot
```

- Open a bash terminal and navigate to the repository by running the following command:

```bash
cd dora-lerobot
```

- Create a virtual environment by running the following command (you can find where is all your pythons executable with
  the command `whereis python3` on Linux, on default for Windows it's located
  in `C:\Users\<User>\AppData\Local\Programs\Python\Python3.12\python.exe)`):

```bash
path_to_your_python3_executable -m venv venv
```

- Activate the virtual environment by running the following command:

```bash
source venv/bin/activate # On Linux
source venv/Scripts/activate # On Windows bash
venv\Scripts\activate.bat # On Windows cmd
venv\Scripts\activate.ps1 # On Windows PowerShell

pip install dora-rs
```

- Install Teleoperation Collector

```bash
git clone https://github.com/pollen-robotics/reachy2_hdf5_recorder/
pip install -r reachy2_hdf5_recorder/requirements.txt
```

- Install LeRobot

```bash
git clone https://github.com/huggingface/lerobot.git && cd lerobot
git checkout origin/user/rcadene/2024_06_03_reachy2
cd ..
pip install -e ./lerobot
```

## License

This library is licensed under the [Apache License 2.0](../../LICENSE).