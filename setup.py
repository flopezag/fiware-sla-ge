from setuptools import setup, find_packages
from pip.req import parse_requirements

install_reqs = parse_requirements("requirements.txt", session=False)
requirements_list = [str(ir.req) for ir in install_reqs]

setup(
    name='fiware-sla-ge',
    version='1.0.0',
    packages=find_packages(exclude=['tests*']),
    install_requires=requirements_list,
    url='<github url>',
    license='Apache 2.0',
    author='Fernando Lopez',
    keywords=['fiware', 'fiware-ops', 'python2', 'pandas', 'JIRA', 'fiware-lab'],
    author_email='fernando.lopez@fiware.org',
    description='Management of FIWARE Generic Enablers help-desk tickets SLA data',
    classifiers=[
                  "License :: OSI Approved :: Apache Software License", ],
)
