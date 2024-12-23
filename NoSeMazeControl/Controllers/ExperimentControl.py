"""
This module contains thread controller and thread. 

As this module was developed rapidly per changing demand, some actually 
unused code might still be saved as comments and there may be some codes that is 
actually obsolete, but still not removed, as it might be used later on, if 
demand changed.
"""
"""
Copyright (c) 2019, 2022 [copyright holders here]

This file is part of NoSeMaze.

NoSeMaze is free software: you can redistribute it and/or 
modify it under the terms of GNU General Public License as 
published by the Free Software Foundation, either version 3 
of the License, or (at your option) at any later version.

NoSeMaze is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty 
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public 
License along with NoSeMaze. If not, see https://www.gnu.org/licenses.
"""

# import PyQt modules
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QReadWriteLock

# import standard modules
from time import sleep, time
import datetime
import os
import csv
import numpy as np

# import custom modules
from PyPulse import PulseInterface, PulseGeneration
from TrialLogic import TrialConditions
import daqface.DAQ as daq
import HelperFunctions.RFID as rfid
import HelperFunctions.Reward as reward
import HelperFunctions.BeamCheck as beam
import HelperFunctions.Email as email

# import for type hinting
from Models.Experiment import Mouse

# TODO: Type hinting MainApp as parent of ExperimentController.

class ExperimentController:
    """
    Thread controller. Controls if thread should be started or stopped.

    Attributes
    ----------
    parent : MainApp
        Parent of ExperimentController.
    
    thread : QtCore.QThread
        Thread of the experiment controller where worker should work.
    
    trial_job : ExperimentWorker
        Instance of ExperimentWorker that will be moved to thread.
    
    should_run : bool
        True if experiment should run; else false.
    
    start_timestamp : datetime
        Timestamp when experiment is started.
    
    count : float
        Time from epoch in seconds as the experiment is started. Obsolete.
    """
    def __init__(self, parent):
        """
        Parameters
        ----------
        parent : obj
            Parent of this class. It should be MainApp
        """

        self.parent = parent

        # initialise thread
        self.thread : QtCore.QThread = QtCore.QThread()

        # initialise job then move it to thread
        self.trial_job : ExperimentWorker = ExperimentWorker(self)
        self.trial_job.moveToThread(self.thread)

        # connecting signals and slots
        self.thread.finished.connect(self.thread.quit)
        self.thread.started.connect(self.trial_job.trial)

        # attributes
        self.should_run : bool = False

    def update_pref(self, new_pref: dict[str, object]):
        """Slot for updating hardware preferences while the experiment is 
        running
        
        Parameters
        ----------
        new_pref : dict
            The new hardware preferences should be used.
        """

        self.trial_job.hardware_prefs = new_pref

    def start(self):
        """Slot for starting the experiment."""

        # checking if any animal does not have a schedule
        check = []

        for animal in self.parent.experiment.animal_list:
            if len(self.parent.experiment.animal_list[animal].schedule_list) > 0:
                check.append(1)
            else:
                check.append(0)

        check = np.nonzero(np.array(check))[0]

        if len(self.parent.experiment.animal_list) > len(check):
            QtWidgets.QMessageBox.about(self.parent,
                                        "Error",
                                        "An animal does not have a schedule! " +
                                        "Please update the Animal List")
        elif self.parent.experiment.save_path is not None:
            # Only start experiment if experiment is not started.
            if not self.should_run:
                self.should_run = True
                self.start_timestamp : datetime.datetime = datetime.datetime.now()
                self.count : float = time()
                self.thread.start()
                print('thread started')
        else:
            QtWidgets.QMessageBox.about(self.parent,
                                        "Error",
                                        "Experiment not saved! " +
                                        "Please save before starting")

    def stop(self):
        """Slot for stopping experiment"""

        # Only stop if experiment was started.
        if self.should_run:
            self.should_run = False
            self.thread.terminate()
            self.thread.wait()
            print('thread ended')


