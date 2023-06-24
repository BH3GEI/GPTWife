from setuptools import setup, find_packages

setup(
    name='GPTPET_1.0',
    version='1.0',
    packages=find_packages(),
    install_requires=['os', 'sys', 'random', 'PyQt5', 'weather', 'datetime', 'requests', 'json', 'cv2', 'numpy', 'tensorflow', 'keras'],
    author="Dai Yina",  # 作者
    description="A desktop pet"  # 描述
)
