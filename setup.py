from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in cspl_accounting_tweaks/__init__.py
from cspl_accounting_tweaks import __version__ as version

setup(
	name='cspl_accounting_tweaks',
	version=version,
	description='Accounting tweaks to ERPnext. eg: autogen document on bank recon. etc',
	author='Charioteer Software Pvt Ltd',
	author_email='satish@charioteersoftware.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
