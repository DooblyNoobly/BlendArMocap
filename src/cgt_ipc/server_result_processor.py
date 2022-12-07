from .json_parser import JsonParser
from ..cgt_patterns import observer_pattern, events
from ..cgt_processing import processor_interface, hand_processing, face_processing, pose_processing


class ServerResultsProcessor(object):
    data_listener: observer_pattern.Listener
    data_observer: observer_pattern.Observer
    data_processor: processor_interface.DataProcessor
    json_parser: JsonParser

    start_frame: int = 0
    user = None
    bridge_initialized: bool

    def __init__(self):
        self.json_parser = JsonParser()
        self.bridge_initialized = False

    def exec(self, payload: str):
        """ Push server results in the processing bridge """
        arr, frame = self.json_parser.exec(payload)
        if not self.bridge_initialized:
            self.bridge_initialized = self.init_bridge(self.json_parser.detection_type)
        self.update_data_listeners(arr, frame)

    def init_bridge(self, data_type: str):
        """ Initializes bridge to blender """
        if data_type == 'HOLISTIC':
            _processor = [hand_processing.HandProcessor(), face_processing.FaceProcessor(),
                          pose_processing.PoseProcessor()]
            _listener = events.UpdateListener()
            _observer = events.HolisticBpyUpdateReceiver(_processor)
            self.data_observer = _observer
            self.data_listener = _listener
            self.data_listener.attach(self.data_observer)
            return True

        processors = {
            'HANDS': hand_processing.HandProcessor,
            'FACE': face_processing.FaceProcessor,
            'POSE': pose_processing.PoseProcessor
        }

        _processor = processors[data_type]()
        _listener = events.UpdateListener()
        _observer = events.BpyUpdateReceiver(_processor)

        self.data_observer = _observer
        self.data_listener = _listener
        self.data_listener.attach(self.data_observer)
        return True

    def update_data_listeners(self, payload, frame):
        """ Update listeners """
        # todo: add start frame
        self.data_listener.data = payload
        self.data_listener.frame = self.start_frame + frame
        self.data_listener.notify()

    def __del__(self):
        """ Upon finish processing. """
        self.data_listener.detach(self.data_observer)
        del self.data_observer
        del self.data_listener
