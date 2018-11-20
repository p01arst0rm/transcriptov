from setuptools import setup

setup(
    name='Transcriptov',
    version='1.0.0',
    description='A transcript based markov chain bot for twitter created in python 3.7',
    url='https://gitlab.com/p01arst0rm/transcriptov',
    author='p01arst0rm',
    author_email='polar@ever3st.com',
    license='MIT',
    packages=['Transcriptov'],
    install_requires=['tweepy>=3.6.0','markovify>=0.7.1'],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    zip_safe=False)
