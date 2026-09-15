def force_asio():
    import os
    import importlib
    import sounddevice as sd
    os.environ['SD_ENABLE_ASIO'] = '1'
    importlib.reload(sd)

_template_list = []

def _get_playrec_instance(play_method,rec_method):
    for method in _template_list:
        if method.play_method == play_method and method.rec_method == rec_method:
            return method
