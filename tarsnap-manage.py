import optparse
import subprocess
import time
from datetime import date, timedelta

def _get_filename(archive_name, period, d):
	return '%s_%s_%s' % (archive_name, period, d.isoformat())

def _get_daily_filename(archive_name, d):
	return get_filename(archive_name, 'daily', d)

def _get_weekly_filename(archive_name, d):
	return get_filename(archive_name, 'weekly', d)

def _get_monthly_filename(archive_name, d):
	return get_filename(archive_name, 'monthly', d)

def _run(options, args):
	if options.dry_run:
		s = ' '.join(args)
		print s
		# Return for unit testing.
		return s
	else:
		subprocess.call(args)

def _make_archive(options, paths, filename):
	pass

def _delete_archive(options, filename):
	pass

def _make_daily_archive(options, paths, d):
	filename = _get_daily_filename(options.archive_name, d)
	_make_archive(options, paths, filename)

def _make_weekly_archive(options, paths, d):
	if d.isoweekday() == options.weekday:
		filename = _get_weekly_filename(options.archive_name, d)
		_make_archive(options, paths, filename)
		# Delete the oldest weekly backup if it exists.
		td = timedelta(weeks=options.num_weeks)
		oldest_date = d - td
		oldest_filename = _get_weekly_filename(options.archive_name, oldest_date)
		_delete_archive(options, oldest_filename)

def _subtract_months(d, num_months):
	one_week = timedelta(weeks=1)
	prev_d = d
	months_counted = 0
	while True:
		prev_d -= one_week
		if d.isoweekday() <= 7:
			months_counted += 1
			if months_counted == num_months:
				break
	return prev_d

def _make_monthly_archive(options, paths, d):
	if (d.isoweekday() == options.weekday) and (d.day <= 7):
		filename = _get_monthly_filename(options.archive_name, d)
		_make_archive(options, paths, filename)
		# Delete the oldest monthly backup if it exists.
		oldest_date = _subtract_months(d, options.num_months)
		oldest_filename = _get_monthly_filename(options.archive_name, oldest_date)
		_delete_archive(options, oldest_filename)

def backup(options, paths):
	d = date.today()
	_make_daily_archive(options, paths, d)
	_make_weekly_archive(options, paths, d)
	_make_monthly_archive(options, paths, d)

def _parse_args():
	parser = optparse.OptionParser()
	parser.add_option('--key_file', 'The key file for encryption.')
	parser.add_option('--dry_run', 'Whether a dry run should be performed.')
	parser.add_option('--archive_name', 'Name of the archive that is archive_nameed to each filename.')
	parser.add_option('--weekday', 'The day on which to do daily and weekly backups, where Monday is 0 and Sunday is 6.')
	parser.add_option('--num_days', 'The number of consecutive daily backups to store.')
	parser.add_option('--num_weeks', 'The number of consecutive weekly backups to store.')
	parser.add_option('--num_months', 'The number of consecutive monthly backups to store.')
	return parser.parse_args()

if __name__ == '__main__':
	options, paths = _parse_args()
	backup(options, paths)