class ExperimentWorker(QtCore.QObject):
    """Worker of experiment thread. Sequence of thread is in trial method.
    
    Attributes
    ----------
    parent : QtCore.QObject
        Parent of worker instance.
    
    lock_llog : ReadWriteLock
        Read-Write-Lock for log files.

    hardware_prefs : dict[str, Any]
        Hardware preferences. Configured in hardware preference window.
    
    experiment : Experiment
        Experiment instance of this experiment session.
    
    save_timestamp : datetime
        Timestamp when experiment is last saved.
    
    morning_notification_sent : bool
        True if morning notification has been sent; else false.
    
    afternoon_notification_sent : bool
        True if afternoon notification has been sent; else false.
    
    notification_sent : bool
        True if notification has been sent; else false.
    """

    # define custom signals to be connected
    finished = QtCore.pyqtSignal()
    """pyqtSignal : Signal sent if an experiment is finished."""
    
    trial_end = QtCore.pyqtSignal()
    """pyqtSignal : Signal sent if a trial has ended."""

    def __init__(self, parent: ExperimentController = None):
        """
        Parameters
        ----------
        parent : QObject, default=None
            Parent of worker. None if not specified.
        """

        # initilise QObject with no parent
        super(self.__class__, self).__init__(None)

        # set parent of worker
        self.parent : ExperimentController = parent

        # set lock
        self.lock_llog : QReadWriteLock = QReadWriteLock()

        # attributes
        self.hardware_prefs = self.parent.parent.hardware_prefs
        self.experiment = self.parent.parent.experiment
        self.save_timestamp = datetime.datetime.now()
        self.morning_notification_sent = False
        self.afternoon_notification_sent = False
        self.evening_notification_sent = False
        self.notification_sent = False

    def trial(self):
        """Sequence of trial. Contains pre-trial sequences, trial sequences in 
        daq instance, and post-trial sequences."""

        # Intialise start timestamp.
        self.start_timestamp = [self.parent.start_timestamp,
                                self.parent.start_timestamp]
        self.today = datetime.date.today()

        while self.parent.should_run:
            start = time()

            if self.animal_present():
                print("Animal present - Beam broken")
                
                animal : Mouse = self.get_present_animal()
                current_trial = animal.current_trial()
                current_trial_pulse = animal.current_trial_pulse()

                # current_trial_pulse is a set of parameters to be given to
                # PulseInterface or PulseGenerator. These parameters are
                # defined in Schedule.

                # Check if schedule is defined as concetenate wait training.
                if 'concatenate_odour_training' not in current_trial_pulse[0]:
                    concatenate = False
                else:
                    concatenate = current_trial_pulse[0]['concatenate_odour_training']

                # As a different NI-Board from the autonomouse version by Andrew Erskine
                # is used, all actual sequences falls under 'static' option.
                # This option can be changed in hardware preference window.
                #
                # WARNING: sequences not under the 'static' option was not
                # in development and may not function properly. Hence, keep
                # the 'static' option always on.

                # Parse parameter in trial pulse to be given to DAQ.
                
                #TODO: Change all analog channels to digital channels 
                
                
                if self.hardware_prefs['static']:
                    if concatenate:
                        odor_pulses : list = current_trial[9]
                        onset : float = current_trial_pulse[0]['onset']
                        offset : float = current_trial_pulse[0]['offset']
                        total_length : float= np.sum(odor_pulses) + onset + offset

                        #TODO: Understand t without analog input
                        t = np.linspace(0,
                                        total_length,
                                        int(total_length*self.hardware_prefs['samp_rate']))

                    else:
                        pulses = []

                        for params in current_trial_pulse:
                            this_pulse = PulseGeneration.simple_pulse_static(
                                self.hardware_prefs['samp_rate'], params)
                            pulses.append(this_pulse)
                            onset = params['onset']
                            offset = params['offset']

                        if current_trial_pulse[0]['fromLength']:
                            duration = current_trial_pulse[0]['length']
                        else:
                            duration = current_trial_pulse[0]['pulse_width']

                        odor_pulses = np.zeros((len(pulses), 1))

                        for p, pulse in enumerate(pulses):
                            odor_pulses[p] = pulse

                        total_length = round(duration + onset + offset, 10)

                        t = np.linspace(0,
                                        total_length,
                                        int(total_length*self.hardware_prefs['samp_rate']))

                        odor_pulses = [odor_pulses, onset, duration, offset]
                        fv_pulse = np.array([self.hardware_prefs['fv_delay']])

                # Check if schedule is defined as pretraining schedule.
                if not ('pretraining' in current_trial_pulse[0]):
                    pretraining = False
                else:
                    pretraining = current_trial_pulse[0]['pretraining']

                # Check if schedule is defined as odour training schedule.
                if not 'odour_training' in current_trial_pulse[0]:
                    odour_training = False
                else:
                    odour_training = current_trial_pulse[0]['odour_training']

                if pretraining and not concatenate:
                    # if a normal pretraining case, reward is given without
                    # trial. Then daq should measure if the lick port is
                    # licked afterwards.

                    self.reward(animal)
                    water_given = [True, True]

                    # Initialise DAQ
                    trial_daq = self.get_trial_daq(
                        t=t,
                        odor_pulses=odor_pulses,
                        current_trial=current_trial,
                        fv_pulse=fv_pulse,
                        pretraining=pretraining)

                    # Record start time
                    start_time = datetime.datetime.now()

                    # Get data from DAQ
                    #TODO: Change analog data to digital data
                    analog_data = trial_daq.DoTask()

                    # Get time of licked and number of licks
                    lick_time_l, licks_l = TrialConditions.licks_number(
                        analog_data[self.hardware_prefs['lick_channel_l']], 2, self.hardware_prefs['samp_rate'], start_time)
                    lick_time_r, licks_r = TrialConditions.licks_number(
                        analog_data[self.hardware_prefs['lick_channel_r']], 2, self.hardware_prefs['samp_rate'], start_time)

                    # Set licked time and number of licks as list
                    lick_time = [lick_time_l, lick_time_r]
                    licks = [licks_l, licks_r]

                    # Set last data to be shown in UI
                    self.experiment.last_data_l = analog_data[self.hardware_prefs['lick_channel_l']]
                    self.experiment.last_data_r = analog_data[self.hardware_prefs['lick_channel_r']]

                    # Detect if it was licked. That means, if number of licks
                    # is above a threshold
                    response_l = TrialConditions.lick_detect(
                        analog_data[self.hardware_prefs['lick_channel_l']], 2, float(current_trial_pulse[0]['lick_fraction']))
                    response_r = TrialConditions.lick_detect(
                        analog_data[self.hardware_prefs['lick_channel_r']], 2, float(current_trial_pulse[0]['lick_fraction']))
                    response = [response_l, response_r]

                    # Wait response is in this case 0
                    wait_response_l = 0
                    wait_response_r = 0
                    wait_response = [wait_response_l, wait_response_r]

                    # Save the probability and amount of rewards
                    rewarded = current_trial[0:6]

                    # In case of pretraining is correct always True
                    result, correct, timeout = TrialConditions.trial_result(
                        rewarded, response_l, response_r)
                    correct = True

                    # In this case, there is no wait window
                    wait_time_l = 'there is no wait window'
                    wait_time_r = 'there is no wait window'
                    wait_time = [wait_time_l, wait_time_r]

                    timestamp = datetime.datetime.now()

                else:
                    if odour_training:
                        # Get DAQ for odour training.
                        trial_daq = self.get_trial_daq(
                            t=t,
                            odor_pulses=odor_pulses,
                            current_trial=current_trial,
                            fv_pulse=fv_pulse,
                            odour_training=odour_training)

                        #TODO: Change analog data to digital data
                        # Get data to be processed.
                        analog_data, wait_data, should_lick_data, start_time, water_given, wait_response, wait_time, start_time_2 = trial_daq.DoTask()

                        # Set last data to be shown in UI
                        self.experiment.last_data_l = analog_data[self.hardware_prefs['lick_channel_l']]
                        self.experiment.last_data_r = analog_data[self.hardware_prefs['lick_channel_r']]

                        # Save the probability and amount of rewards
                        rewarded = current_trial[0:6]

                        # Detect if it was licked. That means, if number of
                        # licks is above a threshold
                        response_l = TrialConditions.lick_detect(
                            should_lick_data[self.hardware_prefs['lick_channel_l']], 2, float(current_trial_pulse[0]['lick_fraction']))
                        response_r = TrialConditions.lick_detect(
                            should_lick_data[self.hardware_prefs['lick_channel_r']], 2, float(current_trial_pulse[0]['lick_fraction']))
                        response = [response_l, response_r]

                        result, correct, timeout = TrialConditions.trial_result(
                            rewarded, response_l, response_r)
                        # correct = np.logical_or(*water_given) # If needed, correct always True if water is given

                        # Detect number of licks and lick timestamps
                        lick_time_l, licks_l = TrialConditions.licks_number(
                            should_lick_data[self.hardware_prefs['lick_channel_l']], 2, self.hardware_prefs['samp_rate'], start_time)
                        lick_time_r, licks_r = TrialConditions.licks_number(
                            should_lick_data[self.hardware_prefs['lick_channel_r']], 2, self.hardware_prefs['samp_rate'], start_time)
                        lick_time = [lick_time_l, lick_time_r]
                        licks = [licks_l, licks_r]

                        print('water given :', str(water_given))
                        print('wait response :', str(wait_response))

                        timestamp = start_time_2

                        # timeout if necessary
