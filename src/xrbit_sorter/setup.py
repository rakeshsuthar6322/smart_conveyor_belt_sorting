from setuptools import find_packages, setup

package_name = 'xrbit_sorter'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'numpy', 'scipy'],
    zip_safe=True,
    maintainer='rakesh',
    maintainer_email='rakesh@todo.todo',
    description='State Machine and Kalman Tracker',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'sorter_node = xrbit_sorter.sorter_node:main'
        ],
    },
)
