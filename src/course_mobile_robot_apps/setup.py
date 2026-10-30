from glob import glob
import os
from setuptools import find_packages, setup

package_name = 'course_mobile_robot_apps'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ROS 2 Course Teacher',
    maintainer_email='teacher@example.com',
    description='Multi-mode mobile robot applications.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'simple_cruise_node = course_mobile_robot_apps.simple_cruise_node:main',
            'simple_goal_navigation_node = course_mobile_robot_apps.simple_goal_navigation_node:main',
        ],
    },
)
