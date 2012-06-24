from datetime import date
import unittest

import tarsnap_manager

_DEFAULT_KEY_FILE = 'key_file_value'
_DEFAULT_ARCHIVE_NAME = 'archive_name_value'
_DEFAULT_WEEKDAY = 4
_DEFAULT_NUM_DAYS = 5
_DEFAULT_NUM_WEEKS = 3
_DEFAULT_NUM_MONTHS = 2

def _get_valid_args_map():
	args = {}
	args['key_file'] = _DEFAULT_KEY_FILE
	args['archive_name'] = _DEFAULT_ARCHIVE_NAME
	args['weekday'] = _DEFAULT_WEEKDAY
	args['num_days'] = _DEFAULT_NUM_DAYS
	args['num_weeks'] = _DEFAULT_NUM_WEEKS
	args['num_months'] = _DEFAULT_NUM_MONTHS
	return args

def _make_args_array(args):
	return ['--%s=%s' % (key, value) for key, value in args.iteritems()]

class TarsnapManagerTestCase(unittest.TestCase):
	def test_filenames(self):
		archive_name = 'foo'
		d = date(2012, 3, 24)

		filename = tarsnap_manager._get_daily_filename(archive_name, d)
		self.assertEquals('foo_daily_2012-03-24', filename)

		filename = tarsnap_manager._get_weekly_filename(archive_name, d)
		self.assertEquals('foo_weekly_2012-03-24', filename)

		filename = tarsnap_manager._get_monthly_filename(archive_name, d)
		self.assertEquals('foo_monthly_2012-03-24', filename)

	def test_subtract_months(self):
		# February 3 2012 is the first Friday.
		d = date(2012, 2, 3)

		# January 6 2012 is also a first Friday.
		new_date = tarsnap_manager._subtract_months(d, 1)
		self.assertEquals(2012, new_date.year)
		self.assertEquals(1, new_date.month)
		self.assertEquals(6, new_date.day)

		# December 2 2011 is also a first Friday.
		new_date = tarsnap_manager._subtract_months(d, 2)
		self.assertEquals(2011, new_date.year)
		self.assertEquals(12, new_date.month)
		self.assertEquals(2, new_date.day)

		# October 7 2011 is also a first Friday.
		new_date = tarsnap_manager._subtract_months(d, 4)
		self.assertEquals(2011, new_date.year)
		self.assertEquals(10, new_date.month)
		self.assertEquals(7, new_date.day)

		# July 1 2011 is also a first Friday.
		new_date = tarsnap_manager._subtract_months(d, 7)
		self.assertEquals(2011, new_date.year)
		self.assertEquals(7, new_date.month)
		self.assertEquals(1, new_date.day)

	def test_valid_args(self):
		args = _make_args_array(_get_valid_args_map())
		options, args = tarsnap_manager._parse_args(args)
		self.assertEquals(_DEFAULT_KEY_FILE, options.key_file)
		self.assertFalse(options.dry_run)
		self.assertEquals(_DEFAULT_ARCHIVE_NAME, options.archive_name)
		self.assertEquals(_DEFAULT_WEEKDAY, options.weekday)
		self.assertEquals(_DEFAULT_NUM_DAYS, options.num_days)
		self.assertEquals(_DEFAULT_NUM_WEEKS, options.num_weeks)
		self.assertEquals(_DEFAULT_NUM_MONTHS, options.num_months)

		# Assert that the dry_run option is recognized.
		args = _make_args_array(_get_valid_args_map())
		args.append('--dry_run')
		options, args = tarsnap_manager._parse_args(args)
		self.assertTrue(options.dry_run)

	def test_invalid_args(self):
		args = _get_valid_args_map()
		del args['key_file']
		with self.assertRaises(SystemExit):
			tarsnap_manager._parse_args(_make_args_array(args))

		args = _get_valid_args_map()
		args['archive_name'] = ''
		with self.assertRaises(SystemExit):
			tarsnap_manager._parse_args(_make_args_array(args))

		args = _get_valid_args_map()
		args['weekday'] = 0
		with self.assertRaises(SystemExit):
			tarsnap_manager._parse_args(_make_args_array(args))

		args = _get_valid_args_map()
		args['weekday'] = 8
		with self.assertRaises(SystemExit):
			tarsnap_manager._parse_args(_make_args_array(args))

		args = _get_valid_args_map()
		args['num_days'] = 0
		with self.assertRaises(SystemExit):
			tarsnap_manager._parse_args(_make_args_array(args))

		args = _get_valid_args_map()
		args['num_weeks'] = -1
		with self.assertRaises(SystemExit):
			tarsnap_manager._parse_args(_make_args_array(args))

		args = _get_valid_args_map()
		args['num_months'] = -1
		with self.assertRaises(SystemExit):
			tarsnap_manager._parse_args(_make_args_array(args))


