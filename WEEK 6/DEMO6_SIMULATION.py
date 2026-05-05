#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Demo 6 Simulation
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
import os
import sys
import logging as log

def get_state_directory() -> str:
    oldpath = os.path.expanduser("~/.grc_gnuradio")
    try:
        from gnuradio.gr import paths
        newpath = paths.persistent()
        if os.path.exists(newpath):
            return newpath
        if os.path.exists(oldpath):
            log.warning(f"Found persistent state path '{newpath}', but file does not exist. " +
                     f"Old default persistent state path '{oldpath}' exists; using that. " +
                     "Please consider moving state to new location.")
            return oldpath
        # Default to the correct path if both are configured.
        # neither old, nor new path exist: create new path, return that
        os.makedirs(newpath, exist_ok=True)
        return newpath
    except (ImportError, NameError):
        log.warning("Could not retrieve GNU Radio persistent state directory from GNU Radio. " +
                 "Trying defaults.")
        xdgstate = os.getenv("XDG_STATE_HOME", os.path.expanduser("~/.local/state"))
        xdgcand = os.path.join(xdgstate, "gnuradio")
        if os.path.exists(xdgcand):
            return xdgcand
        if os.path.exists(oldpath):
            log.warning(f"Using legacy state path '{oldpath}'. Please consider moving state " +
                     f"files to '{xdgcand}'.")
            return oldpath
        # neither old, nor new path exist: create new path, return that
        os.makedirs(xdgcand, exist_ok=True)
        return xdgcand

sys.path.append(os.environ.get('GRC_HIER_PATH', get_state_directory()))

from PyQt5.QtCore import QObject, pyqtSlot
from gnuradio import analog
from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from power_calc import power_calc  # grc-generated hier_block
import DEMO6_SIMULATION_epy_block_0_0 as epy_block_0_0  # embedded python block
import sip
import threading



