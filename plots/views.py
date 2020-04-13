from django.shortcuts import render
import io
import urllib, base64
from .plots_lib import increments, cumulative_plot_abs
from .models import Borough, Dates

def index(request):

	# Get relevant borough and dates
	b = Borough.objects.get(name__exact='Southwark')
	d = Dates.objects.get()

	# Get the daily increments for the borough 
	b_increments = increments(b.cumulative_array, b.population)

	# Plot of cumulative cases
	cumul_abs = cumulative_plot_abs(d.dates_array, b.cumulative_array, b_increments, b.name)

	# Save plot into buffer and convert to be able to visualise it
	buf = io.BytesIO()
	cumul_abs.savefig(buf,format='png')
	buf.seek(0)
	string = base64.b64encode(buf.read())
	uri = urllib.parse.quote(string)

	return render(request, 'index.html', {'data':uri})