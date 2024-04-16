from django.contrib import admin

from .models import Priority, TicketStatus, TicketAllocation, Ticket

# Register your models here.
admin.site.register(
    [
        Priority,
        TicketStatus,
        TicketAllocation,
        Ticket,
    ]
)