class DEMO6_SIMULATION(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Demo 6 Simulation", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Demo 6 Simulation")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "DEMO6_SIMULATION")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 32000
        self.f3_vals = f3_vals = 3,2,4,1,5,0
        self.f2_vals = f2_vals = 5,4,3,2,1,0
        self.f1_vals = f1_vals = [0,1,2,3,4,5]
        self.Sim_Setup = Sim_Setup = 0
        self.F_select = F_select = 0

        ##################################################
        # Blocks
        ##################################################

        # Create the options list
        self._F_select_options = [0, 1, 2, 3, 4, 5]
        # Create the labels list
        self._F_select_labels = ['F0', 'F1', 'F2', 'F3', 'F4', 'F5']
        # Create the combo box
        self._F_select_tool_bar = Qt.QToolBar(self)
        self._F_select_tool_bar.addWidget(Qt.QLabel("Fingerprint Select" + ": "))
        self._F_select_combo_box = Qt.QComboBox()
        self._F_select_tool_bar.addWidget(self._F_select_combo_box)
        for _label in self._F_select_labels: self._F_select_combo_box.addItem(_label)
        self._F_select_callback = lambda i: Qt.QMetaObject.invokeMethod(self._F_select_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._F_select_options.index(i)))
        self._F_select_callback(self.F_select)
        self._F_select_combo_box.currentIndexChanged.connect(
            lambda i: self.set_F_select(self._F_select_options[i]))
        # Create the radio buttons
        self.top_layout.addWidget(self._F_select_tool_bar)
        self.qtgui_number_sink_1_0 = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_VERT,
            1,
            None # parent
        )
        self.qtgui_number_sink_1_0.set_update_time(0.10)
        self.qtgui_number_sink_1_0.set_title("")

        labels = ['', '', '', '', '',
            '', '', '', '', '']
        units = ['', '', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.qtgui_number_sink_1_0.set_min(i, 0)
            self.qtgui_number_sink_1_0.set_max(i, 2)
            self.qtgui_number_sink_1_0.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.qtgui_number_sink_1_0.set_label(i, "Data {0}".format(i))
            else:
                self.qtgui_number_sink_1_0.set_label(i, labels[i])
            self.qtgui_number_sink_1_0.set_unit(i, units[i])
            self.qtgui_number_sink_1_0.set_factor(i, factor[i])

        self.qtgui_number_sink_1_0.enable_autoscale(False)
        self._qtgui_number_sink_1_0_win = sip.wrapinstance(self.qtgui_number_sink_1_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_number_sink_1_0_win, 0, 0, 2, 1)
        for r in range(0, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_number_sink_0_0 = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_HORIZ,
            3,
            None # parent
        )
        self.qtgui_number_sink_0_0.set_update_time(0.10)
        self.qtgui_number_sink_0_0.set_title("Input Values")

        labels = ['', '', '', '', '',
            '', '', '', '', '']
        units = ['', '', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(3):
            self.qtgui_number_sink_0_0.set_min(i, -1)
            self.qtgui_number_sink_0_0.set_max(i, 6)
            self.qtgui_number_sink_0_0.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.qtgui_number_sink_0_0.set_label(i, "Data {0}".format(i))
            else:
                self.qtgui_number_sink_0_0.set_label(i, labels[i])
            self.qtgui_number_sink_0_0.set_unit(i, units[i])
            self.qtgui_number_sink_0_0.set_factor(i, factor[i])

        self.qtgui_number_sink_0_0.enable_autoscale(False)
        self._qtgui_number_sink_0_0_win = sip.wrapinstance(self.qtgui_number_sink_0_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_number_sink_0_0_win, 0, 1, 2, 3)
        for r in range(0, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.power_calc_1_0_1 = power_calc(
            ma_len=1000,
            samp_rate=1000000,
        )
        self.power_calc_1_0_0 = power_calc(
            ma_len=1000,
            samp_rate=1000000,
        )
        self.power_calc_1_0 = power_calc(
            ma_len=1000,
            samp_rate=1000000,
        )
        self.epy_block_0_0 = epy_block_0_0.blk()
        self.blocks_throttle2_0_0 = blocks.throttle( gr.sizeof_float*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_add_xx_0 = blocks.add_vcc(1)
        self.band_pass_filter_2 = filter.fir_filter_ccf(
            1,
            firdes.band_pass(
                1,
                samp_rate,
                1,
                2000,
                1,
                window.WIN_HAMMING,
                6.76))
        self.band_pass_filter_1 = filter.fir_filter_ccf(
            1,
            firdes.band_pass(
                1,
                samp_rate,
                2000,
                4000,
                1,
                window.WIN_HAMMING,
                6.76))
        self.band_pass_filter_0 = filter.fir_filter_ccf(
            1,
            firdes.band_pass(
                1,
                samp_rate,
                4000,
                6000,
                1,
                window.WIN_HAMMING,
                6.76))
        self.analog_sig_source_x_2_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, 3000, f2_vals[F_select], 0, 0)
        self.analog_sig_source_x_1_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, 5000, f1_vals[F_select], 0, 0)
        self.analog_sig_source_x_0_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, 1000, f3_vals[F_select], 0, 0)
        # Create the options list
        self._Sim_Setup_options = [0, 1]
        # Create the labels list
        self._Sim_Setup_labels = ['Simulation', 'Real']
        # Create the combo box
        self._Sim_Setup_tool_bar = Qt.QToolBar(self)
        self._Sim_Setup_tool_bar.addWidget(Qt.QLabel("Simulation Setup" + ": "))
        self._Sim_Setup_combo_box = Qt.QComboBox()
        self._Sim_Setup_tool_bar.addWidget(self._Sim_Setup_combo_box)
        for _label in self._Sim_Setup_labels: self._Sim_Setup_combo_box.addItem(_label)
        self._Sim_Setup_callback = lambda i: Qt.QMetaObject.invokeMethod(self._Sim_Setup_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._Sim_Setup_options.index(i)))
        self._Sim_Setup_callback(self.Sim_Setup)
        self._Sim_Setup_combo_box.currentIndexChanged.connect(
            lambda i: self.set_Sim_Setup(self._Sim_Setup_options[i]))
        # Create the radio buttons
        self.top_layout.addWidget(self._Sim_Setup_tool_bar)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_0_0, 0), (self.blocks_add_xx_0, 2))
        self.connect((self.analog_sig_source_x_1_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.analog_sig_source_x_2_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.band_pass_filter_0, 0), (self.power_calc_1_0, 0))
        self.connect((self.band_pass_filter_1, 0), (self.power_calc_1_0_0, 0))
        self.connect((self.band_pass_filter_2, 0), (self.power_calc_1_0_1, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.band_pass_filter_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.band_pass_filter_1, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.band_pass_filter_2, 0))
        self.connect((self.blocks_throttle2_0_0, 0), (self.qtgui_number_sink_1_0, 0))
        self.connect((self.epy_block_0_0, 0), (self.blocks_throttle2_0_0, 0))
        self.connect((self.power_calc_1_0, 0), (self.epy_block_0_0, 0))
        self.connect((self.power_calc_1_0, 0), (self.qtgui_number_sink_0_0, 0))
        self.connect((self.power_calc_1_0_0, 0), (self.epy_block_0_0, 1))
        self.connect((self.power_calc_1_0_0, 0), (self.qtgui_number_sink_0_0, 1))
        self.connect((self.power_calc_1_0_1, 0), (self.epy_block_0_0, 2))
        self.connect((self.power_calc_1_0_1, 0), (self.qtgui_number_sink_0_0, 2))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "DEMO6_SIMULATION")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_0_0.set_sampling_freq(self.samp_rate)
        self.analog_sig_source_x_1_0.set_sampling_freq(self.samp_rate)
        self.analog_sig_source_x_2_0.set_sampling_freq(self.samp_rate)
        self.band_pass_filter_0.set_taps(firdes.band_pass(1, self.samp_rate, 4000, 6000, 1, window.WIN_HAMMING, 6.76))
        self.band_pass_filter_1.set_taps(firdes.band_pass(1, self.samp_rate, 2000, 4000, 1, window.WIN_HAMMING, 6.76))
        self.band_pass_filter_2.set_taps(firdes.band_pass(1, self.samp_rate, 1, 2000, 1, window.WIN_HAMMING, 6.76))
        self.blocks_throttle2_0_0.set_sample_rate(self.samp_rate)

    def get_f3_vals(self):
        return self.f3_vals

    def set_f3_vals(self, f3_vals):
        self.f3_vals = f3_vals
        self.analog_sig_source_x_0_0.set_amplitude(self.f3_vals[self.F_select])

    def get_f2_vals(self):
        return self.f2_vals

    def set_f2_vals(self, f2_vals):
        self.f2_vals = f2_vals
        self.analog_sig_source_x_2_0.set_amplitude(self.f2_vals[self.F_select])

    def get_f1_vals(self):
        return self.f1_vals

    def set_f1_vals(self, f1_vals):
        self.f1_vals = f1_vals
        self.analog_sig_source_x_1_0.set_amplitude(self.f1_vals[self.F_select])

    def get_Sim_Setup(self):
        return self.Sim_Setup

    def set_Sim_Setup(self, Sim_Setup):
        self.Sim_Setup = Sim_Setup
        self._Sim_Setup_callback(self.Sim_Setup)

    def get_F_select(self):
        return self.F_select

    def set_F_select(self, F_select):
        self.F_select = F_select
        self._F_select_callback(self.F_select)
        self.analog_sig_source_x_0_0.set_amplitude(self.f3_vals[self.F_select])
        self.analog_sig_source_x_1_0.set_amplitude(self.f1_vals[self.F_select])
        self.analog_sig_source_x_2_0.set_amplitude(self.f2_vals[self.F_select])




def main(top_block_cls=DEMO6_SIMULATION, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()
    tb.flowgraph_started.set()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
