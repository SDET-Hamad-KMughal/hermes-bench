import logging
import os

# Get the path to the 'instance' folder
instance_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'instance')

if not os.path.exists(instance_path):
    os.makedirs(instance_path)

log_file_path = os.path.join(instance_path, 'hermes.log')

logger = logging.getLogger('hermes_logger')
logger.setLevel(logging.INFO)

# Use FileHandler with the absolute path
handler = logging.FileHandler(log_file_path)
logger.addHandler(handler)

def log_action(user, action):
    username = user.username if user and hasattr(user, 'username') else 'Anonymous'
    logger.info(f"User: {username} | Action: {action}")