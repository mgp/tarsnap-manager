import optparse
import subprocess
import time
from datetime import date, timedelta

def _get_filename(archive_name, period, d):
	return '%s_%s_%s' % (archive_name, period, d.isoformat())

def _get_daily_filename(archive_name, d):
	return _get_filename(archive_name, 'daily', d)

def _get_weekly_filename(archive_name, d):
	return _get_filename(archive_name, 'weekly', d)

def _get_monthly_filename(archive_name, d):
	return _get_filename(archive_name, 'monthly', d)

def _run(options, args):
	if options.dry_run:
		s = ' '.join(args)
		print s
	else:
		subprocess.call(args)

def _append_required_args(options, args):
	args.extend(('--keyfile', options.key_file))
	args.extend(('--cachedir', options.cache_dir))

def _append_filename_arg(filename, args):
	args.extend(('-f', filename))

def _make_archive(options, paths, filename):
	args = ['tarsnap']
	_append_required_args(options, args)
	args.append('-c')
	_append_filename_arg(filename, args)
	args.extend(paths)
	_run(options, args)

def _delete_archive(options, filename):
	args = ['tarsnap']
	_append_required_args(options, args)
	args.append('-d')
	_append_filename_arg(filename, args)
	_run(options, args)

def _make_daily_archive(options, paths, d):
	filename = _get_daily_filename(options.archive_name, d)
	_make_archive(options, paths, filename)

def _make_weekly_archive(options, paths, d):
	if options.num_weeks and (d.isoweekday() == options.weekday):
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
		if prev_d.day <= 7:
			months_counted += 1
			if months_counted == num_months:
				break
	return prev_d

def _make_monthly_archive(options, paths, d):
	if options.num_months and (d.isoweekday() == options.weekday) and (d.day <= 7):
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

_DEFAULT_CACHE_DIR = '/usr/tarsnap-cache'

def _parse_args(args):
	# Parse the arguments.
	parser = optparse.OptionParser()
	parser.add_option('--key_file',
		help='The key file for encryption.')
	parser.add_option('--cache_dir',
		default=_DEFAULT_CACHE_DIR,
		help='The cache directory.')
	parser.add_option('--dry_run',
		action='store_true',
		default=False,
		help='Whether a dry run should be performed.')
	parser.add_option('--archive_name',
		help='Name of the archive that is prefixed to each filename.')
	parser.add_option('--weekday',
		type='int',
		default=0,
		help='The day on which to do daily and weekly backups, where Monday is 0 and Sunday is 6.')
	parser.add_option('--num_days',
		type='int',
		default=3,
		help='The number of consecutive daily backups to store.')
	parser.add_option('--num_weeks',
		type='int',
		default=2,
		help='The number of consecutive weekly backups to store.')
	parser.add_option('--num_months',
		type='int',
		default=1,
		help='The number of consecutive monthly backups to store.')
	options, args = parser.parse_args(args)

	# Validate the arguments.
	if not options.key_file:
		parser.error('option --key_file must be specified')
	if not options.archive_name:
		parser.error('option --archive_name must be specified')
	if (options.weekday < 0) or (options.weekday > 6):
		parser.error('option --weekday must be >= 0 and <= 6')
	if options.num_days <= 0:
		parser.error('option --num_days must be > 0')
	if options.num_weeks < 0:
		parser.error('option --num_weeks must be >= 0')
	if options.num_months < 0:
		parser.error('option --num_months must be >= 0')
	
	return options, args

if __name__ == '__main__':
	options, paths = _parse_args()
	backup(options, paths)