class MakeDeleteArchiveTestCase(unittest.TestCase):
	def setUp(self):
		# Use the fake methods for testing.
		self.prev_run = tarsnap_manager._run
		tarsnap_manager._run = self._fake_run

		# Clear the command called with.
		self.run_cmd = None

		self.filename = 'filename_value'
	
	def tearDown(self):
		tarsnap_manager._run = self.prev_run

	def _fake_run(self, options, args):
		self.run_cmd = ' '.join(args)

	def test_make_archive(self):
		args = _make_args_array(_get_valid_args_map())
		options, args = tarsnap_manager._parse_args(args)

		paths = ('/path1', '/path2')
		tarsnap_manager._make_archive(options, paths, self.filename)
		expected_cmd = 'tarsnap --keyfile %s --cachedir %s -c -f %s %s %s' % (
			_DEFAULT_KEY_FILE,
			tarsnap_manager._DEFAULT_CACHE_DIR,
			self.filename,
			paths[0], paths[1])
		self.assertEquals(expected_cmd, self.run_cmd)
	
	def test_delete_archive(self):
		args = _make_args_array(_get_valid_args_map())
		options, args = tarsnap_manager._parse_args(args)

		tarsnap_manager._delete_archive(options, self.filename)
		expected_cmd = 'tarsnap --keyfile %s --cachedir %s -d -f %s' % (
			_DEFAULT_KEY_FILE,
			tarsnap_manager._DEFAULT_CACHE_DIR,
			self.filename)
		self.assertEquals(expected_cmd, self.run_cmd)


class WeeklyMonthlyArchiveTestCase(unittest.TestCase):
	def setUp(self):
		# Use the fake methods for testing.
		self.prev_make_archive = tarsnap_manager._make_archive
		self.prev_delete_archive = tarsnap_manager._delete_archive
		tarsnap_manager._make_archive = self._fake_make_archive
		tarsnap_manager._delete_archive = self._fake_delete_archive

		# Clear the archive names called with.
		self.make_archive_filename = None
		self.delete_archive_filename = None

		# February 3 2012 is a Friday.
		self.d = date(2012, 2, 3)
		self.paths = ('/path1', '/path2')
		self.archive_name = 'foo'
	
	def tearDown(self):
		tarsnap_manager._make_archive = self.prev_make_archive
		tarsnap_manager._delete_archive = self.prev_delete_archive

	def _fake_make_archive(self, options, paths, filename):
		self.make_archive_filename = filename
	
	def _fake_delete_archive(self, options, filename):
		self.delete_archive_filename = filename

	def test_make_weekly_archive(self):
		args = _make_args_array(_get_valid_args_map())
		options, args = tarsnap_manager._parse_args(args)
		options.archive_name = 	self.archive_name

		# Do not write when Friday but num_weeks is 0.
		options.num_weeks = 0
		options.weekday = 5
		tarsnap_manager._make_weekly_archive(options, self.paths, self.d)
		self.assertIsNone(self.make_archive_filename)
		self.assertIsNone(self.delete_archive_filename)

		# Do not write when num_weeks > 0 but not right weekday.
		options.num_weeks = 2
		options.weekday = 6
		tarsnap_manager._make_weekly_archive(options, self.paths, self.d)
		self.assertIsNone(self.make_archive_filename)
		self.assertIsNone(self.delete_archive_filename)

		# Write when num_weeks > 0 and also Friday.
		options.num_weeks = 2
		options.weekday = 5
		tarsnap_manager._make_weekly_archive(options, self.paths, self.d)
		self.assertEquals('foo_weekly_2012-02-03', self.make_archive_filename)
		self.assertEquals('foo_weekly_2012-01-20', self.delete_archive_filename)
	
	def test_make_monthly_archive(self):
		args = _make_args_array(_get_valid_args_map())
		options, args = tarsnap_manager._parse_args(args)

		# February 3 2012 is a Friday.
		d = date(2012, 2, 3)
		paths = ('/path1', '/path2')
		options.archive_name = 'foo'

		tarsnap_manager._make_archive = self._fake_make_archive
		tarsnap_manager._delete_archive = self._fake_delete_archive
		self.make_archive_filename = None
		self.delete_archive_filename = None

		# Do not write when the first Friday but num_months is 0.
		options.num_months = 0
		options.weekday = 5
		tarsnap_manager._make_monthly_archive(options, paths, d)
		self.assertIsNone(self.make_archive_filename)
		self.assertIsNone(self.delete_archive_filename)

		# Do not write when num_months > 0 and first week but not right weekday.
		options.num_months = 2
		options.weekday = 6
		tarsnap_manager._make_monthly_archive(options, paths, d)
		self.assertIsNone(self.make_archive_filename)
		self.assertIsNone(self.delete_archive_filename)
		
		# Do not write when num_months > 0 and Friday but not first week.
		options.num_months = 2
		options.weekday = 5
		tarsnap_manager._make_monthly_archive(options, paths, date(2012, 2, 10))
		self.assertIsNone(self.make_archive_filename)
		self.assertIsNone(self.delete_archive_filename)

		# Write when num_months > 0 and also the first Friday.
		tarsnap_manager._make_monthly_archive(options, paths, d)
		self.assertEquals('foo_monthly_2012-02-03', self.make_archive_filename)
		self.assertEquals('foo_monthly_2011-12-02', self.delete_archive_filename)


if __name__ == '__main__':
	unittest.main()

