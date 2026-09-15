#%%
import os
import sounddevice as sd
from functools import wraps

def enable_asio():
    import importlib
    asio_key = 'SD_ENABLE_ASIO'
    os.environ['SD_ENABLE_ASIO'] = '1'
    importlib.reload(sd)


def query_devices(hosts,formatter='$index$ - $name$ ($api$, $io$)'):
    keys = formatter.split('$')
    keys = [s for s in keys if s != '']

    device_data = _get_device_data(hosts)
    formatted_devices = []
    for device in device_data:
        string = _format_string(device,keys)
        formatted_devices.append(string)
    return formatted_devices


@wraps(query_devices)
def print_devices(*args,**kwargs):
    devlist = query_devices(*args,**kwargs)
    for dev in devlist:
        print(dev)


def _get_device_data(hosts='ASIO'):
    host_full = sd.query_hostapis()
    host_names = [host['name'] for host in host_full]
    if hosts == 'all':
        hosts = host_names
    elif isinstance(hosts,str):
        hosts = [hosts]

    hosts_to_query = [host for host in host_names if (host in hosts)]

    devices_index = [host['devices'] for host in host_full if (host['name'] in hosts_to_query)]
    device_data = []
    for hst in devices_index:
        for dev in hst:
            device_data.append(sd.query_devices(dev))
    return device_data


def _format_string(device,keys):
    host_names = [host['name'] for host in sd.query_hostapis()]
    out_str = ''
    for key in keys:
        key = key.lower()
        if key == 'index':
            out_str +=  f"{device['index']}"
        elif key == 'name':
            out_str += f"{device['name']}"
        elif key == 'io':
            out_str += f"{device['max_input_channels']}i{device['max_output_channels']}o"
        elif key == 'api':
            out_str += f"{host_names[int(device['hostapi'])]} "
        elif key == 'fs':
            out_str += f"{device['default_samplerate']}"
        else:
            out_str += key
    return out_str
#%%
# print_devices('ASIO')
