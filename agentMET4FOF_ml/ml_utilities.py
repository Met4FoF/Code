def extract_x_y(message):
    """Extract features & target from ``message['data']`` with expected structure

    The message structure should resemble one of:

    1. tuple - (x,y)
    2. dict - {'x':x_data,'y':y_data}
    """
    if type(message['data']) == tuple:
        x = message['data'][0]
        y = message['data'][1]
    elif type(message['data']) == dict:
        x = message['data']['x']
        y = message['data']['y']
    else:
        return 1
    return x, y