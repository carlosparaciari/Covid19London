from django.contrib import admin

from .models import Borough, Province, LondonDate, ItalyDate

admin.site.register(Borough)
admin.site.register(Province)
admin.site.register(LondonDate)
admin.site.register(ItalyDate)
