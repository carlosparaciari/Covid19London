from django.test import TestCase

import numpy as np
from .plots_lib import simple_moving_average

class SimpleMovingAverageTest(TestCase):

	@classmethod
	def setUpTestData(cls):
		cls.test_array = np.array([3,2,7,3,9])
		cls.wrong_period = 4

	def test_exception_with_even(self):
		self.assertRaises( ValueError, simple_moving_average(self.test_array,period=7.) )