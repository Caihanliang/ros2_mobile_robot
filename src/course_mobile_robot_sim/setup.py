from glob import glob
import os
from setuptools import find_packages, setup

package_name = 'course_mobile_robot_sim'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        (os.path.join('share', package_name, 'urdf'),
         glob('urdf/*.urdf') + glob('urdf/*.xacro')),
        (os.path.join('share', package_name, 'urdf', 'components'),
         glob('urdf/components/*')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ROS 2 Course Teacher',
    maintainer_email='teacher@example.com',
    description='Teaching-oriented ROS 2 mobile robot simulation.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'keyboard_teleop_node = course_mobile_robot_sim.keyboard_teleop_node:main',
            'control_mode_node = course_mobile_robot_sim.control_mode_node:main',
            'cmd_vel_safety_node = course_mobile_robot_sim.cmd_vel_safety_node:main',
            'front_distance_node = course_mobile_robot_sim.front_distance_node:main',
        ],
    },
)
