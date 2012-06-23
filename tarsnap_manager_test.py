from datetime import date
import unittest

import tarsnap_manager

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
		# February 3 2012 is a Friday.
		d = date(2012, 2, 3)

		# January 6 2012 is also a Friday.
		new_date = tarsnap_manager._subtract_months(d, 1)
		self.assertEquals(2012, new_date.year)
		self.assertEquals(1, new_date.month)
		self.assertEquals(6, new_date.day)

		# December 2 2011 is also a Friday.
		new_date = tarsnap_manager._subtract_months(d, 2)
		self.assertEquals(2011, new_date.year)
		self.assertEquals(12, new_date.month)
		self.assertEquals(2, new_date.day)

		# October 7 2011 is also a Friday.
		new_date = tarsnap_manager._subtract_months(d, 4)
		self.assertEquals(2011, new_date.year)
		self.assertEquals(10, new_date.month)
		self.assertEquals(7, new_date.day)

		# July 1 2011 is also a Friday.
		new_date = tarsnap_manager._subtract_months(d, 7)
		self.assertEquals(2011, new_date.year)
		self.assertEquals(7, new_date.month)
		self.assertEquals(1, new_date.day)

	_DEFAULT_KEY_FILE = 'key_file_value'
	_DEFAULT_ARCHIVE_NAME = 'archive_name_value'
	_DEFAULT_WEEKDAY = 4
	_DEFAULT_NUM_DAYS = 5
	_DEFAULT_NUM_WEEKS = 3
	_DEFAULT_NUM_MONTHS = 2

	def _get_valid_args_map(self):
		args = {}
		args['key_file'] = TarsnapManagerTestCase._DEFAULT_KEY_FILE
		args['archive_name'] = TarsnapManagerTestCase._DEFAULT_ARCHIVE_NAME
		args['weekday'] = TarsnapManagerTestCase._DEFAULT_WEEKDAY
		args['num_days'] = TarsnapManagerTestCase._DEFAULT_NUM_DAYS
		args['num_weeks'] = TarsnapManagerTestCase._DEFAULT_NUM_WEEKS
		args['num_months'] = TarsnapManagerTestCase._DEFAULT_NUM_MONTHS
		return args
	
	def _make_args_array(self, args):
		return ['--%s=%s' % (key, value) for key, value in args.iteritems()]

	def test_valid_args(self):
		args = self._make_args_array(self._get_valid_args_map())
		options, args = tarsnap_manager._parse_args(args)
		self.assertEquals(TarsnapManagerTestCase._DEFAULT_KEY_FILE,
			options.key_file)
		self.assertFalse(options.dry_run)
		self.assertEquals(TarsnapManagerTestCase._DEFAULT_ARCHIVE_NAME,
			options.archive_name)
		self.assertEquals(TarsnapManagerTestCase._DEFAULT_WEEKDAY,
			options.weekday)
		self.assertEquals(TarsnapManagerTestCase._DEFAULT_NUM_DAYS,
			options.num_days)
		self.assertEquals(TarsnapManagerTestCase._DEFAULT_NUM_WEEKS,
			options.num_weeks)
		self.assertEquals(TarsnapManagerTestCase._DEFAULT_NUM_MONTHS,
			options.num_months)

		# Assert that the dry_run option is recognized.
		args = self._make_args_array(self._get_valid_args_map())
		args.append('--dry_run')
		options, args = tarsnap_manager._parse_args(args)
		self.assertTrue(options.dry_run)

	def _fake_run(self, options, args):
		self.run_cmd = ' '.join(args)

	def test_make_archive(self):
		args = self._make_args_array(self._get_valid_args_map())
		options, args = tarsnap_manager._parse_args(args)

		tarsnap_manager._run = self._fake_run
		paths = ('/path1', '/path2')
		filename = 'filename_value'
		tarsnap_manager._make_archive(options, paths, filename)
		expected_cmd = 'tarsnap --keyfile %s --cachedir %s -c -f %s %s %s' % (
			TarsnapManagerTestCase._DEFAULT_KEY_FILE,
			tarsnap_manager._DEFAULT_CACHE_DIR,
			filename,
			paths[0], paths[1])
		self.assertEquals(expected_cmd, self.run_cmd)
	
	def test_delete_archive(self):
		args = self._make_args_array(self._get_valid_args_map())
		options, args = tarsnap_manager._parse_args(args)

		tarsnap_manager._run = self._fake_run
		filename = 'filename_value'
		tarsnap_manager._delete_archive(options, filename)
		expected_cmd = 'tarsnap --keyfile %s --cachedir %s -d -f %s' % (
			TarsnapManagerTestCase._DEFAULT_KEY_FILE,
			tarsnap_manager._DEFAULT_CACHE_DIR,
			filename)
		self.assertEquals(expected_cmd, self.run_cmd)

	def test_invalid_args(self):
		args = self._get_valid_args_map()
		del args['key_file']
		with self.assertRaises(SystemExit):
			tarsnap_manager._parse_args(self._make_args_array(args))

		args = self._get_valid_args_map()
		args['archive_name'] = ''
		with self.assertRaises(SystemExit):
			tarsnap_manager._parse_args(self._make_args_array(args))

		args = self._get_valid_args_map()
		args['weekday'] = -1
		with self.assertRaises(SystemExit):
			tarsnap_manager._parse_args(self._make_args_array(args))

		args = self._get_valid_args_map()
		args['weekday'] = 7
		with self.assertRaises(SystemExit):
			tarsnap_manager._parse_args(self._make_args_array(args))

		args = self._get_valid_args_map()
		args['num_days'] = 0
		with self.assertRaises(SystemExit):
			tarsnap_manager._parse_args(self._make_args_array(args))

		args = self._get_valid_args_map()
		args['num_weeks'] = -1
		with self.assertRaises(SystemExit):
			tarsnap_manager._parse_args(self._make_args_array(args))

		args = self._get_valid_args_map()
		args['num_months'] = -1
		with self.assertRaises(SystemExit):
			tarsnap_manager._parse_args(self._make_args_array(args))


if __name__ == '__main__':
	unittest.main()

