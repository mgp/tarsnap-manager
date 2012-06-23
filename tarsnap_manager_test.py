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

if __name__ == '__main__':
	unittest.main()

