from . import db
from datetime import datetime, timedelta
from pytz import timezone  # For PST timezone handling

class StateCount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(200), nullable=False)
    count = db.Column(db.Integer, nullable=False, default=0)
    renewable = db.Column(db.Integer, nullable=False, default=0)
    solar = db.Column(db.Integer, nullable=False, default=0)
    wind = db.Column(db.Integer, nullable=False, default=0)
    hydro = db.Column(db.Integer, nullable=False, default=0)
    nuclear = db.Column(db.Integer, nullable=False, default=0)
    coal = db.Column(db.Integer, nullable=False, default=0)
    gas = db.Column(db.Integer, nullable=False, default=0)
    petroleum = db.Column(db.Integer, nullable=False, default=0)
    list_of_ids = db.Column(db.Text, nullable=False, default="")


class RecentSearch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(200), unique=True, nullable=False)
    clicks = db.Column(db.Integer, nullable=False, default=0)
    click_dates = db.Column(db.Text, nullable=False, default="")

    def get_click_dates(self):
        return self.click_dates.split(',') if self.click_dates else []

    def update_click_dates(self, current_date):
        pst = timezone('US/Pacific')
        if current_date.tzinfo is None:
            current_date = pst.localize(current_date)

        click_dates = self.get_click_dates()
        
        # Add the current date
        click_dates.append(current_date.strftime('%Y-%m-%d'))

        # Filter out dates older than 14 days
        cutoff_date = pst.localize(datetime.now() - timedelta(days=14))
        filtered_dates = [date for date in click_dates if pst.localize(datetime.strptime(date, '%Y-%m-%d')) >= cutoff_date]
        
        # Update the database fields
        self.click_dates = ','.join(filtered_dates)
        self.clicks = len(filtered_dates)