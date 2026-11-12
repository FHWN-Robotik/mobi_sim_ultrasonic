# Mobi Sim Ultrasonic

ROS 2 Jazzy-Simulationspaket für den mobilen Roboter **Mobi** mit Gazebo Harmonic und sechs Ultraschallsensoren.

Dieses Projekt erweitert das ursprüngliche [Mobi Sim](https://github.com/FHWN-Robotik/mobi_sim) der FHWN-Robotik. Das Originalprojekt bleibt unverändert.

Die Simulation bietet einen Differential-Drive-Antrieb mit vier Rädern, LiDAR, IMU, Odometrie, sechs Ultraschallsensoren und eine vorbereitete RViz2-Visualisierung. Mobi kann mit Teleop gesteuert werden.

> **Sensormodell:** Die Ultraschallsensoren verwenden derzeit eine idealisierte Entfernungsmessung ohne zusätzliches Messrauschen. Gazebo erzeugt neun Laserstrahlen pro Sensor; ein ROS-2-Konverter veröffentlicht den kleinsten gültigen Abstand als `sensor_msgs/msg/Range`.

## 1. Voraussetzungen

- Ubuntu 24.04
- ROS 2 Jazzy
- Gazebo Harmonic
- Python 3 und `colcon`

ROS 2 Jazzy und Gazebo Harmonic müssen bereits eingerichtet sein. Weitere benötigte Pakete:

```bash
sudo apt update
sudo apt install -y \
  git \
  python3-colcon-common-extensions \
  python3-rosdep \
  ros-jazzy-xacro \
  ros-jazzy-robot-state-publisher \
  ros-jazzy-rviz2 \
  ros-jazzy-ros-gz-sim \
  ros-jazzy-ros-gz-bridge \
  ros-jazzy-rclpy \
  ros-jazzy-sensor-msgs \
  ros-jazzy-teleop-twist-keyboard
```

## 2. Repository klonen

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
# Nach Veröffentlichung die tatsächliche Repository-Adresse einsetzen:
git clone https://github.com/FHWN-Robotik/mobi_sim_ultrasonic.git
```

**Hinweis:** Die oben genannte URL ist die geplante Adresse und muss vor dem Studententest bestätigt werden.

## 3. Paket bauen

```bash
cd ~/ros2_ws
source /opt/ros/jazzy/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --packages-select mobi_sim_ultrasonic --symlink-install
source install/setup.bash
```

## 4. Gazebo starten (Terminal 1)

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 launch mobi_sim_ultrasonic mobi_gazebo.launch.py
```

Gazebo startet mit der einfachen Welt `empty.sdf`. Testhindernisse können bei Bedarf manuell eingefügt werden; eine zusätzliche Testwelt wird nicht benötigt.

## 5. Ultraschall-Konverter starten (Terminal 2)

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run mobi_sim_ultrasonic ultrasonic_converter.py
```

Der Konverter abonniert die sechs Gazebo-Scans und veröffentlicht je einen `sensor_msgs/msg/Range`-Messwert.

## 6. RViz2 starten (Terminal 3)

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run rviz2 rviz2 \
  -d ~/ros2_ws/src/mobi_sim_ultrasonic/rviz/mobi_ultrasonic.rviz \
  --ros-args -p use_sim_time:=true
```

Die Konfiguration zeigt das Robotermodell, LiDAR und die sechs Ultraschall-Messkegel. Als `Fixed Frame` wird für die relative Sensordarstellung `base_link` verwendet.

## 7. Mobi mit Teleop steuern (Terminal 4)

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Wichtige Tasten: `i` vorwärts, `,` rückwärts, `j` links drehen, `l` rechts drehen, `k` stoppen. Das Teleop-Terminal muss den Tastaturfokus besitzen. Langsam fahren und Messkegel in RViz2 beobachten.

## 8. Ultraschallsensoren und Topics

| Sensor | Richtung relativ zu Mobi | Range-Topic |
| --- | --- | --- |
| Vorne links | +X | `/ultrasonic/front_left` |
| Vorne rechts | +X | `/ultrasonic/front_right` |
| Hinten links | −X | `/ultrasonic/rear_left` |
| Hinten rechts | −X | `/ultrasonic/rear_right` |
| Links | +Y | `/ultrasonic/left` |
| Rechts | −Y | `/ultrasonic/right` |

Alle sechs Sensoren besitzen eigene `us_*_range_frame`-Koordinatensysteme. Die positive X-Achse zeigt jeweils in Messrichtung.

| Eigenschaft | Wert |
| --- | --- |
| Öffnungswinkel | 30° |
| Messbereich | 0,02–4,0 m |
| Aktualisierungsrate in Gazebo | 10 Hz |
| Strahlen pro Sensor | 9 |
| ROS-Ausgabe | `sensor_msgs/msg/Range` |

Beispiel zum Auslesen:

```bash
ros2 topic echo /ultrasonic/left --once
```

Ein endlicher `range`-Wert bezeichnet die Entfernung in Metern. `inf` kann bedeuten, dass im Messbereich kein Hindernis erkannt wurde.

Weitere wichtige Topics: `/cmd_vel`, `/odom`, `/scan`, `/imu`, `/joint_states`, `/robot_description`, `/tf` und `/tf_static`.

## 9. Projektstruktur

```text
mobi_sim_ultrasonic/
├── launch/
│   └── mobi_gazebo.launch.py
├── scripts/
│   └── ultrasonic_converter.py
├── urdf/
│   ├── mobi.urdf.xacro
│   ├── mobi.gazebo.xacro
│   └── common_properties.xacro
├── rviz/
│   └── mobi_ultrasonic.rviz
├── worlds/
│   └── empty.sdf
├── CMakeLists.txt
├── package.xml
├── README.md
└── LICENSE
```

## 10. Hinweise

- Gazebo, Konverter, RViz2 und Teleop werden bewusst separat gestartet.
- Die aktuelle RViz2-Konfiguration visualisiert Messungen relativ zu `base_link`. Die Gazebo-Modell-TF-Bridge wurde während der Entwicklung zur Vermeidung eines möglichen TF-Konflikts deaktiviert; die dynamische TF-Kette für Navigation sollte vor einem entsprechenden Einsatz gesondert geprüft werden.
- Das Sensormodell bildet noch keine realistischen Ultraschallreflexionen oder Messfehler ab.
- Programme werden in den jeweiligen Terminals mit `Strg + C` beendet.

## Lizenz und Ursprung

Basierend auf [FHWN-Robotik/mobi_sim](https://github.com/FHWN-Robotik/mobi_sim). Lizenz: Apache-2.0, siehe `LICENSE`.
