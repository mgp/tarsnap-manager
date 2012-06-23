import optparse
import subprocess
import time

def _get_filename(archive_name, period, time):
	return '%s_%s_%s-%s-%s' % (archive_name, period, time.tm_year, time.tm_mon, time.tm_day)

def _get_daily_filename(archive_name, tm):
	return get_filename(archive_name, 'daily', tm)

def _get_weekly_filename(archive_name, tm):
	return get_filename(archive_name, 'weekly', tm)

def _get_monthly_filename(archive_name, tm):
	return get_filename(archive_name, 'monthly', tm)

def _run(options, args):
	if options.dry_run:
		print ' '.join(args)
	else:
		subprocess.call(args)

def _make_archive(options, paths, filename):
	pass

def _delete_archive(options, filename):
	pass

def _make_daily_archive(options, paths, tm):
	filename = _get_daily_filename(options.archive_name, tm)
	_make_archive(options, paths, filename)

def _make_weekly_archive(options, paths, tm):
	if tm.tm_wday() == options.weekday:
		filename = _get_weekly_filename(options.archive_name, tm)
		_make_archive(options, paths, filename)
		# TODO: Delete oldest weekly backup if necessary.

def _make_monthly_archive(options, paths, tm):
	if (tm.tm_wday() == options.weekday) and (tm.mday <= 7):
		filename = _get_monthly_filename(options.archive_name, tm)
		_make_archive(options, paths, filename)
		# TODO: Delete oldest monthly backup if necessary.

def backup(options, paths):
	tm = time.gmtime()
	_make_daily_archive(options, paths, tm)
	_make_weekly_archive(options, paths, tm)
	_make_monthly_archive(options, paths, tm)

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

