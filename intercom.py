#!/usr/bin/env python

import linphone
import logging
import signal
import time
import os

import cv2
import threading
import gpio_dev
import util

class Intercom:
    def __init__(self):
        self.quit = False
        self.make_call = False

        callbacks = linphone.Factory.get().create_core_cbs()
        callbacks.call_state_changed = self.call_state_changed
        callbacks.dtmf_received = self.dtmf_received

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        self.logfile = logging.FileHandler(os.environ['LOG_PATH'])
        logger.addHandler(self.logfile)

        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGUSR1, self.signal_handler)

        linphone.set_log_handler(self.log_handler)

        self.core = linphone.Factory.get().create_core(callbacks, None, None)
        self.core.video_capture_enabled = True
        self.core.video_display_enabled = False
        self.core.video_device = os.environ['VIDEO_DEVICE']
        self.core.capture_device = os.environ['SOUND_DEVICE']
        self.core.ringback = '{}/call.wav'.format(os.environ['SOUNDS_PATH'])

        self.configure_account()

    def configure_account(self):
        proxy_cfg = self.core.create_proxy_config()
        proxy_cfg.identity_address = self.core.create_address(('sip:{}@{}').format(os.environ['USERNAME'], os.environ['HOST']))
        proxy_cfg.server_addr = 'sip:{};transport=udp'.format(os.environ['HOST'])
        proxy_cfg.register_enabled = True
        proxy_cfg.avpf_mode = 1
        proxy_cfg.publish_enabled = True
        self.core.add_proxy_config(proxy_cfg)
        self.core.default_proxy_config = proxy_cfg

        auth_info = self.core.create_auth_info(os.environ['USERNAME'], None, os.environ['PASSWORD'], None, None, os.environ['HOST'])
        self.core.add_auth_info(auth_info)

    def dtmf_received(self, core, call, digits):
        self.open_door()

    def call_state_changed(self, core, call, state, message):
        if state == linphone.CallState.IncomingReceived:
            params = core.create_call_params(call)
            core.accept_call_with_params(call, params)

    def call(self):
        print("Calling")
        self.make_call = False
        if self.core.current_call:
            print("already in call")
            return

        self.camera_snapshot()

        params = self.core.create_call_params(None)
        params.audio_enabled = True
        params.video_enabled = True
        params.audio_multicast_enabled = False
        params.video_multicast_enabled = False
        # params.early_media_sending_enabled = True
        address = linphone.Address.new(os.environ['PANEL_ADDRESS'])

        self.core.invite_address_with_params(address, params)

    def play(self, type, is_sip=False):
        if is_sip:
            self.core.play_local('{}/{}.wav'.format(os.environ['SOUNDS_PATH'], type))
        else:
            os.system('aplay {}/{}.wav'.format(os.environ['SOUNDS_PATH'], type))

    def open_door(self):
        self.play('open_door')
        gpio_dev.pulse_relay(gpio_dev.DOOR_PIN)

    def signal_handler(self, sig, frame):

        if sig == signal.SIGINT:
            self.core.terminate_all_calls()
            self.quit = True

        elif sig == signal.SIGUSR1:
            self.make_call = True

    def log_handler(self, level, msg):
        method = getattr(logging, level)
        method(msg)

    def camera_snapshot(self):
        video = cv2.VideoCapture(int(os.environ['SNAPSHOT_DEVICE']))
        (grabbed, frame) = video.read()
        if not grabbed:
            print("Failed to get snapshot")

        ret, jpeg = cv2.imencode('.jpg', frame)
        f = open(os.environ['SNAPSHOT_PATH'] + '/call_{}.jpg'.format(int(time.time())), 'wb')
        f.write(jpeg.tobytes())
        f.close()
        video.release()

    def run(self):

        while not self.quit:
            if (not gpio_dev.read(gpio_dev.CALL_BUTTON_PIN)):
                self.make_call = True

            if self.make_call == True:
                self.call()

            self.core.iterate()
            time.sleep(0.03)

if __name__ == '__main__':
    intercom = Intercom()
    try:
        intercom.run()
    finally:
        gpio_dev.cleanup()
