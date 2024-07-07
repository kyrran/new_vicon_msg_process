python sample_trajectories_from_model.py short_training_period -h
python main.py -a SACfD -n 1000 -f output-test -v
python main.py  -t 4000 -algo SACfD -gui --show-demo




 make px4_sitl gz_x500^C
micro-xrce-dds-agent udp4 -p 8888


conda install -c conda-forge libgcc=5.2.0
conda install -c anaconda libstdcxx-ng
conda install -c conda-forge gcc=12.1.0

ros2 bag record -a
ros2 topic list

ros2 bag play rosbag2_2024_06_14-12_14_43_0.db3 
nano ~/.bashrc
source ~/.bashrc


pip install -r requirements.txt


conda config --set auto_activate_base true
conda config --set auto_activate_base false
conda deactivate


pip install future
pip install pyyaml lz4

