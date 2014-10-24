""" This file contains configuration information for the build slave host
machines. """


import collections
import ntpath
import os
import posixpath
import sys

import skia_vars


buildbot_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             os.pardir))
sys.path.append(buildbot_path)


from compute_engine_scripts.compute_engine_cfg import \
    PROJECT_USER as CHROMECOMPUTE_USERNAME
from compute_engine_scripts.compute_engine_cfg import \
    PROJECT_ID as CHROMECOMPUTE_PROJECT


CHROMECOMPUTE_BUILDBOT_PATH = ['storage', 'skia-repo', 'buildbot']

# Indicates that this machine is not connected to a KVM switch.
NO_KVM_NUM = '(not on KVM)'

# Indicates that this machine has no static IP address.
NO_IP_ADDR = '(no static IP)'

# Files to copy into buildslave checkouts.
CHROMEBUILD_COPIES = [
  {
    "source": ".boto",
    "destination": "build/site_config",
  },
  {
    "source": ".bot_password",
    "destination": "build/site_config",
  },
]

GCE_PROJECT = skia_vars.GetGlobalVariable('gce_project')
GCE_USERNAME = skia_vars.GetGlobalVariable('gce_username')
GCE_ZONE = skia_vars.GetGlobalVariable('gce_compile_bots_zone')

GCE_COMPILE_A_ONLINE = GCE_ZONE == 'a'
GCE_COMPILE_B_ONLINE = GCE_ZONE == 'b'
GCE_COMPILE_C_ONLINE = True

LAUNCH_SCRIPT_UNIX = ['scripts', 'skiabot-slave-start-on-boot.sh']
LAUNCH_SCRIPT_WIN = ['scripts', 'skiabot-slave-start-on-boot.bat']

SKIALAB_ROUTER_IP = skia_vars.GetGlobalVariable('skialab_router_ip')
SKIALAB_USERNAME = skia_vars.GetGlobalVariable('skialab_username')


# Procedures for logging in to the host machines.

def skia_lab_login(hostname, config):
  """Procedure for logging into SkiaLab machines."""
  return [
    'ssh', '%s@%s' % (SKIALAB_USERNAME, SKIALAB_ROUTER_IP),
    'ssh', '%s@%s' % (SKIALAB_USERNAME, config['ip'])
  ]


def compute_engine_login(hostname, config):
  """Procedure for logging into Skia GCE instances."""
  return [
    'gcutil', '--project=%s' % GCE_PROJECT,
    'ssh', '--ssh_user=%s' % GCE_USERNAME, hostname,
  ]


def chromecompute_login(hostname, config):
  """Procedure for logging into ChromeCompute GCE instances."""
  return [
    'gcutil', '--project=%s' % CHROMECOMPUTE_PROJECT,
    'ssh', '--ssh_user=%s' % CHROMECOMPUTE_USERNAME, hostname,
  ]