#                        if timeout or wait_response > 15:
#                            self.timeout()

                    else:
                        # If schedule is not odour training or pretraining, then
                        # it is normal trial.

                        # Get DAQ
                        if concatenate:
                            trial_daq = self.get_trial_daq(
                                odor_pulses=odor_pulses,
                                current_trial=current_trial,
                                concatenate=concatenate,
                                pretraining=pretraining)
                        else:
                            trial_daq = self.get_trial_daq(
                                t=t,
                                odor_pulses=odor_pulses,
                                current_trial=current_trial,
                                fv_pulse=fv_pulse)

                        # Get data from DAQ
                        #TODO: Change analog data to digital data
                        analog_data, wait_data, should_lick_data, start_time1, start_time2, water_given = trial_daq.DoTask()

                        # Set last data to be shown in UI
                        self.experiment.last_data_l = analog_data[self.hardware_prefs['lick_channel_l']]
                        self.experiment.last_data_r = analog_data[self.hardware_prefs['lick_channel_r']]

                        # Save number of licks and licks timestamps of wait
                        # window, if window existed
                        wait_time_l, wait_response_l = TrialConditions.licks_number(
                            wait_data[self.hardware_prefs['lick_channel_l']], 2, self.hardware_prefs['samp_rate'], start_time2)
                        wait_time_r, wait_response_r = TrialConditions.licks_number(
                            wait_data[self.hardware_prefs['lick_channel_r']], 2, self.hardware_prefs['samp_rate'], start_time2)

                        wait_time = [wait_time_l, wait_time_r]
                        wait_response = [wait_response_l, wait_response_r]

                        # Save the probability and amount of rewards
                        rewarded = current_trial[0:6]

                        # Detect if it was licked. That means, if number of
                        # licks is above a threshold
                        response_l = TrialConditions.lick_detect(
                            should_lick_data[self.hardware_prefs['lick_channel_l']], 2, float(current_trial_pulse[0]['lick_fraction']))
                        response_r = TrialConditions.lick_detect(
                            should_lick_data[self.hardware_prefs['lick_channel_r']], 2, float(current_trial_pulse[0]['lick_fraction']))
                        response = [response_l, response_r]

                        result, correct, timeout = TrialConditions.trial_result(
                            rewarded, response_l, response_r)
                        # correct = np.logical_or(*water_given) # If needed: correct always True, if water is given

                        # Detect number of licks and lick timestamps
                        lick_time_l, licks_l = TrialConditions.licks_number(
                            should_lick_data[self.hardware_prefs['lick_channel_l']], 2, self.hardware_prefs['samp_rate'], start_time1)
                        lick_time_r, licks_r = TrialConditions.licks_number(
                            should_lick_data[self.hardware_prefs['lick_channel_r']], 2, self.hardware_prefs['samp_rate'], start_time1)

                        lick_time = [lick_time_l, lick_time_r]
                        licks = [licks_l, licks_r]

                        # timeout if needed
                        if result == TrialConditions.TrialResult.false_alarm:
                            self.timeout()

                        print('water given :', str(water_given))
                        print('wait_response :', str(wait_response))
                        timestamp = start_time2

                # Save trial duration in seconds
                length = time() - start

                # Update database.
                animal.schedule_list[animal.current_schedule_idx].add_trial_data(
                    timestamp, wait_response, response, correct, timeout, licks, rewarded)
                self.experiment.add_trial(animal.id, timestamp.strftime("%Y-%m-%d %H:%M:%S.%f"), animal.current_schedule_idx, animal.current_trial_idx,
                                          list(map(str, rewarded)), wait_response, response, str(correct), timeout, licks)

                # Update licks log.
                self.lock_llog.lockForWrite()
                animal.update_licks(timestamp.strftime("%Y-%m-%d %H:%M:%S.%f"), rewarded, wait_response,
                                    licks, self.experiment.logs_path, water_given, np.sum(water_given[0]), int(timeout))
                self.lock_llog.unlock()

                # Check licks and status
                self.check_licks()
                sleep(0.005)
                self.check_status()

                """ Advance animal to next trial """
                animal.advance_trial()

                """ Save bulkiest part of data to disk and save experiment if necessary """
                self.save_data(animal.id, timestamp, rewarded, wait_response, response, correct,
                               timeout, odor_pulses, t, self.save_timestamp, lick_time, licks, wait_time)

                if len(self.experiment.trials) % 10 == 0:
                    self.experiment.save()

                """ Signal that trial has finished """
                print("water given:", water_given)
                print("Trial index : {0}".format(
                    len(self.experiment.trials)-1))
                print("Length of trial : {0:.2f} s".format(length))
                print("Trial at ", timestamp.strftime('%X'))

                self.trial_end.emit()
            else:
                self.check_licks()
                sleep(0.005)
                self.check_status()

            # If there is no beam broken, then beam will be check every 0.5 s.
            sleep(0.5)
        self.finished.emit()

    def check_status(self):
        """
        Check if deadman's switch has be sent or not. Message will be sent at
        8 AM, 5 PM, and 10 PM.
        """

        if datetime.date.today() != self.today:
            self.today = datetime.date.today()
            self.morning_notification_sent = False
            self.afternoon_notification_sent = False
            self.evening_notification_sent = False

        morning = datetime.datetime.combine(self.today, datetime.time(hour=8))
        afternoon = datetime.datetime.combine(self.today, datetime.time(hour=17))
        evening = datetime.datetime.combine(self.today, datetime.time(hour=22))
        now = datetime.datetime.now()

        if now > morning and now <= afternoon and not self.morning_notification_sent:
            print('sending morning mail')
            email.deadmans_switch(self.experiment)
            self.morning_notification_sent = True
        elif now > afternoon and now <= evening and not self.afternoon_notification_sent:
            print('sending afternoon mail')
            email.deadmans_switch(self.experiment)
            self.afternoon_notification_sent = True
        elif now > evening and not self.evening_notification_sent:
            email.deadmans_switch(self.experiment)
            self.evening_notification_sent = True
        elif now < morning and not self.notification_sent:
            email.deadmans_switch(self.experiment)
            self.notification_sent = True

    def check_licks(self):
        """
        Check if a mouse has not licked in a period of time, then send a
        warning e-mail. Currently, all e-mail will be saved as text notification
        in Dropbox.
        """

        self.lock_llog.lockForRead()
        interval = datetime.timedelta(hours=6)  # Period set to 6 hours

        if (datetime.datetime.now() - self.start_timestamp[0]) > interval:
            self.start_timestamp[0] = datetime.datetime.now()
            problem_list = list()
            for animal in self.experiment.animal_list:
                if animal != 'default':
                    fname = self.experiment.animal_list[animal].fname
                    if fname is not None and os.path.isfile(fname):
                        with open(fname, 'r', newline='') as f:
                            licks_list = f.readlines()
                            licks_list = licks_list[1:]
                        for i, row in enumerate(licks_list):
                            licks_list[i] = row.split(';')
                    else:
                        licks_list = list()

                    if len(licks_list) == 0:
                        last_hour_low_licked = True
                    else:
                        licks_T = list(map(list, zip(*licks_list)))
                        time = list()
                        for x in range(len(licks_T[0])):
                            time.append(datetime.datetime.strptime(
                                licks_T[0][x].strip('\n'), '%Y-%m-%d %H:%M:%S.%f'))
                        try:
                            licks = licks_T[6]
                        except:
                            licks = [0]

                        if self.start_timestamp[0] - time[-1] > interval or licks[-1] == 0 or licks[-1] == None:
                            last_hour_low_licked = True
                        else:
                            if time[-1] - time[0] < interval:
                                licks_per_trial_last_hour = (
                                    int(licks[-1]) - int(licks[0]))/len(licks)
                            else:
                                i = 2
                                while time[-1] - time[-i] < interval:
                                    i += 1
                                licks_per_trial_last_hour = (
                                    int(licks[-1])-int(licks[-i]))/i
                            last_hour_low_licked = licks_per_trial_last_hour < self.hardware_prefs[
                                'low_lickrate']

                    if last_hour_low_licked:
                        problem_list.append(animal)
            if len(problem_list) > 0:
                problem_list.append('default')
                email.warning_licks(self.experiment.logs_path, problem_list)
        self.lock_llog.unlock()

    def animal_present(self):
        """Checks whether animal is present in the port."""

        # DEBUG : for debugging purpose
        #return np.random.rand() > 0.5

        return beam.check_beam(self.hardware_prefs['beam_channel'])

    def get_present_animal(self):
        """Returns the animal in the port. 'Rfid.check_rfid' method differs 
        between NoSeMaze 1 and NoSeMaze 2."""

        # DEBUG : just chooses a random animal
        # animals = list(self.experiment.animal_list.keys())
        # animal = np.random.choice(animals)

        animal = rfid.check_rfid(self.hardware_prefs['rfid_port'], 10)
        try:
            if animal in self.experiment.animal_list.keys():
                return self.experiment.animal_list[animal]
            else:
                return self.experiment.animal_list['default']
        except:
            return self.experiment.animal_list['default']

    def reward(self, animal: Mouse):
        """
        Initialise DAQ and execute giving water.

        Parameters
        ----------
        animal : instance of Mouse class from Experiment module
            Instance of mouse to be given the reward. Reward is given according
            to the schedule (Only amount of water. Reward is always given or 
            probability is always 1).
        """

        if self.hardware_prefs['static']:
            rewarded = animal.current_trial()
            if rewarded[0] > 0 and rewarded[1] > 0:
                reward.deliver_reward_static_two(
                    self.hardware_prefs['reward_output1'], self.hardware_prefs['reward_output2'], rewarded[2], rewarded[3])
            elif rewarded[0] > 0 and rewarded[1] == 0:
                reward.deliver_reward_static(
                    self.hardware_prefs['reward_output1'], rewarded[2])
            elif rewarded[0] == 0 and rewarded[1] > 0:
                reward.deliver_reward_static(
                    self.hardware_prefs['reward_output2'], rewarded[3])

    def timeout(self):
        """Set the thread to sleep of a duration."""

        sleep(self.hardware_prefs['timeout'])

    def save_data(self, animal_id: str, timestamp: datetime.datetime, rewarded: list,
                  wait_response: list, response: list, correct: bool, timeout: bool,
                  pulses: np.array, time_axis: np.array,
                  file_timestamp: datetime.datetime, lick_time: list[list],
                  licks: list[float], wait_time: list[list]):
        """
        Save experiment data. New data will be appended in the existing file.
        If there is no existing file or date is changed, a new file will be
        made.

        Parameters
        ----------
        animal_id : str
            Id of animal

        timestamp : datetime.datetime
            Timestamp of trial started.

        rewarded : list
            List of reward parameters (Reward probabilty and amount of water).

        wait_respone : list
            Response at wait window of left and right port. Currently, only left
            port is used.

        response : list
            Response at lick window of left and right port. Currently, only left
            port is used.

        correct : bool
            Indicator if trial is correctly performed (hit or correct 
            rejection). Currently, correct is always True if water is given.
            That means, correct rejection will be falsely indicated as false.

        timeout : bool
            Indicator if a timeout is executed. Currently, there is no timeout.

        pulses : ndarray
            Array of pulses shown. Currently obsolete.

        time_axis : ndarray
            Array of indicator of time axis. Currently obsolete.

        file_timestamp : datetime.datetime
            Timestamp to be converted to file name.

        lick_time : 2d-list
            List of timestamp of licks on left port and right port. Currently,
            only left port is used.

        licks : list of float
            List of number of licks on left port and right port. Currently,
            only left port is used.

        wait_time : 2d-list
            List of timestamp of licks in wait window.
        """

        strTimestamp = str(timestamp)
        file_timestamp = str(file_timestamp).replace('/', '-')
        file_timestamp = file_timestamp.replace(' ', 'T')
        file_timestamp = file_timestamp.replace(':', '')
        file_timestamp = file_timestamp.split('.')[0]

        file_name = self.experiment.save_path + '/' + 'trials_'+file_timestamp

        # change rewarded into a str variable
        rewarded = '|'.join(list(map(str, rewarded)))

        newData = {
            'a_animal_id': animal_id,
            'b_timestamp': strTimestamp,
            'c_licks_number_l': licks[0],
            'd_licks_number_r': licks[1],
            'e_rewarded': rewarded,
            'f_wait_response_l': wait_response[0],
            'g_wait_response_r': wait_response[1],
            'h_response_l': response[0],
            'i_response_r': response[1],
            'j_correct': correct,
            'k_timeout': timeout,
            'l_wait_timestamps_l': wait_time[0],
            'm_wait_timestamps_r': wait_time[1],
            'n_lick_timestamp_l': lick_time[0],
            'o_lick_timestamp_r': lick_time[1]
        }

        # save in .csv
        fn = sorted(newData.keys())
        if os.path.isfile(file_name+'.csv'):
            should_write_header = False
        else:
            should_write_header = True
        with open(file_name+'.csv', 'a+', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fn, delimiter=';')
            if should_write_header:
                writer.writeheader()
            writer.writerow(newData)

    def get_trial_daq(self, t: list = None, odor_pulses: object | list[float] = None,
                      current_trial: list | float = None, fv_pulse: float = None,
                      pretraining: bool = False, odour_training: bool = False,
                      concatenate: bool = False) -> daq.ThreadSafeAnalogInput | \
                      daq.DoAiMultiTaskOdourTraining  |  daq.DoAiMultiTask:
        """
        Initialise daq instance then returns it. Daq instance is responsible 
        for data acquisition and the sequences of the actual trial. E.g. 
        sequence of pretraining trial or wait training trial.


        Parameters
        ----------
        t : list
            Time axis.

        odor_pulses : obj or list of float
            List of odor parameters to be given to DAQ

        current_trial : list of float
            Current trial parameters. Details, see schedule generator.

        fv_pulse : float
            Duration of delay before final valve is opened.

        pretraining : bool
            Indicator if schedule is for pretraining.

        odour_training : bool
            Indicator if schedule is for odour training.

        concatenate : bool
            Indicator if schedule is for concatenated trial.

        Returns
        -------
        trial_daq : daqface.daq-class
            Instance of daq class that is responsible of executing the trial
            sequence.
        """

        if pretraining and not concatenate:
            trial_daq = daq.ThreadSafeAnalogInput(
                self.hardware_prefs['analog_input'], self.hardware_prefs['analog_channels'], self.hardware_prefs['samp_rate'], 2)
        elif odour_training:
            trial_daq = daq.DoAiMultiTaskOdourTraining(self.hardware_prefs['analog_input'],
                                                       self.hardware_prefs['analog_channels'],
                                                       self.hardware_prefs['odour_output'],
                                                       self.hardware_prefs['finalvalve_output'],
                                                       self.hardware_prefs['reward_output1'],
                                                       self.hardware_prefs['reward_output2'],
                                                       self.hardware_prefs['samp_rate'],
                                                       len(t) /
                                                       self.hardware_prefs['samp_rate'],
                                                       odor_pulses, fv_pulse,
                                                       self.hardware_prefs['sync_clock'],
                                                       self.hardware_prefs['static'],
                                                       current_trial[4],
                                                       self.hardware_prefs['lick_delay'],
                                                       self.hardware_prefs['lick_channel_l'],
                                                       self.hardware_prefs['lick_channel_r'],
                                                       current_trial[0:4])

        else:
            trial_daq = daq.DoAiMultiTask(self.hardware_prefs['analog_input'],
                                          self.hardware_prefs['analog_channels'],
                                          self.hardware_prefs['odour_output'],
                                          self.hardware_prefs['finalvalve_output'],
                                          self.hardware_prefs['reward_output1'],
                                          self.hardware_prefs['reward_output2'],
                                          self.hardware_prefs['samp_rate'],
                                          len(t) /
                                          self.hardware_prefs['samp_rate'],
                                          odor_pulses, fv_pulse,
                                          self.hardware_prefs['sync_clock'],
                                          self.hardware_prefs['static'],
                                          current_trial[4],
                                          self.hardware_prefs["lick_delay"],
                                          self.hardware_prefs['lick_channel_l'],
                                          self.hardware_prefs['lick_channel_r'],
                                          current_trial[0:4])

        return trial_daq
