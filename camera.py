# -*- coding: utf-8 -*-
#!/usr/bin/env python3
'''
    Project Edenbridge
    Copyright (C) 2019  Zhengyu Peng

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

from threading import Thread
import time
import picamera
import datetime
import queue
import logging


class Camera(Thread):
    def __init__(self, config, motion2camera, camera2bot):
        Thread.__init__(self)
        self.motion2camera = motion2camera
        self.camera2bot = camera2bot

        self.camera = picamera.PiCamera(resolution=(1280, 720))
        self.camera.start_preview()
        self.max_frames = 10
        time.sleep(2)

    def capture_jpg(self, frames, period):
        datetime_str = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        if frames > 0:
            for frame_idx in frames:
                name_str = './photos/' + str(
                    frame_idx) + '_' + datetime_str + '.jpg'
                self.camera.capture(name_str)
                self.camera2bot.put(name_str)
                time.sleep(period)
        else:
            frame_idx = 0
            while True:
                name_str = './photos/' + str(
                    frame_idx) + '_' + datetime_str + '.jpg'
                self.camera.capture(name_str)
                logging.info('Capture ' + name_str)

                self.camera2bot.put(name_str)
                try:
                    motion_command = self.motion2camera.get(
                        block=True, timeout=period)
                except queue.Empty:
                    # Handle empty queue here
                    pass
                else:
                    if motion_command is 'stop_capture_jpg':
                        self.motion2camera.task_done()
                        logging.info('Stop capturing')
                        break
                    else:
                        self.motion2camera.task_done()
                        logging.warning('Wrong command, continue capturing')

                frame_idx += frame_idx

                if frame_idx >= self.max_frames:
                    logging.warning('Reach to maximum frame')
                    break

    def run(self):
        logging.info('Camera thread started')
        while True:
            # retrieve data (blocking)
            motion_command = self.motion2camera.get()
            if motion_command is 'capture_jpg':
                self.motion2camera.task_done()
                self.capture_jpg(0, 30)
                logging.info('Start to capture photos')

            else:
                self.motion2camera.task_done()


'''

    `                      `
    -:.                  -#:
    -//:.              -###:
    -////:.          -#####:
    -/:.://:.      -###++##:
    ..   `://:-  -###+. :##:
           `:/+####+.   :##:
    .::::::::/+###.     :##:
    .////-----+##:    `:###:
     `-//:.   :##:  `:###/.
       `-//:. :##:`:###/.
         `-//:+######/.
           `-/+####/.
             `+##+.
              :##:
              :##:
              :##:
              :##:
              :##:
               .+:

'''