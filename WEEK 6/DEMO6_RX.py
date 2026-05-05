#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Demo 6 RX
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

from PyQt5 import QtCore
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
from gnuradio import zeromq
from power_calc import power_calc  # grc-generated hier_block
from xmlrpc.server import SimpleXMLRPCServer
import threading
import DEMO6_RX_epy_block_0_0 as epy_block_0_0  # embedded python block
import sip



class DEMO6_RX(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Demo 6 RX", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Demo 6 RX")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "DEMO6_RX")

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
        self.zmq_add = zmq_add = "tcp://127.0.0.1:55555"
        self.xmlrpc_add = xmlrpc_add = "localhost"
        self.tx_Y1 = tx_Y1 = -2
        self.tx_Y0 = tx_Y0 = 2
        self.tx_X1 = tx_X1 = 2
        self.tx_X0 = tx_X0 = -2
        self.samp_rate = samp_rate = 32000
        self.rx_fq = rx_fq = 915000000
        self.rx_Y = rx_Y = 0
        self.rx_X = rx_X = 0
        self.filt_w = filt_w = 2000
        self.f2_vals = f2_vals = 5,4,3,2,1,0
        self.f1_vals = f1_vals = [0,1,2,3,4,5]
        self.Sim_Setup = Sim_Setup = 0
        self.F_select = F_select = 0

        ##################################################
        # Blocks
        ##################################################

        self._rx_Y_range = qtgui.Range(-1.8, 1.8, 0.2, 0, 200)
        self._rx_Y_win = qtgui.RangeWidget(self._rx_Y_range, self.set_rx_Y, "receiver position y", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._rx_Y_win)
        self._rx_X_range = qtgui.Range(-1.8, 1.8, 0.2, 0, 200)
        self._rx_X_win = qtgui.RangeWidget(self._rx_X_range, self.set_rx_X, "receiver position x", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._rx_X_win)
        self._filt_w_range = qtgui.Range(2000, 1000000, 2000, 2000, 200)
        self._filt_w_win = qtgui.RangeWidget(self._filt_w_range, self.set_filt_w, "Filter Width", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._filt_w_win)
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
        self.zeromq_pub_sink_0 = zeromq.pub_sink(gr.sizeof_float, 1, zmq_add, 100, False, (-1), '', True, True)
        self.xmlrpc_server_0 = SimpleXMLRPCServer((xmlrpc_add, 8080), allow_none=True)
        self.xmlrpc_server_0.register_instance(self)
        self.xmlrpc_server_0_thread = threading.Thread(target=self.xmlrpc_server_0.serve_forever)
        self.xmlrpc_server_0_thread.daemon = True
        self.xmlrpc_server_0_thread.start()
        self._rx_fq_range = qtgui.Range(800000000, 1000000000, 5000000, 915000000, 200)
        self._rx_fq_win = qtgui.RangeWidget(self._rx_fq_range, self.set_rx_fq, "Receiver center freq", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._rx_fq_win)
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
            2,
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

        for i in range(2):
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
        self.qtgui_const_sink_x_0 = qtgui.const_sink_c(
            1024, #size
            "", #name
            3, #number of inputs
            None # parent
        )
        self.qtgui_const_sink_x_0.set_update_time(0.10)
        self.qtgui_const_sink_x_0.set_y_axis((-2), 2)
        self.qtgui_const_sink_x_0.set_x_axis((-2), 2)
        self.qtgui_const_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, "")
        self.qtgui_const_sink_x_0.enable_autoscale(False)
        self.qtgui_const_sink_x_0.enable_grid(False)
        self.qtgui_const_sink_x_0.enable_axis_labels(True)


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        styles = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        markers = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(3):
            if len(labels[i]) == 0:
                self.qtgui_const_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_const_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_const_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_const_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_const_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_const_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_const_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_const_sink_x_0_win = sip.wrapinstance(self.qtgui_const_sink_x_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_const_sink_x_0_win, 3, 0, 1, 1)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.power_calc_1_0_0 = power_calc(
            ma_len=500,
            samp_rate=1000000,
        )
        self.power_calc_1_0 = power_calc(
            ma_len=500,
            samp_rate=1000000,
        )
        self.epy_block_0_0 = epy_block_0_0.blk()
        self.blocks_throttle2_0_0_0_0_1 = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_throttle2_0_0_0_0_0 = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_throttle2_0_0_0_0 = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_throttle2_0_0_0 = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_selector_0_4 = blocks.selector(gr.sizeof_gr_complex*1,Sim_Setup,0)
        self.blocks_selector_0_4.set_enabled(True)
        self.blocks_selector_0_2 = blocks.selector(gr.sizeof_gr_complex*1,Sim_Setup,0)
        self.blocks_selector_0_2.set_enabled(True)
        self.blocks_multiply_const_vxx_1 = blocks.multiply_const_cc(1/((rx_X - tx_X1)**2   +   (rx_Y - tx_Y1)**2)**0.5)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(1/((rx_X - tx_X0)**2   +   (rx_Y - tx_Y0)**2)**0.5)
        self.blocks_keep_one_in_n_0_0_1 = blocks.keep_one_in_n(gr.sizeof_float*1, 3200)
        self.blocks_keep_one_in_n_0_0_0 = blocks.keep_one_in_n(gr.sizeof_float*1, 3200)
        self.blocks_keep_one_in_n_0_0 = blocks.keep_one_in_n(gr.sizeof_float*1, 3200)
        self.blocks_keep_one_in_n_0 = blocks.keep_one_in_n(gr.sizeof_float*1, 3200)
        self.blocks_float_to_complex_2 = blocks.float_to_complex(1)
        self.blocks_float_to_complex_1 = blocks.float_to_complex(1)
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.blocks_add_xx_0 = blocks.add_vcc(1)
        self.band_pass_filter_1 = filter.fir_filter_ccf(
            1,
            firdes.band_pass(
                1,
                samp_rate,
                1,
                filt_w,
                1,
                window.WIN_HAMMING,
                6.76))
        self.band_pass_filter_0 = filter.fir_filter_ccf(
            1,
            firdes.band_pass(
                1,
                samp_rate,
                filt_w,
                (filt_w * 2),
                1,
                window.WIN_HAMMING,
                6.76))
        self.analog_sig_source_x_2_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, 1000, 1, 0, 0)
        self.analog_sig_source_x_1_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, 3000, 1, 0, 0)
        self.analog_noise_source_x_0 = analog.noise_source_c(analog.GR_GAUSSIAN, 1, 0)
        self.analog_const_source_x_5_4 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, rx_Y)
        self.analog_const_source_x_5_3 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, rx_X)
        self.analog_const_source_x_5_2 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, 2)
        self.analog_const_source_x_5_1 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, 2)
        self.analog_const_source_x_5_0 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, (-2))
        self.analog_const_source_x_5 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, (-2))
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


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_const_source_x_5, 0), (self.blocks_float_to_complex_0, 1))
        self.connect((self.analog_const_source_x_5_0, 0), (self.blocks_float_to_complex_1, 0))
        self.connect((self.analog_const_source_x_5_1, 0), (self.blocks_float_to_complex_1, 1))
        self.connect((self.analog_const_source_x_5_2, 0), (self.blocks_float_to_complex_0, 0))
        self.connect((self.analog_const_source_x_5_3, 0), (self.blocks_float_to_complex_2, 0))
        self.connect((self.analog_const_source_x_5_4, 0), (self.blocks_float_to_complex_2, 1))
        self.connect((self.analog_noise_source_x_0, 0), (self.blocks_add_xx_0, 2))
        self.connect((self.analog_noise_source_x_0, 0), (self.blocks_selector_0_2, 1))
        self.connect((self.analog_noise_source_x_0, 0), (self.blocks_selector_0_4, 1))
        self.connect((self.analog_sig_source_x_1_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.analog_sig_source_x_2_0, 0), (self.blocks_multiply_const_vxx_1, 0))
        self.connect((self.band_pass_filter_0, 0), (self.power_calc_1_0, 0))
        self.connect((self.band_pass_filter_1, 0), (self.power_calc_1_0_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.blocks_throttle2_0_0_0, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.blocks_throttle2_0_0_0_0_0, 0))
        self.connect((self.blocks_float_to_complex_1, 0), (self.blocks_throttle2_0_0_0_0, 0))
        self.connect((self.blocks_float_to_complex_2, 0), (self.blocks_throttle2_0_0_0_0_1, 0))
        self.connect((self.blocks_keep_one_in_n_0, 0), (self.epy_block_0_0, 0))
        self.connect((self.blocks_keep_one_in_n_0_0, 0), (self.qtgui_number_sink_0_0, 0))
        self.connect((self.blocks_keep_one_in_n_0_0_0, 0), (self.epy_block_0_0, 1))
        self.connect((self.blocks_keep_one_in_n_0_0_1, 0), (self.qtgui_number_sink_0_0, 1))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_1, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.blocks_selector_0_2, 0), (self.band_pass_filter_0, 0))
        self.connect((self.blocks_selector_0_4, 0), (self.band_pass_filter_1, 0))
        self.connect((self.blocks_throttle2_0_0_0, 0), (self.blocks_selector_0_2, 0))
        self.connect((self.blocks_throttle2_0_0_0, 0), (self.blocks_selector_0_4, 0))
        self.connect((self.blocks_throttle2_0_0_0_0, 0), (self.qtgui_const_sink_x_0, 0))
        self.connect((self.blocks_throttle2_0_0_0_0_0, 0), (self.qtgui_const_sink_x_0, 1))
        self.connect((self.blocks_throttle2_0_0_0_0_1, 0), (self.qtgui_const_sink_x_0, 2))
        self.connect((self.epy_block_0_0, 0), (self.qtgui_number_sink_1_0, 0))
        self.connect((self.epy_block_0_0, 0), (self.zeromq_pub_sink_0, 0))
        self.connect((self.power_calc_1_0, 0), (self.blocks_keep_one_in_n_0, 0))
        self.connect((self.power_calc_1_0, 0), (self.blocks_keep_one_in_n_0_0, 0))
        self.connect((self.power_calc_1_0_0, 0), (self.blocks_keep_one_in_n_0_0_0, 0))
        self.connect((self.power_calc_1_0_0, 0), (self.blocks_keep_one_in_n_0_0_1, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "DEMO6_RX")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_zmq_add(self):
        return self.zmq_add

    def set_zmq_add(self, zmq_add):
        self.zmq_add = zmq_add

    def get_xmlrpc_add(self):
        return self.xmlrpc_add

    def set_xmlrpc_add(self, xmlrpc_add):
        self.xmlrpc_add = xmlrpc_add

    def get_tx_Y1(self):
        return self.tx_Y1

    def set_tx_Y1(self, tx_Y1):
        self.tx_Y1 = tx_Y1
        self.blocks_multiply_const_vxx_1.set_k(1/((self.rx_X - self.tx_X1)**2   +   (self.rx_Y - self.tx_Y1)**2)**0.5)

    def get_tx_Y0(self):
        return self.tx_Y0

    def set_tx_Y0(self, tx_Y0):
        self.tx_Y0 = tx_Y0
        self.blocks_multiply_const_vxx_0.set_k(1/((self.rx_X - self.tx_X0)**2   +   (self.rx_Y - self.tx_Y0)**2)**0.5)

    def get_tx_X1(self):
        return self.tx_X1

    def set_tx_X1(self, tx_X1):
        self.tx_X1 = tx_X1
        self.blocks_multiply_const_vxx_1.set_k(1/((self.rx_X - self.tx_X1)**2   +   (self.rx_Y - self.tx_Y1)**2)**0.5)

    def get_tx_X0(self):
        return self.tx_X0

    def set_tx_X0(self, tx_X0):
        self.tx_X0 = tx_X0
        self.blocks_multiply_const_vxx_0.set_k(1/((self.rx_X - self.tx_X0)**2   +   (self.rx_Y - self.tx_Y0)**2)**0.5)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_1_0.set_sampling_freq(self.samp_rate)
        self.analog_sig_source_x_2_0.set_sampling_freq(self.samp_rate)
        self.band_pass_filter_0.set_taps(firdes.band_pass(1, self.samp_rate, self.filt_w, (self.filt_w * 2), 1, window.WIN_HAMMING, 6.76))
        self.band_pass_filter_1.set_taps(firdes.band_pass(1, self.samp_rate, 1, self.filt_w, 1, window.WIN_HAMMING, 6.76))
        self.blocks_throttle2_0_0_0.set_sample_rate(self.samp_rate)
        self.blocks_throttle2_0_0_0_0.set_sample_rate(self.samp_rate)
        self.blocks_throttle2_0_0_0_0_0.set_sample_rate(self.samp_rate)
        self.blocks_throttle2_0_0_0_0_1.set_sample_rate(self.samp_rate)

    def get_rx_fq(self):
        return self.rx_fq

    def set_rx_fq(self, rx_fq):
        self.rx_fq = rx_fq

    def get_rx_Y(self):
        return self.rx_Y

    def set_rx_Y(self, rx_Y):
        self.rx_Y = rx_Y
        self.analog_const_source_x_5_4.set_offset(self.rx_Y)
        self.blocks_multiply_const_vxx_0.set_k(1/((self.rx_X - self.tx_X0)**2   +   (self.rx_Y - self.tx_Y0)**2)**0.5)
        self.blocks_multiply_const_vxx_1.set_k(1/((self.rx_X - self.tx_X1)**2   +   (self.rx_Y - self.tx_Y1)**2)**0.5)

    def get_rx_X(self):
        return self.rx_X

    def set_rx_X(self, rx_X):
        self.rx_X = rx_X
        self.analog_const_source_x_5_3.set_offset(self.rx_X)
        self.blocks_multiply_const_vxx_0.set_k(1/((self.rx_X - self.tx_X0)**2   +   (self.rx_Y - self.tx_Y0)**2)**0.5)
        self.blocks_multiply_const_vxx_1.set_k(1/((self.rx_X - self.tx_X1)**2   +   (self.rx_Y - self.tx_Y1)**2)**0.5)

    def get_filt_w(self):
        return self.filt_w

    def set_filt_w(self, filt_w):
        self.filt_w = filt_w
        self.band_pass_filter_0.set_taps(firdes.band_pass(1, self.samp_rate, self.filt_w, (self.filt_w * 2), 1, window.WIN_HAMMING, 6.76))
        self.band_pass_filter_1.set_taps(firdes.band_pass(1, self.samp_rate, 1, self.filt_w, 1, window.WIN_HAMMING, 6.76))

    def get_f2_vals(self):
        return self.f2_vals

    def set_f2_vals(self, f2_vals):
        self.f2_vals = f2_vals

    def get_f1_vals(self):
        return self.f1_vals

    def set_f1_vals(self, f1_vals):
        self.f1_vals = f1_vals

    def get_Sim_Setup(self):
        return self.Sim_Setup

    def set_Sim_Setup(self, Sim_Setup):
        self.Sim_Setup = Sim_Setup
        self._Sim_Setup_callback(self.Sim_Setup)
        self.blocks_selector_0_2.set_input_index(self.Sim_Setup)
        self.blocks_selector_0_4.set_input_index(self.Sim_Setup)

    def get_F_select(self):
        return self.F_select

    def set_F_select(self, F_select):
        self.F_select = F_select
        self._F_select_callback(self.F_select)




def main(top_block_cls=DEMO6_RX, options=None):

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