# Data for all Skia build slave hosts.
_slave_host_dicts = {

################################ Linux Machines ################################

  'skiabot-shuttle-ubuntu12-gtx550ti-001': {
    'slaves': [
      ('skiabot-shuttle-ubuntu12-gtx550ti-001', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': skia_lab_login,
    'ip': '192.168.1.132',
    'kvm_num': 'A',
    'path_module': posixpath,
    'path_to_buildbot': ['buildbot'],
    'remote_access': True,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skiabot-shuttle-ubuntu12-gtx660-001': {
    'slaves': [
      ('skiabot-shuttle-ubuntu12-gtx660-000', '0', False),
      ('skiabot-shuttle-ubuntu12-gtx660-001', '0', False),
      ('skiabot-shuttle-ubuntu12-gtx660-002', '0', False),
      ('skiabot-shuttle-ubuntu12-gtx660-003', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': skia_lab_login,
    'ip': '192.168.1.113',
    'kvm_num': 'E',
    'path_module': posixpath,
    'path_to_buildbot': ['buildbot'],
    'remote_access': True,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skiabot-shuttle-ubuntu12-gtx660-002': {
    'slaves': [
      ('skiabot-shuttle-ubuntu12-gtx660-bench', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': skia_lab_login,
    'ip': '192.168.1.122',
    'kvm_num': 'F',
    'path_module': posixpath,
    'path_to_buildbot': ['buildbot'],
    'remote_access': True,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skiabot-shuttle-ubuntu12-android-003': {
    'slaves': [
      ('skiabot-shuttle-ubuntu12-xoom-001',        '0', False),
      ('skiabot-shuttle-ubuntu12-xoom-002',        '1', False),
      ('skiabot-shuttle-ubuntu12-xoom-003',        '2', False),
      ('skiabot-shuttle-ubuntu12-nexus7-001',      '6', False),
      ('skiabot-shuttle-ubuntu12-nexus7-002',      '7', False),
      ('skiabot-shuttle-ubuntu12-nexus7-003',      '8', False),
      ('skiabot-shuttle-ubuntu12-nexus10-001',     '9', False),
      ('skiabot-shuttle-ubuntu12-nexus10-003',     '10', False),
      ('skiabot-shuttle-ubuntu12-venue8-001',      '11', False),
      ('skiabot-shuttle-ubuntu12-nexus5-001',      '12', False),
      ('skiabot-shuttle-ubuntu12-nexus5-002',      '13', False),
      ('skiabot-shuttle-ubuntu12-galaxys4-001',    '14', False),
      ('skiabot-shuttle-ubuntu12-galaxys4-002',    '15', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': skia_lab_login,
    'ip': '192.168.1.110',
    'kvm_num': 'C',
    'path_module': posixpath,
    'path_to_buildbot': ['buildbot'],
    'remote_access': True,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skiabot-shuttle-ubuntu12-xxx': {
    'slaves': [
      ('skiabot-shuttle-ubuntu12-002',        '2', False),
      ('skiabot-shuttle-ubuntu12-003',        '3', False),
      ('skiabot-shuttle-ubuntu12-004',        '4', False),
      ('skiabot-shuttle-ubuntu12-nexus9-001', '5', True),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': skia_lab_login,
    'ip': '192.168.1.109',
    'kvm_num': 'B',
    'path_module': posixpath,
    'path_to_buildbot': ['buildbot'],
    'remote_access': True,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skiabot-shuttle-ubuntu13-xxx': {
    'slaves': [
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': skia_lab_login,
    'ip': '192.168.1.120',
    'kvm_num': 'D',
    'path_module': posixpath,
    'path_to_buildbot': ['buildbot'],
    'remote_access': True,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skiabot-shuttle-ubuntu13-002': {
    'slaves': [
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': skia_lab_login,
    'ip': '192.168.1.115',
    'kvm_num': 'G',
    'path_module': posixpath,
    'path_to_buildbot': ['buildbot'],
    'remote_access': True,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skia-vm-001': {
    'slaves': [
      ('skiabot-linux-compile-000', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': chromecompute_login,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': posixpath,
    'path_to_buildbot': CHROMECOMPUTE_BUILDBOT_PATH,
    'remote_access': GCE_COMPILE_C_ONLINE,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skia-vm-002': {
    'slaves': [
      ('skiabot-linux-compile-001', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': chromecompute_login,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': posixpath,
    'path_to_buildbot': CHROMECOMPUTE_BUILDBOT_PATH,
    'remote_access': GCE_COMPILE_C_ONLINE,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skia-vm-003': {
    'slaves': [
      ('skiabot-linux-compile-002', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': chromecompute_login,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': posixpath,
    'path_to_buildbot': CHROMECOMPUTE_BUILDBOT_PATH,
    'remote_access': GCE_COMPILE_C_ONLINE,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skia-vm-004': {
    'slaves': [
      ('skiabot-linux-compile-003', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': chromecompute_login,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': posixpath,
    'path_to_buildbot': CHROMECOMPUTE_BUILDBOT_PATH,
    'remote_access': GCE_COMPILE_C_ONLINE,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skia-vm-005': {
    'slaves': [
      ('skiabot-linux-compile-004', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': chromecompute_login,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': posixpath,
    'path_to_buildbot': CHROMECOMPUTE_BUILDBOT_PATH,
    'remote_access': GCE_COMPILE_C_ONLINE,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skia-vm-006': {
    'slaves': [
      ('skiabot-linux-compile-005', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': chromecompute_login,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': posixpath,
    'path_to_buildbot': CHROMECOMPUTE_BUILDBOT_PATH,
    'remote_access': GCE_COMPILE_C_ONLINE,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skia-vm-007': {
    'slaves': [
      ('skiabot-linux-compile-006', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': chromecompute_login,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': posixpath,
    'path_to_buildbot': CHROMECOMPUTE_BUILDBOT_PATH,
    'remote_access': GCE_COMPILE_C_ONLINE,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skia-vm-008': {
    'slaves': [
      ('skiabot-linux-compile-007', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': chromecompute_login,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': posixpath,
    'path_to_buildbot': CHROMECOMPUTE_BUILDBOT_PATH,
    'remote_access': GCE_COMPILE_C_ONLINE,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skia-vm-009': {
    'slaves': [
      ('skiabot-linux-compile-008', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': chromecompute_login,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': posixpath,
    'path_to_buildbot': CHROMECOMPUTE_BUILDBOT_PATH,
    'remote_access': GCE_COMPILE_C_ONLINE,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skia-vm-010': {
    'slaves': [
      ('skiabot-linux-compile-009', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': chromecompute_login,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': posixpath,
    'path_to_buildbot': CHROMECOMPUTE_BUILDBOT_PATH,
    'remote_access': GCE_COMPILE_C_ONLINE,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skia-vm-011': {
    'slaves': [
      ('skiabot-linux-compile-010', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': chromecompute_login,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': posixpath,
    'path_to_buildbot': CHROMECOMPUTE_BUILDBOT_PATH,
    'remote_access': GCE_COMPILE_C_ONLINE,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skia-vm-012': {
    'slaves': [
      ('skiabot-linux-compile-011', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': chromecompute_login,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': posixpath,
    'path_to_buildbot': CHROMECOMPUTE_BUILDBOT_PATH,
    'remote_access': GCE_COMPILE_C_ONLINE,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skia-vm-013': {
    'slaves': [
      ('skiabot-linux-compile-012', '0', False),
      ('skiabot-linux-housekeeper-000', '1', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': chromecompute_login,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': posixpath,
    'path_to_buildbot': CHROMECOMPUTE_BUILDBOT_PATH,
    'remote_access': GCE_COMPILE_C_ONLINE,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skia-vm-014': {
    'slaves': [
      ('skia-android-canary', '0', True),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': chromecompute_login,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': posixpath,
    'path_to_buildbot': CHROMECOMPUTE_BUILDBOT_PATH,
    'remote_access': GCE_COMPILE_C_ONLINE,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skia-vm-015': {
    'slaves': [
      ('skiabot-linux-housekeeper-001', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': chromecompute_login,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': posixpath,
    'path_to_buildbot': CHROMECOMPUTE_BUILDBOT_PATH,
    'remote_access': GCE_COMPILE_C_ONLINE,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skia-vm-016': {
    'slaves': [
      ('skiabot-win-compile-000', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': None,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': ntpath,
    'path_to_buildbot': ['buildbot'],
    'remote_access': False,
    'launch_script': LAUNCH_SCRIPT_WIN,
  },

  'skia-vm-017': {
    'slaves': [
      ('skiabot-win-compile-001', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': None,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': ntpath,
    'path_to_buildbot': ['buildbot'],
    'remote_access': False,
    'launch_script': LAUNCH_SCRIPT_WIN,
  },

  'skia-vm-018': {
    'slaves': [
      ('skiabot-win-compile-002', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': None,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': ntpath,
    'path_to_buildbot': ['buildbot'],
    'remote_access': False,
    'launch_script': LAUNCH_SCRIPT_WIN,
  },

  'skia-vm-019': {
    'slaves': [
      ('skiabot-win-compile-003', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': None,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': ntpath,
    'path_to_buildbot': ['buildbot'],
    'remote_access': False,
    'launch_script': LAUNCH_SCRIPT_WIN,
  },

  'skia-vm-020': {
    'slaves': [
      ('skiabot-linux-tester-000', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': chromecompute_login,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': posixpath,
    'path_to_buildbot': CHROMECOMPUTE_BUILDBOT_PATH,
    'remote_access': GCE_COMPILE_C_ONLINE,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skia-vm-021': {
    'slaves': [
      ('skiabot-linux-tester-001', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': chromecompute_login,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': posixpath,
    'path_to_buildbot': CHROMECOMPUTE_BUILDBOT_PATH,
    'remote_access': GCE_COMPILE_C_ONLINE,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skia-vm-022': {
    'slaves': [
      ('skiabot-linux-tester-002', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': chromecompute_login,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': posixpath,
    'path_to_buildbot': CHROMECOMPUTE_BUILDBOT_PATH,
    'remote_access': GCE_COMPILE_C_ONLINE,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skia-vm-023': {
    'slaves': [
      ('skiabot-linux-tester-003', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': chromecompute_login,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': posixpath,
    'path_to_buildbot': CHROMECOMPUTE_BUILDBOT_PATH,
    'remote_access': GCE_COMPILE_C_ONLINE,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skia-vm-024': {
    'slaves': [
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': chromecompute_login,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': posixpath,
    'path_to_buildbot': CHROMECOMPUTE_BUILDBOT_PATH,
    'remote_access': GCE_COMPILE_C_ONLINE,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skia-vm-025': {
    'slaves': [
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': chromecompute_login,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': posixpath,
    'path_to_buildbot': CHROMECOMPUTE_BUILDBOT_PATH,
    'remote_access': GCE_COMPILE_C_ONLINE,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skia-vm-026': {
    'slaves': [
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': chromecompute_login,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': posixpath,
    'path_to_buildbot': CHROMECOMPUTE_BUILDBOT_PATH,
    'remote_access': GCE_COMPILE_C_ONLINE,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skia-vm-027': {
    'slaves': [
      ('skiabot-linux-xsan-000', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': chromecompute_login,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': posixpath,
    'path_to_buildbot': CHROMECOMPUTE_BUILDBOT_PATH,
    'remote_access': GCE_COMPILE_C_ONLINE,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skia-vm-028': {
    'slaves': [
      ('skiabot-linux-xsan-001', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': chromecompute_login,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': posixpath,
    'path_to_buildbot': CHROMECOMPUTE_BUILDBOT_PATH,
    'remote_access': GCE_COMPILE_C_ONLINE,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skia-vm-029': {
    'slaves': [
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': chromecompute_login,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': posixpath,
    'path_to_buildbot': CHROMECOMPUTE_BUILDBOT_PATH,
    'remote_access': GCE_COMPILE_C_ONLINE,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skia-vm-030': {
    'slaves': [
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': None,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': ntpath,
    'path_to_buildbot': ['buildbot'],
    'remote_access': False,
    'launch_script': LAUNCH_SCRIPT_WIN,
  },

  'skia-vm-031': {
    'slaves': [
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': None,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': ntpath,
    'path_to_buildbot': ['buildbot'],
    'remote_access': False,
    'launch_script': LAUNCH_SCRIPT_WIN,
  },

  'skia-vm-032': {
    'slaves': [
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': None,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': ntpath,
    'path_to_buildbot': ['buildbot'],
    'remote_access': False,
    'launch_script': LAUNCH_SCRIPT_WIN,
  },

  'skia-vm-101': {
    'slaves': [
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': chromecompute_login,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': posixpath,
    'path_to_buildbot': CHROMECOMPUTE_BUILDBOT_PATH,
    'remote_access': GCE_COMPILE_C_ONLINE,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

################################# Mac Machines #################################

  'skiabot-macmini-10_6-001': {
    'slaves': [
      ('skiabot-macmini-10_6-000', '0', False),
      ('skiabot-macmini-10_6-001', '1', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': skia_lab_login,
    'ip': '192.168.1.144',
    'kvm_num': '2',
    'path_module': posixpath,
    'path_to_buildbot': ['buildbot'],
    'remote_access': True,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skiabot-macmini-10_6-002': {
    'slaves': [
      ('skiabot-macmini-10_6-002', '2', False),
      ('skiabot-macmini-10_6-003', '3', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': skia_lab_login,
    'ip': '192.168.1.121',
    'kvm_num': '1',
    'path_module': posixpath,
    'path_to_buildbot': ['buildbot'],
    'remote_access': True,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skiabot-macmini-10_7-001': {
    'slaves': [
      ('skiabot-macmini-10_7-000', '0', False),
      ('skiabot-macmini-10_7-001', '1', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': skia_lab_login,
    'ip': '192.168.1.137',
    'kvm_num': '3',
    'path_module': posixpath,
    'path_to_buildbot': ['buildbot'],
    'remote_access': True,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skiabot-macmini-10_7-002': {
    'slaves': [
      ('skiabot-macmini-10_7-bench', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': skia_lab_login,
    'ip': '192.168.1.124',
    'kvm_num': '4',
    'path_module': posixpath,
    'path_to_buildbot': ['buildbot'],
    'remote_access': True,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skiabot-macmini-10_8-001': {
    'slaves': [
      ('skiabot-macmini-10_8-000', '0', False),
      ('skiabot-macmini-10_8-001', '1', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': skia_lab_login,
    'ip': '192.168.1.125',
    'kvm_num': '8',
    'path_module': posixpath,
    'path_to_buildbot': ['buildbot'],
    'remote_access': True,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skiabot-macmini-10_8-002': {
    'slaves': [
      ('skiabot-macmini-10_8-bench', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': skia_lab_login,
    'ip': '192.168.1.135',
    'kvm_num': '6',
    'path_module': posixpath,
    'path_to_buildbot': ['buildbot'],
    'remote_access': True,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skiabot-mac-10_7-compile': {
    'slaves': [
      ('skiabot-mac-10_7-compile-000', '0', False),
      ('skiabot-mac-10_7-compile-001', '1', False),
      ('skiabot-mac-10_7-compile-002', '2', False),
      ('skiabot-mac-10_7-compile-003', '3', False),
      ('skiabot-mac-10_7-compile-004', '4', False),
      ('skiabot-mac-10_7-compile-005', '5', False),
      ('skiabot-mac-10_7-compile-006', '6', False),
      ('skiabot-mac-10_7-compile-007', '7', False),
      ('skiabot-mac-10_7-compile-008', '8', False),
      ('skiabot-mac-10_7-compile-009', '9', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': skia_lab_login,
    'ip': '192.168.1.118',
    'kvm_num': '5',
    'path_module': posixpath,
    'path_to_buildbot': ['buildbot'],
    'remote_access': True,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'skiabot-mac-10_8-compile': {
    'slaves': [
      ('skiabot-mac-10_8-compile-000', '0', False),
      ('skiabot-mac-10_8-compile-001', '1', False),
      ('skiabot-mac-10_8-compile-002', '2', False),
      ('skiabot-mac-10_8-compile-003', '3', False),
      ('skiabot-mac-10_8-compile-004', '4', False),
      ('skiabot-mac-10_8-compile-005', '5', False),
      ('skiabot-mac-10_8-compile-006', '6', False),
      ('skiabot-mac-10_8-compile-007', '7', False),
      ('skiabot-mac-10_8-compile-008', '8', False),
      ('skiabot-mac-10_8-compile-009', '9', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': skia_lab_login,
    'ip': '192.168.1.104',
    'kvm_num': '7',
    'path_module': posixpath,
    'path_to_buildbot': ['buildbot'],
    'remote_access': True,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

############################### Windows Machines ###############################

  'win7-intel-002': {
    'slaves': [
      ('skiabot-shuttle-win7-intel-bench', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': None,
    'ip': '192.168.1.139',
    'kvm_num': 'F',
    'path_module': ntpath,
    'path_to_buildbot': ['buildbot'],
    'remote_access': False,
    'launch_script': LAUNCH_SCRIPT_WIN,
  },

  'win7-intel-003': {
    'slaves': [
      ('skiabot-shuttle-win7-intel-000', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': None,
    'ip': '192.168.1.114',
    'kvm_num': 'G',
    'path_module': ntpath,
    'path_to_buildbot': ['buildbot'],
    'remote_access': False,
    'launch_script': LAUNCH_SCRIPT_WIN,
  },

  'win8-gtx660-001': {
    'slaves': [
      ('skiabot-shuttle-win8-gtx660-bench', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': None,
    'ip': '192.168.1.133',
    'kvm_num': 'B',
    'path_module': ntpath,
    'path_to_buildbot': ['buildbot'],
    'remote_access': False,
    'launch_script': LAUNCH_SCRIPT_WIN,
  },

  'win8-hd7770-000': {
    'slaves': [
      ('skiabot-shuttle-win8-hd7770-000', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': None,
    'ip': '192.168.1.117',
    'kvm_num': 'C',
    'path_module': ntpath,
    'path_to_buildbot': ['buildbot'],
    'remote_access': False,
    'launch_script': LAUNCH_SCRIPT_WIN,
  },

  'win8-hd7770-001': {
    'slaves': [
      ('skiabot-shuttle-win8-hd7770-bench', '0', False),
    ],
    'copies': CHROMEBUILD_COPIES,
    'login_cmd': None,
    'ip': '192.168.1.107',
    'kvm_num': 'D',
    'path_module': ntpath,
    'path_to_buildbot': ['buildbot'],
    'remote_access': False,
    'launch_script': LAUNCH_SCRIPT_WIN,
  },

############################ Machines in Chrome Golo ###########################

  'build3-a3': {
    'slaves': [
      ('build3-a3', '0', False),
    ],
    'copies': None,
    'login_cmd': None,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': None,
    'path_to_buildbot': None,
    'remote_access': False,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'build4-a3': {
    'slaves': [
      ('build4-a3', '0', False),
    ],
    'copies': None,
    'login_cmd': None,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': None,
    'path_to_buildbot': None,
    'remote_access': False,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  'build5-a3': {
    'slaves': [
      ('build5-a3', '0', False),
    ],
    'copies': None,
    'login_cmd': None,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': posixpath,
    'path_to_buildbot': None,
    'remote_access': False,
    'launch_script': LAUNCH_SCRIPT_UNIX,
  },

  # TODO(borenet): These buildslaves are actually not running, but they still
  # appear in a slaves.cfg file. We list them here to avoid having to remove
  # them from slaves.cfg in case we want to add them back in the future.
  'extra_buildslaves_catchall': {
    'slaves': [
      ('skiabot-macmini-10_7-002', '2', False),
      ('skiabot-macmini-10_7-003', '3', False),
      ('skiabot-macmini-10_8-002', '2', False),
      ('skiabot-macmini-10_8-003', '3', False),
    ],
    'copies': None,
    'login_cmd': None,
    'ip': NO_IP_ADDR,
    'kvm_num': NO_KVM_NUM,
    'path_module': posixpath,
    'path_to_buildbot': None,
    'remote_access': False,
    'launch_script': None,
  },
}


# Class which holds configuration data describing a build slave host.
SlaveHostConfig = collections.namedtuple('SlaveHostConfig',
                                         ('hostname, slaves, copies, login_cmd,'
                                          ' ip, kvm_num, path_module,'
                                          ' path_to_buildbot, remote_access,'
                                          ' launch_script'))


SLAVE_HOSTS = {}
for (_hostname, _config) in _slave_host_dicts.iteritems():
  login_cmd = _config.pop('login_cmd')
  if login_cmd:
    resolved_login_cmd = login_cmd(_hostname, _config)
  else:
    resolved_login_cmd = None
  SLAVE_HOSTS[_hostname] = SlaveHostConfig(hostname=_hostname,
                                           login_cmd=resolved_login_cmd,
                                           **_config)


def default_slave_host_config(hostname):
  """Return a default configuration for the given hostname.

  Assumes that the slave host is the machine on which this function is called.

  Args:
      hostname: string; name of the build slave host.
  Returns:
      SlaveHostConfig instance with configuration for this machine.
  """
  path_to_buildbot = os.path.join(os.path.dirname(__file__), os.pardir)
  path_to_buildbot = os.path.abspath(path_to_buildbot).split(os.path.sep)
  launch_script = LAUNCH_SCRIPT_WIN if os.name == 'nt' else LAUNCH_SCRIPT_UNIX
  return SlaveHostConfig(
    hostname=hostname,
    slaves=[(hostname, '0', True)],
    copies=CHROMEBUILD_COPIES,
    login_cmd=None,
    ip=None,
    kvm_num=None,
    path_module=os.path,
    path_to_buildbot=path_to_buildbot,
    remote_access=False,
    launch_script=launch_script,
  )


def get_slave_host_config(hostname):
  """Helper function for retrieving slave host configuration information.

  If the given hostname is unknown, returns a default config.

  Args:
      hostname: string; the hostname of the slave host machine.
  Returns:
      SlaveHostConfig instance representing the given host.
  """
  return SLAVE_HOSTS.get(hostname, default_slave_host_config(hostname))
