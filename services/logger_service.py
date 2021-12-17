from datetime import datetime, timedelta
import logging

current_day = datetime.today().strftime("%d_%m_%y")
logging.basicConfig(filename='Location_reminder_log%s.log' % current_day,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)