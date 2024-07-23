# Dora pipeline Robots

Reachy1 is an open-source, humanoid robot designed by Pollen Robotics for research and development purposes. It features
modular and customizable components, allowing for flexible experimentation in robotics and AI. With its expressive face
and dexterous arms, Reachy1 can interact naturally with its environment. It supports various programming languages and
tools, making it accessible for a wide range of applications in academia and industry.

## Recording

This section explains how to record episodes for LeRobot using the Reachy1 Robot.

Recording is the process of tele operating the robot and saving the episodes to a dataset. The dataset is used to train
the robot to perform tasks autonomously.

- Robot manipulation

Click on the button on the base to turn on the robot, then click on the button on the shoulder of the robot.\
Make sure the emergency button is not pressed in.

- Reachy Initialization

```bash
ssh bedrock@192.168.1.51

cd dev_docker
sudo service stop


docker compose -f mode/dev.yaml up -d core

docker exec -it core bash

# In the docker container

ros2 launch reachy_bringup reachy.launch.py start_sdk_server:=true
```

- Data Collection

```bash
cd dora-lerobot/

# If you are using a custom environment, you will have to activate it before running the command
source [your_custom_env_bin]/activate

# If you followed the installation instructions, you can run the following command
source venv/bin/activate # On Linux
source venv/Scripts/activate # On Windows bash
venv\Scripts\activate.bat # On Windows cmd
venv\Scripts\activate.ps1 # On Windows PowerShell

python reachy2_hdf5_recorder/reachy1_record_episodes_hdf5.py -n <recording_session_name>_raw -l <epiodes_duration in s>

# Must have a HugginFace token with write permission in https://huggingface.co/settings/tokens
huggingface-cli login --token ${HUGGINGFACE_TOKEN} --add-to-git-credential

python ./lerobot/lerobot/scripts/push_dataset_to_hub.py 
    -data-dir data 
    --dataset-id <recording_session_name>
    --raw-format reachy2_hdf5 
    --community-id <HuggingFace_id>
```

- Training

```bash
cd dora-lerobot/

# If you are using a custom environment, you will have to activate it before running the command
source [your_custom_env_bin]/activate

# If you followed the installation instructions, you can run the following command
source venv/bin/activate # On Linux
source venv/Scripts/activate # On Windows bash
venv\Scripts\activate.bat # On Windows cmd
venv\Scripts\activate.ps1 # On Windows PowerShell

python lerobot/scripts/train.py 
    policy=act_reachy2_real 
    env=dora_reachy2_real 
    wandb.enable=true 
    hydra.run.dir=<recording_session_name> 
    env.state_dim=8 
    nv.action_dim=8 
    dataset_repo_id=<HuggingFace_id>/<recording_session_name>
```

- Evaluation

Inside of the file `lerobot/<recording_session_name>/checkpoints/last/pretrained_model/config.yaml` change the env.task from DoraReachy2-v0 to DoraReachy1-v0.

Make sure to get the right path for the source and args of eval in the file eval.yml

```bash
cd dora-lerobot/

# If you are using a custom environment, you will have to activate it before running the command
source [your_custom_env_bin]/activate

# If you followed the installation instructions, you can run the following command
source venv/bin/activate # On Linux
source venv/Scripts/activate # On Windows bash
venv\Scripts\activate.bat # On Windows cmd
venv\Scripts\activate.ps1 # On Windows PowerShell

dora up
dora start ./robots/reachy1/graphs/eval.yml
```

## License

This library is licensed under the [Apache License 2.0](../../LICENSE).