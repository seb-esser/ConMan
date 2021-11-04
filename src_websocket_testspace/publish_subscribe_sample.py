
from pubsub import pub


# ------------ create a listener ------------------

def listener1(patch):
    print('Function listener1 received:')
    print('  patch =', patch)


def sub_listener1(patch):
    print('Function sub_listener1 received:')
    print('  patch =', patch)


# ------------ register listener ------------------

pub.subscribe(listener1, 'rootTopic')
pub.subscribe(sub_listener1, 'subtopic')

# ---------------- send a message ------------------

print('Publish something via pubsub')
anObj = dict(a=456, b='abc')
pub.sendMessage('rootTopic.subtopic', sa=anObj)
