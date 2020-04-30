from django.test import TestCase

import numpy as np
from .plots_lib import simple_moving_average

class SimpleMovingAverageTest(TestCase):

	@classmethod
	def setUpTestData(cls):
		cls.test_array = np.array([3,2,7,3,9])
		cls.exp_array = np.array([4.,15./4.,24./5.,21./4.,19./3.])
		cls.test_period = 5
		cls.wrong_period = 4

	def test_exception_with_even_period(self):
		self.assertRaises(ValueError, simple_moving_average, self.test_array, period=self.wrong_period)

	def test_working_example(self):
		obt_array = simple_moving_average(self.test_array, period=self.test_period)
		np.testing.assert_array_equal(obt_array, self.exp_array,
									  err_msg='simple_moving_average does not work as expected')
