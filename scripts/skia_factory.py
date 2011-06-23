#!/usr/bin/python
# Copyright (c) 2011 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Utility class to build the Skia master BuildFactory's.

Based on gclient_factory.py and adds Skia-specific steps."""

import os

from buildbot.process.properties import WithProperties

from master.factory import gclient_factory

import config
import skia_commands

BENCH_REPEAT_COUNT = 20
BENCH_GRAPH_FIRST_REVISION = 1642
BENCH_GRAPH_X = 1024
BENCH_GRAPH_Y = 768

# TODO(epoger): I can probably get rid of target_platform now.

class SkiaFactory(gclient_factory.GClientFactory):
  """Encapsulates data and methods common to the Skia master.cfg files."""

  def __init__(self, build_subdir, target_platform=None, configuration='Debug',
               default_timeout=600,
               environment_variables=None, gm_image_subdir=None,
               perf_output_dir=None):
    """Instantiates a SkiaFactory as appropriate for this target_platform.

    build_subdir: string indicating path within slave directory
    target_platform: a string such as skia_commands.TARGET_PLATFORM_LINUX
    configuration: 'Debug' or 'Release'
    default_timeout: default timeout for each command, in seconds
    environment_variables: dictionary of environment variables that should
        be passed to all commands
    gm_image_subdir: directory containing images for comparison against results
        of gm tool
    perf_output_dir: path to directory where we store performance data,
        or None if we don't want to store performance data
    """
    # The only thing we use the BaseFactory for is to deal with gclient.
    gclient_solution = gclient_factory.GClientSolution(
        svn_url=config.Master.skia_url + 'trunk', name=build_subdir)
    gclient_factory.GClientFactory.__init__(
        self, build_dir='', solutions=[gclient_solution],
        target_platform=target_platform)
    self._configuration = configuration
    self._factory = self.BaseFactory(factory_properties=None)
    self._gm_image_subdir = gm_image_subdir

    # If we are going to store performance output, prepare its directories.
    if perf_output_dir:
      self._perf_data_dir = os.path.join(perf_output_dir, 'data')
      if not os.path.exists(self._perf_data_dir):
        os.makedirs(self._perf_data_dir)
      self._perf_graphs_dir = os.path.join(perf_output_dir, 'graphs')
      if not os.path.exists(self._perf_graphs_dir):
        os.makedirs(self._perf_graphs_dir)
    else:
      self._perf_data_dir = None
      self._perf_graphs_dir = None

    # Get an implementation of SkiaCommands as appropriate for
    # this target_platform.
    self._skia_cmd_obj = skia_commands.CreateSkiaCommands(
        target_platform=target_platform, factory=self._factory,
        configuration=configuration, build_subdir=build_subdir, target_arch=None,
        default_timeout=default_timeout,
        environment_variables=environment_variables)

  def Build(self, clobber=False):
    """Build and return the complete BuildFactory.

    clobber: boolean indicating whether we should clean before building
    """
    if clobber:
      self._skia_cmd_obj.AddClean()
    self._skia_cmd_obj.AddRun(
        run_command='make core BUILDTYPE=%s' % self._configuration,
        description='BuildCore')
    self._skia_cmd_obj.AddRun(
        run_command='make tests BUILDTYPE=%s' % self._configuration,
        description='BuildTests')
    self._skia_cmd_obj.AddRun(
        run_command='out/%s/tests' % self._configuration,
        description='RunTests')
    self._skia_cmd_obj.AddRun(
        run_command='make gm BUILDTYPE=%s' % self._configuration,
        description='BuildGM')
    self._skia_cmd_obj.AddRun(
        run_command='out/%s/gm -r gm/%s' % (
            self._configuration, self._gm_image_subdir),
        description='RunGM')

    # Build and run "bench", piping the output somewhere so we can graph
    # results over time.
    #
    # TODO(epoger): Currently this is a hack--we just tell the slave to
    # pipe the output to a directory on local disk.  This assumes that all
    # slaves are running on the same system.
    # Eventually, we will want the master to capture the output and store it.
    self._skia_cmd_obj.AddRun(
        run_command='make bench BUILDTYPE=%s' % self._configuration,
        description='BuildBench')
    # Running bench can be quite slow, so run it fewer times if we aren't
    # recording the output.
    if self._perf_data_dir:
      count = BENCH_REPEAT_COUNT
    else:
      count = 2
    base_command = 'out/%s/bench -repeat %d -timers wcg' % (
        self._configuration, count)
    if self._perf_data_dir:
      # The WithProperties() stuff is very touchy and mysterious.
      # With trial and error, I was able to get it to assemble a filename
      # including the revision as follows...
      #
      # TODO(epoger): added ugly chmod to make the data files world-readable
      command = WithProperties(
          '%s | tee %s/bench_r%%(%s:-)s_data ' \
          '&& chmod a+r %s/bench_r%%(%s:-)s_data' % (
              base_command, self._perf_data_dir, 'revision',
              self._perf_data_dir, 'revision'))
    else:
      command = base_command
    self._skia_cmd_obj.AddRun(
        run_command=command, description='RunBench')

    # Generate bench performance graphs (but only if we have been recording
    # bench output for this build type).
    #
    # TODO(epoger): Ben notes that we should probably make the -r and -f values
    # something like current_revision-100 and current_revision-20, respectively.
    if self._perf_data_dir:
      command = 'python %s -d %s -r %d -f %d -x %d -y %d > %s' % (
          'bench/bench_graph_svg.py', self._perf_data_dir,
          BENCH_GRAPH_FIRST_REVISION, BENCH_GRAPH_FIRST_REVISION,
          BENCH_GRAPH_X, BENCH_GRAPH_Y,
          os.path.join(self._perf_graphs_dir, 'graph.xhtml'))
      self._skia_cmd_obj.AddRun(
          run_command=command, description='GenerateBenchGraphs')

    # Build all remaining targets, just to make sure they compile.
    self._skia_cmd_obj.AddRun(
        run_command='make all BUILDTYPE=%s' % self._configuration,
        description='BuildAllOtherTargets')
    return self._factory
