# Dora pipeline Robots

Reachy2 is an open-source, humanoid robot designed by Pollen Robotics for research and development purposes. It features
modular and customizable components, allowing for flexible experimentation in robotics and AI. With its expressive face
and dexterous arms, Reachy1 can interact naturally with its environment. It supports various programming languages and
tools, making it accessible for a wide range of applications in academia and industry.

## Configuring

- Connect Camera USB

```bash
echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="03e7", MODE="0666"' | sudo tee /etc/udev/rules.d/80-movidius.rules
sudo udevadm control --reload-rules && sudo udevadm trigger
```

## License

This library is licensed under the [Apache License 2.0](../../LICENSE).