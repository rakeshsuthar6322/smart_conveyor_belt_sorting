from setuptools import find_packages, setup

package_name = 'xrbit_vision'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='rakesh',
    maintainer_email='rakeshsuthar6322@gmail.com',
    description='YOLOv8 Vision Node for XRbit Sorter',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'vision_node = xrbit_vision.vision_node:main'
        ],
    },
)
